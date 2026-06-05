from __future__ import annotations

import sys
from datetime import datetime, timezone

from awsglue.utils import getResolvedOptions
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


ARGS = getResolvedOptions(sys.argv, ["JOB_NAME", "RAW_BUCKET", "CURATED_BUCKET"])
RAW_ROOT = f"s3://{ARGS['RAW_BUCKET']}/raw"
CURATED_ROOT = f"s3://{ARGS['CURATED_BUCKET']}/curated"

spark = SparkSession.builder.appName(ARGS["JOB_NAME"]).getOrCreate()
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

REQUIRED_COLUMNS = {
    "customers": {"customer_id", "company_name", "signup_date", "region", "industry", "acquisition_channel", "company_segment"},
    "subscriptions": {"customer_id", "status", "initial_plan", "current_plan", "health_band"},
    "billing_events": {"event_id", "customer_id", "billing_month", "plan_name", "event_type", "payment_collected", "mrr_before", "mrr_after", "delta_mrr"},
    "daily_product_usage": {"usage_date", "customer_id", "active_users", "api_calls", "workflow_runs", "feature_adoption_score"},
    "support_tickets": {"ticket_id", "customer_id", "opened_at", "severity", "resolution_hours", "csat"},
}


def read_source(name: str) -> DataFrame:
    return spark.read.option("header", True).option("inferSchema", True).csv(f"{RAW_ROOT}/{name}/")


def run_quality_checks(frames: dict[str, DataFrame]) -> None:
    keys = {"customers": "customer_id", "subscriptions": "customer_id", "billing_events": "event_id", "daily_product_usage": None, "support_tickets": "ticket_id"}
    customers = frames["customers"].select("customer_id").distinct()
    results: list[dict] = []

    for name, frame in frames.items():
        missing = sorted(REQUIRED_COLUMNS[name] - set(frame.columns))
        results.append({"dataset": name, "check": "required_columns", "status": "FAIL" if missing else "PASS", "failed_rows": len(missing), "detail": f"Missing: {', '.join(missing)}" if missing else "Schema accepted"})
        if missing:
            continue

        key = keys[name]
        duplicate_count = 0 if key is None else frame.groupBy(key).count().filter((F.col(key).isNull()) | (F.col("count") > 1)).count()
        results.append({"dataset": name, "check": "primary_key", "status": "FAIL" if duplicate_count else "PASS", "failed_rows": duplicate_count, "detail": "Duplicate or null keys" if duplicate_count else "Key accepted"})

        orphan_count = 0 if name == "customers" else frame.select("customer_id").distinct().join(customers, "customer_id", "left_anti").count()
        results.append({"dataset": name, "check": "customer_foreign_key", "status": "FAIL" if orphan_count else "PASS", "failed_rows": orphan_count, "detail": "Unknown customers" if orphan_count else "References accepted"})

    billing = frames["billing_events"]
    invalid_revenue = billing.filter((F.col("payment_collected") < 0) | (F.col("mrr_before") < 0) | (F.col("mrr_after") < 0)).count()
    results.append({"dataset": "billing_events", "check": "non_negative_revenue", "status": "FAIL" if invalid_revenue else "PASS", "failed_rows": invalid_revenue, "detail": "Revenue range validation"})

    usage = frames["daily_product_usage"]
    invalid_usage = usage.filter((F.col("active_users") < 0) | (F.col("api_calls") < 0) | (F.col("workflow_runs") < 0) | (~F.col("feature_adoption_score").between(0, 1))).count()
    results.append({"dataset": "daily_product_usage", "check": "valid_usage_metrics", "status": "FAIL" if invalid_usage else "PASS", "failed_rows": invalid_usage, "detail": "Usage range validation"})

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    spark.createDataFrame(results).withColumn("run_id", F.lit(run_id)).coalesce(1).write.mode("overwrite").json(f"{CURATED_ROOT}/data_quality/run_id={run_id}")

    failed = [result for result in results if result["status"] == "FAIL"]
    if failed:
        names = ", ".join(f"{item['dataset']}.{item['check']}" for item in failed)
        raise ValueError(f"Data quality gate failed: {names}")


def build_customer_monthly_metrics(frames: dict[str, DataFrame]) -> DataFrame:
    billing = (
        frames["billing_events"]
        .withColumn("metric_month", F.trunc(F.to_date("billing_month"), "month"))
        .withColumn("payment_failure", F.when(F.col("event_type") == "payment_failed", 1).otherwise(0))
        .withColumn("churned_customer", F.when(F.col("event_type") == "churn", 1).otherwise(0))
        .groupBy("customer_id", "metric_month")
        .agg(
            F.last("plan_name", ignorenulls=True).alias("plan_name"),
            F.sum("payment_collected").alias("payment_collected"),
            F.last("mrr_before", ignorenulls=True).alias("mrr_before"),
            F.last("mrr_after", ignorenulls=True).alias("ending_mrr"),
            F.sum(F.when(F.col("delta_mrr") > 0, F.col("delta_mrr")).otherwise(0)).alias("expansion_mrr"),
            F.sum(F.when(F.col("delta_mrr") < 0, F.col("delta_mrr")).otherwise(0)).alias("contraction_mrr"),
            F.sum("payment_failure").alias("payment_failures"),
            F.max("churned_customer").alias("churned_customer"),
        )
    )

    usage = (
        frames["daily_product_usage"]
        .withColumn("metric_month", F.trunc(F.to_date("usage_date"), "month"))
        .groupBy("customer_id", "metric_month")
        .agg(
            F.avg("active_users").alias("active_users_avg"),
            F.max("active_users").alias("active_users_peak"),
            F.sum("api_calls").alias("api_calls_total"),
            F.sum("workflow_runs").alias("workflow_runs_total"),
            F.avg("feature_adoption_score").alias("feature_adoption_avg"),
        )
    )

    tickets = (
        frames["support_tickets"]
        .withColumn("metric_month", F.trunc(F.to_date("opened_at"), "month"))
        .withColumn("high_priority", F.when(F.col("severity").isin("high", "critical"), 1).otherwise(0))
        .groupBy("customer_id", "metric_month")
        .agg(
            F.count("ticket_id").alias("ticket_count"),
            F.sum("high_priority").alias("high_priority_tickets"),
            F.avg("resolution_hours").alias("avg_resolution_hours"),
            F.avg("csat").alias("avg_csat"),
        )
    )

    context = frames["customers"].select("customer_id", "company_name", "signup_date", "region", "industry", "acquisition_channel", "company_segment").join(frames["subscriptions"].select("customer_id", "status", "health_band"), "customer_id", "left")

    return (
        billing.join(usage, ["customer_id", "metric_month"], "left")
        .join(tickets, ["customer_id", "metric_month"], "left")
        .join(context, "customer_id", "left")
        .fillna({"active_users_avg": 0, "active_users_peak": 0, "api_calls_total": 0, "workflow_runs_total": 0, "feature_adoption_avg": 0, "ticket_count": 0, "high_priority_tickets": 0, "avg_resolution_hours": 0, "avg_csat": 5.0})
        .withColumn("active_customer", F.when(F.col("ending_mrr") > 0, 1).otherwise(0))
        .withColumn("risk_score", F.when(F.col("active_users_avg") == 0, 35).otherwise(0) + F.when(F.col("payment_failures") >= 1, 25).otherwise(0) + F.when(F.col("high_priority_tickets") >= 2, 20).otherwise(0) + F.when(F.col("avg_csat") < 3.9, 12).otherwise(0) + F.when(F.col("contraction_mrr") < 0, 8).otherwise(0))
        .withColumn("risk_band", F.when(F.col("risk_score") >= 55, "high").when(F.col("risk_score") >= 30, "medium").otherwise("low"))
        .withColumn("metric_year", F.year("metric_month"))
        .withColumn("metric_month_number", F.month("metric_month"))
    )


def build_monthly_kpis(metrics: DataFrame) -> DataFrame:
    return (
        metrics.groupBy("metric_month", "metric_year", "metric_month_number")
        .agg(
            F.sum("active_customer").alias("active_customers"),
            F.round(F.sum("ending_mrr"), 2).alias("mrr"),
            F.round(F.sum("payment_collected"), 2).alias("collected_revenue"),
            F.sum("churned_customer").alias("churned_customers"),
            F.sum("payment_failures").alias("payment_failures"),
            F.round(F.avg("avg_csat"), 2).alias("avg_csat"),
            F.round(F.avg("feature_adoption_avg"), 3).alias("avg_feature_adoption"),
        )
        .withColumn("arpa", F.round(F.col("mrr") / F.col("active_customers"), 2))
    )


def main() -> None:
    frames = {name: read_source(name) for name in REQUIRED_COLUMNS}
    run_quality_checks(frames)
    metrics = build_customer_monthly_metrics(frames)
    monthly_kpis = build_monthly_kpis(metrics)
    metrics.write.mode("overwrite").partitionBy("metric_year", "metric_month_number").parquet(f"{CURATED_ROOT}/customer_monthly_metrics")
    monthly_kpis.write.mode("overwrite").partitionBy("metric_year", "metric_month_number").parquet(f"{CURATED_ROOT}/monthly_kpis")


if __name__ == "__main__":
    main()

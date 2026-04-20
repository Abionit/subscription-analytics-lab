from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ANALYTICS_DIR = BASE_DIR / "analytics"
SQL_DIR = BASE_DIR / "sql"

for directory in (OUTPUT_DIR, ANALYTICS_DIR):
    directory.mkdir(parents=True, exist_ok=True)


CUSTOMERS_PATH = DATA_DIR / "customers.csv"
SUBSCRIPTIONS_PATH = DATA_DIR / "subscriptions.csv"
BILLING_PATH = DATA_DIR / "billing_events.csv"
USAGE_PATH = DATA_DIR / "daily_product_usage.csv"
TICKETS_PATH = DATA_DIR / "support_tickets.csv"
DB_PATH = ANALYTICS_DIR / "subscription_analytics.db"
SCHEMA_PATH = SQL_DIR / "schema.sql"


def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp()


def compute_risk_score(row: pd.Series) -> int:
    score = 0

    if row.get("usage_ratio_vs_trailing_3m", 1.0) < 0.72:
        score += 35
    if row.get("payment_failures", 0) >= 1:
        score += 25
    if row.get("high_priority_tickets", 0) >= 2:
        score += 20
    if row.get("avg_csat", 5.0) < 3.9:
        score += 12
    if row.get("contraction_mrr", 0) < 0:
        score += 8

    return min(score, 100)


def risk_band(score: int) -> str:
    if score >= 55:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def build_monthly_usage(usage_df: pd.DataFrame) -> pd.DataFrame:
    usage_df["metric_month"] = month_start(usage_df["usage_date"])
    monthly_usage = (
        usage_df.groupby(["customer_id", "metric_month"], as_index=False)
        .agg(
            active_users_avg=("active_users", "mean"),
            active_users_peak=("active_users", "max"),
            api_calls_total=("api_calls", "sum"),
            workflow_runs_total=("workflow_runs", "sum"),
            feature_adoption_avg=("feature_adoption_score", "mean"),
        )
        .sort_values(["customer_id", "metric_month"])
    )
    monthly_usage["usage_ratio_vs_trailing_3m"] = (
        monthly_usage.groupby("customer_id")["active_users_avg"]
        .transform(lambda series: (series / series.rolling(3, min_periods=1).mean()).round(3))
    )
    return monthly_usage


def build_monthly_tickets(tickets_df: pd.DataFrame) -> pd.DataFrame:
    tickets_df["metric_month"] = month_start(tickets_df["opened_at"])
    tickets_df["high_priority"] = tickets_df["severity"].isin(["high", "critical"]).astype(int)
    return (
        tickets_df.groupby(["customer_id", "metric_month"], as_index=False)
        .agg(
            ticket_count=("ticket_id", "count"),
            high_priority_tickets=("high_priority", "sum"),
            avg_resolution_hours=("resolution_hours", "mean"),
            avg_csat=("csat", "mean"),
        )
        .round({"avg_resolution_hours": 1, "avg_csat": 2})
    )


def build_monthly_billing(billing_df: pd.DataFrame) -> pd.DataFrame:
    billing_df["metric_month"] = month_start(billing_df["billing_month"])
    billing_df["payment_failures"] = (billing_df["event_type"] == "payment_failed").astype(int)
    billing_df["expansion_mrr"] = billing_df["delta_mrr"].clip(lower=0)
    billing_df["contraction_mrr"] = billing_df["delta_mrr"].clip(upper=0)
    billing_df["churned_customer"] = (billing_df["event_type"] == "churn").astype(int)

    monthly_billing = (
        billing_df.groupby(["customer_id", "metric_month"], as_index=False)
        .agg(
            plan_name=("plan_name", "last"),
            invoice_amount=("invoice_amount", "sum"),
            payment_collected=("payment_collected", "sum"),
            mrr_before=("mrr_before", "last"),
            ending_mrr=("mrr_after", "last"),
            net_mrr_change=("delta_mrr", "sum"),
            expansion_mrr=("expansion_mrr", "sum"),
            contraction_mrr=("contraction_mrr", "sum"),
            payment_failures=("payment_failures", "sum"),
            churned_customer=("churned_customer", "max"),
        )
        .round(2)
    )
    monthly_billing["active_customer"] = (monthly_billing["ending_mrr"] > 0).astype(int)
    return monthly_billing


def build_customer_monthly_metrics(
    customers_df: pd.DataFrame,
    subscriptions_df: pd.DataFrame,
    monthly_billing: pd.DataFrame,
    monthly_usage: pd.DataFrame,
    monthly_tickets: pd.DataFrame,
) -> pd.DataFrame:
    metrics = (
        monthly_billing.merge(monthly_usage, on=["customer_id", "metric_month"], how="left")
        .merge(monthly_tickets, on=["customer_id", "metric_month"], how="left")
        .merge(customers_df, on="customer_id", how="left")
        .merge(subscriptions_df[["customer_id", "status", "health_band"]], on="customer_id", how="left")
    )
    metrics["signup_month"] = month_start(metrics["signup_date"])
    metrics["months_since_signup"] = (
        (metrics["metric_month"].dt.year - metrics["signup_month"].dt.year) * 12
        + (metrics["metric_month"].dt.month - metrics["signup_month"].dt.month)
    )
    metrics[["ticket_count", "high_priority_tickets", "payment_failures"]] = metrics[
        ["ticket_count", "high_priority_tickets", "payment_failures"]
    ].fillna(0)
    metrics[["active_users_avg", "active_users_peak", "api_calls_total", "workflow_runs_total"]] = metrics[
        ["active_users_avg", "active_users_peak", "api_calls_total", "workflow_runs_total"]
    ].fillna(0)
    metrics[["feature_adoption_avg", "avg_resolution_hours", "avg_csat", "usage_ratio_vs_trailing_3m"]] = metrics[
        ["feature_adoption_avg", "avg_resolution_hours", "avg_csat", "usage_ratio_vs_trailing_3m"]
    ].fillna({"feature_adoption_avg": 0, "avg_resolution_hours": 0, "avg_csat": 5.0, "usage_ratio_vs_trailing_3m": 1.0})
    metrics["risk_score"] = metrics.apply(compute_risk_score, axis=1)
    metrics["risk_band"] = metrics["risk_score"].map(risk_band)
    return metrics.sort_values(["metric_month", "customer_id"]).reset_index(drop=True)


def build_monthly_kpis(customer_monthly_metrics: pd.DataFrame) -> pd.DataFrame:
    monthly_kpis = (
        customer_monthly_metrics.groupby("metric_month", as_index=False)
        .agg(
            active_customers=("active_customer", "sum"),
            mrr=("ending_mrr", "sum"),
            collected_revenue=("payment_collected", "sum"),
            churned_customers=("churned_customer", "sum"),
            payment_failures=("payment_failures", "sum"),
            avg_csat=("avg_csat", "mean"),
            avg_feature_adoption=("feature_adoption_avg", "mean"),
        )
        .sort_values("metric_month")
        .round(2)
    )
    monthly_kpis["arpa"] = (monthly_kpis["mrr"] / monthly_kpis["active_customers"]).round(2)
    monthly_kpis["prior_month_mrr"] = monthly_kpis["mrr"].shift(1)
    monthly_kpis["mrr_growth_pct"] = (
        ((monthly_kpis["mrr"] - monthly_kpis["prior_month_mrr"]) / monthly_kpis["prior_month_mrr"]) * 100
    ).round(2)
    monthly_kpis["prior_month_active"] = monthly_kpis["active_customers"].shift(1)
    monthly_kpis["logo_churn_rate_pct"] = (
        (monthly_kpis["churned_customers"] / monthly_kpis["prior_month_active"]) * 100
    ).round(2)
    revenue_components = (
        customer_monthly_metrics.groupby("metric_month", as_index=False)
        .agg(
            opening_mrr=("mrr_before", "sum"),
            expansion_mrr=("expansion_mrr", "sum"),
            contraction_mrr=("contraction_mrr", "sum"),
            closing_mrr=("ending_mrr", "sum"),
        )
        .sort_values("metric_month")
    )
    monthly_kpis = monthly_kpis.merge(revenue_components, on="metric_month", how="left")
    monthly_kpis["net_revenue_retention_pct"] = (
        (
            (monthly_kpis["opening_mrr"] + monthly_kpis["expansion_mrr"] + monthly_kpis["contraction_mrr"])
            / monthly_kpis["opening_mrr"].replace(0, pd.NA)
        )
        * 100
    ).round(2)
    monthly_kpis["net_revenue_retention_pct"] = pd.to_numeric(monthly_kpis["net_revenue_retention_pct"], errors="coerce")
    monthly_kpis["mrr_growth_pct"] = monthly_kpis["mrr_growth_pct"].fillna(0.0)
    monthly_kpis["logo_churn_rate_pct"] = monthly_kpis["logo_churn_rate_pct"].fillna(0.0)
    monthly_kpis["net_revenue_retention_pct"] = monthly_kpis["net_revenue_retention_pct"].fillna(100.0)
    return monthly_kpis


def build_cohort_retention(customer_monthly_metrics: pd.DataFrame) -> pd.DataFrame:
    active_metrics = customer_monthly_metrics[customer_monthly_metrics["active_customer"] == 1].copy()
    cohort_sizes = (
        active_metrics[active_metrics["months_since_signup"] == 0]
        .groupby("signup_month", as_index=False)
        .agg(cohort_size=("customer_id", "nunique"))
    )
    retained = (
        active_metrics.groupby(["signup_month", "months_since_signup"], as_index=False)
        .agg(retained_customers=("customer_id", "nunique"))
        .merge(cohort_sizes, on="signup_month", how="left")
    )
    retained["retention_rate_pct"] = ((retained["retained_customers"] / retained["cohort_size"]) * 100).round(2)
    return retained.sort_values(["signup_month", "months_since_signup"]).reset_index(drop=True)


def build_segment_summary(customer_monthly_metrics: pd.DataFrame) -> pd.DataFrame:
    latest_month = customer_monthly_metrics["metric_month"].max()
    latest_metrics = customer_monthly_metrics[customer_monthly_metrics["metric_month"] == latest_month]
    return (
        latest_metrics.groupby(["plan_name", "region"], as_index=False)
        .agg(
            active_customers=("customer_id", "nunique"),
            mrr=("ending_mrr", "sum"),
            avg_active_users=("active_users_avg", "mean"),
            avg_csat=("avg_csat", "mean"),
            avg_ticket_count=("ticket_count", "mean"),
            high_risk_customers=("risk_band", lambda values: (values == "high").sum()),
        )
        .round(2)
        .sort_values(["mrr", "active_customers"], ascending=[False, False])
    )


def build_watchlist(customer_monthly_metrics: pd.DataFrame) -> pd.DataFrame:
    latest_month = customer_monthly_metrics["metric_month"].max()
    watchlist = customer_monthly_metrics[customer_monthly_metrics["metric_month"] == latest_month].copy()
    watchlist = watchlist.sort_values(["risk_score", "ending_mrr"], ascending=[False, False])
    columns = [
        "customer_id",
        "company_name",
        "region",
        "plan_name",
        "ending_mrr",
        "risk_score",
        "risk_band",
        "usage_ratio_vs_trailing_3m",
        "payment_failures",
        "high_priority_tickets",
        "avg_csat",
    ]
    return watchlist.loc[:, columns].head(20).reset_index(drop=True)


def build_revenue_anomalies(monthly_kpis: pd.DataFrame) -> pd.DataFrame:
    anomalies = monthly_kpis[["metric_month", "mrr", "mrr_growth_pct", "logo_churn_rate_pct", "net_revenue_retention_pct"]].copy()
    warmup_start = anomalies["metric_month"].min() + pd.DateOffset(months=4)
    anomalies = anomalies[anomalies["metric_month"] >= warmup_start].copy()
    growth_std = anomalies["mrr_growth_pct"].std(ddof=0) or 1
    growth_mean = anomalies["mrr_growth_pct"].mean()
    anomalies["growth_z_score"] = ((anomalies["mrr_growth_pct"] - growth_mean) / growth_std).round(2)
    anomalies["flagged"] = (
        anomalies["mrr_growth_pct"].abs().ge(8) | anomalies["growth_z_score"].abs().ge(1.4) | anomalies["logo_churn_rate_pct"].ge(6)
    )
    return anomalies[anomalies["flagged"]].reset_index(drop=True)


def write_sqlite_tables(
    customers_df: pd.DataFrame,
    subscriptions_df: pd.DataFrame,
    billing_df: pd.DataFrame,
    usage_df: pd.DataFrame,
    tickets_df: pd.DataFrame,
    customer_monthly_metrics: pd.DataFrame,
    monthly_kpis: pd.DataFrame,
    cohort_retention: pd.DataFrame,
) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        customers_df.to_sql("customers", connection, if_exists="replace", index=False)
        subscriptions_df.to_sql("subscriptions", connection, if_exists="replace", index=False)
        billing_df.to_sql("billing_events", connection, if_exists="replace", index=False)
        usage_df.to_sql("daily_product_usage", connection, if_exists="replace", index=False)
        tickets_df.to_sql("support_tickets", connection, if_exists="replace", index=False)
        customer_monthly_metrics.to_sql("customer_monthly_metrics", connection, if_exists="replace", index=False)
        monthly_kpis.to_sql("monthly_kpis", connection, if_exists="replace", index=False)
        cohort_retention.to_sql("cohort_retention", connection, if_exists="replace", index=False)
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def write_report(monthly_kpis: pd.DataFrame, segment_summary: pd.DataFrame, watchlist: pd.DataFrame, anomalies: pd.DataFrame) -> None:
    latest = monthly_kpis.sort_values("metric_month").iloc[-1]
    best_region = segment_summary.groupby("region", as_index=False)["mrr"].sum().sort_values("mrr", ascending=False).iloc[0]
    highest_plan = segment_summary.groupby("plan_name", as_index=False)["mrr"].sum().sort_values("mrr", ascending=False).iloc[0]

    lines = [
        "# Subscription Analytics Report",
        "",
        f"Generated at: {pd.Timestamp.utcnow().isoformat()}",
        "",
        "## Executive Summary",
        "",
        f"- Latest month: {pd.Timestamp(latest['metric_month']).date().isoformat()}",
        f"- Active customers: {int(latest['active_customers'])}",
        f"- Monthly recurring revenue (MRR): {float(latest['mrr']):,.2f}",
        f"- ARPA: {float(latest['arpa']):,.2f}",
        f"- Net revenue retention: {float(latest['net_revenue_retention_pct']):.2f}%",
        f"- Logo churn rate: {float(latest['logo_churn_rate_pct']):.2f}%",
        f"- Average CSAT: {float(latest['avg_csat']):.2f}",
        f"- Strongest region by MRR: {best_region['region']} ({float(best_region['mrr']):,.2f})",
        f"- Leading plan by MRR: {highest_plan['plan_name']} ({float(highest_plan['mrr']):,.2f})",
        "",
        "## Revenue Anomalies",
        "",
    ]

    if anomalies.empty:
        lines.append("- No material revenue anomalies were flagged in the current series.")
    else:
        for _, row in anomalies.iterrows():
            lines.append(
                f"- {pd.Timestamp(row['metric_month']).date().isoformat()}: MRR growth {float(row['mrr_growth_pct']):.2f}%, logo churn {float(row['logo_churn_rate_pct']):.2f}%, NRR {float(row['net_revenue_retention_pct']):.2f}%"
            )

    lines.extend(
        [
            "",
            "## Highest-Risk Accounts",
            "",
        ]
    )

    for _, row in watchlist.head(10).iterrows():
        lines.append(
            f"- {row['customer_id']} | {row['company_name']} | plan={row['plan_name']} | region={row['region']} | risk={int(row['risk_score'])} ({row['risk_band']}) | payment_failures={int(row['payment_failures'])} | high_priority_tickets={int(row['high_priority_tickets'])} | avg_csat={float(row['avg_csat']):.2f}"
        )

    (OUTPUT_DIR / "subscription_analytics_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for path in (CUSTOMERS_PATH, SUBSCRIPTIONS_PATH, BILLING_PATH, USAGE_PATH, TICKETS_PATH, SCHEMA_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    customers_df = pd.read_csv(CUSTOMERS_PATH)
    subscriptions_df = pd.read_csv(SUBSCRIPTIONS_PATH)
    billing_df = pd.read_csv(BILLING_PATH)
    usage_df = pd.read_csv(USAGE_PATH)
    tickets_df = pd.read_csv(TICKETS_PATH)

    monthly_usage = build_monthly_usage(usage_df)
    monthly_tickets = build_monthly_tickets(tickets_df)
    monthly_billing = build_monthly_billing(billing_df)
    customer_monthly_metrics = build_customer_monthly_metrics(
        customers_df,
        subscriptions_df,
        monthly_billing,
        monthly_usage,
        monthly_tickets,
    )
    monthly_kpis = build_monthly_kpis(customer_monthly_metrics)
    cohort_retention = build_cohort_retention(customer_monthly_metrics)
    segment_summary = build_segment_summary(customer_monthly_metrics)
    watchlist = build_watchlist(customer_monthly_metrics)
    anomalies = build_revenue_anomalies(monthly_kpis)

    customer_monthly_metrics.to_csv(OUTPUT_DIR / "customer_monthly_metrics.csv", index=False)
    monthly_kpis.to_csv(OUTPUT_DIR / "monthly_kpis.csv", index=False)
    cohort_retention.to_csv(OUTPUT_DIR / "cohort_retention.csv", index=False)
    segment_summary.to_csv(OUTPUT_DIR / "segment_summary.csv", index=False)
    watchlist.to_csv(OUTPUT_DIR / "churn_risk_watchlist.csv", index=False)
    anomalies.to_csv(OUTPUT_DIR / "revenue_anomalies.csv", index=False)

    write_sqlite_tables(
        customers_df,
        subscriptions_df,
        billing_df,
        usage_df,
        tickets_df,
        customer_monthly_metrics,
        monthly_kpis,
        cohort_retention,
    )
    write_report(monthly_kpis, segment_summary, watchlist, anomalies)

    print("Built analytics artifacts:")
    print(f"- customer_monthly_metrics.csv: {len(customer_monthly_metrics)} rows")
    print(f"- monthly_kpis.csv: {len(monthly_kpis)} rows")
    print(f"- cohort_retention.csv: {len(cohort_retention)} rows")
    print(f"- segment_summary.csv: {len(segment_summary)} rows")
    print(f"- churn_risk_watchlist.csv: {len(watchlist)} rows")
    print(f"- revenue_anomalies.csv: {len(anomalies)} rows")
    print(f"- subscription_analytics_report.md")
    print(f"- subscription_analytics.db")


if __name__ == "__main__":
    main()

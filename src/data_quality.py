from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


@dataclass(frozen=True)
class QualityCheck:
    dataset: str
    check: str
    status: str
    failed_rows: int
    detail: str


SCHEMAS = {
    "customers": {"required": {"customer_id", "company_name", "signup_date", "region", "industry", "acquisition_channel", "company_segment", "status", "initial_plan", "current_plan", "health_band"}, "key": "customer_id"},
    "subscriptions": {"required": {"customer_id", "start_date", "status", "initial_plan", "current_plan", "health_band"}, "key": "customer_id"},
    "billing_events": {"required": {"event_id", "customer_id", "billing_month", "plan_name", "event_type", "invoice_amount", "payment_collected", "mrr_before", "mrr_after", "delta_mrr"}, "key": "event_id"},
    "daily_product_usage": {"required": {"usage_date", "customer_id", "active_users", "api_calls", "workflow_runs", "feature_adoption_score"}, "key": None},
    "support_tickets": {"required": {"ticket_id", "customer_id", "opened_at", "severity", "resolution_hours", "csat"}, "key": "ticket_id"},
}


def check_schema(dataset: str, frame: pd.DataFrame) -> QualityCheck:
    missing = sorted(SCHEMAS[dataset]["required"] - set(frame.columns))
    return QualityCheck(dataset, "required_columns", "fail" if missing else "pass", len(missing), f"Missing columns: {', '.join(missing)}" if missing else "All required columns are present.")


def check_primary_key(dataset: str, frame: pd.DataFrame) -> QualityCheck:
    key = SCHEMAS[dataset]["key"]
    if key is None:
        return QualityCheck(dataset, "primary_key", "pass", 0, "No single-column primary key is defined.")
    if key not in frame.columns:
        return QualityCheck(dataset, "primary_key", "fail", len(frame), f"Key column {key} is missing.")
    failed = int(frame[key].isna().sum() + frame[key].duplicated().sum())
    return QualityCheck(dataset, "primary_key", "fail" if failed else "pass", failed, f"{failed} null or duplicate key values found." if failed else f"{key} is complete and unique.")


def check_required_values(dataset: str, frame: pd.DataFrame) -> QualityCheck:
    columns = SCHEMAS[dataset]["required"] & set(frame.columns)
    failed = int(frame[list(columns)].isna().sum().sum())
    return QualityCheck(dataset, "required_values", "fail" if failed else "pass", failed, f"{failed} null values found in required fields." if failed else "Required fields contain no null values.")


def check_foreign_key(dataset: str, frame: pd.DataFrame, customer_ids: set[str]) -> QualityCheck:
    if dataset == "customers":
        return QualityCheck(dataset, "customer_foreign_key", "pass", 0, "Source table for customer keys.")
    if "customer_id" not in frame.columns:
        return QualityCheck(dataset, "customer_foreign_key", "fail", len(frame), "customer_id is missing.")
    failed = int((~frame["customer_id"].astype(str).isin(customer_ids)).sum())
    return QualityCheck(dataset, "customer_foreign_key", "fail" if failed else "pass", failed, f"{failed} rows reference an unknown customer." if failed else "All customer references are valid.")


def check_business_rules(dataset: str, frame: pd.DataFrame) -> list[QualityCheck]:
    checks: list[QualityCheck] = []
    if dataset == "customers" and {"status", "health_band"}.issubset(frame.columns):
        failed = int((~frame["status"].isin({"active", "churned"})).sum() + (~frame["health_band"].isin({"expansion", "stable", "at_risk"})).sum())
        checks.append(QualityCheck(dataset, "valid_customer_categories", "fail" if failed else "pass", failed, "Customer status and health values are within the accepted domains."))
    if dataset == "billing_events":
        present = [column for column in ["invoice_amount", "payment_collected", "mrr_before", "mrr_after"] if column in frame.columns]
        failed = int((frame[present] < 0).sum().sum()) if present else len(frame)
        checks.append(QualityCheck(dataset, "non_negative_revenue", "fail" if failed else "pass", failed, f"{failed} negative revenue values found." if failed else "Revenue fields are non-negative."))
    if dataset == "daily_product_usage":
        present = [column for column in ["active_users", "api_calls", "workflow_runs"] if column in frame.columns]
        failed = int((frame[present] < 0).sum().sum()) if present else len(frame)
        if "feature_adoption_score" in frame.columns:
            failed += int((~frame["feature_adoption_score"].between(0, 1)).sum())
        checks.append(QualityCheck(dataset, "valid_usage_metrics", "fail" if failed else "pass", failed, "Usage metrics are non-negative and feature adoption is between 0 and 1."))
    if dataset == "support_tickets":
        failed = 0
        if "severity" in frame.columns:
            failed += int((~frame["severity"].isin({"low", "medium", "high", "critical"})).sum())
        if "resolution_hours" in frame.columns:
            failed += int((frame["resolution_hours"] < 0).sum())
        if "csat" in frame.columns:
            failed += int((~frame["csat"].between(1, 5)).sum())
        checks.append(QualityCheck(dataset, "valid_support_metrics", "fail" if failed else "pass", failed, "Ticket severity, resolution time, and CSAT are within accepted ranges."))
    return checks


def validate_frames(frames: dict[str, pd.DataFrame]) -> list[QualityCheck]:
    customers = frames.get("customers")
    customer_ids = set(customers["customer_id"].dropna().astype(str)) if customers is not None and "customer_id" in customers.columns else set()
    checks: list[QualityCheck] = []
    for dataset, frame in frames.items():
        checks.extend([check_schema(dataset, frame), check_primary_key(dataset, frame), check_required_values(dataset, frame), check_foreign_key(dataset, frame, customer_ids)])
        checks.extend(check_business_rules(dataset, frame))
    return checks


def write_quality_report(checks: list[QualityCheck]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = [asdict(check) for check in checks]
    (OUTPUT_DIR / "data_quality_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    failed_checks = [check for check in checks if check.status == "fail"]
    lines = ["# Data Quality Report", "", f"- Checks executed: {len(checks)}", f"- Passed: {len(checks) - len(failed_checks)}", f"- Failed: {len(failed_checks)}", f"- Pipeline status: {'FAILED' if failed_checks else 'PASSED'}", "", "| Dataset | Check | Status | Failed rows | Detail |", "| --- | --- | --- | ---: | --- |"]
    lines.extend(f"| {check.dataset} | {check.check} | {check.status.upper()} | {check.failed_rows} | {check.detail} |" for check in checks)
    (OUTPUT_DIR / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")


def load_source_frames() -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.read_csv(DATA_DIR / "customers.csv"),
        "subscriptions": pd.read_csv(DATA_DIR / "subscriptions.csv"),
        "billing_events": pd.read_csv(DATA_DIR / "billing_events.csv"),
        "daily_product_usage": pd.read_csv(DATA_DIR / "daily_product_usage.csv"),
        "support_tickets": pd.read_csv(DATA_DIR / "support_tickets.csv"),
    }


def main() -> None:
    checks = validate_frames(load_source_frames())
    write_quality_report(checks)
    failed_checks = [check for check in checks if check.status == "fail"]
    if failed_checks:
        failed_names = ", ".join(f"{check.dataset}.{check.check}" for check in failed_checks)
        raise RuntimeError(f"Data quality checks failed: {failed_names}")
    print(f"Data quality checks passed: {len(checks)} checks.")


if __name__ == "__main__":
    main()

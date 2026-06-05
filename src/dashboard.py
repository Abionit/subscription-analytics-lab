from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"


@st.cache_data
def load_outputs() -> dict[str, pd.DataFrame | str | list[dict]]:
    quality_path = OUTPUT_DIR / "data_quality_results.json"
    return {
        "monthly_kpis": pd.read_csv(OUTPUT_DIR / "monthly_kpis.csv", parse_dates=["metric_month"]),
        "cohort_retention": pd.read_csv(OUTPUT_DIR / "cohort_retention.csv", parse_dates=["signup_month"]),
        "segment_summary": pd.read_csv(OUTPUT_DIR / "segment_summary.csv"),
        "watchlist": pd.read_csv(OUTPUT_DIR / "churn_risk_watchlist.csv"),
        "anomalies": pd.read_csv(OUTPUT_DIR / "revenue_anomalies.csv", parse_dates=["metric_month"]),
        "customer_metrics": pd.read_csv(OUTPUT_DIR / "customer_monthly_metrics.csv", parse_dates=["metric_month", "signup_month"]),
        "report_text": (OUTPUT_DIR / "subscription_analytics_report.md").read_text(encoding="utf-8"),
        "quality_results": json.loads(quality_path.read_text(encoding="utf-8")) if quality_path.exists() else [],
    }


def render_kpis(monthly_kpis: pd.DataFrame) -> None:
    ordered = monthly_kpis.sort_values("metric_month")
    latest = ordered.iloc[-1]
    previous = ordered.iloc[-2]
    columns = st.columns(5)
    columns[0].metric("Active customers", int(latest["active_customers"]), int(latest["active_customers"] - previous["active_customers"]))
    columns[1].metric("MRR", f"{latest['mrr']:,.0f}", f"{latest['mrr_growth_pct']:.2f}%")
    columns[2].metric("ARPA", f"{latest['arpa']:,.0f}")
    columns[3].metric("NRR", f"{latest['net_revenue_retention_pct']:.2f}%")
    columns[4].metric("Logo churn", f"{latest['logo_churn_rate_pct']:.2f}%")


def render_quality(results: list[dict]) -> None:
    st.markdown("## Pipeline Quality")
    if not results:
        st.warning("No quality results found. Run: python src/run_pipeline.py")
        return
    frame = pd.DataFrame(results)
    passed = int((frame["status"].str.lower() == "pass").sum())
    failed = len(frame) - passed
    columns = st.columns(3)
    columns[0].metric("Checks executed", len(frame))
    columns[1].metric("Passed", passed)
    columns[2].metric("Failed", failed)
    if failed:
        st.error("The latest run contains failed quality checks.")
    else:
        st.success("The latest run passed every configured quality check.")
    st.dataframe(frame, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Subscription Data Operations", layout="wide")
    st.title("Subscription Data Operations")
    st.caption("Multi-source pipeline monitoring, data quality, recurring revenue, retention, and customer-risk analysis.")

    outputs = load_outputs()
    monthly_kpis = outputs["monthly_kpis"]
    cohort_retention = outputs["cohort_retention"]
    segment_summary = outputs["segment_summary"]
    watchlist = outputs["watchlist"]
    anomalies = outputs["anomalies"]
    customer_metrics = outputs["customer_metrics"]

    render_quality(outputs["quality_results"])
    st.markdown("## Business Metrics")
    render_kpis(monthly_kpis)

    revenue_col, churn_col = st.columns(2)
    with revenue_col:
        st.subheader("MRR and collected revenue")
        st.line_chart(monthly_kpis.set_index("metric_month")[["mrr", "collected_revenue"]], height=320)
    with churn_col:
        st.subheader("Retention and churn")
        st.line_chart(monthly_kpis.set_index("metric_month")[["net_revenue_retention_pct", "logo_churn_rate_pct"]], height=320)

    st.markdown("## Segment Performance")
    filter_col1, filter_col2 = st.columns(2)
    selected_region = filter_col1.selectbox("Region", ["All"] + sorted(segment_summary["region"].unique().tolist()))
    selected_plan = filter_col2.selectbox("Plan", ["All"] + sorted(segment_summary["plan_name"].unique().tolist()))
    filtered = segment_summary.copy()
    if selected_region != "All":
        filtered = filtered[filtered["region"] == selected_region]
    if selected_plan != "All":
        filtered = filtered[filtered["plan_name"] == selected_plan]
    if filtered.empty:
        st.info("No segment data available for the selected filters.")
    else:
        filtered = filtered.assign(segment=filtered["plan_name"] + " | " + filtered["region"])
        left, right = st.columns(2)
        left.bar_chart(filtered.set_index("segment")[["mrr"]], height=320)
        right.bar_chart(filtered.set_index("segment")[["high_risk_customers"]], height=320)

    st.markdown("## Cohort Retention")
    matrix = cohort_retention.pivot(index="signup_month", columns="months_since_signup", values="retention_rate_pct").sort_index()
    matrix.index = matrix.index.strftime("%Y-%m")
    st.dataframe(matrix.style.background_gradient(cmap="Blues"), use_container_width=True)

    st.markdown("## Risk And Revenue Exceptions")
    left, right = st.columns(2)
    with left:
        st.subheader("Churn risk watchlist")
        st.dataframe(watchlist, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Revenue anomalies")
        st.dataframe(anomalies, use_container_width=True, hide_index=True)

    st.markdown("## Latest Customer-Month Records")
    latest_month = customer_metrics["metric_month"].max()
    latest = customer_metrics[customer_metrics["metric_month"] == latest_month].sort_values(["risk_score", "ending_mrr"], ascending=[False, False])
    columns = ["customer_id", "company_name", "region", "plan_name", "ending_mrr", "active_users_avg", "ticket_count", "payment_failures", "risk_score", "risk_band"]
    st.dataframe(latest.loc[:, columns], use_container_width=True, hide_index=True)

    with st.expander("Generated business report"):
        st.markdown(outputs["report_text"])


if __name__ == "__main__":
    main()

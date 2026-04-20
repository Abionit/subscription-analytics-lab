from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"


@st.cache_data
def load_outputs() -> dict[str, pd.DataFrame | str]:
    monthly_kpis = pd.read_csv(OUTPUT_DIR / "monthly_kpis.csv", parse_dates=["metric_month"])
    cohort_retention = pd.read_csv(OUTPUT_DIR / "cohort_retention.csv", parse_dates=["signup_month"])
    segment_summary = pd.read_csv(OUTPUT_DIR / "segment_summary.csv")
    watchlist = pd.read_csv(OUTPUT_DIR / "churn_risk_watchlist.csv")
    anomalies = pd.read_csv(OUTPUT_DIR / "revenue_anomalies.csv", parse_dates=["metric_month"])
    customer_metrics = pd.read_csv(OUTPUT_DIR / "customer_monthly_metrics.csv", parse_dates=["metric_month", "signup_month"])
    report_text = (OUTPUT_DIR / "subscription_analytics_report.md").read_text(encoding="utf-8")
    return {
        "monthly_kpis": monthly_kpis,
        "cohort_retention": cohort_retention,
        "segment_summary": segment_summary,
        "watchlist": watchlist,
        "anomalies": anomalies,
        "customer_metrics": customer_metrics,
        "report_text": report_text,
    }


def format_metric(value: float, suffix: str = "") -> str:
    if suffix == "%":
        return f"{value:,.2f}%"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:,.2f}"


def render_kpis(monthly_kpis: pd.DataFrame) -> None:
    latest = monthly_kpis.sort_values("metric_month").iloc[-1]
    previous = monthly_kpis.sort_values("metric_month").iloc[-2]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Active customers", int(latest["active_customers"]), int(latest["active_customers"] - previous["active_customers"]))
    col2.metric("MRR", f"{latest['mrr']:,.0f}", f"{latest['mrr_growth_pct']:.2f}%")
    col3.metric("ARPA", f"{latest['arpa']:,.0f}")
    col4.metric("NRR", f"{latest['net_revenue_retention_pct']:.2f}%")
    col5.metric("Logo churn", f"{latest['logo_churn_rate_pct']:.2f}%")


def main() -> None:
    st.set_page_config(page_title="Subscription Analytics Lab", layout="wide")
    st.title("Subscription Analytics Lab Dashboard")
    st.caption(
        "Advanced portfolio project for subscription analytics, cohort retention, churn risk, revenue quality, and SQL-backed reporting."
    )

    outputs = load_outputs()
    monthly_kpis = outputs["monthly_kpis"]
    cohort_retention = outputs["cohort_retention"]
    segment_summary = outputs["segment_summary"]
    watchlist = outputs["watchlist"]
    anomalies = outputs["anomalies"]
    customer_metrics = outputs["customer_metrics"]
    report_text = outputs["report_text"]

    render_kpis(monthly_kpis)

    st.markdown("## Revenue And Retention")
    revenue_col, churn_col = st.columns(2)
    with revenue_col:
        st.subheader("MRR trend")
        st.line_chart(monthly_kpis.set_index("metric_month")[["mrr", "collected_revenue"]], height=320)
    with churn_col:
        st.subheader("Retention and churn")
        st.line_chart(
            monthly_kpis.set_index("metric_month")[["net_revenue_retention_pct", "logo_churn_rate_pct"]],
            height=320,
        )

    st.markdown("## Segment Performance")
    filter_col1, filter_col2 = st.columns(2)
    selected_region = filter_col1.selectbox("Region", ["All"] + sorted(segment_summary["region"].unique().tolist()))
    selected_plan = filter_col2.selectbox("Plan", ["All"] + sorted(segment_summary["plan_name"].unique().tolist()))

    filtered_segment = segment_summary.copy()
    if selected_region != "All":
        filtered_segment = filtered_segment[filtered_segment["region"] == selected_region]
    if selected_plan != "All":
        filtered_segment = filtered_segment[filtered_segment["plan_name"] == selected_plan]

    seg_col1, seg_col2 = st.columns(2)
    with seg_col1:
        st.subheader("MRR by plan-region slice")
        if filtered_segment.empty:
            st.info("No segment data available for the selected filters.")
        else:
            plot_df = filtered_segment.assign(slice_label=filtered_segment["plan_name"] + " | " + filtered_segment["region"])
            st.bar_chart(plot_df.set_index("slice_label")[["mrr"]], height=320)
    with seg_col2:
        st.subheader("Risk concentration")
        if filtered_segment.empty:
            st.info("No risk data available for the selected filters.")
        else:
            plot_df = filtered_segment.assign(slice_label=filtered_segment["plan_name"] + " | " + filtered_segment["region"])
            st.bar_chart(plot_df.set_index("slice_label")[["high_risk_customers"]], height=320)

    st.markdown("## Cohort Retention")
    retention_matrix = cohort_retention.pivot(index="signup_month", columns="months_since_signup", values="retention_rate_pct").sort_index()
    retention_matrix.index = retention_matrix.index.strftime("%Y-%m")
    st.dataframe(retention_matrix.style.background_gradient(cmap="Blues"), use_container_width=True)

    st.markdown("## Watchlist And Anomalies")
    risk_col, anomaly_col = st.columns(2)
    with risk_col:
        st.subheader("Churn risk watchlist")
        st.dataframe(watchlist, use_container_width=True, hide_index=True)
    with anomaly_col:
        st.subheader("Revenue anomalies")
        if anomalies.empty:
            st.info("No material anomalies were flagged.")
        else:
            anomalies_display = anomalies.copy()
            anomalies_display["metric_month"] = anomalies_display["metric_month"].dt.strftime("%Y-%m")
            st.dataframe(anomalies_display, use_container_width=True, hide_index=True)

    st.markdown("## Latest Customer-Month Sample")
    latest_month = customer_metrics["metric_month"].max()
    latest_metrics = customer_metrics[customer_metrics["metric_month"] == latest_month].sort_values(
        ["risk_score", "ending_mrr"],
        ascending=[False, False],
    )
    columns = [
        "customer_id",
        "company_name",
        "region",
        "plan_name",
        "ending_mrr",
        "active_users_avg",
        "ticket_count",
        "payment_failures",
        "risk_score",
        "risk_band",
    ]
    st.dataframe(latest_metrics.loc[:, columns], use_container_width=True, hide_index=True)

    st.markdown("## Report Preview")
    st.code(report_text, language="markdown")


if __name__ == "__main__":
    main()

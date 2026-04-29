# Subscription Analytics Lab

Portfolio analytics case study that turns subscription data into KPI reporting, churn monitoring, cohort analysis, and revenue review.

Detailed documentation:

- English: [README.en.md](README.en.md)
- Espanol: [README.es.md](README.es.md)

## Fast Review

If you only want the strongest evidence, open these first:

- Report preview: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)
- SQL queries: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)
- KPI outputs: [output/monthly_kpis.csv](output/monthly_kpis.csv)
- Churn watchlist: [output/churn_risk_watchlist.csv](output/churn_risk_watchlist.csv)

## Best Role Fit

- Data Analyst
- BI / Reporting Analyst
- Operations Analyst with KPI and recurring-metrics ownership

## Business Questions

- Which customer signals explain retention pressure and churn risk?
- Which cohorts retain better or decay faster over time?
- Where is recurring revenue at risk?
- Which accounts should move into a watchlist for review?

## At A Glance

- Analytical focus: recurring revenue, retention, churn risk, segmentation, and customer health
- Stack: Python, SQL, SQLite, Streamlit
- Main outputs: KPI series, cohort retention, segment summary, churn watchlist, revenue anomaly report
- Current snapshot: `232` active customers | `61,418` MRR | `264.73` ARPA | `1.28%` logo churn | `4.33` average CSAT

## What This Project Demonstrates

- Reproducible analytics workflow from source data to reporting outputs
- Customer-month modeling for recurring revenue analysis
- KPI design for MRR, ARPA, churn, and net revenue retention
- Cohort retention and churn risk analysis
- SQL and Python working together in one analytical workflow
- Dashboard-ready outputs and report-ready business communication

## Workflow

1. Generate synthetic customer, billing, usage, and support data.
2. Build the customer-month analytical layer in Python.
3. Calculate recurring revenue, retention, churn, and risk metrics.
4. Export representative outputs in CSV and Markdown.
5. Materialize SQLite tables and views for reusable SQL analysis.
6. Review results in the Streamlit dashboard.

## Repository Layout

- [src/](src): pipeline scripts and dashboard
- [sql/](sql): schema and reusable SQL queries
- [output/](output): representative analytical outputs
- [tests/](tests): unit tests for core risk scoring logic
- [CHANGELOG.md](CHANGELOG.md): version notes

## Representative Outputs

- KPI series: [output/monthly_kpis.csv](output/monthly_kpis.csv)
- Cohort retention: [output/cohort_retention.csv](output/cohort_retention.csv)
- Segment summary: [output/segment_summary.csv](output/segment_summary.csv)
- Churn watchlist: [output/churn_risk_watchlist.csv](output/churn_risk_watchlist.csv)
- Revenue anomalies: [output/revenue_anomalies.csv](output/revenue_anomalies.csv)
- Report preview: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)

## Run Locally

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies and run the workflow:

```bash
pip install -r requirements.txt
python src/run_pipeline.py
python -m streamlit run src/dashboard.py
python -m unittest discover -s tests
```

## Notes

This public portfolio version stays lightweight on purpose.

Running the pipeline locally regenerates the source data files under `data/`, the customer-month analytical layer, and the SQLite database under `analytics/`.

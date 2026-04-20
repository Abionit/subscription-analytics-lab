# Subscription Analytics Lab - Revenue, Retention, and Churn Analysis

Advanced portfolio project built to show how SQL, Python, and reporting can be used to monitor subscription revenue, retention, and customer health.

## Business Question

Which signals help identify revenue risk and retention pressure early in a subscription business?

This project answers that question by combining customer lifecycle context, billing behavior, product usage, support activity, KPI reporting, and analytical outputs that can be reviewed quickly.

## What This Repository Demonstrates

- Python-based data generation and analytics pipeline
- SQL-backed reporting with reusable views and query sets
- Customer-month modeling for subscription analytics
- KPI design for MRR, ARPA, logo churn, and net revenue retention
- Cohort retention analysis
- Churn risk scoring from behavioral and operational signals
- Dashboard communication through Streamlit

## Current Snapshot

The current generated outputs show:

- `232` active customers in the latest month
- `61,418` in MRR
- `264.73` ARPA
- `1.28%` logo churn
- `4.33` average CSAT
- `LATAM` as the strongest region by MRR
- `Scale` as the leading plan by total MRR

## Data Model

The pipeline generates a synthetic dataset with five core entities:

1. `customers.csv`
2. `subscriptions.csv`
3. `billing_events.csv`
4. `daily_product_usage.csv`
5. `support_tickets.csv`

These sources are transformed into a reusable analytical layer:

- `customer_monthly_metrics.csv`
- `monthly_kpis.csv`
- `cohort_retention.csv`
- `segment_summary.csv`
- `churn_risk_watchlist.csv`
- `revenue_anomalies.csv`

## Workflow

1. Generate source data: [src/generate_sample_data.py](src/generate_sample_data.py)
2. Build analytics outputs: [src/build_analytics.py](src/build_analytics.py)
3. Run the full pipeline: [src/run_pipeline.py](src/run_pipeline.py)
4. Review the dashboard: [src/dashboard.py](src/dashboard.py)
5. Query the SQLite layer: [sql/schema.sql](sql/schema.sql) and [sql/portfolio_queries.sql](sql/portfolio_queries.sql)

## Analytical Coverage

### KPI Layer

The project calculates recurring business metrics such as:

- active customers
- monthly recurring revenue
- collected revenue
- ARPA
- logo churn rate
- net revenue retention
- average CSAT
- average feature adoption

### Cohort Retention

Each customer is mapped to a signup cohort and tracked by `months_since_signup`, making it possible to review retention behavior over time.

### Churn Risk Scoring

Each customer-month record includes a risk score derived from:

- product usage versus trailing activity
- payment failures
- high-priority support tickets
- low CSAT
- contraction in recurring revenue

### Revenue Quality Monitoring

The analytics layer flags unusual revenue periods using MRR growth, churn, and NRR behavior.

## Why This Project Works Well In A Portfolio

This repository is useful for recruiter review and technical review because it goes beyond isolated notebook exploration.

It shows:

- a reproducible workflow
- business-oriented metrics
- reusable SQL assets
- exported outputs in CSV and Markdown
- a pipeline that materializes SQLite locally
- a dashboard that surfaces actionable signals

That makes it a strong project for roles involving `data analysis`, `business analytics`, `SQL`, `reporting`, and early `analytics engineering` foundations.

## Repository Structure

- [src/](src): pipeline scripts and dashboard
- [sql/](sql): schema and query assets
- [output/](output): representative analytical outputs
- [tests/](tests): unit tests
- [CHANGELOG.md](CHANGELOG.md): release notes

## Setup

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

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Pipeline

```bash
python src/run_pipeline.py
```

## Run The Dashboard

```bash
python -m streamlit run src/dashboard.py
```

## Run The Test Suite

```bash
python -m unittest discover -s tests
```

## Project Outputs

The public portfolio version keeps the repository lightweight. Running the pipeline regenerates the full source data, the customer-month analytical layer, and the SQLite database locally.

- KPI series: [output/monthly_kpis.csv](output/monthly_kpis.csv)
- Cohort retention: [output/cohort_retention.csv](output/cohort_retention.csv)
- Segment summary: [output/segment_summary.csv](output/segment_summary.csv)
- Churn watchlist: [output/churn_risk_watchlist.csv](output/churn_risk_watchlist.csv)
- Revenue anomalies: [output/revenue_anomalies.csv](output/revenue_anomalies.csv)
- Report preview: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)

## SQL Layer

The repository includes reusable SQL assets:

- schema and views: [sql/schema.sql](sql/schema.sql)
- portfolio query set: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)

The SQL layer is designed to support:

- latest KPI inspection
- retention review
- risk watchlists
- plan mix analysis
- regional health monitoring

## Interview Discussion Areas

1. Why the customer-month grain is useful for analytics and reporting
2. How cohort retention changes the interpretation of growth
3. Which signals are useful for churn risk scoring
4. Why revenue quality matters beyond raw revenue growth
5. How this project could evolve into a warehouse or BI workflow

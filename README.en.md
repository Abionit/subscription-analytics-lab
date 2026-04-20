# Subscription Analytics Lab - Revenue, Retention, and Churn Analysis

Advanced portfolio project that demonstrates practical data analysis skills with a subscription business dataset, a reusable SQL layer, and a dashboard for revenue and customer health monitoring.

## Problem Statement

Subscription businesses need more than a single revenue chart. Analysts are often expected to combine:

1. customer lifecycle context,
2. billing and collections behavior,
3. product usage patterns,
4. support signals,
5. retention and cohort analysis,
6. reporting that decision-makers can review quickly.

This project simulates that workflow end to end.

## Skills Demonstrated

- Python data processing and analytics engineering
- SQL reporting with SQLite
- Customer-month modeling for subscription analytics
- Cohort retention analysis
- Churn risk scoring from behavioral and operational signals
- KPI design for MRR, ARPA, churn, and net revenue retention
- Dashboard communication with Streamlit

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

## Architecture

1. Data generation: [src/generate_sample_data.py](src/generate_sample_data.py)
2. Analytics build step: [src/build_analytics.py](src/build_analytics.py)
3. Pipeline orchestration: [src/run_pipeline.py](src/run_pipeline.py)
4. Dashboard: [src/dashboard.py](src/dashboard.py)
5. SQL views: [sql/schema.sql](sql/schema.sql)
6. Portfolio queries: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)

## Analytical Features

### 1. Monthly KPI Layer

The project exports recurring metrics such as:

- active customers
- monthly recurring revenue
- collected revenue
- ARPA
- logo churn rate
- net revenue retention
- average CSAT
- average feature adoption

### 2. Cohort Retention

Each customer is mapped to a signup cohort and tracked by `months_since_signup`, making it possible to review retention behavior over time.

### 3. Churn Risk Scoring

Each customer-month record includes a risk score derived from:

- product usage versus trailing activity
- payment failures
- high-priority support tickets
- low CSAT
- contraction in recurring revenue

### 4. Revenue Quality Monitoring

The analytics layer flags unusual revenue periods using MRR growth, churn, and NRR behavior.

## Latest Snapshot

The current generated outputs show:

- `232` active customers in the latest month
- `61,418` in MRR
- `264.73` ARPA
- `1.28%` logo churn
- `4.33` average CSAT
- `LATAM` as the strongest region by MRR
- `Scale` as the leading plan by total MRR

## Why This Project Is Strong For Portfolio Use

This repository is useful for both analyst-facing and recruiter-facing review because it shows more than notebook-style exploration.

It includes:

- reproducible data generation
- a structured analytical data model
- SQL queries that can be reused
- exported outputs in CSV and Markdown
- a pipeline that materializes a SQLite database locally
- a dashboard that surfaces business and customer health signals

That makes it a strong project for roles involving `data analysis`, `business analytics`, `SQL`, `reporting`, and early `analytics engineering` foundations.

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

## Run the Pipeline

```bash
python src/run_pipeline.py
```

## Run the Dashboard

```bash
python -m streamlit run src/dashboard.py
```

## Run the Test Suite

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

## Technical Discussion Areas

1. How the customer-month grain supports analytics and reporting
2. Why cohort retention matters for subscription businesses
3. Which signals are useful for churn risk scoring
4. How revenue quality differs from raw revenue growth
5. How this project could evolve into a larger warehouse or BI workflow

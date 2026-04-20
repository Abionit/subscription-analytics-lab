# Subscription Analytics Lab

Advanced data analytics project focused on subscription revenue, retention, churn risk, cohort analysis, and SQL-backed reporting.

Documentation is available in two languages:

- English: [README.en.md](README.en.md)
- Espanol: [README.es.md](README.es.md)

## Quick Links

- English documentation: [README.en.md](README.en.md)
- Spanish documentation: [README.es.md](README.es.md)
- Version guide: [CHANGELOG.md](CHANGELOG.md)
- Pipeline runner: [src/run_pipeline.py](src/run_pipeline.py)
- Dashboard: [src/dashboard.py](src/dashboard.py)
- SQL queries: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)
- Sample report: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)
- Visual artifact: [evidence/v1/README.md](evidence/v1/README.md)

## Project Highlights

- Synthetic SaaS data model with customers, subscriptions, billing, usage, and support tickets
- Customer-month analytical layer with risk scoring and operational features
- Monthly KPI exports for MRR, ARPA, churn, and net revenue retention
- Cohort retention analysis and segment-level performance views
- SQLite database plus reusable SQL queries
- Streamlit dashboard for portfolio-ready review

## Project Outputs

- `data/customers.csv`
- `data/subscriptions.csv`
- `data/billing_events.csv`
- `data/daily_product_usage.csv`
- `data/support_tickets.csv`
- `output/customer_monthly_metrics.csv`
- `output/monthly_kpis.csv`
- `output/cohort_retention.csv`
- `output/segment_summary.csv`
- `output/churn_risk_watchlist.csv`
- `output/revenue_anomalies.csv`
- `output/subscription_analytics_report.md`
- `analytics/subscription_analytics.db`

## Quick Start

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

Install dependencies and run the project:

```bash
pip install -r requirements.txt
python src/run_pipeline.py
python -m streamlit run src/dashboard.py
```
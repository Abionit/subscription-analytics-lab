# Subscription Analytics Lab

Data engineering and analytics case study that consolidates subscription data into validated, query-ready datasets for KPI reporting, churn monitoring, cohort analysis, and revenue review.

Detailed documentation:

- English: [README.en.md](README.en.md)
- Espanol: [README.es.md](README.es.md)

## Fast Review

- Report preview: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)
- Data quality report: [output/data_quality_report.md](output/data_quality_report.md)
- SQL queries: [sql/portfolio_queries.sql](sql/portfolio_queries.sql)
- KPI outputs: [output/monthly_kpis.csv](output/monthly_kpis.csv)
- AWS architecture: [docs/aws_architecture.md](docs/aws_architecture.md)

## Best Role Fit

- Junior Data Engineer
- Analytics Engineer
- Data Analyst
- BI / Reporting Analyst

## Business Problem

A subscription company receives customer, subscription, billing, product usage, and support data from separate sources. The business needs reliable datasets for recurring revenue, retention, customer health, and churn-risk reporting.

## At A Glance

- Local stack: Python, pandas, SQL, SQLite, Streamlit
- AWS stack: S3, Glue, PySpark, Glue Data Catalog, Athena, CloudFormation
- Optional warehouse path: Amazon Redshift
- Sources integrated: customers, subscriptions, billing, product usage, and support
- Current snapshot: `232` active customers | `61,418` MRR | `264.73` ARPA | `1.28%` logo churn | `4.33` average CSAT

## What This Project Demonstrates

- Reproducible pipeline from five source datasets to analytical outputs
- Automated schema, key, foreign-key, range, and completeness checks
- Customer-month modeling for recurring revenue analysis
- KPI design for MRR, ARPA, churn, and net revenue retention
- Cohort retention and churn-risk analysis
- SQLite and reusable SQL for local review
- Deployment-ready AWS pipeline that writes partitioned Parquet to S3
- Athena queries and an optional Redshift warehouse path

## Local Workflow

1. Generate synthetic customer, billing, usage, and support data.
2. Validate schemas, keys, customer references, required values, and business ranges.
3. Build the customer-month analytical layer in Python.
4. Calculate recurring revenue, retention, churn, and risk metrics.
5. Export CSV and Markdown reports.
6. Materialize SQLite tables and views.
7. Review results in the Streamlit dashboard.

## AWS Workflow

The cloud path uploads the same five datasets to an S3 raw zone, runs a Glue PySpark transformation, writes partitioned Parquet to a curated zone, catalogs the outputs, and exposes them to Athena.

- Architecture: [docs/aws_architecture.md](docs/aws_architecture.md)
- Deployment guide: [docs/aws_deployment.md](docs/aws_deployment.md)
- Glue job: [aws/glue/subscription_etl.py](aws/glue/subscription_etl.py)
- Athena queries: [aws/athena/portfolio_queries.sql](aws/athena/portfolio_queries.sql)
- Redshift scripts: [aws/redshift/](aws/redshift)
- CloudFormation: [infrastructure/cloudformation.yaml](infrastructure/cloudformation.yaml)
- Execution evidence checklist: [evidence/aws/README.md](evidence/aws/README.md)

The AWS implementation is defined as code. It should only be described as deployed after real execution evidence is added.

## Repository Layout

- [src/](src): local pipeline, quality checks, and dashboard
- [sql/](sql): SQLite schema and analytical queries
- [aws/](aws): Glue, Athena, and Redshift assets
- [infrastructure/](infrastructure): CloudFormation template
- [docs/](docs): architecture and deployment documentation
- [output/](output): representative analytical and quality outputs
- [tests/](tests): unit tests

## Representative Outputs

- Data quality report: [output/data_quality_report.md](output/data_quality_report.md)
- KPI series: [output/monthly_kpis.csv](output/monthly_kpis.csv)
- Cohort retention: [output/cohort_retention.csv](output/cohort_retention.csv)
- Segment summary: [output/segment_summary.csv](output/segment_summary.csv)
- Churn watchlist: [output/churn_risk_watchlist.csv](output/churn_risk_watchlist.csv)
- Revenue anomalies: [output/revenue_anomalies.csv](output/revenue_anomalies.csv)
- Business report: [output/subscription_analytics_report.md](output/subscription_analytics_report.md)

## Run Locally

```bash
python -m venv .venv
```

Activate the environment and run:

```bash
pip install -r requirements.txt
python src/run_pipeline.py
python -m unittest discover -s tests
python -m streamlit run src/dashboard.py
```

Running the pipeline regenerates source data under `data/`, the analytical layer, quality reports, and the SQLite database under `analytics/`.

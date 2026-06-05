# Changelog

This project records notable changes by release. Versioned entries describe completed capabilities; work awaiting a release remains under `Unreleased`.

## Unreleased

- branch and commit conventions
- pull request and issue templates
- CI validation for Python, unit tests, and CloudFormation
- repository rules for credentials, generated data, tooling, and line endings

## v2

Added a data engineering path with:

- automated local data quality gate
- quality reports in Markdown and JSON
- AWS Glue PySpark transformation
- S3 raw and curated data zones
- partitioned Parquet outputs
- Glue Data Catalog crawler
- Athena workgroup and analytical queries
- optional Redshift schema and load scripts
- CloudFormation infrastructure
- CI tests and AWS deployment documentation

## v1

Initial public portfolio release with:

- synthetic subscription business dataset
- customer-month analytical layer
- KPI exports for revenue and retention
- cohort analysis
- churn risk watchlist
- revenue anomaly detection
- SQLite database and reusable SQL queries
- Streamlit dashboard

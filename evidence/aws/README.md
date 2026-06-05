# AWS Execution Evidence

This folder is reserved for evidence captured after deploying the project in an AWS account.

| File | What it should show |
| --- | --- |
| `01_cloudformation_stack.png` | Created S3, Glue, IAM, and Athena resources |
| `02_s3_raw_zone.png` | Five source datasets organized by prefix |
| `03_glue_job_success.png` | Successful PySpark job run |
| `04_s3_curated_zone.png` | Partitioned Parquet outputs and quality results |
| `05_glue_catalog.png` | Curated tables in the Data Catalog |
| `06_athena_kpi_query.png` | KPI query against curated data |
| `07_athena_quality_query.png` | Data quality history in Athena |
| `08_redshift_query.png` | Optional warehouse load and query result |

Only add screenshots from a real execution. Remove account IDs, usernames, bucket names, and other sensitive details before publishing.

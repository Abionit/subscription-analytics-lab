# AWS Deployment Guide

## Prerequisites

- AWS account with access to CloudFormation, S3, IAM, Glue, and Athena.
- AWS CLI configured locally.
- Python 3.11 or later.

## 1. Run And Validate Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py
python -m unittest discover -s tests
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

The pipeline must finish with a passing `output/data_quality_report.md`.

## 2. Create AWS Resources

```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation.yaml \
  --stack-name subscription-analytics-pipeline \
  --capabilities CAPABILITY_IAM
```

Read generated resource names:

```bash
aws cloudformation describe-stacks \
  --stack-name subscription-analytics-pipeline \
  --query "Stacks[0].Outputs"
```

## 3. Upload Sources And Assets

```bash
python scripts/upload_to_s3.py \
  --raw-bucket RAW_BUCKET_NAME \
  --artifacts-bucket ARTIFACTS_BUCKET_NAME
```

Use `--profile PROFILE_NAME` when needed.

## 4. Run Glue

```bash
aws glue start-job-run --job-name subscription-analytics-etl
aws glue get-job-runs --job-name subscription-analytics-etl --max-results 1
```

## 5. Update The Data Catalog

```bash
aws glue start-crawler --name subscription-analytics-curated-crawler
```

## 6. Query With Athena

Use the generated workgroup and run `aws/athena/portfolio_queries.sql`.

Useful portfolio evidence includes the latest KPI query, high-risk customers, regional health, and data quality history.

## 7. Optional Redshift Load

If a Redshift cluster or Serverless workgroup is available:

1. Run `aws/redshift/schema.sql`.
2. Replace placeholders in `aws/redshift/load.sql`.
3. Run the `COPY` commands with an IAM role that can read the curated bucket.

## Evidence

Do not publish credentials, account IDs, usernames, or private bucket names. Capture the stack resources, S3 zones, successful Glue run, Data Catalog tables, Athena results, and optional Redshift results.

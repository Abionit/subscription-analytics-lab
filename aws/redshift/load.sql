-- Replace the placeholders before running this script.
-- The IAM role must allow Redshift to read the curated S3 prefix.

TRUNCATE TABLE analytics.monthly_kpis;

COPY analytics.monthly_kpis
FROM 's3://CURATED_BUCKET/curated/monthly_kpis/'
IAM_ROLE 'arn:aws:iam::ACCOUNT_ID:role/REDSHIFT_S3_ROLE'
FORMAT AS PARQUET;

TRUNCATE TABLE analytics.customer_monthly_metrics;

COPY analytics.customer_monthly_metrics
FROM 's3://CURATED_BUCKET/curated/customer_monthly_metrics/'
IAM_ROLE 'arn:aws:iam::ACCOUNT_ID:role/REDSHIFT_S3_ROLE'
FORMAT AS PARQUET;

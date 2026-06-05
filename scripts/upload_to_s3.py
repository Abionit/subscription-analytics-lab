from __future__ import annotations

import argparse
from pathlib import Path

import boto3


BASE_DIR = Path(__file__).resolve().parents[1]
DATASETS = {
    "customers.csv": "customers",
    "subscriptions.csv": "subscriptions",
    "billing_events.csv": "billing_events",
    "daily_product_usage.csv": "daily_product_usage",
    "support_tickets.csv": "support_tickets",
}


def upload_file(client, source: Path, bucket: str, key: str) -> None:
    client.upload_file(str(source), bucket, key)
    print(f"Uploaded {source.name} -> s3://{bucket}/{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload pipeline sources and AWS assets to S3.")
    parser.add_argument("--raw-bucket", required=True)
    parser.add_argument("--artifacts-bucket", required=True)
    parser.add_argument("--profile")
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    s3 = session.client("s3")

    for filename, dataset in DATASETS.items():
        source = BASE_DIR / "data" / filename
        if not source.exists():
            raise FileNotFoundError(f"{source} does not exist. Run python src/run_pipeline.py first.")
        upload_file(s3, source, args.raw_bucket, f"raw/{dataset}/{filename}")

    upload_file(s3, BASE_DIR / "aws" / "glue" / "subscription_etl.py", args.artifacts_bucket, "jobs/subscription_etl.py")
    upload_file(s3, BASE_DIR / "aws" / "athena" / "portfolio_queries.sql", args.artifacts_bucket, "sql/athena/portfolio_queries.sql")


if __name__ == "__main__":
    main()

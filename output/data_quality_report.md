# Data Quality Report

- Checks executed: 24
- Passed: 24
- Failed: 0
- Pipeline status: PASSED

| Dataset | Check | Status | Failed rows | Detail |
| --- | --- | --- | ---: | --- |
| customers | required_columns | PASS | 0 | All required columns are present. |
| customers | primary_key | PASS | 0 | customer_id is complete and unique. |
| customers | required_values | PASS | 0 | Required fields contain no null values. |
| customers | customer_foreign_key | PASS | 0 | Source table for customer keys. |
| customers | valid_customer_categories | PASS | 0 | Customer status and health values are within the accepted domains. |
| subscriptions | required_columns | PASS | 0 | All required columns are present. |
| subscriptions | primary_key | PASS | 0 | customer_id is complete and unique. |
| subscriptions | required_values | PASS | 0 | Required fields contain no null values. |
| subscriptions | customer_foreign_key | PASS | 0 | All customer references are valid. |
| billing_events | required_columns | PASS | 0 | All required columns are present. |
| billing_events | primary_key | PASS | 0 | event_id is complete and unique. |
| billing_events | required_values | PASS | 0 | Required fields contain no null values. |
| billing_events | customer_foreign_key | PASS | 0 | All customer references are valid. |
| billing_events | non_negative_revenue | PASS | 0 | Revenue fields are non-negative. |
| daily_product_usage | required_columns | PASS | 0 | All required columns are present. |
| daily_product_usage | primary_key | PASS | 0 | No single-column primary key is defined. |
| daily_product_usage | required_values | PASS | 0 | Required fields contain no null values. |
| daily_product_usage | customer_foreign_key | PASS | 0 | All customer references are valid. |
| daily_product_usage | valid_usage_metrics | PASS | 0 | Usage metrics are non-negative and feature adoption is between 0 and 1. |
| support_tickets | required_columns | PASS | 0 | All required columns are present. |
| support_tickets | primary_key | PASS | 0 | ticket_id is complete and unique. |
| support_tickets | required_values | PASS | 0 | Required fields contain no null values. |
| support_tickets | customer_foreign_key | PASS | 0 | All customer references are valid. |
| support_tickets | valid_support_metrics | PASS | 0 | Ticket severity, resolution time, and CSAT are within accepted ranges. |

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.monthly_kpis (
    metric_month DATE,
    active_customers INTEGER,
    mrr DECIMAL(18, 2),
    collected_revenue DECIMAL(18, 2),
    churned_customers INTEGER,
    payment_failures INTEGER,
    avg_csat DECIMAL(5, 2),
    avg_feature_adoption DECIMAL(6, 3),
    arpa DECIMAL(18, 2),
    metric_year SMALLINT,
    metric_month_number SMALLINT
)
DISTSTYLE AUTO
SORTKEY (metric_month);

CREATE TABLE IF NOT EXISTS analytics.customer_monthly_metrics (
    customer_id VARCHAR(20),
    metric_month DATE,
    company_name VARCHAR(200),
    region VARCHAR(50),
    industry VARCHAR(100),
    company_segment VARCHAR(50),
    plan_name VARCHAR(50),
    ending_mrr DECIMAL(18, 2),
    payment_collected DECIMAL(18, 2),
    payment_failures INTEGER,
    ticket_count INTEGER,
    high_priority_tickets INTEGER,
    avg_csat DECIMAL(5, 2),
    risk_score INTEGER,
    risk_band VARCHAR(20),
    metric_year SMALLINT,
    metric_month_number SMALLINT
)
DISTSTYLE AUTO
SORTKEY (metric_month, customer_id);

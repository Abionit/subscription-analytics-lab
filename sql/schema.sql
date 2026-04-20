DROP VIEW IF EXISTS monthly_plan_mix;
CREATE VIEW monthly_plan_mix AS
SELECT
    metric_month,
    plan_name,
    COUNT(*) AS active_customers,
    ROUND(SUM(ending_mrr), 2) AS mrr
FROM customer_monthly_metrics
WHERE active_customer = 1
GROUP BY metric_month, plan_name;

DROP VIEW IF EXISTS regional_health_summary;
CREATE VIEW regional_health_summary AS
SELECT
    metric_month,
    region,
    ROUND(SUM(ending_mrr), 2) AS mrr,
    ROUND(AVG(avg_csat), 2) AS avg_csat,
    ROUND(AVG(risk_score), 2) AS avg_risk_score,
    SUM(CASE WHEN risk_band = 'high' THEN 1 ELSE 0 END) AS high_risk_accounts
FROM customer_monthly_metrics
GROUP BY metric_month, region;

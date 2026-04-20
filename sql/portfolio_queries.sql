-- Latest monthly KPI snapshot
SELECT
    metric_month,
    active_customers,
    mrr,
    arpa,
    logo_churn_rate_pct,
    net_revenue_retention_pct
FROM monthly_kpis
ORDER BY metric_month DESC
LIMIT 6;

-- Cohort retention by signup month and tenure month
SELECT
    signup_month,
    months_since_signup,
    retained_customers,
    cohort_size,
    retention_rate_pct
FROM cohort_retention
ORDER BY signup_month, months_since_signup;

-- Current high-risk accounts with revenue exposure
SELECT
    customer_id,
    company_name,
    region,
    plan_name,
    ending_mrr,
    risk_score,
    risk_band,
    payment_failures,
    high_priority_tickets,
    avg_csat
FROM customer_monthly_metrics
WHERE metric_month = (SELECT MAX(metric_month) FROM customer_monthly_metrics)
  AND risk_band = 'high'
ORDER BY risk_score DESC, ending_mrr DESC;

-- Monthly plan mix
SELECT
    metric_month,
    plan_name,
    active_customers,
    mrr
FROM monthly_plan_mix
ORDER BY metric_month, mrr DESC;

-- Regional health summary
SELECT
    metric_month,
    region,
    mrr,
    avg_csat,
    avg_risk_score,
    high_risk_accounts
FROM regional_health_summary
ORDER BY metric_month DESC, mrr DESC;

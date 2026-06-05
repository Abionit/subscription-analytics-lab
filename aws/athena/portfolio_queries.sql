-- Latest monthly KPI snapshot
SELECT metric_month, active_customers, mrr, arpa, collected_revenue,
       churned_customers, payment_failures, avg_csat, avg_feature_adoption
FROM subscription_analytics.monthly_kpis
ORDER BY metric_month DESC
LIMIT 12;

-- High-risk accounts with the largest recurring-revenue exposure
SELECT customer_id, company_name, region, company_segment, plan_name,
       ending_mrr, risk_score, risk_band, payment_failures,
       high_priority_tickets, avg_csat
FROM subscription_analytics.customer_monthly_metrics
WHERE metric_month = (
    SELECT MAX(metric_month)
    FROM subscription_analytics.customer_monthly_metrics
)
  AND risk_band = 'high'
ORDER BY ending_mrr DESC, risk_score DESC
LIMIT 25;

-- Revenue and customer health by region
SELECT metric_month, region,
       COUNT(DISTINCT customer_id) AS customers,
       ROUND(SUM(ending_mrr), 2) AS mrr,
       ROUND(AVG(avg_csat), 2) AS avg_csat,
       SUM(CASE WHEN risk_band = 'high' THEN 1 ELSE 0 END) AS high_risk_accounts
FROM subscription_analytics.customer_monthly_metrics
GROUP BY metric_month, region
ORDER BY metric_month DESC, mrr DESC;

-- Data quality history written by the Glue job
SELECT run_id, dataset, "check", status, failed_rows, detail
FROM subscription_analytics.data_quality
ORDER BY run_id DESC, dataset, "check";

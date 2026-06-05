from __future__ import annotations

import unittest

import pandas as pd

from src.data_quality import validate_frames


def valid_frames() -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.DataFrame([{"customer_id": "C0001", "company_name": "North Labs", "signup_date": "2025-01-01", "region": "LATAM", "industry": "SaaS", "acquisition_channel": "Organic", "company_segment": "SMB", "status": "active", "initial_plan": "Starter", "current_plan": "Starter", "health_band": "stable"}]),
        "subscriptions": pd.DataFrame([{"customer_id": "C0001", "start_date": "2025-01-01", "status": "active", "initial_plan": "Starter", "current_plan": "Starter", "health_band": "stable"}]),
        "billing_events": pd.DataFrame([{"event_id": "BE-1", "customer_id": "C0001", "billing_month": "2025-01-01", "plan_name": "Starter", "event_type": "invoice_paid", "invoice_amount": 49, "payment_collected": 49, "mrr_before": 0, "mrr_after": 49, "delta_mrr": 49}]),
        "daily_product_usage": pd.DataFrame([{"usage_date": "2025-01-01", "customer_id": "C0001", "active_users": 10, "api_calls": 1000, "workflow_runs": 20, "feature_adoption_score": 0.7}]),
        "support_tickets": pd.DataFrame([{"ticket_id": "TK-1", "customer_id": "C0001", "opened_at": "2025-01-01T09:00:00", "severity": "low", "resolution_hours": 4, "csat": 4.5}]),
    }


class DataQualityTests(unittest.TestCase):
    def test_valid_sources_pass_all_checks(self) -> None:
        checks = validate_frames(valid_frames())
        self.assertTrue(checks)
        self.assertFalse([check for check in checks if check.status == "fail"])

    def test_unknown_customer_fails_foreign_key_check(self) -> None:
        frames = valid_frames()
        frames["billing_events"].loc[0, "customer_id"] = "UNKNOWN"
        failures = [check for check in validate_frames(frames) if check.status == "fail"]
        self.assertTrue(any(check.dataset == "billing_events" and check.check == "customer_foreign_key" for check in failures))

    def test_invalid_business_values_are_rejected(self) -> None:
        frames = valid_frames()
        frames["daily_product_usage"].loc[0, "feature_adoption_score"] = 1.4
        frames["support_tickets"].loc[0, "csat"] = 7
        failures = [check for check in validate_frames(frames) if check.status == "fail"]
        failed_names = {(check.dataset, check.check) for check in failures}
        self.assertIn(("daily_product_usage", "valid_usage_metrics"), failed_names)
        self.assertIn(("support_tickets", "valid_support_metrics"), failed_names)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

import pandas as pd

from src.build_analytics import compute_risk_score, risk_band


class RiskScoringTests(unittest.TestCase):
    def test_high_risk_customers_are_scored_aggressively(self) -> None:
        row = pd.Series(
            {
                "usage_ratio_vs_trailing_3m": 0.51,
                "payment_failures": 2,
                "high_priority_tickets": 3,
                "avg_csat": 3.1,
                "contraction_mrr": -149,
            }
        )
        score = compute_risk_score(row)
        self.assertGreaterEqual(score, 80)
        self.assertEqual(risk_band(score), "high")

    def test_low_risk_customers_remain_low(self) -> None:
        row = pd.Series(
            {
                "usage_ratio_vs_trailing_3m": 1.02,
                "payment_failures": 0,
                "high_priority_tickets": 0,
                "avg_csat": 4.6,
                "contraction_mrr": 0,
            }
        )
        score = compute_risk_score(row)
        self.assertLess(score, 35)
        self.assertEqual(risk_band(score), "low")


if __name__ == "__main__":
    unittest.main()

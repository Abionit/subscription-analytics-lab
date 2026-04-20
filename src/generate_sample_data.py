from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
ANALYSIS_END = pd.Timestamp("2026-03-31")

PLAN_CONFIG = {
    "Starter": {"mrr": 49, "usage": 24, "api": 3500},
    "Growth": {"mrr": 149, "usage": 72, "api": 14000},
    "Scale": {"mrr": 399, "usage": 180, "api": 46000},
    "Enterprise": {"mrr": 999, "usage": 520, "api": 145000},
}

REGIONS = ["North America", "LATAM", "EMEA"]
INDUSTRIES = ["Fintech", "Healthcare", "E-commerce", "Logistics", "SaaS", "EdTech"]
CHANNELS = ["Organic", "Paid Search", "Referral", "Partnerships", "Outbound"]
COMPANY_SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
TICKET_CATEGORIES = ["Billing", "Product", "Integrations", "Onboarding", "Performance"]
SEVERITY_WEIGHTS = [("low", 0.54), ("medium", 0.28), ("high", 0.13), ("critical", 0.05)]


@dataclass
class CustomerProfile:
    customer_id: str
    company_name: str
    signup_date: pd.Timestamp
    region: str
    industry: str
    acquisition_channel: str
    company_segment: str
    initial_plan: str
    current_plan: str
    status: str
    end_date: pd.Timestamp | None
    health_band: str


def weighted_choice(choices: list[tuple[str, float]]) -> str:
    labels = [label for label, _ in choices]
    weights = [weight for _, weight in choices]
    return random.choices(labels, weights=weights, k=1)[0]


def build_customers() -> tuple[pd.DataFrame, pd.DataFrame]:
    random.seed(SEED)
    customers: list[CustomerProfile] = []
    subscriptions: list[dict] = []
    signup_dates = pd.date_range("2025-01-01", "2025-12-15", freq="3D")

    for index in range(1, 241):
        signup_date = random.choice(list(signup_dates))
        region = random.choices(REGIONS, weights=[0.38, 0.34, 0.28], k=1)[0]
        segment = random.choices(COMPANY_SEGMENTS, weights=[0.48, 0.37, 0.15], k=1)[0]
        initial_plan = random.choices(
            ["Starter", "Growth", "Scale", "Enterprise"],
            weights=[0.44, 0.34, 0.17, 0.05],
            k=1,
        )[0]
        health_band = random.choices(
            ["expansion", "stable", "at_risk"],
            weights=[0.22, 0.58, 0.20],
            k=1,
        )[0]
        lifetime_months = random.randint(3, 14)
        churn_happens = health_band == "at_risk" and random.random() < 0.42
        tentative_end = signup_date + pd.DateOffset(months=lifetime_months)
        end_date = (
            pd.Timestamp(min(tentative_end, ANALYSIS_END))
            if churn_happens and tentative_end <= ANALYSIS_END
            else None
        )
        status = "churned" if end_date is not None else "active"
        current_plan = initial_plan

        if health_band == "expansion" and initial_plan != "Enterprise":
            upgrade_path = ["Starter", "Growth", "Scale", "Enterprise"]
            current_plan = upgrade_path[min(upgrade_path.index(initial_plan) + random.randint(1, 2), 3)]
        elif health_band == "at_risk" and initial_plan in {"Scale", "Enterprise"} and random.random() < 0.35:
            downgrade_path = ["Starter", "Growth", "Scale", "Enterprise"]
            current_plan = downgrade_path[max(downgrade_path.index(initial_plan) - 1, 0)]

        customer = CustomerProfile(
            customer_id=f"C{index:04d}",
            company_name=f"{random.choice(['North', 'Blue', 'Nova', 'Vertex', 'Prime', 'Apex', 'Bright', 'Delta'])}{random.choice(['Labs', 'Works', 'Systems', 'Cloud', 'Retail', 'Health', 'Logix', 'Data'])}",
            signup_date=signup_date,
            region=region,
            industry=random.choice(INDUSTRIES),
            acquisition_channel=random.choice(CHANNELS),
            company_segment=segment,
            initial_plan=initial_plan,
            current_plan=current_plan,
            status=status,
            end_date=end_date,
            health_band=health_band,
        )
        customers.append(customer)

        subscriptions.append(
            {
                "customer_id": customer.customer_id,
                "company_name": customer.company_name,
                "signup_date": customer.signup_date.date().isoformat(),
                "start_date": customer.signup_date.date().isoformat(),
                "end_date": customer.end_date.date().isoformat() if customer.end_date is not None else "",
                "status": customer.status,
                "initial_plan": customer.initial_plan,
                "current_plan": customer.current_plan,
                "health_band": customer.health_band,
            }
        )

    customers_df = pd.DataFrame(
        {
            "customer_id": [customer.customer_id for customer in customers],
            "company_name": [customer.company_name for customer in customers],
            "signup_date": [customer.signup_date.date().isoformat() for customer in customers],
            "region": [customer.region for customer in customers],
            "industry": [customer.industry for customer in customers],
            "acquisition_channel": [customer.acquisition_channel for customer in customers],
            "company_segment": [customer.company_segment for customer in customers],
        }
    )
    subscriptions_df = pd.DataFrame(subscriptions)
    return customers_df, subscriptions_df


def plan_for_month(subscription_row: pd.Series, month_index: int) -> str:
    plan_order = ["Starter", "Growth", "Scale", "Enterprise"]
    initial_plan = subscription_row["initial_plan"]
    current_plan = subscription_row["current_plan"]
    health_band = subscription_row["health_band"]

    if initial_plan == current_plan:
        return current_plan

    if health_band == "expansion":
        initial_idx = plan_order.index(initial_plan)
        current_idx = plan_order.index(current_plan)
        if month_index <= 2:
            return initial_plan
        if month_index <= 6 and current_idx - initial_idx >= 2:
            return plan_order[initial_idx + 1]
        return current_plan

    if health_band == "at_risk":
        return initial_plan if month_index <= 4 else current_plan

    return current_plan


def build_billing_events(subscriptions_df: pd.DataFrame) -> pd.DataFrame:
    random.seed(SEED + 1)
    events: list[dict] = []

    for _, row in subscriptions_df.iterrows():
        signup_date = pd.Timestamp(row["signup_date"])
        end_date = pd.Timestamp(row["end_date"]) if row["end_date"] else ANALYSIS_END
        month_starts = pd.date_range(signup_date.to_period("M").to_timestamp(), end_date.to_period("M").to_timestamp(), freq="MS")
        previous_mrr = 0

        for month_index, month_start in enumerate(month_starts):
            if month_start < signup_date.to_period("M").to_timestamp():
                continue

            plan_name = plan_for_month(row, month_index)
            target_mrr = PLAN_CONFIG[plan_name]["mrr"]
            payment_failed = row["health_band"] == "at_risk" and random.random() < 0.18
            if row["health_band"] == "stable":
                payment_failed = random.random() < 0.05
            if row["status"] == "churned" and month_start == end_date.to_period("M").to_timestamp():
                event_type = "churn"
                amount = 0
                mrr_after = 0
                delta_mrr = -previous_mrr
            else:
                event_type = "invoice_paid"
                amount = target_mrr
                mrr_after = target_mrr
                delta_mrr = target_mrr - previous_mrr
                if payment_failed:
                    event_type = "payment_failed"

            event_date = month_start + pd.Timedelta(days=random.randint(0, 6))
            events.append(
                {
                    "event_id": f"BE-{row['customer_id']}-{month_start.strftime('%Y%m')}",
                    "customer_id": row["customer_id"],
                    "event_date": event_date.date().isoformat(),
                    "billing_month": month_start.date().isoformat(),
                    "plan_name": plan_name,
                    "event_type": event_type,
                    "invoice_amount": amount,
                    "payment_collected": 0 if event_type == "payment_failed" else amount,
                    "mrr_before": previous_mrr,
                    "mrr_after": mrr_after,
                    "delta_mrr": delta_mrr,
                }
            )
            previous_mrr = mrr_after if event_type != "payment_failed" else previous_mrr

    return pd.DataFrame(events).sort_values(["billing_month", "customer_id"]).reset_index(drop=True)


def build_daily_usage(subscriptions_df: pd.DataFrame) -> pd.DataFrame:
    random.seed(SEED + 2)
    daily_usage: list[dict] = []

    for _, row in subscriptions_df.iterrows():
        start_date = pd.Timestamp(row["signup_date"])
        end_date = pd.Timestamp(row["end_date"]) if row["end_date"] else ANALYSIS_END
        date_range = pd.date_range(start_date, end_date, freq="D")

        base_multiplier = {"SMB": 1.0, "Mid-Market": 1.7, "Enterprise": 3.8}
        segment_multiplier = base_multiplier[row["company_segment"]]

        for current_date in date_range:
            month_index = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month
            plan_name = plan_for_month(row, max(month_index, 0))
            plan_profile = PLAN_CONFIG[plan_name]
            engagement_factor = {"expansion": 1.18, "stable": 0.97, "at_risk": 0.63}[row["health_band"]]
            weekday_factor = 0.86 if current_date.weekday() >= 5 else 1.04
            active_users = max(
                2,
                int(random.gauss(plan_profile["usage"] * segment_multiplier * engagement_factor * weekday_factor, 7)),
            )
            api_calls = max(
                800,
                int(random.gauss(plan_profile["api"] * segment_multiplier * engagement_factor * weekday_factor, 1600)),
            )
            workflow_runs = max(1, int(active_users * random.uniform(1.8, 3.6)))
            feature_adoption = round(
                min(
                    0.98,
                    max(
                        0.18,
                        random.gauss(
                            {"expansion": 0.78, "stable": 0.62, "at_risk": 0.37}[row["health_band"]],
                            0.08,
                        ),
                    ),
                ),
                3,
            )
            daily_usage.append(
                {
                    "usage_date": current_date.date().isoformat(),
                    "customer_id": row["customer_id"],
                    "active_users": active_users,
                    "api_calls": api_calls,
                    "workflow_runs": workflow_runs,
                    "feature_adoption_score": feature_adoption,
                }
            )

    return pd.DataFrame(daily_usage)


def build_support_tickets(subscriptions_df: pd.DataFrame) -> pd.DataFrame:
    random.seed(SEED + 3)
    tickets: list[dict] = []

    for _, row in subscriptions_df.iterrows():
        signup_date = pd.Timestamp(row["signup_date"])
        end_date = pd.Timestamp(row["end_date"]) if row["end_date"] else ANALYSIS_END
        month_starts = pd.date_range(signup_date.to_period("M").to_timestamp(), end_date.to_period("M").to_timestamp(), freq="MS")

        for month_index, month_start in enumerate(month_starts):
            base_ticket_rate = {"expansion": 0.8, "stable": 1.2, "at_risk": 2.8}[row["health_band"]]
            ticket_count = max(0, int(random.gauss(base_ticket_rate, 1.1)))
            if row["company_segment"] == "Enterprise":
                ticket_count += random.randint(0, 2)
            if month_index <= 1:
                ticket_count += 1

            for ticket_number in range(ticket_count):
                severity = weighted_choice(SEVERITY_WEIGHTS)
                opened_at = month_start + pd.Timedelta(days=random.randint(0, 27), hours=random.randint(0, 23))
                resolution_hours = round(
                    max(2, random.gauss({"low": 8, "medium": 18, "high": 42, "critical": 76}[severity], 4)),
                    1,
                )
                csat = round(
                    min(
                        5.0,
                        max(
                            1.8,
                            random.gauss(
                                {"expansion": 4.6, "stable": 4.1, "at_risk": 3.2}[row["health_band"]],
                                0.35,
                            ),
                        ),
                    ),
                    1,
                )
                tickets.append(
                    {
                        "ticket_id": f"TK-{row['customer_id']}-{month_start.strftime('%Y%m')}-{ticket_number + 1}",
                        "customer_id": row["customer_id"],
                        "opened_at": opened_at.isoformat(),
                        "ticket_category": random.choice(TICKET_CATEGORIES),
                        "severity": severity,
                        "resolution_hours": resolution_hours,
                        "csat": csat,
                    }
                )

    return pd.DataFrame(tickets).sort_values("opened_at").reset_index(drop=True)


def main() -> None:
    customers_df, subscriptions_df = build_customers()
    customers_enriched = customers_df.merge(
        subscriptions_df[["customer_id", "status", "initial_plan", "current_plan", "health_band", "end_date"]],
        on="customer_id",
        how="left",
    )
    billing_df = build_billing_events(subscriptions_df.merge(customers_df[["customer_id", "company_segment"]], on="customer_id"))
    usage_df = build_daily_usage(subscriptions_df.merge(customers_df[["customer_id", "company_segment"]], on="customer_id"))
    tickets_df = build_support_tickets(subscriptions_df.merge(customers_df[["customer_id", "company_segment"]], on="customer_id"))

    customers_enriched.to_csv(DATA_DIR / "customers.csv", index=False)
    subscriptions_df.to_csv(DATA_DIR / "subscriptions.csv", index=False)
    billing_df.to_csv(DATA_DIR / "billing_events.csv", index=False)
    usage_df.to_csv(DATA_DIR / "daily_product_usage.csv", index=False)
    tickets_df.to_csv(DATA_DIR / "support_tickets.csv", index=False)

    print("Generated sample data:")
    print(f"- customers.csv: {len(customers_enriched)} rows")
    print(f"- subscriptions.csv: {len(subscriptions_df)} rows")
    print(f"- billing_events.csv: {len(billing_df)} rows")
    print(f"- daily_product_usage.csv: {len(usage_df)} rows")
    print(f"- support_tickets.csv: {len(tickets_df)} rows")


if __name__ == "__main__":
    main()

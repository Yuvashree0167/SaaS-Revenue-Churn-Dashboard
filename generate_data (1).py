"""Generates a synthetic SaaS subscription dataset (data.csv)."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa"]
categories = ["Starter", "Professional", "Enterprise", "Add-ons"]
base_ticket = {"Starter": 40, "Professional": 120, "Enterprise": 480, "Add-ons": 25}
region_weight = {"North America": 1.3, "Europe": 1.1, "Asia Pacific": 1.2,
                 "Latin America": 0.7, "Middle East & Africa": 0.6}

dates = pd.date_range("2025-01-01", "2026-10-18", freq="D")
rows = []
for d in dates:
    growth = 1 + 0.0009 * (d - dates[0]).days          # steady growth
    season = 1 + 0.12 * np.sin(2 * np.pi * d.dayofyear / 365)
    for r in regions:
        for c in categories:
            orders = rng.poisson(6 * growth * season * region_weight[r])
            if orders == 0:
                continue
            ticket = base_ticket[c] * rng.normal(1, 0.12)
            rows.append({
                "date": d,
                "region": r,
                "category": c,
                "orders": orders,
                "revenue": round(orders * ticket, 2),
                "active_users": int(orders * rng.uniform(3, 6)),
                "churned_users": int(orders * rng.uniform(0.1, 0.45)),
            })

df = pd.DataFrame(rows)
df.to_csv("data.csv", index=False)
print(f"Wrote data.csv with {len(df):,} rows")

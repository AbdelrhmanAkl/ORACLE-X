import sqlite3
import math

import pandas as pd

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

START_DATE = "2018-08-01"
END_DATE = "2018-08-22"

# Simulation assumptions.
# These are not historical facts.
BASELINE_COVER_DAYS = 14
REORDER_COVER_DAYS = 7


conn = sqlite3.connect(DB_PATH)


# ============================================================
# 1. DAILY PRODUCT DEMAND
# ============================================================

query = f"""
SELECT
    oi.product_id,
    DATE(o.order_purchase_timestamp) AS date,
    SUM(oi.order_item_id) AS units_sold,
    SUM(oi.price) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE DATE(o.order_purchase_timestamp)
      BETWEEN '{START_DATE}' AND '{END_DATE}'
GROUP BY
    oi.product_id,
    DATE(o.order_purchase_timestamp)
ORDER BY
    oi.product_id,
    date;
"""

daily = pd.read_sql_query(query, conn)


if daily.empty:
    raise RuntimeError("No product demand data found for the baseline period.")


# ============================================================
# 2. PRODUCT-LEVEL DEMAND METRICS
# ============================================================

inventory = (
    daily.groupby("product_id")
    .agg(
        baseline_units_sold=("units_sold", "sum"),
        baseline_revenue=("revenue", "sum"),
        active_days=("date", "count"),
        average_daily_demand=("units_sold", "mean"),
        demand_std=("units_sold", "std"),
    )
    .reset_index()
)

inventory["demand_std"] = inventory["demand_std"].fillna(0)

inventory["average_price"] = (
    inventory["baseline_revenue"]
    / inventory["baseline_units_sold"]
)

inventory["demand_cv"] = (
    inventory["demand_std"]
    / inventory["average_daily_demand"].replace(0, pd.NA)
)

inventory["demand_cv"] = (
    inventory["demand_cv"]
    .fillna(0)
)


# ============================================================
# 3. ESTIMATED INVENTORY STATE
# ============================================================

inventory["estimated_stock"] = (
    inventory["average_daily_demand"]
    * BASELINE_COVER_DAYS
)

inventory["reorder_point"] = (
    inventory["average_daily_demand"]
    * REORDER_COVER_DAYS
)

inventory["days_of_cover"] = (
    inventory["estimated_stock"]
    / inventory["average_daily_demand"].replace(0, pd.NA)
)

inventory["days_of_cover"] = (
    inventory["days_of_cover"]
    .fillna(0)
)


# ============================================================
# 4. STOCKOUT RISK
# ============================================================

def classify_stock_risk(row):
    days = row["days_of_cover"]
    cv = row["demand_cv"]

    if days < 3:
        return "CRITICAL"

    if days < 7:
        return "HIGH"

    if days < 14 and cv >= 0.75:
        return "HIGH"

    if days < 14:
        return "MEDIUM"

    return "LOW"


inventory["stockout_risk"] = inventory.apply(
    classify_stock_risk,
    axis=1
)


# ============================================================
# 5. PRODUCT INFORMATION
# ============================================================

product_query = """
SELECT
    p.product_id,
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM products p
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name;
"""

products = pd.read_sql_query(product_query, conn)


inventory = inventory.merge(
    products,
    on="product_id",
    how="left"
)


# ============================================================
# 6. CLEAN NUMERIC VALUES
# ============================================================

numeric_columns = [
    "baseline_units_sold",
    "baseline_revenue",
    "active_days",
    "average_daily_demand",
    "demand_std",
    "average_price",
    "demand_cv",
    "estimated_stock",
    "reorder_point",
    "days_of_cover",
]

for column in numeric_columns:
    inventory[column] = (
        pd.to_numeric(
            inventory[column],
            errors="coerce"
        )
        .fillna(0)
    )


# ============================================================
# 7. SAVE TO DATABASE
# ============================================================

inventory.to_sql(
    "inventory_v2",
    conn,
    if_exists="replace",
    index=False
)


# ============================================================
# 8. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("ORACLE-X INVENTORY INTELLIGENCE")
print("=" * 70)

print(f"\nBaseline Period: {START_DATE} -> {END_DATE}")

print("\nASSUMPTIONS")
print("-" * 70)
print(f"Estimated baseline stock coverage: {BASELINE_COVER_DAYS} days")
print(f"Reorder point coverage:            {REORDER_COVER_DAYS} days")

print("\nINVENTORY SUMMARY")
print("-" * 70)

print(f"Products with observed demand: {len(inventory):,}")

print(
    f"Total baseline units sold: "
    f"{inventory['baseline_units_sold'].sum():,.0f}"
)

print(
    f"Estimated total stock: "
    f"{inventory['estimated_stock'].sum():,.0f}"
)

print(
    f"Average days of cover: "
    f"{inventory['days_of_cover'].mean():.2f}"
)

print("\nSTOCKOUT RISK DISTRIBUTION")
print("-" * 70)

print(
    inventory["stockout_risk"]
    .value_counts()
    .reindex(
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        fill_value=0
    )
    .to_string()
)


print("\nTOP HIGH-RISK PRODUCTS")
print("-" * 70)

risk_order = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}

top_risk = inventory.copy()

top_risk["risk_rank"] = (
    top_risk["stockout_risk"]
    .map(risk_order)
)

top_risk = (
    top_risk
    .sort_values(
        ["risk_rank", "demand_cv", "baseline_revenue"],
        ascending=[True, False, False]
    )
    .head(15)
)

print(
    top_risk[
        [
            "product_id",
            "category",
            "baseline_units_sold",
            "average_daily_demand",
            "demand_cv",
            "estimated_stock",
            "days_of_cover",
            "stockout_risk",
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 70)
print("Inventory table saved as: inventory_v2")
print("=" * 70)

conn.close()
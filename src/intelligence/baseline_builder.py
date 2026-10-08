import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

conn = sqlite3.connect(DB_PATH)

START_DATE = "2018-08-01"
END_DATE = "2018-08-22"


# ============================================================
# 1. DAILY BUSINESS METRICS
# ============================================================

orders_query = f"""
SELECT
    DATE(order_purchase_timestamp) AS date,
    COUNT(DISTINCT order_id) AS orders
FROM orders
WHERE DATE(order_purchase_timestamp)
      BETWEEN '{START_DATE}' AND '{END_DATE}'
GROUP BY DATE(order_purchase_timestamp)
ORDER BY date;
"""

orders_df = pd.read_sql_query(orders_query, conn)


revenue_query = f"""
SELECT
    DATE(o.order_purchase_timestamp) AS date,
    SUM(oi.price) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE DATE(o.order_purchase_timestamp)
      BETWEEN '{START_DATE}' AND '{END_DATE}'
GROUP BY DATE(o.order_purchase_timestamp)
ORDER BY date;
"""

revenue_df = pd.read_sql_query(revenue_query, conn)


daily_df = orders_df.merge(
    revenue_df,
    on="date",
    how="left"
)

daily_df["revenue"] = daily_df["revenue"].fillna(0)

daily_df["average_order_value"] = (
    daily_df["revenue"] / daily_df["orders"]
)


# ============================================================
# 2. CUSTOMER EXPERIENCE
# ============================================================

reviews_query = f"""
SELECT
    AVG(r.review_score) AS average_review_score,
    COUNT(*) AS review_count
FROM order_reviews r
JOIN orders o
    ON r.order_id = o.order_id
WHERE DATE(o.order_purchase_timestamp)
      BETWEEN '{START_DATE}' AND '{END_DATE}';
"""

reviews_df = pd.read_sql_query(reviews_query, conn)


# ============================================================
# 3. BASELINE SUMMARY
# ============================================================

total_orders = int(daily_df["orders"].sum())
total_revenue = float(daily_df["revenue"].sum())

average_daily_orders = float(
    daily_df["orders"].mean()
)

average_daily_revenue = float(
    daily_df["revenue"].mean()
)

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

average_review_score = float(
    reviews_df.iloc[0]["average_review_score"]
)


# ============================================================
# 4. TOP PRODUCT CATEGORIES
# ============================================================

category_query = f"""
SELECT
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.price) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
WHERE DATE(o.order_purchase_timestamp)
      BETWEEN '{START_DATE}' AND '{END_DATE}'
GROUP BY category
ORDER BY revenue DESC
LIMIT 10;
"""

category_df = pd.read_sql_query(category_query, conn)


# ============================================================
# 5. TOP SELLERS
# ============================================================

seller_query = f"""
SELECT
    oi.seller_id,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.price) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE DATE(o.order_purchase_timestamp)
      BETWEEN '{START_DATE}' AND '{END_DATE}'
GROUP BY oi.seller_id
ORDER BY revenue DESC
LIMIT 10;
"""

seller_df = pd.read_sql_query(seller_query, conn)


# ============================================================
# 6. OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("ORACLE-X RELIABLE BUSINESS BASELINE")
print("=" * 70)

print(f"\nBaseline Period:")
print(f"{START_DATE} -> {END_DATE}")

print("\n" + "-" * 70)
print("CORE BUSINESS METRICS")
print("-" * 70)

print(f"Total Orders:           {total_orders:,}")
print(f"Total Item Revenue:     ${total_revenue:,.2f}")
print(f"Average Daily Orders:   {average_daily_orders:,.2f}")
print(f"Average Daily Revenue:  ${average_daily_revenue:,.2f}")
print(f"Average Order Value:    ${average_order_value:,.2f}")
print(f"Average Review Score:   {average_review_score:.2f}")
print(f"Review Count:           {int(reviews_df.iloc[0]['review_count']):,}")

print("\n" + "-" * 70)
print("DAILY BUSINESS PERFORMANCE")
print("-" * 70)

print(
    daily_df.to_string(
        index=False,
        formatters={
            "revenue": lambda x: f"${x:,.2f}",
            "average_order_value": lambda x: f"${x:,.2f}"
        }
    )
)

print("\n" + "-" * 70)
print("TOP PRODUCT CATEGORIES")
print("-" * 70)

print(
    category_df.to_string(
        index=False,
        formatters={
            "revenue": lambda x: f"${x:,.2f}"
        }
    )
)

print("\n" + "-" * 70)
print("TOP SELLERS")
print("-" * 70)

print(
    seller_df.to_string(
        index=False,
        formatters={
            "revenue": lambda x: f"${x:,.2f}"
        }
    )
)

print("\n" + "=" * 70)

conn.close()
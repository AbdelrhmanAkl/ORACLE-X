import sqlite3

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    strftime('%Y-%W', order_purchase_timestamp) AS week,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(
        (
            SELECT COALESCE(SUM(oi.price), 0)
            FROM order_items oi
            WHERE oi.order_id = o.order_id
        )
    ), 2) AS revenue
FROM orders o
GROUP BY week
ORDER BY week DESC
LIMIT 10;
"""

rows = conn.execute(query).fetchall()

print("\nLAST 10 ACTIVE WEEKS\n")

for week, orders, revenue in rows:
    print(
        f"{week} -> "
        f"{orders} orders | "
        f"${revenue:,.2f} revenue"
    )

conn.close()

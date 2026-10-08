import sqlite3

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    DATE(order_purchase_timestamp) AS date,
    COUNT(DISTINCT order_id) AS orders
FROM orders
GROUP BY DATE(order_purchase_timestamp)
HAVING COUNT(DISTINCT order_id) > 0
ORDER BY date DESC
LIMIT 10;
"""

rows = conn.execute(query).fetchall()

for date, orders in rows:
    print(f"{date} -> {orders} orders")

conn.close()

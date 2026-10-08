import sqlite3

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    MIN(DATE(order_purchase_timestamp)) AS first_date,
    MAX(DATE(order_purchase_timestamp)) AS last_date,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders;
"""

result = conn.execute(query).fetchone()

print("First date :", result[0])
print("Last date  :", result[1])
print("Total orders:", result[2])

conn.close()

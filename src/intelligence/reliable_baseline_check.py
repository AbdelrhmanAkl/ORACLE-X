import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    DATE(o.order_purchase_timestamp) AS date,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE DATE(o.order_purchase_timestamp)
      BETWEEN '2018-08-01' AND '2018-09-10'
GROUP BY DATE(o.order_purchase_timestamp)
ORDER BY date;
"""

df = pd.read_sql_query(query, conn)

print("\n" + "=" * 70)
print("ORACLE-X RELIABLE BASELINE CHECK")
print("=" * 70)

print(df.to_string(index=False))

print("\n" + "=" * 70)

conn.close()

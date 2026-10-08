import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH

DB_PATH = DATABASE_PATH


def main():
    conn = sqlite3.connect(DB_PATH)

    try:
        query = """
        SELECT
            DATE(order_purchase_timestamp) AS date,
            COUNT(DISTINCT order_id) AS orders,
            COUNT(DISTINCT customer_id) AS customers
        FROM orders
        GROUP BY DATE(order_purchase_timestamp)
        ORDER BY date
        """

        daily = pd.read_sql_query(query, conn)

        query = """
        SELECT
            order_status,
            COUNT(*) AS orders
        FROM orders
        GROUP BY order_status
        ORDER BY orders DESC
        """

        statuses = pd.read_sql_query(query, conn)

        query = """
        SELECT
            ROUND(AVG(review_score), 2) AS avg_review_score,
            COUNT(*) AS reviews
        FROM order_reviews
        WHERE review_score IS NOT NULL
        """

        reviews = pd.read_sql_query(query, conn)

        query = """
        SELECT
            COUNT(*) AS total_products,
            SUM(CASE WHEN stockout_risk = 'HIGH' THEN 1 ELSE 0 END)
                AS high_risk_products
        FROM inventory
        """

        inventory = pd.read_sql_query(query, conn)

        query = """
        SELECT
            ROUND(AVG(reliability_score), 2) AS avg_supplier_reliability,
            ROUND(AVG(risk_score), 2) AS avg_supplier_risk,
            COUNT(*) AS suppliers
        FROM suppliers
        """

        suppliers = pd.read_sql_query(query, conn)

        print("\n=== ORACLE-X AUTONOMOUS HEALTH SCAN ===")

        print("\n[DAILY BUSINESS]")
        print(f"Days: {len(daily):,}")
        print(f"Total Orders: {daily['orders'].sum():,}")
        print(f"Average Daily Orders: {daily['orders'].mean():,.2f}")

        if len(daily) >= 60:
            first_period = daily.head(30)["orders"].mean()
            last_period = daily.tail(30)["orders"].mean()

            change = ((last_period - first_period) / first_period) * 100

            print(f"First 30-Day Avg Orders: {first_period:,.2f}")
            print(f"Last 30-Day Avg Orders: {last_period:,.2f}")
            print(f"Order Trend: {change:+.2f}%")

        print("\n[ORDER STATUS]")
        print(statuses.to_string(index=False))

        print("\n[CUSTOMER EXPERIENCE]")
        print(reviews.to_string(index=False))

        print("\n[INVENTORY]")
        print(inventory.to_string(index=False))

        print("\n[SUPPLIER RISK]")
        print(suppliers.to_string(index=False))

        print("\n=== SCAN COMPLETE ===")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
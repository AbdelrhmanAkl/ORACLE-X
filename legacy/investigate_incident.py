import sqlite3
import pandas as pd


DB_PATH = "oracle_x.db"
INCIDENT_DATE = "2017-11-25"


def run_query(conn, query):
    return pd.read_sql_query(query, conn)


def main():
    conn = sqlite3.connect(DB_PATH)

    try:
        print("=" * 70)
        print("ORACLE-X AUTONOMOUS INCIDENT INVESTIGATION")
        print("=" * 70)

        print(f"\nIncident Date: {INCIDENT_DATE}")

        # ---------------------------------------------------------
        # 1. Incident baseline
        # ---------------------------------------------------------

        query = """
        SELECT
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(oi.price), 2) AS revenue,
            ROUND(AVG(r.review_score), 2) AS review_score
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        LEFT JOIN order_reviews r
            ON o.order_id = r.order_id
        WHERE DATE(o.order_purchase_timestamp) = ?
        """

        incident = run_query(
            conn,
            query.replace("?", f"'{INCIDENT_DATE}'"),
        )

        print("\n[1] INCIDENT METRICS")
        print(incident.to_string(index=False))

        # ---------------------------------------------------------
        # 2. Compare with previous 30 days
        # ---------------------------------------------------------

        query = """
        SELECT
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(oi.price), 2) AS revenue,
            ROUND(AVG(r.review_score), 2) AS review_score
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        LEFT JOIN order_reviews r
            ON o.order_id = r.order_id
        WHERE DATE(o.order_purchase_timestamp)
              BETWEEN DATE('2017-10-26') AND DATE('2017-11-24')
        """

        baseline = run_query(conn, query)

        print("\n[2] PREVIOUS 30-DAY BASELINE")
        print(baseline.to_string(index=False))

        # ---------------------------------------------------------
        # 3. Product categories affected
        # ---------------------------------------------------------

        query = """
        SELECT
            COALESCE(p.product_category_name, 'unknown') AS category,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(oi.price), 2) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE DATE(o.order_purchase_timestamp) = '2017-11-25'
        GROUP BY category
        ORDER BY revenue DESC
        LIMIT 15
        """

        categories = run_query(conn, query)

        print("\n[3] TOP AFFECTED PRODUCT CATEGORIES")
        print(categories.to_string(index=False))

        # ---------------------------------------------------------
        # 4. Seller concentration
        # ---------------------------------------------------------

        query = """
        SELECT
            oi.seller_id,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(oi.price), 2) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE DATE(o.order_purchase_timestamp) = '2017-11-25'
        GROUP BY oi.seller_id
        ORDER BY revenue DESC
        LIMIT 15
        """

        sellers = run_query(conn, query)

        print("\n[4] TOP SELLERS")
        print(sellers.to_string(index=False))

        # ---------------------------------------------------------
        # 5. Order status distribution
        # ---------------------------------------------------------

        query = """
        SELECT
            order_status,
            COUNT(*) AS orders
        FROM orders
        WHERE DATE(order_purchase_timestamp) = '2017-11-25'
        GROUP BY order_status
        ORDER BY orders DESC
        """

        statuses = run_query(conn, query)

        print("\n[5] ORDER STATUS")
        print(statuses.to_string(index=False))

        # ---------------------------------------------------------
        # 6. Payment behavior
        # ---------------------------------------------------------

        query = """
        SELECT
            p.payment_type,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(p.payment_value), 2) AS payment_value
        FROM orders o
        JOIN order_payments p
            ON o.order_id = p.order_id
        WHERE DATE(o.order_purchase_timestamp) = '2017-11-25'
        GROUP BY p.payment_type
        ORDER BY payment_value DESC
        """

        payments = run_query(conn, query)

        print("\n[6] PAYMENT MIX")
        print(payments.to_string(index=False))

        # ---------------------------------------------------------
        # 7. Customer experience
        # ---------------------------------------------------------

        query = """
        SELECT
            r.review_score,
            COUNT(*) AS reviews
        FROM orders o
        JOIN order_reviews r
            ON o.order_id = r.order_id
        WHERE DATE(o.order_purchase_timestamp) = '2017-11-25'
        GROUP BY r.review_score
        ORDER BY r.review_score
        """

        reviews = run_query(conn, query)

        print("\n[7] REVIEW DISTRIBUTION")
        print(reviews.to_string(index=False))

        print("\n" + "=" * 70)
        print("INVESTIGATION COMPLETE")
        print("=" * 70)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

def main():
    conn = sqlite3.connect(DB_PATH)

    try:
        latest_date = pd.read_sql_query(
            """
            SELECT MAX(DATE(order_purchase_timestamp)) AS latest_date
            FROM orders
            """,
            conn,
        ).iloc[0]["latest_date"]

        metrics_query = """
        WITH recent_orders AS (
            SELECT
                o.order_id,
                DATE(o.order_purchase_timestamp) AS order_date
            FROM orders o
            WHERE DATE(o.order_purchase_timestamp)
                  BETWEEN DATE(?, '-29 days') AND DATE(?)
        ),
        order_revenue AS (
            SELECT
                ro.order_id,
                ro.order_date,
                SUM(oi.price) AS order_revenue
            FROM recent_orders ro
            JOIN order_items oi
                ON ro.order_id = oi.order_id
            GROUP BY
                ro.order_id,
                ro.order_date
        ),
        daily_metrics AS (
            SELECT
                order_date,
                COUNT(*) AS daily_orders,
                SUM(order_revenue) AS daily_revenue
            FROM order_revenue
            GROUP BY order_date
        )
        SELECT
            COUNT(*) AS total_orders,
            ROUND(SUM(order_revenue), 2) AS total_revenue,
            ROUND(
                SUM(order_revenue) / COUNT(*),
                2
            ) AS average_order_value,
            ROUND(
                AVG(daily_orders),
                2
            ) AS average_daily_orders,
            ROUND(
                AVG(daily_revenue),
                2
            ) AS average_daily_revenue
        FROM order_revenue
        CROSS JOIN (
            SELECT
                AVG(daily_orders) AS daily_orders,
                AVG(daily_revenue) AS daily_revenue
            FROM daily_metrics
        );
        """

        state = pd.read_sql_query(
            metrics_query,
            conn,
            params=(latest_date, latest_date),
        )

        review_query = """
        SELECT
            ROUND(AVG(r.review_score), 2) AS average_review_score
        FROM order_reviews r
        JOIN orders o
            ON r.order_id = o.order_id
        WHERE DATE(o.order_purchase_timestamp)
              BETWEEN DATE(?, '-29 days') AND DATE(?);
        """

        review = pd.read_sql_query(
            review_query,
            conn,
            params=(latest_date, latest_date),
        )

        state["average_review_score"] = review.iloc[0][
            "average_review_score"
        ]

        category_query = """
        SELECT
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'unknown'
            ) AS category,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(oi.price), 2) AS revenue
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        LEFT JOIN category_translation ct
            ON p.product_category_name = ct.product_category_name
        WHERE DATE(o.order_purchase_timestamp)
              BETWEEN DATE(?, '-29 days') AND DATE(?)
        GROUP BY category
        ORDER BY revenue DESC
        LIMIT 10;
        """

        categories = pd.read_sql_query(
            category_query,
            conn,
            params=(latest_date, latest_date),
        )

        print("\n" + "=" * 80)
        print("ORACLE-X CURRENT BUSINESS STATE")
        print("=" * 80)

        print(f"\nLast known business date: {latest_date}")
        print("Analysis window: Last 30 days")

        print("\nCORE BUSINESS METRICS\n")
        print(state.to_string(index=False))

        print("\nTOP PRODUCT CATEGORIES\n")
        print(categories.to_string(index=False))

        print("\n" + "=" * 80)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
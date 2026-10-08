import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH


def main():
    conn = sqlite3.connect(DB_PATH)

    try:
        query = """
        SELECT
            oi.seller_id,
            COUNT(DISTINCT o.order_id) AS orders,
            AVG(
                julianday(o.order_delivered_customer_date)
                - julianday(o.order_estimated_delivery_date)
            ) AS avg_delivery_delta,
            AVG(r.review_score) AS avg_review_score
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        LEFT JOIN order_reviews r
            ON o.order_id = r.order_id
        WHERE
            o.order_delivered_customer_date IS NOT NULL
            AND o.order_estimated_delivery_date IS NOT NULL
        GROUP BY oi.seller_id
        HAVING COUNT(DISTINCT o.order_id) >= 20
        ORDER BY avg_delivery_delta DESC
        LIMIT 20
        """

        df = pd.read_sql_query(query, conn)

        print("\n=== ORACLE-X ROOT CAUSE CANDIDATES ===\n")

        print(
            df.to_string(
                index=False,
                float_format=lambda x: f"{x:.2f}",
            )
        )

        print("\n=== INTERPRETATION ===")

        delayed = df[df["avg_delivery_delta"] > 0]

        print(
            f"Sellers with average delivery delay: "
            f"{len(delayed)}"
        )

        if not delayed.empty:
            print(
                f"Worst average delay: "
                f"{delayed['avg_delivery_delta'].max():.2f} days"
            )

        print("\nSCAN COMPLETE")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
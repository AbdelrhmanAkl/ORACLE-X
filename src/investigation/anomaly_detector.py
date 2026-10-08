import sqlite3

import numpy as np
import pandas as pd

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH


def main():
    conn = sqlite3.connect(DB_PATH)

    try:
        query = """
        SELECT
            DATE(o.order_purchase_timestamp) AS date,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(oi.price), 2) AS revenue,
            ROUND(AVG(r.review_score), 2) AS review_score
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        LEFT JOIN order_reviews r
            ON o.order_id = r.order_id
        GROUP BY DATE(o.order_purchase_timestamp)
        ORDER BY date
        """

        df = pd.read_sql_query(query, conn)

        # Rolling historical baseline.
        df["orders_baseline"] = (
            df["orders"]
            .rolling(window=14, min_periods=7)
            .mean()
            .shift(1)
        )

        df["revenue_baseline"] = (
            df["revenue"]
            .rolling(window=14, min_periods=7)
            .mean()
            .shift(1)
        )

        df["review_baseline"] = (
            df["review_score"]
            .rolling(window=14, min_periods=7)
            .mean()
            .shift(1)
        )

        # Percentage deviations from the historical baseline.
        df["orders_change_pct"] = (
            (df["orders"] - df["orders_baseline"])
            / df["orders_baseline"]
            * 100
        )

        df["revenue_change_pct"] = (
            (df["revenue"] - df["revenue_baseline"])
            / df["revenue_baseline"]
            * 100
        )

        df["review_change_pct"] = (
            (df["review_score"] - df["review_baseline"])
            / df["review_baseline"]
            * 100
        )

        # Composite anomaly score.
        df["anomaly_score"] = (
            df["orders_change_pct"].abs()
            + df["revenue_change_pct"].abs()
            + df["review_change_pct"].abs()
        )

        anomalies = (
            df.dropna(subset=["anomaly_score"])
            .sort_values("anomaly_score", ascending=False)
            .head(20)
        )

        print("\n" + "=" * 80)
        print("ORACLE-X AUTONOMOUS ANOMALY DETECTOR")
        print("=" * 80)

        print("\nTOP ANOMALOUS BUSINESS DAYS\n")

        columns = [
            "date",
            "orders",
            "revenue",
            "review_score",
            "orders_change_pct",
            "revenue_change_pct",
            "review_change_pct",
            "anomaly_score",
        ]

        print(
            anomalies[columns].to_string(
                index=False,
                float_format=lambda x: f"{x:.2f}",
            )
        )

        print("\n" + "=" * 80)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
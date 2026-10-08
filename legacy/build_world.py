import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "oracle_x.db"


def main():
    connection = sqlite3.connect(DB_PATH)

    try:
        print("Loading real business data...")

        orders = pd.read_sql_query(
            """
            SELECT
                order_id,
                customer_id,
                order_status,
                order_purchase_timestamp,
                order_delivered_customer_date,
                order_estimated_delivery_date
            FROM orders
            """,
            connection,
        )

        items = pd.read_sql_query(
            """
            SELECT
                order_id,
                product_id,
                seller_id,
                price,
                freight_value
            FROM order_items
            """,
            connection,
        )

        products = pd.read_sql_query(
            """
            SELECT
                product_id,
                product_category_name
            FROM products
            """,
            connection,
        )

        sellers = pd.read_sql_query(
            """
            SELECT
                seller_id,
                seller_city,
                seller_state
            FROM sellers
            """,
            connection,
        )

        print("Creating inventory intelligence...")

        product_sales = (
            items.groupby("product_id")
            .agg(
                units_sold=("product_id", "size"),
                avg_price=("price", "mean"),
            )
            .reset_index()
        )

        inventory = products.merge(
            product_sales,
            on="product_id",
            how="left",
        )

        inventory["units_sold"] = inventory["units_sold"].fillna(0)
        inventory["avg_price"] = inventory["avg_price"].fillna(0)

        # Demand proxy derived from actual historical sales.
        inventory["avg_daily_demand"] = (
            inventory["units_sold"] / 24
        )

        inventory["stock_level"] = np.maximum(
            np.ceil(inventory["avg_daily_demand"] * 14),
            5,
        )

        inventory["reorder_point"] = np.maximum(
            np.ceil(inventory["avg_daily_demand"] * 7),
            3,
        )

        inventory["stockout_risk"] = np.where(
            inventory["stock_level"] <= inventory["reorder_point"],
            "HIGH",
            "LOW",
        )

        inventory = inventory[
            [
                "product_id",
                "product_category_name",
                "units_sold",
                "avg_daily_demand",
                "stock_level",
                "reorder_point",
                "stockout_risk",
            ]
        ]

        inventory.to_sql(
            "inventory",
            connection,
            if_exists="replace",
            index=False,
        )

        print(f"Inventory records: {len(inventory):,}")

        print("Creating supplier intelligence...")

        seller_orders = (
            items.groupby("seller_id")
            .agg(
                orders_fulfilled=("order_id", "nunique"),
                revenue=("price", "sum"),
                avg_freight=("freight_value", "mean"),
            )
            .reset_index()
        )

        supplier = sellers.merge(
            seller_orders,
            on="seller_id",
            how="left",
        )

        supplier["orders_fulfilled"] = supplier[
            "orders_fulfilled"
        ].fillna(0)

        supplier["revenue"] = supplier["revenue"].fillna(0)
        supplier["avg_freight"] = supplier["avg_freight"].fillna(0)

        supplier["reliability_score"] = (
            supplier["orders_fulfilled"]
            / supplier["orders_fulfilled"].max()
            * 100
        ).round(2)

        supplier["risk_score"] = (
            100 - supplier["reliability_score"]
        ).round(2)

        supplier.to_sql(
            "suppliers",
            connection,
            if_exists="replace",
            index=False,
        )

        print(f"Supplier records: {len(supplier):,}")

        print("Creating marketing intelligence...")

        daily_sales = (
            items.merge(
                orders[["order_id", "order_purchase_timestamp"]],
                on="order_id",
                how="left",
            )
        )

        daily_sales["date"] = pd.to_datetime(
            daily_sales["order_purchase_timestamp"]
        ).dt.date

        marketing = (
            daily_sales.groupby("date")
            .agg(
                orders=("order_id", "nunique"),
                revenue=("price", "sum"),
            )
            .reset_index()
        )

        marketing["marketing_spend"] = (
            marketing["revenue"] * 0.08
        ).round(2)

        marketing["conversion_rate"] = (
            marketing["orders"]
            / marketing["orders"].max()
            * 100
        ).round(2)

        marketing.to_sql(
            "marketing",
            connection,
            if_exists="replace",
            index=False,
        )

        print(f"Marketing records: {len(marketing):,}")

        print("Creating financial operations...")

        financial = (
            daily_sales.groupby("date")
            .agg(
                revenue=("price", "sum"),
                freight_cost=("freight_value", "sum"),
            )
            .reset_index()
        )

        financial["operating_expense"] = (
            financial["revenue"] * 0.12
        ).round(2)

        financial["estimated_profit"] = (
            financial["revenue"]
            - financial["freight_cost"]
            - financial["operating_expense"]
        ).round(2)

        financial.to_sql(
            "financial_operations",
            connection,
            if_exists="replace",
            index=False,
        )

        print(f"Financial records: {len(financial):,}")

        connection.commit()

        print("\nORACLE-X Business World created successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
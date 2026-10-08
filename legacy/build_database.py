import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "oracle_x.db"

TABLES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)

    try:
        for table_name, filename in TABLES.items():
            csv_path = BASE_DIR / filename

            print(f"Loading: {filename}")

            df = pd.read_csv(csv_path)

            df.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False,
            )

            print(f"  Rows: {len(df):,}")
            print(f"  Columns: {len(df.columns)}")

        print("\nCreating indexes...")

        indexes = [
            ("idx_orders_customer", "orders", "customer_id"),
            ("idx_order_items_order", "order_items", "order_id"),
            ("idx_order_items_product", "order_items", "product_id"),
            ("idx_order_items_seller", "order_items", "seller_id"),
            ("idx_payments_order", "order_payments", "order_id"),
            ("idx_reviews_order", "order_reviews", "order_id"),
            ("idx_products_product", "products", "product_id"),
            ("idx_customers_customer", "customers", "customer_id"),
            ("idx_sellers_seller", "sellers", "seller_id"),
        ]

        for index_name, table_name, column_name in indexes:
            connection.execute(
                f"""
                CREATE INDEX {index_name}
                ON {table_name} ({column_name})
                """
            )

        connection.commit()

        print("\nDatabase created successfully:")
        print(DB_PATH)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
import sqlite3
from datetime import datetime

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

BASELINE_START = "2018-08-01"
BASELINE_END = "2018-08-22"

# These are explicit modeling assumptions.
# They are NOT historical Olist inventory facts.
ESTIMATED_INVENTORY_COVER_DAYS = 14
ESTIMATED_REORDER_COVER_DAYS = 7


def create_business_world():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("ORACLE-X BUSINESS WORLD BUILDER")
    print("=" * 70)
    print()
    print(f"Historical baseline: {BASELINE_START} -> {BASELINE_END}")
    print()

    # ------------------------------------------------------------------
    # 1. HISTORICAL BUSINESS BASELINE
    # ------------------------------------------------------------------
    # Orders and item revenue are observed from the Olist dataset.
    # Revenue here means item revenue, not accounting/payment revenue.
    #
    # Reviews are aggregated separately to avoid duplication caused by
    # joining orders with multiple order items.
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(order_value), 0),
            COALESCE(AVG(order_value), 0)
        FROM (
            SELECT
                o.order_id,
                SUM(oi.price) AS order_value
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            WHERE DATE(o.order_purchase_timestamp)
                  BETWEEN ? AND ?
            GROUP BY o.order_id
        )
        """,
        (BASELINE_START, BASELINE_END),
    )

    orders, revenue, average_order_value = cursor.fetchone()

    # ------------------------------------------------------------------
    # 2. CUSTOMER EXPERIENCE
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(AVG(r.review_score), 0)
        FROM order_reviews r
        JOIN orders o
            ON r.order_id = o.order_id
        WHERE DATE(o.order_purchase_timestamp)
              BETWEEN ? AND ?
        """,
        (BASELINE_START, BASELINE_END),
    )

    review_count, average_review_score = cursor.fetchone()

    # ------------------------------------------------------------------
    # 3. PRODUCT AND SELLER SCALE
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM products
        """
    )

    total_products = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM sellers
        """
    )

    total_sellers = cursor.fetchone()[0]

    # ------------------------------------------------------------------
    # 4. ACTIVE CUSTOMERS
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(DISTINCT customer_id)
        FROM orders
        WHERE DATE(order_purchase_timestamp)
              BETWEEN ? AND ?
        """,
        (BASELINE_START, BASELINE_END),
    )

    active_customers = cursor.fetchone()[0]

    # ------------------------------------------------------------------
    # 5. DELIVERED ORDERS
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE DATE(order_purchase_timestamp)
              BETWEEN ? AND ?
              AND order_status = 'delivered'
        """,
        (BASELINE_START, BASELINE_END),
    )

    delivered_orders = cursor.fetchone()[0]

    # ------------------------------------------------------------------
    # 6. TIME NORMALIZATION
    # ------------------------------------------------------------------

    start_date = datetime.strptime(BASELINE_START, "%Y-%m-%d")
    end_date = datetime.strptime(BASELINE_END, "%Y-%m-%d")

    days = (end_date - start_date).days + 1

    average_daily_orders = (
        orders / days
        if days > 0
        else 0
    )

    average_daily_revenue = (
        revenue / days
        if days > 0
        else 0
    )

    # ------------------------------------------------------------------
    # 7. INVENTORY SIGNAL
    # ------------------------------------------------------------------
    #
    # Olist does NOT provide historical inventory quantities.
    #
    # inventory_v2 therefore contains an estimated inventory baseline.
    # We preserve that distinction explicitly.
    #
    # Actual historical facts:
    #   baseline_units_sold
    #
    # Estimated/model-derived:
    #   estimated_stock
    #   days_of_cover
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(baseline_units_sold), 0),
            COALESCE(SUM(estimated_stock), 0),
            COALESCE(AVG(days_of_cover), 0)
        FROM inventory_v2
        """
    )

    (
        inventory_products,
        baseline_units_sold,
        estimated_inventory_units,
        average_days_of_cover,
    ) = cursor.fetchone()

    # ------------------------------------------------------------------
    # 8. SELLER INTELLIGENCE
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT
            COUNT(*),
            SUM(
                CASE
                    WHEN risk_level = 'MEDIUM'
                    THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN risk_level = 'INSUFFICIENT_EVIDENCE'
                    THEN 1
                    ELSE 0
                END
            ),
            COALESCE(AVG(adjusted_risk_score), 0)
        FROM seller_intelligence
        """
    )

    (
        seller_records,
        medium_risk_sellers,
        insufficient_evidence_sellers,
        average_seller_risk,
    ) = cursor.fetchone()

    medium_risk_sellers = medium_risk_sellers or 0
    insufficient_evidence_sellers = insufficient_evidence_sellers or 0
    average_seller_risk = average_seller_risk or 0

    # ------------------------------------------------------------------
    # 9. BUSINESS WORLD TABLE
    # ------------------------------------------------------------------

    cursor.execute(
        """
        DROP TABLE IF EXISTS business_world
        """
    )

    cursor.execute(
        """
        CREATE TABLE business_world (
            snapshot_id INTEGER PRIMARY KEY,
            snapshot_type TEXT NOT NULL,

            baseline_start TEXT NOT NULL,
            baseline_end TEXT NOT NULL,

            total_orders INTEGER NOT NULL,
            delivered_orders INTEGER NOT NULL,
            active_customers INTEGER NOT NULL,

            item_revenue REAL NOT NULL,
            average_daily_orders REAL NOT NULL,
            average_daily_revenue REAL NOT NULL,
            average_order_value REAL NOT NULL,

            average_review_score REAL NOT NULL,
            review_count INTEGER NOT NULL,

            total_products INTEGER NOT NULL,
            total_sellers INTEGER NOT NULL,

            inventory_products INTEGER NOT NULL,
            baseline_units_sold INTEGER NOT NULL,
            estimated_inventory_units REAL NOT NULL,

            average_estimated_days_of_cover REAL NOT NULL,
            estimated_reorder_cover_days REAL NOT NULL,

            seller_records INTEGER NOT NULL,
            medium_risk_sellers INTEGER NOT NULL,
            insufficient_evidence_sellers INTEGER NOT NULL,
            average_seller_risk REAL NOT NULL,

            inventory_state TEXT NOT NULL,
            supplier_state TEXT NOT NULL,
            demand_state TEXT NOT NULL,
            customer_state TEXT NOT NULL,

            state_source TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # ------------------------------------------------------------------
    # 10. INITIAL SIMULATED BUSINESS STATE
    # ------------------------------------------------------------------
    #
    # This is the starting state for the future simulation engine.
    #
    # Important:
    # This is NOT a claim that the historical Olist company actually had
    # these inventory or operational conditions.
    #
    # It is a controlled state reconstructed from historical evidence.
    # ------------------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO business_world (
            snapshot_id,
            snapshot_type,

            baseline_start,
            baseline_end,

            total_orders,
            delivered_orders,
            active_customers,

            item_revenue,
            average_daily_orders,
            average_daily_revenue,
            average_order_value,

            average_review_score,
            review_count,

            total_products,
            total_sellers,

            inventory_products,
            baseline_units_sold,
            estimated_inventory_units,

            average_estimated_days_of_cover,
            estimated_reorder_cover_days,

            seller_records,
            medium_risk_sellers,
            insufficient_evidence_sellers,
            average_seller_risk,

            inventory_state,
            supplier_state,
            demand_state,
            customer_state,

            state_source,
            created_at
        )
        VALUES (
            1,
            'INITIAL_SIMULATED_STATE',

            ?,
            ?,

            ?,
            ?,
            ?,

            ?,
            ?,
            ?,
            ?,

            ?,
            ?,

            ?,
            ?,

            ?,
            ?,
            ?,

            ?,
            ?,

            ?,
            ?,
            ?,
            ?,

            'STABLE',
            'STABLE_WITH_LIMITED_EVIDENCE',
            'BASELINE',
            'STABLE',

            'Historical Olist baseline + explicit simulation assumptions',
            ?
        )
        """,
        (
            BASELINE_START,
            BASELINE_END,

            orders,
            delivered_orders,
            active_customers,

            revenue,
            average_daily_orders,
            average_daily_revenue,
            average_order_value,

            average_review_score,
            review_count,

            total_products,
            total_sellers,

            inventory_products,
            baseline_units_sold,
            estimated_inventory_units,

            average_days_of_cover,
            ESTIMATED_REORDER_COVER_DAYS,

            seller_records,
            medium_risk_sellers,
            insufficient_evidence_sellers,
            average_seller_risk,

            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    conn.commit()

    # ------------------------------------------------------------------
    # 11. VALIDATION
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT
            total_orders,
            delivered_orders,
            active_customers,
            item_revenue,
            average_daily_orders,
            average_daily_revenue,
            average_order_value,
            average_review_score,
            inventory_products,
            baseline_units_sold,
            estimated_inventory_units,
            average_estimated_days_of_cover,
            medium_risk_sellers,
            insufficient_evidence_sellers,
            average_seller_risk
        FROM business_world
        WHERE snapshot_id = 1
        """
    )

    state = cursor.fetchone()

    print("BUSINESS WORLD STATE")
    print("-" * 70)

    labels = [
        "Total Orders",
        "Delivered Orders",
        "Active Customers",
        "Item Revenue",
        "Average Daily Orders",
        "Average Daily Revenue",
        "Average Order Value",
        "Average Review Score",
        "Inventory Products",
        "Baseline Units Sold",
        "Estimated Inventory Units",
        "Average Estimated Days of Cover",
        "Medium-Risk Sellers",
        "Insufficient-Evidence Sellers",
        "Average Adjusted Seller Risk",
    ]

    for label, value in zip(labels, state):

        if isinstance(value, float):
            print(f"{label}: {value:,.2f}")
        else:
            print(f"{label}: {value:,}")

    print()

    print("INITIAL BUSINESS STATES")
    print("-" * 70)
    print("Inventory State: STABLE")
    print("Supplier State: STABLE_WITH_LIMITED_EVIDENCE")
    print("Demand State: BASELINE")
    print("Customer State: STABLE")

    print()

    print("DATA PROVENANCE")
    print("-" * 70)
    print("OBSERVED:")
    print("  - Orders")
    print("  - Item revenue")
    print("  - Customers")
    print("  - Reviews")
    print("  - Products")
    print("  - Sellers")
    print("  - Seller performance")

    print()
    print("ESTIMATED / MODEL-DERIVED:")
    print("  - Inventory level")
    print("  - Inventory coverage")

    print()
    print("SIMULATED LATER:")
    print("  - Demand shocks")
    print("  - Inventory depletion")
    print("  - Supplier pressure")
    print("  - Customer impact")
    print("  - Strategic scenarios")
    print("  - Future business outcomes")

    print()
    print("MODEL ASSUMPTIONS")
    print("-" * 70)
    print(
        f"Estimated inventory coverage: "
        f"{ESTIMATED_INVENTORY_COVER_DAYS} days"
    )
    print(
        f"Estimated reorder coverage: "
        f"{ESTIMATED_REORDER_COVER_DAYS} days"
    )

    print()
    print("Business world table saved as: business_world")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    create_business_world()
import sqlite3
from datetime import datetime

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

# ----------------------------------------------------------------------
# CONTROLLED BUSINESS EVENT
# ----------------------------------------------------------------------
#
# These values are simulated business conditions.
# They are NOT historical observations from Olist.
# ----------------------------------------------------------------------

DEMAND_CHANGE_PCT = 25.0
INVENTORY_CHANGE_PCT = -18.0
SUPPLIER_PRESSURE_PCT = 12.0
CUSTOMER_SCORE_CHANGE = -0.30


def create_simulation_tables(cursor):
    """
    Create the tables used by the simulation engine.
    """

    cursor.execute(
        """
        DROP TABLE IF EXISTS simulation_events
        """
    )

    cursor.execute(
        """
        CREATE TABLE simulation_events (
            event_id INTEGER PRIMARY KEY,

            event_name TEXT NOT NULL,
            event_type TEXT NOT NULL,

            demand_change_pct REAL NOT NULL,
            inventory_change_pct REAL NOT NULL,
            supplier_pressure_pct REAL NOT NULL,
            customer_score_change REAL NOT NULL,

            description TEXT NOT NULL,
            source_type TEXT NOT NULL,

            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        DROP TABLE IF EXISTS current_simulated_state
        """
    )

    cursor.execute(
        """
        CREATE TABLE current_simulated_state (
            snapshot_id INTEGER PRIMARY KEY,

            event_id INTEGER NOT NULL,

            baseline_orders INTEGER NOT NULL,
            simulated_orders REAL NOT NULL,

            baseline_daily_orders REAL NOT NULL,
            simulated_daily_orders REAL NOT NULL,

            baseline_daily_revenue REAL NOT NULL,
            simulated_daily_revenue REAL NOT NULL,

            baseline_aov REAL NOT NULL,
            simulated_aov REAL NOT NULL,

            baseline_inventory_units REAL NOT NULL,
            simulated_inventory_units REAL NOT NULL,

            baseline_inventory_cover_days REAL NOT NULL,
            simulated_inventory_cover_days REAL NOT NULL,

            baseline_review_score REAL NOT NULL,
            simulated_review_score REAL NOT NULL,

            baseline_seller_risk REAL NOT NULL,
            simulated_seller_risk REAL NOT NULL,

            demand_state TEXT NOT NULL,
            inventory_state TEXT NOT NULL,
            supplier_state TEXT NOT NULL,
            customer_state TEXT NOT NULL,

            simulation_status TEXT NOT NULL,

            created_at TEXT NOT NULL,

            FOREIGN KEY (event_id)
                REFERENCES simulation_events(event_id)
        )
        """
    )


def classify_inventory_state(days_of_cover):
    """
    Classify inventory based on simulated days of cover.

    These thresholds are explicit operational assumptions,
    not historical Olist facts.
    """

    if days_of_cover <= 3:
        return "CRITICAL"

    if days_of_cover <= 7:
        return "HIGH_RISK"

    if days_of_cover <= 10:
        return "WATCH"

    return "STABLE"


def classify_supplier_state(simulated_risk):
    """
    Classify supplier pressure using simulated seller risk.
    """

    if simulated_risk >= 20:
        return "HIGH_PRESSURE"

    if simulated_risk >= 10:
        return "ELEVATED_PRESSURE"

    return "STABLE"


def classify_customer_state(review_score):
    """
    Classify customer experience.
    """

    if review_score < 3.0:
        return "CRITICAL"

    if review_score < 3.5:
        return "AT_RISK"

    if review_score < 4.0:
        return "WATCH"

    return "STABLE"


def classify_demand_state(change_pct):
    """
    Classify demand movement.
    """

    if change_pct >= 20:
        return "SURGE"

    if change_pct >= 10:
        return "INCREASING"

    if change_pct <= -20:
        return "COLLAPSE"

    if change_pct <= -10:
        return "DECLINING"

    return "NORMAL"


def build_simulated_state(
    baseline_orders,
    baseline_daily_orders,
    baseline_daily_revenue,
    baseline_aov,
    baseline_inventory_units,
    baseline_inventory_cover_days,
    baseline_review_score,
    baseline_seller_risk,
    demand_change_pct,
    inventory_change_pct,
    supplier_pressure_pct,
    customer_score_change,
):
    """
    Build the complete simulated business state in memory.

    This function contains only deterministic simulation logic.
    It does not access the database and does not perform any writes.

    All simulation inputs are explicit controlled conditions.
    """

    # ------------------------------------------------------------------
    # 1. SIMULATE DEMAND
    # ------------------------------------------------------------------

    simulated_daily_orders = (
        baseline_daily_orders
        * (1 + demand_change_pct / 100)
    )

    simulated_orders = (
        baseline_orders
        * (1 + demand_change_pct / 100)
    )

    # ------------------------------------------------------------------
    # 2. SIMULATE REVENUE
    # ------------------------------------------------------------------
    #
    # AOV is treated as the canonical order-level business metric.
    # Under this controlled event, demand changes while AOV remains
    # constant as an explicit simulation assumption.
    #
    # Therefore:
    #
    # Revenue = Daily Orders * AOV
    #
    # This keeps the financial relationship internally consistent.
    # ------------------------------------------------------------------

    simulated_aov = baseline_aov

    simulated_daily_revenue = (
        simulated_daily_orders * simulated_aov
    )

    # ------------------------------------------------------------------
    # 3. SIMULATE INVENTORY
    # ------------------------------------------------------------------

    simulated_inventory_units = (
        baseline_inventory_units
        * (1 + inventory_change_pct / 100)
    )

    # ------------------------------------------------------------------
    # 4. CALCULATE INVENTORY COVER
    # ------------------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Inventory units and order counts are different units of measure.
    # We therefore do NOT divide inventory units by daily orders.
    #
    # inventory_v2 was constructed around an estimated baseline coverage
    # assumption of 14 days.
    #
    # We preserve that baseline and model the shock through relative
    # inventory availability and demand growth.
    # ------------------------------------------------------------------

    simulated_inventory_cover_days = (
        baseline_inventory_cover_days
        * (1 + inventory_change_pct / 100)
        / (1 + demand_change_pct / 100)
    )

    # ------------------------------------------------------------------
    # 5. SIMULATE SUPPLIER PRESSURE
    # ------------------------------------------------------------------

    simulated_seller_risk = (
        baseline_seller_risk
        + supplier_pressure_pct
    )

    # ------------------------------------------------------------------
    # 6. SIMULATE CUSTOMER IMPACT
    # ------------------------------------------------------------------

    simulated_review_score = (
        baseline_review_score
        + customer_score_change
    )

    simulated_review_score = max(
        1.0,
        min(5.0, simulated_review_score),
    )

    # ------------------------------------------------------------------
    # 7. CLASSIFY BUSINESS STATES
    # ------------------------------------------------------------------

    demand_state = classify_demand_state(
        demand_change_pct
    )

    inventory_state = classify_inventory_state(
        simulated_inventory_cover_days
    )

    supplier_state = classify_supplier_state(
        simulated_seller_risk
    )

    customer_state = classify_customer_state(
        simulated_review_score
    )

    # ------------------------------------------------------------------
    # 8. RETURN COMPLETE IN-MEMORY STATE
    # ------------------------------------------------------------------

    return {
        "baseline_orders": baseline_orders,
        "simulated_orders": simulated_orders,

        "baseline_daily_orders": baseline_daily_orders,
        "simulated_daily_orders": simulated_daily_orders,

        "baseline_daily_revenue": baseline_daily_revenue,
        "simulated_daily_revenue": simulated_daily_revenue,

        "baseline_aov": baseline_aov,
        "simulated_aov": simulated_aov,

        "baseline_inventory_units": baseline_inventory_units,
        "simulated_inventory_units": simulated_inventory_units,

        "baseline_inventory_cover_days": (
            baseline_inventory_cover_days
        ),
        "simulated_inventory_cover_days": (
            simulated_inventory_cover_days
        ),

        "baseline_review_score": baseline_review_score,
        "simulated_review_score": simulated_review_score,

        "baseline_seller_risk": baseline_seller_risk,
        "simulated_seller_risk": simulated_seller_risk,

        "demand_state": demand_state,
        "inventory_state": inventory_state,
        "supplier_state": supplier_state,
        "customer_state": customer_state,

        "simulation_status": "ACTIVE_SIMULATION",
    }


def run_simulation():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("ORACLE-X CONTROLLED SIMULATION ENGINE")
    print("=" * 70)
    print()

    # ------------------------------------------------------------------
    # 1. CREATE SIMULATION TABLES
    # ------------------------------------------------------------------

    create_simulation_tables(cursor)

    # ------------------------------------------------------------------
    # 2. LOAD BUSINESS BASELINE
    # ------------------------------------------------------------------

    cursor.execute(
        """
        SELECT
            total_orders,
            average_daily_orders,
            average_daily_revenue,
            average_order_value,
            estimated_inventory_units,
            average_estimated_days_of_cover,
            average_review_score,
            average_seller_risk
        FROM business_world
        WHERE snapshot_id = 1
        """
    )

    baseline = cursor.fetchone()

    if baseline is None:
        conn.close()

        raise RuntimeError(
            "Business baseline not found. "
            "Run business_world_builder.py first."
        )

    (
        baseline_orders,
        baseline_daily_orders,
        baseline_daily_revenue,
        baseline_aov,
        baseline_inventory_units,
        baseline_inventory_cover_days,
        baseline_review_score,
        baseline_seller_risk,
    ) = baseline

    # ------------------------------------------------------------------
    # 3. CREATE CONTROLLED BUSINESS EVENT
    # ------------------------------------------------------------------

    event_name = "DEMAND_SURGE_WITH_SUPPLY_PRESSURE"

    event_description = (
        "A controlled simulated business event where demand increases "
        "while available inventory decreases and supplier pressure rises."
    )

    cursor.execute(
        """
        INSERT INTO simulation_events (
            event_id,
            event_name,
            event_type,

            demand_change_pct,
            inventory_change_pct,
            supplier_pressure_pct,
            customer_score_change,

            description,
            source_type,
            created_at
        )
        VALUES (
            1,
            ?,
            'CONTROLLED_BUSINESS_SHOCK',

            ?,
            ?,
            ?,
            ?,

            ?,
            'SIMULATED',
            ?
        )
        """,
        (
            event_name,
            DEMAND_CHANGE_PCT,
            INVENTORY_CHANGE_PCT,
            SUPPLIER_PRESSURE_PCT,
            CUSTOMER_SCORE_CHANGE,
            event_description,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    # ------------------------------------------------------------------
    # 4. BUILD SIMULATED STATE
    # ------------------------------------------------------------------

    simulated_state = build_simulated_state(
        baseline_orders=baseline_orders,
        baseline_daily_orders=baseline_daily_orders,
        baseline_daily_revenue=baseline_daily_revenue,
        baseline_aov=baseline_aov,
        baseline_inventory_units=baseline_inventory_units,
        baseline_inventory_cover_days=baseline_inventory_cover_days,
        baseline_review_score=baseline_review_score,
        baseline_seller_risk=baseline_seller_risk,
        demand_change_pct=DEMAND_CHANGE_PCT,
        inventory_change_pct=INVENTORY_CHANGE_PCT,
        supplier_pressure_pct=SUPPLIER_PRESSURE_PCT,
        customer_score_change=CUSTOMER_SCORE_CHANGE,
    )

    # ------------------------------------------------------------------
    # 5. STORE CURRENT SIMULATED STATE
    # ------------------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO current_simulated_state (
            snapshot_id,

            event_id,

            baseline_orders,
            simulated_orders,

            baseline_daily_orders,
            simulated_daily_orders,

            baseline_daily_revenue,
            simulated_daily_revenue,

            baseline_aov,
            simulated_aov,

            baseline_inventory_units,
            simulated_inventory_units,

            baseline_inventory_cover_days,
            simulated_inventory_cover_days,

            baseline_review_score,
            simulated_review_score,

            baseline_seller_risk,
            simulated_seller_risk,

            demand_state,
            inventory_state,
            supplier_state,
            customer_state,

            simulation_status,

            created_at
        )
        VALUES (
            1,
            1,

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

            'ACTIVE_SIMULATION',

            ?
        )
        """,
        (
            simulated_state["baseline_orders"],
            simulated_state["simulated_orders"],

            simulated_state["baseline_daily_orders"],
            simulated_state["simulated_daily_orders"],

            simulated_state["baseline_daily_revenue"],
            simulated_state["simulated_daily_revenue"],

            simulated_state["baseline_aov"],
            simulated_state["simulated_aov"],

            simulated_state["baseline_inventory_units"],
            simulated_state["simulated_inventory_units"],

            simulated_state["baseline_inventory_cover_days"],
            simulated_state["simulated_inventory_cover_days"],

            simulated_state["baseline_review_score"],
            simulated_state["simulated_review_score"],

            simulated_state["baseline_seller_risk"],
            simulated_state["simulated_seller_risk"],

            simulated_state["demand_state"],
            simulated_state["inventory_state"],
            simulated_state["supplier_state"],
            simulated_state["customer_state"],

            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    conn.commit()

    # ------------------------------------------------------------------
    # 6. VALIDATION OUTPUT
    # ------------------------------------------------------------------

    print("BASELINE")
    print("-" * 70)

    print(
        f"Daily Orders: "
        f"{simulated_state['baseline_daily_orders']:,.2f}"
    )
    print(
        f"Daily Revenue: "
        f"${simulated_state['baseline_daily_revenue']:,.2f}"
    )
    print(
        f"AOV: "
        f"${simulated_state['baseline_aov']:,.2f}"
    )
    print(
        f"Inventory Units: "
        f"{simulated_state['baseline_inventory_units']:,.2f}"
    )
    print(
        f"Inventory Cover: "
        f"{simulated_state['baseline_inventory_cover_days']:,.2f} days"
    )
    print(
        f"Review Score: "
        f"{simulated_state['baseline_review_score']:,.2f}"
    )
    print(
        f"Seller Risk: "
        f"{simulated_state['baseline_seller_risk']:,.2f}"
    )

    print()

    print("CONTROLLED BUSINESS EVENT")
    print("-" * 70)

    print(f"Event: {event_name}")
    print(f"Demand Change: +{DEMAND_CHANGE_PCT:.2f}%")
    print(f"Inventory Change: {INVENTORY_CHANGE_PCT:.2f}%")
    print(f"Supplier Pressure: +{SUPPLIER_PRESSURE_PCT:.2f}%")
    print(f"Customer Score Change: {CUSTOMER_SCORE_CHANGE:.2f}")

    print()

    print("SIMULATED CURRENT STATE")
    print("-" * 70)

    print(
        f"Daily Orders: "
        f"{simulated_state['simulated_daily_orders']:,.2f}"
    )
    print(
        f"Daily Revenue: "
        f"${simulated_state['simulated_daily_revenue']:,.2f}"
    )
    print(
        f"AOV: "
        f"${simulated_state['simulated_aov']:,.2f}"
    )
    print(
        f"Inventory Units: "
        f"{simulated_state['simulated_inventory_units']:,.2f}"
    )
    print(
        f"Inventory Cover: "
        f"{simulated_state['simulated_inventory_cover_days']:,.2f} days"
    )
    print(
        f"Review Score: "
        f"{simulated_state['simulated_review_score']:,.2f}"
    )
    print(
        f"Seller Risk: "
        f"{simulated_state['simulated_seller_risk']:,.2f}"
    )

    print()

    print("BUSINESS STATES")
    print("-" * 70)

    print(
        f"Demand State: "
        f"{simulated_state['demand_state']}"
    )
    print(
        f"Inventory State: "
        f"{simulated_state['inventory_state']}"
    )
    print(
        f"Supplier State: "
        f"{simulated_state['supplier_state']}"
    )
    print(
        f"Customer State: "
        f"{simulated_state['customer_state']}"
    )

    print()

    print("SIMULATION VALIDATION")
    print("-" * 70)

    print("Simulation Status: ACTIVE_SIMULATION")
    print("Event Source: SIMULATED")
    print("Historical Data Modified: NO")
    print("Randomness Used: NO")

    print()

    print("TABLES SAVED")
    print("-" * 70)

    print("  - simulation_events")
    print("  - current_simulated_state")

    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    run_simulation()
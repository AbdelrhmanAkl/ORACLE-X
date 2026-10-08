import json
import sqlite3
from datetime import datetime, timezone

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

RULE_NAME = "DEMAND_SUPPLY_IMBALANCE"
RULE_VERSION = "1.0"

DEMAND_INCREASE_THRESHOLD = 15.0
INVENTORY_COVER_DECLINE_THRESHOLD = 20.0
MAX_CURRENT_INVENTORY_COVER_DAYS = 10.0


def calculate_change_pct(current, baseline):
    if baseline == 0:
        return None

    return round(
        ((current - baseline) / baseline) * 100.0,
        10,
    )

def create_incidents_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            affected_dimension TEXT NOT NULL,
            snapshot_id INTEGER NOT NULL,
            evidence_json TEXT NOT NULL,
            rule_name TEXT NOT NULL,
            rule_version TEXT NOT NULL,
            source_type TEXT NOT NULL,
            UNIQUE(snapshot_id, rule_name, rule_version)
        )
        """
    )

    conn.commit()


def detect_demand_supply_imbalance(state):
    demand_change_pct = calculate_change_pct(
        state["simulated_daily_orders"],
        state["baseline_daily_orders"],
    )

    inventory_cover_change_pct = calculate_change_pct(
        state["simulated_inventory_cover_days"],
        state["baseline_inventory_cover_days"],
    )

    inventory_cover_decline_pct = (
        -inventory_cover_change_pct
        if inventory_cover_change_pct is not None
        else None
    )

    signals = {
        "demand_increase": (
            demand_change_pct is not None
            and demand_change_pct >= DEMAND_INCREASE_THRESHOLD
        ),
        "inventory_cover_decline": (
            inventory_cover_decline_pct is not None
            and inventory_cover_decline_pct
            >= INVENTORY_COVER_DECLINE_THRESHOLD
        ),
        "low_inventory_cover": (
            state["simulated_inventory_cover_days"]
            <= MAX_CURRENT_INVENTORY_COVER_DAYS
        ),
    }

    triggered = all(signals.values())

    evidence = {
        "baseline_daily_orders": state["baseline_daily_orders"],
        "simulated_daily_orders": state["simulated_daily_orders"],
        "demand_change_pct": (
            round(demand_change_pct, 2)
            if demand_change_pct is not None
            else None
        ),
        "baseline_inventory_cover_days": (
            state["baseline_inventory_cover_days"]
        ),
        "simulated_inventory_cover_days": (
            state["simulated_inventory_cover_days"]
        ),
        "inventory_cover_decline_pct": (
            round(inventory_cover_decline_pct, 2)
            if inventory_cover_decline_pct is not None
            else None
        ),
        "signals": signals,
        "thresholds": {
            "demand_increase_min_pct": DEMAND_INCREASE_THRESHOLD,
            "inventory_cover_decline_min_pct": (
                INVENTORY_COVER_DECLINE_THRESHOLD
            ),
            "max_inventory_cover_days": (
                MAX_CURRENT_INVENTORY_COVER_DAYS
            ),
        },
        "rule_name": RULE_NAME,
        "rule_version": RULE_VERSION,
        "source_type": "SIMULATED",
    }

    return triggered, evidence


def save_incident(conn, state, evidence):
    detected_at = datetime.now(timezone.utc).isoformat()

    title = "Demand and supply imbalance detected"

    summary = (
        "Simulated demand increased while inventory coverage "
        "declined below the configured safety threshold."
    )

    affected_dimension = "DEMAND_INVENTORY"

    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO incidents (
            detected_at,
            incident_type,
            severity,
            status,
            title,
            summary,
            affected_dimension,
            snapshot_id,
            evidence_json,
            rule_name,
            rule_version,
            source_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            detected_at,
            "DEMAND_SUPPLY_IMBALANCE",
            "HIGH",
            "DETECTED",
            title,
            summary,
            affected_dimension,
            state["snapshot_id"],
            json.dumps(evidence),
            RULE_NAME,
            RULE_VERSION,
            "SIMULATED",
        ),
    )

    conn.commit()

    if cursor.rowcount == 1:
        return cursor.lastrowid

    existing = conn.execute(
        """
        SELECT incident_id
        FROM incidents
        WHERE snapshot_id = ?
          AND rule_name = ?
          AND rule_version = ?
        """,
        (
            state["snapshot_id"],
            RULE_NAME,
            RULE_VERSION,
        ),
    ).fetchone()

    return existing["incident_id"]


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        create_incidents_table(conn)

        state = conn.execute(
            """
            SELECT *
            FROM current_simulated_state
            ORDER BY snapshot_id DESC
            LIMIT 1
            """
        ).fetchone()

        if state is None:
            raise RuntimeError(
                "No simulated business state found."
            )

        triggered, evidence = detect_demand_supply_imbalance(state)

        print("\n" + "=" * 80)
        print("ORACLE-X AUTONOMOUS DETECTION ENGINE")
        print("=" * 80)

        print(f"\nSnapshot ID: {state['snapshot_id']}")
        print(f"Simulation Status: {state['simulation_status']}")

        print("\n[DETECTION RULE]")
        print(f"Rule: {RULE_NAME}")
        print(f"Version: {RULE_VERSION}")

        print("\n[EVIDENCE]")
        print(json.dumps(evidence, indent=2))

        print("\n[RESULT]")

        if triggered:
            incident_id = save_incident(
                conn,
                state,
                evidence,
            )

            print("Incident detected: DEMAND_SUPPLY_IMBALANCE")
            print("Severity: HIGH")
            print("Status: DETECTED")
            print(f"Incident ID: {incident_id}")
        else:
            print("No incident detected.")

        print("\n" + "=" * 80)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
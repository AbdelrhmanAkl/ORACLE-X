import json
import sqlite3
from datetime import datetime, timezone

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH


class SimulationPersistenceAdapter:
    """
    Responsible only for persisting simulation events,
    simulated snapshots, and simulation incidents.
    """

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_simulation_event(self, scenario):
        """
        Save one simulation scenario as a simulation event.

        Returns:
            int: event_id
        """
        conn = self._connect()

        try:
            cursor = conn.execute(
                """
                INSERT INTO simulation_events (
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scenario.name,
                    scenario.event_type,
                    scenario.demand_change_pct,
                    scenario.inventory_change_pct,
                    scenario.supplier_pressure_pct,
                    scenario.customer_score_change,
                    scenario.description,
                    "SIMULATED",
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            event_id = cursor.lastrowid
            conn.commit()

            return event_id

        finally:
            conn.close()

    def save_simulated_state(self, event_id, state):
        """
        Save one simulated business state linked to an event.

        Returns:
            int: snapshot_id
        """
        conn = self._connect()

        try:
            cursor = conn.execute(
                """
                INSERT INTO current_simulated_state (
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
                    ?
                )
                """,
                (
                    event_id,
                    state["baseline_orders"],
                    state["simulated_orders"],
                    state["baseline_daily_orders"],
                    state["simulated_daily_orders"],
                    state["baseline_daily_revenue"],
                    state["simulated_daily_revenue"],
                    state["baseline_aov"],
                    state["simulated_aov"],
                    state["baseline_inventory_units"],
                    state["simulated_inventory_units"],
                    state["baseline_inventory_cover_days"],
                    state["simulated_inventory_cover_days"],
                    state["baseline_review_score"],
                    state["simulated_review_score"],
                    state["baseline_seller_risk"],
                    state["simulated_seller_risk"],
                    state["demand_state"],
                    state["inventory_state"],
                    state["supplier_state"],
                    state["customer_state"],
                    state["simulation_status"],
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            snapshot_id = cursor.lastrowid
            conn.commit()

            return snapshot_id

        finally:
            conn.close()

    def save_incident(self, state, evidence):
        """
        Save a detected simulation incident.

        Returns:
            int: incident_id
        """
        conn = self._connect()

        try:
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
                    datetime.now(timezone.utc).isoformat(),
                    "DEMAND_SUPPLY_IMBALANCE",
                    "HIGH",
                    "DETECTED",
                    "Demand and supply imbalance detected",
                    (
                        "Simulated demand increased while inventory "
                        "coverage declined below the configured "
                        "safety threshold."
                    ),
                    "DEMAND_INVENTORY",
                    state["snapshot_id"],
                    json.dumps(evidence),
                    evidence["rule_name"],
                    evidence["rule_version"],
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
                    evidence["rule_name"],
                    evidence["rule_version"],
                ),
            ).fetchone()

            return existing["incident_id"]

        finally:
            conn.close()

    def save_scenario(self, scenario, state):
        """
        Persist a scenario event and its resulting simulated state.

        Returns:
            dict containing event_id and snapshot_id.
        """
        event_id = self.save_simulation_event(scenario)

        snapshot_id = self.save_simulated_state(
            event_id,
            state,
        )

        return {
            "event_id": event_id,
            "snapshot_id": snapshot_id,
        }
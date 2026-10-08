import json
import sqlite3

from config.settings import DATABASE_PATH


class RootCauseAnalyzer:
    """
    Deterministic Root Cause Analysis for ORACLE-X.

    Important:
    - Historical data provides context.
    - Simulation provides controlled scenario evidence.
    - No causal certainty is claimed.
    - No LLM is used.
    """

    def __init__(self, database_path=DATABASE_PATH):
        self.database_path = database_path

    def _load_incident(self, cursor, incident_id):
        row = cursor.execute(
            """
            SELECT
                incident_id,
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
            FROM incidents
            WHERE incident_id = ?
            """,
            (incident_id,),
        ).fetchone()

        if row is None:
            raise ValueError(f"Incident {incident_id} not found.")

        columns = [
            "incident_id",
            "incident_type",
            "severity",
            "status",
            "title",
            "summary",
            "affected_dimension",
            "snapshot_id",
            "evidence_json",
            "rule_name",
            "rule_version",
            "source_type",
        ]

        incident = dict(zip(columns, row))
        incident["evidence"] = json.loads(incident["evidence_json"])

        return incident

    def _load_snapshot(self, cursor, snapshot_id):
        row = cursor.execute(
            """
            SELECT
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
                simulation_status
            FROM current_simulated_state
            WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        ).fetchone()

        if row is None:
            raise ValueError(f"Simulation snapshot {snapshot_id} not found.")

        columns = [
            "baseline_daily_orders",
            "simulated_daily_orders",
            "baseline_daily_revenue",
            "simulated_daily_revenue",
            "baseline_aov",
            "simulated_aov",
            "baseline_inventory_units",
            "simulated_inventory_units",
            "baseline_inventory_cover_days",
            "simulated_inventory_cover_days",
            "baseline_review_score",
            "simulated_review_score",
            "baseline_seller_risk",
            "simulated_seller_risk",
            "demand_state",
            "inventory_state",
            "supplier_state",
            "customer_state",
            "simulation_status",
        ]

        return dict(zip(columns, row))

    def _confidence(
        self,
        cause,
        demand_above_historical_max=False,
        historical_context_available=False,
    ):
        """
        Conservative, deterministic confidence assessment.

        Confidence reflects evidence strength, not causal certainty.
        Simulated or model-derived evidence cannot become HIGH confidence
        without sufficiently strong supporting evidence.
        """
        if cause == "Demand Surge":
            if (
                historical_context_available
                and demand_above_historical_max
            ):
                return "HIGH"

            if historical_context_available:
                return "MODERATE"

            return "LOW"

        if cause == "Inventory Pressure":
            return "MODERATE"

        if cause == "Supplier Pressure":
            return "LOW"

        if cause == "Customer Experience Deterioration":
            return "LOW"

        return "LOW"

    def analyze(self, incident_id):
        con = sqlite3.connect(self.database_path)

        try:
            cursor = con.cursor()

            incident = self._load_incident(cursor, incident_id)
            snapshot = self._load_snapshot(
                cursor,
                incident["snapshot_id"],
            )

            evidence = incident["evidence"]

            demand_change = evidence["demand_change_pct"]
            inventory_decline = evidence["inventory_cover_decline_pct"]
            supplier_pressure = snapshot["simulated_seller_risk"] - snapshot[
                "baseline_seller_risk"
            ]
            customer_change = (
                snapshot["simulated_review_score"]
                - snapshot["baseline_review_score"]
            )

            demand_above_historical_max = False

            historical_rows = cursor.execute(
                """
                SELECT COUNT(*)
                FROM orders
                WHERE DATE(order_purchase_timestamp)
                    BETWEEN ? AND ?
                GROUP BY DATE(order_purchase_timestamp)
                """,
                ("2018-08-01", "2018-08-22"),
            ).fetchall()

            historical_daily_orders = [row[0] for row in historical_rows]

            if historical_daily_orders:
                historical_max = max(historical_daily_orders)
                demand_above_historical_max = (
                    snapshot["simulated_daily_orders"] > historical_max
                )
            else:
                historical_max = None

            causes = []

            causes.append(
                {
                    "candidate_cause": "Demand Surge",
                    "evidence_for": (
                        f"Simulated demand increased by {demand_change:.2f}%."
                    ),
                    "evidence_against": (
                        f"Simulated daily orders "
                        f"({snapshot['simulated_daily_orders']:.2f}) "
                        f"remain below the historical maximum "
                        f"({historical_max}) for the validated baseline window."
                        if historical_max is not None
                        else "Historical comparison unavailable."
                    ),
                    "confidence": self._confidence(
                        "Demand Surge",
                        demand_above_historical_max=demand_above_historical_max,
                        historical_context_available=bool(
                            historical_daily_orders
                        ),
                    ),
                    "evidence_type": "SIMULATED_WITH_HISTORICAL_CONTEXT",
                }
            )

            causes.append(
                {
                    "candidate_cause": "Inventory Pressure",
                    "evidence_for": (
                        f"Inventory cover declined by {inventory_decline:.2f}%, "
                        f"from {snapshot['baseline_inventory_cover_days']:.2f} "
                        f"to {snapshot['simulated_inventory_cover_days']:.2f} days."
                    ),
                    "evidence_against": (
                        "Inventory level and coverage are model-derived because "
                        "the source dataset does not contain actual stock levels."
                    ),
                    "confidence": self._confidence("Inventory Pressure"),
                    "evidence_type": "SIMULATED_MODEL_DERIVED",
                }
            )

            causes.append(
                {
                    "candidate_cause": "Supplier Pressure",
                    "evidence_for": (
                        f"Simulated supplier pressure increased by "
                        f"{supplier_pressure:.2f} risk points, "
                        f"with supplier state "
                        f"{snapshot['supplier_state']}."
                    ),
                    "evidence_against": (
                        "Supplier pressure is a controlled simulated condition, "
                        "not an observed historical causal relationship."
                    ),
                    "confidence": self._confidence("Supplier Pressure"),
                    "evidence_type": "SIMULATED",
                }
            )

            causes.append(
                {
                    "candidate_cause": "Customer Experience Deterioration",
                    "evidence_for": (
                        f"Simulated review score declined by "
                        f"{abs(customer_change):.2f} points, "
                        f"from {snapshot['baseline_review_score']:.2f} "
                        f"to {snapshot['simulated_review_score']:.2f}."
                    ),
                    "evidence_against": (
                        "Customer deterioration is downstream simulated evidence "
                        "and does not establish causal origin."
                    ),
                    "confidence": self._confidence(
                        "Customer Experience Deterioration"
                    ),
                    "evidence_type": "SIMULATED_DOWNSTREAM_IMPACT",
                }
            )

            return {
                "incident_id": incident_id,
                "incident_type": incident["incident_type"],
                "severity": incident["severity"],
                "source_type": incident["source_type"],
                "candidate_causes": causes,
                "validation": {
                    "deterministic": True,
                    "llm_used": False,
                    "causal_certainty_claimed": False,
                    "historical_context_available": bool(
                        historical_daily_orders
                    ),
                    "demand_above_historical_max": demand_above_historical_max,
                },
            }

        finally:
            con.close()


def print_report(result):
    print("=" * 70)
    print("ORACLE-X ROOT CAUSE ANALYSIS")
    print("=" * 70)

    print(f"Incident ID: {result['incident_id']}")
    print(f"Incident Type: {result['incident_type']}")
    print(f"Severity: {result['severity']}")
    print(f"Source Type: {result['source_type']}")

    print("\nCANDIDATE CAUSES")

    for index, cause in enumerate(result["candidate_causes"], start=1):
        print(f"\n{index}. {cause['candidate_cause']}")
        print(f"Evidence For: {cause['evidence_for']}")
        print(f"Evidence Against: {cause['evidence_against']}")
        print(f"Confidence: {cause['confidence']}")
        print(f"Evidence Type: {cause['evidence_type']}")

    validation = result["validation"]

    print("\nRCA VALIDATION")
    print(f"Deterministic: {'YES' if validation['deterministic'] else 'NO'}")
    print(f"LLM Used: {'YES' if validation['llm_used'] else 'NO'}")
    print(
        "Causal Certainty Claimed: "
        f"{'YES' if validation['causal_certainty_claimed'] else 'NO'}"
    )
    print(
        "Historical Context Available: "
        f"{'YES' if validation['historical_context_available'] else 'NO'}"
    )
    print(
        "Demand Above Historical Maximum: "
        f"{'YES' if validation['demand_above_historical_max'] else 'NO'}"
    )


if __name__ == "__main__":
    analyzer = RootCauseAnalyzer()
    result = analyzer.analyze(incident_id=1)
    print_report(result)
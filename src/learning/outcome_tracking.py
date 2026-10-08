import sqlite3

from config.settings import DATABASE_PATH
from src.data.decision_outcome import save_decision_outcome


class OutcomeTrackingEngine:
    """
    Deterministic outcome tracking layer for ORACLE-X.

    Responsibilities:
    - Validate that a decision memory record exists.
    - Store observed outcome data.
    - Preserve outcome provenance.
    - Never infer or invent business outcomes.
    - Never use an LLM.
    """

    VERSION = "1.0"

    def record_outcome(
        self,
        investigation_id,
        outcome_status,
        observed_at,
        outcome_data,
        provenance,
        db_path=DATABASE_PATH,
    ):
        connection = sqlite3.connect(db_path)

        try:
            row = connection.execute(
                """
                SELECT
                    memory_id,
                    investigation_id
                FROM decision_memory
                WHERE investigation_id = ?
                """,
                (investigation_id,),
            ).fetchone()

        finally:
            connection.close()

        if row is None:
            return {
                "outcome_status": "NO_DECISION_FOUND",
                "investigation_id": investigation_id,
                "outcome_id": None,
                "constraints": {
                    "deterministic": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "outcome_inferred": False,
                },
                "provenance": {
                    "source": "DECISION_MEMORY",
                    "tracking_method": "DETERMINISTIC",
                },
                "version": self.VERSION,
            }

        memory_id = row[0]

        outcome_id = save_decision_outcome(
            memory_id=memory_id,
            investigation_id=investigation_id,
            outcome_status=outcome_status,
            observed_at=observed_at,
            outcome_data=outcome_data,
            provenance=provenance,
            db_path=db_path,
        )

        return {
            "outcome_status": "OUTCOME_RECORDED",
            "investigation_id": investigation_id,
            "memory_id": memory_id,
            "outcome_id": outcome_id,
            "constraints": {
                "deterministic": True,
                "llm_used": False,
                "business_facts_generated": False,
                "outcome_inferred": False,
            },
            "provenance": {
                "source": "OBSERVED_OUTCOME",
                "tracking_method": "DETERMINISTIC",
            },
            "version": self.VERSION,
        }
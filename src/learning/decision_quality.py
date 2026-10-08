import json
import sqlite3

from config.settings import DATABASE_PATH


class DecisionQualityEvaluator:
    """
    Deterministic decision-quality evaluator for ORACLE-X.

    Responsibilities:
    - Evaluate the structural quality of a stored decision.
    - Distinguish decision validity from business outcome.
    - Read observed outcomes when available.
    - Never claim success or failure without an observed outcome.
    - Never use an LLM.
    """

    VERSION = "1.0"

    def evaluate(
        self,
        investigation_id,
        db_path=DATABASE_PATH,
    ):
        connection = sqlite3.connect(db_path)

        try:
            row = connection.execute(
                """
                SELECT
                    memory_id,
                    decision_status,
                    validation_status,
                    recommended_action,
                    supporting_evidence_json
                FROM decision_memory
                WHERE investigation_id = ?
                """,
                (investigation_id,),
            ).fetchone()

            if row is None:
                return {
                    "quality_status": "NO_DECISION_FOUND",
                    "investigation_id": investigation_id,
                    "quality_score": None,
                    "outcome_status": "UNKNOWN",
                    "constraints": {
                        "deterministic": True,
                        "llm_used": False,
                        "business_facts_generated": False,
                        "outcome_claimed": False,
                    },
                    "provenance": {
                        "source": "DECISION_MEMORY",
                        "evaluation_method": "DETERMINISTIC",
                    },
                    "version": self.VERSION,
                }

            (
                memory_id,
                decision_status,
                validation_status,
                recommended_action,
                supporting_evidence_json,
            ) = row

            supporting_evidence_count = len(
                json.loads(
                    supporting_evidence_json
                )
            )

            outcome_row = connection.execute(
                """
                SELECT
                    outcome_id,
                    outcome_status,
                    observed_at
                FROM decision_outcomes
                WHERE memory_id = ?
                AND investigation_id = ?
                ORDER BY outcome_id DESC
                LIMIT 1
                """,
                (
                    memory_id,
                    investigation_id,
                ),
            ).fetchone()

            checks = {
                "decision_present": decision_status is not None,
                "validation_passed": validation_status == "VALID",
                "action_present": bool(recommended_action),
                "supporting_evidence_present": (
                    supporting_evidence_count > 0
                ),
            }

            passed_checks = sum(
                1 for value in checks.values() if value
            )

            quality_score = (
                passed_checks / len(checks)
            )

            if quality_score == 1.0:
                quality_status = "STRUCTURALLY_STRONG"
            elif quality_score >= 0.75:
                quality_status = "STRUCTURALLY_ACCEPTABLE"
            else:
                quality_status = "STRUCTURALLY_WEAK"

            if outcome_row is None:
                outcome_status = "UNKNOWN"
                outcome_id = None
                outcome_observed_at = None
            else:
                outcome_id = outcome_row[0]
                outcome_status = outcome_row[1]
                outcome_observed_at = outcome_row[2]

            return {
                "quality_status": quality_status,
                "investigation_id": investigation_id,
                "memory_id": memory_id,
                "quality_score": quality_score,
                "outcome_status": outcome_status,
                "outcome_id": outcome_id,
                "outcome_observed_at": outcome_observed_at,
                "checks": checks,
                "supporting_evidence_count": (
                    supporting_evidence_count
                ),
                "constraints": {
                    "deterministic": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "outcome_claimed": False,
                },
                "provenance": {
                    "source": "DECISION_MEMORY_AND_OUTCOMES",
                    "evaluation_method": "DETERMINISTIC",
                },
                "version": self.VERSION,
            }

        finally:
            connection.close()
import json
import sqlite3

from config.settings import DATABASE_PATH
from src.learning.outcome_evaluator import OutcomeEvaluator


class LearningEngine:
    """
    Deterministic learning layer for ORACLE-X.

    Responsibilities:
    - Read persisted decision memory.
    - Read observed decision outcomes when available.
    - Evaluate observed outcomes using deterministic rules.
    - Extract reusable learning signals.
    - Preserve decision and outcome provenance.
    - Never invent outcomes.
    - Never modify business rules.
    - Never use an LLM.
    """

    VERSION = "1.3"

    def learn(
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
                    incident_id,
                    snapshot_id,
                    investigation_id,
                    decision_status,
                    recommended_action,
                    rationale,
                    supporting_evidence_json,
                    validation_status,
                    validation_errors_json,
                    provenance_json,
                    created_at
                FROM decision_memory
                WHERE investigation_id = ?
                """,
                (investigation_id,),
            ).fetchone()

            if row is None:
                return {
                    "learning_status": "NO_MEMORY_FOUND",
                    "investigation_id": investigation_id,
                    "learning_signals": [],
                    "constraints": {
                        "deterministic": True,
                        "llm_used": False,
                        "business_facts_generated": False,
                        "outcome_claimed": False,
                        "rules_modified": False,
                    },
                    "provenance": {
                        "source": "DECISION_MEMORY",
                        "learning_method": (
                            "DETERMINISTIC_MEMORY_AND_OUTCOME_ANALYSIS"
                        ),
                    },
                    "version": self.VERSION,
                }

            (
                memory_id,
                incident_id,
                snapshot_id,
                stored_investigation_id,
                decision_status,
                recommended_action,
                rationale,
                supporting_evidence_json,
                validation_status,
                validation_errors_json,
                provenance_json,
                created_at,
            ) = row

            supporting_evidence = json.loads(
                supporting_evidence_json
            )

            provenance = json.loads(provenance_json)

            outcome_row = connection.execute(
                """
                SELECT
                    outcome_id,
                    outcome_status,
                    observed_at,
                    outcome_data_json,
                    provenance_json
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

            learning_signals = []

            if validation_status == "VALID":
                learning_signals.append(
                    {
                        "signal": "VALIDATED_DECISION",
                        "evidence": (
                            "The stored decision passed deterministic "
                            "validation."
                        ),
                        "evidence_type": "OBSERVED_DECISION_RECORD",
                    }
                )

            if decision_status == "ACTIONABLE":
                learning_signals.append(
                    {
                        "signal": "ACTIONABLE_DECISION",
                        "evidence": (
                            "The stored decision produced an actionable "
                            "recommendation."
                        ),
                        "evidence_type": "OBSERVED_DECISION_RECORD",
                    }
                )

            if supporting_evidence:
                learning_signals.append(
                    {
                        "signal": "EVIDENCE_BACKED_DECISION",
                        "evidence": (
                            f"{len(supporting_evidence)} supporting "
                            "evidence item(s) were stored."
                        ),
                        "evidence_type": "OBSERVED_DECISION_RECORD",
                    }
                )

            outcome_evaluation = None
            learning_conclusion = None

            if outcome_row is None:
                outcome_status = "UNKNOWN"
                outcome_id = None
                outcome_observed_at = None
                outcome_data = None
                outcome_provenance = None

            else:
                (
                    outcome_id,
                    outcome_status,
                    outcome_observed_at,
                    outcome_data_json,
                    outcome_provenance_json,
                ) = outcome_row

                outcome_data = json.loads(
                    outcome_data_json
                )

                outcome_provenance = json.loads(
                    outcome_provenance_json
                )

                learning_signals.append(
                    {
                        "signal": "OBSERVED_OUTCOME_AVAILABLE",
                        "evidence": (
                            f"Outcome {outcome_id} was observed for "
                            f"the stored decision with status "
                            f"{outcome_status}."
                        ),
                        "evidence_type": "OBSERVED_OUTCOME",
                    }
                )

                inventory_cover_days = outcome_data.get(
                    "inventory_cover_days"
                )

                outcome_evaluation = (
                    OutcomeEvaluator()
                    .evaluate_inventory_cover(
                        inventory_cover_days
                    )
                )

                learning_signals.append(
                    {
                        "signal": "OUTCOME_EVALUATED",
                        "evidence": (
                            f"Outcome classified as "
                            f"{outcome_evaluation['outcome_class']} "
                            "using inventory cover days."
                        ),
                        "evidence_type": (
                            "DETERMINISTIC_OUTCOME_EVALUATION"
                        ),
                    }
                )

                outcome_class = (
                    outcome_evaluation["outcome_class"]
                )

                if outcome_class == "POSITIVE_OUTCOME":
                    learning_conclusion = (
                        "POSITIVE_OUTCOME_LEARNED"
                    )

                    learning_signals.append(
                        {
                            "signal": (
                                "POSITIVE_OUTCOME_LEARNED"
                            ),
                            "evidence": (
                                "The observed outcome met the "
                                "configured deterministic success "
                                "threshold."
                            ),
                            "evidence_type": (
                                "DETERMINISTIC_OUTCOME_LEARNING"
                            ),
                        }
                    )

                elif outcome_class == "NEGATIVE_OUTCOME":
                    learning_conclusion = (
                        "NEGATIVE_OUTCOME_LEARNED"
                    )

                    learning_signals.append(
                        {
                            "signal": (
                                "NEGATIVE_OUTCOME_LEARNED"
                            ),
                            "evidence": (
                                "The observed outcome did not meet "
                                "the configured deterministic "
                                "success threshold."
                            ),
                            "evidence_type": (
                                "DETERMINISTIC_OUTCOME_LEARNING"
                            ),
                        }
                    )

                elif outcome_class == "INCONCLUSIVE_OUTCOME":
                    learning_conclusion = (
                        "INCONCLUSIVE_OUTCOME"
                    )

            return {
                "learning_status": "LEARNING_SIGNALS_EXTRACTED",
                "memory_id": memory_id,
                "incident_id": incident_id,
                "snapshot_id": snapshot_id,
                "investigation_id": stored_investigation_id,
                "decision_status": decision_status,
                "recommended_action": recommended_action,
                "rationale": rationale,
                "learning_signals": learning_signals,
                "learning_conclusion": learning_conclusion,
                "memory_created_at": created_at,
                "decision_provenance": provenance,
                "outcome": {
                    "outcome_id": outcome_id,
                    "outcome_status": outcome_status,
                    "observed_at": outcome_observed_at,
                    "outcome_data": outcome_data,
                    "provenance": outcome_provenance,
                    "evaluation": outcome_evaluation,
                },
                "constraints": {
                    "deterministic": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "outcome_claimed": False,
                    "rules_modified": False,
                },
                "provenance": {
                    "source": (
                        "DECISION_MEMORY_AND_OUTCOMES"
                    ),
                    "learning_method": (
                        "DETERMINISTIC_MEMORY_AND_OUTCOME_ANALYSIS"
                    ),
                    "memory_id": memory_id,
                    "outcome_id": outcome_id,
                },
                "version": self.VERSION,
            }

        finally:
            connection.close()
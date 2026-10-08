import json
import sqlite3

from config.settings import DATABASE_PATH


class AdaptiveIntelligenceEngine:
    """
    Read-only adaptive intelligence layer for ORACLE-X.

    Responsibilities:
    - Read observed decision outcomes.
    - Count eligible observations.
    - Produce deterministic adaptive insights.
    - Never modify business rules.
    - Never modify thresholds.
    - Never use an LLM.
    - Never invent outcomes.
    """

    VERSION = "1.1"
    MINIMUM_OBSERVATIONS = 3
    INVENTORY_COVER_THRESHOLD_DAYS = 10.0

    def analyze(
        self,
        db_path=DATABASE_PATH,
    ):
        connection = sqlite3.connect(db_path)

        try:
            rows = connection.execute(
                """
                SELECT
                    outcome_id,
                    memory_id,
                    investigation_id,
                    outcome_status,
                    observed_at,
                    outcome_data_json,
                    provenance_json
                FROM decision_outcomes
                ORDER BY outcome_id ASC
                """
            ).fetchall()

            observation_count = len(rows)

            if observation_count < self.MINIMUM_OBSERVATIONS:
                return {
                    "adaptive_status": (
                        "INSUFFICIENT_LEARNING_DATA"
                    ),
                    "observation_count": observation_count,
                    "insights": [],
                    "proposals": [],
                    "constraints": {
                        "deterministic": True,
                        "read_only": True,
                        "llm_used": False,
                        "business_facts_generated": False,
                        "rules_modified": False,
                        "thresholds_modified": False,
                    },
                    "provenance": {
                        "source": "DECISION_OUTCOMES",
                        "analysis_method": (
                            "DETERMINISTIC_OBSERVATION_COUNT"
                        ),
                    },
                    "version": self.VERSION,
                }

            observations = []

            for row in rows:
                (
                    outcome_id,
                    memory_id,
                    investigation_id,
                    outcome_status,
                    observed_at,
                    outcome_data_json,
                    provenance_json,
                ) = row

                observations.append(
                    {
                        "outcome_id": outcome_id,
                        "memory_id": memory_id,
                        "investigation_id": investigation_id,
                        "outcome_status": outcome_status,
                        "observed_at": observed_at,
                        "outcome_data": json.loads(
                            outcome_data_json
                        ),
                        "provenance": json.loads(
                            provenance_json
                        ),
                    }
                )

            positive_count = 0
            negative_count = 0
            inconclusive_count = 0

            for observation in observations:
                inventory_cover_days = observation[
                    "outcome_data"
                ].get("inventory_cover_days")

                if inventory_cover_days is None:
                    inconclusive_count += 1
                elif (
                    inventory_cover_days
                    >= self.INVENTORY_COVER_THRESHOLD_DAYS
                ):
                    positive_count += 1
                else:
                    negative_count += 1

            classified_count = (
                positive_count
                + negative_count
            )

            insights = [
                {
                    "insight_type": (
                        "OBSERVED_OUTCOME_DISTRIBUTION"
                    ),
                    "metric": "inventory_cover_days",
                    "observation_count": observation_count,
                    "classified_observations": (
                        classified_count
                    ),
                    "positive_outcomes": positive_count,
                    "negative_outcomes": negative_count,
                    "inconclusive_outcomes": (
                        inconclusive_count
                    ),
                    "threshold_days": (
                        self.INVENTORY_COVER_THRESHOLD_DAYS
                    ),
                    "provenance": (
                        "OBSERVED_OUTCOME"
                    ),
                }
            ]

            return {
                "adaptive_status": (
                    "ADAPTIVE_ANALYSIS_AVAILABLE"
                ),
                "observation_count": observation_count,
                "insights": insights,
                "proposals": [],
                "constraints": {
                    "deterministic": True,
                    "read_only": True,
                    "llm_used": False,
                    "business_facts_generated": False,
                    "rules_modified": False,
                    "thresholds_modified": False,
                },
                "provenance": {
                    "source": "DECISION_OUTCOMES",
                    "analysis_method": (
                        "DETERMINISTIC_OBSERVED_OUTCOME_ANALYSIS"
                    ),
                    "observation_ids": [
                        observation["outcome_id"]
                        for observation in observations
                    ],
                },
                "version": self.VERSION,
            }

        finally:
            connection.close()
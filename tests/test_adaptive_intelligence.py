import json
import sqlite3
import tempfile
from pathlib import Path

from src.learning.adaptive_intelligence import (
    AdaptiveIntelligenceEngine,
)


def create_test_database(path):
    connection = sqlite3.connect(path)

    connection.execute(
        """
        CREATE TABLE decision_outcomes (
            outcome_id INTEGER PRIMARY KEY,
            memory_id INTEGER NOT NULL,
            investigation_id TEXT NOT NULL,
            outcome_status TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            outcome_data_json TEXT NOT NULL,
            provenance_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def insert_outcome(
    path,
    outcome_id,
    memory_id,
    investigation_id,
    inventory_cover_days,
):
    connection = sqlite3.connect(path)

    connection.execute(
        """
        INSERT INTO decision_outcomes (
            outcome_id,
            memory_id,
            investigation_id,
            outcome_status,
            observed_at,
            outcome_data_json,
            provenance_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            outcome_id,
            memory_id,
            investigation_id,
            "OBSERVED",
            "2026-10-07T00:00:00+00:00",
            json.dumps(
                {
                    "inventory_cover_days": (
                        inventory_cover_days
                    )
                }
            ),
            json.dumps(
                {
                    "source": "TEST",
                    "type": "TEMPORARY",
                }
            ),
            "2026-10-07T00:00:00+00:00",
        ),
    )

    connection.commit()
    connection.close()


def test_insufficient_learning_data():
    with tempfile.TemporaryDirectory() as directory:
        db_path = str(
            Path(directory) / "adaptive_test.db"
        )

        create_test_database(db_path)

        result = AdaptiveIntelligenceEngine().analyze(
            db_path=db_path
        )

        assert (
            result["adaptive_status"]
            == "INSUFFICIENT_LEARNING_DATA"
        )
        assert result["observation_count"] == 0
        assert result["insights"] == []
        assert result["proposals"] == []

        assert (
            result["constraints"]["rules_modified"]
            is False
        )
        assert (
            result["constraints"]["thresholds_modified"]
            is False
        )


def test_adaptive_analysis_with_three_observations():
    with tempfile.TemporaryDirectory() as directory:
        db_path = str(
            Path(directory) / "adaptive_test.db"
        )

        create_test_database(db_path)

        insert_outcome(
            db_path,
            1,
            101,
            "TEST-1",
            12,
        )

        insert_outcome(
            db_path,
            2,
            102,
            "TEST-2",
            11,
        )

        insert_outcome(
            db_path,
            3,
            103,
            "TEST-3",
            8,
        )

        result = AdaptiveIntelligenceEngine().analyze(
            db_path=db_path
        )

        assert (
            result["adaptive_status"]
            == "ADAPTIVE_ANALYSIS_AVAILABLE"
        )
        assert result["observation_count"] == 3

        assert len(result["insights"]) == 1

        insight = result["insights"][0]

        assert (
            insight["insight_type"]
            == "OBSERVED_OUTCOME_DISTRIBUTION"
        )
        assert (
            insight["metric"]
            == "inventory_cover_days"
        )
        assert insight["observation_count"] == 3
        assert insight["classified_observations"] == 3
        assert insight["positive_outcomes"] == 2
        assert insight["negative_outcomes"] == 1
        assert insight["inconclusive_outcomes"] == 0
        assert insight["threshold_days"] == 10.0
        assert (
            insight["provenance"]
            == "OBSERVED_OUTCOME"
        )

        assert result["proposals"] == []

        assert (
            result["constraints"]["rules_modified"]
            is False
        )
        assert (
            result["constraints"]["thresholds_modified"]
            is False
        )
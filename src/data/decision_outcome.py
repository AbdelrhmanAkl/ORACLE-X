import json
import sqlite3
from datetime import datetime, timezone

from config.settings import DATABASE_PATH


CREATE_DECISION_OUTCOMES_TABLE = """
CREATE TABLE IF NOT EXISTS decision_outcomes (
    outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    investigation_id TEXT NOT NULL,
    outcome_status TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    outcome_data_json TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (memory_id)
        REFERENCES decision_memory(memory_id)
)
"""


def create_decision_outcomes_table(db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(CREATE_DECISION_OUTCOMES_TABLE)
        connection.commit()

    finally:
        connection.close()


def save_decision_outcome(
    memory_id,
    investigation_id,
    outcome_status,
    observed_at,
    outcome_data,
    provenance,
    db_path=DATABASE_PATH,
):
    create_decision_outcomes_table(db_path)

    connection = sqlite3.connect(db_path)

    try:
        existing_outcome = connection.execute(
            """
            SELECT outcome_id
            FROM decision_outcomes
            WHERE memory_id = ?
            AND investigation_id = ?
            """,
            (
                memory_id,
                investigation_id,
            ),
        ).fetchone()

        if existing_outcome is not None:
            return existing_outcome[0]

        created_at = datetime.now(timezone.utc).isoformat()

        cursor = connection.execute(
            """
            INSERT INTO decision_outcomes (
                memory_id,
                investigation_id,
                outcome_status,
                observed_at,
                outcome_data_json,
                provenance_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                investigation_id,
                outcome_status,
                observed_at,
                json.dumps(
                    outcome_data,
                    ensure_ascii=False,
                ),
                json.dumps(
                    provenance,
                    ensure_ascii=False,
                ),
                created_at,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()
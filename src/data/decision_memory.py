import json
import sqlite3
from datetime import datetime, timezone

from config.settings import DATABASE_PATH


CREATE_DECISION_MEMORY_TABLE = """
CREATE TABLE IF NOT EXISTS decision_memory (
    memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    snapshot_id INTEGER NOT NULL,
    investigation_id TEXT NOT NULL UNIQUE,
    decision_status TEXT NOT NULL,
    recommended_action TEXT,
    rationale TEXT NOT NULL,
    supporting_evidence_json TEXT NOT NULL,
    validation_status TEXT NOT NULL,
    validation_errors_json TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (incident_id)
        REFERENCES incidents(incident_id),
    FOREIGN KEY (snapshot_id)
        REFERENCES current_simulated_state(snapshot_id)
)
"""


def create_decision_memory_table(db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(CREATE_DECISION_MEMORY_TABLE)
        connection.commit()

    finally:
        connection.close()


def save_decision_memory(
    incident_id,
    snapshot_id,
    investigation_id,
    decision,
    decision_validation,
    db_path=DATABASE_PATH,
):
    create_decision_memory_table(db_path)

    connection = sqlite3.connect(db_path)

    try:
        existing_memory = connection.execute(
            """
            SELECT memory_id
            FROM decision_memory
            WHERE investigation_id = ?
            """,
            (investigation_id,),
        ).fetchone()

        if existing_memory is not None:
            return existing_memory[0]

        created_at = datetime.now(timezone.utc).isoformat()

        cursor = connection.execute(
            """
            INSERT INTO decision_memory (
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
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident_id,
                snapshot_id,
                investigation_id,
                decision["decision_status"],
                decision["recommended_action"],
                decision["rationale"],
                json.dumps(
                    decision["supporting_evidence"],
                    ensure_ascii=False,
                ),
                decision_validation["validation_status"],
                json.dumps(
                    decision_validation["errors"],
                    ensure_ascii=False,
                ),
                json.dumps(
                    decision["provenance"],
                    ensure_ascii=False,
                ),
                created_at,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()
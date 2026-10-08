import sqlite3

from config.settings import DATABASE_PATH


def migrate_decision_memory(db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)

    try:
        connection.execute("PRAGMA foreign_keys = OFF")

        connection.execute(
            """
            CREATE TABLE decision_memory_new (
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
        )

        connection.execute(
            """
            INSERT INTO decision_memory_new (
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
            )
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
            """
        )

        connection.execute(
            "DROP TABLE decision_memory"
        )

        connection.execute(
            """
            ALTER TABLE decision_memory_new
            RENAME TO decision_memory
            """
        )

        connection.commit()

    finally:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.close()


if __name__ == "__main__":
    migrate_decision_memory()
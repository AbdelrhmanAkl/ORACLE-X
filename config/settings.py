import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

DATABASE_PATH = Path(
    os.getenv(
        "ORACLE_X_DB_PATH",
        str(DATA_DIR / "oracle_x.db"),
    )
)

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
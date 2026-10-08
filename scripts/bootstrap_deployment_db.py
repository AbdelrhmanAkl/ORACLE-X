import hashlib
import os
import zipfile
from pathlib import Path
from urllib.request import urlopen


DB_URL = os.environ["ORACLE_X_DB_URL"]
DB_SHA256 = os.environ["ORACLE_X_DB_SHA256"]
DB_PATH = Path(
    os.getenv(
        "ORACLE_X_DB_PATH",
        "/tmp/oracle_x_deploy.db",
    )
)

ZIP_PATH = DB_PATH.with_suffix(".zip")


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(url, timeout=120) as response:
        with destination.open("wb") as file:
            while chunk := response.read(1024 * 1024):
                file.write(chunk)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    if DB_PATH.exists():
        print(f"Deployment database already exists: {DB_PATH}")
        return

    print(f"Downloading deployment database from: {DB_URL}")
    download_file(DB_URL, ZIP_PATH)

    actual_sha256 = sha256_file(ZIP_PATH)

    if actual_sha256 != DB_SHA256:
        raise RuntimeError(
            "Deployment database checksum mismatch: "
            f"expected={DB_SHA256}, actual={actual_sha256}"
        )

    print("Checksum verified.")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        database_members = [
            name
            for name in archive.namelist()
            if name.endswith(".db")
        ]

        if len(database_members) != 1:
            raise RuntimeError(
                "Expected exactly one database in archive, "
                f"found: {database_members}"
            )

        extracted_path = Path(
            archive.extract(database_members[0], DB_PATH.parent)
        )

    if extracted_path != DB_PATH:
        extracted_path.replace(DB_PATH)

    if not DB_PATH.exists():
        raise RuntimeError(
            f"Database was not found after extraction: {DB_PATH}"
        )

    print(f"Deployment database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
"""Database connection and initialization helpers for HRS."""

from __future__ import annotations

import sqlite3
from pathlib import Path

try:
    from .models import DATABASE_FILENAME, TABLE_STATEMENTS
except ImportError:  # Supports running modules directly from database/.
    from models import DATABASE_FILENAME, TABLE_STATEMENTS

DATABASE_PATH = Path(__file__).resolve().parent / DATABASE_FILENAME


class DatabaseError(RuntimeError):
    """Raised when SQLite cannot complete an HRS database operation."""


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys and row dictionaries enabled."""
    path = Path(db_path) if db_path is not None else DATABASE_PATH
    try:
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    except sqlite3.Error as error:
        raise DatabaseError(f"Unable to connect to the HRS database: {error}") from error


def initialize_database(db_path: str | Path | None = None) -> Path:
    """Create all HRS database tables when they do not already exist."""
    path = Path(db_path) if db_path is not None else DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with get_connection(path) as connection:
            for statement in TABLE_STATEMENTS:
                connection.execute(statement)
    except sqlite3.Error as error:
        raise DatabaseError(f"Unable to initialize the HRS database: {error}") from error
    return path


if __name__ == "__main__":
    print(f"Database initialized: {initialize_database()}")

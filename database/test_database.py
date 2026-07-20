"""Utility for validating the HRS database layer without creating sample doctor data."""

from __future__ import annotations

from database import get_connection, initialize_database


def main() -> None:
    """Initialize the database and print the created tables for verification."""
    database_path = initialize_database()
    with get_connection() as connection:
        foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        tables = [row["name"] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall() if row["name"] in {"doctors", "patients", "visits", "tokens"}]

    print(f"Database: {database_path}")
    print(f"Foreign keys enabled: {foreign_keys_enabled}")
    print(f"Required tables: {', '.join(tables)}")


if __name__ == "__main__":
    main()

"""Typed CRUD operations for the Health Registration System SQLite database."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, datetime
from functools import wraps
from typing import Any

try:
    from .database import DatabaseError, get_connection, initialize_database
    from .models import PATIENT_ID_PREFIX, TOKEN_PREFIX
except ImportError:  # Supports running this module directly from database/.
    from database import DatabaseError, get_connection, initialize_database
    from models import PATIENT_ID_PREFIX, TOKEN_PREFIX

Record = dict[str, Any]


def _record(row: sqlite3.Row | None) -> Record | None:
    """Convert a SQLite row into a standard dictionary."""
    return dict(row) if row is not None else None


def _records(rows: list[sqlite3.Row]) -> list[Record]:
    """Convert SQLite rows into standard dictionaries."""
    return [dict(row) for row in rows]


def _require_text(value: str, field_name: str) -> str:
    """Return a non-empty text value or raise a clear validation error."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required.")
    return value.strip()


def _iso_now() -> str:
    """Return the local system timestamp in ISO 8601 format."""
    return datetime.now().isoformat(timespec="seconds")


def _handle_database_errors(function: Any) -> Any:
    """Translate SQLite exceptions into one application-level exception type."""
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except sqlite3.Error as error:
            raise DatabaseError(f"Database operation failed: {error}") from error
    return wrapper


def _next_patient_id(connection: sqlite3.Connection) -> str:
    """Build the next patient ID from the largest existing numeric suffix."""
    row = connection.execute(
        "SELECT MAX(CAST(SUBSTR(patient_id, 4) AS INTEGER)) AS last_number "
        "FROM patients WHERE patient_id GLOB 'PAT[0-9]*'"
    ).fetchone()
    next_number = (row["last_number"] or 0) + 1
    return f"{PATIENT_ID_PREFIX}{next_number:06d}"


def _next_token_number(connection: sqlite3.Connection, token_date: date) -> str:
    """Build the next unique token number for the supplied local calendar day."""
    date_part = token_date.strftime("%Y%m%d")
    prefix = f"{TOKEN_PREFIX}-{date_part}-"
    row = connection.execute(
        "SELECT MAX(CAST(SUBSTR(token_number, ?) AS INTEGER)) AS last_number "
        "FROM tokens WHERE token_number LIKE ?",
        (len(prefix) + 1, f"{prefix}%"),
    ).fetchone()
    next_number = (row["last_number"] or 0) + 1
    return f"{prefix}{next_number:04d}"


@_handle_database_errors
def add_doctor(doctor_name: str, department: str | None = None, room_no: str | None = None,
               block_no: str | None = None, phone_number: str | None = None,
               status: str | None = "Active") -> Record:
    """Add a doctor and return the inserted record."""
    initialize_database()
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            """INSERT INTO doctors
            (doctor_name, department, room_no, block_no, phone_number, status)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (_require_text(doctor_name, "doctor_name"), department, room_no, block_no, phone_number, status),
        )
        doctor_id = cursor.lastrowid
    doctor = get_doctor_by_id(doctor_id)
    if doctor is None:
        raise RuntimeError("Doctor was not saved.")
    return doctor


@_handle_database_errors
def update_doctor(doctor_id: int, **fields: Any) -> Record | None:
    """Update allowed doctor fields and return the updated record."""
    allowed = {"doctor_name", "department", "room_no", "block_no", "phone_number", "status"}
    updates = {name: value for name, value in fields.items() if name in allowed}
    if not updates:
        raise ValueError("Provide at least one doctor field to update.")
    if "doctor_name" in updates:
        updates["doctor_name"] = _require_text(updates["doctor_name"], "doctor_name")
    assignments = ", ".join(f"{name} = ?" for name in updates)
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(f"UPDATE doctors SET {assignments} WHERE doctor_id = ?",
                                    (*updates.values(), doctor_id))
    return get_doctor_by_id(doctor_id) if cursor.rowcount else None


@_handle_database_errors
def delete_doctor(doctor_id: int) -> bool:
    """Delete a doctor while preserving linked history with a null doctor link."""
    with closing(get_connection()) as connection, connection:
        return connection.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,)).rowcount > 0


@_handle_database_errors
def get_doctor_by_id(doctor_id: int) -> Record | None:
    """Return one doctor by ID, or None when it does not exist."""
    with closing(get_connection()) as connection:
        return _record(connection.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,)).fetchone())


@_handle_database_errors
def get_all_doctors() -> list[Record]:
    """Return all doctors ordered by their numeric ID."""
    with closing(get_connection()) as connection:
        return _records(connection.execute("SELECT * FROM doctors ORDER BY doctor_id").fetchall())


@_handle_database_errors
def add_patient(patient_name: str, patient_phone: str | None = None, gender: str | None = None,
                date_of_birth: str | None = None, patient_aadhaar: str | None = None,
                insurance_provider: str | None = None, insurance_number: str | None = None,
                attender_name: str | None = None, attender_phone: str | None = None,
                allergies: str | None = None, unsuitable_medicines: str | None = None) -> Record:
    """Create a patient with the next generated patient ID."""
    initialize_database()
    with closing(get_connection()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        patient_id = _next_patient_id(connection)
        connection.execute(
            """INSERT INTO patients (
                patient_id, patient_name, patient_phone, gender, date_of_birth,
                patient_aadhaar, insurance_provider, insurance_number, attender_name,
                attender_phone, allergies, unsuitable_medicines
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, _require_text(patient_name, "patient_name"), patient_phone, gender,
             date_of_birth, patient_aadhaar, insurance_provider, insurance_number,
             attender_name, attender_phone, allergies, unsuitable_medicines),
        )
        connection.commit()
    patient = get_patient_details(patient_id)
    if patient is None:
        raise RuntimeError("Patient was not saved.")
    return patient


@_handle_database_errors
def update_patient(patient_id: str, **fields: Any) -> Record | None:
    """Update allowed patient fields and return the updated record."""
    allowed = {"patient_name", "patient_phone", "gender", "date_of_birth", "patient_aadhaar",
               "insurance_provider", "insurance_number", "attender_name", "attender_phone",
               "allergies", "unsuitable_medicines"}
    updates = {name: value for name, value in fields.items() if name in allowed}
    if not updates:
        raise ValueError("Provide at least one patient field to update.")
    if "patient_name" in updates:
        updates["patient_name"] = _require_text(updates["patient_name"], "patient_name")
    assignments = ", ".join(f"{name} = ?" for name in updates)
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(f"UPDATE patients SET {assignments} WHERE patient_id = ?",
                                    (*updates.values(), patient_id))
    return get_patient_details(patient_id) if cursor.rowcount else None


@_handle_database_errors
def delete_patient(patient_id: str) -> bool:
    """Delete a patient while preserving linked history with null patient links."""
    with closing(get_connection()) as connection, connection:
        return connection.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,)).rowcount > 0


@_handle_database_errors
def search_patient_by_id(patient_id: str) -> Record | None:
    """Search for a patient by their generated patient ID."""
    return get_patient_details(patient_id)


@_handle_database_errors
def search_patients_by_aadhaar(patient_aadhaar: str) -> list[Record]:
    """Return patients whose Aadhaar value exactly matches the supplied value."""
    with closing(get_connection()) as connection:
        rows = connection.execute("SELECT * FROM patients WHERE patient_aadhaar = ? ORDER BY patient_id",
                                  (patient_aadhaar,)).fetchall()
    return _records(rows)


@_handle_database_errors
def search_patients_by_phone(patient_phone: str) -> list[Record]:
    """Return patients whose phone value exactly matches the supplied value."""
    with closing(get_connection()) as connection:
        rows = connection.execute("SELECT * FROM patients WHERE patient_phone = ? ORDER BY patient_id",
                                  (patient_phone,)).fetchall()
    return _records(rows)


@_handle_database_errors
def get_patient_details(patient_id: str) -> Record | None:
    """Return one patient by ID, or None when it does not exist."""
    with closing(get_connection()) as connection:
        return _record(connection.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone())


@_handle_database_errors
def add_visit(patient_id: str, doctor_id: int, visit_date: str | None = None,
              symptoms: str | None = None, problem_description: str | None = None,
              temperature: float | None = None, heart_rate: float | None = None,
              room_temperature: float | None = None, humidity: float | None = None,
              report_path: str | None = None) -> Record:
    """Add a visit that is linked to an existing patient and doctor."""
    initialize_database()
    if get_patient_details(patient_id) is None:
        raise ValueError("patient_id does not refer to an existing patient.")
    if get_doctor_by_id(doctor_id) is None:
        raise ValueError("doctor_id does not refer to an existing doctor.")
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            """INSERT INTO visits (
                patient_id, doctor_id, visit_date, symptoms, problem_description,
                temperature, heart_rate, room_temperature, humidity, report_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, doctor_id, visit_date or _iso_now(), symptoms, problem_description,
             temperature, heart_rate, room_temperature, humidity, report_path),
        )
        visit_id = cursor.lastrowid
    visit = get_visit_by_id(visit_id)
    if visit is None:
        raise RuntimeError("Visit was not saved.")
    return visit


@_handle_database_errors
def get_visit_by_id(visit_id: int) -> Record | None:
    """Return one visit by ID, or None when it does not exist."""
    with closing(get_connection()) as connection:
        return _record(connection.execute("SELECT * FROM visits WHERE visit_id = ?", (visit_id,)).fetchone())


@_handle_database_errors
def update_visit_report_path(visit_id: int, report_path: str) -> Record | None:
    """Store the generated PDF path for an existing visit."""
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            "UPDATE visits SET report_path = ? WHERE visit_id = ?",
            (report_path, visit_id),
        )
    return get_visit_by_id(visit_id) if cursor.rowcount else None


@_handle_database_errors
def delete_token(token_id: int) -> bool:
    """Delete a token created for a cancelled, unreported visit draft."""
    with closing(get_connection()) as connection, connection:
        return connection.execute("DELETE FROM tokens WHERE token_id = ?", (token_id,)).rowcount > 0


@_handle_database_errors
def delete_visit(visit_id: int) -> bool:
    """Delete an unreported visit draft after its token has been removed."""
    with closing(get_connection()) as connection, connection:
        return connection.execute("DELETE FROM visits WHERE visit_id = ?", (visit_id,)).rowcount > 0


@_handle_database_errors
def get_visit_history_for_patient(patient_id: str) -> list[Record]:
    """Return all visits for a patient, newest first."""
    with closing(get_connection()) as connection:
        rows = connection.execute(
            "SELECT * FROM visits WHERE patient_id = ? ORDER BY visit_date DESC, visit_id DESC",
            (patient_id,),
        ).fetchall()
    return _records(rows)


@_handle_database_errors
def get_previous_visits(patient_id: str) -> list[Record]:
    """Return a patient's previous visits; an alias for visit-history retrieval."""
    return get_visit_history_for_patient(patient_id)


@_handle_database_errors
def generate_token_record(patient_id: str, visit_id: int,
                          generated_time: str | None = None) -> Record:
    """Generate and save a daily token after validating its patient/visit link."""
    initialize_database()
    with closing(get_connection()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        visit = connection.execute("SELECT patient_id FROM visits WHERE visit_id = ?", (visit_id,)).fetchone()
        if visit is None:
            connection.rollback()
            raise ValueError("visit_id does not refer to an existing visit.")
        if visit["patient_id"] != patient_id:
            connection.rollback()
            raise ValueError("The selected visit does not belong to the supplied patient.")
        if connection.execute("SELECT 1 FROM patients WHERE patient_id = ?", (patient_id,)).fetchone() is None:
            connection.rollback()
            raise ValueError("patient_id does not refer to an existing patient.")
        token_number = _next_token_number(connection, date.today())
        timestamp = generated_time or _iso_now()
        cursor = connection.execute(
            "INSERT INTO tokens (token_number, patient_id, visit_id, generated_time) VALUES (?, ?, ?, ?)",
            (token_number, patient_id, visit_id, timestamp),
        )
        token_id = cursor.lastrowid
        connection.commit()
    token = get_token_by_id(token_id)
    if token is None:
        raise RuntimeError("Token was not saved.")
    return token


@_handle_database_errors
def get_token_by_id(token_id: int) -> Record | None:
    """Return one token by ID, or None when it does not exist."""
    with closing(get_connection()) as connection:
        return _record(connection.execute("SELECT * FROM tokens WHERE token_id = ?", (token_id,)).fetchone())


@_handle_database_errors
def get_token_by_number(token_number: str) -> Record | None:
    """Return one token by its unique display number."""
    with closing(get_connection()) as connection:
        return _record(connection.execute("SELECT * FROM tokens WHERE token_number = ?", (token_number,)).fetchone())

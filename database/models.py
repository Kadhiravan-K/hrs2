"""Shared SQLite schema definitions for the Health Registration System."""

DATABASE_FILENAME = "hrs.db"
PATIENT_ID_PREFIX = "PAT"
TOKEN_PREFIX = "HRS"

CREATE_DOCTORS_TABLE = """
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_name TEXT NOT NULL,
    department TEXT,
    room_no TEXT,
    block_no TEXT,
    phone_number TEXT,
    status TEXT DEFAULT 'Active',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""

CREATE_PATIENTS_TABLE = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    patient_name TEXT NOT NULL,
    patient_phone TEXT,
    gender TEXT,
    date_of_birth TEXT,
    patient_aadhaar TEXT,
    insurance_provider TEXT,
    insurance_number TEXT,
    attender_name TEXT,
    attender_phone TEXT,
    allergies TEXT,
    unsuitable_medicines TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""

CREATE_VISITS_TABLE = """
CREATE TABLE IF NOT EXISTS visits (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    doctor_id INTEGER,
    visit_date TEXT NOT NULL,
    symptoms TEXT,
    problem_description TEXT,
    temperature REAL,
    heart_rate REAL,
    room_temperature REAL,
    humidity REAL,
    report_path TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE SET NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
);
"""

CREATE_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS tokens (
    token_id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_number TEXT NOT NULL UNIQUE,
    patient_id TEXT,
    visit_id INTEGER,
    generated_time TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE SET NULL,
    FOREIGN KEY (visit_id) REFERENCES visits(visit_id) ON DELETE SET NULL
);
"""

TABLE_STATEMENTS = (
    CREATE_DOCTORS_TABLE,
    CREATE_PATIENTS_TABLE,
    CREATE_VISITS_TABLE,
    CREATE_TOKENS_TABLE,
)

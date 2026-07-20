"""Patient validation and database-facing operations for HRS."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from database import queries

Record = dict[str, Any]


class ValidationError(ValueError):
    """Raised when user-entered information is not valid for HRS."""


class PatientService:
    """Validate, search, and register patients without UI dependencies."""

    @staticmethod
    def validate_phone(phone: str | None) -> str | None:
        """Validate an optional Indian-style ten digit phone number."""
        if not phone or not phone.strip():
            return None
        normalized = "".join(character for character in phone if character.isdigit())
        if len(normalized) != 10:
            raise ValidationError("Phone number must contain exactly 10 digits.")
        return normalized

    @staticmethod
    def validate_date_of_birth(date_of_birth: str) -> str:
        """Validate an ISO date that is not in the future."""
        try:
            parsed = datetime.strptime(date_of_birth.strip(), "%Y-%m-%d").date()
        except (TypeError, ValueError) as error:
            raise ValidationError("Date of birth must use YYYY-MM-DD format.") from error
        if parsed > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        return parsed.isoformat()

    @staticmethod
    def validate_required(value: str, label: str) -> str:
        """Return required text or raise a readable validation error."""
        if not value or not value.strip():
            raise ValidationError(f"{label} is required.")
        return value.strip()

    def find_existing(self, search_type: str, search_value: str) -> list[Record]:
        """Search patients by one supported identifier."""
        value = self.validate_required(search_value, search_type)
        if search_type == "Patient ID":
            patient = queries.search_patient_by_id(value.upper())
            return [patient] if patient else []
        if search_type == "Aadhaar":
            return queries.search_patients_by_aadhaar(value)
        if search_type == "Phone":
            return queries.search_patients_by_phone(self.validate_phone(value) or "")
        raise ValidationError("Choose Patient ID, Aadhaar, or Phone for searching.")

    def _ensure_not_duplicate(self, patient_name: str, phone: str | None, aadhaar: str | None) -> None:
        """Block exact Aadhaar or normalized name-and-phone duplicate patients."""
        if aadhaar and aadhaar.strip() and queries.search_patients_by_aadhaar(aadhaar.strip()):
            raise ValidationError("A patient with this Aadhaar number already exists.")
        if phone:
            name_key = " ".join(patient_name.casefold().split())
            for patient in queries.search_patients_by_phone(phone):
                existing_name = " ".join(str(patient["patient_name"]).casefold().split())
                if existing_name == name_key:
                    raise ValidationError("A patient with this name and phone number already exists.")

    def register_new(self, values: dict[str, str]) -> Record:
        """Validate and create a full new-patient record."""
        name = self.validate_required(values.get("patient_name", ""), "Patient name")
        phone = self.validate_phone(self.validate_required(values.get("patient_phone", ""), "Patient phone number"))
        gender = self.validate_required(values.get("gender", ""), "Gender")
        dob = self.validate_date_of_birth(self.validate_required(values.get("date_of_birth", ""), "Date of birth"))
        aadhaar = values.get("patient_aadhaar", "").strip() or None
        self._ensure_not_duplicate(name, phone, aadhaar)
        return queries.add_patient(
            patient_name=name,
            patient_phone=phone,
            gender=gender,
            date_of_birth=dob,
            patient_aadhaar=aadhaar,
            insurance_provider=values.get("insurance_provider", "").strip() or None,
            insurance_number=values.get("insurance_number", "").strip() or None,
            attender_name=values.get("attender_name", "").strip() or None,
            attender_phone=self.validate_phone(values.get("attender_phone", "")),
            allergies=values.get("allergies", "").strip() or None,
            unsuitable_medicines=values.get("unsuitable_medicines", "").strip() or None,
        )

    def register_emergency(self, values: dict[str, str]) -> tuple[Record, int]:
        """Create a minimal patient record and return the entered emergency age."""
        name = values.get("patient_name", "").strip() or "Emergency Patient"
        gender = values.get("gender", "").strip() or None
        try:
            age = int(values.get("age", ""))
        except (TypeError, ValueError) as error:
            raise ValidationError("Emergency age must be a whole number.") from error
        if not 0 <= age <= 120:
            raise ValidationError("Emergency age must be between 0 and 120.")
        phone = self.validate_phone(values.get("patient_phone", ""))
        attender_name = self.validate_required(values.get("attender_name", ""), "Attender name")
        attender_phone = self.validate_phone(self.validate_required(values.get("attender_phone", ""), "Attender phone number"))
        self._ensure_not_duplicate(name, phone, None)
        patient = queries.add_patient(
            patient_name=name,
            patient_phone=phone,
            gender=gender,
            attender_name=attender_name,
            attender_phone=attender_phone,
        )
        return patient, age

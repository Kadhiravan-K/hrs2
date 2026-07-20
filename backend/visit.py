"""In-progress visit state and persistence operations for HRS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from database import queries

Record = dict[str, Any]


@dataclass
class VisitDraft:
    """Data collected across HRS screens before a PDF is generated."""

    patient: Record
    flow_type: str
    previous_history: list[Record]
    visit_type: str | None = None
    emergency_age: int | None = None
    symptoms: list[str] = field(default_factory=list)
    questionnaire: dict[str, str] = field(default_factory=dict)
    doctor: Record | None = None
    sensor_readings: dict[str, dict[str, float | str]] = field(default_factory=dict)
    visit: Record | None = None
    token: Record | None = None


class VisitService:
    """Create, cancel, and finalize patient visits using existing tables."""

    QUESTION_LABELS = (
        "Days symptoms have been present",
        "Do you have fever?",
        "Do you have pain?",
        "Are you taking medicines?",
        "Any previous medical condition?",
    )

    def begin_draft(self, patient: Record, flow_type: str, visit_type: str | None = None,
                    emergency_age: int | None = None) -> VisitDraft:
        """Capture history before the new visit is created."""
        history = queries.get_visit_history_for_patient(patient["patient_id"])
        return VisitDraft(patient, flow_type, history, visit_type, emergency_age)

    @staticmethod
    def display_age(draft: VisitDraft) -> str:
        """Return entered emergency age or calculate age from a stored date of birth."""
        if draft.emergency_age is not None:
            return str(draft.emergency_age)
        date_of_birth = draft.patient.get("date_of_birth")
        if not date_of_birth:
            return "Not provided"
        try:
            born = datetime.strptime(str(date_of_birth), "%Y-%m-%d").date()
        except ValueError:
            return "Not provided"
        today = date.today()
        return str(today.year - born.year - ((today.month, today.day) < (born.month, born.day)))

    @staticmethod
    def set_symptoms(draft: VisitDraft, symptoms: list[str]) -> None:
        """Validate and set the user-selected symptoms."""
        if not symptoms:
            raise ValueError("Select at least one symptom.")
        draft.symptoms = symptoms

    def set_questionnaire(self, draft: VisitDraft, answers: dict[str, str]) -> None:
        """Validate the five required question answers."""
        if set(answers) != set(self.QUESTION_LABELS) or any(not value.strip() for value in answers.values()):
            raise ValueError("Answer all five basic questions.")
        draft.questionnaire = answers

    @staticmethod
    def _reading_value(draft: VisitDraft, key: str) -> float | None:
        value = draft.sensor_readings.get(key, {}).get("value")
        return float(value) if value is not None else None

    @staticmethod
    def _format_questionnaire(draft: VisitDraft) -> str:
        """Store non-schema visit details in the existing description field."""
        lines = [f"Visit Type: {draft.visit_type or draft.flow_type.title()}"]
        if draft.emergency_age is not None:
            lines.append(f"Emergency Age: {draft.emergency_age}")
        if draft.flow_type == "emergency":
            lines.append("Questionnaire: Not collected (emergency)")
        else:
            lines.append("Questionnaire:")
            lines.extend(f"- {question}: {answer}" for question, answer in draft.questionnaire.items())
        return "\n".join(lines)

    def create_preview_records(self, draft: VisitDraft) -> VisitDraft:
        """Create the visit and final token required by the report preview."""
        if draft.doctor is None:
            raise ValueError("Select a doctor before continuing.")
        if not draft.sensor_readings:
            raise ValueError("Read sensor values before continuing.")
        draft.visit = queries.add_visit(
            patient_id=draft.patient["patient_id"],
            doctor_id=int(draft.doctor["doctor_id"]),
            visit_date=datetime.now().isoformat(timespec="seconds"),
            symptoms=", ".join(draft.symptoms),
            problem_description=self._format_questionnaire(draft),
            temperature=self._reading_value(draft, "body_temperature"),
            heart_rate=self._reading_value(draft, "heart_rate"),
            room_temperature=self._reading_value(draft, "room_temperature"),
            humidity=self._reading_value(draft, "humidity"),
        )
        draft.token = queries.generate_token_record(draft.patient["patient_id"], draft.visit["visit_id"])
        return draft

    @staticmethod
    def cancel_preview_records(draft: VisitDraft) -> None:
        """Remove a visit/token draft when the user goes back or cancels."""
        if draft.token is not None:
            queries.delete_token(int(draft.token["token_id"]))
        if draft.visit is not None:
            queries.delete_visit(int(draft.visit["visit_id"]))
        draft.token = None
        draft.visit = None

    @staticmethod
    def save_report_path(draft: VisitDraft, report_path: str) -> Record:
        """Attach a completed report path to a saved visit."""
        if draft.visit is None:
            raise ValueError("No visit is available to update.")
        updated = queries.update_visit_report_path(int(draft.visit["visit_id"]), report_path)
        if updated is None:
            raise RuntimeError("The saved visit could not be updated with its report path.")
        draft.visit = updated
        return updated

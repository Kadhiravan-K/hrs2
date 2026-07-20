"""PDF report generation for Health Registration System visits."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.visit import VisitDraft, VisitService


class ReportGenerationError(RuntimeError):
    """Raised when a PDF report cannot be created."""


class ReportService:
    """Generate one local PDF report per completed visit token."""

    def __init__(self, reports_directory: str | Path | None = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.reports_directory = Path(reports_directory) if reports_directory else root / "reports"

    @staticmethod
    def _history_lines(history: list[dict[str, Any]]) -> list[str]:
        """Convert previous visit records into compact PDF lines."""
        if not history:
            return ["No previous visit history."]
        return [
            f"{visit['visit_date']}: {visit.get('symptoms') or 'No symptoms recorded'}"
            for visit in history
        ]

    def generate_report(self, draft: VisitDraft) -> str:
        """Create and return the PDF path for a saved draft and token."""
        if draft.visit is None or draft.token is None or draft.doctor is None:
            raise ReportGenerationError("Visit, token, and doctor are required before generating a report.")
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
        except ImportError as error:
            raise ReportGenerationError("ReportLab is not installed. Install it before generating reports.") from error

        self.reports_directory.mkdir(parents=True, exist_ok=True)
        output_path = self.reports_directory / f"{draft.token['token_number']}.pdf"
        styles = getSampleStyleSheet()
        body = styles["BodyText"]
        title = styles["Title"]

        def safe(value: Any) -> str:
            return str(value if value not in (None, "") else "Not provided").replace("&", "&amp;").replace("<", "&lt;")

        patient = draft.patient
        doctor = draft.doctor
        readings = draft.sensor_readings
        lines = [
            ("Token Number", draft.token["token_number"]),
            ("Patient ID", patient["patient_id"]),
            ("Patient Name", patient["patient_name"]),
            ("Age", VisitService.display_age(draft)),
            ("Gender", patient.get("gender")),
            ("Symptoms", ", ".join(draft.symptoms)),
            ("Allergies", patient.get("allergies")),
            ("Medicines Not Suitable", patient.get("unsuitable_medicines")),
            ("Doctor", doctor["doctor_name"]),
            ("Department", doctor.get("department")),
            ("Room / Block", f"{doctor.get('room_no') or '-'} / {doctor.get('block_no') or '-'}"),
            ("Body Temperature", f"{readings['body_temperature']['value']} °C"),
            ("Heart Rate", f"{readings['heart_rate']['value']} BPM"),
            ("Room Temperature", f"{readings['room_temperature']['value']} °C"),
            ("Humidity", f"{readings['humidity']['value']} %"),
            ("Visit Date", draft.visit["visit_date"]),
        ]
        story = [Paragraph("Health Registration System Report", title), Spacer(1, 12)]
        story.extend(Paragraph(f"<b>{label}:</b> {safe(value)}", body) for label, value in lines)
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Question Answers</b>", body))
        if draft.flow_type == "emergency":
            story.append(Paragraph("Not collected (emergency).", body))
        else:
            story.extend(Paragraph(f"{safe(question)}: {safe(answer)}", body)
                         for question, answer in draft.questionnaire.items())
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Previous History</b>", body))
        story.extend(Paragraph(safe(line), body) for line in self._history_lines(draft.previous_history))
        try:
            SimpleDocTemplate(str(output_path), pagesize=A4).build(story)
        except Exception as error:
            raise ReportGenerationError(f"Could not create PDF report: {error}") from error
        return str(output_path)

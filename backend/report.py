"""Print-ready PDF report generation for Health Registration System visits."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.visit import VisitDraft, VisitService


class ReportGenerationError(RuntimeError):
    """Raised when a PDF report cannot be created."""


class ReportService:
    """Generate one professional local PDF report per completed visit token."""

    def __init__(self, reports_directory: str | Path | None = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.reports_directory = Path(reports_directory) if reports_directory else root / "reports"

    @staticmethod
    def _history_lines(history: list[dict[str, Any]]) -> list[str]:
        """Convert previous visit records into compact report lines."""
        if not history:
            return ["No previous visit history."]
        return [f"{visit['visit_date']}: {visit.get('symptoms') or 'No symptoms recorded'}" for visit in history]

    def generate_report(self, draft: VisitDraft) -> str:
        """Create a structured A4 PDF and return its local path."""
        if draft.visit is None or draft.token is None or draft.doctor is None:
            raise ReportGenerationError("Visit, token, and doctor are required before generating a report.")
        try:
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_RIGHT
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError as error:
            raise ReportGenerationError("ReportLab is not installed. Install it before generating reports.") from error

        self.reports_directory.mkdir(parents=True, exist_ok=True)
        output_path = self.reports_directory / f"{draft.token['token_number']}.pdf"
        navy = colors.HexColor("#143B5A")
        blue = colors.HexColor("#2563EB")
        pale_blue = colors.HexColor("#EAF4FF")
        border = colors.HexColor("#C9D9E8")
        ink = colors.HexColor("#18324A")
        muted = colors.HexColor("#5F7286")
        styles = getSampleStyleSheet()
        body = ParagraphStyle("HRSBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9,
                              leading=13, textColor=ink, spaceAfter=0)
        label = ParagraphStyle("HRSLabel", parent=body, fontName="Helvetica-Bold", textColor=navy)
        section = ParagraphStyle("HRSSection", parent=body, fontName="Helvetica-Bold", fontSize=10,
                                 textColor=colors.white, leading=13)
        header_title = ParagraphStyle("HRSHeader", parent=body, fontName="Helvetica-Bold", fontSize=18,
                                      leading=22, textColor=colors.white)
        header_subtitle = ParagraphStyle("HRSHeaderSub", parent=body, fontSize=8.5, leading=11,
                                         textColor=colors.white, alignment=TA_RIGHT)

        def safe(value: Any) -> str:
            text = str(value if value not in (None, "") else "Not provided")
            return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")

        def value_cell(value: Any) -> Paragraph:
            return Paragraph(safe(value), body)

        def label_cell(value: str) -> Paragraph:
            return Paragraph(value, label)

        def section_bar(title: str) -> Table:
            table = Table([[Paragraph(title, section)]], colWidths=[170 * mm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), navy),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            return table

        def details_table(rows: list[list[Any]], widths: list[float]) -> Table:
            table = Table(rows, colWidths=widths, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, border),
                ("BACKGROUND", (0, 0), (0, -1), pale_blue),
                ("BACKGROUND", (2, 0), (2, -1), pale_blue),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            return table

        patient = draft.patient
        doctor = draft.doctor
        readings = draft.sensor_readings
        page_width = 170 * mm
        header = Table([
            [Paragraph("Health Registration System", header_title),
             Paragraph(f"PATIENT REPORT<br/>Token: {safe(draft.token['token_number'])}", header_subtitle)],
        ], colWidths=[110 * mm, 60 * mm])
        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), navy),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        patient_rows = [
            [label_cell("Patient Name"), value_cell(patient["patient_name"]), label_cell("Patient ID"), value_cell(patient["patient_id"])],
            [label_cell("Age / Gender"), value_cell(f"{VisitService.display_age(draft)} / {patient.get('gender') or 'Not provided'}"),
             label_cell("Visit Date"), value_cell(draft.visit["visit_date"])],
            [label_cell("Attender"), value_cell(patient.get("attender_name")), label_cell("Attender Phone"), value_cell(patient.get("attender_phone"))],
        ]
        doctor_rows = [
            [label_cell("Doctor"), value_cell(doctor["doctor_name"]), label_cell("Department"), value_cell(doctor.get("department"))],
            [label_cell("Room Number"), value_cell(doctor.get("room_no")), label_cell("Block Number"), value_cell(doctor.get("block_no"))],
        ]
        vital_rows = [
            [Paragraph("Body Temperature", label), Paragraph("Heart Rate", label), Paragraph("Room Temperature", label), Paragraph("Humidity", label)],
            [value_cell(f"{readings['body_temperature']['value']} deg C"), value_cell(f"{readings['heart_rate']['value']} BPM"),
             value_cell(f"{readings['room_temperature']['value']} deg C"), value_cell(f"{readings['humidity']['value']} %")],
        ]
        vital_table = Table(vital_rows, colWidths=[page_width / 4] * 4)
        vital_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.45, border),
            ("BACKGROUND", (0, 0), (-1, 0), pale_blue),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        questions = "Not collected (emergency)." if draft.flow_type == "emergency" else "<br/>".join(
            f"<b>{safe(question)}:</b> {safe(answer)}" for question, answer in draft.questionnaire.items()
        )
        history = "<br/>".join(safe(line) for line in self._history_lines(draft.previous_history))
        story = [header, Spacer(1, 10), section_bar("PATIENT AND VISIT DETAILS"),
                 details_table(patient_rows, [30 * mm, 55 * mm, 30 * mm, 55 * mm]), Spacer(1, 10),
                 section_bar("ASSIGNED DOCTOR"), details_table(doctor_rows, [30 * mm, 55 * mm, 30 * mm, 55 * mm]), Spacer(1, 10),
                 section_bar("VITAL SIGNS"), vital_table, Spacer(1, 10),
                 section_bar("CLINICAL INTAKE")]
        intake_rows = [
            [label_cell("Symptoms"), value_cell(", ".join(draft.symptoms))],
            [label_cell("Allergies"), value_cell(patient.get("allergies"))],
            [label_cell("Medicines Not Suitable"), value_cell(patient.get("unsuitable_medicines"))],
        ]
        intake = Table(intake_rows, colWidths=[45 * mm, 125 * mm])
        intake.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.45, border),
            ("BACKGROUND", (0, 0), (0, -1), pale_blue),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.extend([intake, Spacer(1, 10), section_bar("QUESTION ANSWERS"),
                      Table([[Paragraph(questions, body)]], colWidths=[page_width], style=TableStyle([
                          ("BOX", (0, 0), (-1, -1), 0.45, border), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                          ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7),
                          ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                      ])), Spacer(1, 10), section_bar("PREVIOUS VISIT HISTORY"),
                      Table([[Paragraph(history, body)]], colWidths=[page_width], style=TableStyle([
                          ("BOX", (0, 0), (-1, -1), 0.45, border), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                          ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7),
                          ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                      ]))])

        def decorate_page(canvas: Any, document: Any) -> None:
            canvas.saveState()
            canvas.setStrokeColor(blue)
            canvas.setLineWidth(0.8)
            canvas.line(20 * mm, 14 * mm, 190 * mm, 14 * mm)
            canvas.setFillColor(muted)
            canvas.setFont("Helvetica", 7.5)
            canvas.drawString(20 * mm, 9 * mm, "Health Registration System - Local Patient Report")
            canvas.drawRightString(190 * mm, 9 * mm, f"Page {document.page}")
            canvas.restoreState()

        try:
            document = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
                                         topMargin=18 * mm, bottomMargin=22 * mm, title="HRS Patient Report")
            document.build(story, onFirstPage=decorate_page, onLaterPages=decorate_page)
        except Exception as error:
            raise ReportGenerationError(f"Could not create PDF report: {error}") from error
        return str(output_path)

"""Report preview and final PDF generation screen for HRS."""

from __future__ import annotations

import os
import subprocess
from tkinter import messagebox, ttk
from typing import Any

from backend.report import ReportGenerationError
from frontend.home import BaseScreen


class ReportPreviewScreen(BaseScreen):
    """Show every collected value before the final PDF is created."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Report Preview", "Review the collected information before generating the PDF report.")
        if app.draft is None or app.draft.visit is None or app.draft.token is None or app.draft.doctor is None:
            ttk.Label(self, text="No completed visit draft is available.").pack(anchor="w")
            ttk.Button(self, text="Return Home", command=app.cancel_preview).pack(anchor="w", pady=16)
            return

        draft = app.draft
        patient = draft.patient
        doctor = draft.doctor
        readings = draft.sensor_readings
        rows = [
            ("Token Number", draft.token["token_number"]),
            ("Patient ID", patient["patient_id"]),
            ("Patient Name", patient["patient_name"]),
            ("Age", self.app.visit_service.display_age(draft)),
            ("Gender", patient.get("gender") or "Not provided"),
            ("Symptoms", ", ".join(draft.symptoms)),
            ("Allergies", patient.get("allergies") or "Not provided"),
            ("Medicines Not Suitable", patient.get("unsuitable_medicines") or "Not provided"),
            ("Doctor", doctor["doctor_name"]),
            ("Department", doctor.get("department") or "Not provided"),
            ("Room Number", doctor.get("room_no") or "Not provided"),
            ("Block Number", doctor.get("block_no") or "Not provided"),
            ("Body Temperature", f"{readings['body_temperature']['value']} °C"),
            ("Heart Rate", f"{readings['heart_rate']['value']} BPM"),
            ("Room Temperature", f"{readings['room_temperature']['value']} °C"),
            ("Humidity", f"{readings['humidity']['value']} %"),
            ("Visit Date", draft.visit["visit_date"]),
        ]
        content = self.add_scrollable_content()
        summary = ttk.Frame(content, style="Card.TFrame", padding=22)
        summary.pack(fill="x", padx=2, pady=(0, 8))
        for row, (label, value) in enumerate(rows):
            ttk.Label(summary, text=f"{label}:", font=("Segoe UI", 10, "bold")).grid(
                row=row, column=0, sticky="nw", padx=(0, 12), pady=2
            )
            ttk.Label(summary, text=str(value), wraplength=680).grid(row=row, column=1, sticky="w", pady=2)

        ttk.Label(summary, text="Question Answers:", font=("Segoe UI", 10, "bold")).grid(
            row=len(rows), column=0, sticky="nw", padx=(0, 12), pady=(8, 2)
        )
        answers = "Not collected (emergency)." if draft.flow_type == "emergency" else "\n".join(
            f"{question}: {answer}" for question, answer in draft.questionnaire.items()
        )
        ttk.Label(summary, text=answers, wraplength=680).grid(row=len(rows), column=1, sticky="w", pady=(8, 2))
        history_text = "No previous visit history." if not draft.previous_history else "\n".join(
            f"{visit['visit_date']}: {visit.get('symptoms') or 'No symptoms recorded'}"
            for visit in draft.previous_history
        )
        ttk.Label(summary, text="Previous History:", font=("Segoe UI", 10, "bold")).grid(
            row=len(rows) + 1, column=0, sticky="nw", padx=(0, 12), pady=(8, 2)
        )
        ttk.Label(summary, text=history_text, wraplength=680).grid(row=len(rows) + 1, column=1, sticky="w", pady=(8, 2))

        actions = ttk.Frame(content)
        actions.pack(fill="x", pady=(14, 8))
        ttk.Button(actions, text="Back", command=self.go_back, style="Secondary.TButton").pack(side="left")
        ttk.Button(actions, text="Cancel", command=app.cancel_preview, style="Secondary.TButton").pack(side="left", padx=8)
        ttk.Button(actions, text="Generate Report", command=self.generate_report, style="Primary.TButton").pack(side="right")

    def go_back(self) -> None:
        """Remove reserved records and return to sensor collection for changes."""
        from frontend.sensor_screen import SensorScreen
        if self.app.draft is not None:
            self.app.visit_service.cancel_preview_records(self.app.draft)
        self.app.show_screen(SensorScreen)

    def generate_report(self) -> None:
        """Generate the PDF, save its existing report path, and complete the visit."""
        if self.app.draft is None:
            return
        try:
            report_path = self.app.report_service.generate_report(self.app.draft)
            self.app.visit_service.save_report_path(self.app.draft, report_path)
        except (ReportGenerationError, RuntimeError, ValueError) as error:
            messagebox.showerror("Report generation", str(error), parent=self)
            return
        self.show_report_complete(report_path)

    def show_report_complete(self, report_path: str) -> None:
        """Offer optional printing before starting the next registration loop."""
        for child in self.winfo_children():
            child.destroy()
        self.add_title("Report Generated", "The report has been saved successfully.")
        card = self.add_card()
        ttk.Label(card, text="Patient report is ready", style="Section.TLabel").pack(anchor="w")
        ttk.Label(card, text=report_path, style="Card.TLabel", wraplength=760).pack(anchor="w", pady=(10, 24))
        actions = ttk.Frame(card, style="Card.TFrame")
        actions.pack(anchor="w")
        ttk.Button(actions, text="Print Report", command=lambda: self.print_report(report_path),
                   style="Secondary.TButton").pack(side="left")
        ttk.Button(actions, text="Next Registration", command=self.next_registration,
                   style="Primary.TButton").pack(side="left", padx=10)

    def print_report(self, report_path: str) -> None:
        """Send the completed PDF to the operating system's configured printer."""
        try:
            if os.name == "nt":
                os.startfile(report_path, "print")  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["lp", report_path])
        except (OSError, FileNotFoundError) as error:
            messagebox.showerror("Print report", f"Could not send the report to a printer:\n{error}", parent=self)
            return
        messagebox.showinfo("Print report", "The report was sent to the system printer.", parent=self)

    def next_registration(self) -> None:
        """Return to Home and begin the next patient registration."""
        from frontend.home import HomeScreen
        self.app.clear_draft()
        self.app.show_screen(HomeScreen)

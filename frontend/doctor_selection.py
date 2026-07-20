"""Doctor selection screen backed by the existing doctors table."""

from __future__ import annotations

from tkinter import messagebox, ttk
from typing import Any

from frontend.home import BaseScreen


class DoctorSelectionScreen(BaseScreen):
    """List active doctors and require exactly one selection."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Doctor Selection", "A recommendation is preselected from the selected symptoms; you can choose any doctor.")
        self.doctors = app.doctor_service.get_active_doctors()
        self.recommended_doctor = self._recommend_doctor()
        content = self.add_scrollable_content()
        card = ttk.Frame(content, style="Card.TFrame", padding=22)
        card.pack(fill="x", padx=2, pady=(0, 8))
        recommendation = (f"Recommended: {self.recommended_doctor['doctor_name']} - "
                          f"{self.recommended_doctor['department']}"
                          if self.recommended_doctor else "No symptom-based recommendation is available.")
        ttk.Label(card, text=recommendation, style="Section.TLabel").pack(anchor="w", pady=(0, 14))
        self.table = ttk.Treeview(card, columns=("name", "department", "room", "block"), show="headings", height=12)
        for key, label, width in (("name", "Doctor Name", 250), ("department", "Department", 250),
                                  ("room", "Room Number", 140), ("block", "Block Number", 140)):
            self.table.heading(key, text=label)
            self.table.column(key, width=width)
        self.table.pack(fill="both", expand=True)
        for doctor in self.doctors:
            self.table.insert("", "end", iid=str(doctor["doctor_id"]), values=(
                doctor["doctor_name"], doctor.get("department") or "-", doctor.get("room_no") or "-",
                doctor.get("block_no") or "-"
            ))
        if self.recommended_doctor is not None:
            self.table.selection_set(str(self.recommended_doctor["doctor_id"]))
            self.table.focus(str(self.recommended_doctor["doctor_id"]))
        self.notice = ttk.Label(card, text="" if self.doctors else "No active doctors are available in the database.", style="Card.TLabel")
        self.notice.pack(anchor="w", pady=(10, 0))
        self.continue_button = self.add_navigation(self.go_back, self.continue_visit, parent=content)
        if not self.doctors:
            self.continue_button.configure(state="disabled")

    def _recommend_doctor(self) -> dict | None:
        """Suggest a doctor from symptoms without overriding manual selection."""
        if self.app.draft is None:
            return None
        symptoms = {symptom.split(":", 1)[0].strip() for symptom in self.app.draft.symptoms}
        department_by_symptom = {
            "Chest Pain": "Cardiology", "High Blood Pressure": "Cardiology", "Low Blood Pressure": "Cardiology",
            "Joint Pain": "Orthopedics", "Back Pain": "Orthopedics", "Body Pain": "Orthopedics",
            "Accident": "Orthopedics", "Swelling": "Orthopedics", "Skin Problem": "Dermatology",
            "Skin Rash": "Dermatology", "Allergy": "Dermatology", "Burn Injury": "Dermatology",
            "Eye Pain": "Ophthalmology", "Ear Pain": "ENT", "Sore Throat": "ENT", "Tooth Pain": "ENT",
            "Headache": "Neurology", "Dizziness": "Neurology", "Stomach Pain": "General Medicine",
            "Vomiting": "General Medicine", "Nausea": "General Medicine", "Diarrhea": "General Medicine",
            "Constipation": "General Medicine", "Diabetes": "General Medicine", "Fever": "General Medicine",
            "Cold": "General Medicine", "Cough": "General Medicine", "Breathing Difficulty": "General Medicine",
            "Weakness": "General Medicine", "Fatigue": "General Medicine", "Bleeding": "General Medicine",
        }
        recommended_department = next((department_by_symptom[item] for item in symptoms if item in department_by_symptom), None)
        if recommended_department:
            return next((doctor for doctor in self.doctors if doctor.get("department") == recommended_department), None)
        return self.doctors[0] if self.doctors else None

    def go_back(self) -> None:
        """Return to the prior intake step for this workflow."""
        from frontend.questionnaire import QuestionnaireScreen
        from frontend.symptoms import SymptomsScreen
        if self.app.draft and self.app.draft.flow_type == "emergency":
            self.app.show_screen(SymptomsScreen)
        else:
            self.app.show_screen(QuestionnaireScreen)

    def continue_visit(self) -> None:
        """Store the selected doctor in the current draft."""
        from frontend.sensor_screen import SensorScreen
        selected = self.table.selection()
        if not selected:
            messagebox.showerror("Doctor selection", "Select one doctor.", parent=self)
            return
        if self.app.draft is None:
            return
        doctor_id = int(selected[0])
        self.app.draft.doctor = next(doctor for doctor in self.doctors if doctor["doctor_id"] == doctor_id)
        self.app.show_screen(SensorScreen)

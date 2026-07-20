"""Symptom selection screen for HRS visits."""

from __future__ import annotations

from tkinter import BooleanVar, StringVar, messagebox, ttk
from typing import Any

from frontend.home import BaseScreen, HomeScreen


class SymptomsScreen(BaseScreen):
    """Allow a patient visit to contain one or more selected symptoms."""

    SYMPTOMS = (
        "Fever", "Headache", "Cold", "Cough", "Chest Pain", "Breathing Difficulty", "Body Pain",
        "Skin Problem", "Accident", "Sore Throat", "Joint Pain", "Back Pain", "Stomach Pain",
        "Vomiting", "Nausea", "Diarrhea", "Constipation", "Skin Rash", "Allergy", "Dizziness",
        "Weakness", "Fatigue", "Eye Pain", "Ear Pain", "Tooth Pain", "Burn Injury", "Bleeding",
        "Swelling", "High Blood Pressure", "Low Blood Pressure", "Diabetes", "Other",
    )

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Symptoms", "Select every symptom that applies to this visit.")
        self.selected = {symptom: BooleanVar() for symptom in self.SYMPTOMS}
        self.other_text = StringVar()
        content = self.add_scrollable_content()
        options = ttk.Frame(content, style="Card.TFrame", padding=22)
        options.pack(fill="x", padx=2, pady=(0, 8))
        ttk.Label(options, text="Select Symptoms", style="Section.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))
        for index, symptom in enumerate(self.SYMPTOMS):
            ttk.Checkbutton(options, text=symptom, variable=self.selected[symptom]).grid(
                row=(index // 4) + 1, column=index % 4, sticky="w", padx=(0, 22), pady=5
            )
        other = ttk.Frame(options, style="Card.TFrame")
        other.grid(row=10, column=0, columnspan=4, sticky="w", pady=(16, 0))
        ttk.Label(other, text="Other symptom details:", style="Card.TLabel").pack(side="left")
        ttk.Entry(other, textvariable=self.other_text, width=42).pack(side="left", padx=8)
        self.add_navigation(lambda: app.show_screen(HomeScreen), self.continue_visit, parent=content)

    def continue_visit(self) -> None:
        """Save selections to the draft and choose the next flow screen."""
        from frontend.doctor_selection import DoctorSelectionScreen
        from frontend.questionnaire import QuestionnaireScreen
        if self.app.draft is None:
            self.app.show_screen(HomeScreen)
            return
        symptoms = [name for name in self.SYMPTOMS if self.selected[name].get() and name != "Other"]
        if self.selected["Other"].get():
            detail = self.other_text.get().strip()
            symptoms.append(f"Other: {detail}" if detail else "Other")
        try:
            self.app.visit_service.set_symptoms(self.app.draft, symptoms)
        except ValueError as error:
            messagebox.showerror("Symptoms", str(error), parent=self)
            return
        if self.app.draft.flow_type == "emergency":
            self.app.show_screen(DoctorSelectionScreen)
        else:
            self.app.show_screen(QuestionnaireScreen)

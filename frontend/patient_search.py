"""Existing-patient search and visit-type selection screen."""

from __future__ import annotations

from tkinter import StringVar, messagebox, ttk
from typing import Any

from backend.patient import ValidationError
from frontend.home import BaseScreen, HomeScreen


class PatientSearchScreen(BaseScreen):
    """Search existing patients and display their previous visit history."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Existing Patient", "Search by Patient ID, Aadhaar, or phone number.")
        self.search_type = StringVar(value="Patient ID")
        self.search_value = StringVar()
        self.visit_type = StringVar(value="Check-up")
        self.selected_patient: dict | None = None

        search = ttk.Frame(self)
        search.pack(fill="x")
        ttk.Combobox(search, textvariable=self.search_type, values=("Patient ID", "Aadhaar", "Phone"),
                     state="readonly", width=16).pack(side="left")
        ttk.Entry(search, textvariable=self.search_value, width=36).pack(side="left", padx=8)
        ttk.Button(search, text="Search", command=self.search).pack(side="left")
        self.details = ttk.Label(self, text="Search for a patient to continue.", justify="left")
        self.details.pack(anchor="w", pady=(18, 8))
        ttk.Label(self, text="Previous Visit History").pack(anchor="w")
        self.history = ttk.Treeview(self, columns=("date", "symptoms"), show="headings", height=8)
        self.history.heading("date", text="Visit Date")
        self.history.heading("symptoms", text="Symptoms")
        self.history.column("date", width=220)
        self.history.column("symptoms", width=600)
        self.history.pack(fill="both", expand=True, pady=(4, 10))
        choice = ttk.Frame(self)
        choice.pack(anchor="w")
        ttk.Label(choice, text="Visit Type:").pack(side="left")
        ttk.Radiobutton(choice, text="Check-up", variable=self.visit_type, value="Check-up").pack(side="left", padx=8)
        ttk.Radiobutton(choice, text="New Problem", variable=self.visit_type, value="New Problem").pack(side="left")
        self.add_navigation(lambda: app.show_screen(HomeScreen), self.continue_visit)

    def search(self) -> None:
        """Perform the selected database search and render one matching patient."""
        try:
            matches = self.app.patient_service.find_existing(self.search_type.get(), self.search_value.get())
        except ValidationError as error:
            messagebox.showerror("Search", str(error), parent=self)
            return
        if not matches:
            self.selected_patient = None
            self.details.configure(text="No patient was found.")
            self.history.delete(*self.history.get_children())
            return
        self.selected_patient = matches[0]
        patient = self.selected_patient
        self.details.configure(text=(
            f"Patient ID: {patient['patient_id']}\nName: {patient['patient_name']}\n"
            f"Phone: {patient.get('patient_phone') or 'Not provided'}\nGender: {patient.get('gender') or 'Not provided'}"
        ))
        self.history.delete(*self.history.get_children())
        for visit in self.app.visit_service.begin_draft(patient, "existing").previous_history:
            self.history.insert("", "end", values=(visit["visit_date"], visit.get("symptoms") or "Not recorded"))

    def continue_visit(self) -> None:
        """Begin an existing-patient draft after a successful search."""
        from frontend.symptoms import SymptomsScreen
        if self.selected_patient is None:
            messagebox.showerror("Existing patient", "Search for and select a patient first.", parent=self)
            return
        self.app.begin_visit(self.selected_patient, "existing", self.visit_type.get())
        self.app.show_screen(SymptomsScreen)

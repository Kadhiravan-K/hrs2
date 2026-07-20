"""New-patient form for the HRS Tkinter application."""

from __future__ import annotations

from tkinter import StringVar, messagebox, ttk
from typing import Any

from tkcalendar import DateEntry

from backend.patient import ValidationError
from frontend.home import BaseScreen, HomeScreen


class PatientRegistrationScreen(BaseScreen):
    """Collect and validate all fields for a normal new patient."""

    FIELDS = (
        ("patient_name", "Patient Name"),
        ("patient_phone", "Patient Phone Number"),
        ("gender", "Gender"),
        ("date_of_birth", "Date of Birth"),
        ("patient_aadhaar", "Patient Aadhaar"),
        ("insurance_provider", "Insurance Provider"),
        ("insurance_number", "Insurance Number"),
        ("attender_name", "Attender Name"),
        ("attender_phone", "Attender Phone"),
        ("allergies", "Allergies"),
        ("unsuitable_medicines", "Medicines Not Suitable"),
    )

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("New Patient Registration", "Fields marked by validation are required.")
        self.values = {key: StringVar() for key, _ in self.FIELDS}
        form = self.add_card()
        ttk.Label(form, text="Patient Details", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))
        for row, (key, label) in enumerate(self.FIELDS):
            grid_row = row + 1
            ttk.Label(form, text=label, style="Card.TLabel").grid(row=grid_row, column=0, sticky="w", padx=(0, 24), pady=6)
            if key == "gender":
                field = ttk.Combobox(form, textvariable=self.values[key], values=("Male", "Female", "Other"), state="readonly")
            elif key == "date_of_birth":
                field = DateEntry(form, textvariable=self.values[key], date_pattern="y-mm-dd", width=39,
                                  background="#0B4F8A", foreground="#FFFFFF", borderwidth=1)
            else:
                field = ttk.Entry(form, textvariable=self.values[key], width=42)
            field.grid(row=grid_row, column=1, sticky="ew", pady=6)
        form.columnconfigure(1, weight=1)
        self.add_navigation(lambda: app.show_screen(HomeScreen), self.submit, "Continue")
        # Keyboard shortcuts: Enter to continue, Escape to go back
        self.bind_all("<Return>", lambda event: self.submit())
        self.bind_all("<Escape>", lambda event: app.show_screen(HomeScreen))

    def submit(self) -> None:
        """Create a patient before proceeding to symptom selection."""
        from frontend.symptoms import SymptomsScreen
        try:
            patient = self.app.patient_service.register_new({key: value.get() for key, value in self.values.items()})
        except ValidationError as error:
            messagebox.showerror("Patient validation", str(error), parent=self)
            return
        self.app.begin_visit(patient, "new")
        self.app.show_screen(SymptomsScreen)

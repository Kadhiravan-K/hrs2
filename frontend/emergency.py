"""Emergency registration screen for HRS."""

from __future__ import annotations

from tkinter import StringVar, messagebox, ttk
from typing import Any

from backend.patient import ValidationError
from frontend.home import BaseScreen, HomeScreen


class EmergencyScreen(BaseScreen):
    """Collect only the information needed to begin an emergency visit."""

    FIELDS = (
        ("patient_name", "Patient Name"),
        ("age", "Age"),
        ("gender", "Gender"),
        ("patient_phone", "Patient Phone"),
        ("attender_name", "Attender Name"),
        ("attender_phone", "Attender Phone"),
    )

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Emergency Registration", "Enter the minimum patient information.")
        self.values = {key: StringVar() for key, _ in self.FIELDS}
        form = ttk.Frame(self)
        form.pack(fill="x", expand=True)
        for row, (key, label) in enumerate(self.FIELDS):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=(0, 16), pady=5)
            if key == "gender":
                field = ttk.Combobox(form, textvariable=self.values[key], values=("Male", "Female", "Other"), state="readonly")
            else:
                field = ttk.Entry(form, textvariable=self.values[key], width=40)
            field.grid(row=row, column=1, sticky="ew", pady=5)
        form.columnconfigure(1, weight=1)
        self.add_navigation(lambda: app.show_screen(HomeScreen), self.submit, "Continue")

    def submit(self) -> None:
        """Create the emergency patient and skip directly to symptoms."""
        from frontend.symptoms import SymptomsScreen
        try:
            patient, age = self.app.patient_service.register_emergency(
                {key: value.get() for key, value in self.values.items()}
            )
        except ValidationError as error:
            messagebox.showerror("Emergency validation", str(error), parent=self)
            return
        self.app.begin_visit(patient, "emergency", emergency_age=age)
        self.app.show_screen(SymptomsScreen)

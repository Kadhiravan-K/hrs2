"""Five-question medical intake screen for non-emergency HRS visits."""

from __future__ import annotations

from tkinter import StringVar, messagebox, ttk
from typing import Any

from backend.visit import VisitService
from frontend.home import BaseScreen


class QuestionnaireScreen(BaseScreen):
    """Collect exactly the five agreed basic health questions."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Basic Questions", "Answer all five questions before selecting a doctor.")
        self.answers = {question: StringVar() for question in VisitService.QUESTION_LABELS}
        form = ttk.Frame(self)
        form.pack(fill="x", expand=True)
        for row, question in enumerate(VisitService.QUESTION_LABELS):
            ttk.Label(form, text=question).grid(row=row, column=0, sticky="w", padx=(0, 14), pady=7)
            if row == 0:
                field = ttk.Entry(form, textvariable=self.answers[question], width=35)
            else:
                field = ttk.Combobox(form, textvariable=self.answers[question], values=("Yes", "No"),
                                     state="readonly", width=32)
            field.grid(row=row, column=1, sticky="w", pady=7)
        self.add_navigation(self.go_back, self.continue_visit)

    def go_back(self) -> None:
        """Return to symptoms without changing the draft."""
        from frontend.symptoms import SymptomsScreen
        self.app.show_screen(SymptomsScreen)

    def continue_visit(self) -> None:
        """Persist question answers in the draft and move to doctor selection."""
        from frontend.doctor_selection import DoctorSelectionScreen
        if self.app.draft is None:
            return
        try:
            self.app.visit_service.set_questionnaire(
                self.app.draft, {question: value.get() for question, value in self.answers.items()}
            )
        except ValueError as error:
            messagebox.showerror("Basic Questions", str(error), parent=self)
            return
        self.app.show_screen(DoctorSelectionScreen)

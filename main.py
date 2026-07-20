"""Entry point and screen controller for the Health Registration System."""

from __future__ import annotations

import tkinter as tk
from typing import Type

from backend.doctor import DoctorService
from backend.patient import PatientService
from backend.report import ReportService
from backend.sensors import SensorManager
from backend.visit import VisitDraft, VisitService
from frontend.doctor_selection import DoctorSelectionScreen
from frontend.emergency import EmergencyScreen
from frontend.home import HomeScreen
from frontend.patient_registration import PatientRegistrationScreen
from frontend.patient_search import PatientSearchScreen
from frontend.questionnaire import QuestionnaireScreen
from frontend.report_preview import ReportPreviewScreen
from frontend.sensor_screen import SensorScreen
from frontend.splash import SplashScreen
from frontend.symptoms import SymptomsScreen


class HRSApplication(tk.Tk):
    """Coordinate HRS screens and keep a single visit draft in memory."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Health Registration System")
        self.geometry("1080x720")
        self.minsize(760, 520)
        self._configure_theme()
        self.patient_service = PatientService()
        self.doctor_service = DoctorService()
        self.visit_service = VisitService()
        self.sensor_manager = SensorManager()
        self.report_service = ReportService()
        self.draft: VisitDraft | None = None
        self._current_screen: tk.Frame | None = None
        self.show_screen(SplashScreen)
        self.after(1500, lambda: self.show_screen(HomeScreen))

    def _configure_theme(self) -> None:
        """Apply a softer, more modern healthcare-themed interface."""
        background = "#F5F7FB"
        surface = "#FFFFFF"
        surface_alt = "#F8FBFF"
        border = "#D9E6F2"
        navy = "#143B5A"
        blue = "#2563EB"
        blue_soft = "#EAF4FF"
        text = "#18324A"
        muted = "#6B7A90"
        self.configure(background=background)
        style = tk.ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=background, foreground=text, font=("Segoe UI", 10))
        style.configure("TFrame", background=background)
        style.configure("Card.TFrame", background=surface, relief="flat", borderwidth=1)
        style.configure("Hero.TFrame", background=surface, relief="flat", borderwidth=1)
        style.configure("Accent.TFrame", background=blue_soft, relief="flat", borderwidth=0)
        style.configure("TLabel", background=background, foreground=text, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=surface, foreground=text, font=("Segoe UI", 10))
        style.configure("Subtitle.TLabel", background=background, foreground=muted, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=surface, foreground=navy, font=("Segoe UI", 12, "bold"))
        style.configure("Hero.TLabel", background=surface, foreground=navy, font=("Segoe UI", 24, "bold"))
        style.configure("Muted.TLabel", background=surface, foreground=muted, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(16, 10), relief="flat")
        style.configure("Primary.TButton", background=blue, foreground="#FFFFFF", borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#1D4ED8"), ("disabled", "#A9BED0")], foreground=[("active", "#FFFFFF"), ("disabled", "#F8FAFC")])
        style.configure("Secondary.TButton", background="#ECF5FF", foreground=navy, borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#DCEBFF")], foreground=[("active", navy)])
        style.configure("Emergency.TButton", background="#DC2626", foreground="#FFFFFF", borderwidth=0)
        style.map("Emergency.TButton", background=[("active", "#B91C1C")], foreground=[("active", "#FFFFFF")])
        style.configure("TEntry", fieldbackground=surface, padding=8)
        style.configure("TCombobox", fieldbackground=surface, padding=7)
        style.configure("Treeview", background=surface, fieldbackground=surface, rowheight=32,
                        font=("Segoe UI", 10), foreground=text)
        style.configure("Treeview.Heading", background=navy, foreground="#FFFFFF", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#DDEDFD")], foreground=[("selected", navy)])

    def show_screen(self, screen_class: Type[tk.Frame]) -> None:
        """Replace the visible content frame with the requested screen."""
        if self._current_screen is not None:
            self._current_screen.destroy()
        self._current_screen = screen_class(self)
        self._current_screen.pack(fill="both", expand=True)

    def begin_visit(self, patient: dict, flow_type: str, visit_type: str | None = None,
                    emergency_age: int | None = None) -> None:
        """Create the in-memory draft for the selected patient workflow."""
        self.draft = self.visit_service.begin_draft(patient, flow_type, visit_type, emergency_age)

    def clear_draft(self) -> None:
        """Forget the current workflow after completion or cancellation."""
        self.draft = None

    def cancel_preview(self) -> None:
        """Remove saved preview records and return to the home screen."""
        if self.draft is not None:
            self.visit_service.cancel_preview_records(self.draft)
        self.clear_draft()
        self.show_screen(HomeScreen)


if __name__ == "__main__":
    HRSApplication().mainloop()

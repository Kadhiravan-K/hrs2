"""Sensor collection screen with real/demo source coloring."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from frontend.home import BaseScreen


class SensorScreen(BaseScreen):
    """Read values on demand and show blue real values or red demo values."""

    DISPLAY = (
        ("body_temperature", "Body Temperature", "°C"),
        ("heart_rate", "Heart Rate", "BPM"),
        ("room_temperature", "Room Temperature", "°C"),
        ("humidity", "Humidity", "%"),
    )

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Sensor Data Collection", "click the read sensor button") # Blue = real sensor value. Red = demo fallback value
        self.value_labels: dict[str, tk.Label] = {}
        self.header_labels: dict[str, tk.Label] = {}
        panel = ttk.Frame(self)
        panel.pack(anchor="w", pady=18)
        for row, (key, label, unit) in enumerate(self.DISPLAY):
            header = tk.Label(panel, text=f"{label}:", font=("Segoe UI", 14, "bold"), fg="black")
            header.grid(row=row, column=0, sticky="w", padx=(0, 16), pady=8)
            value = tk.Label(panel, text="Not read", font=("Segoe UI", 13), fg="black")
            value.grid(row=row, column=1, sticky="w", pady=8)
            self.value_labels[key] = value
            self.header_labels[key] = header
        style = ttk.Style(self)
        style.configure("Accent.TButton", background="#2563EB", foreground="#FFFFFF", padding=(14, 8))
        style.map("Accent.TButton", background=[("active", "#1D4ED8")], foreground=[("active", "#FFFFFF")])
        ttk.Button(self, text="Read Sensors", command=self.read_sensors, style="Accent.TButton").pack(anchor="w")
        self.add_navigation(self.go_back, self.continue_visit, "Continue to Preview")

    def read_sensors(self) -> None:
        """Collect values without allowing an unavailable hardware library to crash the UI."""
        readings = self.app.sensor_manager.collect_readings()
        if self.app.draft is not None:
            self.app.draft.sensor_readings = readings
        units = {key: unit for key, _, unit in self.DISPLAY}
        for key, reading in readings.items():
            source = reading.get("source", "demo")
            color = "blue" if source == "real" else "red"
            self.header_labels[key].configure(fg=color)
            # Do not display the literal 'demo' text in the red fallback UI.
            suffix = f" ({source.upper()})" if source == "real" else ""
            self.value_labels[key].configure(text=f"{reading['value']} {units[key]}{suffix}", fg=color)

    def go_back(self) -> None:
        """Return to doctor selection while retaining any prior readings in the draft."""
        from frontend.doctor_selection import DoctorSelectionScreen
        self.app.show_screen(DoctorSelectionScreen)

    def continue_visit(self) -> None:
        """Reserve the visit/token records needed for the report preview."""
        from frontend.report_preview import ReportPreviewScreen
        if self.app.draft is None:
            return
        try:
            self.app.visit_service.create_preview_records(self.app.draft)
        except (ValueError, RuntimeError) as error:
            messagebox.showerror("Sensor collection", str(error), parent=self)
            return
        self.app.show_screen(ReportPreviewScreen)

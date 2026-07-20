"""Sensor collection screen with real/demo source coloring."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from frontend.home import BaseScreen


class SensorScreen(BaseScreen):
    """Read values on demand and distinguish hardware values from fallback values."""

    DISPLAY = (
        ("body_temperature", "Body Temperature", "deg C"),
        ("heart_rate", "Heart Rate", "BPM"),
        ("room_temperature", "Room Temperature", "deg C"),
        ("humidity", "Humidity", "%"),
    )

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.title_label = self.add_title("Sensor Data Collection", "Click Read Sensors to collect the current values.")
        self.value_labels: dict[str, tk.Label] = {}
        self.header_labels: dict[str, tk.Label] = {}
        card = self.add_card()
        panel = ttk.Frame(card, style="Card.TFrame")
        panel.pack(anchor="w", pady=(0, 18))
        for row, (key, label, _) in enumerate(self.DISPLAY):
            header = tk.Label(panel, text=f"{label}:", font=("Segoe UI", 14, "bold"), fg="#18324A", bg="#FFFFFF")
            header.grid(row=row, column=0, sticky="w", padx=(0, 20), pady=10)
            value = tk.Label(panel, text="Not read", font=("Segoe UI", 13), fg="#18324A", bg="#FFFFFF")
            value.grid(row=row, column=1, sticky="w", pady=10)
            self.value_labels[key] = value
            self.header_labels[key] = header
        ttk.Button(card, text="Read Sensors", command=self.read_sensors, style="Primary.TButton").pack(anchor="w")
        self.add_navigation(self.go_back, self.continue_visit, "Continue to Preview")

    def read_sensors(self) -> None:
        """Collect readings without allowing unavailable hardware libraries to crash the UI."""
        readings = self.app.sensor_manager.collect_readings()
        if self.app.draft is not None:
            self.app.draft.sensor_readings = readings
        units = {key: unit for key, _, unit in self.DISPLAY}
        for key, reading in readings.items():
            source = reading.get("source", "demo")
            color = "#2563EB" if source == "real" else "#DC2626"
            self.header_labels[key].configure(fg=color)
            suffix = " (REAL)" if source == "real" else ""
            self.value_labels[key].configure(text=f"{reading['value']} {units[key]}{suffix}", fg=color)
        # Blue title means every reading is real; red means one or more values are demo/fallback.
        title_color = "#2563EB" if all(item.get("source") == "real" for item in readings.values()) else "#DC2626"
        self.title_label.configure(foreground=title_color)

    def go_back(self) -> None:
        """Return to doctor selection while retaining prior readings in the draft."""
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

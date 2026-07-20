"""Shared Tkinter screen helpers and the HRS home screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any


class BaseScreen(ttk.Frame):
    """Base frame with small shared layout helpers for all HRS screens."""

    def __init__(self, app: Any) -> None:
        super().__init__(app, padding=24)
        self.app = app

    def add_title(self, title: str, subtitle: str = "") -> ttk.Label:
        """Add a modern hero-style screen heading."""
        hero = ttk.Frame(self, style="Hero.TFrame", padding=20)
        hero.pack(fill="x", pady=(0, 16))
        title_label = ttk.Label(hero, text=title, style="Hero.TLabel")
        title_label.pack(anchor="w")
        if subtitle:
            ttk.Label(hero, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(6, 0))
        accent = ttk.Frame(hero, style="Accent.TFrame", height=4)
        accent.pack(fill="x", pady=(12, 0))
        accent.configure(height=4)
        return title_label

    def add_card(self) -> ttk.Frame:
        """Create a modern content card with calmer spacing."""
        card = ttk.Frame(self, style="Card.TFrame", padding=22)
        card.pack(fill="both", expand=True)
        return card

    def add_scrollable_content(self) -> ttk.Frame:
        """Return a mouse-wheel scrollable area for long responsive screens."""
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, background="#F5F7FB", highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        content = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def update_scroll_region(_: Any) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def update_width(event: Any) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def on_mouse_wheel(event: Any) -> None:
            canvas.yview_scroll(int(-event.delta / 120), "units")

        def remove_mouse_wheel(event: Any) -> None:
            if event.widget is outer:
                canvas.unbind_all("<MouseWheel>")

        content.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_width)
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        outer.bind("<Destroy>", remove_mouse_wheel, add="+")
        return content

    def add_navigation(self, back_command: Any, next_command: Any, next_text: str = "Continue",
                       parent: ttk.Frame | None = None) -> ttk.Button:
        """Add standard Back and Continue buttons with a cleaner layout."""
        row = ttk.Frame(parent or self)
        row.pack(fill="x", pady=(20, 8))
        ttk.Button(row, text="Back", command=back_command, style="Secondary.TButton").pack(side="left")
        next_button = ttk.Button(row, text=next_text, command=next_command, style="Primary.TButton")
        next_button.pack(side="right")
        return next_button


class HomeScreen(BaseScreen):
    """Provide the three starting patient workflows."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.add_title("Health Registration System", "Patient registration and basic health measurement kiosk.")
        from frontend.emergency import EmergencyScreen
        from frontend.patient_registration import PatientRegistrationScreen
        from frontend.patient_search import PatientSearchScreen

        card = self.add_card()
        ttk.Label(card, text="Choose a Registration Path", style="Section.TLabel").pack(anchor="w")
        ttk.Label(card, text="Start a new registration or continue with an existing record.", style="Card.TLabel").pack(anchor="w", pady=(5, 18))

        options = [
            ("Existing Patient", "Continue a visit for a known patient.", "Primary.TButton", "#EAF4FF", lambda: app.show_screen(PatientSearchScreen)),
            ("New Patient", "Register a fresh patient and begin intake.", "Primary.TButton", "#F7FAFF", lambda: app.show_screen(PatientRegistrationScreen)),
            ("Emergency", "Start the urgent care flow immediately.", "Emergency.TButton", "#FFF1F1", lambda: app.show_screen(EmergencyScreen)),
        ]

        row = ttk.Frame(card)
        row.pack(fill="x", pady=(6, 0))
        for title, subtitle, style_name, accent, command in options:
            option_card = ttk.Frame(row, style="Card.TFrame", padding=16)
            option_card.pack(side="left", fill="both", expand=True, padx=6)
            option_card.configure(style="Card.TFrame")
            if title == "Emergency":
                option_card.configure(style="Card.TFrame")
            ttk.Label(option_card, text=title, font=("Segoe UI", 11, "bold"), foreground="#143B5A").pack(anchor="w")
            ttk.Label(option_card, text=subtitle, style="Subtitle.TLabel", wraplength=220).pack(anchor="w", pady=(4, 10))
            button = ttk.Button(option_card, text="Open", width=16, style=style_name, command=command)
            button.pack(anchor="w", pady=(4, 0))

        ttk.Label(card, text="Fast, offline-ready, and built for quick patient intake.", style="Subtitle.TLabel").pack(anchor="w", pady=(16, 0))

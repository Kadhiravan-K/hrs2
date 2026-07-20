"""Short startup splash screen for HRS."""

from __future__ import annotations

from typing import Any

from frontend.home import BaseScreen


class SplashScreen(BaseScreen):
    """Display a simple non-animated splash while the application starts."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        container = self
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        from tkinter import ttk

        hero = ttk.Frame(container, style="Hero.TFrame", padding=28)
        hero.grid(row=0, column=0, sticky="nsew")
        hero.columnconfigure(0, weight=1)
        ttk.Label(hero, text="Health Registration System", style="Hero.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(hero, text="Offline patient registration kiosk", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 12))
        accent = ttk.Frame(hero, style="Accent.TFrame", height=4)
        accent.grid(row=2, column=0, sticky="ew")
        accent.configure(height=4)
        ttk.Label(hero, text="Modern intake experience for fast, secure check-in.", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=(14, 0))

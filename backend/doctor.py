"""Doctor selection operations for HRS."""

from __future__ import annotations

from typing import Any

from database import queries

Record = dict[str, Any]


class DoctorService:
    """Expose active doctors for appointment selection."""

    @staticmethod
    def _is_placeholder_doctor(doctor: Record) -> bool:
        """Identify sample or test doctors that should not be shown to users."""
        name = str(doctor.get("doctor_name") or "").casefold()
        department = str(doctor.get("department") or "").casefold()
        markers = ("test", "sample", "demo")
        return any(marker in name or marker in department for marker in markers)

    def get_active_doctors(self) -> list[Record]:
        """Return active doctors only, excluding obvious placeholder records."""
        return [
            doctor for doctor in queries.get_all_doctors()
            if str(doctor.get("status") or "").casefold() == "active"
            and not self._is_placeholder_doctor(doctor)
        ]

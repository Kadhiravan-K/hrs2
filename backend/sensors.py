"""Hardware-safe sensor collection with Windows-compatible demo fallback."""

from __future__ import annotations

import random
from typing import Any


class SensorManager:
    """Read available I2C sensors without importing Pi libraries on Windows startup."""

    @staticmethod
    def _demo_readings() -> dict[str, dict[str, float | str]]:
        """Return realistic non-clinical fallback values for development."""
        return {
            "body_temperature": {"value": round(random.uniform(36.2, 37.5), 1), "source": "demo"},
            "heart_rate": {"value": round(random.uniform(60, 100)), "source": "demo"},
            "room_temperature": {"value": round(random.uniform(22.0, 30.0), 1), "source": "demo"},
            "humidity": {"value": round(random.uniform(35.0, 65.0), 1), "source": "demo"},
        }

    def collect_readings(self) -> dict[str, dict[str, float | str]]:
        """Read MLX90614/BME280 where possible and demo-fallback every unavailable value."""
        readings = self._demo_readings()
        try:
            import board  # type: ignore[import-not-found]
            import busio  # type: ignore[import-not-found]
            import adafruit_bme280  # type: ignore[import-not-found]
            import adafruit_mlx90614  # type: ignore[import-not-found]

            i2c = busio.I2C(board.SCL, board.SDA)
            try:
                mlx = adafruit_mlx90614.MLX90614(i2c)
                readings["body_temperature"] = {
                    "value": round(float(mlx.object_temperature), 1), "source": "real"
                }
            except Exception:
                pass
            try:
                bme = adafruit_bme280.Adafruit_BME280_I2C(i2c)
                readings["room_temperature"] = {"value": round(float(bme.temperature), 1), "source": "real"}
                readings["humidity"] = {"value": round(float(bme.humidity), 1), "source": "real"}
            except Exception:
                pass
        except Exception:
            pass
        # KY-039 is analog and cannot be read directly by Raspberry Pi without an ADC.
        return readings

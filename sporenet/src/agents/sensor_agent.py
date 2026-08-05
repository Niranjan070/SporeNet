"""
SporeNet Sensor Agent
Responsible for ingesting and validating continuous microclimate stream telemetry from Raspberry Pi edge nodes.
"""

from typing import Dict, Any

class SensorAgent:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validates incoming weather telemetry data."""
        telemetry = state.get("telemetry", {})
        
        temp = telemetry.get("temperature", 25.0)
        rh = telemetry.get("relative_humidity", 85.0)
        rain = telemetry.get("rainfall_mm", 0.0)
        wet_hrs = telemetry.get("leaf_wetness_hours", 8.0)

        # Basic range sanitization
        temp_valid = -10.0 <= float(temp) <= 60.0
        rh_valid = 0.0 <= float(rh) <= 100.0
        rain_valid = float(rain) >= 0.0
        wet_valid = 0.0 <= float(wet_hrs) <= 168.0

        is_valid = temp_valid and rh_valid and rain_valid and wet_valid
        
        telemetry_clean = {
            "temperature": float(temp),
            "relative_humidity": float(rh),
            "rainfall_mm": max(0.0, float(rain)),
            "leaf_wetness_hours": max(0.0, float(wet_hrs))
        }

        return {
            **state,
            "sensor_status": "valid" if is_valid else "sanitized",
            "telemetry_clean": telemetry_clean
        }


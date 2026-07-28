"""
SporeNet Raspberry Pi Telemetry Logger
Simulates continuous 5-15 minute environmental sensor logging (Temp, RH, Wind, Rain) on edge devices.
"""

import time
from datetime import datetime
from typing import Dict, Any

class PiSensorLogger:
    def __init__(self, field_id: str = "F01", trap_id: str = "TRAP-A"):
        self.field_id = field_id
        self.trap_id = trap_id

    def read_sensors(self) -> Dict[str, Any]:
        """Reads physical GPIO / I2C environmental sensors or returns mock readings."""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "field_id": self.field_id,
            "trap_id": self.trap_id,
            "temp_c": 26.5,
            "humidity_pct": 82.0,
            "wind_kmh": 10.5,
            "rainfall_mm": 0.0,
        }

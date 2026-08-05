"""
SporeNet Raspberry Pi Telemetry Logger
Simulates continuous 5-15 minute environmental sensor logging (Temp, RH, Wind, Rain) on edge devices.
"""

import time
from datetime import datetime
from typing import Dict, Any

import time
import argparse
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

class PiSensorLogger:
    def __init__(self, field_id: str = "F01", trap_id: str = "TRAP-A", csv_path: Path = None):
        self.field_id = field_id
        self.trap_id = trap_id
        self.csv_path = csv_path or (REPO_ROOT / "data" / "synthetic" / "weather_stream.csv")

    def read_sensors(self) -> Dict[str, Any]:
        """Reads physical GPIO / I2C environmental sensors or returns mock readings."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Simulate realistic diurnal microclimate fluctuations
        temp_c = round(random.uniform(22.0, 32.0), 2)
        humidity_pct = round(random.uniform(70.0, 98.0), 2)
        wind_kmh = round(random.uniform(2.0, 18.0), 2)
        rainfall_mm = round(random.choice([0.0, 0.0, 0.0, 1.2, 4.5, 12.0]), 2)
        leaf_wetness_hours = round(random.uniform(4.0, 24.0), 1)

        return {
            "timestamp": now_str,
            "field_id": self.field_id,
            "trap_id": self.trap_id,
            "temp_c": temp_c,
            "humidity_pct": humidity_pct,
            "wind_kmh": wind_kmh,
            "rainfall_mm": rainfall_mm,
        }


    def log_reading(self) -> Dict[str, Any]:

        """Reads sensor values and appends to the target CSV dataset."""
        reading = self.read_sensors()
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        df_row = pd.DataFrame([reading])
        if self.csv_path.exists():
            df_row.to_csv(self.csv_path, mode="a", header=False, index=False)
        else:
            df_row.to_csv(self.csv_path, mode="w", header=True, index=False)
            
        return reading

def main():
    parser = argparse.ArgumentParser(description="SporeNet Edge Raspberry Pi Sensor Telemetry Logger")
    parser.add_argument("--field-id", type=str, default="F01", help="Field location ID")
    parser.add_argument("--trap-id", type=str, default="TRAP-A", help="Air trap hardware ID")
    parser.add_argument("--once", action="store_true", help="Log a single sensor reading and exit")
    parser.add_argument("--interval", type=int, default=15, help="Logging interval in seconds (default: 15)")
    args = parser.parse_args()

    logger = PiSensorLogger(field_id=args.field_id, trap_id=args.trap_id)

    if args.once:
        reading = logger.log_reading()
        print(f"[OK] Logged edge sensor reading to {logger.csv_path.name}: {reading}")
    else:
        print(f"[INFO] Starting continuous Pi sensor logger (Interval: {args.interval}s, Field: {args.field_id})...")
        try:
            while True:
                reading = logger.log_reading()
                print(f"[{reading['timestamp']}] Logged: Temp={reading['temperature']}°C, RH={reading['relative_humidity']}%, WetHrs={reading['leaf_wetness_hours']}h")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n[INFO] Sensor logger stopped by user.")

if __name__ == "__main__":
    main()


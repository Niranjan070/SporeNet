import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest
import pandas as pd
from src.edge.pi_logger import PiSensorLogger

def test_pi_sensor_logger_readings():
    logger = PiSensorLogger(field_id="F02", trap_id="TRAP-B")
    reading = logger.read_sensors()

    assert reading["field_id"] == "F02"
    assert reading["trap_id"] == "TRAP-B"
    assert "temp_c" in reading
    assert "humidity_pct" in reading
    assert "wind_kmh" in reading


def test_pi_sensor_logger_csv_append(tmp_path):
    target_csv = tmp_path / "test_stream.csv"
    logger = PiSensorLogger(field_id="F01", trap_id="TRAP-A", csv_path=target_csv)

    reading1 = logger.log_reading()
    assert target_csv.exists()
    df1 = pd.read_csv(target_csv)
    assert len(df1) == 1

    reading2 = logger.log_reading()
    df2 = pd.read_csv(target_csv)
    assert len(df2) == 2

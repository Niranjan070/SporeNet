import sys
from pathlib import Path

# Add project root to python path for imports
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest
import pandas as pd
import math
from scripts.temporal_alignment import (
    calculate_shannon_entropy,
    derive_proxy_risk_label,
    run_temporal_alignment
)

def test_calculate_shannon_entropy():
    # Equal distribution of 2 classes: p=0.5 -> entropy = -2*(0.5 * ln(0.5)) = ln(2) = 0.6931
    counts = [10, 10, 0, 0, 0, 0, 0, 0, 0]
    entropy = calculate_shannon_entropy(counts)
    assert abs(entropy - math.log(2)) < 0.001

def test_proxy_veto_rule():
    # Dry forecast vetoes high burden: weighted_burden=60, blast_days=0, wet_hours=0 -> Low
    assert derive_proxy_risk_label(60, 0, 0) == "Low"
    # No inoculum vetoes perfect weather: weighted_burden=0, blast_days=7, wet_hours=100 -> Low
    assert derive_proxy_risk_label(0, 7, 100) == "Low"
    # High burden + High weather -> Critical: weighted_burden=30, blast_days=3, wet_hours=40 -> Critical
    assert derive_proxy_risk_label(30, 3, 40) == "Critical"

def test_join_key_invariant(tmp_path):
    """
    Assert that the temporal join matches on [exposure_start, exposure_end] only,
    ignoring lab_capture_date completely, and that lab_capture_date never appears in join logic.
    """
    # Create weather frame spanning 2 different regimes
    # Regime A: Exposure window [2026-01-01 to 2026-01-07] -> constant 20.0 C
    # Regime B: Lab date window [2026-01-08 to 2026-01-10] -> constant 40.0 C
    dates_exp = pd.date_range("2026-01-01 00:00:00", "2026-01-07 23:00:00", freq="1h")
    dates_lab = pd.date_range("2026-01-08 00:00:00", "2026-01-10 23:00:00", freq="1h")

    weather_rows = []
    for dt in dates_exp:
        weather_rows.append({
            "timestamp": dt, "field_id": "F01", "trap_id": "TRAP-A",
            "temp_c": 20.0, "humidity_pct": 85.0, "wind_kmh": 5.0, "rainfall_mm": 0.0
        })
    for dt in dates_lab:
        weather_rows.append({
            "timestamp": dt, "field_id": "F01", "trap_id": "TRAP-A",
            "temp_c": 40.0, "humidity_pct": 30.0, "wind_kmh": 10.0, "rainfall_mm": 0.0
        })
    weather_df = pd.DataFrame(weather_rows)
    weather_csv = tmp_path / "weather_invariant.csv"
    weather_df.to_csv(weather_csv, index=False)

    # Sample with exposure_start/end in Regime A and lab_capture_date in Regime B
    sample_df = pd.DataFrame([{
        "sample_id": "SMP-TEST-001",
        "field_id": "F01",
        "trap_id": "TRAP-A",
        "exposure_start": "2026-01-01 00:00:00",
        "exposure_end": "2026-01-07 23:00:00",
        "image_path": "data/raw/images/SMP-TEST-001.tif",
        "spore_magnaporthe_oryzae": 30,
        "spore_alternaria": 0, "spore_bipolaris": 0, "spore_curvularia": 0,
        "spore_curvularia_eragrostidis": 0, "spore_exserohilum": 0,
        "spore_fusarium": 0, "spore_fusarium_microconidie": 0, "spore_mycelium": 0,
        "lab_capture_date": "2026-01-09",
        "officer_id": "OFC-TEST"
    }])
    samples_csv = tmp_path / "samples_invariant.csv"
    sample_df.to_csv(samples_csv, index=False)

    output_csv = tmp_path / "aligned_output.csv"
    df = run_temporal_alignment(samples_csv, weather_csv, output_csv)

    # Assert look-back mean temp equals 20.0 (Regime A) and NOT 40.0 (Regime B)
    assert df.iloc[0]["lb_mean_temp"] == 20.0
    # Assert lab_capture_date does not appear as a join key in the output features
    assert "lab_capture_date" not in df.columns

def test_run_temporal_alignment_pipeline(tmp_path):
    repo_root = Path(__file__).resolve().parent.parent
    samples_csv = repo_root / "data" / "synthetic" / "samples.csv"
    weather_csv = repo_root / "data" / "synthetic" / "weather_stream.csv"
    output_csv = tmp_path / "aligned_features.csv"
    
    if samples_csv.exists() and weather_csv.exists():
        df = run_temporal_alignment(samples_csv, weather_csv, output_csv)
        assert output_csv.exists()
        samples_df = pd.read_csv(samples_csv)
        assert len(df) == len(samples_df)

        assert "sample_id" in df.columns
        assert "proxy_risk_label" in df.columns

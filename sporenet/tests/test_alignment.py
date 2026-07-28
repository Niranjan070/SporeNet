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

def test_derive_proxy_risk_label():
    label_low = derive_proxy_risk_label(weighted_score=10.0, blast_days=0, wet_hours=10.0)
    assert label_low == "Low"
    
    label_critical = derive_proxy_risk_label(weighted_score=80.0, blast_days=5, wet_hours=100.0)
    assert label_critical in ["High", "Critical"]

def test_run_temporal_alignment_pipeline(tmp_path):
    repo_root = Path(__file__).resolve().parent.parent
    samples_csv = repo_root / "data" / "synthetic" / "samples.csv"
    weather_csv = repo_root / "data" / "synthetic" / "weather_stream.csv"
    output_csv = tmp_path / "aligned_features.csv"
    
    if samples_csv.exists() and weather_csv.exists():
        df = run_temporal_alignment(samples_csv, weather_csv, output_csv)
        assert output_csv.exists()
        assert len(df) == 12
        assert "sample_id" in df.columns
        assert "proxy_risk_label" in df.columns

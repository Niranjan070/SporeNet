#!/usr/bin/env python3
"""
SporeNet Temporal Alignment Engine
Joins weekly spore trap sample metadata with continuous 24/7 microclimate sensor telemetry.

CRITICAL TEMPORAL JOIN RULE:
The temporal join key is ALWAYS exposure_start and exposure_end from the samples table.
NEVER use lab_capture_date or image file timestamps for joining weather.
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import yaml

# Pathogenicity weights for proxy risk score derivation
DEFAULT_SPECIES_WEIGHTS = {
    "spore_magnaporthe_oryzae": 1.00,       # Primary Target (Rice Blast anchor)
    "spore_alternaria": 0.00,               # Background class
    "spore_bipolaris": 0.00,                # Background class
    "spore_curvularia": 0.00,               # Background class
    "spore_curvularia_eragrostidis": 0.00,  # Background class
    "spore_exserohilum": 0.00,              # Background class
    "spore_fusarium": 0.00,                 # Background class
    "spore_fusarium_microconidie": 0.00,    # Background class
    "spore_mycelium": 0.00,                 # Background class
}

SPORE_COLUMNS = [
    "spore_magnaporthe_oryzae",
    "spore_alternaria",
    "spore_bipolaris",
    "spore_curvularia",
    "spore_curvularia_eragrostidis",
    "spore_exserohilum",
    "spore_fusarium",
    "spore_fusarium_microconidie",
    "spore_mycelium",
]

def calculate_shannon_entropy(counts: list[int]) -> float:
    """Calculates Shannon entropy (diversity index) for a vector of spore counts."""
    total = sum(counts)
    if total == 0:
        return 0.0
    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            entropy -= p * math.log(p)
    return round(entropy, 4)

def derive_proxy_risk_label(primary_spore_count: float, lf_fc_blast_risk_days: int, lf_fc_wet_hours: float) -> str:
    """
    Two-factor rule with veto power.
    Inoculum bucket (primary_spore_count, class 0):
      - High: >= 20
      - Medium: 5 - 19
      - Low: < 5
    Weather bucket (look-forward forecast):
      - High: lf_fc_blast_risk_days >= 3 AND lf_fc_wet_hours >= 36
      - Medium: lf_fc_blast_risk_days >= 1 OR lf_fc_wet_hours >= 24
      - Low: otherwise
    VETO: If inoculum IS Low -> Risk IS Low (no spores = no infection).
          If weather IS Low -> Risk IS Low (dry/hostile weather = no infection).
    Rule matrix when neither is Low:
      - Inoculum High + Weather High -> "Critical"
      - Inoculum High + Weather Medium -> "High"
      - Inoculum Medium + Weather High -> "High"
      - Inoculum Medium + Weather Medium -> "Medium"
    Returns string: "Low", "Medium", "High", "Critical"
    """
    if primary_spore_count >= 20:
        ino_bucket = "High"
    elif primary_spore_count >= 5:
        ino_bucket = "Medium"
    else:
        ino_bucket = "Low"

    if lf_fc_blast_risk_days >= 3 and lf_fc_wet_hours >= 36:
        wx_bucket = "High"
    elif lf_fc_blast_risk_days >= 1 or lf_fc_wet_hours >= 24:
        wx_bucket = "Medium"
    else:
        wx_bucket = "Low"

    if ino_bucket == "Low" or wx_bucket == "Low":
        return "Low"
    if ino_bucket == "High" and wx_bucket == "High":
        return "Critical"
    if ino_bucket == "High" or wx_bucket == "High":
        return "High"
    return "Medium"

def run_temporal_alignment(
    samples_path: Path,
    weather_path: Path,
    output_path: Path,
    weights_path: Path = None,
    decay_k: float = 0.3
) -> pd.DataFrame:
    """
    Main temporal alignment function.
    Reads samples and continuous weather streams, computes look-back and look-forward aggregates,
    applies inoculum decay dynamics, computes Shannon entropy, and outputs aligned feature set.
    """

    print("=" * 60)
    print("      SporeNet Temporal Alignment & Feature Fusion Engine")
    print("=" * 60)

    # 1. Load Data
    if not samples_path.exists():
        raise FileNotFoundError(f"Samples file not found at: {samples_path}")
    if not weather_path.exists():
        raise FileNotFoundError(f"Weather file not found at: {weather_path}")

    samples_df = pd.read_csv(samples_path)
    weather_df = pd.read_csv(weather_path)

    # Parse timestamps
    samples_df["exposure_start"] = pd.to_datetime(samples_df["exposure_start"])
    samples_df["exposure_end"] = pd.to_datetime(samples_df["exposure_end"])
    weather_df["timestamp"] = pd.to_datetime(weather_df["timestamp"])

    # Sort weather data chronologically
    weather_df = weather_df.sort_values("timestamp").reset_index(drop=True)
    samples_df = samples_df.sort_values("exposure_end").reset_index(drop=True)

    # Load pathogenicity weights if available
    weights = DEFAULT_SPECIES_WEIGHTS.copy()
    if weights_path and weights_path.exists():
        with open(weights_path, "r") as f:
            yaml_weights = yaml.safe_load(f).get("species_weights", {})
            for k, v in yaml_weights.items():
                col_name = f"spore_{k}" if not k.startswith("spore_") else k
                if col_name in weights:
                    weights[col_name] = float(v)

    aligned_rows = []
    inoculum_state = 0.0  # Initial inoculum state at t=0

    # 2. Iterate through each slide sample
    for idx, row in samples_df.iterrows():
        sample_id = row["sample_id"]
        field_id = row["field_id"]
        exp_start = row["exposure_start"]
        exp_end = row["exposure_end"]

        # Save previous inoculum state for feature column
        inoculum_state_prev = round(inoculum_state, 2)

        # -------------------------------------------------------------
        # LOOK-BACK WINDOW: [exposure_start, exposure_end]
        # -------------------------------------------------------------
        lb_weather = weather_df[
            (weather_df["timestamp"] >= exp_start) & 
            (weather_df["timestamp"] <= exp_end)
        ]

        if len(lb_weather) > 0:
            lb_mean_temp = round(float(lb_weather["temp_c"].mean()), 2)
            lb_mean_humidity = round(float(lb_weather["humidity_pct"].mean()), 2)
            # Wet hours: count of 10-minute intervals with RH > 80%
            lb_wet_hours = round(float((lb_weather["humidity_pct"] > 80.0).sum() * (10.0 / 60.0)), 2)
            lb_rain_sum = round(float(lb_weather["rainfall_mm"].sum()), 2)

            # Blast risk days: days where temp is 24-28°C AND RH > 90% for >= 4 hours (24 slots)
            lb_weather_copy = lb_weather.copy()
            lb_weather_copy["is_blast_favorable"] = (
                (lb_weather_copy["temp_c"] >= 24.0) & 
                (lb_weather_copy["temp_c"] <= 28.0) & 
                (lb_weather_copy["humidity_pct"] >= 90.0)
            )
            daily_blast = lb_weather_copy.groupby(lb_weather_copy["timestamp"].dt.date)["is_blast_favorable"].sum()
            lb_blast_risk_days = int((daily_blast >= 24).sum())  # >= 4 hours in a day
        else:
            lb_mean_temp = 25.0
            lb_mean_humidity = 80.0
            lb_wet_hours = 0.0
            lb_rain_sum = 0.0
            lb_blast_risk_days = 0

        # -------------------------------------------------------------
        # LOOK-FORWARD WINDOW: [exposure_end, exposure_end + 7 days]
        # -------------------------------------------------------------
        lf_start = exp_end
        lf_end = exp_end + pd.Timedelta(days=7)
        lf_weather = weather_df[
            (weather_df["timestamp"] > lf_start) & 
            (weather_df["timestamp"] <= lf_end)
        ]

        if len(lf_weather) > 0:
            lf_fc_wet_hours = round(float((lf_weather["humidity_pct"] > 80.0).sum() * (10.0 / 60.0)), 2)
            lf_fc_rain_prob = round(float((lf_weather["rainfall_mm"] > 0.0).mean()), 4)

            lf_weather_copy = lf_weather.copy()
            lf_weather_copy["is_blast_favorable"] = (
                (lf_weather_copy["temp_c"] >= 24.0) & 
                (lf_weather_copy["temp_c"] <= 28.0) & 
                (lf_weather_copy["humidity_pct"] >= 90.0)
            )
            daily_blast_lf = lf_weather_copy.groupby(lf_weather_copy["timestamp"].dt.date)["is_blast_favorable"].sum()
            lf_fc_blast_risk_days = int((daily_blast_lf >= 24).sum())
        else:
            lf_fc_wet_hours = lb_wet_hours
            lf_fc_rain_prob = 0.20
            lf_fc_blast_risk_days = lb_blast_risk_days

        # -------------------------------------------------------------
        # SPORE COUNTS, DIVERSITY & INOCULUM DECAY
        # -------------------------------------------------------------
        counts_vector = [int(row[col]) for col in SPORE_COLUMNS]
        total_spores = sum(counts_vector)
        diversity_index = calculate_shannon_entropy(counts_vector)

        # Update inoculum state for next week using exponential decay:
        # state_t = state_{t-1} * exp(-k) + current_primary_spores
        primary_spore_count = int(row["spore_magnaporthe_oryzae"])
        inoculum_state = (inoculum_state * math.exp(-decay_k)) + primary_spore_count

        # Compute proxy risk label using primary inoculum (class 0) and look-forward weather forecast
        proxy_risk_label = derive_proxy_risk_label(primary_spore_count, lf_fc_blast_risk_days, lf_fc_wet_hours)

        aligned_row = {
            "sample_id": sample_id,
            "field_id": field_id,
            "exposure_start": exp_start.strftime("%Y-%m-%d %H:%M:%S"),
            "exposure_end": exp_end.strftime("%Y-%m-%d %H:%M:%S"),
            "spore_magnaporthe_oryzae": counts_vector[0],
            "spore_alternaria": counts_vector[1],
            "spore_bipolaris": counts_vector[2],
            "spore_curvularia": counts_vector[3],
            "spore_curvularia_eragrostidis": counts_vector[4],
            "spore_exserohilum": counts_vector[5],
            "spore_fusarium": counts_vector[6],
            "spore_fusarium_microconidie": counts_vector[7],
            "spore_mycelium": counts_vector[8],
            "total_spores": total_spores,
            "diversity_index": diversity_index,
            "lb_mean_temp": lb_mean_temp,
            "lb_mean_humidity": lb_mean_humidity,
            "lb_wet_hours": lb_wet_hours,
            "lb_rain_sum": lb_rain_sum,
            "lb_blast_risk_days": lb_blast_risk_days,
            "lf_fc_wet_hours": lf_fc_wet_hours,
            "lf_fc_rain_prob": lf_fc_rain_prob,
            "lf_fc_blast_risk_days": lf_fc_blast_risk_days,
            "inoculum_state_prev": inoculum_state_prev,
            "proxy_risk_label": proxy_risk_label,
        }
        aligned_rows.append(aligned_row)

    out_df = pd.DataFrame(aligned_rows)

    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # Save to processed directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)

    print(f"\n[OK] Temporal Alignment Complete!")
    print(f"   Output Dataset: {output_path}")
    print(f"   Aligned Feature Shape: {out_df.shape}")
    print("\nFirst Aligned Feature Row:")
    for col, val in out_df.iloc[0].items():
        print(f"   - {col:<30}: {val}")

    return out_df

def main():
    repo_root = Path(__file__).resolve().parent.parent
    samples_csv = repo_root / "data" / "synthetic" / "samples.csv"
    weather_csv = repo_root / "data" / "synthetic" / "weather_stream.csv"
    weights_yaml = repo_root / "configs" / "species_weights.yaml"
    output_csv = repo_root / "data" / "processed" / "aligned_features.csv"

    run_temporal_alignment(samples_csv, weather_csv, output_csv, weights_yaml)

if __name__ == "__main__":
    main()

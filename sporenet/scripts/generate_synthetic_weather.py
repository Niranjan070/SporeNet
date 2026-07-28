#!/usr/bin/env python3
"""
Synthetic Weather Generator for SporeNet
Generates 90 days of continuous 10-minute microclimate sensor readings for Raspberry Pi edge logging simulation.
"""

from pathlib import Path
import numpy as np
import pandas as pd

def generate_synthetic_weather(
    output_path: Path,
    days: int = 90,
    field_id: str = "F01",
    trap_id: str = "TRAP-A",
    start_date: str = "2026-05-01 00:00:00",
    seed: int = 42
):
    np.random.seed(seed)
    
    # 10-minute intervals for 90 days
    periods = days * 24 * 6  # 6 readings per hour
    timestamps = pd.date_range(start=start_date, periods=periods, freq="10min")
    
    # Time vector in hours from start
    hours = np.linspace(0, days * 24, periods)
    
    # Diurnal temperature cycle: peaks at 14:00 (2pm), lowest at 04:00 (4am)
    # Base temp around 27°C, varying between 22°C and 32°C
    diurnal_temp = 27.0 + 4.5 * np.sin(2 * np.pi * (hours - 8.0) / 24.0)
    temp_noise = np.random.normal(0, 0.8, size=periods)
    temp_c = np.clip(diurnal_temp + temp_noise, 20.0, 35.0)
    
    # Diurnal humidity cycle: inverse to temp (highest at night 90-95%, lowest during day 60-70%)
    diurnal_rh = 78.0 - 15.0 * np.sin(2 * np.pi * (hours - 8.0) / 24.0)
    rh_noise = np.random.normal(0, 2.5, size=periods)
    humidity_pct = np.clip(diurnal_rh + rh_noise, 50.0, 98.0)
    
    # Wind speed: 0 to 25 km/h with random gusts
    wind_base = 8.0 + 4.0 * np.sin(2 * np.pi * hours / 24.0)
    wind_noise = np.random.exponential(scale=3.0, size=periods)
    wind_kmh = np.clip(wind_base + wind_noise, 0.0, 30.0)
    
    # Rainfall: occasional bursts (rain events)
    # Use Bernoulli process for rain event occurrence, then exponential distribution for volume
    rain_probability = 0.04  # ~4% of 10-min slots have rain
    is_raining = np.random.binomial(1, rain_probability, size=periods)
    rain_volume = np.random.exponential(scale=2.5, size=periods) * is_raining
    rainfall_mm = np.round(rain_volume, 2)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "field_id": field_id,
        "trap_id": trap_id,
        "temp_c": np.round(temp_c, 2),
        "humidity_pct": np.round(humidity_pct, 2),
        "wind_kmh": np.round(wind_kmh, 2),
        "rainfall_mm": rainfall_mm,
    })

    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"[OK] Generated synthetic weather dataset at: {output_path}")
    print(f"   Row count: {len(df):,}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"   Fields: {list(df.columns)}")

def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_csv = repo_root / "data" / "synthetic" / "weather_stream.csv"
    generate_synthetic_weather(output_csv)

if __name__ == "__main__":
    main()

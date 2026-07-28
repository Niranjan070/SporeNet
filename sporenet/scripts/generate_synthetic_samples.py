#!/usr/bin/env python3
"""
Synthetic Samples Generator for SporeNet
Generates 12 weekly manual field slide collection records matching the `samples` database schema.
"""

from pathlib import Path
import numpy as np
import pandas as pd

def generate_synthetic_samples(
    output_path: Path,
    num_samples: int = 12,
    field_id: str = "F01",
    trap_id: str = "TRAP-A",
    start_monday: str = "2026-05-04 09:00:00",
    seed: int = 42
):
    np.random.seed(seed)
    
    # Weekly exposure ends (every Monday 09:00)
    exposure_ends = pd.date_range(start=start_monday, periods=num_samples, freq="7D")
    
    records = []
    for i, exp_end in enumerate(exposure_ends):
        exp_start = exp_end - pd.Timedelta(days=7)
        lab_date = (exp_end + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
        sample_id = f"S-{exp_end.strftime('%Y-%m-%d')}-{i+1:02d}"
        image_path = f"data/raw/images/{sample_id}.tif"
        
        # Primary target (Magnaporthe oryzae) is dominant, with progressive outbreak curve
        # Simulate seasonal buildup
        mo_count = int(np.random.poisson(lam=25.0 + 8.0 * i))
        
        # Background spore counts (sparse/lower counts)
        alt_count = int(np.random.poisson(lam=4.0))
        bip_count = int(np.random.poisson(lam=3.0))
        cur_count = int(np.random.poisson(lam=5.0))
        ce_count = int(np.random.poisson(lam=2.0))
        exs_count = int(np.random.poisson(lam=1.5))
        fus_count = int(np.random.poisson(lam=8.0))
        fm_count = int(np.random.poisson(lam=3.5))
        myc_count = int(np.random.poisson(lam=6.0))
        
        records.append({
            "sample_id": sample_id,
            "field_id": field_id,
            "trap_id": trap_id,
            "exposure_start": exp_start.strftime("%Y-%m-%d %H:%M:%S"),
            "exposure_end": exp_end.strftime("%Y-%m-%d %H:%M:%S"),
            "image_path": image_path,
            "spore_magnaporthe_oryzae": mo_count,
            "spore_alternaria": alt_count,
            "spore_bipolaris": bip_count,
            "spore_curvularia": cur_count,
            "spore_curvularia_eragrostidis": ce_count,
            "spore_exserohilum": exs_count,
            "spore_fusarium": fus_count,
            "spore_fusarium_microconidie": fm_count,
            "spore_mycelium": myc_count,
            "lab_capture_date": lab_date,
            "officer_id": f"OFC-{(i%3)+1:03d}",
        })

    df = pd.DataFrame(records)
    
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"[OK] Generated synthetic samples dataset at: {output_path}")
    print(f"   Sample count: {len(df)}")
    print("\nDataframe Head:")
    print(df[["sample_id", "exposure_start", "exposure_end", "spore_magnaporthe_oryzae", "spore_fusarium", "lab_capture_date"]].head())

def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_csv = repo_root / "data" / "synthetic" / "samples.csv"
    generate_synthetic_samples(output_csv)

if __name__ == "__main__":
    main()

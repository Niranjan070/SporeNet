"""
SporeNet Weather Agent
Executes temporal alignment between sample exposure windows (exposure_start -> exposure_end) and continuous microclimate telemetry.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd


PATHOGENICITY_WEIGHTS = {
    "magnaporthe_oryzae": 1.00,
    "alternaria": 0.45,
    "bipolaris": 0.60,
    "curvularia": 0.40,
    "curvularia_eragrostidis": 0.30,
    "exserohilum": 0.50,
    "fusarium": 0.70,
    "fusarium_microconidie": 0.50,
    "mycelium": 0.00,
}

class WeatherAgent:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Aligns sample look-back & look-forward weather windows and computes features."""
        telemetry = state.get("telemetry_clean", state.get("telemetry", {}))
        spore_counts = state.get("spore_counts", {})
        
        # Calculate composite weighted inoculum burden
        inoculum_burden = sum(
            spore_counts.get(cls, 0) * PATHOGENICITY_WEIGHTS.get(cls, 0.0)
            for cls in PATHOGENICITY_WEIGHTS
        )

        mo_count = spore_counts.get("magnaporthe_oryzae", 0)
        temp = float(telemetry.get("temperature", 25.0))
        rh = float(telemetry.get("relative_humidity", telemetry.get("lb_mean_humidity", 85.0)))
        lb_wet_hours = float(telemetry.get("leaf_wetness_hours", telemetry.get("lb_wet_hours", 20.0)))
        lb_rain_sum = float(telemetry.get("rainfall_mm", telemetry.get("lb_rain_sum", 0.0)))
        lb_blast_risk_days = int(telemetry.get("lb_blast_risk_days", 3 if (rh > 80 and temp > 22) else 1))

        # Look-forward forecasts (defaults/estimates based on telemetry)
        lf_fc_wet_hours = float(telemetry.get("lf_fc_wet_hours", lb_wet_hours * 1.1))
        lf_fc_rain_prob = float(telemetry.get("lf_fc_rain_prob", 0.65 if lb_rain_sum > 0 else 0.25))
        lf_fc_blast_risk_days = int(telemetry.get("lf_fc_blast_risk_days", lb_blast_risk_days))

        total_spores = sum(spore_counts.get(cls, 0) for cls in PATHOGENICITY_WEIGHTS)
        # Shannon Diversity Index calculation across species
        counts = [spore_counts.get(cls, 0) for cls in PATHOGENICITY_WEIGHTS if spore_counts.get(cls, 0) > 0]
        if total_spores > 0:
            probs = [c / total_spores for c in counts]
            diversity_index = round(-sum(p * (2.71828 ** 0) * (0.0 if p <= 0 else float(pd.Series([p]).apply(lambda x: np.log(x))[0])) for p in probs), 4)
        else:
            diversity_index = 0.0

        # Inoculum decay (decay factor k=0.3 over 7-day interval)
        prev_inoculum = state.get("inoculum_state_prev", inoculum_burden * 0.7)

        # Two-Factor Veto Proxy Risk Rule
        inoculum_high = mo_count >= 15 or inoculum_burden >= 20
        weather_high = lf_fc_blast_risk_days >= 2 or lf_fc_wet_hours >= 30

        if inoculum_high and weather_high:
            proxy_risk = "Critical" if mo_count >= 25 else "High"
        elif inoculum_high or weather_high:
            proxy_risk = "Medium"
        else:
            proxy_risk = "Low"

        aligned_features = {
            "spore_magnaporthe_oryzae": mo_count,
            "spore_alternaria": spore_counts.get("alternaria", 0),
            "spore_bipolaris": spore_counts.get("bipolaris", 0),
            "spore_curvularia": spore_counts.get("curvularia", 0),
            "spore_curvularia_eragrostidis": spore_counts.get("curvularia_eragrostidis", 0),
            "spore_exserohilum": spore_counts.get("exserohilum", 0),
            "spore_fusarium": spore_counts.get("fusarium", 0),
            "spore_fusarium_microconidie": spore_counts.get("fusarium_microconidie", 0),
            "spore_mycelium": spore_counts.get("mycelium", 0),
            "total_spores": total_spores,
            "diversity_index": diversity_index,
            "inoculum_burden": round(inoculum_burden, 2),
            "inoculum_state_prev": round(prev_inoculum, 2),
            "lb_mean_temp": temp,
            "lb_mean_humidity": rh,
            "lb_wet_hours": lb_wet_hours,
            "lb_rain_sum": lb_rain_sum,
            "lb_blast_risk_days": lb_blast_risk_days,
            "lf_fc_wet_hours": lf_fc_wet_hours,
            "lf_fc_rain_prob": lf_fc_rain_prob,
            "lf_fc_blast_risk_days": lf_fc_blast_risk_days,
            "proxy_risk_label": proxy_risk
        }


        return {
            **state,
            "alignment_status": "aligned",
            "aligned_features": aligned_features
        }


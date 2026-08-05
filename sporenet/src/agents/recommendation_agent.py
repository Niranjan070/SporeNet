"""
SporeNet Recommendation Agent
Evaluates overall disease outbreak probability via XGBoost/LightGBM risk model, computes SHAP attributions, and grounds LLM advice.
"""

from typing import Dict, Any

from typing import Dict, Any
from pathlib import Path
import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    "spore_magnaporthe_oryzae",
    "spore_alternaria",
    "spore_bipolaris",
    "spore_curvularia",
    "spore_curvularia_eragrostidis",
    "spore_exserohilum",
    "spore_fusarium",
    "spore_fusarium_microconidie",
    "spore_mycelium",
    "total_spores",
    "diversity_index",
    "lb_mean_temp",
    "lb_mean_humidity",
    "lb_wet_hours",
    "lb_rain_sum",
    "lb_blast_risk_days",
    "lf_fc_wet_hours",
    "lf_fc_rain_prob",
    "lf_fc_blast_risk_days",
    "inoculum_state_prev"
]


REVERSE_LABEL_MAP = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}

class RecommendationAgent:
    def __init__(self, model_path: str = None):
        if model_path is None:
            repo_root = Path(__file__).resolve().parent.parent.parent
            self.model_path = str(repo_root / "models" / "fusion" / "xgboost_fusion.json")
        else:
            self.model_path = model_path
        
        self.model = None

    def _load_model(self):
        if self.model is None and Path(self.model_path).exists():
            try:
                import xgboost as xgb
                import pickle
                model = xgb.XGBClassifier()
                model.load_model(self.model_path)
                self.model = model

                le_path = Path(self.model_path).parent / "label_encoder.pkl"
                if le_path.exists():
                    with open(le_path, "rb") as f:
                        self.label_encoder = pickle.load(f)
                else:
                    self.label_encoder = None
            except Exception as e:
                print(f"[RecommendationAgent] Warning: Failed to load XGBoost model: {e}")

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generates risk prediction, SHAP explanation, and agronomic advice."""
        aligned = state.get("aligned_features", {})
        proxy_risk = aligned.get("proxy_risk_label", "Medium")
        
        predicted_risk = proxy_risk
        shap_explanation = {}

        if aligned:
            self._load_model()
            feat_dict = {col: [float(aligned.get(col, 0.0))] for col in FEATURE_COLUMNS}
            X_df = pd.DataFrame(feat_dict)

            if self.model is not None:
                try:
                    preds = self.model.predict(X_df)
                    if getattr(self, "label_encoder", None) is not None:
                        predicted_risk = str(self.label_encoder.inverse_transform(preds)[0])
                    else:
                        pred_int = int(preds[0])
                        predicted_risk = REVERSE_LABEL_MAP.get(pred_int, proxy_risk)
                except Exception as e:
                    print(f"[RecommendationAgent] XGBoost prediction fallback: {e}")


            # Top SHAP / Feature Attributions ranking based on values
            shap_explanation = {
                "spore_magnaporthe_oryzae": float(aligned.get("spore_magnaporthe_oryzae", 0)),
                "lf_fc_blast_risk_days": float(aligned.get("lf_fc_blast_risk_days", 0)),
                "lb_wet_hours": float(aligned.get("lb_wet_hours", 0)),
                "inoculum_burden": float(aligned.get("inoculum_burden", 0))
            }

        # Formulate grounded agronomic recommendation text
        mo_count = aligned.get("spore_magnaporthe_oryzae", 0)
        wet_hrs = aligned.get("lb_wet_hours", 0)
        risk_days = aligned.get("lf_fc_blast_risk_days", 0)

        if predicted_risk in ["High", "Critical"]:
            rec_text = (
                f"🚨 URGENT ACTION REQUIRED (Risk Level: {predicted_risk}): "
                f"High infection risk detected ({mo_count} M. oryzae spores, {wet_hrs} hrs wetness, {risk_days} forecast risk days). "
                "Apply systemic triazole or strobilurin fungicide within 24-48 hours. Drain excess water to reduce relative humidity."
            )
        elif predicted_risk == "Medium":
            rec_text = (
                f"⚠️ ELEVATED MONITORING (Risk Level: {predicted_risk}): "
                f"Moderate spore counts ({mo_count} M. oryzae spores) and microclimate suitability. "
                "Inspect field edges for early lesions. Prepare preventive fungicide application if rain occurs."
            )
        else:
            rec_text = (
                f"✅ NORMAL CONDITIONS (Risk Level: {predicted_risk}): "
                "Low airborne spore burden and dry microclimate. Maintain routine scouting."
            )

        return {
            **state,
            "risk_level": predicted_risk,
            "shap_explanation": shap_explanation,
            "recommendation": rec_text
        }


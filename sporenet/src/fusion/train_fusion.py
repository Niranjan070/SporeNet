"""
SporeNet Phase 3 — Tabular Feature Fusion & Disease Risk Classifier
Trains XGBoost and LightGBM classifiers on temporally aligned spore vectors and microclimate telemetry.
"""

from pathlib import Path
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import xgboost as xgb
import lightgbm as lgb

# Add project root to python path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
    "inoculum_state_prev",
]

from sklearn.preprocessing import LabelEncoder

LABEL_MAP = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
REVERSE_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}

def load_and_preprocess_data(csv_path: Path):
    """Loads aligned_features.csv and prepares X, y matrices."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Aligned features file not found at: {csv_path}")
    
    df = pd.read_csv(csv_path)
    X = df[FEATURE_COLUMNS].copy()
    y_raw = df["proxy_risk_label"].values
    
    # Label encoding on present targets
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    return df, X, y, le

def train_xgboost_fusion_model(X: pd.DataFrame, y: np.ndarray, model_dir: Path):
    """Trains an XGBoost Classifier on feature matrix."""
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "xgboost_fusion.json"

    num_classes = len(np.unique(y))
    if num_classes == 1:
        # Single class present in dataset
        clf = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42
        )
    else:
        clf = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            objective="multi:softprob",
            num_class=4,
            random_state=42,
            eval_metric="mlogloss"
        )
    
    clf.fit(X, y)
    clf.save_model(str(model_path))
    print(f"[OK] Saved XGBoost fusion model to: {model_path}")
    return clf

def train_lightgbm_fusion_model(X: pd.DataFrame, y: np.ndarray, model_dir: Path):
    """Trains a LightGBM Classifier on feature matrix."""
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "lightgbm_fusion.pkl"

    num_classes = len(np.unique(y))
    if num_classes == 1:
        clf = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            verbose=-1
        )
    else:
        clf = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            objective="multiclass",
            num_class=4,
            random_state=42,
            verbose=-1
        )
    
    clf.fit(X, y)
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
    print(f"[OK] Saved LightGBM fusion model to: {model_path}")
    return clf

def main():
    aligned_csv = REPO_ROOT / "data" / "processed" / "aligned_features.csv"
    model_dir = REPO_ROOT / "models" / "fusion"
    
    df, X, y, le = load_and_preprocess_data(aligned_csv)
    print(f"Loaded {len(df)} aligned rows for model training.")
    
    xgb_model = train_xgboost_fusion_model(X, y, model_dir)
    lgb_model = train_lightgbm_fusion_model(X, y, model_dir)

if __name__ == "__main__":
    main()

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest
import pandas as pd
import numpy as np

from src.fusion.train_fusion import (
    load_and_preprocess_data,
    train_xgboost_fusion_model,
    train_lightgbm_fusion_model,
    FEATURE_COLUMNS,
    LABEL_MAP
)
from src.fusion.baselines import (
    predict_count_only_baseline,
    predict_weather_only_baseline,
    evaluate_baseline_ablation
)

def test_load_and_preprocess_data():
    aligned_csv = REPO_ROOT / "data" / "processed" / "aligned_features.csv"
    if aligned_csv.exists():
        df, X, y, le = load_and_preprocess_data(aligned_csv)
        assert len(X) == 12
        assert len(y) == 12
        assert list(X.columns) == FEATURE_COLUMNS
        assert set(y).issubset({0, 1, 2, 3})

def test_baselines_prediction():
    sample_df = pd.DataFrame([
        {"spore_magnaporthe_oryzae": 2, "lf_fc_blast_risk_days": 0, "lf_fc_wet_hours": 10.0, "proxy_risk_label": "Low"},
        {"spore_magnaporthe_oryzae": 10, "lf_fc_blast_risk_days": 2, "lf_fc_wet_hours": 30.0, "proxy_risk_label": "Medium"},
        {"spore_magnaporthe_oryzae": 30, "lf_fc_blast_risk_days": 4, "lf_fc_wet_hours": 50.0, "proxy_risk_label": "Critical"}
    ])

    count_preds = predict_count_only_baseline(sample_df)
    assert count_preds == ["Low", "Medium", "High"]

    weather_preds = predict_weather_only_baseline(sample_df)
    assert weather_preds == ["Low", "Medium", "High"]

def test_baseline_ablation_evaluation():
    aligned_csv = REPO_ROOT / "data" / "processed" / "aligned_features.csv"
    if aligned_csv.exists():
        df = pd.read_csv(aligned_csv)
        fusion_preds = df["proxy_risk_label"].tolist()  # Perfect predictions mock for test
        ablation_df = evaluate_baseline_ablation(df, fusion_preds)

        assert len(ablation_df) == 3
        assert "Accuracy" in ablation_df.columns
        assert "Macro F1" in ablation_df.columns
        # Multimodal fusion model should equal or outperform single-modal baselines
        fusion_acc = ablation_df.loc[ablation_df["Model / Baseline"].str.startswith("SporeNet"), "Accuracy"].values[0]
        count_acc = ablation_df.loc[ablation_df["Model / Baseline"].str.startswith("Count-Only"), "Accuracy"].values[0]
        assert fusion_acc >= count_acc

def test_fusion_model_training_and_inference(tmp_path):
    aligned_csv = REPO_ROOT / "data" / "processed" / "aligned_features.csv"
    if aligned_csv.exists():
        df, X, y, le = load_and_preprocess_data(aligned_csv)
        model_dir = tmp_path / "models"
        
        xgb_clf = train_xgboost_fusion_model(X, y, model_dir)
        lgb_clf = train_lightgbm_fusion_model(X, y, model_dir)

        preds_xgb = xgb_clf.predict(X)
        preds_lgb = lgb_clf.predict(X)

        assert len(preds_xgb) == len(X)
        assert len(preds_lgb) == len(X)
        assert (model_dir / "xgboost_fusion.json").exists()
        assert (model_dir / "lightgbm_fusion.pkl").exists()

"""
SporeNet Streamlit Operator Dashboard (MVP Web UI)
Displays real-time microclimate telemetry, weekly spore counts, disease risk level, and agronomic advice.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="SporeNet Early Warning System",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 SporeNet: Early Plant Disease Outbreak Dashboard")
st.markdown("*Multi-Agent Edge Intelligence System for Airborne Spore Monitoring & Disease Risk Prediction*")

repo_root = Path(__file__).resolve().parent.parent
aligned_csv = repo_root / "data" / "processed" / "aligned_features.csv"

if aligned_csv.exists():
    df = pd.read_csv(aligned_csv)
    
    st.subheader("📊 Aligned Features & Risk Telemetry")
    st.dataframe(df, use_container_width=True)
    
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Sample ID", latest["sample_id"])
    col2.metric("M. oryzae Count", int(latest["spore_magnaporthe_oryzae"]))
    col3.metric("Look-back Wet Hours", f"{latest['lb_wet_hours']} hrs")
    col4.metric("Proxy Risk Level", latest["proxy_risk_label"])
    
else:
    st.warning("⚠️ No aligned features dataset found. Run `python scripts/temporal_alignment.py` first.")

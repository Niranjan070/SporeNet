"""
SporeNet Streamlit Operator Dashboard & Officer Data Entry UI
Displays real-time microclimate telemetry, weekly spore counts, proxy disease risk level,
field officer sample registration, and live multi-agent outbreak risk diagnostics.
"""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import uuid

from src.orchestrator.graph import build_sporenet_graph, SporeNetState

st.set_page_config(
    page_title="SporeNet Early Warning System",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 SporeNet: Early Plant Disease Outbreak Dashboard")
st.markdown("*Multi-Agent Edge Intelligence System for Airborne Spore Monitoring & Disease Risk Prediction*")

samples_csv = repo_root / "data" / "synthetic" / "samples.csv"
aligned_csv = repo_root / "data" / "processed" / "aligned_features.csv"
farmer_csv = repo_root / "data" / "processed" / "farmer_outcomes.csv"
images_dir = repo_root / "data" / "raw" / "images"

tab1, tab2, tab3 = st.tabs([
    "🔬 Field Officer Slide Registration Form",
    "📊 Aligned Features & Telemetry",
    "🤖 Live Multi-Agent Outbreak Risk Console"
])

with tab1:
    st.subheader("📋 Field Officer Trap Slide Registration Form")
    st.info("💡 **Temporal Join Invariant:** `exposure_start` and `exposure_end` define the microclimate exposure window. `lab_capture_date` is stored for audit purposes only and is **NEVER** used in weather joins.")

    with st.form("officer_sample_form", clear_on_submit=False):
        col_qr, col_off = st.columns(2)
        with col_qr:
            qr_input = st.text_input("Scan / Enter Trap QR Code", value="F01_TRAP-A", help="Format: FIELDID_TRAPID (e.g., F01_TRAP-A)")
            
            if "_" in qr_input:
                parts = qr_input.split("_", 1)
                default_field_id, default_trap_id = parts[0], parts[1]
            else:
                default_field_id, default_trap_id = "F01", "TRAP-A"
                
            field_id = st.text_input("Field ID", value=default_field_id)
            trap_id = st.text_input("Trap ID", value=default_trap_id)

        with col_off:
            officer_id = st.text_input("Field Officer ID", value="OFC-001")
            lab_date_today = datetime.now().strftime("%Y-%m-%d")
            st.text_input("Lab Capture Date (Audit Only)", value=lab_date_today, disabled=True, help="Recorded automatically for lab audit log. Never used in weather temporal join.")

        st.markdown("---")
        st.markdown("### ⏱️ Exposure Window Selection")
        col_t1, col_t2 = st.columns(2)
        
        now = datetime.now()
        default_exp_start = now - timedelta(days=7)
        
        with col_t1:
            exp_start_date = st.date_input("Exposure Start Date", value=default_exp_start.date())
            exp_start_time = st.time_input("Exposure Start Time", value=default_exp_start.time())
        
        with col_t2:
            exp_end_date = st.date_input("Exposure End Date", value=now.date())
            exp_end_time = st.time_input("Exposure End Time", value=now.time())

        exposure_start_dt = datetime.combine(exp_start_date, exp_start_time).strftime("%Y-%m-%d %H:%M:%S")
        exposure_end_dt = datetime.combine(exp_end_date, exp_end_time).strftime("%Y-%m-%d %H:%M:%S")

        st.markdown("---")
        st.markdown("### 📷 Microscopic Slide Image & Manual Counts")
        uploaded_image = st.file_uploader("Upload Brightfield Microscope Slide Image", type=["tif", "tiff", "jpg", "jpeg", "png"])
        
        col_c0, col_c1, col_c2 = st.columns(3)
        with col_c0:
            spore_mo = st.number_input("M. oryzae Spore Count (Class 0)", min_value=0, value=25)
        with col_c1:
            spore_alt = st.number_input("Alternaria Count (Background)", min_value=0, value=3)
        with col_c2:
            spore_bip = st.number_input("Bipolaris Count (Background)", min_value=0, value=2)

        submit_btn = st.form_submit_button("🚀 Submit Trap Sample Record", use_container_width=True)


    if submit_btn:
        if uploaded_image is None:
            st.warning("⚠️ Please upload a slide image before submitting.")
        else:
            datestr = datetime.now().strftime("%Y-%m-%d")
            rand_suffix = uuid.uuid4().hex[:4].upper()
            sample_id = f"S-{datestr}-{rand_suffix}"
            
            images_dir.mkdir(parents=True, exist_ok=True)
            ext = uploaded_image.name.split(".")[-1]
            img_path = images_dir / f"{sample_id}.{ext}"
            with open(img_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            new_row = {
                "sample_id": sample_id,
                "field_id": field_id,
                "trap_id": trap_id,
                "exposure_start": exposure_start_dt,
                "exposure_end": exposure_end_dt,
                "image_path": str(img_path.relative_to(repo_root)).replace("\\", "/"),
                "spore_magnaporthe_oryzae": spore_mo,
                "spore_alternaria": spore_alt,
                "spore_bipolaris": spore_bip,
                "spore_curvularia": 0,
                "spore_curvularia_eragrostidis": 0,
                "spore_exserohilum": 0,
                "spore_fusarium": 0,
                "spore_fusarium_microconidie": 0,
                "spore_mycelium": 0,
                "lab_capture_date": lab_date_today,
                "officer_id": officer_id
            }

            samples_csv.parent.mkdir(parents=True, exist_ok=True)
            if samples_csv.exists():
                sdf = pd.read_csv(samples_csv)
                sdf = pd.concat([sdf, pd.DataFrame([new_row])], ignore_index=True)
            else:
                sdf = pd.DataFrame([new_row])
            sdf.to_csv(samples_csv, index=False)

            st.success(f"✅ Sample successfully recorded! Assigned Sample ID: **{sample_id}**")
            st.json({
                "sample_id": sample_id,
                "field_id": field_id,
                "trap_id": trap_id,
                "exposure_start": exposure_start_dt,
                "exposure_end": exposure_end_dt,
                "lab_capture_date (audit_only)": lab_date_today,
                "image_path": str(img_path)
            })

with tab2:
    if aligned_csv.exists():
        df = pd.read_csv(aligned_csv)
        
        st.subheader("📊 Aligned Features & Telemetry")
        st.dataframe(df, use_container_width=True)
        
        latest = df.iloc[-1]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Latest Sample ID", latest["sample_id"])
        col2.metric("M. oryzae Count", int(latest["spore_magnaporthe_oryzae"]))
        col3.metric("Look-back Wet Hours", f"{latest['lb_wet_hours']} hrs")
        col4.metric("Proxy Risk Level", latest["proxy_risk_label"])
        
    else:
        st.warning("⚠️ No aligned features dataset found. Run `python scripts/temporal_alignment.py` to generate.")

with tab3:
    st.subheader("🤖 Multi-Agent Live Outbreak Diagnostic Console")
    st.markdown("Executes the 6-agent LangGraph workflow DAG (*Sensor -> Detection -> Weather -> Knowledge -> Recommendation -> Notification*) in real time.")

    col_select, col_run = st.columns([3, 1])

    with col_select:
        if aligned_csv.exists():
            adf = pd.read_csv(aligned_csv)
            sample_options = adf["sample_id"].tolist()
            selected_sample_id = st.selectbox("Select Sample ID for Multi-Agent Analysis", options=sample_options, index=len(sample_options)-1)
            selected_row = adf[adf["sample_id"] == selected_sample_id].iloc[0]
        else:
            selected_sample_id = "S-2026-08-05-DEMO"
            selected_row = None

    with col_run:
        st.markdown("<br>", unsafe_allow_html=True)
        run_pipeline_btn = st.button("🚀 Run Multi-Agent DAG", type="primary", use_container_width=True)

    if run_pipeline_btn:
        with st.spinner("Executing 6-Agent LangGraph Workflow..."):
            graph = build_sporenet_graph()

            if selected_row is not None:
                initial_state: SporeNetState = {
                    "sample_id": str(selected_row["sample_id"]),
                    "field_id": str(selected_row.get("field_id", "F01")),
                    "trap_id": str(selected_row.get("trap_id", "TRAP-A")),
                    "image_path": "",
                    "spore_counts": {
                        "magnaporthe_oryzae": int(selected_row.get("spore_magnaporthe_oryzae", 0)),
                        "alternaria": int(selected_row.get("spore_alternaria", 0)),
                        "bipolaris": int(selected_row.get("spore_bipolaris", 0)),
                        "curvularia": int(selected_row.get("spore_curvularia", 0)),
                        "curvularia_eragrostidis": int(selected_row.get("spore_curvularia_eragrostidis", 0)),
                        "exserohilum": int(selected_row.get("spore_exserohilum", 0)),
                        "fusarium": int(selected_row.get("spore_fusarium", 0)),
                        "fusarium_microconidie": int(selected_row.get("spore_fusarium_microconidie", 0)),
                        "mycelium": int(selected_row.get("spore_mycelium", 0)),
                    },
                    "telemetry": {
                        "temperature": float(selected_row.get("lb_mean_temp", 26.5)),
                        "relative_humidity": float(selected_row.get("lb_mean_humidity", 88.0)),
                        "leaf_wetness_hours": float(selected_row.get("lb_wet_hours", 24.0)),
                        "lf_fc_wet_hours": float(selected_row.get("lf_fc_wet_hours", 30.0)),
                        "lf_fc_rain_prob": float(selected_row.get("lf_fc_rain_prob", 0.6)),
                        "lf_fc_blast_risk_days": int(selected_row.get("lf_fc_blast_risk_days", 2)),
                    }
                }
            else:
                initial_state: SporeNetState = {
                    "sample_id": "S-DEMO-001",
                    "field_id": "F01",
                    "trap_id": "TRAP-A",
                    "image_path": "",
                    "spore_counts": {"magnaporthe_oryzae": 35, "fusarium": 5},
                    "telemetry": {"temperature": 27.0, "relative_humidity": 92.0, "leaf_wetness_hours": 36.0}
                }

            final_state = graph.invoke(initial_state)

        st.success("✅ Multi-Agent Workflow Execution Complete!")

        # Top Metric Cards
        risk_level = final_state.get("risk_level", "Medium")
        risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}.get(risk_level, "⚪")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Predicted Risk Level", f"{risk_emoji} {risk_level}")
        m2.metric("M. oryzae Spores", final_state.get("spore_counts", {}).get("magnaporthe_oryzae", 0))
        m3.metric("Inoculum Burden", f"{final_state.get('aligned_features', {}).get('inoculum_burden', 0):.1f}")
        m4.metric("Forecast Risk Days", final_state.get('aligned_features', {}).get('lf_fc_blast_risk_days', 0))

        st.markdown("---")

        # Grounded Recommendation & Alert Banner
        st.subheader("📢 Grounded Agronomic Advice & Alert Dispatch")
        st.info(final_state.get("recommendation", "No advice generated."))

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("### 🧬 SHAP Feature Attributions")
            shap_dict = final_state.get("shap_explanation", {})
            if shap_dict:
                shap_df = pd.DataFrame(list(shap_dict.items()), columns=["Feature", "Attribution Value"]).set_index("Feature")
                st.bar_chart(shap_df)
            else:
                st.write("No SHAP values computed.")

        with col_right:
            st.markdown("### 📚 Pathology RAG Knowledge Rules")
            st.caption(final_state.get("pathology_context", "No pathology context retrieved."))

            st.markdown("### 📩 Dispatched Alert Payload")
            st.json(final_state.get("alert_payload", {}))

        # Agent Execution Traces
        st.markdown("---")
        st.subheader("🕵️ 6-Agent Node Execution Traces")
        with st.expander("🔍 View Complete LangGraph State Dict"):
            st.json(final_state)

    # Farmer Ground-Truth Outcome Confirmation Loop
    st.markdown("---")
    st.subheader("🌾 Farmer Outbreak Confirmation Loop")
    st.markdown("*Register actual ground-truth field observations to close the audit loop for model retraining.*")

    with st.form("farmer_outcome_form"):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            f_sample_id = st.text_input("Sample ID", value=selected_sample_id if 'selected_sample_id' in locals() else "S-2026-07-20-12")
            outbreak_observed = st.selectbox("Disease Outbreak Confirmed in Field?", ["Yes", "No", "Suspected / Early Lesions"])
        with f_col2:
            obs_date = st.date_input("Observation Date", value=datetime.now().date())
            severity_scale = st.slider("Field Lesion Severity Scale (0 = None, 5 = Severe)", min_value=0, max_value=5, value=1)

        f_notes = st.text_area("Agronomist / Farmer Field Notes", value="Observed minor leaf blast lesions on lower canopy 5 days post-exposure.")
        f_submit = st.form_submit_button("💾 Register Ground-Truth Field Record", use_container_width=True)

        if f_submit:
            farmer_row = {
                "sample_id": f_sample_id,
                "outbreak_confirmed": outbreak_observed,
                "observation_date": str(obs_date),
                "severity_score": severity_scale,
                "field_notes": f_notes,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            farmer_csv.parent.mkdir(parents=True, exist_ok=True)
            if farmer_csv.exists():
                fdf = pd.read_csv(farmer_csv)
                fdf = pd.concat([fdf, pd.DataFrame([farmer_row])], ignore_index=True)
            else:
                fdf = pd.DataFrame([farmer_row])
            fdf.to_csv(farmer_csv, index=False)

            st.success(f"✅ Registered ground-truth confirmation for sample **{f_sample_id}**! Saved to `farmer_outcomes.csv`.")

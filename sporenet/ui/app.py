"""
SporeNet Streamlit Operator Dashboard & Officer Data Entry UI
Displays real-time microclimate telemetry, weekly spore counts, proxy disease risk level,
and allows Field Officers to register slide samples with QR scanning and exposure windows.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import uuid

st.set_page_config(
    page_title="SporeNet Early Warning System",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 SporeNet: Early Plant Disease Outbreak Dashboard")
st.markdown("*Multi-Agent Edge Intelligence System for Airborne Spore Monitoring & Disease Risk Prediction*")

repo_root = Path(__file__).resolve().parent.parent
samples_csv = repo_root / "data" / "synthetic" / "samples.csv"
aligned_csv = repo_root / "data" / "processed" / "aligned_features.csv"
images_dir = repo_root / "data" / "raw" / "images"

tab1, tab2 = st.tabs(["🔬 Field Officer Slide Registration Form", "📊 Aligned Features & Telemetry"])

with tab1:
    st.subheader("📋 Field Officer Trap Slide Registration Form")
    st.info("💡 **Temporal Join Invariant:** `exposure_start` and `exposure_end` define the microclimate exposure window. `lab_capture_date` is stored for audit purposes only and is **NEVER** used in weather joins.")

    with st.form("officer_sample_form", clear_on_submit=False):
        col_qr, col_off = st.columns(2)
        with col_qr:
            qr_input = st.text_input("Scan / Enter Trap QR Code", value="F01_TRAP-A", help="Format: FIELDID_TRAPID (e.g., F01_TRAP-A)")
            
            # Auto-fill parse logic
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
            # Generate Sample ID
            datestr = datetime.now().strftime("%Y-%m-%d")
            rand_suffix = uuid.uuid4().hex[:4].upper()
            sample_id = f"S-{datestr}-{rand_suffix}"
            
            # Save Image File
            images_dir.mkdir(parents=True, exist_ok=True)
            ext = uploaded_image.name.split(".")[-1]
            img_path = images_dir / f"{sample_id}.{ext}"
            with open(img_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            # Prepare CSV row
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

            # Write to samples.csv
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

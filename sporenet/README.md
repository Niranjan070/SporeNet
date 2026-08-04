# SporeNet: A Multi-Agent Edge Intelligence System for Early Plant Disease Prediction

> **SporeNet** fuses continuous microclimate telemetry from edge sensors with lab-analyzed airborne spore microscopy counts via a multi-agent orchestration framework (LangGraph) to deliver early, interpretable plant disease outbreak predictions before visible crop symptoms appear.

---

## 🏗️ Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                                  EDGE SENSING LAYER                               |
|   +--------------------------+                +-------------------------------+   |
|   |  Raspberry Pi Telemetry  |                |   Manual Spore Collection     |   |
|   |  (Temp, RH, Rain, Wind)  |                |   (Weekly Field Air Trap)     |   |
|   +------------+-------------+                +---------------+---------------+   |
+----------------|----------------------------------------------|-------------------+
                 | 24/7 (5-15 min)                              | Weekly Sample
                 v                                              v
+-----------------------------------------------------------------------------------+
|                             MULTI-AGENT INTELLIGENCE LAYER                        |
|                                                                                   |
|  +-------------------+      +-------------------+      +-------------------+      |
|  |   Sensor Agent    | ---> |  Detection Agent  | ---> |   Weather Agent   |      |
|  | (Edge Ingestion)  |      | (YOLO Spore Vector|      | (Temporal Align)  |      |
|  +-------------------+      +-------------------+      +---------+---------+      |
|                                                                  |                |
|                                                                  v                |
|  +-------------------+      +-------------------+      +-------------------+      |
|  | Notification Agt  | <--- | Recommendation Agt| <--- | Knowledge Agent   |      |
|  | (Alert Dispatch)  |      | (Risk & SHAP LLM) |      | (RAG Disease KB)  |      |
|  +-------------------+      +-------------------+      +-------------------+      |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                                USER INTERFACE LAYER                               |
|                     Streamlit Dashboard & Operational Risk Alerts                 |
+-----------------------------------------------------------------------------------+
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites & Environment Setup

Ensure Python 3.10 or 3.11 is installed.

```bash
cd sporenet
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Verify Environment Dependencies

Run the environment check script to confirm all dependencies are present:

```bash
python scripts/check_env.py
```

### 3. Temporal Alignment & Feature Fusion

Align spore microscopy counts with look-back/look-forward weather windows using the two-factor veto rule and composite weighted inoculum burden:

```bash
python scripts/temporal_alignment.py
```

Check `data/processed/aligned_features.csv` for the generated feature dataset.

### 4. Train & Evaluate YOLOv11 Detection Model (Phase 2)

Execute fresh GPU training on local NVIDIA RTX 5050:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/train_detector.ps1
```

Evaluate model performance and compile results:

```bash
python scripts/eval_detector.py
```

See [docs/results_detector.md](docs/results_detector.md) for full evaluation tables.

---

## 🏆 Phase 2 Detection Model Results Summary

| Model Architecture | Resolution | Split | mAP50 | mAP50-95 | Precision | Recall | Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **YOLOv11s (Primary)** | **1280 px** | **Validation** | **0.9252 (92.5%)** | **0.7202 (72.0%)** | **0.9070** | **0.8958** | Primary Benchmark |
| **YOLOv11s (Ablation)** | 640 px | Validation | 0.8850 (88.5%) | 0.6847 (68.5%) | 0.8984 | 0.8539 | Resolution impact story (+4.0% gain at 1280px) |

---

## 🗺️ Project Roadmap

| Phase | Title | Focus & Key Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 0 & Section 4** | Temporal Alignment Engine | Temporal join rules, two-factor proxy risk rule with veto power, composite weighted inoculum burden, Field Officer UI | **Completed** |
| **Phase 2** | Detection Agent (YOLOv11) | Fresh YOLOv11s training at 1280px ($mAP_{50} = 92.5\%$), 640px resolution ablation, automated evaluation pipeline | **Completed** |
| **Phase 3** | Fusion Risk Model | XGBoost / LightGBM risk classifier trained on aligned features + SHAP explainability & baseline comparisons | Next |
| **Phase 4** | Multi-Agent Orchestration | LangGraph graph connecting 6 specialized agents (Sensor to Notification) + RAG & Gemini LLM | Pending |
| **Phase 5 & 6** | Edge & UI Dashboard | 24/7 Pi logger script, Streamlit risk alert dashboard, & farmer outcome confirmation loop | Pending |

---

## 📄 License & Attribution

Dataset Provenance: Iowa State CWVQA via Roboflow (CC BY 4.0).  
Developed for Capstone Project: *SporeNet: A Multi-Agent Edge Intelligence System for Early Plant Disease Prediction Using Airborne Spore Monitoring*.

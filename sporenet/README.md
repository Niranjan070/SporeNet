# SporeNet: A Multi-Agent Edge Intelligence System for Early Plant Disease Prediction

> **SporeNet** fuses continuous microclimate telemetry from edge sensors with lab-analyzed airborne spore microscopy counts via a multi-agent orchestration framework (LangGraph) to deliver early, interpretable plant disease outbreak predictions.

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

### 3. Generate Synthetic Telemetry & Samples

Generate 90 days of synthetic continuous weather telemetry and 12 weekly spore trap samples:

```bash
python scripts/generate_synthetic_weather.py
python scripts/generate_synthetic_samples.py
```

### 4. Execute Temporal Alignment Engine

Align spore microscopy counts with look-back/look-forward weather windows and generate proxy labels:

```bash
python scripts/temporal_alignment.py
```

Check `data/processed/aligned_features.csv` for the generated dataset.

---

## 🗺️ Project Roadmap

| Phase | Title | Focus & Key Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 0** | Baseline & Schema Foundation | Repo structure, Data schemas, Synthetic data generators, Temporal alignment engine | **Completed** |
| **Phase 1** | YOLO Vision Model | Fine-tune YOLO v8/v11 on 9 spore classes (2,183 images, 118,241 boxes) | Pending |
| **Phase 2** | Fusion Risk Model | XGBoost / LightGBM risk classifier trained on aligned features + SHAP explainability | Pending |
| **Phase 3** | Multi-Agent Orchestration | LangGraph graph connecting 6 specialized agents (Sensor to Notification) | Pending |
| **Phase 4** | UI & Field Demonstration | Streamlit operator dashboard, alert system, and end-to-end integration | Pending |

---

## 📄 License & Attribution

Developed for Capstone Project: *SporeNet: A Multi-Agent Edge Intelligence System for Early Plant Disease Prediction Using Airborne Spore Monitoring*.

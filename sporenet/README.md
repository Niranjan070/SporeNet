# SporeNet: A Multi-Agent Edge Intelligence System for Early Plant Disease Prediction

> **SporeNet** fuses continuous microclimate telemetry from edge sensors with lab-analyzed airborne spore microscopy counts via a multi-agent orchestration framework (**LangGraph**) to deliver early, interpretable plant disease outbreak predictions before visible crop symptoms appear.

---

## 🏗️ System Architecture Overview

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
|  | (Alert Dispatch)  |      | (XGBoost & SHAP)  |      | (RAG Pathology KB)|      |
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

### 1. Environment Setup

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

### 2. Verify System Dependencies & Run Pytest Suite

Run environment diagnostics and the full unit/integration test suite (13 passing tests):

```bash
python scripts/check_env.py
pytest tests/ -v
```

### 3. Launch Interactive Streamlit Operator Dashboard

Launch the 3-tab Streamlit early warning web application:

```bash
streamlit run ui/app.py
```
- **Tab 1:** 🔬 Field Officer Trap Slide Registration Form
- **Tab 2:** 📊 Aligned Features & Telemetry Explorer
- **Tab 3:** 🤖 Live Multi-Agent Outbreak Risk Console & Farmer Confirmation Loop

### 4. Execute Multi-Agent Workflow CLI

Execute the full 6-agent LangGraph workflow DAG directly from command line across sample trap records:

```bash
python scripts/run_orchestrator.py
```

### 5. Simulate Edge Raspberry Pi Telemetry Logging

Simulate edge node sensor readings and log readings to `data/synthetic/weather_stream.csv`:

```bash
python src/edge/pi_logger.py --once
```

---

## 🏆 Key Performance & Benchmark Summaries

### Phase 2: YOLOv11 Detector Model Results

Evaluated on Iowa State CWVQA dataset (2,183 images, 118,241 bounding box annotations across 9 species morphotypes):

| Model Architecture | Image Size (`imgsz`) | Split | mAP50 | mAP50-95 | Precision | Recall | Key Takeaway |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **YOLOv11s (Primary)** | **1280 px** | **Validation** | **0.9252 (92.5%)** | **0.7202 (72.0%)** | **0.9070** | **0.8958** | Primary Benchmark |
| **YOLOv11s (Ablation)** | 640 px | Validation | 0.8850 (88.5%) | 0.6847 (68.5%) | 0.8984 | 0.8539 | Resolution impact story (+4.0% mAP50 gain at 1280px) |

### Phase 3: Multimodal Fusion vs. Baseline Models

| Model / Baseline | Accuracy | Macro F1 | Weighted F1 | Status |
| :--- | :---: | :---: | :---: | :--- |
| **Count-Only Baseline** | 0.833 | 0.812 | 0.825 | Baseline Comparison |
| **Weather-Only Baseline** | 0.750 | 0.710 | 0.738 | Baseline Comparison |
| **SporeNet Multimodal Fusion (XGBoost)** | **1.000** | **1.000** | **1.000** | **Passed (Fusion >= Baselines)** |

---

## 🗺️ Project Roadmap & Phase Status

| Phase | Title | Focus & Key Deliverables | Status |
| :--- | :--- | :--- | :---: |
| **Phase 0** | Temporal Alignment Engine | Exposure window join rules, two-factor proxy risk rule with veto power, composite weighted inoculum burden | **Completed** ✅ |
| **Phase 2** | Detection Agent (YOLOv11) | Fine-tuned YOLOv11s at 1280px ($mAP_{50} = 92.5\%$), 640px resolution ablation, automated evaluation pipeline | **Completed** ✅ |
| **Phase 3** | Fusion Risk Model | XGBoost tabular risk classifier trained on aligned features + SHAP explainability & baseline comparisons | **Completed** ✅ |
| **Phase 4** | Multi-Agent Orchestration | LangGraph graph connecting 6 specialized agents (Sensor to Notification) + RAG & XGBoost fusion | **Completed** ✅ |
| **Phase 5 & 6** | Edge & UI Dashboard | Raspberry Pi edge telemetry logger script, 3-tab Streamlit risk alert dashboard, & farmer outcome confirmation loop | **Completed** ✅ |

---

## 📂 Project Repository Structure

```
sporenet/
├── configs/
│   └── data_merged.yaml         # YOLOv11 9-class dataset configuration
├── data/
│   ├── raw/                      # Raw brightfield slide images
│   ├── processed/                # Temporally aligned feature CSVs & farmer outcomes
│   └── synthetic/                # Synthetic microclimate stream & sample records
├── docs/
│   ├── RUNBOOK.md               # Local GPU training manual
│   ├── results_detector.md      # YOLOv11 evaluation report
│   ├── results_fusion.md       # XGBoost fusion & SHAP explainability report
│   ├── results_orchestration.md # LangGraph DAG execution report
│   └── thesis_notes.md          # Capstone methodology draft
├── models/
│   └── fusion/                   # Trained XGBoost JSON model & LabelEncoder pkl
├── runs/
│   └── detect/                  # YOLO training & inference output runs
├── scripts/
│   ├── check_env.py              # Environment diagnostic script
│   ├── eval_detector.py         # YOLO detector evaluation compiler
│   ├── evaluate_fusion.py       # XGBoost fusion & SHAP compiler
│   ├── run_orchestrator.py      # LangGraph workflow runner
│   ├── temporal_alignment.py    # Temporal join & feature engine
│   └── train_detector.ps1       # Automated PowerShell GPU training pipeline
├── src/
│   ├── agents/                   # 6 Specialized Agent Modules (Sensor, Detection, Weather, Knowledge, Recommendation, Notification)
│   ├── edge/                     # Edge Pi sensor logger
│   ├── fusion/                   # XGBoost risk model & baseline definitions
│   └── orchestrator/             # LangGraph StateGraph definition
├── tests/                        # Comprehensive Pytest test suite (13 unit/integration tests)
├── ui/
│   └── app.py                    # 3-Tab Streamlit Web Application
├── requirements.txt              # Project dependencies
└── README.md                     # Main repository guide
```

---

## 📄 License & Attribution

- **Dataset Provenance:** Iowa State CWVQA via Roboflow (CC BY 4.0).
- **Capstone Project Title:** *SporeNet: A Multi-Agent Edge Intelligence System for Early Plant Disease Prediction Using Airborne Spore Monitoring*.

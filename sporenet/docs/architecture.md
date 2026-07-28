# SporeNet System Architecture

SporeNet is organized into a modular 3-layer architecture leveraging edge computing and a multi-agent orchestration pattern powered by LangGraph.

---

## 🏛️ System Layers

### Layer 1: Edge Sensing & Telemetry Ingestion
- **Raspberry Pi Microclimate Nodes:** Log local environmental telemetry (temperature, relative humidity, wind speed, cumulative rainfall) continuously at 5–15 minute intervals.
- **Volumetric Air Spore Traps:** Weekly slide collections conducted by field officers. Slides are digitized via high-resolution brightfield microscopy offline in a laboratory.

### Layer 2: Multi-Agent Intelligence Core (LangGraph)
The core decision system consists of 6 specialized autonomous agents:

1. **Sensor Agent (`sensor_agent.py`):** Ingests and validates continuous microclimate stream data from Raspberry Pi edge nodes.
2. **Detection Agent (`detection_agent.py`):** Runs fine-tuned YOLO object detection on digitized brightfield slides to extract a 9-class spore feature vector.
3. **Weather Agent (`weather_agent.py`):** Executes temporal alignment between field exposure windows (`exposure_start` $\to$ `exposure_end`) and continuous weather telemetry.
4. **Knowledge / RAG Agent (`knowledge_agent.py`):** Queries domain knowledge bases for plant pathology rules, host vulnerability stages, and chemical/biological intervention protocols.
5. **Recommendation Agent (`recommendation_agent.py`):** Evaluates risk via an XGBoost / LightGBM multi-modal fusion model, computes SHAP feature attributions, and grounds LLM natural language guidance.
6. **Notification Agent (`notification_agent.py`):** Formats operational alerts and dispatches risk warnings to farm operators.

### Layer 3: User Interface & Operations
- **Streamlit Dashboard:** Interactive web UI for farm managers to monitor real-time weather, spore counts, disease risk levels, SHAP explanations, and action recommendations.

---

## 🔄 End-to-End Data Pipeline Flow

```
[Weekly Spore Slide] ---> [Detection Agent (YOLO)] ---> Spore Vector (9 Classes)
                                                                 |
[24/7 Pi Weather Stream] -> [Weather Agent (Alignment)] -------> [Temporal Feature Matrix]
                                                                 |
                                                                 v
                                                     [Fusion Risk Model (XGBoost)]
                                                                 |
                                                                 v
                                                      [Risk Level & SHAP Matrix]
                                                                 |
                                                                 v
                                                     [Knowledge & Recommendation Agent]
                                                                 |
                                                                 v
                                                       [Farmer Alert & UI]
```

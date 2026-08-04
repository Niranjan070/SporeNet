# SporeNet Thesis Methodology Notes & Methods Draft

This document logs the formal methods paragraphs for each completed phase of the SporeNet capstone project.

---

## Section 4 — Immediate Patches & Data Model Methods

Microscopic spore trap slide sampling is conducted at fixed weekly intervals, while microclimate sensor telemetry (temperature, relative humidity, wind speed, cumulative rainfall) is logged continuously at 5–15 minute intervals via Raspberry Pi edge nodes. To prevent temporal misalignment, the join key between spore trap counts and weather telemetry is strictly defined as `exposure_start` and `exposure_end` corresponding to the field sampling interval. `lab_capture_date` is recorded solely for laboratory audit logs and is excluded from temporal join operations.

In the absence of field-verified disease outcome labels, a domain-grounded **Proxy Risk Index** is derived using a two-factor decision structure with mutual veto power. The inoculum state evaluates a composite weighted spore burden $S_{\text{burden}} = \sum_{i=1}^{9} w_i \times \text{spore\_count}_i$, where pathogenicity weights reflect literature-informed virulence across cereal pathogens (*Magnaporthe oryzae*: 1.0, *Fusarium* spp.: 0.7, *Bipolaris* spp.: 0.6, *Exserohilum* spp.: 0.5, *Alternaria* spp.: 0.45, *Curvularia* spp.: 0.4, *C. eragrostidis*: 0.3, *Fusarium* microconidia: 0.5, vegetative mycelium: 0.0). Look-forward weather forecasts evaluate upcoming blast-conducive conditions (temperature 24–28°C and relative humidity $\ge 90\%$ for $\ge 4$ hours daily). Veto rules mandate that if either inoculum burden or forecast weather pressure is low, the proxy risk level defaults to `Low`, preventing circular labeling or false infection warnings during dry intervals.

---

## Phase 2 — Detection Agent Methods (YOLOv11 Multi-Class Object Detection)

The SporeNet vision pipeline adopts a single multi-class object detection architecture based on Ultralytics YOLOv11s trained from COCO-pretrained weights (`yolo11s.pt`). The target dataset comprises 2,183 high-resolution brightfield microscopy images containing 118,241 annotated bounding boxes across 9 fungal morphotypes (Iowa State CWVQA dataset via Roboflow, CC BY 4.0). Unlike conventional plant pathology models that attempt direct disease classification from foliar images, the SporeNet vision model serves exclusively as a quantitative feature extractor, outputting a 9-element spore count vector per slide.

To resolve fine-grained spore morphology ($10\text{--}30\ \mu\text{m}$ diameter) across high-resolution captures (up to 2560 px width), training is performed at a primary resolution of `imgsz=1280` (batch size 4, 60 epochs, AdamW optimizer, mixed-precision `amp=True`). A secondary resolution ablation run at `imgsz=640` is conducted to quantify the trade-off between computational throughput and small-object detection accuracy ($mAP_s$). Evaluation metrics include $mAP_{50}$, $mAP_{50\text{-}95}$, precision, recall, and per-class performance tables, with primary quantitative validation reported on the validation split (`val`) due to the compact test set size (34 images).

---

## Phase 3 — Tabular Fusion Model & SHAP Explainability Methods

The Tabular Fusion Risk Model combines quantitative spore count vectors ($9$ species classes, total spore volume, Shannon diversity index) with 7-day look-back historical weather telemetry, 7-day look-forward forecast microclimate windows, and exponential inoculum decay states ($\text{state}_t = \text{state}_{t-1} e^{-k} + \text{count}_t, k=0.3$). Multi-modal classification is implemented using gradient boosted decision tree architectures (XGBoost and LightGBM) trained to output disease outbreak probabilities across four risk tiers (`Low`, `Medium`, `High`, `Critical`).

Model interpretability is enforced using Tree SHAP (SHapley Additive exPlanations). For each prediction, exact Shapley attribution values ($\phi_i$) are calculated across all 20 input features. The top-3 highest-contributing features per sample are extracted dynamically and passed into the downstream LLM prompt to ground natural language agronomic recommendations on empirical data drivers rather than ungrounded language generation. Model performance is benchmarked against two baseline models: a Count-Only heuristic rule (<5, 5–19, $\ge 20$ spores/slide) and a Weather-Only forecast rule. A weight sensitivity analysis perturbing literature-derived species pathogenicity weights by $\pm 20\%$ confirms stability of rank orders and risk classifications across validation samples.

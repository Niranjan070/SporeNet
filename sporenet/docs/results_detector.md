# SporeNet Phase 2 — Detection Model Results & Evaluation Report

Dataset Provenance: Iowa State CWVQA via Roboflow (CC BY 4.0)  
Total Images: 2,183 | Total Annotations: 118,241 YOLO bounding boxes | Classes: 9  

---

## 🏆 Summary Evaluation Table

| Model Architecture | Image Size (`imgsz`) | Split | mAP50 | mAP50-95 | Precision | Recall | Status / Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **YOLOv11s (Primary)** | **1280 px** | **Validation** | **0.9252** | **0.7202** | **0.907** | **0.8958** | Primary evaluation metric |
| **YOLOv11s (Primary)** | **1280 px** | **Test (34 img)** | 0.9391 | 0.7761 | 0.8564 | 0.9156 | Note: Test set small (34 img limit) |
| **YOLOv11s (Ablation)** | 640 px | Validation | 0.885 | 0.6847 | 0.8984 | 0.8539 | Resolution impact story |
| **YOLOv11s (Ablation)** | 640 px | Test (34 img) | 0.9132 | 0.7427 | 0.9 | 0.8497 | Resolution impact story |

---

## 📊 Per-Class Performance Breakdown (9 Classes)

| Class ID | Species Name | Category | Primary Target | Class Weight | Notes / Imbalance |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 0 | `magnaporthe_oryzae` | Primary Pathogen | **YES (Rice Blast)** | 1.00 | Dominant class (75.6% of box instances) |
| 1 | `alternaria` | Foliar Pathogen | No (Background) | 0.45 | Context feature |
| 2 | `bipolaris` | Brown Spot Pathogen | No (Background) | 0.60 | Context feature |
| 3 | `curvularia` | Leaf Spot Pathogen | No (Background) | 0.40 | Context feature |
| 4 | `curvularia_eragrostidis` | Minor Foliar | No (Background) | 0.30 | Rare class |
| 5 | `exserohilum` | Northern Blight Relative | No (Background) | 0.50 | Rare class |
| 6 | `fusarium` | Wilt / Blight Pathogen | No (Background) | 0.70 | Context feature |
| 7 | `fusarium_microconidie` | Microconidia Phase | No (Background) | 0.50 | Small object morphology |
| 8 | `mycelium` | Hyphae Fragments | No (Background) | 0.00 | Context indicator only |

---

## 🔍 Resolution & Small Object Analysis (mAP_s)
- **Resolution Impact:** High-resolution training at 1280px resolves tiny spore morphology (10-30 um) significantly better than standard 640px.
- **Limitation Note:** The test split contains only 34 images. Primary quantitative metrics report validation split performance (`val`).

*Report generated automatically by `scripts/eval_detector.py`.*

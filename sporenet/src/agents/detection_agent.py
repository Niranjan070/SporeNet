"""
SporeNet Detection Agent
Executes fine-tuned YOLO v8/v11 object detection on digitized brightfield slides to extract a 9-class spore feature vector.
"""

from typing import Dict, Any
from pathlib import Path

DEFAULT_SPORE_CLASSES = [
    "magnaporthe_oryzae",
    "alternaria",
    "bipolaris",
    "curvularia",
    "curvularia_eragrostidis",
    "exserohilum",
    "fusarium",
    "fusarium_microconidie",
    "mycelium"
]

class DetectionAgent:
    def __init__(self, model_path: str = None):
        if model_path is None:
            # Prefer primary trained weights if available, fallback to yolo11s.pt
            repo_root = Path(__file__).resolve().parent.parent.parent
            primary_best = repo_root / "runs" / "detect" / "runs" / "sporenet" / "primary_v11s_1280" / "weights" / "best.pt"
            if primary_best.exists():
                self.model_path = str(primary_best)
            else:
                self.model_path = str(repo_root / "yolo11s.pt")
        else:
            self.model_path = model_path
        
        self.model = None

    def _load_model(self):
        if self.model is None and Path(self.model_path).exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(self.model_path)
            except Exception as e:
                print(f"[DetectionAgent] Warning: Failed to load YOLO model from {self.model_path}: {e}")

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs YOLO object detection on image_path and extracts spore counts."""
        image_path = state.get("image_path", "")
        spore_counts = state.get("spore_counts", {cls: 0 for cls in DEFAULT_SPORE_CLASSES})

        if image_path and Path(image_path).exists():
            self._load_model()
            if self.model is not None:
                try:
                    results = self.model.predict(source=image_path, imgsz=1280, conf=0.25, verbose=False)
                    detected_counts = {cls: 0 for cls in DEFAULT_SPORE_CLASSES}
                    for r in results:
                        boxes = r.boxes
                        for c in boxes.cls:
                            cls_name = self.model.names[int(c)]
                            clean_name = cls_name.lower().replace(" ", "_")
                            if clean_name in detected_counts:
                                detected_counts[clean_name] += 1
                            elif clean_name == "curvularia_eragrostidi":
                                detected_counts["curvularia_eragrostidis"] += 1
                    spore_counts = detected_counts
                except Exception as e:
                    print(f"[DetectionAgent] Prediction failed for {image_path}: {e}")

        return {
            **state,
            "spore_counts": spore_counts,
            "detection_status": "complete"
        }


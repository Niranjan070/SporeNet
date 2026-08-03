# SporeNet Phase 2 — Detection Agent Runbook & Training Manual

This runbook guides the execution of fresh YOLOv11 detector training on your local **NVIDIA RTX 5050 GPU (8 GB VRAM)**.

---

## 🛠️ Step 1: Environment & CUDA Verification

Ensure PyTorch with CUDA 12.8 support and Ultralytics are installed:

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -U ultralytics pycocotools
```

Verify GPU detection:
```powershell
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"
```

*Expected output:* `CUDA Available: True`, `Device Name: NVIDIA GeForce RTX 5050`

---

## 🚀 Step 2: Automated Training Pipeline Execution

You can run the full automated PowerShell pipeline script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/train_detector.ps1
```

---

## 🎯 Step 3: Manual Execution Commands (Alternative)

If you prefer launching training commands manually:

### Primary Training Run (YOLOv11s @ 1280px):
```powershell
yolo detect train model=yolo11s.pt data=configs/data_merged.yaml imgsz=1280 batch=4 epochs=60 patience=20 device=0 workers=2 amp=True project=runs/sporenet name=primary_v11s_1280
```
*Note for OOM Fallback:* If Out-Of-Memory occurs, reduce batch/resolution:
`imgsz=1024 batch=2`

### Resolution Ablation Run (YOLOv11s @ 640px):
```powershell
yolo detect train model=yolo11s.pt data=configs/data_merged.yaml imgsz=640 batch=8 epochs=60 patience=20 device=0 workers=2 amp=True project=runs/sporenet name=ablation_v11s_640
```

---

## 📊 Step 4: Evaluation & Results Compilation

After training finishes, run the evaluation script to calculate mAP50, mAP50-95, and generate `docs/results_detector.md`:

```powershell
python scripts/eval_detector.py
```

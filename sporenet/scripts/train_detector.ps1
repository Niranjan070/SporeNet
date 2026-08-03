# SporeNet Phase 2 — YOLOv11 Detector Training PowerShell Script
# Target GPU: NVIDIA RTX 5050 (8 GB VRAM)
# Executes CUDA 12.8 PyTorch environment check, primary 1280px training, 640px ablation, and evaluation.

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
Write-Host "Working Directory set to: $RepoRoot" -ForegroundColor Cyan

Write-Host "============================================================" -ForegroundColor Green
Write-Host "      SporeNet Phase 2: YOLOv11 Fresh GPU Training Runner" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

# 1. Environment & CUDA Setup Check
Write-Host "`n[Step 1/4] Verifying & Installing PyTorch CUDA Environment..." -ForegroundColor Yellow
pip install --force-reinstall --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -U ultralytics pycocotools

$device = python -c "import torch; print('0' if torch.cuda.is_available() else 'cpu')"
$device = $device.Trim()
Write-Host "PyTorch Version: $(python -c 'import torch; print(torch.__version__)')"
Write-Host "CUDA Available:  $(python -c 'import torch; print(torch.cuda.is_available())')"
Write-Host "Selected Training Device: $device" -ForegroundColor Cyan

# 2. Primary YOLOv11s Training at imgsz 1280
Write-Host "`n[Step 2/4] Starting Primary Training Run (YOLOv11s @ 1280px on device=$device)..." -ForegroundColor Yellow
yolo detect train `
    model=yolo11s.pt `
    data=configs/data_merged.yaml `
    imgsz=1280 `
    batch=4 `
    epochs=60 `
    patience=20 `
    device=$device `
    workers=2 `
    amp=True `
    project=runs/sporenet `
    name=primary_v11s_1280

# 3. Resolution Ablation Run at imgsz 640
Write-Host "`n[Step 3/4] Starting Resolution Ablation Run (YOLOv11s @ 640px on device=$device)..." -ForegroundColor Yellow
yolo detect train `
    model=yolo11s.pt `
    data=configs/data_merged.yaml `
    imgsz=640 `
    batch=8 `
    epochs=60 `
    patience=20 `
    device=$device `
    workers=2 `
    amp=True `
    project=runs/sporenet `
    name=ablation_v11s_640

# 4. Evaluation & Results Compilation
Write-Host "`n[Step 4/4] Evaluating Models & Compiling Results to docs/results_detector.md..." -ForegroundColor Yellow
python scripts/eval_detector.py

Write-Host "`n[COMPLETE] Phase 2 Detection Agent Training & Evaluation Finished!" -ForegroundColor Green
Write-Host "Results saved to docs/results_detector.md" -ForegroundColor Green

#!/usr/bin/env python3
"""
SporeNet Environment Diagnostics Script
Checks availability of required dependencies for SporeNet Phase 0-4 execution.
"""

import sys
import importlib

REQUIRED_PACKAGES = [
    ("torch", "torch"),
    ("ultralytics", "ultralytics"),
    ("opencv-python", "cv2"),
    ("xgboost", "xgboost"),
    ("lightgbm", "lightgbm"),
    ("shap", "shap"),
    ("langgraph", "langgraph"),
    ("streamlit", "streamlit"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("scikit-learn", "sklearn"),
    ("pyyaml", "yaml"),
    ("scipy", "scipy"),
]

def main():
    print("=" * 60)
    print("      SporeNet Environment Diagnostics & Package Verification")
    print("=" * 60)
    
    passed = 0
    failed = 0

    for display_name, import_name in REQUIRED_PACKAGES:
        try:
            mod = importlib.import_module(import_name)
            version = getattr(mod, "__version__", "installed (no __version__)")
            print(f"  [PASS] {display_name:<20} -> Version: {version}")
            passed += 1
        except ImportError as e:
            print(f"  [FAIL] {display_name:<20} -> Missing module: {import_name} ({e})")
            failed += 1

    print("-" * 60)
    print(f"Summary: Total: {len(REQUIRED_PACKAGES)} | Passed: {passed} | Failed: {failed}")
    print("=" * 60)

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    if failed > 0:
        print("\n[!] Some dependencies are missing. Run: pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("\n[OK] Environment is fully functional for SporeNet Phase 0.")
        sys.exit(0)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Predice la categoría de un mensaje con el modelo entrenado."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "category_pipeline.joblib"
ALLOWED = {"ACCESS", "BUG", "FEATURE", "SECURITY"}


def main() -> None:
    if not MODEL_PATH.is_file():
        print(json.dumps({"error": "MODEL_NOT_TRAINED", "message": "Ejecute primero: python scripts/train_ml.py"}))
        sys.exit(2)
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        print(json.dumps({"error": "INVALID_MESSAGE", "message": "Indique un mensaje de texto."}))
        sys.exit(2)

    model = joblib.load(MODEL_PATH)
    category = str(model.predict([message])[0]).upper()
    if category not in ALLOWED:
        print(json.dumps({"error": "INVALID_PREDICTION", "message": f"Categoría inesperada: {category}"}))
        sys.exit(3)
    print(json.dumps({"category": category}, ensure_ascii=False))


if __name__ == "__main__":
    main()

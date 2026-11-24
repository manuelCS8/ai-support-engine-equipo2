#!/usr/bin/env python3
"""Entrena el clasificador ML del profe (TF-IDF + Logistic Regression) con data/tickets.csv.

Sigue el código entregado en clase:
  - 80 % entrenamiento / 20 % prueba (200 registros -> 160 / 40), estratificado.
  - Pipeline("tfidf" -> "classifier").
  - Evaluación con classification_report y confusion_matrix.
  - Predicción de ejemplo con score aproximado (predict_proba).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "tickets.csv"
MODEL_PATH = ROOT / "models" / "category_pipeline.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"

# El CSV del profe usa encabezados en español; su código usa message/category.
COLUMNS = {"Mensaje": "message", "Categoría": "category"}
ALLOWED = {"ACCESS", "BUG", "FEATURE", "SECURITY"}
TEST_SIZE = 0.2
RANDOM_STATE = 42
SAMPLE_MESSAGE = "Encontré datos de otros clientes"


def load_dataset(path: Path) -> pd.DataFrame:
    # utf-8-sig: el CSV puede traer BOM al inicio (guardado desde Excel).
    data = pd.read_csv(path, encoding="utf-8-sig")
    missing = [col for col in COLUMNS if col not in data.columns]
    if missing:
        raise SystemExit(f"El CSV debe tener las columnas {list(COLUMNS)}. Faltan: {missing}")
    data = data[list(COLUMNS)].rename(columns=COLUMNS).dropna()
    data["message"] = data["message"].astype(str).str.strip()
    data["category"] = data["category"].astype(str).str.strip().str.upper()
    data = data[data["message"] != ""]
    unknown = sorted(set(data["category"]) - ALLOWED)
    if unknown:
        raise SystemExit(f"Categorías no permitidas en el CSV: {unknown}")
    counts = data["category"].value_counts()
    if (counts < 2).any():
        raise SystemExit(f"Cada categoría necesita al menos 2 ejemplos. Conteos:\n{counts}")
    return data


def build_model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


def main() -> None:
    # La consola de Windows puede no usar UTF-8; evita errores con acentos.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    data = load_dataset(CSV_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        data["message"],
        data["category"],
        test_size=TEST_SIZE,
        stratify=data["category"],
        random_state=RANDOM_STATE,
    )
    print(f"Registros: {len(data)} | entrenamiento: {len(X_train)} | prueba: {len(X_test)}")
    print("Por categoría (entrenamiento):", y_train.value_counts().sort_index().to_dict())
    print("Por categoría (prueba):", y_test.value_counts().sort_index().to_dict())

    model = build_model()
    model.fit(X_train, y_train)

    # --- Evaluación con los registros de prueba (código del profe) ---
    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions, zero_division=0)
    labels = [str(label) for label in model.classes_]
    matrix = confusion_matrix(y_test, predictions, labels=model.classes_)
    accuracy = accuracy_score(y_test, predictions)

    print("\n=== classification_report ===")
    print(report)
    print("=== confusion_matrix (filas = real, columnas = predicho) ===")
    print("Etiquetas:", labels)
    print(matrix)

    # --- Predicción de ejemplo con score aproximado ---
    category = str(model.predict([SAMPLE_MESSAGE])[0])
    confidence = float(model.predict_proba([SAMPLE_MESSAGE]).max())
    print(f"\nMensaje de ejemplo: {SAMPLE_MESSAGE!r}")
    print("Categoría:", category)
    print("Score aproximado:", round(confidence, 3))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    errors = [
        {"message": message, "expected": expected, "predicted": predicted}
        for message, expected, predicted in zip(X_test, y_test, predictions)
        if expected != predicted
    ]
    metrics = {
        "trainedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows": int(len(data)),
        "train": int(len(X_train)),
        "test": int(len(X_test)),
        "testSize": TEST_SIZE,
        "randomState": RANDOM_STATE,
        "labels": labels,
        "accuracy": round(float(accuracy), 4),
        "confusionMatrix": matrix.tolist(),
        "classificationReport": report,
        "testErrors": errors,
        "samplePrediction": {
            "message": SAMPLE_MESSAGE,
            "category": category,
            "confidence": round(confidence, 3),
        },
        "modelPath": str(MODEL_PATH.relative_to(ROOT)).replace("\\", "/"),
    }
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nAccuracy en prueba: {accuracy:.4f} ({len(X_test) - len(errors)}/{len(X_test)})")
    print(f"Modelo guardado en {MODEL_PATH.relative_to(ROOT)}")
    print(f"Métricas en {METRICS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

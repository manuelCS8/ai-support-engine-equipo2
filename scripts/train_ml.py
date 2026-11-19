#!/usr/bin/env python3
"""Entrena el clasificador ML (TF-IDF + Logistic Regression) con data/tickets.csv."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "tickets.csv"
MODEL_PATH = ROOT / "models" / "category_pipeline.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"

REQUIRED_COLUMNS = ("Mensaje", "Categoría")
ALLOWED = {"ACCESS", "BUG", "FEATURE", "SECURITY"}


def load_dataset(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        raise SystemExit(f"El CSV debe tener columnas {REQUIRED_COLUMNS}. Faltan: {missing}")
    data = data[list(REQUIRED_COLUMNS)].dropna()
    data["Mensaje"] = data["Mensaje"].astype(str).str.strip()
    data["Categoría"] = data["Categoría"].astype(str).str.strip().str.upper()
    data = data[(data["Mensaje"] != "") & (data["Categoría"].isin(ALLOWED))]
    if data.empty:
        raise SystemExit("No hay filas válidas en el CSV.")
    counts = data["Categoría"].value_counts()
    if (counts < 2).any():
        raise SystemExit(f"Cada categoría necesita al menos 2 ejemplos. Conteos:\n{counts}")
    return data


def build_model() -> Pipeline:
    return Pipeline(
        [
            ("vectorizer", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


def main() -> None:
    data = load_dataset(CSV_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        data["Mensaje"],
        data["Categoría"],
        test_size=0.2,
        stratify=data["Categoría"],
        random_state=42,
    )
    model = build_model()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions, zero_division=0)
    print("=== classification_report ===")
    print(report)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    sample = "Alguien entró a mi cuenta sin autorización"
    sample_pred = model.predict([sample])[0]
    print(f"Ejemplo: {sample!r} -> {sample_pred}")

    metrics = {
        "rows": int(len(data)),
        "train": int(len(X_train)),
        "test": int(len(X_test)),
        "categories": sorted(data["Categoría"].unique().tolist()),
        "model_path": str(MODEL_PATH.relative_to(ROOT)).replace("\\", "/"),
        "sample_prediction": {"message": sample, "category": sample_pred},
        "classification_report": report,
    }
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Modelo guardado en {MODEL_PATH}")
    print(f"Métricas en {METRICS_PATH}")


if __name__ == "__main__":
    main()

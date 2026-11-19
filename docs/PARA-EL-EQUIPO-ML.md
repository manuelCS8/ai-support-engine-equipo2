# Para el equipo — entender el módulo ML (5 minutos)

Léelo antes de revisar el PR. No tienes que programar el modelo: sí debes poder **explicarlo**.

---

## ¿Qué pedía el profe?

Agregar al proyecto que **ya teníamos** un módulo de Machine Learning:

1. Dataset en **CSV** con 2 columnas: `Mensaje` y `Categoría`
2. Entrenar un clasificador (Pandas + sklearn)
3. **Integrarlo** al sistema (nosotros estamos en Node → Opción B: Python clasifica, Node orquesta)

No era borrar traditional ni generative. Era **sumar** un tercer camino.

---

## Los 3 motores (compáralos así)

| Modo | ¿Cómo decide? | ¿Genera texto libre? |
|---|---|---|
| `traditional` | Reglas / palabras clave que escribimos | No: respuestas fijas |
| `ml` | Aprende de ejemplos del CSV | No: predice categoría + plantilla |
| `generative` | Gemini (LLM) | Sí: responde contextual |

---

## Flujo del ML (dibujo mental)

```text
data/tickets.csv
   Mensaje,Categoría
        │
        ▼
scripts/train_ml.py     ← entrena TF-IDF + Logistic Regression
        │
        ▼
models/category_pipeline.joblib
        │
        ▼
API mode:"ml"  →  src/ml.js  →  scripts/predict_ml.py
        │
        ▼
{ category, priority, response, requiresHumanReview, mode:"ml" }
```

---

## Piezas nuevas en el repo

| Ruta | Para qué |
|---|---|
| `data/tickets.csv` | Ejemplos etiquetados (lo del profe) |
| `scripts/train_ml.py` | Entrena y guarda el modelo |
| `scripts/predict_ml.py` | Predice la categoría de un mensaje |
| `src/ml.js` | Puente Node → Python + contrato JSON |
| `requirements-ml.txt` | Librerías Python |
| `models/` | Modelo entrenado + métricas |

---

## Cómo probarlo (si quieren)

```powershell
python -m pip install -r requirements-ml.txt
npm.cmd run ml:train
npm.cmd start
```

En la UI: motor **Machine Learning · sklearn**  
O API:

```json
{ "message": "Detecté una vulnerabilidad", "mode": "ml" }
```

---

## Frases listas para el profe

**Dana**  
> Traditional usa reglas. ML aprende de un CSV con Mensaje y Categoría. Siguen siendo modos distintos en la misma API.

**Abraham**  
> Generative usa Gemini y puede redactar. ML usa TF-IDF y regresión logística: clasifica, no es un LLM.

**Emmanuel**  
> Integramos Opción B: el monolito Node acepta `mode: "ml"` y llama al script Python. Misma respuesta JSON que los otros motores.

---

## Checklist al revisar el PR

- [ ] Existe CSV con `Mensaje` y `Categoría`
- [ ] Hay script de entrenamiento sklearn
- [ ] La API acepta `mode: "ml"`
- [ ] No hay `.env` ni secretos
- [ ] Traditional y generative siguen existiendo
- [ ] README explica cómo entrenar

Si eso está → **aprueba**. Si falta algo → comenta en el PR.

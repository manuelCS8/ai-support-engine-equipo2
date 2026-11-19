# Guía ML — Equipo 2 (simple)

Emmanuel implementa el módulo de Machine Learning.  
**Dana y Abraham:** solo **revisan, aprueban el PR y entienden** para poder explicar.

Reglas iguales: **nada a `main` directo**. Todo por pull request + otro aprueba.

---

## 1. Qué vamos a hacer (para que todos entiendan)

Hoy el proyecto tiene 2 motores:

| Modo | Cómo clasifica |
|---|---|
| `traditional` | Reglas (regex) |
| `generative` | Gemini (IA generativa) |

Ahora agregamos un **tercer camino** con Machine Learning:

| Modo | Cómo clasifica |
|---|---|
| `ml` | Modelo entrenado con ejemplos (TF-IDF + Logistic Regression) |

### Idea en 4 pasos

1. Tenemos un CSV con muchos mensajes ya etiquetados (`Mensaje`, `Categoría`).
2. Entrenamos un modelo en Python (código del profe / sklearn).
3. El modelo aprende a predecir la categoría de un texto nuevo.
4. Nuestra API Node llama a ese módulo y responde con el **mismo JSON** de siempre.

### Lo que dijo el profe

- Integrar ML **dentro** del proyecto (módulo adicional).
- Dataset en **CSV** con 2 columnas: `Mensaje` y `Categoría`.
- Como estamos en **JavaScript/Node** → Opción B: Python para entrenar/predecir y Node lo consume (o adaptar la lógica).
- El proceso puede tardar (entrenamiento); la predicción de un ticket debe ser rápida.

---

## 2. Qué hace el código sklearn (explicación fácil)

```text
tickets.csv  →  divide train/test  →  TF-IDF convierte texto a números
                                    →  Logistic Regression aprende categorías
                                    →  predice categoría de un mensaje nuevo
```

| Pieza | En español |
|---|---|
| `tickets.csv` | Ejemplos etiquetados (Mensaje + Categoría) |
| `TfidfVectorizer` | Convierte texto a números (palabras importantes) |
| `LogisticRegression` | Clasificador que aprende de esos números |
| `Pipeline` | Junta vectorizador + clasificador en un solo modelo |
| `train_test_split` | Separa datos para entrenar y para medir |
| `classification_report` | Muestra qué tan bien clasifica |

**No es Gemini.** No genera texto creativo: solo **elige una categoría** según lo que aprendió.

---

## 3. Reparto de tareas (simple)

| Quién | Qué hace | Qué NO hace |
|---|---|---|
| **Emmanuel** | Implementa CSV, script Python, integración API `mode: "ml"`, abre PR | Pedir que los demás programen ML |
| **Abraham** | Revisa el PR, prueba si puede, **aprueba**, explica generative vs ML | No mergea solo; no sube `.env` |
| **Dana** | Revisa el PR, prueba traditional vs ml si puede, **aprueba**, explica reglas vs ML | No reescribe el modelo |

---

## 4. Tarea de Abraham (copiar al chat / WhatsApp)

```text
Abraham — tu tarea ML (simple):

1) Cuando Emma abra el PR del módulo ML, ábrelo en GitHub.
2) Revisa que:
   - Exista un CSV con columnas Mensaje y Categoría (o message/category según el PR).
   - Haya un script/modelo ML (Python sklearn).
   - La API acepte mode "ml" o quede documentado cómo se llama.
   - NO haya .env ni API keys en el PR.
3) Si puedes, prueba un mensaje de seguridad y uno de login.
4) Aprueba el PR si está bien (o comenta qué falta).
5) Prepárate para decir esto al profe:
   "El generativo usa Gemini y redacta respuesta. El ML usa un clasificador
   entrenado con CSV (TF-IDF + regresión logística) y predice la categoría."
```

---

## 5. Tarea de Dana (copiar al chat / WhatsApp)

```text
Dana — tu tarea ML (simple):

1) Cuando Emma abra el PR del módulo ML, ábrelo en GitHub.
2) Revisa que:
   - El motor traditional NO se rompió (sigue existiendo src/traditional.js).
   - El ML es un módulo NUEVO, no reemplaza tus reglas.
   - Hay dataset CSV (Mensaje / Categoría) como pidió el profe.
   - README o docs explica cómo correr la parte ML.
3) Aprueba el PR si está bien.
4) Prepárate para decir esto al profe:
   "Traditional usa reglas que escribimos. ML aprende de ejemplos en un CSV.
   Los dos pueden vivir en el mismo proyecto: same API, distintos modes."
```

---

## 6. Tarea de Emmanuel (implementación)

Orden sugerido:

1. Rama: `feat/manuelCS8-motor-ml` desde `main` actualizado.
2. Crear `data/tickets.csv` con columnas del profe: `Mensaje,Categoría` (mínimo varios ejemplos de ACCESS/BUG/FEATURE/SECURITY; se puede basar en `tests/cases.json`).
3. Script Python tipo el del profe: entrena Pipeline TF-IDF + LogisticRegression, imprime `classification_report`, predice un ejemplo.
4. Integrar al monolito Node (Opción B del profe), por ejemplo:
   - entrenar/guardar modelo en Python, y
   - `src/ml.js` + `mode: "ml"` en `POST /api/analyze`, **o**
   - servicio/script Python que Node invoca y mapea al contrato JSON.
5. Respuesta: misma forma `{ category, priority, response, requiresHumanReview, mode: "ml" }`.
6. Documentar en README: cómo instalar Python deps, cómo entrenar, cómo llamar `mode: "ml"`.
7. Abrir PR → Dana y Abraham revisan/aprueban → merge.

---

## 7. Frases listas para el profe (todo el equipo)

**¿Qué agregaron?**  
> Un módulo de Machine Learning supervisado: CSV con Mensaje y Categoría, entrenamos TF-IDF + Logistic Regression, y lo integramos al proyecto como otro modo de clasificación.

**¿Por qué Python si el proyecto es Node?**  
> El proyecto principal sigue en Node. Python se usa para el módulo ML (Pandas/sklearn), como indicó el profe en la opción para proyectos JavaScript: adaptar/consumir ese script desde la arquitectura actual.

**¿ML reemplaza a Gemini o a las reglas?**  
> No. Son caminos distintos: reglas, generativo y ML. Se pueden comparar.

**¿Qué es TF-IDF + Logistic Regression?**  
> TF-IDF convierte el texto en números; la regresión logística aprende a asignar categorías a partir de esos números.

---

## 8. Mensaje corto para el grupo

```text
Equipo — siguiente: módulo ML (lo que explicó el profe).

Emma implementa (CSV Mensaje/Categoría + sklearn + integrar al proyecto).
Dana y Abraham: SOLO revisar el PR, aprobar si está bien, y entender la explicación
para poder contestar al profe. No tienen que programar el modelo.

Guía: docs/GUIA-EQUIPO-ML.md
Regla: nada a main directo.
```

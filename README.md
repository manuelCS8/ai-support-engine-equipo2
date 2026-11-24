# AI Support Engine

Prototipo funcional para clasificar solicitudes de soporte con tres enfoques: reglas tradicionales, Machine Learning supervisado (TF-IDF + Logistic Regression) y un modelo generativo real mediante Gemini API. Incluye API HTTP, interfaz web, pruebas independientes y 12 casos comparativos con referencias definidas antes de la evaluación.

## Requisitos

- Node.js 22.9 o superior (verifique con `node --version`).
- Internet y una clave de Gemini API para el modo generativo. El tradicional funciona sin clave y sin internet.
- Para el modo `ml`: Python 3, dependencias de `requirements-ml.txt`, y ejecutar el entrenamiento una vez (`npm run ml:train`).
- No hay dependencias npm externas. La disponibilidad de modelos, cuotas y posibles cargos depende de la cuenta y configuración de Google AI Studio; revise su panel antes de usar la API.

## Inicio en Windows

Abra PowerShell en la carpeta `ai-support-engine`:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

1. Cree una clave en [Google AI Studio](https://aistudio.google.com/api-keys) con su cuenta de Google.
2. En el archivo `.env` recién abierto, escriba su clave después de `GEMINI_API_KEY=` y guarde. No la comparta por chat ni la suba a GitHub.
3. Mantenga `GEMINI_MODEL=gemini-3.8-flash` o indique otro modelo de texto de su cuenta que admita salidas estructuradas.
4. Inicie el servidor:

```powershell
npm.cmd start
```

Abra <http://127.0.0.1:3000>. Seleccione tradicional, Machine Learning, generativo o comparar. Después de modificar `.env`, reinicie el servidor. Las antiguas variables `OLLAMA_*` ya no se utilizan; si conserva un `.env` de la versión anterior, añada las nuevas variables de `.env.example` sin sobrescribir otras configuraciones.

Si PowerShell bloquea `npm.ps1`, utilice `npm.cmd start`, `npm.cmd test` y `npm.cmd run compare`. No es necesario cambiar la política de ejecución del equipo. Detenga el servidor con Ctrl+C.

Puede iniciar el prototipo antes de configurar Gemini. El modo tradicional estará disponible y el generativo mostrará `MISSING_API_KEY`, sin simular respuestas. La clave se utiliza sólo en el servidor, en una cabecera HTTPS destinada a Google; no se entrega a la interfaz web ni se incluye en la URL.

## Motor Machine Learning (corrección del profesor)

Integra el enfoque supervisado con el CSV del profesor: **200 registros** de dos columnas (`Mensaje`, `Categoría`), 50 por categoría. El proyecto principal sigue en Node (opción B): Python entrena/predice y la API lo consume.

```powershell
python -m pip install -r requirements-ml.txt
npm.cmd run ml:train
python scripts/predict_ml.py "Encontré datos de otros clientes"
```

`scripts/train_ml.py` sigue el código del profesor:

1. Divide el CSV con `train_test_split(test_size=0.2, stratify=category, random_state=42)`: **160 registros para entrenar y 40 para probar** (40/10 por categoría).
2. Entrena `Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2))), ("classifier", LogisticRegression(max_iter=1000))])`.
3. Evalúa los 40 de prueba con `classification_report` y `confusion_matrix` (filas = categoría real, columnas = predicha).
4. Predice un mensaje de ejemplo y muestra su **score aproximado** (`predict_proba(...).max()`).

Guarda el modelo en `models/category_pipeline.joblib` y las métricas (accuracy, matriz, reporte, errores de prueba) en `models/metrics.json`. Resultado real del último entrenamiento: **accuracy 87.5 % (35/40)**; ver [`evidence/2026-11-24-ml-entrenamiento.txt`](evidence/2026-11-24-ml-entrenamiento.txt).

`predict_ml.py` devuelve `{"category": "...", "confidence": 0.416}`. Luego, con el servidor en marcha:

```json
{ "message": "Encontré datos de otros clientes", "mode": "ml" }
```

El modelo predice `category`. Prioridad y respuesta plantilla se completan en `src/ml.js` para cumplir el mismo contrato JSON de cinco campos (el score no se agrega a la respuesta para no romper el contrato). `requiresHumanReview` es `true` si la categoría es SECURITY **o si el score es menor a 0.40** (configurable con `ML_MIN_CONFIDENCE` en `.env`). Guía corta del equipo: [`docs/PARA-EL-EQUIPO-ML.md`](docs/PARA-EL-EQUIPO-ML.md).

## Uso de la API

`POST /api/analyze` con `Content-Type: application/json`:

```json
{ "message": "No puedo iniciar sesión", "mode": "traditional" }
```

```json
{
  "category": "ACCESS",
  "priority": "MEDIUM",
  "response": "Verifique sus credenciales y utilice la recuperación de contraseña si es necesario. Si persiste el problema, contacte a soporte sin compartir contraseñas ni códigos de acceso.",
  "requiresHumanReview": false,
  "mode": "traditional"
}
```

Para consultar el modelo real, envíe `mode: "generative"`. Para Machine Learning, `mode: "ml"` (requiere entrenamiento previo). Los tres motores exportan `analyze(message)` y cumplen el mismo contrato. Las únicas categorías son ACCESS, BUG, FEATURE y SECURITY; prioridades LOW, MEDIUM, HIGH y CRITICAL. `GET /api/health` comprueba el servidor, no la disponibilidad del modelo ni de Gemini.

Ejemplo en PowerShell:

```powershell
$ticket = @{ message = 'Detecté una vulnerabilidad'; mode = 'generative' } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:3000/api/analyze -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($ticket))
```

La entrada exige message con texto de hasta 5000 caracteres y mode válido. No admite campos extra. El límite del cuerpo es 32 KiB. Errores: 400 entrada/JSON inválido, 413 tamaño excesivo, 415 contenido no JSON, 429 cuota o límite de uso de Gemini, 502 respuesta del modelo inválida/incompleta o bloqueada, 503 clave faltante/rechazada, modelo no disponible o proveedor inaccesible, 504 tiempo agotado. Los errores tienen `{ "error": { "code": "...", "message": "..." } }` y no contienen claves ni mensajes privados del proveedor.

## Pruebas y comparación real

```powershell
npm test
npm run compare
```

Las pruebas unitarias y de API no requieren clave ni conexión con Google. Los dobles de proveedor existen únicamente en pruebas; no son evidencia de IA real. `npm run compare` llama realmente a ambos motores con los 12 mensajes de `tests/cases.json`, y guarda resultados detallados, tabla CSV y conclusión de menos de 150 palabras en `results/`. La comparación envía los 12 tickets a Google y consume cuota. Si falta la clave o falla el proveedor, registra fallos explícitos, devuelve código 1 y no declara un ganador. Reejecute la comparación tras configurar una clave con cuota disponible para obtener la evidencia completa.

La exactitud exige contrato válido y coincidencia de categoría, prioridad y revisión humana. El denominador son los 12 casos por motor, incluyendo fallos. Si no hay respuestas del proveedor, su exactitud es `null`, no evaluable. La muestra incluye ambigüedad y dos intentos de manipulación; no representa una medición general de calidad en producción.

## Organización del equipo

- Dana: `src/traditional.js` y `tests/traditional.test.cjs` (conservados).
- Motor generativo: `src/generative.js`; instrucciones del sistema, esquema JSON y consulta HTTPS real a `generateContent` de Gemini.
- Motor ML: `data/tickets.csv`, `scripts/train_ml.py`, `scripts/predict_ml.py`, `src/ml.js` (integración Node ↔ Python).
- API e integración: `src/server.js`, `src/contract.js`, `public/`, `scripts/compare.js` y pruebas adicionales.

## Decisiones y límites

El motor tradicional normaliza acentos, espacios y mayúsculas. Usa precedencia SECURITY > ACCESS > BUG > FEATURE. ACCESS/BUG suelen ser MEDIUM, mejoras LOW, bloqueos y seguridad HIGH, pérdidas/fugas de datos y caídas generales CRITICAL. Sin contexto devuelve BUG/MEDIUM provisional y revisión humana. No interpreta toda negación o ironía.

El motor ML lee un CSV (`Mensaje`, `Categoría`), entrena TF-IDF + Logistic Regression y predice solo la categoría. No reemplaza a Gemini ni a las reglas: es un tercer modo. Con 200 registros los scores son bajos (en prueba, entre 0.28 y 0.65), por eso se usan como señal para pedir revisión y no como probabilidad exacta. El dataset es didáctico, no un corpus de producción; el accuracy de 40 casos no generaliza. SECURITY del ML también marca revisión humana, pero a diferencia del generativo el ML no tiene defensa por reglas: puede clasificar un incidente de seguridad como otra categoría.

El generativo separa instrucciones del sistema y ticket no confiable, solicita un esquema JSON y valida los cinco campos en la respuesta. Rechaza respuestas truncadas, bloqueadas o mal formadas. Una defensa de reglas evita que señales conocidas de seguridad se desescalen: SECURITY siempre requiere revisión y mínimo HIGH. Esta defensa no sustituye la generación: si Gemini falla, la solicitud falla. La respuesta profesional procede del modelo, cuya calidad puede variar; las reglas no detectan todos los incidentes ni garantizan resistencia absoluta a manipulación.

El servidor de la API no guarda tickets ni registra sus contenidos; el comparador sí guarda los casos y resultados de evaluación en `results/`. La interfaz usa texto seguro para mostrar respuestas, no HTML del modelo. `.env` está excluido del repositorio. La interfaz y API se sirven en localhost; el motor generativo envía el ticket a Google por internet. No envíe datos personales, contraseñas o secretos. No exponga el prototipo a internet sin autenticación, límites de uso y una revisión adicional.

Configuración en `.env`: HOST y PORT para el servidor; GEMINI_API_KEY para el generativo; GEMINI_MODEL (por defecto `gemini-3.8-flash`); GEMINI_TIMEOUT_MS (por defecto 60000, entre 1 y 300000 milisegundos); ML_MIN_CONFIDENCE (por defecto 0.4, entre 0 y 1); ML_TIMEOUT_MS y PYTHON para el motor ML. La URL del proveedor está fijada a Google para evitar que una configuración accidental envíe la clave a otro destino.

Documentación oficial: [Gemini API](https://ai.google.dev/gemini-api/docs), [salidas estructuradas](https://ai.google.dev/gemini-api/docs/structured-output), [referencia generateContent](https://ai.google.dev/api/generate-content), [modelos disponibles](https://ai.google.dev/gemini-api/docs/models).

## Equipo

| Integrante | Usuario de GitHub |
|---|---|
| Emmanuel Castro Salvador | [@manuelCS8](https://github.com/manuelCS8) |
| Abraham Cervantes Romero | [@BAM-JI](https://github.com/BAM-JI) |
| Lizbeth (Dana) | [@lizcast06](https://github.com/lizcast06) |

## Cómo trabajamos

- **Nada se sube directo a `main`.** Todo entra por pull request con la aprobación de otro integrante; la rama está protegida con una regla de GitHub.
- Reglas completas en [CONTRIBUTING.md](CONTRIBUTING.md). Evidencias de ejecución en [`evidence/`](evidence/).
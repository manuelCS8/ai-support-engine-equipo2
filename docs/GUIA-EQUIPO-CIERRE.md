# Guía de cierre — AI Support Engine (Equipo 2)

Documento interno para terminar el reto **hoy**.  
Pásalo por privado a cada integrante. Cada quien puede pegar su bloque «Prompt para Cursor» en su chat y ejecutarlo.

**Repo:** https://github.com/manuelCS8/ai-support-engine-equipo2  
**Rama base:** `main` (solo se actualiza por pull request)  
**Stack:** Node.js ≥ 22.9, sin dependencias npm, Gemini API real (no Ollama)

| Integrante | GitHub | Rol en el cierre |
|---|---|---|
| Emmanuel Castro Salvador | @manuelCS8 | Coordinación + API/evidencias de servidor + merge final |
| Abraham Cervantes Romero | @BAM-JI | Clave Gemini + motor generativo + `npm run compare` |
| Lizbeth (Dana) | @lizcast06 | Motor tradicional + evidencias traditional + revisión de PRs |

---

## 1. Qué es el proyecto (para explicar al profe)

### Problema
Una empresa recibe tickets de soporte. Hoy una persona lee cada mensaje, decide de qué se trata, asigna prioridad y responde. Nosotros automatizamos esa clasificación con **dos motores** que cumplen el **mismo contrato JSON**.

### Contrato de respuesta (ambos motores)

```json
{
  "category": "ACCESS | BUG | FEATURE | SECURITY",
  "priority": "LOW | MEDIUM | HIGH | CRITICAL",
  "response": "texto de respuesta",
  "requiresHumanReview": true o false,
  "mode": "traditional | generative"
}
```

### Endpoint obligatorio

`POST /api/analyze`

```json
{ "message": "No puedo iniciar sesión", "mode": "generative" }
```

### Los dos enfoques

1. **Motor tradicional (`src/traditional.js`)**  
   Reglas / expresiones regulares. Sin IA generativa.  
   Normaliza texto (acentos, mayúsculas). Precedencia: **SECURITY > ACCESS > BUG > FEATURE**.  
   Respuestas **predeterminadas**. SECURITY siempre marca revisión humana y al menos HIGH.  
   Si no reconoce nada → BUG/MEDIUM provisional + revisión humana.

2. **Motor generativo (`src/generative.js`)**  
   Llama de verdad a **Gemini** (`generateContent` por HTTPS).  
   Interpreta el ticket, clasifica, prioriza y **genera** una respuesta profesional.  
   Valida el JSON. Si el modelo falla o responde mal → error HTTP (no se inventa respuesta).  
   Hay una **defensa de seguridad** con las reglas del tradicional: no deja bajar un incidente SECURITY aunque el prompt diga «prioridad baja».

### API y seguridad (`src/server.js` + `src/contract.js`)

- Valida `message` y `mode`.
- Rechaza campos extra, JSON inválido, cuerpo > 32 KiB.
- Errores tipados (400, 413, 415, 429, 502, 503, 504) sin filtrar la API key.
- SECURITY → `requiresHumanReview: true`.
- `.env` nunca se sube a GitHub (solo `.env.example`).

### Pruebas comparativas

- 12 casos en `tests/cases.json` (más de los 10 pedidos): normales, ambiguos y **2 intentos de manipulación**.
- `npm run compare` corre ambos motores y genera en `results/`:
  - `comparison.json`
  - `comparison.csv`
  - `conclusion.md` (≤ 150 palabras)

### Frases útiles si pregunta el profe

- «No simulamos el generativo: sin `GEMINI_API_KEY` falla con `MISSING_API_KEY`.»
- «Los mocks solo existen en `tests/`; no son evidencia del motor real.»
- «SECURITY siempre va a revisión humana; intentos tipo jailbreak deben seguir en SECURITY/HIGH o CRITICAL.»
- «Misma forma de respuesta en traditional y generative; solo cambia cómo se obtiene.»
- «Nada entra a `main` sin pull request y aprobación de otro integrante.»

### Qué ya está hecho en el código

- Motores traditional + generative (Gemini real)
- API + interfaz web (`public/`)
- Validaciones y manejo de errores
- 12 casos de referencia + script `compare`
- README, CONTRIBUTING, estructura `evidence/` y `results/`
- Pruebas automatizadas: `npm test` → 53 tests OK

### Qué falta para entregar el reto

Solo las **evidencias reales** que pide el PDF:

1. Evidencia de ejecución de ambos motores  
2. Evidencia de ≥ 10 casos comparativos  
3. Tabla de resultados + conclusión ≤ 150 palabras  

Eso se genera corriendo comandos de verdad y subiendo archivos a `evidence/` y `results/` por PR.

---

## 2. Reglas del equipo (obligatorias)

1. **Nada se sube directo a `main`.** Ni push, ni commits en `main` local para “arreglar rápido”.
2. Flujo siempre:
   ```powershell
   git checkout main
   git pull origin main
   git checkout -b tipo/usuario-descripcion
   ```
   Tipos: `feat/`, `fix/`, `test/`, `docs/`, `chore/`
3. Abrir **pull request hacia `main`**.
4. **Otro integrante** revisa y aprueba. Nadie aprueba su propio PR.
5. Merge con **Create a merge commit** (no squash / no rebase).
6. Sin force push. Sin borrar historial remoto.
7. Cada quien committea con **su** cuenta Git (`user.name` / `user.email`).
8. **`.env` nunca se commitea.** Antes de cada commit: `git status` y confirmar que `.env` no aparece.
9. Evidencias = salidas **reales** de comandos. No inventar ni editar a mano resultados de Gemini.
10. Datos ficticios solamente. Sin contraseñas, correos reales ni la API key en capturas/archivos.
11. Si usaron IA de apoyo, cada uno debe poder explicar su parte.
12. Antes de abrir PR: `npm.cmd test` debe pasar.

Detalle completo: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 3. Checklist de entrega (PDF)

Marcar cuando esté en el repo (vía PR mergeado):

- [ ] Repo con código + instrucciones en README
- [ ] Evidencia motor **traditional** (`evidence/AAAA-MM-DD-api-traditional.txt`)
- [ ] Evidencia motor **generative** (`evidence/AAAA-MM-DD-api-generative.txt`)
- [ ] Evidencia `npm test` (`evidence/AAAA-MM-DD-npm-test.txt`)
- [ ] Comparación ≥ 10 casos (`results/comparison.json` + `.csv` y/o copia en `evidence/`)
- [ ] Conclusión ≤ 150 palabras (`results/conclusion.md`)
- [ ] Ningún secreto en GitHub
- [ ] Todos pueden explicar su módulo

---

## 4. Orden de trabajo (importante)

```text
1) Abraham configura .env con GEMINI_API_KEY y verifica generative
2) Dana captura evidence traditional + npm test (puede en paralelo si no toca .env)
3) Abraham corre npm run compare → results/
4) Emmanuel captura evidence generative + arma/revisa PR final de evidencias
5) Dana o Emmanuel aprueba el PR del otro → merge a main
```

**Abraham debe terminar el paso 1 antes del compare.** Sin clave válida, `npm run compare` falla y no hay evidencia generativa.

---

## 5. Trabajo por integrante + prompt para Cursor

Copia **solo tu sección** y pégala en tu chat de Cursor (modo Agent), con el repo abierto en `ai-support-engine-equipo2`.

---

### A) Lizbeth (Dana) — Motor tradicional + evidencias traditional

**Qué te toca**

1. Revisar/entender `src/traditional.js` y `tests/traditional.test.cjs` (es tu módulo).
2. Crear rama `chore/lizcast06-evidencias-traditional`.
3. Guardar evidencias reales en `evidence/`:
   - `AAAA-MM-DD-npm-test.txt` (salida completa de `npm.cmd test`)
   - `AAAA-MM-DD-api-traditional.txt` (respuesta real de `POST /api/analyze` con `mode: "traditional"`)
4. Incluir al inicio de cada archivo: fecha, `git rev-parse HEAD`, comando usado.
5. Abrir PR → que Emmanuel o Abraham aprueben.
6. Revisar/aprobar el PR de evidencias generativas de Abraham (cuando exista).

**Comandos útiles**

```powershell
git checkout main
git pull origin main
git checkout -b chore/lizcast06-evidencias-traditional

npm.cmd test | Tee-Object -FilePath evidence\2026-11-17-npm-test.txt

# Terminal 1
npm.cmd start

# Terminal 2
$ticket = @{ message = 'No puedo iniciar sesión'; mode = 'traditional' } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:3000/api/analyze -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($ticket)) | ConvertTo-Json -Depth 5 | Tee-Object -FilePath evidence\2026-11-17-api-traditional.txt
```

**Prompt para Cursor (Dana) — copiar y pegar**

```text
Estoy en el repo ai-support-engine-equipo2. Soy Lizbeth (Dana), dueña del motor tradicional.

REGLAS:
- Nunca hagas push ni commits directos a main.
- Trabaja en la rama chore/lizcast06-evidencias-traditional creada desde main actualizado.
- No toques .env ni pidas/subas GEMINI_API_KEY.
- No edites a mano resultados: las evidencias deben ser salidas reales de comandos.
- No hagas commit de .env.

TAREAS:
1) Actualiza main, crea la rama chore/lizcast06-evidencias-traditional.
2) Ejecuta npm.cmd test y guarda la salida completa en evidence/ con nombre AAAA-MM-DD-npm-test.txt. Al inicio del archivo escribe fecha ISO, commit (git rev-parse HEAD) y el comando.
3) Arranca el servidor (npm.cmd start) y haz POST /api/analyze con mode traditional y message "No puedo iniciar sesión". Guarda la respuesta JSON real en evidence/AAAA-MM-DD-api-traditional.txt con el mismo encabezado (fecha, commit, comando).
4) Verifica que git status no muestre .env.
5) Haz commit solo de los archivos de evidence/ con mensaje claro.
6) Push de la rama y abre PR hacia main con gh, explicando cómo se generaron las evidencias. NO hagas merge.
7) Al final dime: archivos creados, URL del PR, y un resumen de 8-10 líneas de cómo funciona traditional.js por si pregunta el profe (categorías, precedencia, prioridades, SECURITY, casos ambiguos).
```

**Si el profe te pregunta (Dana)**

- Clasificas con reglas/regex, no con LLM.
- Precedencia SECURITY > ACCESS > BUG > FEATURE.
- SECURITY → revisión humana + mínimo HIGH.
- CRITICAL ante fuga/pérdida de datos, caída total, etc.
- Mensaje vacío o sin texto → error; sin match → BUG/MEDIUM + review.

---

### B) Abraham — Gemini + comparación real

**Qué te toca**

1. Crear clave en https://aistudio.google.com/api-keys (cuenta Google del equipo/propia).
2. Configurar `.env` local (NUNCA subirla):
   ```powershell
   if (!(Test-Path .env)) { Copy-Item .env.example .env }
   notepad .env
   ```
   Dejar:
   ```env
   GEMINI_API_KEY=tu_clave_aqui
   GEMINI_MODEL=gemini-3.8-flash
   ```
   Si ese modelo falla en tu cuenta, prueba otro de texto disponible en AI Studio y documenta cuál usaste.
3. Probar generative de verdad (UI o API).
4. Correr `npm.cmd run compare` y generar `results/comparison.json`, `comparison.csv`, `conclusion.md`.
5. Guardar también copia/evidencia en `evidence/AAAA-MM-DD-comparacion.*` y `AAAA-MM-DD-api-generative.txt` (o coordinar generative evidence con Emmanuel).
6. Rama: `chore/BAM-JI-evidencias-comparacion`
7. PR → que Dana o Emmanuel aprueben.

**Prompt para Cursor (Abraham) — copiar y pegar**

```text
Estoy en el repo ai-support-engine-equipo2. Soy Abraham. Me toca el motor generativo con Gemini y la comparación real.

REGLAS:
- Nunca push/commit a main. Usa rama chore/BAM-JI-evidencias-comparacion desde main actualizado.
- La API key va SOLO en .env local. .env está en .gitignore. Si aparece en git status, DETENTE.
- No inventes respuestas generativas. Si falla Gemini, guarda el error real como evidencia honesta y no declares ganador falso.
- No hagas merge a main.

TAREAS:
1) Confirma Node >= 22.9. Si no existe .env, copia .env.example a .env.
2) NO escribas tú la clave en el chat. Pídeme que yo la pegue en .env con notepad y confirme cuando esté lista. Cuando yo confirme:
3) Arranca el servidor y prueba POST /api/analyze con mode generative y un mensaje de login. Guarda evidencia real en evidence/AAAA-MM-DD-api-generative.txt (fecha, git rev-parse HEAD, comando, JSON o error real).
4) Ejecuta npm.cmd run compare. Debe crear results/comparison.json, comparison.csv y conclusion.md.
5) Copia también a evidence/ una versión fechada de la comparación/conclusión (sin secretos).
6) Revisa conclusion.md: máximo 150 palabras, indica qué motor fue mejor y por qué (o que la evaluación está incompleta si generative falló).
7) npm.cmd test debe seguir pasando.
8) Commit SOLO de evidence/ y results/ (nunca .env). Push + gh pr create hacia main. No mergees.
9) Al final: URL del PR, % de aciertos traditional vs generative, y explicación corta de generative.js (llamada real a Gemini, schema JSON, validación, defensa SECURITY, errores sin simular).
```

**Si el profe te pregunta (Abraham)**

- Se llama a Google Gemini por HTTPS con la key en cabecera `x-goog-api-key`, no en el navegador.
- Pedimos JSON con esquema; validamos los 5 campos.
- Si el modelo miente en seguridad, la defensa con reglas corrige categoría/prioridad mínima.
- No hay respuestas hardcodeadas del generativo: sin clave o sin cuota → error explícito.

---

### C) Emmanuel — Coordinación + API + PR final

**Qué te toca**

1. Asegurar que `main` esté limpio y el README siga siendo usable.
2. Ayudar a capturar evidencia generative si Abraham no la subió, o revisar la de él.
3. Revisar PRs de Dana y Abraham (aprobar si están bien).
4. Si hace falta un PR de cierre `chore/manuelCS8-evidencias-cierre` que unifique:
   - checklist de `evidence/README.md` cumplido
   - `results/` completo
   - que no falte conclusión ≤ 150 palabras
5. Verificar en GitHub que **no** esté `.env` ni la key en ningún archivo.
6. Preparar al equipo: cada uno explica su módulo 1 minuto.

**Prompt para Cursor (Emmanuel) — copiar y pegar**

```text
Estoy en el repo ai-support-engine-equipo2. Soy Emmanuel (manuelCS8), coordinador del cierre.

REGLAS del equipo:
- Nada a main sin PR + aprobación de otro.
- No force push. No squash/rebase al merge.
- Nunca commit de .env ni secretos.
- Evidencias = salidas reales.

TAREAS:
1) Revisa el estado del repo vs el PDF del reto: motores, API, validaciones, 10+ casos, evidencias.
2) Lista qué archivos ya existen en evidence/ y results/ y qué falta exactamente.
3) Si falta evidencia de API generative o traditional, genérala en rama chore/manuelCS8-evidencias-cierre (sin hardcodear). Si falta compare, NO inventes results: indica que Abraham debe correr npm run compare con clave.
4) Si results/ ya está, verifica conclusion.md ≤ 150 palabras y que comparison.csv/json existan.
5) Abre o actualiza PR de lo que falte. No mergees tu propio PR.
6) Dame un checklist final de entrega listo para marcar, y un guion de 60 segundos por integrante para defender el proyecto ante el profe (Dana traditional, Abraham generative, yo API/seguridad/comparación).
7) Confirma con git status / git log / búsqueda que no hay secretos trackeados.
```

**Si el profe te pregunta (Emmanuel)**

- `POST /api/analyze` valida entrada, enruta por `mode`, valida contrato de salida.
- Errores controlados; la key nunca sale al cliente.
- Comparación: 12 casos con referencia previa; se mide categoría + prioridad + review + formato.
- Porcentaje de aciertos por motor; conclusión técnica breve.

---

## 6. Cómo generar evidencias (recetas PowerShell)

### Encabezado sugerido para cada `.txt`

```text
fecha: 2026-11-17T...
commit: <pegar salida de git rev-parse HEAD>
comando: <comando exacto>
---
<salida real>
```

### npm test

```powershell
npm.cmd test 2>&1 | Tee-Object -FilePath evidence\2026-11-17-npm-test.txt
```

### API traditional / generative

```powershell
npm.cmd start
```

En otra terminal:

```powershell
$trad = @{ message = 'No puedo iniciar sesión'; mode = 'traditional' } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:3000/api/analyze -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($trad)) | ConvertTo-Json -Depth 5 | Tee-Object evidence\2026-11-17-api-traditional.txt

$gen = @{ message = 'Detecté una vulnerabilidad'; mode = 'generative' } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:3000/api/analyze -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($gen)) | ConvertTo-Json -Depth 5 | Tee-Object evidence\2026-11-17-api-generative.txt
```

### Comparación (12 casos reales)

```powershell
npm.cmd run compare
# Genera results/comparison.json, comparison.csv, conclusion.md
```

Opcional: copiar a `evidence/` con fecha para el entregable.

---

## 7. Criterios del PDF (para no olvidar el peso)

| Criterio | Valor | ¿Código listo? | ¿Evidencia lista? |
|---|---|---|---|
| Motor tradicional funcional | 25% | Sí | Falta capturar |
| Integración real IA generativa | 30% | Sí | Falta corrida con clave |
| Validaciones, errores y seguridad | 20% | Sí | Cubierto por tests + API |
| Pruebas comparativas y resultados | 15% | Script listo | Falta `npm run compare` |
| Repositorio y evidencias | 10% | Repo listo | Falta subir `evidence/` + `results/` |

---

## 8. Definición de “terminado”

El proyecto está cerrado cuando:

1. `main` tiene código + README (ya).
2. `evidence/` tiene salidas reales de test + API traditional + API generative.
3. `results/` tiene JSON, CSV y conclusión ≤ 150 palabras de una corrida real con Gemini.
4. Todo entró por PRs aprobados por otro integrante.
5. No hay secretos en el remoto.
6. Los tres pueden explicar su parte sin leer el chat.

---

## 9. Mensaje corto para WhatsApp / privado

Puedes copiar esto al grupo:

```text
Chicos: el código del reto YA está. Falta SOLO evidencias reales.

Regla de oro: NADA a main directo. Todo por PR + otro aprueba.

Dana → evidence de npm test + API traditional (rama chore/lizcast06-evidencias-traditional)
Abraham → .env con Gemini + API generative + npm run compare (results/) (rama chore/BAM-JI-evidencias-comparacion)
Emma → coordina, revisa PRs, cierra lo que falte (chore/manuelCS8-evidencias-cierre)

Les paso la guía docs/GUIA-EQUIPO-CIERRE.md: ahí está la explicación del proyecto para el profe y el prompt listo para pegar en Cursor de cada quien.
```

---

*Documento generado para el cierre del Reto práctico: AI Support Engine. No sustituye el PDF del reto; lo opera.*

'use strict';

const { spawn } = require('node:child_process');
const path = require('node:path');
const { validateMessage, validResult } = require('./contract');

const ROOT = path.join(__dirname, '..');
const PREDICT_SCRIPT = path.join(ROOT, 'scripts', 'predict_ml.py');

const RESPONSES = {
  ACCESS: 'Verifique sus credenciales y utilice la recuperación de contraseña si es necesario. Si persiste el problema, contacte a soporte sin compartir contraseñas ni códigos de acceso.',
  BUG: 'Comparta los pasos para reproducir el problema, el resultado esperado y el mensaje de error, sin incluir datos sensibles.',
  FEATURE: 'Gracias por su propuesta. Describa la funcionalidad y el beneficio esperado para que el equipo pueda evaluarla.',
  SECURITY: 'Su reporte requiere revisión del equipo de seguridad. No comparta credenciales ni datos sensibles; conserve la evidencia para entregarla por un canal seguro.',
};

const CRITICAL = /\b(perdida de datos|data loss|ransomware|filtracion|fuga de datos|datos expuestos|data leak|brecha|breach|sistema caido|servicio caido|system down|todos los usuarios|all users)\b/i;
const HIGH = /\b(urgente|urgent|bloqueante|blocker|no puedo trabajar|impide trabajar|cuenta bloqueada|account locked|produccion|production)\b/i;

class MlError extends Error {
  constructor(code, message, status = 503) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

function priorityFor(category, message) {
  if (CRITICAL.test(message) || (category === 'SECURITY' && /\b(fuga|leak|ransomware|brecha|breach)\b/i.test(message))) {
    return 'CRITICAL';
  }
  if (category === 'SECURITY' || HIGH.test(message)) return 'HIGH';
  if (category === 'FEATURE') return 'LOW';
  if (/\b(tipografico|typo|cosmetico|cosmetic|detalle visual)\b/i.test(message)) return 'LOW';
  return 'MEDIUM';
}

function runPredict(message, { pythonPath = process.env.PYTHON || 'python', timeoutMs = Number(process.env.ML_TIMEOUT_MS || 60000) } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(pythonPath, [PREDICT_SCRIPT, message], {
      cwd: ROOT,
      windowsHide: true,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      child.kill();
      reject(new MlError('ML_TIMEOUT', 'El clasificador ML excedió el tiempo de respuesta.', 504));
    }, timeoutMs);
    child.stdout.on('data', chunk => { stdout += chunk; });
    child.stderr.on('data', chunk => { stderr += chunk; });
    child.on('error', error => {
      clearTimeout(timer);
      if (error.code === 'ENOENT') {
        reject(new MlError('PYTHON_NOT_FOUND', 'No se encontró Python. Instale Python 3 y defina PYTHON si hace falta.', 503));
        return;
      }
      reject(new MlError('ML_SPAWN_ERROR', 'No se pudo iniciar el clasificador ML.', 503));
    });
    child.on('close', code => {
      clearTimeout(timer);
      let parsed;
      try { parsed = JSON.parse(stdout.trim().split(/\r?\n/).filter(Boolean).at(-1) || ''); }
      catch {
        reject(new MlError('ML_INVALID_OUTPUT', 'El clasificador ML no devolvió JSON válido.', 502));
        return;
      }
      if (parsed.error) {
        const status = parsed.error === 'MODEL_NOT_TRAINED' ? 503 : 502;
        reject(new MlError(parsed.error, parsed.message || 'Error del clasificador ML.', status));
        return;
      }
      if (code !== 0) {
        reject(new MlError('ML_PROCESS_ERROR', stderr.trim() || 'El proceso ML terminó con error.', 503));
        return;
      }
      if (!parsed.category) {
        reject(new MlError('ML_INVALID_OUTPUT', 'El clasificador ML no devolvió categoría.', 502));
        return;
      }
      resolve(parsed.category);
    });
  });
}

function createAnalyzer(options = {}) {
  const predict = options.predictImpl || runPredict;
  return async function analyze(message) {
    validateMessage(message);
    const category = await predict(message, options);
    const result = {
      category,
      priority: priorityFor(category, message),
      response: RESPONSES[category],
      requiresHumanReview: category === 'SECURITY',
      mode: 'ml',
    };
    if (!validResult(result, 'ml')) {
      throw new MlError('INVALID_ENGINE_OUTPUT', 'El motor ML no cumplió el contrato.', 502);
    }
    return result;
  };
}

async function analyze(message) {
  return createAnalyzer()(message);
}

module.exports = { analyze, createAnalyzer, runPredict, MlError, priorityFor };

'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { once } = require('node:events');
const { createServer } = require('../src/server');
const { createAnalyzer, MlError, priorityFor } = require('../src/ml');

async function running(t, options = {}) {
  const server = createServer(options);
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(() => { server.closeAllConnections(); server.close(); });
  return `http://127.0.0.1:${server.address().port}`;
}

test('priorityFor marca SECURITY en revisión y eleva CRITICAL por fuga', () => {
  assert.equal(priorityFor('SECURITY', 'Detecté una vulnerabilidad'), 'HIGH');
  assert.equal(priorityFor('SECURITY', 'Hay una fuga de datos'), 'CRITICAL');
  assert.equal(priorityFor('FEATURE', 'Agregar modo oscuro'), 'LOW');
  assert.equal(priorityFor('ACCESS', 'No puedo iniciar sesión'), 'MEDIUM');
});

test('createAnalyzer arma el contrato ml con la categoría predicha', async () => {
  const analyze = createAnalyzer({ predictImpl: async () => 'ACCESS' });
  const result = await analyze('No puedo iniciar sesión');
  assert.equal(result.mode, 'ml');
  assert.equal(result.category, 'ACCESS');
  assert.equal(result.priority, 'MEDIUM');
  assert.equal(result.requiresHumanReview, false);
  assert.ok(result.response.length > 0);
});

test('SECURITY del ML exige revisión humana', async () => {
  const analyze = createAnalyzer({ predictImpl: async () => 'SECURITY' });
  const result = await analyze('Detecté una vulnerabilidad');
  assert.equal(result.requiresHumanReview, true);
  assert.equal(result.priority, 'HIGH');
});

test('POST mode ml enruta al motor inyectado', async t => {
  const expected = {
    category: 'BUG', priority: 'MEDIUM', response: 'Reproducir el error.', requiresHumanReview: false, mode: 'ml',
  };
  const base = await running(t, { mlAnalyze: async text => { assert.match(text, /error/i); return expected; } });
  const response = await fetch(`${base}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hay un error al guardar', mode: 'ml' }),
  });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), expected);
});

test('Propaga MlError sin filtrar detalles internos', async t => {
  const base = await running(t, {
    mlAnalyze: async () => { throw new MlError('MODEL_NOT_TRAINED', 'Ejecute train_ml.py', 503); },
  });
  const response = await fetch(`${base}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'No puedo iniciar sesión', mode: 'ml' }),
  });
  assert.equal(response.status, 503);
  assert.equal((await response.json()).error.code, 'MODEL_NOT_TRAINED');
});

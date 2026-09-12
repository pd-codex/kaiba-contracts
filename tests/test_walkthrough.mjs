import test from 'node:test';
import assert from 'node:assert/strict';
import {steps, initialState, evaluate, advance, visit, reconcile} from '../website/walkthrough-model.mjs';

const publicationId = 'publication-fixture-001';
function reach(scenario, id) {
  let state = initialState(scenario);
  while (steps[state.step].id !== id) state = advance(evaluate(state, publicationId));
  return state;
}

test('future steps cannot bypass an unevaluated handoff', () => {
  const state = initialState();
  assert.equal(advance(state), state);
  assert.equal(visit(state, 7), state);
});

test('reviewed route accepts once and never claims fulfillment', () => {
  let state = reach('reviewed', 'accept');
  assert.equal(state.acceptanceCount, 0);
  state = evaluate(state, publicationId);
  assert.equal(state.publication, publicationId);
  assert.equal(state.acceptanceCount, 1);
  assert.equal(evaluate(state, publicationId), state);
  state = evaluate(advance(state), publicationId);
  assert.match(state.results.fulfill.message, /unproven/);
  assert.equal(state.acceptanceCount, 1);
});

test('valid development evidence stays blocked at identity, including after revisiting', () => {
  let state = evaluate(reach('development', 'identity'), publicationId);
  assert.equal(state.results.observe.kind, 'passed');
  assert.equal(state.results.identity.kind, 'blocked');
  assert.equal(advance(state), state);
  assert.equal(visit(state, 7), state);
  state = advance(visit(state, 0));
  assert.equal(state.results.identity.kind, 'blocked');
  assert.equal(state.publication, null);
});

test('revision conflict rejects the entire acceptance and creates no work', () => {
  const state = evaluate(reach('conflict', 'accept'), publicationId);
  assert.equal(state.results.accept.kind, 'blocked');
  assert.equal(state.acceptanceCount, 0);
  assert.equal(state.publication, null);
  assert.equal(advance(state), state);
});

test('lost reply leaves caller unknown; identical reconciliation preserves one acceptance', () => {
  let state = evaluate(reach('lost', 'accept'), publicationId);
  assert.equal(state.results.accept.kind, 'unknown');
  assert.equal(state.acceptanceCount, 1);
  assert.equal(advance(state), state);
  state = reconcile(state);
  assert.equal(state.results.accept.kind, 'passed');
  assert.equal(state.publication, publicationId);
  assert.equal(state.acceptanceCount, 1);
  assert.equal(state.retries, 1);
  assert.equal(reconcile(state), state);
  assert.equal(advance(state).step, 8);
});

test('restart creates an empty, isolated scenario', () => {
  const completed = evaluate(reach('reviewed', 'accept'), publicationId);
  const fresh = initialState('development');
  assert.equal(completed.acceptanceCount, 1);
  assert.deepEqual(fresh.results, {});
  assert.equal(fresh.acceptanceCount, 0);
  assert.equal(fresh.step, 0);
  assert.throws(() => initialState('unsupported'));
});

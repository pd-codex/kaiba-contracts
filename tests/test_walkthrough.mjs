import test from 'node:test';
import assert from 'node:assert/strict';
import {steps, initialState, evaluate, advance, visit, reconcile} from '../website/walkthrough-model.mjs';
import {deviceTransition} from '../website/device-transitions.mjs';

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

test('device exits become the next entries; an unevaluated step has no exit', () => {
  let state = initialState();
  assert.equal(deviceTransition(state).exit, null);
  for (let index = 0; index < steps.length - 1; index++) {
    state = evaluate(state, publicationId);
    const exit = deviceTransition(state).exit;
    state = advance(state);
    assert.deepEqual(deviceTransition(state).entry, exit);
  }
});

test('authoring, review and acceptance never imply device assignment or runtime changes', () => {
  let state = reach('reviewed', 'components');
  const before = deviceTransition(state).entry;
  state = evaluate(state, publicationId);
  assert.deepEqual(deviceTransition(state).entry, deviceTransition(state).exit);
  for (let index = 4; index < steps.length; index++) {
    state = evaluate(advance(state), publicationId);
    const exit = deviceTransition(state).exit;
    assert.equal(exit.physical, before.physical);
    assert.equal(exit.desired, before.desired);
    assert.equal(exit.running, before.running);
  }
  assert.match(deviceTransition(state).exit.intent, /Publication accepted/);
  assert.deepEqual(deviceTransition(state).changed, []);
});

test('development gate preserves entry state and never claims activation operations', () => {
  const state = evaluate(reach('development', 'identity'), publicationId);
  const transition = deviceTransition(state);
  assert.deepEqual(transition.entry, transition.exit);
  assert.deepEqual(transition.changed, []);
  assert.match(transition.operations.join(' '), /do not activate/);
});

test('concurrent desired-state change is explicit and survives rejected publication', () => {
  const state = evaluate(reach('conflict', 'accept'), publicationId);
  const transition = deviceTransition(state);
  assert.match(transition.event, /another assignment/);
  assert.match(transition.entry.desired, /Revision 1/);
  assert.equal(transition.exit.desired, transition.entry.desired);
  assert.equal(transition.exit.running, transition.entry.running);
  assert.match(transition.exit.intent, /rejected/);
});

test('reconciling a lost reply changes caller knowledge, not the device exit state', () => {
  const unknown = evaluate(reach('lost', 'accept'), publicationId);
  const known = reconcile(unknown);
  assert.deepEqual(deviceTransition(unknown).exit, deviceTransition(known).exit);
  assert.match(deviceTransition(known).operations.at(-1), /no second acceptance/);
  assert.deepEqual(deviceTransition(visit(known, 0)).entry, deviceTransition(initialState()).entry);
});

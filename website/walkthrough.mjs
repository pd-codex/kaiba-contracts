import data from './walkthrough-data.mjs';
import {scenarios, steps, initialState, unlockedStep, visit, advance, evaluate, reconcile} from './walkthrough-model.mjs';

const $ = id => document.getElementById(id);
let state = initialState();

function list(element, values) {
  element.replaceChildren(...values.map(value => {
    const li = document.createElement('li'); li.textContent = value; return li;
  }));
}

function definitionList(element, values) {
  element.replaceChildren(...values.map(([label, value]) => {
    const div = document.createElement('div');
    const dt = document.createElement('dt'); dt.textContent = label;
    const dd = document.createElement('dd'); dd.textContent = String(value);
    div.append(dt, dd); return div;
  }));
}

function inspect(step, result) {
  const fixtures = data.fixtures;
  const binding = fixtures['binding-active'];
  const request = fixtures['publish-request'];
  const target = request.targets[0];
  const accepted = state.publication && result?.kind === 'passed';
  const fixtureNames = {
    observe: state.scenario === 'development' ? 'provisioning-development' : 'provisioning-production-candidate',
    identity: result?.kind === 'passed' ? 'binding-active' : 'binding-staged',
    request: 'publish-request', accept: 'publication',
  };
  let name = fixtureNames[step.id];
  if (step.id === 'identity' && state.scenario === 'development') name = null;
  if (step.id === 'accept' && !accepted) name = null;
  const record = name ? fixtures[name] : null;
  let summary;
  if (step.id === 'observe') {
    summary = [['Record / revision', `${record.record_id} / ${record.revision}`], ['Source state', record.source.state], ['Production ready', record.readiness.production_ready], ['Enrollment ready', record.readiness.enrollment_ready]];
  } else if (step.id === 'identity') {
    summary = record ? [['Device / instance', `${record.logical_device_id} / ${record.instance_id}`], ['Storage generation', record.storage_generation], ['Tuple state / revision', `${record.state} / ${record.revision}`], ['Credential', `${record.credential.slot} · key generation ${record.credential.key_generation}`]] : [['Output', 'No production binding'], ['Reason', 'Development posture cannot pass production identity activation']];
  } else if (step.id === 'admit') {
    summary = [['Exact instance', binding.instance_id], ['Participation', 'Hypothetically eligible after current policy checks'], ['Required context', 'Tenant, domain, platform capabilities, restrictions, decision and freshness']];
  } else if (step.id === 'components') {
    summary = [['Shared consumers', 'Flow editor and resolver'], ['Required definition', 'Typed ports, field schemas, permissions, compatibility and health'], ['Versioning', 'Immutable, pinned component definitions']];
  } else if (step.id === 'author') {
    summary = [['Intent', 'Immutable graph with typed connections'], ['Pinned inputs', 'Component versions and authoring provenance'], ['Secrets', 'Scoped references only; never secret values']];
  } else if (step.id === 'resolve') {
    summary = [['Fixture plan reference', `${request.plan_ref.record_id} / revision ${request.plan_ref.revision}`], ['Eligible instance', `${target.instance_id} / storage generation ${target.storage_generation}`], ['Expected desired revision', target.expected_desired_state_revision], ['Deferred / blocked', 'None in this one-target teaching scenario'], ['Required full plan', 'Effective inputs, provenance, pins, approvals, expiry and rollout policy']];
  } else if (step.id === 'request') {
    summary = [['Plan digest', request.plan_ref.digest], ['Ordered target count', request.targets.length], ['Expected desired revision', target.expected_desired_state_revision], ['Stable retry identity', request.idempotency_key]];
  } else if (step.id === 'accept') {
    summary = [['Expected / current desired revision', state.scenario === 'conflict' ? '0 / 1 — conflict' : '0 / 0'], ['Caller outcome', result?.kind === 'unknown' ? 'Unknown: response lost' : result?.kind === 'blocked' ? 'Rejected: no publication' : accepted ? 'Accepted' : 'Awaiting checks'], ['Publication ID known to Flow', accepted ? state.publication : 'None'], ['Retry identity', request.idempotency_key]];
  } else {
    summary = [['BuildResult', 'Complete input-to-artifact mapping'], ['AuthorizedRelease', 'Independent approval of exact digests'], ['DesiredAssignment', 'Exact instance, attempt, lease and current revision checks'], ['DeviceObservation + PolicyDecision', 'Sequenced device evidence and independent appraisal'], ['ExecutionResult', 'Attempt-correlated confirmed outcome']];
  }
  $('contract-links').replaceChildren(...step.contracts.map(name => {
    const link = document.createElement('a');
    link.href = data.catalog[name].url;
    link.textContent = name;
    const badge = document.createElement('span');
    badge.className = `badge ${data.catalog[name].specified ? 'specified' : 'deferred'}`;
    badge.textContent = data.catalog[name].specified ? 'Specified' : 'Deferred';
    const row = document.createElement('div'); row.append(link, badge); return row;
  }));
  definitionList($('record-summary'), summary);
  $('record-details').hidden = !record;
  $('record-json').textContent = record ? JSON.stringify(record, null, 2) : '';
  if (name) $('download').href = `fixtures/${name}.json`;
  else $('download').removeAttribute('href');
  const specified = step.contracts.every(name => data.catalog[name].specified);
  $('record-label').textContent = record ? (result?.kind === 'passed' ? 'Simulated output · repository fixture' : 'Reference fixture · before this handoff') : specified ? 'No output record available to Flow' : 'Conceptual handoff · wire format deferred';
  $('record-caveat').textContent = record ? 'This is the unchanged public fixture, not live evidence or authorization. The walkthrough does not perform schema, PKI or policy verification in your browser.' : specified ? 'The publication inspector reveals the accepted fixture only when Flow knows the acceptance outcome. The server and caller views can differ after a lost response.' : 'These obligations illustrate the specification. They are not a proposed JSON format or executable implementation.';
  if (step.id === 'identity' && !record) $('record-caveat').textContent = 'A development observation cannot be upgraded into production identity by advancing the UI.';
}

function render(focus = false) {
  const step = steps[state.step];
  const result = state.results[step.id];
  const completed = Object.values(state.results).filter(result => result.kind === 'passed').length;
  $('scenario').value = state.scenario;
  $('scenario-description').textContent = scenarios[state.scenario].description;
  $('progress-label').textContent = `Step ${state.step + 1} of ${steps.length}`;
  $('progress-count').textContent = `${completed} / ${steps.length} explored`;
  $('progress').value = completed;
  $('stepper').replaceChildren(...steps.map((item, index) => {
    const li = document.createElement('li');
    const button = document.createElement('button'); button.type = 'button';
    const number = document.createElement('span'); number.textContent = String(index + 1).padStart(2, '0');
    const label = document.createElement('span'); label.textContent = item.label;
    const status = state.results[item.id]?.kind;
    button.className = status || '';
    button.disabled = index > unlockedStep(state);
    if (index === state.step) button.setAttribute('aria-current', 'step');
    button.setAttribute('aria-label', `${index + 1}. ${item.label}${status ? `: ${status}` : button.disabled ? ': complete preceding steps first' : ''}`);
    button.append(number, label);
    button.addEventListener('click', () => {state = visit(state, index); render(true);});
    li.append(button); return li;
  }));
  $('step-number').textContent = `STEP ${String(state.step + 1).padStart(2, '0')}`;
  $('step-status').textContent = result?.kind === 'passed' ? 'Explored' : result?.kind === 'blocked' ? 'Blocked' : result?.kind === 'unknown' ? 'Outcome unknown' : 'Ready to explore';
  $('step-status').className = `badge ${result?.kind === 'passed' ? 'specified' : 'deferred'}`;
  $('step-title').textContent = step.title;
  $('step-description').textContent = step.description;
  $('producer').textContent = step.producer;
  $('consumer').textContent = step.consumer;
  list($('inputs'), step.inputs); list($('gates'), step.gates);
  $('step-note').textContent = step.note;
  $('outcome').hidden = !result;
  $('outcome').className = `outcome ${result?.kind || ''}`;
  $('outcome').textContent = result?.message || '';
  $('evaluate').textContent = step.action;
  $('evaluate').hidden = Boolean(result);
  $('reconcile').hidden = result?.kind !== 'unknown';
  $('restart-blocked').hidden = result?.kind !== 'blocked';
  $('back').disabled = state.step === 0;
  $('next').disabled = result?.kind !== 'passed' || state.step === steps.length - 1;
  $('next').textContent = state.step === steps.length - 1 ? 'End of walkthrough' : 'Next step →';
  inspect(step, result);
  $('acceptance-count').textContent = String(state.acceptanceCount);
  $('caller-state').textContent = state.results.accept?.kind === 'unknown' ? 'Unknown after lost reply' : state.results.accept?.kind === 'blocked' ? 'Rejected' : state.publication ? 'Accepted' : state.results.request ? 'Request sent' : 'Not requested';
  $('publication-id').textContent = state.publication && state.results.accept?.kind === 'passed' ? `Stable ID: ${state.publication}` : state.publication ? 'Teaching view: the server committed once; Flow must reconcile.' : 'No accepted publication.';
  const trace = steps.filter(item => state.results[item.id]).map(item => `${item.contracts.join(' + ')} — ${state.results[item.id].kind === 'passed' ? item.id === 'fulfill' ? 'obligations explored; no fulfillment records created' : 'handoff explored' : state.results[item.id].kind}`);
  list($('trace'), trace.length ? trace : ['No handoffs explored yet. Start with the provisioning observation.']);
  if (focus) { $('record-details').open = false; $('step-title').focus({preventScroll: true}); $('step-title').scrollIntoView({block: 'start'}); }
}

$('evaluate').addEventListener('click', () => {state = evaluate(state, data.fixtures.publication.record_id); render(); $('outcome').focus({preventScroll: true});});
$('reconcile').addEventListener('click', () => {state = reconcile(state); render(); $('outcome').focus({preventScroll: true});});
$('next').addEventListener('click', () => {state = advance(state); render(true);});
$('back').addEventListener('click', () => {state = visit(state, state.step - 1); render(true);});
$('scenario').addEventListener('change', event => {state = initialState(event.target.value); $('record-details').open = false; render();});
$('reset').addEventListener('click', () => {state = initialState(state.scenario); $('record-details').open = false; render();});
$('restart-blocked').addEventListener('click', () => { $('scenario').focus(); $('scenario').scrollIntoView({block: 'center'}); });
render();
$('loading').hidden = true;
$('walkthrough').hidden = false;

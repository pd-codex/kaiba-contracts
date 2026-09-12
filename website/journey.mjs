import data from './walkthrough-data.mjs';
import {steps, initialState, unlockedStep, visit, advance, evaluate, reconcile} from './walkthrough-model.mjs';
import {stories, storyScenarios, storyFor} from './journey-content.mjs';

const $ = id => document.getElementById(id);
let state = initialState();
let busy = false;
let generation = 0;
let timers = [];
const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
let motion = !motionPreference.matches;

function clearWork() {
  generation++;
  timers.forEach(clearTimeout);
  timers = [];
  busy = false;
}

function reset(scenario = state.scenario) {
  clearWork();
  state = initialState(scenario);
  $('peek').open = false;
  render();
}

function go(next) {
  clearWork();
  state = next;
  $('peek').open = false;
  render(true);
}

function render(focus = false) {
  const step = steps[state.step];
  const story = storyFor(state);
  const result = state.results[step.id];
  const completed = Object.values(state.results).filter(value => value.kind === 'passed').length;
  document.body.dataset.motion = motion ? 'on' : 'off';
  document.body.dataset.scene = step.id;
  document.body.dataset.result = result?.kind || 'pending';
  $('scene').classList.toggle('is-working', busy);
  $('scene').classList.toggle('is-complete', result?.kind === 'passed');
  $('scene').classList.toggle('network-on', state.step > 2 || (state.step === 2 && result?.kind === 'passed'));
  $('scene').classList.toggle('identity-on', state.step > 1 || (state.step === 1 && result?.kind === 'passed'));
  $('scene').classList.toggle('prepared', state.step > 0 || Boolean(result));
  $('story-app').setAttribute('aria-busy', String(busy));
  $('chapter').textContent = `${String(state.step + 1).padStart(2, '0')} / ${String(steps.length).padStart(2, '0')}`;
  $('act').textContent = story.act;
  $('headline-first').textContent = story.headline[0];
  $('headline-accent').textContent = story.headline[1];
  $('story-intro').textContent = story.intro;
  $('status-chip').textContent = result?.kind === 'blocked' ? 'A reason to pause' : result?.kind === 'unknown' ? 'Confirmation missing' : result?.kind === 'passed' ? step.id === 'fulfill' ? 'Story complete' : 'Step explored' : 'Your next step';
  $('before-title').textContent = story.before[0];
  $('before-detail').textContent = story.before[1];
  $('operation-title').textContent = story.operation[0];
  $('operation-detail').textContent = story.operation[1];
  $('after-title').textContent = result ? story.after[0] : 'Let’s find out';
  $('after-detail').textContent = result ? story.after[1] : 'Run this step to reveal what changes.';
  $('after-state').className = `state-stop after ${result?.kind || 'waiting'}`;
  $('artifact-eyebrow').textContent = story.artifact[0];
  $('artifact-title').textContent = story.artifact[1];
  $('artifact-icon').setAttribute('href', `#icon-${story.icon}`);
  $('artifact-check').textContent = result?.kind === 'passed' ? step.id === 'fulfill' ? 'Ahead' : '✓' : result?.kind === 'blocked' ? '!' : result?.kind === 'unknown' ? '?' : '…';
  $('story-tasks').replaceChildren(...story.tasks.map((task, index) => {
    const li = document.createElement('li');
    const number = document.createElement('span'); number.textContent = String(index + 1).padStart(2, '0');
    const text = document.createElement('span'); text.textContent = task;
    li.append(number, text); return li;
  }));
  $('scene-caption').textContent = state.step === 0 ? result ? state.scenario === 'development' ? 'Prepared for the lab' : 'Prepared for an identity check' : 'Device 01 · waiting for setup' : state.step === 1 ? result?.kind === 'passed' ? 'Device 01 · identity recognized' : state.scenario === 'development' ? 'Device 01 · lab-only' : 'Device 01 · identity pending' : state.step === 2 && !result ? 'Device 01 · fleet membership pending' : 'Device 01 · waiting for its new job';
  $('location-chip').textContent = state.step === 0 ? 'At the provisioning station' : state.step === 1 ? 'Device + identity service' : state.step === 2 ? 'In the fleet service' : state.step < 6 ? 'In the planning tools' : state.step < 8 ? 'In Flow + Kaiba' : 'Future rollout work';
  $('outcome').hidden = !result;
  $('outcome').textContent = result ? story.outcome : '';
  $('story-announcement').textContent = result ? story.outcome : `${story.name}. ${story.before[0]}.`;
  $('take-action').disabled = busy;
  $('take-action').textContent = result?.kind === 'unknown' ? 'Recover the confirmation' : result?.kind === 'blocked' ? 'Try the complete journey' : result?.kind === 'passed' ? state.step === steps.length - 1 ? 'Start the story again' : `Next: ${stories[steps[state.step + 1].id].name.toLowerCase()}` : story.action;
  $('action-hint').textContent = result?.kind === 'unknown' ? 'Same request. Same saved decision.' : result?.kind === 'blocked' ? 'Restart with the example checks assumed to pass.' : result?.kind === 'passed' ? state.step === steps.length - 1 ? 'The real device has not been changed by this demo.' : 'Continue when you are ready.' : 'Try this step in the illustration.';
  $('previous').disabled = busy || state.step === 0;
  $('scenario').value = state.scenario;
  $('scenario').disabled = busy;
  $('scenario-description').textContent = storyScenarios[state.scenario][1];
  $('motion').textContent = motion ? 'Motion on' : 'Motion off';
  $('motion').setAttribute('aria-pressed', String(motion));
  $('journey-progress').value = completed;
  $('progress-count').textContent = `${completed} of ${steps.length} explored`;
  $('chapter-nav').replaceChildren(...steps.map((item, index) => {
    const button = document.createElement('button'); button.type = 'button';
    const number = document.createElement('span'); number.textContent = String(index + 1).padStart(2, '0');
    const name = document.createElement('span'); name.textContent = stories[item.id].name;
    button.append(number, name);
    button.disabled = busy || index > unlockedStep(state);
    button.className = state.results[item.id]?.kind || '';
    if (index === state.step) button.setAttribute('aria-current', 'step');
    button.setAttribute('aria-label', `${index + 1}. ${stories[item.id].name}${state.results[item.id] ? `: ${state.results[item.id].kind}` : ''}`);
    button.addEventListener('click', () => go(visit(state, index)));
    return button;
  }));
  $('peek-note').textContent = story.note;
  $('contract-list').replaceChildren(...step.contracts.map(name => {
    const link = document.createElement('a'); link.href = data.catalog[name].url;
    link.textContent = `${name} · ${data.catalog[name].specified ? 'draft specified' : 'format still to define'}`;
    return link;
  }));
  $('acceptance-count').textContent = String(state.acceptanceCount);
  if (focus) {
    $('story-title').focus({preventScroll: true});
    $('story-app').scrollIntoView({block: 'start', behavior: motion ? 'smooth' : 'auto'});
  }
}

function runOperation(retry = false) {
  if (busy) return;
  const ticket = ++generation;
  const story = storyFor(state);
  busy = true;
  render();
  $('take-action').textContent = retry ? 'Recovering the confirmation…' : story.busy;
  $('action-hint').textContent = 'Playing this example…';
  const tasks = [...$('story-tasks').children];
  const interval = motion ? 240 : 0;
  tasks.forEach((task, index) => timers.push(setTimeout(() => {
    if (ticket !== generation) return;
    task.classList.add('lit');
  }, interval * index)));
  timers.push(setTimeout(() => {
    if (ticket !== generation) return;
    state = retry ? reconcile(state) : evaluate(state, data.fixtures.publication.record_id);
    busy = false;
    timers = [];
    render();
    $('take-action').focus({preventScroll: true});
  }, interval * tasks.length + (motion ? 150 : 0)));
}

$('take-action').addEventListener('click', () => {
  const result = state.results[steps[state.step].id];
  if (!result) runOperation();
  else if (result.kind === 'unknown') runOperation(true);
  else if (result.kind === 'blocked') {reset('reviewed'); $('what-if').open = false;}
  else if (state.step === steps.length - 1) reset();
  else go(advance(state));
});
$('previous').addEventListener('click', () => go(visit(state, state.step - 1)));
$('restart').addEventListener('click', () => reset());
$('scenario').addEventListener('change', event => {reset(event.target.value); $('what-if').open = false; $('take-action').focus({preventScroll: true});});
$('motion').addEventListener('click', () => {motion = !motion; document.body.dataset.motion = motion ? 'on' : 'off'; $('motion').textContent = motion ? 'Motion on' : 'Motion off'; $('motion').setAttribute('aria-pressed', String(motion));});
motionPreference.addEventListener('change', event => {motion = !event.matches; document.body.dataset.motion = motion ? 'on' : 'off'; $('motion').textContent = motion ? 'Motion on' : 'Motion off'; $('motion').setAttribute('aria-pressed', String(motion));});
render();
$('loading').hidden = true;
$('story-app').hidden = false;

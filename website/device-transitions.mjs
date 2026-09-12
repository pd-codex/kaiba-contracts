// Presentation states for the teaching scenario, not new shared wire contracts.
import {steps} from './walkthrough-model.mjs';

export const stateFields = [
  ['physical', 'Physical / provisioning'], ['identity', 'Management identity'],
  ['admission', 'Fleet participation'], ['intent', 'Configuration intent'],
  ['desired', 'Desired assignment'], ['running', 'Observed running state'],
];

const baseline = () => ({
  phase: 'Selected target; preparation pending',
  physical: 'Initial target state still to verify',
  identity: 'No active binding established',
  admission: 'Not admitted',
  intent: 'No configuration selected',
  desired: 'Revision 0 · no assignment in this scenario',
  running: 'No runtime observation supplied',
});

const descriptions = {
  observe: {
    title: 'Prepare the device and capture its state',
    description: 'Start with a selected target. The owning provisioning workflow prepares it under an approved profile and exports what was observed.',
    effect: 'Device preparation + retained evidence',
    operations: [
      'Verify the target’s initial state, exact identity and operation authority.',
      'Run the approved profile’s provisioning operations through the physical lane; retain control and audit evidence.',
      'Export the resulting source state and readiness claims in an immutable observation.',
    ],
    note: 'The entry state is an illustrative starting condition, not proof of a fresh board. Physical operations belong to provisioning. Its export adapter only reads the resulting evidence. The production exit shown here is hypothetical; development remains explicitly unqualified.',
  },
  identity: {
    title: 'Verify the installed identity and activate it',
    description: 'The prepared device has a staged management credential. Verification binds the installed key to the exact instance before inventory activates that tuple.',
    effect: 'Identity authorization changes; software stays as observed',
    operations: [
      'Bind fresh bootstrap and operational-key proofs to this exact device instance and credential.',
      'Check the installed key, certificate tuple, identity policy and verifier evidence.',
      'Atomically activate the tuple in inventory and issue its next binding revision.',
    ],
  },
  admit: {
    title: 'Allow this instance to participate in the fleet',
    description: 'An active identity enters admission. Current tenant, platform and policy checks decide whether this instance can become a configuration target.',
    effect: 'Fleet eligibility changes; no device-side write',
    operations: [
      'Check current inventory authorization, tenant membership and platform qualification.',
      'Apply current admission policy, restrictions and freshness requirements.',
      'Expose this exact instance as an eligible target with its constraints.',
    ],
  },
  components: {
    title: 'Make compatible components available',
    description: 'The admitted device waits while component owners publish the definitions used by Flow and the resolver. This prerequisite may happen before provisioning.',
    effect: 'Component catalog changes; device state is unchanged',
    operations: [
      'Define typed ports, configuration fields, compatibility, permissions and health requirements.',
      'Review and pin component versions for the editor and resolver.',
      'Make that shared vocabulary available for authoring; send nothing to the device.',
    ],
  },
  author: {
    title: 'Create the configuration intended for the device',
    description: 'The operator builds a graph in Flow. A frozen graph becomes configuration intent; it has not yet been resolved or assigned to this device.',
    effect: 'Authoring intent changes; no device-side write',
    operations: [
      'Connect typed components and choose settings using the shared component definitions.',
      'Pin component versions and use scoped references for secrets.',
      'Freeze an immutable graph revision while keeping the editable draft separate.',
    ],
  },
  resolve: {
    title: 'Resolve and review this device’s exact configuration',
    description: 'Combine the frozen graph with the instance’s constraints and settings. Review the effective values and exact target before publication.',
    effect: 'Reviewed intent changes; desired assignment stays at revision 0',
    operations: [
      'Resolve platform constraints, tenant baseline, group settings and permitted device overrides.',
      'Retain value provenance and separate eligible, deferred and blocked targets.',
      'Review this exact instance, effective inputs, expected revision, approvals and rollout policy.',
    ],
  },
  request: {
    title: 'Request publication for the reviewed device',
    description: 'The operator submits the reviewed intent. The device keeps its existing assignment while the publication authority considers the request.',
    effect: 'A request is sent; no device-side write',
    operations: [
      'Select the exact reviewed plan and its ordered eligible target list.',
      'Send the instance, storage generation, expected revision and stable idempotency key.',
      'Use authenticated actor and tenant context; await an acceptance decision.',
    ],
  },
  accept: {
    title: 'Accept the device’s configuration intent',
    description: 'Publication commits the reviewed intent for this device. It creates recoverable execution work; it does not install software or advance the desired assignment.',
    effect: 'Durable intent changes; device execution remains pending',
    operations: [
      'Recheck the exact plan, current admission, approvals and every expected desired-state revision.',
      'Commit the request identity, accepted publication and recoverable execution intent together.',
      'Return the stable publication ID to Flow.',
    ],
  },
  fulfill: {
    title: 'Identify the operations still needed on the device',
    description: 'The device leaves publication with accepted intent and no new assignment. These later operations are required before its running configuration can change and be confirmed.',
    effect: 'Future execution preview; no device transition is simulated here',
    operations: [
      'Build from the exact effective inputs and independently authorize the release artifacts.',
      'Recheck policy and desired revision, then assign an instance-bound execution attempt.',
      'Stage and activate through the qualified platform update path; collect release and health observations.',
      'Appraise the evidence independently before reporting a confirmed execution result.',
    ],
  },
};

function applyExit(entry, id, scenario, result) {
  if (!result) return {...entry};
  const exit = {...entry};
  if (result.kind === 'blocked') {
    if (id === 'accept') { exit.phase = 'Publication rejected; new review required'; exit.intent = 'Reviewed request rejected · revision conflict'; }
    return exit;
  }
  if (id === 'observe') {
    const development = scenario === 'development';
    exit.phase = development ? 'Development preparation recorded' : 'Prepared; identity activation pending';
    exit.physical = development ? 'security_applied · development source' : 'credentials_staged · hypothetical source';
    exit.identity = development ? 'Production identity blocked by posture' : 'Staged credential · not active';
  } else if (id === 'identity') {
    exit.phase = 'Identity active; admission pending'; exit.identity = 'Active exact tuple · binding revision 2';
  } else if (id === 'admit') {
    exit.phase = 'Admitted; configuration not assigned'; exit.admission = 'Eligible instance · current checks required';
  } else if (id === 'author') {
    exit.phase = 'Graph frozen; device resolution pending'; exit.intent = 'Immutable graph · not resolved for this instance';
  } else if (id === 'resolve') {
    exit.phase = 'Exact configuration reviewed'; exit.intent = 'Reviewed plan · exact instance and expected revision 0';
  } else if (id === 'request') {
    exit.phase = 'Publication requested; decision pending'; exit.intent = 'Reviewed request sent · acceptance pending';
  } else if (id === 'accept') {
    exit.phase = 'Intent accepted; execution pending'; exit.intent = 'Publication accepted · recoverable execution intent';
  }
  return exit;
}

export function deviceTransition(state) {
  const step = steps[state.step];
  let entry = baseline();
  // Reconstruct the historical entry, so revisiting a step cannot show later state.
  for (let index = 0; index < state.step; index++) {
    entry = applyExit(entry, steps[index].id, state.scenario, state.results[steps[index].id]);
  }
  let event = '';
  if (state.scenario === 'conflict' && step.id === 'accept') {
    entry.desired = 'Revision 1 · advanced by another assignment';
    event = 'Between steps: another assignment advanced the desired-state revision from 0 to 1. That external change is present on entry; this request still expects 0. No new runtime observation is supplied.';
  }
  const result = state.results[step.id];
  const details = {...descriptions[step.id], operations: [...descriptions[step.id].operations]};
  if (step.id === 'identity' && state.scenario === 'development') {
    details.description = 'The development device enters with security_applied evidence and no production-ready posture. The identity gate must stop here.';
    details.effect = 'Gate blocks; device and identity remain unchanged';
    details.operations = ['Read the development posture and readiness blockers.', 'Reject production identity activation because qualification is missing.', 'Retain the observation for review; do not activate a credential or admit the device.'];
  } else if (step.id === 'accept' && state.scenario === 'conflict') {
    details.effect = 'Request rejected; external desired revision 1 is preserved';
    details.operations = ['Read current desired-state revision 1 for the exact instance.', 'Compare it with the reviewed request’s expected revision 0.', 'Reject the whole request without a Publication or execution intent. Require a newly resolved and reviewed plan.'];
  } else if (step.id === 'accept' && state.scenario === 'lost') {
    details.operations[2] = 'Lose the response after the server commits; Flow’s outcome becomes unknown.';
    if (state.retries) details.operations.push('Authenticate an identical retry and retrieve the original publication; create no second acceptance.');
  }
  const exit = result ? applyExit(entry, step.id, state.scenario, result) : null;
  const changed = exit ? stateFields.filter(([key]) => entry[key] !== exit[key]).map(([key]) => key) : [];
  return {...details, entry, exit, changed, event, result, previewOnly: step.id === 'fulfill'};
}

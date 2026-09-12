// Pure teaching model. No service calls, credentials, or device operations.
export const scenarios = {
  reviewed: {title: 'Reviewed publication', description: 'Hypothetical production path. Authority, fresh proofs and policy checks are assumed to pass at the fixture time. This is not implemented production behavior.'},
  development: {title: 'Current development block', description: 'A valid development observation reaches the inbox, but production identity activation remains blocked. Successful provisioning does not grant enrollment.'},
  conflict: {title: 'Desired revision changed', description: 'The operator reviews expected revision 0. Before acceptance, another assignment advances it to 1. The whole publication request must be rejected.'},
  lost: {title: 'Publication response lost', description: 'Acceptance commits, but the reply never reaches Flow. Reconcile using the identical request and key to recover the same publication.'},
};

export const steps = [
  {
    id: 'observe', label: 'Prepare device', title: 'Carry the observation forward',
    producer: 'Provisioning authority', consumer: 'Identity / observation inbox', contracts: ['ProvisioningRecord'],
    description: 'Export one immutable observation of the physical transaction. Its source state and readiness claims stay separate from downstream decisions.',
    inputs: ['Approved profile and exact transaction', 'Scoped control state and independent audit evidence'],
    gates: ['Preserve source identity, revision, tenant and domain.', 'Consumers must authenticate origin and assess authoritative evidence and freshness.', 'Retained evidence checks in the development inbox do not close the live authority gate.'],
    note: 'The production fixture is early candidate evidence. Final completion must not be required before the identity activation that completion itself depends on.',
    action: 'Simulate preparation and observe exit',
    success: 'The observation is available to consumers. It is evidence of a source outcome, not permission to join the fleet.',
  },
  {
    id: 'identity', label: 'Activate identity', title: 'Bind one exact instance',
    producer: 'RA / CA / verifier / inventory', consumer: 'Relying services and admission', contracts: ['DeviceBinding'],
    description: 'A certificate starts as a staged tuple. A fresh verifier result and an atomic inventory decision activate that exact installed credential.',
    inputs: ['Early ProvisioningRecord evidence', 'Bootstrap and operational-key proofs bound to one transaction', 'Canonical device, instance, storage generation and credential tuple'],
    gates: ['Require current identity policy and a qualified profile.', 'Verify the exact instance, slot, key generation and certificate.', 'Activate atomically; an active snapshot alone never proves current authorization.'],
    note: 'The hypothetical candidate has enrollment_ready=false because verification is pending. That is different from an explicitly development-only posture, which cannot pass this production gate.',
    action: 'Simulate identity gate',
    success: 'The staged tuple becomes active in the hypothetical inventory. The record keeps the same identity and increments its revision from 1 to 2.',
  },
  {
    id: 'admit', label: 'Admit to fleet', title: 'Decide participation now',
    producer: 'Fleet admission', consumer: 'Resolver / controller', contracts: ['FleetTarget'],
    description: 'Admission combines active identity with tenant authorization, platform qualification and current policy. The output describes the exact instance and its restrictions.',
    inputs: ['Current inventory authorization for the active binding', 'Tenant membership, qualified capabilities and fresh policy'],
    gates: ['Reject stale, quarantined or revoked authority.', 'Carry constraints and decision freshness with the target.'],
    note: 'This contract’s wire format is deferred. The fields shown in the inspector are conceptual obligations.',
    action: 'Simulate admission decision',
    success: 'One exact instance is eligible in this hypothetical scenario. Admission is rechecked later; this decision is not a perpetual grant.',
  },
  {
    id: 'components', label: 'Define components', title: 'Agree the editor’s vocabulary',
    producer: 'Component owners', consumer: 'Flow editor and resolver', contracts: ['ComponentContract'],
    description: 'Component definitions give the editor and resolver the same typed ports, configuration rules, compatibility and operational requirements.',
    inputs: ['Reviewed component definition and implementation semantics', 'Pinned component versions'],
    gates: ['Define port types, permissions and health requirements.', 'Agree deterministic resolution behavior before claiming compiler conformance.'],
    note: 'This is a parallel prerequisite for authoring and resolution. It can happen before provisioning; its placement here is for explanation.',
    action: 'Inspect component handoff',
    success: 'The hypothetical component vocabulary is available to both Flow and the resolver. Its wire format remains deferred.',
  },
  {
    id: 'author', label: 'Author in Flow', title: 'Freeze the operator’s graph',
    producer: 'Kaiba Flow / authoring', consumer: 'Resolver', contracts: ['ConfigurationRevision'],
    description: 'The operator connects typed components and chooses settings. Publishing uses an immutable graph revision, while the editable draft remains separate.',
    inputs: ['Pinned ComponentContract versions', 'Graph connections, configuration values and scoped secret references'],
    gates: ['Preserve immutable component pins and authoring provenance.', 'Keep secret values out of records and Nix outputs.'],
    note: 'The current Flow inbox branch reads observations. This stage illustrates future authoring against shared contracts.',
    action: 'Simulate freezing the graph',
    success: 'An immutable configuration revision is ready for resolution. Changing the draft later cannot mutate this revision.',
  },
  {
    id: 'resolve', label: 'Resolve & review', title: 'Review exact scope and values',
    producer: 'Resolver → operator review', consumer: 'Publication authority', contracts: ['DeploymentPlan'],
    description: 'Resolve group selection into exact instances and effective values. The reviewed plan binds the graph, inputs, provenance, exclusions and expected desired-state revisions.',
    inputs: ['Configuration revision and admitted targets', 'Platform constraints → tenant baseline → group settings → allowed overrides'],
    gates: ['Block equal-layer conflicts; preserve locked platform constraints.', 'Separate eligible, deferred and blocked targets with reasons.', 'Freeze exact instances, approvals, expiry, rollout policy and complete effective inputs.'],
    note: 'The repository’s plan stub only binds test fixtures. It is not a complete DeploymentPlan schema or an executable plan.',
    action: 'Simulate reviewing this plan',
    success: 'The operator reviewed one eligible instance at expected desired-state revision 0. Membership changes require a new reviewed plan.',
  },
  {
    id: 'request', label: 'Request publication', title: 'Submit the exact reviewed intent',
    producer: 'Kaiba Flow / authorized client', consumer: 'Publication authority', contracts: ['PublishRequest'],
    description: 'Send the plan reference, its exact ordered eligible list and a stable retry identity. The authenticated context supplies the actor and tenant.',
    inputs: ['Reviewed plan reference and digest', 'Exact instance and expected desired-state revision 0'],
    gates: ['Match the ordered eligible target list exactly.', 'Use the same idempotency key for the same logical request.', 'Do not accept caller-selected actor or tenant fields.'],
    note: 'Sending this request is distinct from receiving durable acceptance. The client may still receive a conflict or lose the response.',
    action: 'Simulate submitting the request',
    success: 'The publication authority received the fixture request. No publication has been accepted yet.',
  },
  {
    id: 'accept', label: 'Accept intent', title: 'Commit durable publication',
    producer: 'Publication authority', consumer: 'Execution / Flow / audit', contracts: ['Publication'],
    description: 'Recheck current scope, admission, plan validity, approvals and every expected revision. Commit the request identity, accepted record and recoverable execution intent together.',
    inputs: ['PublishRequest plus authenticated actor and tenant', 'Current plan, policy and desired-state revisions'],
    gates: ['Accept the entire reviewed eligible list or reject it.', 'Make accepted-but-undispatched work recoverable after a crash.', 'Return one stable publication ID; execution status belongs elsewhere.'],
    note: 'An identical authorized retry retrieves the existing acceptance. It does not create another job or reauthorize execution.',
    action: 'Simulate acceptance checks',
    success: 'Publication accepted. The record is immutable at revision 1; recoverable execution intent exists. Nothing is claimed to be running.',
  },
  {
    id: 'fulfill', label: 'After publication', title: 'Keep fulfillment facts separate',
    producer: 'Build / release / controller / device / appraisal', consumer: 'Execution history and Flow',
    contracts: ['BuildResult', 'AuthorizedRelease', 'DesiredAssignment', 'DeviceObservation', 'PolicyDecision', 'ExecutionResult'],
    description: 'Later services build artifacts, independently authorize releases, assign an exact attempt and assess device evidence. These are separate contracts and gates.',
    inputs: ['Accepted publication and exact resolved plan', 'Fresh policy, compare-and-swap revisions and attempt-correlated evidence'],
    gates: ['Bind complete effective inputs to approved artifact digests.', 'Recheck instance and expected revision at assignment.', 'Require observed release, health checks and independent appraisal for confirmation.'],
    note: 'Unknown outcomes stop rollout expansion. Offline targets remain deferred until a newly authorized attempt. This walkthrough creates no fulfillment records.',
    action: 'Review remaining device operations',
    success: 'Walkthrough complete: one publication is accepted. Built, authorized, assigned, running and confirmed remain separate, unproven outcomes in this simulation.',
  },
];

export function initialState(scenario = 'reviewed') {
  if (!Object.hasOwn(scenarios, scenario)) throw new Error('Unknown scenario');
  return {scenario, step: 0, results: {}, publication: null, acceptanceCount: 0, retries: 0};
}

export function unlockedStep(state) {
  const first = steps.findIndex(step => state.results[step.id]?.kind !== 'passed');
  return first < 0 ? steps.length - 1 : first;
}

export function visit(state, index) {
  if (!Number.isInteger(index) || index < 0 || index > unlockedStep(state)) return state;
  return {...state, step: index};
}

export function advance(state) {
  if (state.results[steps[state.step].id]?.kind !== 'passed') return state;
  return visit(state, Math.min(state.step + 1, steps.length - 1));
}

export function evaluate(state, publicationId) {
  const step = steps[state.step];
  if (state.results[step.id] || state.step > unlockedStep(state)) return state;
  let result = {kind: 'passed', message: step.success};
  let publication = state.publication;
  let acceptanceCount = state.acceptanceCount;
  if (state.scenario === 'development' && step.id === 'identity') {
    result = {kind: 'blocked', message: 'Production identity activation blocked: development_asset, rollback_unimplemented and production_qualification_missing. No DeviceBinding is emitted. The observation stays visible in the inbox.'};
  } else if (state.scenario === 'conflict' && step.id === 'accept') {
    result = {kind: 'blocked', message: 'Conflict: the request expects desired-state revision 0, but the current revision is 1. The entire request is rejected. No Publication or execution intent is created. Resolve and review a new plan; do not silently rebase this request.'};
  } else if (step.id === 'accept') {
    publication = publicationId;
    acceptanceCount = 1;
    if (state.scenario === 'lost') {
      result = {kind: 'unknown', message: 'The server committed acceptance, but Flow lost the reply. The caller’s outcome is unknown. Reconcile the identical request and idempotency key to recover its stable publication ID.'};
    }
  }
  return {...state, publication, acceptanceCount, results: {...state.results, [step.id]: result}};
}

export function reconcile(state) {
  if (state.results.accept?.kind !== 'unknown') return state;
  return {...state, retries: state.retries + 1, results: {...state.results, accept: {
    kind: 'passed', message: `Identical retry recovered ${state.publication}. There is still exactly one accepted publication and one execution intent. Current access is required to retrieve it; execution authorization is checked separately.`,
  }}};
}

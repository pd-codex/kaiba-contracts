# Existing-device pilot enrollment

Status: **proposed, not adopted by either runtime**. The new wire family is
`0.2.0-draft.1`. It implements the contract portion of the
[Ace/Mako pilot plan](https://github.com/PseudoDesign/kaiba-provisioning/blob/e4dd6b08a8efa65fd6e46d684407df660e351dc5/docs/pilot-enrollment.md).
Selecting targets, merging this specification or validating a fixture issues no
credential and authorizes no device operation.

The pilot admits explicitly reviewed existing devices with recorded limitations.
It does not turn development completion into full qualification. All four records
carry `full_qualification: false`; changing that value is invalid. The original
ProvisioningRecord and DeviceBinding at `0.1.0-draft.1` remain unchanged.

## Records and authority

| Record | Producer and meaning | Schema |
| --- | --- | --- |
| PilotAdoptionRecord | Provisioning's authenticated observation of one existing device, its storage, custody/workload reviews and remaining qualification conditions. No invented provisioning transaction or OTP operation. | [adoption](../schemas/0.2.0-draft.1/pilot-adoption-record.json) |
| PilotPolicy | Policy authority's reviewed, bounded two-target scope, issuer, audience, permissions, permitted gaps and freshness limits. | [policy](../schemas/0.2.0-draft.1/pilot-policy.json) |
| PilotAdmissionDecision | Policy authority's approval or denial of the exact adoption and policy revisions for one target, including the exact gaps accepted. | [decision](../schemas/0.2.0-draft.1/pilot-admission-decision.json) |
| PilotDeviceBinding | Fleet inventory's exact pilot credential tuple, source/decision references and effective lifecycle state. | [binding](../schemas/0.2.0-draft.1/pilot-device-binding.json) |

All use common record metadata, JCS RecordRefs and exact-byte EvidenceRefs under
the [common rules](../docs/common-rules.md). An authority ID, approver ID, digest
or `approved` field is a claim, not authority. Consumers MUST resolve immutable
records through independently configured, authenticated authority roles. An
uploaded JSON document is never an approval override. The initial implementation
must supply authenticated record and current-state reads before live activation;
a signature-envelope or alternative transport requires its own reviewed profile.

The provisioning observation authority, admission approver, fleet inventory,
credential issuer and device have separate roles even when hosted on malak.
Pilot trust/issuer configuration MUST be distinct from disposable rehearsal PKI
and from any later fully qualified fleet trust. A caller cannot select its own
tenant, domain, issuer, policy or trusted authority.

## Target and source binding

`target` contains an asset label and exact `identity_ref` / `storage_ref` evidence
references. Labels such as hostnames are not authentication. Identity evidence
must bind the observed board to the authenticated inspection session and station
endorsement. Storage evidence must bind that same board to the actual encrypted
filesystem and the proposed credential directory. URI values are opaque locators,
not destinations to fetch with ambient credentials. Each resolver is configured
for its authority role and refuses arbitrary URLs, credential-bearing redirects
or a target's self-nominated authority.

`source` names the implementation repository/commit, observation ID/time and the
inventory, custody and workload review bytes. Custody includes each device's own
statement about original secrets, derived/recovery keys, retained copies,
protection and unresolved history. A statement is retained testimony, not proof
that no copy exists. `custody_review_complete` means the required review and any
existing-secret exception are documented; an unknown or unfinished review is
false. Ace's statement or exception MUST NOT be reused for Mako. Evidence stays
access-controlled; only synthetic examples belong in this repository.

Exporting the same unchanged inputs returns the same immutable record revision,
issuance time and digest. Changed evidence, observation, conditions or source
revision requires a new revision and a new bound decision. The exporter observes
existing state; it does not enroll, program OTP, reconcile physical operations or
manufacture records for the seven provisioning operations.

## Qualification and hard blockers

The adoption record contains all FA-01 through FA-08 outcomes. Each outcome is
`passed`, `blocked` or `not_evaluated`, with a reason and retained evidence refs.
`passed` requires at least one reference, whose actual sufficiency the consumer
must verify against the applicable baseline. Accepting a gap preserves its
original outcome. An encrypted-filesystem observation alone cannot pass FA-04's
complete protection claim. A process restart cannot establish offline cold boot.
Adoption and policy MUST carry the same `qualification_policy_ref`, binding the
exact authoritative FA baseline bytes; condition names cannot be reinterpreted
under a different baseline while keeping the same approval.

Before pilot admission these conditions MUST hold:

- `target_authenticated`, `encrypted_persistence_observed`,
  `custody_review_complete` and `workloads_recorded` are true.
- `unresolved_mutation`, `conflicting_ownership` and `known_key_exposure` are false.

Neither a permitted gap nor an approver can override those blockers through this
contract. Policy `allowed_gaps` names FA conditions that may remain incomplete;
the decision's `accepted_gaps` MUST equal exactly the adoption's non-passed
conditions, and be a subset of the policy's permitted gaps. The decision's review
reference documents the particular limitation and risk acceptance for that device.
It binds the entire adoption digest, including the custody review and reasons.

## Cohort, validity and permissions

This initial profile is exactly `rpi5-existing-luks-pilot-v1`. A policy contains
exactly two distinct targets; asset labels, identity digests and storage digests
must each be distinct. It is not a hostname allowlist. A third device requires a
new reviewed policy/profile; it cannot reuse one device's endorsement or decision.

Policy and decision validity windows are half-open: `valid_from <= now < expires_at`.
The decision cannot outlive the policy or predate its source records. Future-issued
records are rejected. Policy chooses `max_observation_age_seconds` explicitly,
bounded to 1–604800 seconds; there is no default freshness allowance. Required
authority state must also be current. A recent timestamp cannot revive a revoked
decision, superseded observation or unknown policy. The consumer supplies the
trusted clock; a request cannot choose the time at which it authorizes itself.

The exact permissions are:

- `pilot:self:read`: read this credential's own pilot identity/status.
- `pilot:diagnostic-reference:submit`: submit references to this device's own
  diagnostic results through an authenticated, size-bounded interface.

Neither permits another device's records, administration, enrollment approval,
remote execution, signing, credential issuance or qualified-fleet access. The
diagnostic transport/size limits must be specified and tested by the implementing
service before deployment; this contract grants no arbitrary evidence-fetch API.
Local applications remain independent of fleet availability.

## Enrollment and binding

Fleet assigns the canonical logical identity, instance and generations. The client
generates a distinct operational key on the device, in its verified encrypted
filesystem and restricted credential directory. Private keys stay out of build
outputs, logs, records and transferable fixtures. Pilot credentials use role
`pilot_management` and the policy's exact issuer and audience.

Fresh proofs and pending-verifier receipts MUST bind the enrollment ID, target,
adoption/policy/decision revisions and digests, audience, canonical identity,
instance, storage/key generations, slot, SPKI, issuer/certificate and profile.
Prove installed-key use after a client process restart before atomic activation.
Activation records `restart_kind: client_process`. The contract does not define
an offline cold-boot claim. Source verification, proof transport and the full
receipt payload are implementation integration obligations, not fulfilled by an
EvidenceRef's shape. Both runtimes must adopt the same reviewed profile first.

PilotDeviceBinding uses the existing staged/active/superseded/quarantined/revoked/
retired lifecycle and monotonic revision rules. The credential tuple, target,
adoption, admission and policy references, audience, profile and permissions are
immutable within one binding. Changing admission requires a reviewed new binding
and credential lifecycle, not extending an old approval in place. The original
binding remains available for audit. Quarantine recovery needs fresh verification;
revoked/retired bindings cannot reactivate. Lost replies and restarts reconcile
the same durable enrollment and tuple without duplicate issuance.

Every relying request MUST check PKI and authoritative current membership/policy,
including requests on existing TLS connections. Staged, expired, quarantined,
revoked and retired credentials are denied. Revoking one device must leave the
other device's independent rights intact. Dependency outages fail closed for
fleet authorization and new activation, without stopping local applications.

Pilot credentials cannot be used at a fully qualified endpoint, and pilot bindings
cannot be supplied to the original publication/admission path as DeviceBindings.
Promotion requires the full applicable FA evidence and a separately reviewed
credential/trust transition that retires obsolete pilot authority. This draft
does not implement promotion or deployment of fleet services on Ace.

## Offline checks and runtime obligations

`validate()` checks shape and record-local invariants.
`validate_pilot_handoff()` checks exact references, scope, targets, time, blockers
and accepted gaps. `validate_pilot_binding()` adds binding consistency.
`validate_binding_transition()` checks the same-family lifecycle. These functions
do not authenticate evidence, prove possession or grant access; a consistent
revoked snapshot remains a valid historical record. Runtime consumers must not
treat an empty error list as enrollment authorization.

The portable [linked corpus](../examples/pilot-handoff-cases.json) names complete
local records, an explicit fixture clock and the rejection rule where applicable.
`valid` means linked offline
consistency only. It complements the [record corpus](../examples/manifest.json).
All keys, certificates, authorities and evidence references are synthetic.

Before real pilot enrollment, the owning repositories must demonstrate:

| ID | Required runtime result |
| --- | --- |
| PILOT-01 | Authenticated provisioning and policy reads resolve exact current revisions; tampering, unknown authority, stale/altered approval and unavailable state deny admission. |
| PILOT-02 | Two distinct device keys and server-assigned identities; target, source, custody, gap, challenge, proof and certificate substitutions fail, including an unapproved third target. |
| PILOT-03 | Installed credential works after process restart; pending access is denied; lost issuance/activation replies and authority restarts preserve one durable tuple. |
| PILOT-04 | Each member accesses only its own permitted operations; revocation/quarantine denies the next request on an existing connection and does not affect the other member. |
| PILOT-05 | Rehearsal/development records and issuers cannot enter pilot trust; pilot credentials cannot enter qualified trust. |
| PILOT-06 | Reports separate membership from every FA outcome, retained exception and evidence limit; an accepted gap never becomes a passed hardware check. |

The per-device and cohort reports retain source/contract pins, authenticated target
references, reviewed history/gaps, credential references, membership, timestamps
and restart type. Software conformance, real pilot membership and full hardware
qualification are three separate outcomes.

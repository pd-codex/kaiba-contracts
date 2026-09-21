# Adoption checklist

## Implementation owners

- [kaiba-provisioning](https://github.com/PseudoDesign/kaiba-provisioning) owns physical provisioning, evidence export and the ProvisioningRecord producer.
- [kaiba-fleet](https://github.com/PseudoDesign/kaiba-fleet) owns fleet inventory, enrollment, activation and credential lifecycle, consuming ProvisioningRecord and producing DeviceBinding.
- This repository owns shared semantics and conformance requirements.

The [enrollment handoff](https://github.com/PseudoDesign/kaiba-provisioning/pull/59)
scopes the first producer adapter and isolated consumer rehearsal. Fleet's
implementation is planned; service transport, durable store, CA integration,
evidence authentication and policy freshness still need decisions. Repository
ownership does not replace adoption records or runtime integration evidence.

## Initial integration order

1. Review ProvisioningRecord with provisioning/control/audit owners. Agree the
   export milestone, authentic evidence resolver, source-state mapping and
   quarantine behavior. Do not rename upstream states to fit the new adapter.
2. Review DeviceBinding with RA, CA, inventory and relying-service owners. Agree
   authority identity, pending verifier receipt, exact tuple lookup, revocation
   propagation, replacement and credential-rotation behavior.
3. Specify ComponentContract and DeploymentPlan with UI/resolver/build owners.
   Complete their schemas, typed ports, merge/conflict rules and effective-input
   equivalence before treating a referenced plan as executable.
4. Review Publication with controller/UI/execution owners. Implement durable
   idempotency, all-target acceptance, concurrency control, recoverable dispatch
   and explicit progress states. Exercise lost-response and crash cases.
5. Specify release, assignment and observation contracts. Demonstrate software
   integration in an isolated rehearsal, then satisfy each platform's separate
   physical production gates.

## Decisions still open

| Decision | Who must agree | What is already fixed |
| --- | --- | --- |
| Service and transport layout | System and subsystem maintainers | Logical authority separation survives co-location |
| Schema/SDK distribution | Producer and consumer maintainers | Consumers pin exact versions; schemas are bundled offline |
| Evidence/signature envelopes | Provisioning, identity and release authorities | Record possession and SHA-256 alone confer no authority |
| Admission and policy freshness | Identity, controller and platform owners | Unknown required policy denies new authorization |
| Full DeploymentPlan format | UI, resolver, build and controller owners | Frozen exact instances, provenance, expected versions and explicit exclusions |
| Runtime versus build-time configuration | Component and platform owners | Complete effective inputs determine artifact equivalence |
| Publication status/query transport | UI and controller owners | Durable acceptance is distinct from execution outcome |
| Named maintainers and release process | Repository owner/team | Producer and consumer review precedes a compatibility claim |

## Adoption record required per consumer

Record the contract-set tag/commit, supported wire versions, owning component,
evidence of schema/local checks and runtime scenarios, compatibility/migration
plan, and review approval. This baseline supplies no adoption records and no
production eligibility grants.

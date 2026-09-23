# Adoption checklist

## Implementation owners

- [kaiba-provisioning](https://github.com/PseudoDesign/kaiba-provisioning) owns physical provisioning, evidence export and the ProvisioningRecord producer.
- [kaiba-fleet](https://github.com/PseudoDesign/kaiba-fleet) owns fleet inventory, enrollment, activation and credential lifecycle, consuming ProvisioningRecord and producing DeviceBinding.
- This repository owns shared semantics and conformance requirements.

The [enrollment handoff](https://github.com/PseudoDesign/kaiba-provisioning/pull/59)
scopes the first producer adapter and isolated consumer rehearsal. The
[implementation profile](integrations/enrollment-rehearsal.md) selects Go,
PostgreSQL, HTTPS/mTLS, configured authority resolution and a disposable test CA.
Production CA integration and admission coordination remain open. Repository
ownership does not replace adoption records or runtime integration evidence.

## Proposed pilot adoption order

The [pilot family](../contracts/pilot-enrollment.md), wire `0.2.0-draft.1`, is
specified here but not supported by the current producer or consumer. Their
existing `0.1.0-draft.1` pins and rehearsal restrictions remain authoritative.

1. Review the new policy, adoption, decision and binding semantics together.
2. Implement and test opt-in consumer support with pilot trust disabled by default.
3. Update the provisioning producer/client to the same reviewed contracts commit;
   export actual adoption evidence without manufacturing provisioning operations.
4. Run the packaged two-device integration scenarios with disposable PKI. Record
   matching pins, approved role/transport mappings, evidence resolution and results.
5. Review per-device history/gaps, dedicated issuer custody, durable stores,
   recovery and the malak execution packet before enabling real pilot issuance.

There is no automatic conversion of retained records. During deployment overlap,
each endpoint explicitly supports its reviewed family; it never falls back from
an unknown pilot version to rehearsal or qualified behavior. Rollback disables
new pilot issuance and denies/revokes pilot access under its reviewed recovery
procedure; it cannot reinterpret pilot credentials as legacy DeviceBindings.
Existing records and their pinned schemas remain available for audit. Retiring
pilot trust or promoting a device requires a separate reviewed lifecycle.

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

## Enrollment implementation profile

Use the [authenticated enrollment rehearsal](integrations/enrollment-rehearsal.md)
for the provisioning-to-fleet integration. Implementations pin the shared schemas
and run the existing example corpus as well as their independent runtime tests.
This profile does not adopt or complete production admission.

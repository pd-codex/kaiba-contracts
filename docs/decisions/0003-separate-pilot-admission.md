# Separate pilot admission from full qualification

Status: proposed for producer/consumer review; no live adoption.

The original ProvisioningRecord requires production readiness before enrollment
readiness. Ace/Mako's selected pilot needs authenticated enrollment while retaining
incomplete hardware qualification and existing encrypted storage. Adding a pilot
enum or changing the meaning of readiness in that closed schema would silently
change an already pinned consumer's authority boundary.

Add a separate versioned pilot family: observed adoption, a bounded policy,
an exact per-device decision and a restricted credential binding. Preserve all
original schemas, readiness rules and fixtures byte for byte. Bump the contract
set to `0.2.0-draft.1`; enumerate supported contract/version pairs rather than
assuming every old record acquires the new version.

Policy accepts identified gaps without passing the underlying checks. Target
authentication, reviewed custody, encrypted persistence, workload review and
absence of unresolved mutations/conflicting ownership/known exposure remain hard
requirements. Pilot permissions, issuer and audience remain separate from
rehearsal and fully qualified trust. A two-target policy cannot enroll a third
host, and a generic unsigned override cannot grant admission.

This adds explicit implementation work and separate binding handling. It avoids
turning a development export into synthetic production evidence, or making the
word “pilot” a boolean that bypasses existing qualification. Runtime authenticated
resolution, proof/receipt bindings, persistence, isolation and revocation tests
remain necessary after these offline contracts pass. See the
[contract and migration requirements](../../contracts/pilot-enrollment.md) and
[adoption order](../adoption.md#proposed-pilot-adoption-order).

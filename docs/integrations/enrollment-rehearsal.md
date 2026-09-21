# Authenticated enrollment rehearsal

Status: implementation profile for an isolated software rehearsal. The shared
wire version remains `0.1.0-draft.1`; this document grants no production eligibility.

## Owners and authority

- `PseudoDesign/kaiba-provisioning` produces immutable ProvisioningRecord exports,
  and serves scoped reads from independent control and audit authorities.
- `PseudoDesign/kaiba-fleet` verifies records and evidence, implements inventory
  transitions, and owns the cross-repository process test.
- This repository owns record semantics and the shared example corpus.

The earlier development-controller inbox proposal remains a separate observation
consumer. Its retained-evidence check does not substitute for this profile's live
verification. No controller state, endpoint or contract is reassigned by this work.

## Implementation adoption records for review

Both implementations pin shared commit
`9ebf773d5d07d61d8cb522aea66160d37562e6b1` and support wire version
`0.1.0-draft.1` only. Bundled schemas resolve offline; wire semantics are unchanged
by these PRs. Review status is **pending maintainer review**, not production
adoption approval.

| Owning component | Implementation and coverage | Boundary |
| --- | --- | --- |
| Provisioning exporter, control and audit read surfaces | [Provisioning PR #60](https://github.com/PseudoDesign/kaiba-provisioning/pull/60), commit `a48816dd145774fa0541c1e564f190f08c155884`; producer mapping, authorization and durable revision tests | Produces development ProvisioningRecord only; no eligibility upgrade |
| Fleet verifier, inventory, RA and relying endpoint | [Fleet PR #1](https://github.com/PseudoDesign/kaiba-fleet/pull/1), commit `3fef2b84f63aee2a9dc7e0e4031b4f67248aa65b`; schema corpus, challenge/certificate checks and native process rehearsal | Consumes ProvisioningRecord; emits staged/active/denied DeviceBinding only within the isolated rehearsal |

The [native x86/ARM process run](https://github.com/PseudoDesign/kaiba-fleet/actions/runs/35659646453)
retains a secret-free report with exact source revisions and outcomes for 17
scenario groups. It uses the packaged producer at the commit above, independent
service processes and PostgreSQL. The
[producer CI](https://github.com/PseudoDesign/kaiba-provisioning/actions/runs/35659561707)
retains its repository-wide validation. These are software integration results;
the required physical admission evidence remains separate.

Compatibility changes require a reviewed schema/policy mapping and rerunning the
shared corpus and native process suite. Unknown contract versions fail closed.
There is no automatic relabeling or migration of records to a new wire version.
Fleet begins with database schema version 1 and rejects newer unknown database
versions. Future database upgrades require their own migration design. Exact
pins remain until the corresponding compatibility review approves an update.

## Resolution and freshness

Provisioning exports use operator-configured authority, tenant, domain and
profile/posture/release bindings. A caller supplies a granted transaction ID;
it cannot choose those policy fields. Export revisions belong to the export
store and cover control, audit and policy inputs. They are not control resource
versions. Retrying an unchanged observation returns the same issued time, bytes
and digest. A changed observation creates a new immutable revision.

EvidenceRef URIs use `urn:kaiba:evidence:sha256:<hex>` as opaque locators.
The verifier selects the endpoint and role from its configured authority registry,
never from a payload URL. Profile/posture/release bytes are pinned by policy.
Control and audit retain and return their own exact snapshot bytes. Structured
record digests use JCS; source evidence hashes bind their original retained bytes.

Fleet retrieves the exact record revision and evidence from each authority, then
brackets live audit reads with live control reads. A changed snapshot, missing
receipt, inconsistent scope, digest mismatch or unavailable authority prevents
new successful verification or activation. Issuance time alone never establishes
freshness. Retained historical verification does not authorize future actions.

This is bounded observation, not a distributed atomic transaction across the
control, audit and inventory services. The remaining production coordination
requirements must be resolved before enabling a production admission profile.

Service readers have explicit transaction grants and no station/approver identity.
They cannot submit control commands or audit events. No embedded credential,
redirect, proxy environment variable or client-selected URL expands authority.

## Two distinct test paths

1. The real development control/audit services and exporter produce authentic
   software-fixture observations. Both readiness flags stay false. Fleet verifies
   evidence and rejects enrollment; source uncertainty and quarantine remain visible.
2. A separately trusted synthetic authority supplies hypothetical eligible
   production-candidate records in the `rehearsal` domain. Its distinct source
   schema is `kaiba.test/qualified-candidate/v1`. Only this test path proceeds
   through key proof, staged issuance and activation using a disposable CA.

The synthetic authority is test tooling, not a readiness override in provisioning.
A software client's process restart tests persistence and installed-key proof;
it establishes neither a physical cold boot nor encrypted-state protection.

## Required executable scenarios

| ID | Scenario and required outcome |
| --- | --- |
| EH-01 / INT-PR-01 | Resolve independent authenticated evidence; reject missing, tampered, wrong-scope, malformed or changed authority state. |
| EH-02 / INT-PR-02 | Real development evidence verifies but cannot activate. |
| EH-03 | Repeated export and restart preserve exact immutable revision; changed inputs allocate a new revision. |
| EH-04 / INT-DB-01 | Challenges bind audience, transaction, canonical identity, instance, generations, key, profile and provisioning reference; replay, expiry and substitutions fail. |
| EH-05 / INT-DB-02 | Staged, expired, revoked and prior-instance credentials cannot use a relying service. |
| EH-06 / INT-DB-03 | Quarantine denies the next authorized request even on an existing TLS connection; no positive inventory cache. |
| EH-07 / INT-DB-04 | Lost issuance/activation replies and service restarts reconcile one durable tuple. |
| EH-08 | Concurrent duplicate requests converge; changed idempotency payloads fail without duplicate issuance. |
| EH-09 | Export/verification activity does not rewrite source control or audit stores. |

Report source revisions and scenario outcomes, with `hardware_qualified=false`
and `production_enrollment=false`. Do not publish temporary PKI, database dumps
or private evidence in CI artifacts. Passing the shared schema corpus alone does
not satisfy these scenarios; implementing repositories retain the runtime results.

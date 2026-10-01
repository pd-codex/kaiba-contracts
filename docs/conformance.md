# Conformance and example corpus

The offline suite checks the proposed schemas, record-local invariants and linked
synthetic records. It does not implement a controller or use real evidence,
credentials, devices, signing keys, clocks, inventory or policy services.

## Executable coverage

| Obligation | Local check |
| --- | --- |
| Version, closed shape, types, digests and timestamp formats | All schemas and the positive/negative corpus |
| PR-02: development readiness and reasons | Valid blocked development record; rejected readiness upgrade and missing reasons |
| DB-03: activation shape | Staged record, active record, rejected missing verifier reference and staged activation claim |
| DeviceBinding time and lifecycle consistency | Certificate/activation ordering, valid transitions, retired resurrection, stale revisions and recovery verification |
| DB-05: immutable tuple and scope | Rejected instance, tenant, storage generation and key mutation within one binding |
| PUB-03: target uniqueness and exact request binding | Duplicate-instance fixture and changed plan/instance/revision/key cases |
| SYS-06: publication meaning | Reject a Publication reporting `running` |
| Digest interoperability | JCS ordering/escaping, equivalent integer spellings, key-order-insensitive retries, linked record digests and request substitution |
| Strict parsing | Duplicate keys, non-JSON numbers and non-interoperable integer rejection |
| Offline schema resolution | Every schema reference resolves from the bundled registry |

`examples/manifest.json` declares valid and invalid records and identifies
whether each rejection comes from schema or semantic checks. Tests fail when a
new example is absent from the manifest or a rejection occurs at the wrong level.

The [pilot linked corpus](../examples/pilot-handoff-cases.json) additionally
checks exact adoption/policy/decision/binding links at an explicit fixture time.
Pilot tests cover target substitutions, exact accepted gaps, expiry/freshness,
non-waivable blockers, version/profile isolation and immutable pilot bindings.
The [pilot contract](../contracts/pilot-enrollment.md#offline-checks-and-runtime-obligations)
lists the separate runtime scenarios. Passing this corpus is not a credential,
approval, authenticated evidence check or completed hardware test.

## Example interpretation

- `provisioning-development.json` preserves the current development outcome and
  its blocked readiness. Valid JSON does not make it production-eligible.
- `provisioning-production-candidate.json` and `provisioning-production-complete.json`
  are hypothetical snapshots before and after identity activation/final audit.
  They use an `example.invalid` source repository rather than attributing
  production behavior to the reviewed development source.
- `binding-staged.json`, `binding-active.json` and `binding-retired.json` show a
  hypothetical tuple lifecycle. Activation's provisioning reference deliberately
  points to candidate evidence, avoiding a circular dependency on final completion.
- `publish-request.json` and `publication.json` are linked through a real JCS digest
  computed over the synthetic request.
- `examples/context/deployment-plan.stub.json` is explicitly a reference-only
  fixture. It is neither the proposed full plan wire format nor an executable plan.
- Evidence URNs and their synthetic hashes illustrate shape only. No resolver,
  real verifier, signature, certificate or authorization exists behind them.

The corpus includes a check that an untrusted `authority_id` can remain
schema-valid. This deliberately demonstrates the limit of local validation.

## Required subsystem integration scenarios — not satisfied here

| ID | Scenario | Required result and owner |
| --- | --- | --- |
| INT-PR-01 | Valid-shaped record from wrong authority, audit digest mismatch or stale transaction | Provisioning adapter/admission deny further authority; retain scoped evidence |
| INT-PR-02 | Development outcome presented for production admission | Admission denies regardless of ordinary schema validity |
| INT-DB-01 | Replayed PoP, different operational key, CSR-selected identity or wrong audience | RA/pending verifier reject; no activation |
| INT-DB-02 | Staged, expired, superseded, revoked, wrong-role or prior-instance certificate | Relying service denies despite a valid CA chain where applicable |
| INT-DB-03 | Quarantine occurs while an authorization cache or resumed session exists | Inventory and relying service invalidate within approved policy bounds |
| INT-DB-04 | Inventory activated a tuple but the caller lost the response | Reconcile the existing exact tuple; no duplicate issuance or activation |
| INT-PUB-01 | Spoofed tenant/actor, expired plan, changed eligibility or unauthorized target | Publication authority rejects without hidden partial acceptance |
| INT-PUB-02 | Identical retry, simultaneous duplicate or lost acceptance response | One durable publication and recoverable execution intent |
| INT-PUB-03 | Same idempotency scope/key with different canonical request | `idempotency_conflict`; no second work item |
| INT-PUB-04 | Crash between durable acceptance and dispatch | Accepted work is rediscovered; execution deduplicates delivery |
| INT-PUB-05 | Desired state changes during a build | Assignment compares current version and reports conflict; no silent overwrite |
| INT-EXEC-01 | Artifact substitution, revoked release, missing fresh boot authorization, failed canary or unknown boot | Separate release/device/policy authorities deny advancement and preserve evidence |

An implementing subsystem records its actual integration tests and evidence
against these IDs. Hardware production qualification is an additional platform
gate, never satisfied by this repository's fixtures or CI.

The [authenticated enrollment rehearsal](integrations/enrollment-rehearsal.md)
assigns concrete cross-repository scenarios to these obligations. Its synthetic
eligibility path and real development-denial path remain distinct.

## Proposed renewal authorization

`tests/test_renewal.py` checks the new 0.3.0-draft.1 authorization schema and
linked consistency with existing pilot records. Runtime certificate facts are
explicit inputs, not authenticated by these checks. Fleet integration must still
prove operator authorization, issuance history, crash recovery, proof binding,
atomic cutover, retained-connection rejection, expiry and restore behavior.
Passing these fixtures does not establish a usable renewal implementation.

`tests/test_renewal_cutover.py` and `tools/renewal.py` check successor staging,
installation receipt linkage and activation ordering. They cannot establish
signature verification, crash recovery or live predecessor rejection; those
remain required native fleet integration scenarios.

## Proposed SPIFFE workload binding

`tests/test_workload_binding.py` and the workload-binding corpus validate the
isolated `0.5.0-draft.1` schema, canonical URI/component equality, namespace
boundaries, allowed states and permissions, closed fields and exact version
dispatch. Tests retain valid non-active records and untrusted authority claims
to demonstrate that structural validity is not authorization.

The following require independent runtime evidence before adoption:

| ID | Scenario | Required owner/result |
| --- | --- | --- |
| INT-WB-01 | Wrong trust domain, device, instance or workload; untrusted registry; caller-supplied assertion | Registry/DNS deny before a DNS mutation |
| INT-WB-02 | Active workload record with inactive or replaced enrollment; missing permission; unassigned DNS name | Registry/DNS deny despite valid SVID authentication |
| INT-WB-03 | Registry unavailable, missing or stale; quarantine, retirement or permission removal on an existing connection | Relying service checks each request and denies within the adopted invalidation policy |
| INT-WB-04 | Real SVID rotation, expiry, trust rollover, agent restart and authority outage | Workload API consumer preserves membership through rotation, rejects invalid credentials and uses no file-credential fallback |
| INT-WB-05 | Provider membership loss or provider SVID presented to a local service | Provider denial leaves local identity intact; cross-domain authority is rejected |

A file-backed prototype registry or synthetic SVID test is useful software
evidence only. It does not demonstrate production inventory authentication,
physical attestation, offline rollback protection or an adopted SPIRE service.

## Proposed DNS workload authorization

`tests/test_dns_authorization.py`, `tools/dns_authorization.py`, and the
`dns-authorization-*` corpus check the closed success response, canonical peer
tuple, independent numeric DNS assignment, exact five-second interval, nonce
and peer correlation, configured-zone matching, and strict expiry boundaries.
The request fixture is context for an RPC, not another durable record family.
Structural validity does not establish authenticated transport, freshness of
the underlying registry query, or one-time use.

| ID | Runtime scenario | Required owner/result |
| --- | --- | --- |
| INT-DNS-AUTH-01 | Unlisted controller or unexpected registry SPIFFE identity, even under a trusted CA | Registry/controller deny before DNS desired-state mutation |
| INT-DNS-AUTH-02 | Fresh SVID but missing permission, inactive/replaced enrollment, or absent/conflicting assignment | Fleet checks one current PostgreSQL statement snapshot and denies |
| INT-DNS-AUTH-03 | Quarantine/retirement/permission removal commits before the next request on an existing TLS connection | New registry query denies; an earlier authorized in-flight request may finish |
| INT-DNS-AUTH-04 | Wrong response nonce/peer/name, future/expired timestamp, wrong interval, malformed response, redirect, denial or registry outage | Controller fails closed without legacy or file-registry fallback |
| INT-DNS-AUTH-05 | Two incoming requests within five seconds, including retry or reused TLS | Distinct fresh request nonces and live registry checks; no cached/reused response |
| INT-DNS-AUTH-06 | Nonnumeric logical ID and replacement instance with an existing numeric DNS assignment | Preserve assigned `pi-<ID>` name and DNS idempotency/write-precondition semantics |

Producers and consumers provide their own integration evidence for these
scenarios. Offline tests and a valid DTO do not satisfy production adoption,
hardware qualification, or an actual deployment gate.

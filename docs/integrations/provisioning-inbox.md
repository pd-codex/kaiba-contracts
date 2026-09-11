# Development provisioning → controller inbox

Status: experimental adoption profile, `development-retained-export/v1`.
This profile uses `ProvisioningRecord` **0.1.0-draft.1** without changing any
schema or existing contract acceptance rule. It implements observation ingestion;
it does not claim completion of PR-06's live authority verification gate.

## Ownership

| Project | Owns | Handoff |
| --- | --- | --- |
| kaiba-provisioning | Physical workflow, control state, independent audit source, export adapter | Immutable ProvisioningRecord and privately retained evidence |
| kaiba-contracts | Shared record semantics and this experimental mapping | Pinned schemas, mapping, cross-project fixture |
| kaiba-controller | Durable inbox, revision history, observation assessment and scoped queries | Candidate observations with explicit admission blockers |
| kaiba-flow | Presentation and user intent | Read candidate/history API; future publication requests |

The first transport is an operator-side export and import command. It does not
alter station/lane authentication, grant the controller station credentials,
register an identity, or dispatch work. A controller process must never receive
physical-operation credentials merely to render a candidate.

## Exact mapping

Source control schema: `provisioning.kaiba.network/control-transaction/v1alpha4`.
The deployment's operator-reviewed policy pins the source commit, profile ID,
bundle digest, policy digest, tenant, domain, authority and three evidence refs.
A profile name containing “production” is not qualification evidence.

| ProvisioningRecord | Source / rule |
| --- | --- |
| `record_id` | `provisioning-` + lowercase SHA-256 of UTF-8 `authority_id + NUL + tenant_id + NUL + security_domain_id + NUL + transaction.id` |
| `revision` | `transaction.resource_version`; no adapter counter |
| `issued_at` | `transaction.updated_at`, UTC, truncated to microseconds; never export wall-clock time |
| Scope and authority | Reviewed deployment policy, never an import payload's choice |
| `correlation_id` | Exact source transaction ID |
| `asset_ref` | Source `asset_id`, inventory correlation only |
| `source.transaction_id`, `source.state` | Exact `id` and raw `status` |
| `source.repository`, `source.commit` | Source repository and configured exact deployment commit |
| `source.profile_ref`, `posture_ref`, `release_ref` | Immutable reviewed policy references; source profile/bundle/policy must match the configured pins |
| `purpose`, `cohort` | `candidate_evidence`, `development` in this first profile |
| Readiness | Both false; `approved-development-only` and `live_authority_verification_required` |
| Terminal development reasons | Also `development_asset`, `rollback_unimplemented` |
| Other outcomes | Also `source_state:<raw status>`; unknown states remain observable and blocked |

Export policy is immutable for a source transaction. Changing its metadata or
retained bytes without a source revision is an export conflict, not a reason to
silently replace the snapshot. The identity namespace must change if an authority
resets its transaction IDs or versions. `intended_logical_id` is never promoted
to an active DeviceBinding.

## Retained evidence and trust

The record exposes only an allowlist. Private evidence contains the typed control
transaction and selected audit records, serialized once by the source's Go JSON
encoder. These are new retained export artifacts, not re-encoded signed envelopes.
Existing upstream hashes and times inside them remain unchanged.

`evidence.control_record` references that retained control transaction.
`evidence.audit_receipt` references an ordered JSON array of exactly the audit
records underlying every receipt referenced by current approval, operation
approval/intent/evidence/reconciliation, quarantine, abort and security-applied
state. Empty history is `[]`, not invented success evidence. Each receipt ID is
upstream SHA-256 of `kaiba-audit-receipt + NUL + event_hash`.

Only audit records already bound into control participate. An unrelated later
audit append cannot alter an exported revision. Export brackets audit selection
with equal control reads. The offline command opens both stores using their
existing validators; control is reopened for each read and audit validates its
full retained chain. Export has a store adapter whose `Save` always fails.

Evidence URIs in this profile are `urn:kaiba:evidence:sha256:<hex>`. The resolver
uses separate configured `control`, `audit` and `policy` directories and the
fixed filename `<hex>.json`. It verifies exact bytes before parsing. No embedded
URL is fetched. Private evidence includes capability-like audit lookup metadata;
it is not returned by candidate/history APIs. Real evidence must not be checked
into a repository; the shared rehearsal contains synthetic values only.

**Digests establish integrity, not authority.** The pilot relies on an
operator-controlled import and protected, authority-supplied evidence directories.
Copying all evidence from an untrusted uploader does not authenticate anything.
The controller checks scoped source pins, reference hashes, individual upstream
event hashes, receipt membership and terminal bindings. Selected records are not
a proof of the complete audit chain, independent retention, current authority
state, signing authority, fresh device authentication or hardware qualification.
These missing properties remain explicit blockers even after successful import.

## Inbox behavior

- Import selects a configured authority outside the payload. A scope mismatch is
  rejected under that authority's configured scope, without cross-tenant reads.
- Full records use the shared RFC 8785 digest. Exact logical retry is duplicate;
  the same revision with different content is `idempotency_conflict`.
- One durable transaction stores a new snapshot, latest-candidate pointer and
  acceptance history. A crash before commit cannot leave partial acceptance.
- Previously unseen older revisions or time regressions are `stale_state`.
  A previously accepted older revision can be acknowledged as a duplicate without
  moving the latest pointer backwards. Gaps in source revisions are allowed.
- Malformed, unsupported, missing-evidence, mismatched-policy and conflicting
  imports retain a scoped rejection reason. Bounded raw rejected input is private.
- Historical observations may enter the inbox; source age is recomputed on reads.
  Stale observations and disabled sources remain visible with blockers.
- No candidate is eligible for production admission. Receipt of a candidate is
  distinct from verification, identity binding, enrollment and publication.

## UI read boundary

The first controller exposes authenticated, fixed-tenant/domain queries:
`GET /api/v1/candidates`, `GET /api/v1/candidates/{record_id}/history`, and
`GET /api/v1/imports`. Responses paginate with `limit`, `offset`, `next_offset`.
The candidate view has the original `record`, its JCS `digest`, `received_at`,
`evidence_status: retained_evidence_checked`, `source_age_seconds`, and
`admission: {eligible: false, reasons: [...]}`.

These query envelopes are controller-owned experimental views, not newly
standardized shared contracts. Flow must render source state, source-observed
readiness and controller admission blockers separately. Its server-side adapter
holds read credentials; browser bundles must not contain controller tokens.

## Next gate

Before enabling enrollment or publication: implement authenticated live control
and independent audit resolvers with bounded freshness and invalidation; bind the
candidate's fresh device proof through DeviceBinding; then consume active bindings
when freezing publication targets. Agree those runtime contracts before adding
privileges. Completion evidence must not become a circular prerequisite for the
identity activation that source completion itself requires.

The generated fixture `examples/valid/provisioning-export-development.json`
comes from a simulated seven-operation workflow using real provisioning control
and audit services at baseline `8d0ed51a8177f1431f4e6ff992df811fc134344d`.
The controller repository retains its synthetic evidence and reproducible runner.

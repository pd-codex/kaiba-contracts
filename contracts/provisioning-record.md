# ProvisioningRecord

**Producer:** provisioning control, with independent audit evidence.
**Consumers:** identity inventory, admission and audit.
**Schema:** [provisioning-record.json](../schemas/0.1.0-draft.1/provisioning-record.json).

## Meaning and fields

A secret-free snapshot of a named source transaction and the evidence supporting
its reported outcome. It supplies input for review and conveys no mutation,
identity issuance, enrollment, or fleet-access authority.

| Field | Meaning |
| --- | --- |
| Common record fields | Immutable identity, revision, authority and scope |
| `purpose` | `candidate_evidence` or `completion_evidence`; explicitly distinguishes intermediate evidence from final completion |
| `asset_ref` | Inventory correlation supplied by the producer; never proof of device identity |
| `cohort` | `development`, `test`, or `production` under the stated security domain |
| `source` | Exact source repository commit, transaction ID, raw state, profile, posture and release evidence references |
| `readiness` | Source-observed `production_ready`, `enrollment_ready`, and reasons; not a consumer's admission decision |
| `evidence` | Independently retained control record and audit receipt references |

## Producer obligations

- **PR-01:** Preserve the upstream transaction ID, exact source state and evidence
  bytes. The adapter MUST NOT translate `security_applied` into `complete`.
- **PR-02:** Development and test cohorts MUST report both readiness flags false.
  A false readiness flag MUST have a reason. Enrollment-ready implies
  production-ready, but neither boolean alone is proof of the claim.
- **PR-03:** `completion_evidence` MUST describe an authoritatively completed
  source workflow, including its required identity and audit outcomes. The
  current development terminal outcome remains `candidate_evidence` here.
- **PR-04:** Unknown, incomplete, quarantined, or unreconciled source outcomes
  MUST remain visible and cannot acquire stronger readiness through export.
- **PR-05:** Updating a source observation creates a new immutable record revision.
  Re-exporting an existing revision preserves its content and digest.

## Consumer obligations

- **PR-06:** Authenticate the producer and independently verify control/audit
  bindings, source profile, approved posture, scope, freshness, and current
  transaction state before relying on the record.
- **PR-07:** Bind the actual candidate to fresh bootstrap authentication and key
  proof under the identity contract. A hostname, serial, MAC, USB observation,
  or browser-uploaded file cannot perform this binding.
- **PR-08:** A schema-valid development record is useful audit input and MUST be
  denied production admission. Production eligibility requires independently
  established platform qualification, active identity and current admission
  policy in addition to any readiness claim.

## Lifecycle and failures

The upstream workflow owns its state machine. This contract does not invent
replacement terminal states or a new retry path. Candidate evidence may precede
identity activation; completion evidence may follow it. Consumers must not form
a circular prerequisite between final completion and the activation it requires.

An unknown transaction outcome returns a reconciliation requirement. Export
retry may return the same verified record; it MUST NOT repeat a physical action.
Evidence mismatch, missing audit, stale authority or readiness inconsistency
blocks further authorization and preserves the rejected record for scoped audit.

## Upstream mapping and status

At the [pinned provisioning baseline](../docs/sources.md),
`approved-development-only` reaches `security_applied`, classifies the release as
`development_asset`, and retains `rollback_unimplemented`. Both readiness flags
remain false. No fleet export endpoint currently implements this proposed
adapter. Production `completion_evidence` examples are hypothetical; their
source-state strings do not add states to the provisioning implementation.

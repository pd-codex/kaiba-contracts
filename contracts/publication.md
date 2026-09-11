# Publication and PublishRequest

**Request producer:** flow UI or another authorized client.
**Record producer:** publication authority.
**Consumers:** release execution, UI and audit.
**Schemas:** [publish-request.json](../schemas/0.1.0-draft.1/publish-request.json)
and [publication.json](../schemas/0.1.0-draft.1/publication.json).

## Meaning

Publication is durable acceptance of exact reviewed intent. It does not assert
that artifacts exist, a signer approved them, a device was assigned, or anything
is running. An accepted Publication is immutable; progress is a separate
attempt-correlated observation. Cancellation and later supersession do not erase
the original acceptance fact.

## Request

| Field | Meaning |
| --- | --- |
| `contract`, `contract_version` | Exact request schema version |
| `plan_ref` | Immutable reviewed DeploymentPlan reference and digest |
| `targets` | Ordered eligible targets: logical device, instance, storage generation and expected desired-state revision |
| `idempotency_key` | Stable key for this logical publication request |

The authenticated transport context supplies the actor and tenant. They are not
caller-selectable request fields. Expected revision `0` means the instance has
never had a desired-state assignment; controllers must not reuse it after deletion.
No duplicate device or instance may appear. The request target list must exactly
match the plan's reviewed eligible list; its declared exclusions stay in the plan.

## Accepted record

Publication adds the common record envelope, `status: accepted`, `actor_id`,
`authorization_ref`, `request_digest`, the same plan/targets/idempotency key,
and `accepted_at`. The request digest covers the complete canonical request,
including its idempotency key. Acceptance precedes or equals record issuance.
Publication revision is `1`; mutable execution status lives elsewhere.

## Acceptance transaction

1. **PUB-01:** Authenticate the caller and enforce current tenant/operation scope.
   Resolve the idempotency identity before creating new work.
2. **PUB-02:** Load the exact reviewed plan from its authoritative store; verify
   ID, revision, digest, version, tenant, security domain and current validity.
3. **PUB-03:** Require exact eligible-target equality, effective input bindings,
   required approvals and current admission. Replacements and newly eligible
   devices cannot be silently substituted.
4. **PUB-04:** Compare every expected desired-state revision against current
   authoritative state. Changed target scope, expired review, policy denial or a
   conflicting revision rejects acceptance of the entire request. The operator
   may review a new smaller plan; the server does not invent one.
5. **PUB-05:** Durably commit the request identity, accepted record and recoverable
   execution intent as one acceptance outcome. Crash recovery must discover
   accepted but undispatched work. A success response requires this durability;
   a particular database or message broker is not prescribed.
6. **PUB-06:** Return the stable publication ID and accepted status. Build,
   signing, assignment and confirmation have separate records and gates.

Acceptance is all-or-nothing for the reviewed eligible list. Execution may later
fail or defer individual targets and reports that fact without rewriting scope.
Acceptance is not a perpetual authorization lease: assignment must recheck current
policy, exact instance and expected desired-state revision. Concurrent accepted
publications may race; only an assignment passing the current compare-and-swap
can advance desired state. Others report conflict/supersession, never overwrite.

## Idempotency and failure behavior

The key's scope is `(authenticated tenant, authenticated actor, publish operation,
idempotency_key)`. After authentication and structural validation, the service
durably binds that scope/key to the canonical request digest before acceptance
checks. Same scope/key plus identical canonical request returns the
original accepted outcome without another job, even if devices have since changed.
Current access is still required to retrieve it; replay does not reauthorize
execution. A different digest under that key returns `idempotency_conflict`.

An in-flight duplicate joins or retrieves the durable acceptance decision. A
timeout/lost reply means unknown to the client: retry the identical request/key
or query its status. Never generate a new key automatically after a timeout.
Retain bound keys and conflict tombstones, including pre-acceptance rejections,
for the lifetime of the tenant's publication history; they must not become
reusable after routine log cleanup.
Authentication/structural errors do not reserve keys. A definitive pre-acceptance
rejection creates no publication or work; retry can succeed later only after all
current checks pass. Services must serialize rejection with any competing
acceptance of that same key.

Rejection categories include `invalid_record`, `scope_mismatch`, `stale_state`,
`policy_denied`, `conflict`, `idempotency_conflict`, and `dependency_unavailable`.
Transport response/envelope formats remain undecided. Errors identify remediable
conditions within the caller's scope and never claim a device-side rollback.

## Required fulfillment guarantees

BuildResult must bind complete effective inputs to exact artifact digests.
AuthorizedRelease independently approves those bytes. DesiredAssignment is
instance-bound with an attempt and validity conditions. Confirmation requires
the observed release, required health checks and independent policy appraisal.
None of these obligations are implemented by the schema validator.

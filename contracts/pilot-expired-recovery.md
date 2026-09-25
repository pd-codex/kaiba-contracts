# Proposed supervised recovery after pilot expiry

This additive **0.4.0-draft.1** slice defines `PilotRecoveryAuthorization` and
`PilotRecoveryKeyChallenge`. It specifies approval and proof of the existing key
only. [Recovery issuance, installation and cutover](pilot-recovery-cutover.md)
define the remaining record linkage; runtime adoption is still required. Fleet owns the
authority/issuer; provisioning owns the protected device client. Both must adopt
exact contract pins and demonstrate integration before a reviewed live operation.

## Eligibility and preserved identity

Normal renewal remains `same_key_unexpired` under 0.3. Recovery has a distinct
contract and mode `supervised_same_key_expired`. Its predecessor is the exact
currently selected binding/certificate whose access expired; its stored binding
state must still be `active`. Here that state identifies the historical selected
record, not current permission to access services. Revoked, quarantined, retired,
superseded, unknown or replaced memberships cannot use this path.

Fleet derives `predecessor_access_expires_at` from authenticated stored certificate
and original policy/decision expiry, taking their earliest deadline. An expired
admission can therefore require recovery while its certificate is still valid.
Do not take this timestamp from a caller, stale cache or an outage response.
Withdrawal, failed evidence or unreachable authorities are not expiry. Reject
inconsistent historical records and any runtime revocation/quarantine marker.
Record digests, certificate DER digest and current credential revision must match
retained authority history. A legacy 0.2 credential has revision 1.

The authorization retains logical device, instance, target, tenant/domain,
audience, profile, permissions, credential slot, SPKI, key generation and storage
generation. It advances only credential revision by one. It cannot recreate an
enrollment, rotate a key, restore a revoked identity or confer full qualification.
Original records, certificate and diagnostic history remain retained.

## Fresh approval and records

An authenticated configured operator authorizes the exact operation and retained
predecessor. Fleet records the authenticated `approver_id` and a content-addressed
`review_ref`; callers cannot self-assert approval by supplying those strings.
The reviewed scope must explicitly permit expired same-key recovery for this
asset, instance, predecessor and operation. This approval is distinct from
approval of the original enrollment or a transport-certificate refresh.

Resolve current adoption, policy, decision and evidence through their authenticated
authorities. Enforce accepted gaps, observation freshness and withdrawal checks.
The original expired policy/decision cannot authorize a successor. Fresh records
must permit the same scope; references and target must match the authorization.
The new window is positive, at most seven days and bounded by fresh admission and
policy. A seven-day limit never overrides evidence-age or certificate limits.

## Management relay and proof

Keep ordinary mTLS certificate validation unchanged. The expired device certificate
is an historical binding input, never an authentication exception. A currently
valid, independently authorized management principal relays the challenge and
signature over the reviewed management path. Management credentials alone do not
prove possession of the device key. The device key remains on its protected mount;
no private key export or recovery credential is required for this protocol.

Fleet generates a fresh 192-bit nonce and the `PilotRecoveryKeyChallenge`, purpose
`pilot_expired_recovery_key_possession`, with an exclusive expiry at most five
minutes after issue and no later than authorization expiry. The challenge binds
operation, instance, authority, tenant/domain, exact authorization, predecessor
binding/certificate and SPKI. The client verifies every binding against protected
local state and the reviewed management configuration before signing. Persist the
accepted operation and proof before transmission; changed challenges for that
operation are rejected rather than signed again automatically.

Proof uses standard-base64 ECDSA ASN.1 over SHA-256 of RFC 8785 canonical bytes of
the entire challenge, with the retained P-256 key. Fleet verifies it against the
stored predecessor public key, independently of the relaying principal. Normal
renewal proofs and installation proofs have different purposes and cannot be
substituted. Exact repeats reconcile the original result; changed signatures or
content conflict. Reconciliation never refreshes nonce, approval or deadlines.

Before accepting proof, recheck the operator's scope, current selected predecessor,
fresh successor records and current denial state. Serialize with renewal,
revocation, quarantine and cutover. Reserve a predecessor across **both** renewal
and recovery modes: a new mode or operation ID cannot bypass a consumed/uncertain
operation. Existing abandoned operations require separately reviewed resolution.

## Subsequent implementation gates

Proof verification alone grants no relying access and no signing permission.
The [recovery cutover contract](pilot-recovery-cutover.md) specifies the issuer
reservation, successor binding, installation proof and atomic history transition.
Fleet/issuer and protected-client implementation, real-service integration and
reviewed live execution remain separate gates. No automatic signing retry is allowed.

## Conformance and compatibility

`tools.recovery.validate_pilot_recovery` checks offline linkage, deadlines,
identity and fresh fixture handoff. `validate_recovery_challenge` checks challenge
bindings and time. These helpers do **not** authenticate an approver, resolve live
records, verify signatures or establish runtime membership state. Runtime facts
passed to them must come from authenticated authoritative state.

The new schemas use exact dispatch; existing 0.1/0.2/0.3 schemas and enum values
are unchanged. Pinned consumers reject 0.4 until they adopt it. Existing normal
renewal tests still reject expired predecessors. Examples are fictitious and grant
no access to any live pilot.

Required fleet/client integration includes disabled-default routes; unauthorized
relay/operator; substituted review, target, predecessor, SPKI and nonce; invalid,
replayed, wrong-purpose and expired proofs; stale/withdrawn successor evidence;
revocation/quarantine before and during issuance/cutover; conflicting pending normal
renewal; restart and response-loss reconciliation; retained signing uncertainty;
restored database/client history; and denial of expired/staged/old credentials on
ordinary endpoints. No runtime or hardware result is claimed by this PR.

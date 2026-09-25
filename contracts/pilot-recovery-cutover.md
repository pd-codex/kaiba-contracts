# Proposed expired recovery issuance, installation and cutover

This completes the record linkage following [recovery approval and key proof](pilot-expired-recovery.md).
The 0.4 draft family adds a recovery successor `PilotDeviceBinding` and
`PilotRecoveryInstallationReceipt`. All are proposed wire contracts: fleet/issuer
and provisioning/client implementation and real-service integration remain required.
They do not restore any live pilot's access by merging.

## Issuance boundary

A current recovery authorization alone cannot trigger signing. The issuer must
read the exact durable, proof-verified recovery operation from authenticated fleet
management access, verify its configured inventory authority, operator/review scope,
and match an explicitly installed recovery issuance grant. A normal-renewal grant
is insufficient. Revalidate current successor evidence, admission, policy and
expiry and the exact selected predecessor's binding, certificate digest, revision,
SPKI and denial state. Earlier expiry is expected; revocation, quarantine, unknown
state, withdrawal or outage is not permission to recover.

Signing must share the existing durable predecessor reservation and signing ledger
with normal renewal. Mode is part of the immutable request/grant digest, not a
separate namespace that permits another attempt. A predecessor can have only one
successor reservation across both modes. Preserve original issuance and all prior
grants. Idempotent reads return the original bytes; changed content conflicts.
An uncertain signing attempt stays uncertain and blocks another automatic sign,
even if an operator supplies a new ID. Resolution/cancellation requires a separate
reviewed transition and cannot discard evidence.

The successor certificate retains the same key, identity, issuer and usages. Give
it a distinct serial and DER digest and a current validity interval wholly within
the recovery authorization, CA lifetime and fresh policy/admission limits. The
issuer independently verifies uniqueness and actual certificate contents. Offline
fixture comparisons alone do not establish these properties.

## Staged binding

Create a distinct 0.4 binding with `recovery_authorization_ref` and the exact
`predecessor_binding_ref`. It retains logical device, instance, bootstrap identity,
target, tenant/domain, storage/key generations, SPKI, slot, issuer, audience,
profile and permissions. It increments credential revision by exactly one; the
binding snapshot revision is separate. The authority and correlation operation
match the authorization. If `supersedes` is supplied it names that predecessor.

The binding starts `staged`, without activation or installation receipt, and uses
fresh adoption/policy/decision references from the authorization. The expired
predecessor remains denied. A staged successor receives only installation-protocol
access, never ordinary fleet access. The client validates every field and the
actual certificate before durably saving pending state on its protected mount.
Neither old enrollment nor prior credential/proof history is overwritten.

## Installation proof and receipt

A new client process loads the exact saved successor and proves possession using
its currently valid certificate. This is a client-process restart, not an OS reboot
or hardware qualification. Normal TLS verification remains enabled. No expired
certificate authentication exception is introduced.

The challenge signature input is RFC 8785 canonical JSON containing exactly:

- `purpose`, fixed to `pilot_expired_recovery_installed_key`;
- `operation_id`, `authorization_ref`, `predecessor_binding_ref`,
  `staged_binding_ref`, `certificate_digest`;
- `nonce` (fresh random 192 bits), `challenge_issued_at`,
  `challenge_expires_at`, `restart_kind` (`client_process`);
- `tenant_id`, `security_domain_id`.

Sign using the retained P-256 key with ECDSA ASN.1 over SHA-256; encode the signature
as canonical standard base64. The client checks the exact challenge against its
protected pending operation before signing. The verifier checks certificate chain,
lifetime/usages/identity, exact successor DER digest, signature and current operation.
The exclusive challenge deadline is at most five minutes after issuance and no
later than either successor certificate or authorization expiry. Recovery key proof,
normal-renewal installation proof and enrollment proof cannot substitute for this
purpose, even though the same key signs them.

Only the configured trusted verifier may emit `PilotRecoveryInstallationReceipt`.
It contains the operation, exact authorization/predecessor/staged references,
successor digest, retained proof evidence reference, nonce and times. Verification
occurs within the challenge window and receipt issuance follows verification.
`full_qualification` stays false. A caller-supplied receipt or proof hash alone is
never sufficient evidence of successful installation.

## Atomic cutover and interruption

The active snapshot retains every staged tuple field, advances its snapshot
revision by exactly one, and adds activation plus the exact installation receipt
reference. Activation names that receipt's canonical digest and the successor
policy and follows verified installation. The receipt is at most five minutes old
at cutover. Recheck the authorization, fresh admission and all current denial state
at this step; a once-valid historical proof cannot override later revocation.

Under the same serialization lock used by renewal, revocation and quarantine,
compare the selected predecessor/operation and atomically record the active
successor, current credential revision and predecessor supersession. Re-evaluate
current revision for every relying request, including existing TLS connections.
There is no overlap where the expired predecessor becomes usable. A staged or
revoked successor must also be denied on ordinary endpoints.

On lost responses, restart or restored backups, reconcile the exact operation and
certificate bytes. Keep durable pending client state until the active result is
verified; no second signature, new operation or fresh enrollment to escape an
ambiguous result. Preserve all prior issuer ledger and client credential history.
An expired authorization before cutover stops this operation; approval timestamps
and certificates are never edited in place. A backup preceding cutover cannot be
served as current state without explicit reconciliation of the known history.

## Compatibility and required integration

0.1–0.3 schemas are unchanged. A 0.4 binding has a recovery authorization reference,
not a normal-renewal reference; exact dispatch rejects the wrong family. The generic
binding transition checker cannot replace its certificate, credential revision or
recovery identity. After successful recovery, normal renewal may use the current
0.4 predecessor while it is unexpired and issue a normal 0.3 successor. Subsequent
expired recovery may also use a 0.4 predecessor with exact revision/digest checks.
Neither mode resets generation or history.

Offline validators in `tools/recovery_cutover.py` check schema/linkage, preserved
tuple, temporal ordering and revision advancement. They do not authenticate a
verifier, validate actual certificate signatures, serialize transactions or prove
current runtime state. Supplied predecessor facts must come from the authority.

Before deployment, real fleet/issuer/client tests must cover both initial and
successive predecessors; management-only recovery transport; disabled-default
routes; unauthorized principals; old/staged credential denial; wrong-purpose,
wrong-certificate and expired proofs; changed records and unavailable authorities;
normal-renewal/recovery reservation conflicts; revocation and quarantine racing
signing/cutover; uncertain signing; interrupted installation/cutover; same-byte
reconciliation after restart and database restore; and ordinary renewal following
recovery. Live execution needs a reviewed packet and a recoverable current backup.

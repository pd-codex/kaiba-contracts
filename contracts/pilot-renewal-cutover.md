# Pilot renewal installation and cutover — proposed 0.3.0-draft.1

This completes the proposed record linkage after
[PilotRenewalAuthorization](pilot-renewal-authorization.md). It adds a versioned
successor `PilotDeviceBinding` and `PilotRenewalInstallationReceipt`. Producers
and consumers have not adopted these records; tests here establish offline
consistency only. No live identity, certificate, policy or service is changed.

## Successor binding

A 0.3 binding is a new record for one successor certificate, with a record ID
distinct from its predecessor. It retains the same logical device, instance,
bootstrap identity, target, storage/key generation, SPKI, slot, issuer, audience,
profile and permissions. `credential_revision` increases by one independently
of the binding snapshot revision. `certificate_digest` identifies the actual
successor DER bytes and the serial must differ from the predecessor. An issuer
must independently ensure serial uniqueness and validate the actual certificate;
offline digest/serial comparisons do not establish those properties.

The binding references the exact renewal authorization and predecessor binding.
Successor adoption, policy and admission references match the authorization. Its
certificate is currently valid and contained in the approved interval; delayed
installation never moves the deadline. Issuer CA and transport validity remain
runtime checks. The state starts `staged`, without activation or installation
receipt. A staged credential has only the narrowly scoped installation protocol,
not ordinary fleet relying access.

The generic binding-transition validator still forbids replacing a credential
within one binding record. Renewal uses a distinct successor record and the
explicit linked renewal validator. Older 0.2 bindings can be predecessors of
this first renewal; a later 0.3 predecessor must also agree with the verified
runtime certificate digest and credential revision.

## Installation receipt

A configured trusted verifier emits `PilotRenewalInstallationReceipt` only after
verifying possession of the same private key using the exact installed successor
certificate. It records the exact operation, authorization, predecessor, staged
binding and successor certificate digest, plus the proof evidence reference.
`purpose` is exactly `pilot_renewal_installed_key`; bootstrap or old installed-key
proofs cannot be substituted. Full qualification remains false.

The challenge carries a random 192-bit nonce, issuance and exclusive expiry
within five minutes. Signature input is RFC 8785 canonical JSON of all these
fields, with the exact field names shown below:

- `purpose`, `operation_id`, `authorization_ref`, `predecessor_binding_ref`,
  `staged_binding_ref`, `certificate_digest`, `nonce`, `challenge_issued_at`,
  `challenge_expires_at`, `restart_kind`, `tenant_id`, `security_domain_id`.

The device verifies all bindings against its protected pending state before
signing with ECDSA P-256 over SHA-256 of that canonical input. The proof evidence
must retain the challenge and signature; the verifier must check the actual key,
certificate issuer/lifetime/usages/identity, signature and pending operation.
`proof_ref` is a retained evidence reference, not a substitute for verification.
A receipt schema match or caller-supplied authority ID proves none of this.

`restart_kind: client_process` requires a new client process after durable
installation. It is not an OS reboot or independent hardware attestation. The
receipt's verification time is supplied by the verifier's trusted clock and is
inside the challenge window; receipt issuance follows verification.

## Atomic cutover and history

The active snapshot keeps every staged tuple field unchanged, advances its
snapshot revision by exactly one and includes `installation_receipt_ref` plus
activation. Activation references the same receipt's JCS digest and successor
policy; it follows verification and the receipt is at most five minutes old at
the current check. The predecessor must still be current, active and unexpired
for this normal-renewal mode. An expired/revoked predecessor cannot be revived
by presenting an otherwise valid historical receipt.

Runtime cutover must atomically set the instance's current credential revision,
record the new active binding and supersede the predecessor. Every relying
request resolves that current revision, including requests on an already-open
TLS connection. The old certificate is denied after cutover. Offline records
cannot implement transaction serialization or prove that server behavior.

Store original issuance, staged and active snapshots, proof, receipt and cutover
history durably. Lost responses reconcile the same operation and exact bytes.
Do not create another operation, key or signature to escape ambiguity. Pending
client state must survive interrupted installation without overwriting the last
working credential; a committed server cutover must reconcile without reissuing.

## Compatibility and acceptance

Legacy 0.1/0.2 schemas are unchanged. 0.3 bindings require explicit version dispatch;
a legacy consumer must reject them. Existing active bindings are not rewritten
in place on upgrade. The 0.3 schema set remains proposed until both owners adopt
an exact pin and pass shared integration tests. No stable version is released.

`tools/renewal.py` checks linked staging/cutover, with synthetic fixtures in
`examples/valid/pilot-renewal-{staged,installed,active}-a.json`. It checks exact
references, temporal ordering, unchanged tuple, record revision and windows.
`tests/test_renewal_cutover.py` rejects staged-as-active, missing/stale or
substituted receipts, changed successor identity, expired/revoked predecessors
and implicit certificate replacement. It does not verify signatures.

Before live use, fleet native integration must exercise actual proof validation,
wrong-certificate/role replay, concurrent renewal/revocation, retained-connection
predecessor rejection, interruption at every durable boundary, same-byte issuance
reconciliation, restored history and exact deadline denial. Run these against
both initial 0.2-to-0.3 renewal and subsequent 0.3-to-0.3 renewal. Publication of
these contracts alone does not make a service renewable.

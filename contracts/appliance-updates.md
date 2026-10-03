# Production appliance protocol (0.7.0-draft.1)

This additive family supports the approved outbound appliance update design.
Existing families, VERSION, pilot restrictions and historical evidence remain
unchanged. The Go reference runtime is `runtime/appliancewire`; schemas and Python
checks establish structural consistency only. They do not authenticate witnesses,
admit a device, attest a running release, or close a hardware acceptance claim.

## Records and purposes

| Record | Purpose |
| --- | --- |
| ApplianceRelease | Two immutable A/B variants of one OS/application/catalog release; each variant contains four ordered complete ranges |
| ApplianceQualificationGrant | Operator-reviewed board, provisioning record, exact identity, layout and release transition before admission |
| ApplianceUpdateOffer | Monotonic attempt, current/target release, inactive slot, index/layout digest, production or exact qualification scope |
| ApplianceUpdateLease | Current certificate and exact offer digest; install or activate; five-minute start authorization |
| ApplianceUpdateReceipt | Durable journal sequence, complete readback, boot identity and bounded outcome |
| ProductionCredentialChallenge | Exact registered P-256 key, identity, provisioning record, purpose, predecessor, nonce and two-minute window |
| ProductionCredentialResult | Exact challenge digest and issued public certificate; installing it does not admit a device |
| SandboxLifecycle | Built-in signed catalog readiness/quiesce and state compatibility; no arbitrary application deployment |
| ApplianceDiagnostics | At most 128 fixed event codes with timestamps and typed attempt IDs; no free-form log contents |

All immutable identity fields include authority, tenant, logical device, physical
instance, profile, storage generation, credential slot, key generation and SPKI
digest. IDs cannot contain paths. Numerical fields use the RFC8785 exact-integer
range. Unknown properties, duplicate keys, noncanonical timestamps and unsupported
curves fail validation. Digests use `sha256:` plus lowercase hexadecimal.

## Authentication

A Signed envelope authenticates key_id and canonical payload with P-256 ECDSA
ASN.1 signatures. The signing input is the UTF-8 prefix
`kaiba.appliance/0.7.0-draft.1/<purpose>/<key_id>`, one NUL byte, and RFC8785 payload.
Purposes are release, offer, lease, credential-proof and credential-installed.
Release trust and update authority trust must be distinct installation inputs.
No record supplies trust keys, URLs, commands, disk paths or arbitrary offsets.

The reference integer-profile canonicalizer originated from Fleet's
`internal/wire/json.go` at 32d1efd261e7d8086285909b73a7f8a602f1e07e.
It deliberately rejects floating-point values rather than claiming a general
RFC8785 implementation. Python fixture validation also performs semantic bounds;
authenticated service consumers use the Go runtime.

## Credential lifecycle

A client certificate has one exact `kaiba-appliance://` URI produced by
CredentialURI, only digital-signature key usage and client-auth extended usage,
no additional names, the registered P-256 SPKI, and at most 30 days validity.
Configured production issuer trust must verify it. Every protected Fleet request
additionally matches the exact currently installed certificate in current
inventory. Renewal begins in the last ten days. Expired credentials never gain
ordinary mTLS access.

Initial enrollment requires independently approved registration. Recovery uses a
server-authenticated endpoint and a fresh challenge proved by the current retained
key. Revoked, replaced, quarantined, wrong-instance, changed-storage and changed-key
identities fail. A proved, already-dispatched issuance can reconcile after its
challenge expires; the issuer must provide the same result for the same operation.
Installation acknowledgements authenticate the entire result under a separate
purpose and are idempotent. No failed renewal generates a new key or instance.

## Update lifecycle and assurance

An offer alone authorizes no write. Starting install or activation always requires
a new live phase lease bound to the exact retained offer and current certificate.
The offer delivery window is at most 24 hours; the retained intent may outlive it
for deferred activation under fresh Fleet authorization. A dispatched phase may
finish after lease expiry. Qualification grants expire independently and cannot
be converted into production authorization by a client.

Write inactive boot, root, hash and metadata ranges only; reopen every complete
range independently. Journal intent before mutation and synchronize durable state.
A receipt is a device report, not remote attestation or independent physical proof.
A healthy trial must match root hash, release, catalog, protected volume, SPKI and
state format; confirm only after a subsequent normal boot. Both slots retain the
same private key and state format. Version one permits no destructive migrations.

Selector writes and pre-userspace watchdog recovery require independent native
qualification against the exact firmware/layout/reset design. The software
reference does not establish atomic FAT updates or native secure-boot acceptance.
Missing qualification blocks shipping media writers and rollout deployment.

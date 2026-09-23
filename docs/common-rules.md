# Common contract rules

`MUST`, `MUST NOT`, and `SHOULD` express proposed conformance requirements.
Implementations must satisfy both the written contract and its schema; a
contradiction is a contract defect to resolve, not permission to choose one.

## Records and references

Emitted records carry `contract`, `contract_version`, `record_id`, `revision`,
`issued_at`, `authority_id`, `tenant_id`, `security_domain_id`, and
`correlation_id`. IDs are opaque, case-sensitive values. Revision numbers are
monotonic within a record ID; every `(record_id, revision)` is immutable.
An issuance timestamp records history and never implies current authorization.

`RecordRef` binds `record_id`, `revision`, and `digest`. A consumer MUST retrieve
the named version from an authorized source and compare all three. The digest
of a Kaiba structured record is `sha256:` followed by lowercase hex over the
UTF-8 [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785) representation of the
entire record. There is no self-digest field. Signatures, if required by a
profile, wrap that digest externally with explicit signer role, scope, and
validity. Signature-envelope formats remain open; none of these unsigned
examples are signed credentials or grants.

`EvidenceRef` binds a URI and a SHA-256 digest of the exact evidence bytes as
retained by the evidence owner. Do not reserialize upstream signed evidence.
The URI is a locator, not a trust anchor or instruction to fetch an arbitrary
URL. Evidence retrieval uses an allowlisted authority and scoped access; never
follow embedded credentials or redirects into an unapproved authority.

## Encoding

Wire data is UTF-8 JSON, with no duplicate property names, NaN, infinities, or
invalid Unicode. Integer fields are limited to the exact interoperable range
0 through 9007199254740991, with stricter minima where specified. IDs, certificate
serials and digests are strings. No Unicode normalization is performed.
Timestamps use UTC RFC 3339 strings ending in `Z`, with seconds `00`–`59` and
at most six fractional digits; leap-second labels are outside this wire profile.
Objects reject unknown fields at this draft version. Date/time formats MUST be asserted by the validator;
Draft 2020-12 format annotations alone are insufficient.

Schemas use [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12).
Their `urn:kaiba:contracts:...` IDs are logical identifiers, not hosted services.
Consumers bundle the reviewed schemas and resolve references locally.

## Authority and freshness

Record fields are claims until authenticated against the authority registry and
current policy. A payload cannot nominate itself as a trusted issuer, choose its
tenant, or establish its own freshness window. Binding reads and policy checks
must account for quarantine, retirement, revoked issuers, certificate validity,
and superseded versions. A cache requires a bounded policy lifetime and a
revocation/invalidation mechanism. Unavailable required state fails closed for
new authorization.

Secret-free does not mean public. Inventory, audit references and actor metadata
remain access-controlled. This repository's examples use only synthetic data.

## Errors and retries

Common rejection categories are `unsupported_contract_version`,
`invalid_record`, `untrusted_authority`, `scope_mismatch`, `stale_state`,
`policy_denied`, `conflict`, `idempotency_conflict`, and `dependency_unavailable`.
They are proposed semantic categories; an HTTP status or transport envelope is
not prescribed. Authorization errors must not reveal another tenant's records.

Each mutation contract defines its own idempotency scope and reconciliation
behavior. Publication retry rules never relax the upstream provisioning lane's
execute-once journal, fence, approval, or ambiguous-outcome rules.

## Versioning

`VERSION` identifies the proposed contract set, currently `0.2.0-draft.1`.
Individual wire families retain their exact versions: ProvisioningRecord,
DeviceBinding, PublishRequest and Publication remain at `0.1.0-draft.1`; the
four new [pilot records](../contracts/pilot-enrollment.md) use `0.2.0-draft.1`.
The bundled validator enumerates these exact contract/version pairs. A different
combination is rejected, including an old record relabelled with the new version.
The old schemas and examples are unchanged. Consumers pin a commit or published
tag and explicitly enumerate supported families and versions. This PR does not
update runtime pins or publish a stable release.

After adoption, changes to fields, enums, defaults, authority, freshness,
canonicalization or acceptance semantics require a new reviewed contract version
and migration fixtures. Because schemas are closed, adding an optional field is
not automatically backward compatible. Documentation-only corrections may keep
the wire version only if they do not change accepted behavior; record the review.
Producer and consumer deployment order, overlap windows, rollback and retirement
must accompany each incompatible change.

# WorkloadBinding — proposed SPIFFE workload authorization

**Status: draft, unadopted wire family `0.5.0-draft.1`.** This additive contract
connects the Kaiba membership registry to relying services using SPIFFE workload
identities. It neither adopts a SPIRE deployment nor changes DeviceBinding or
pilot certificate-serial authorization. The [deployment decision](../docs/decisions/0006-spiffe-workload-bindings.md)
records the accepted direction and remaining integration gates.

## Producer, consumers and record

The Kaiba membership registry produces an authenticated, current assertion of
one workload's permission within an enrolled device instance. Relying services
consume it when authorizing an authenticated SPIFFE peer. SPIRE issues workload
credentials; Kaiba owns enrollment, membership and permissions.

The record carries the [common envelope](../docs/common-rules.md): `contract`,
`contract_version`, `record_id`, `revision`, `issued_at`, `authority_id`,
`tenant_id`, `security_domain_id`, and `correlation_id`. It additionally requires:

| Field | Meaning |
| --- | --- |
| `trust_domain` | Exact, configured SPIFFE trust domain authorized for the consumer |
| `logical_device_id` | Stable registry-assigned logical device identity |
| `instance_id` | Registry-assigned enrollment instance; replacement creates a new value |
| `workload` | Registry-assigned workload identifier within that instance |
| `spiffe_id` | Exact canonical URI derived from those four fields |
| `state` | `active`, `quarantined`, or `retired` workload membership |
| `permissions` | Unique list of permitted operations; initially only `dns:update` |

An empty permissions list is valid and authorizes no operation. Non-active
records may retain permissions for history; those permissions confer no access.
The schema is closed: no certificate serial, key material, SVID, arbitrary role,
readiness claim, or caller-selected enrollment grant can be added to this draft.
See the [schema](../schemas/0.5.0-draft.1/workload-binding.json) and
[synthetic active record](../examples/valid/workload-binding-active.json).

## WB-IDENTITY: canonical identity

The URI MUST equal, byte for byte:

```text
spiffe://<trust_domain>/device/<logical_device_id>/instance/<instance_id>/workload/<workload>
```

The three path identifiers contain 1–64 lowercase ASCII letters, digits,
underscores or hyphens; the first character MUST be a letter or digit. Dots,
slashes, colons, percent encoding, whitespace and Unicode are excluded.
`trust_domain` is 1–253 characters of lowercase ASCII DNS-label syntax: each
label contains 1–63 letters, digits or hyphens, begins and ends with a letter or
digit, and labels are separated by single dots. A single label is permitted.
Ports, trailing dots, underscores, user information, query and fragment are not
permitted. This is an intentionally narrow Kaiba namespace profile, not a claim
to accept every legal SPIFFE ID.

Consumers MUST reject aliases rather than lowercasing, URL-decoding, trimming
or otherwise normalizing them. The registry assigns identifiers; callers do not
derive membership from hostname or user-supplied request fields. Legacy opaque
IDs outside this grammar require a separately reviewed mapping before adoption;
they MUST NOT be silently rewritten.

## WB-AUTH: runtime obligations

A schema-valid record is **not a self-authenticating token or access grant**.
Its `authority_id` and timestamp are claims. A relying service MUST:

1. Authenticate the transport peer using a valid SPIFFE SVID and the explicitly
   configured trust bundle. Check certificate validity and the complete peer
   SPIFFE ID; a matching trust domain or valid CA chain alone is insufficient.
2. Retrieve current membership and enrollment state from its authenticated,
   authorized registry, scoped to the configured tenant, security domain and
   trust domain. The caller MUST NOT nominate the registry or supply its own
   assertion as a substitute. Missing, stale, conflicting or unavailable
   required registry state denies the request. `issued_at` alone cannot prove
   freshness; any cache must satisfy reviewed lifetime and invalidation policy.
3. Require the exact peer URI to equal `spiffe_id`, the workload binding to be
   `active`, and the same logical device and instance to remain actively
   enrolled. An active workload record cannot reactivate an old device instance.
4. Require the requested permission on **every request**, including subsequent
   requests on an existing TLS connection. Quarantine, retirement and permission
   removal cannot wait for credential expiry or connection teardown.
5. Apply the operation's resource scope. `dns:update` allows only existing
   assigned names for that logical device under the DNS service's current
   policy; it is neither arbitrary-zone write authority nor fleet administration.

SVID renewal/rekey changes transport credentials without changing this record's
membership tuple. It does not bypass current enrollment or permissions. Issuance
remains auditable, but this family does not activate each SVID serial. Authority
authentication, registry consistency, enrollment APIs, and issuance audit formats
remain owning-subsystem implementation obligations, not new wire fields here.

## Compatibility and validation boundaries

Only `WorkloadBinding` with `0.5.0-draft.1` dispatches to this schema. Existing
families retain their versions and exact credential checks. Records cannot be
upgraded by relabelling their version or interpreted as another family when
validation fails. Runtime consumers must explicitly opt into and adopt this
family; there is no credential-mode fallback.

Schema checks cover the closed shape, canonical component grammar, states and
permissions. Record-local validation checks the exact URI/component equality.
Offline fixtures cannot authenticate the registry, validate an SVID, prove live
enrollment, demonstrate per-request denial, or qualify hardware. Those are
separate [conformance scenarios](../docs/conformance.md#proposed-spiffe-workload-binding)
to demonstrate before adoption.

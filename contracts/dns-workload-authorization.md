# DNSWorkloadAuthorization — per-request registry check

**Status: proposed, unadopted RPC response `0.5.0-draft.1`.** The fleet registry
produces this response for an authenticated DNS controller checking one incoming
workload request. It is neither durable membership nor a bearer grant. It has
no common record envelope, revision, issuer claim, or lifecycle. Membership
remains in [WorkloadBinding](workload-binding.md) and current enrollment state.

## Authenticated request and success response

The controller sends `POST /api/v1/workloads/authorize-dns` to its explicitly
configured registry over mutual TLS. It verifies the registry's exact SPIFFE
identity and trust bundle. The registry accepts only explicitly allowlisted
controller SPIFFE identities in their configured trust and tenant/security
scope; belonging to the same trust domain is insufficient.

The UTF-8 JSON request is a closed object with exactly:

```json
{
  "spiffe_id": "spiffe://kaiba.network/device/device-fixture-001/instance/instance-fixture-001/workload/dns-updater",
  "request_id": "0123456789abcdef0123456789abcdef"
}
```

`spiffe_id` is the complete identity of the workload peer authenticated by the
controller, never a device request-body identity. It follows the exact
WorkloadBinding URI grammar and its workload component MUST be `dns-updater`.
`request_id` contains 32 lowercase ASCII hexadecimal characters, generated
fresh from 16 random bytes for each registry call. It is a correlation nonce,
not an idempotency key. The fixture nonce is synthetic, not a generation method.
The controller retains both request fields for checking the response.

A successful HTTP 200 response is the closed JSON object described by the
[schema](../schemas/0.5.0-draft.1/dns-workload-authorization.json). Every field
is required:

| Field | Required meaning |
| --- | --- |
| `contract`, `contract_version` | Exactly `DNSWorkloadAuthorization` and `0.5.0-draft.1` |
| `request_id`, `spiffe_id` | Exact echoes of the controller's retained request |
| `logical_device_id`, `instance_id` | Exact components of the canonical workload URI |
| `dns_device_id` | Independent persistent DNS assignment: 3–60 ASCII digits, retained as a string |
| `hostname` | Exactly `pi-{dns_device_id}.{configured zone}` |
| `permission` | Exactly `dns:update` |
| `checked_at` | Registry time at the authorization check against current state |
| `expires_at` | Exactly five seconds after `checked_at` |

Timestamps use canonical UTC RFC 3339 ending in `Z`, seconds `00`–`59`, and at
most six fractional digits. Hostnames and the configured zone use lowercase
ASCII DNS labels of at most 63 characters, with no trailing dot; total hostname
length is at most 253. The `pi-` prefix limits the numeric identifier to 60
digits. Leading zeroes are meaningful. Reject aliases rather than normalizing
them. The response has no `zone` field: the consumer uses its configured zone,
never a zone selected by the response or device.

The logical device ID may contain nonnumeric fleet identifiers such as
`device-fixture-001`. The registry stores its assigned numeric DNS ID separately;
it MUST NOT derive that ID from a workload URI or rename an existing assignment
when the enrollment instance changes. The producer and consumer both enforce
the assigned-name relation. This permission grants no other names, zones, or
fleet operations.

## Current state and request boundary

For each call, the registry checks the workload binding, the active enrollment
instance, and the DNS assignment from one current PostgreSQL statement snapshot.
The exact workload must be active, its logical device and instance must still
be actively enrolled, and `dns:update` must be permitted. Its assignment must
be present and unambiguous in the configured scope. No stale replica, fixture,
cached response, or caller-supplied record may stand in for required state.
Missing, inactive, conflicting, or unavailable state denies authorization.

The controller MUST, on every incoming DNS request including requests using
an existing TLS connection:

1. Revalidate the workload credential against current time and the configured
   trust bundle, then send a new registry request for that authenticated peer.
2. Authenticate the registry transport and require HTTP 200 with valid closed
   JSON. Reject redirects, malformed/unknown fields, duplicate keys, wrong
   family/version, and all non-success responses.
3. Require exact nonce and peer-identity equality, matching logical/instance
   URI components, the permitted workload, and the assigned hostname in its
   configured zone. Require `checked_at <= trusted now < expires_at` with an
   exact five-second interval. Future or stale responses fail closed.
4. Use the response only for that incoming request. Do not cache or reuse it,
   even inside the five-second interval. A retry makes a new authorization call
   with a fresh nonce; this does not alter the DNS API's existing idempotency or
   write-precondition semantics.

After quarantine, retirement, permission removal, or instance replacement
commits, the next authorization query observes the change and denies the old
workload. An in-flight request already authorized before that change may
finish. This protocol does not promise a global serialization barrier between
registry state changes and DNS publication.

Registry denial, timeout, invalid time, or dependency failure prevents the DNS
request from mutating desired state. Error bodies do not grant permissions;
their wire format is outside this success-response family. A valid response
cannot compensate for failed peer or registry authentication. It carries no
reusable signature or credential.

## Compatibility and evidence

This additive pair leaves `VERSION`, WorkloadBinding, and every enrollment and
pilot credential-tuple family unchanged. The existing WorkloadBinding prototype
fixture pin is not implicitly upgraded. Producers and consumers explicitly
adopt this RPC together; failure never falls back to a file registry or legacy
credential mode. This contract does not add permission-management APIs.

The common JSON encoding rules apply, but the durable record-envelope rules do
not. [Common rules](../docs/common-rules.md) describe this explicit exception.
The [decision](../docs/decisions/0007-per-request-dns-authorization.md) records
why the response is tied to one live exchange.

Offline schema and semantic checks cover closed shape, canonical identities,
name/ID consistency, and the five-second interval. The consumer helper checks
nonce, peer, configured zone, and caller-supplied time. None can prove random
nonce generation, authenticated TLS, current PostgreSQL state, absence of
caching, or one-time use. Those are the separate
[runtime conformance scenarios](../docs/conformance.md#proposed-dns-workload-authorization).
Passing this repository's tests establishes no deployment, production
adoption, or hardware qualification.

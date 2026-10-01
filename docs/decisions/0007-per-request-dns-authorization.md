# 0007: Check DNS authorization through one live registry exchange

Status: proposed additive RPC; runtime adoption remains separate.

The SPIRE prototype authenticates workloads and validates WorkloadBinding
fixtures, but the DNS controller needs current fleet membership and assigned
names. Fleet logical IDs are not necessarily numeric, while existing DNS names
use `pi-<numeric ID>`. Reinterpreting workload paths as DNS assignments could
rename devices or authorize the wrong names.

Use [DNSWorkloadAuthorization](../../contracts/dns-workload-authorization.md)
for one authenticated controller-to-registry call per DNS request. The registry
checks current enrollment, binding permission, and a separately retained DNS
assignment from one PostgreSQL statement snapshot. It accepts only allowlisted
controller identities. The response binds the authenticated workload and a
fresh request nonce and expires exactly five seconds after the check.

This is a transient RPC result, so it has no durable record envelope and is not
a signed bearer grant. The controller cannot cache or reuse it. Retained TLS
connections still require a new check on each incoming request. In-flight
requests authorized before a membership change may finish; no global barrier
with DNS publication is claimed.

Existing DNS desired-state ordering, idempotency, and publication behavior
remain unchanged. WorkloadBinding and pilot wire families keep their existing
versions and pins. Production adoption, permission administration, issuer
auditing, deployment, and hardware qualification remain owning-project work.

# Proposed: SPIFFE workload bindings and autonomous owner installations

The [accepted integration roadmap](https://github.com/PseudoDesign/kaiba-infra/blob/codex/spiffe-spire-next-steps/docs/spiffe-spire-plan.md)
separates Kaiba membership authorization from SPIRE credential issuance. This
decision implements its first shared contract slice; it does not adopt runtime
consumers or qualify autonomous production operation.

## Installation roles and independent membership

Standalone is a one-device owner fleet with a local controller, SPIRE Server,
SPIRE Agent and applications. Server adds remote enrollment and fleet management;
promotion preserves that owner's trust domain, identities and data. Agent joins
an existing owner authority and does not gain CA signing authority. A newly
initialized owner installation gets its own persistent trust domain. CA,
bootstrap, storage and workload key roles remain distinct even when colocated.

Deployment role, owner-fleet membership and optional `kaiba.network` enrollment
are independent decisions. Provider DNS is optional for local operation. An
opted-in device uses a separate provider SPIRE Agent, state, Workload API socket,
bootstrap credentials and trust bundle. Initially provider membership permits
only updates to the device's assigned DNS names. It grants no local
administration, and owner credentials grant no provider permission. Provider
outage, expiry or unenrollment must not disable local identity. Delegating
`kaiba.network` signing authority to owner servers, federation and remote
administration are outside this first slice.

These role and network semantics are prose only here. They are not additional
record fields or an installer interface. SPIRE, key protection, offline clock,
antirollback, authority-state continuity and physical boot qualification belong
to their implementation owners and remain explicit roadmap gates.

## Additive workload authorization contract

Introduce [WorkloadBinding](../../contracts/workload-binding.md) at the isolated
wire version `0.5.0-draft.1`. The registry asserts one canonical trust domain,
logical device, enrollment instance and workload, plus state and permissions.
Consumers authenticate that registry and require an active enrollment instance,
exact authenticated peer SPIFFE ID and requested permission on every request.
Missing, stale or unavailable required registry state denies access.

Routine SVID rotation does not change fleet membership or require activation of
each new certificate serial. Issuance remains audited and does not itself grant
membership. Existing DeviceBinding, enrollment rehearsal and pilot issuance,
renewal and recovery contracts retain their exact credential tuples and gates.
No record conversion, runtime fallback or production readiness upgrade is
authorized by this draft.

## Adoption gate

The contract steward, fleet/registry, DNS consumer and provisioning maintainers
must review and explicitly adopt matching pins and runtime obligations before
live use. Offline schema tests and prototype fixtures establish neither current
registry authenticity nor enrollment eligibility. This slice leaves `VERSION`
and all earlier wire families unchanged. A later migration must specify
deployment order, overlap, rollback and retained audit history; it cannot
reinterpret an old pilot certificate as a workload grant.

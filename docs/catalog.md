# Contract catalog

All entries are proposed. Only entries marked **specified** have schemas and
record-local fixtures in this baseline; no entry has production conformance.

| Contract | Producer → consumer | Required meaning | Coverage |
| --- | --- | --- | --- |
| ProvisioningRecord | Provisioning → identity/admission | Observed outcome, posture, readiness claims and authoritative evidence | Specified |
| DeviceBinding | Inventory → relying services/admission | Exact canonical identity/instance/credential binding and lifecycle snapshot | Specified |
| FleetTarget | Admission → resolver/controller | Tenant, instance, platform and capability references, policy decision, freshness and restrictions | Deferred |
| ComponentContract | Component owner → editor/resolver/adapter | Versioned schema, typed ports, compatibility, permissions, resolution semantics and health requirements | Deferred |
| ConfigurationRevision | Authoring → resolver | Immutable graph, pinned components, secret references and authoring provenance | Deferred |
| DeploymentPlan | Resolver → reviewer/publication/execution | Exact instances, effective input digests, value provenance, conflicts, exclusions, expected revisions and rollout policy | Deferred |
| PublishRequest | User client → publication authority | Exact plan and expected desired-state versions, with a retry identity | Specified within Publication |
| Publication | Publication authority → execution/UI | Durable acceptance of exact intent, actor and authorization decision | Specified |
| BuildResult | Builder → release authorization | Exact input-to-artifact mapping, compiler/lockfile/source versions and provenance | Deferred |
| AuthorizedRelease | Release authority → assignment/verifier | Approved artifact digests, platform, delegation, epoch, validity and recovery class | Deferred |
| DesiredAssignment | Controller → device | Instance, desired version, release digest, expected base, attempt and lease | Deferred |
| DeviceObservation | Device → controller/appraisal | Sequenced boot/attempt/release observations and separate health dimensions | Deferred |
| PolicyDecision | Appraisal → controller/verifier | Evidence binding, policy version, freshness, result and reasons | Deferred |
| ExecutionResult | Controller → UI/audit | Attempt-correlated result supported by observations and policy decisions | Deferred |

## DeploymentPlan requirements already fixed by its consumers

The full wire format remains open, but Publication requires the plan to expose:

- contract/version, immutable record ID/revision/digest, tenant and security domain;
- pinned graph, baseline, profile, component, resolver and source versions;
- exact logical device/instance/storage generation for every selected target;
- unique eligible targets with their expected desired-state revisions;
- effective configuration digest and field provenance per target;
- deferred and blocked targets with reasons, separately from eligible targets;
- build equivalence determined by complete effective inputs, not CPU type alone;
- validation decision and expiration, approval requirements and execution policy.

All of these participate in the plan digest. PublishRequest's ordered target
list MUST equal the plan's ordered eligible-target list. Their order is
significant until a later contract explicitly defines otherwise. No consumer
may expand membership, erase exclusions, change baselines, or reinterpret
component versions while retaining that digest.

## Resolution precedence

The intended layering is immutable platform constraints → tenant baseline →
matching group settings → explicitly permitted device overrides. Each value
retains its origin. Conflicts at the same layer block the affected target;
platform security constraints cannot be overridden. The precise merge rules
must be finalized with ComponentContract and DeploymentPlan before a compiler
claims conformance.

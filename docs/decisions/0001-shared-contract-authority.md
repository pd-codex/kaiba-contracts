# ADR 0001: shared contract authority

Status: proposed baseline. Date: 2026-09-11.

## Context

Provisioning and the graphical fleet UI are separate projects. Defining their
shared handoffs solely in either implementation creates competing descriptions
of identity, readiness and publication. Generated types alone cannot express
trust, freshness or retry obligations.

## Decision

Maintain system-level semantics, schemas and conformance fixtures here. Each
subsystem owns its internal details. Producer and consumer maintainers jointly
review changes; applications pin reviewed versions and release independently.

Start with ProvisioningRecord, DeviceBinding, and Publication. Catalog the
remaining handoffs without pretending their wire formats are finalized. Use
JSON Schema for record shape and prose plus executable fixtures for semantics.

## Consequences

Schema validity is necessary but not an authority decision. Consumer integration
and hardware qualification remain separate evidence. The existing provisioning
state machine remains authoritative; exported snapshots do not force a new
temporal sequence around its enrollment transaction. SDK generation and service
deployment remain optional implementation work.

# ADR 0002: publication is durable intent

Status: proposed baseline. Date: 2026-09-11.

## Context

The user's publish action precedes asynchronous building, signing and device
execution. Offline targets, conflicting edits and lost responses make a single
"published means running" state misleading and unsafe to retry.

## Decision

Accept an immutable plan and its exact reviewed eligible set as one durable
publication. Bind authenticated actor, plan digest, expected desired-state
versions and retry identity. Report subsequent build, release authorization,
assignment and confirmation separately. No silent partial acceptance or retargeting.

## Consequences

The system must recover accepted-but-undispatched work and deduplicate identical
requests. Acceptance does not reserve indefinite device authority: assignment
rechecks versions and policy. Operator publication, artifact signing, and fresh
boot authorization remain separate decisions. The UI must represent those states
honestly and expose conflicts instead of silently rebasing a plan.

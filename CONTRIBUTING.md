# Changing the contracts

Keep shared semantics here and implementation choices in their owning projects.
Contract-set status is **proposed** until the named producers and consumers
explicitly adopt a version and demonstrate their integration obligations.

For each change:

1. State the interoperability problem and affected producer/consumer roles.
2. Update the written contract, schema, positive examples and negative fixtures
   together. Identify schema checks, record-local checks, and runtime obligations.
3. Explain compatibility with pinned consumers, including enum additions, unknown
   fields, altered defaults, digest rules, and authorization semantics.
4. Record significant system decisions in `docs/decisions/`. Do not silently
   reopen provisioning ownership, key-role, or production qualification decisions.
5. Run the complete offline conformance suite. Required integration evidence must
   come from the owning subsystem; mocks cannot satisfy production gates.
6. Obtain review from the system contract steward and affected producer/consumer
   maintainers. Named individuals and CODEOWNERS assignments are intentionally
   pending the team's ownership decision.

Publish stable tags only after the adoption checklist is satisfied. A passing
workflow or a merged documentation change does not automatically release or
deploy any subsystem.

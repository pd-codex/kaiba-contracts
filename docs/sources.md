# Source baseline and provenance

Reviewed 2026-09-11. These links pin the upstream source used for this proposal.

## Provisioning

Repository: `PseudoDesign/kaiba-provisioning`.
Commit: `8d0ed51a8177f1431f4e6ff992df811fc134344d`.

| Source | Contract implications |
| --- | --- |
| [Architecture and trust boundaries](https://github.com/PseudoDesign/kaiba-provisioning/blob/8d0ed51a8177f1431f4e6ff992df811fc134344d/docs/architecture-and-trust-boundaries.md) | Separate build, signing, control, physical execution and independent audit; preserve execute-once reconciliation |
| [Device identity](https://github.com/PseudoDesign/kaiba-provisioning/blob/8d0ed51a8177f1431f4e6ff992df811fc134344d/docs/device-identity.md) | RA-assigned canonical identity, exact active credential tuples, pending verification, replacement generations and no authentication/attestation equivalence |
| [Production readiness](https://github.com/PseudoDesign/kaiba-provisioning/blob/8d0ed51a8177f1431f4e6ff992df811fc134344d/docs/production-readiness.md) | Current development posture has both readiness flags false; security_applied is not production enrollment |
| [Production security follow-on](https://github.com/PseudoDesign/kaiba-provisioning/blob/8d0ed51a8177f1431f4e6ff992df811fc134344d/docs/raspberry-pi-5-production-security-follow-on.md) | Proposed no-TPM Pi profile, fresh authorization before unlock, read-only root, delegated releases, A/B qualification and destructive storage replacement |

Upstream describes a production identity target and roadmap, not implemented
production enrollment. It also coordinates activation before final completion.
This repository proposes adapters and shared semantics; it does not change
upstream state machines or close production qualification gates.

## Kaiba Flow

The current UI is a design prototype with sample devices and simulated actions.
The architecture used for discussion was recorded in
`docs/provisioning-to-fleet-architecture.md`, and the navigation repair/source
baseline is commit `93b3ebd051f049d2b02c8c3db52032c1efd6eceb` in its Sites source
repository. [Kaiba Flow](https://kaiba-flow.blackmako85.chatgpt.site) is the
interactive prototype, not an authority for these shared contracts. Readers may
need the site owner's access to open it.

## Encoding references

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12): structural schemas; this repository explicitly enables format assertion.
- [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785): canonical representation for structured-record digests. Upstream evidence digests continue to bind the original exact bytes.

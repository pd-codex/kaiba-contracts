# Pilot renewal delegation

`PilotRenewalDelegation` `0.6.0-draft.1` delegates only same-key renewal of
unexpired membership. It does not delegate initial enrollment, recovery,
replacement, permission changes, evidence exceptions, or term reapproval.

An authenticated owner creates revision 1. The authority derives each member
from its exact active enrollment and authenticated current admission. Members
pin enrollment and logical identity, storage/key generations, SPKI, slot,
issuer, audience, profile, permissions, accepted gaps, qualification policy,
observation freshness and evidence scope. An automation identity is distinct
from the owner, station and issuer callback identities. Possession of an
automation credential alone conveys no renewal authority.

The term begins at `activated_at` and ends exactly 2,592,000 seconds later.
Each renewal authorization remains at most 604,800 seconds and must end by the
earliest applicable delegation, admission, policy and trust validity bound.
Neither a restarted controller nor a repeated create request resets the term.
Renewal preserves the existing versioned approval, retained-key proof,
installation proof and atomic activation contracts, including predecessors
issued through the recovery protocol.

`evidence_scope_digest` is JCS/SHA-256 of the adoption record with metadata
normalized as follows: `contract`, `contract_version`, `record_id`, `issued_at`,
`authority_id`, `tenant_id`, `security_domain_id` and `correlation_id` become empty
strings; `revision` becomes zero; `source.observation_id` and `source.observed_at`
become empty strings. Preserve every other field and use JCS encoding.
`tools.delegation.delegation_evidence_digest` is the portable reference helper. All
measured conditions, qualification outcomes, evidence references, source
repository/commit and target remain included. Refreshing observation timestamps
does not authorize changed evidence. Freshness rules continue to apply.

Owner revocation appends revision 2 with the original term, approval and members
unchanged. Revocation is terminal for this delegation. A further term requires
a new owner approval and record ID. Historical records remain readable for
reconciliation; they do not authorize signing or cutover. Signing and activation
must obtain current authenticated delegation state. A cached active revision
cannot override a revoked revision or an unavailable authority.

The issuer independently validates the exact owner-approved delegation and
renewal authorization before signing, preserving its exact issuance grants and
history. Ambiguous issuance remains consumed and requires reconciliation with
the same operation ID; creating another operation is not recovery.

Schema/offline validation proves consistency only. It cannot prove owner
authentication, freshness, current revocation state, host clock certainty,
protected key custody, or a successful installation. `full_qualification`
remains false.

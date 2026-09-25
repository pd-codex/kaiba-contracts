# PilotRenewalAuthorization — proposed 0.3.0-draft.1

This additive record binds an explicit operator-reviewed, same-key renewal to an
exact predecessor and successor admission records. It is the first contract
slice of the [seven-day pilot plan](https://github.com/PseudoDesign/kaiba-fleet/blob/main/docs/pilot-ongoing-operation.md).
It is not an issued credential, installation receipt, activation result or live
authorization token. No producer or consumer has adopted it yet.

## Authority and identity

A configured renewal/admission authority produces this record after explicit
operator approval. The inventory and issuer consume it only through authenticated
current-source reads with their configured authority/tenant/domain scope. A
caller-supplied authority_id or successful offline validation does not establish
that authority. Generic station and device principals cannot approve renewal.

`operation_id` identifies one immutable renewal. `predecessor_binding_ref` names
the exact active binding snapshot by record ID, revision and JCS digest.
`predecessor_certificate_digest` is SHA-256 of the actual DER certificate bytes,
not its PEM text or SPKI. The runtime must independently verify that certificate
against the binding, issuer, stored serial and membership. Offline linked checks
accept its verified digest as a separate input; they do not perform that check.

The predecessor/successor credential revisions identify successive certificates;
the successor is exactly predecessor + 1. They are not key generations, binding
snapshot revisions or storage generations. Current runtime history supplies the
predecessor revision; the validator does not infer it from a binding revision.
Logical device, instance, key/SPKI, slot, storage generation, issuer, target,
audience, permissions and pilot profile remain unchanged. `full_qualification`
remains false. Different-key, different-issuer, revoked/quarantined and expired
credential recovery require separate contracts and cannot use this mode.

The first slice supports references to existing 0.2.0-draft.1 pilot records. It
does not change their schemas or relax the old binding-transition validator.
The proposed [successor binding and installation/cutover contract](pilot-renewal-cutover.md)
defines those linked transitions. Runtime migration and integration remain required
before adoption; this authorization record alone cannot make them valid.

## Window and fresh records

The record includes exact successor adoption, policy and admission references.
All must pass the existing linked pilot checks, including target/custody/gap
consistency and evidence freshness. Authorization issuance cannot precede those
reviewed records. Its validity interval is positive, at most seven days, and
contained in the effective policy/decision intervals. Normal renewal is checked
while the predecessor certificate and membership remain active and unexpired.
The deadline is exclusive. No implementation may silently move that deadline
when issuance or installation is delayed.

Seven days is a maximum, not a requirement to issue a seven-day certificate.
Runtime issuance must also cap validity by issuer CA, approved records and local
policy. Freshness is checked again at issuance, installation/cutover and every
relying request. This record never gives seven days of immunity from revocation,
policy withdrawal, unavailable authority, evidence age or transport expiry.

## Runtime obligations and later slices

- Authenticate the operator decision/current authority, not a copied JSON file.
- Bind a distinct renewal key-possession challenge to the operation, authorization
  digest, predecessor certificate/revision, successor records, identity, random
  nonce and short challenge deadline. Old bootstrap/proof messages cannot renew.
- Serialize against another renewal, quarantine and revocation. Persist operation
  and issuer intent before signing; never retry ambiguous signing automatically.
  A changed request under an existing operation/idempotency key is rejected.
- Preserve old issuance history and exact committed responses through migration.
  A new authorization does not permit deletion or replacement of issuer scope.
- Require proof of installing the exact successor certificate before atomic
  cutover. After cutover reject the predecessor, including on retained TLS
  connections. A pending certificate is not relying authority.
- Preserve current protected client state during interrupted installation and
  reconcile lost replies without creating another key, instance or issuance.
- Preserve expiry enforcement. Supervised recovery after expiry, lost-key
  replacement and revocation recovery are out of scope of this mode.

These are obligations, not claims made by this repository's offline tests.
Fleet/native integration must demonstrate them with disposable PKI and durable
stores before deployment. See [conformance](../docs/conformance.md).

## Compatibility and fixtures

The new exact `(PilotRenewalAuthorization, 0.3.0-draft.1)` dispatch is additive.
Legacy 0.1/0.2 schemas and examples are unchanged. Pinned consumers must reject
this new record until explicitly adopted; no unknown-field tolerance or implicit
upgrade is allowed. Digests retain the existing RFC 8785 rules.

The [schema](../schemas/0.3.0-draft.1/pilot-renewal-authorization.json),
[synthetic authorization](../examples/valid/pilot-renewal-authorization-a.json),
[successor policy](../examples/valid/pilot-renewal-policy.json) and
[successor decision](../examples/valid/pilot-renewal-decision-a.json) are checked
with the existing fixture predecessor. The certificate digest is synthetic;
there is no live certificate or deployment grant in these files. Record-local
negative fixtures cover oversized windows, skipped revision and unsupported
recovery; linked tests cover substitutions, expiry, stale observations and bounds.

# DeviceBinding

**Producer:** authoritative identity inventory, after RA/CA/verifier decisions.
**Consumers:** admission, management relying services and audit.
**Schema:** [device-binding.json](../schemas/0.1.0-draft.1/device-binding.json).

## Meaning and fields

A versioned snapshot of one exact credential tuple and its effective inventory
state. It exposes authorization state; it is not a bearer credential or an
attestation statement.

| Field | Meaning |
| --- | --- |
| `logical_device_id` | Canonical identity assigned by the RA/inventory policy |
| `instance_id`, `storage_generation` | Particular enrollment incarnation; destructive storage replacement changes both |
| `bootstrap_identity_ref` | Public bootstrap identity and its explicitly qualified protection profile |
| `provisioning_ref` | Exact ProvisioningRecord revision used as evidence; may be candidate evidence |
| `credential` | Slot, role, key generation, public SPKI digest, issuer, certificate serial and validity |
| `state` | `staged`, `active`, `superseded`, `quarantined`, `revoked`, or `retired` for this tuple |
| `activation` | Activation timestamp, policy and pending-verifier receipt; required when active |
| `supersedes` | Optional reference to a prior binding during authorized renewal or rekey |

Certificate serials use lowercase hex without `0x` or leading zeroes. They are
meaningful only with the issuer identity. The public-key digest is SHA-256 over
DER SubjectPublicKeyInfo bytes, not PEM text. An issuer ID resolves to a reviewed
issuer identity; it is not a user-selected URL or display name.

## Identity and activation obligations

- **DB-01:** The RA assigns logical identity. Request fields or CSR names cannot
  choose another identity, tenant, role, slot, or generation.
- **DB-02:** Inventory binds bootstrap authentication and fresh operational-key
  proof to the same enrollment transaction, intended audience, canonical identity,
  instance, storage generation, slot, key generation, SPKI and certificate profile.
- **DB-03:** Issuance produces a staged tuple. Production relying services reject
  it until the pending verifier proves the installed key and inventory atomically
  activates the exact tuple named by its receipt.
- **DB-04:** A consumer validates PKI and current inventory authorization for the
  device, instance, slot, generation, exact issuer/serial and role. The snapshot's
  `active` value alone is insufficient; broader quarantine and issuer revocation
  override it. Required policy and freshness checks remain independent.
- **DB-05:** A CA-valid credential from a prior instance cannot inherit an
  assignment to a replacement. Binding generation never serves as a hardware
  anti-rollback counter.
- **DB-06:** Successful authentication is not attestation. Bootstrap and
  operational protection claims must name their actual attacker boundary.

## Lifecycle

Allowed effective transitions for the same tuple are:

| From | To | Required condition |
| --- | --- | --- |
| staged | active | Exact fresh verifier result, policy approval and atomic activation |
| staged | quarantined, revoked, retired | Failed or cancelled enrollment; retained audit |
| active | superseded | Approved renewal/rekey cutover to another exact tuple |
| active | quarantined, revoked, retired | Current inventory policy denies routine use |
| quarantined | active | Explicit recovery/revalidation of the same uncompromised tuple |
| quarantined | revoked, retired | Recovery denied or retirement selected |
| superseded | revoked, retired | Old tuple cleanup |
| revoked | retired | Administrative retirement; no reactivation |
| retired | — | Terminal |

Every state change increments revision. Certificate expiry independently denies
use without waiting for a new state record. Historical activation evidence may
remain on inactive records. Same-state snapshots may refresh provenance at a
new revision without changing tuple fields or restoring denied authority.
Same-key renewal creates a new certificate binding
with the same key generation; rekey creates a new key generation. An ordinary
rotation never rewrites an old tuple's key or certificate fields. Any overlap
window must be bounded and explicitly authorized; this draft provides no default
overlap grant. Lost activation responses are reconciled against inventory.

Storage replacement creates a new instance and storage generation; the previous
instance is denied before the replacement activates. Tenant/security-domain
transfer is a separate reviewed lifecycle, not a mutable label on this record.
For the current Pi proposal, immutable customer-root domain changes require fresh
boards. Recovery from a compromised key must not rely solely on that key.

## Validation limits

The local validator checks schema, validity-window ordering, and activation time
consistency. It cannot verify a real certificate, key possession, authority,
transaction binding, current revocation or platform qualification. Those are
required consumer integration tests listed in [conformance](../docs/conformance.md).

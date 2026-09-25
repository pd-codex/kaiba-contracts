# Kaiba contracts

Shared contracts from device provisioning to publication of a graphical device
configuration. This repository defines the records, responsibilities, and
guarantees that connect Kaiba subsystems. It does not implement a provisioning
lane, controller, signer, device agent, or production admission service.

**Status: proposed contract set `0.3.0-draft.1`.** The additive renewal authorization
has not yet been adopted by the producer or consumer. The original family is used by the
[isolated enrollment rehearsal](docs/integrations/enrollment-rehearsal.md).
Passing the included tests means
the documents' sample records satisfy the checked rules; it does not qualify
hardware, authenticate a device, or authorize a release.

## Read in this order

The [process guide website](https://pd-codex.github.io/kaiba-contracts/) provides
a visual walkthrough of the handoffs, ownership, contract coverage and current
development slice. It is published by GitHub Pages once the repository's Pages
source is enabled. See [website maintenance and setup](website/README.md).

The [visual device story](https://pd-codex.github.io/kaiba-contracts/walkthrough.html)
introduces the journey in plain language, with an animated device and before/after
states. The [technical walkthrough](https://pd-codex.github.io/kaiba-contracts/technical.html)
adds contract fixtures, exact state transitions and acceptance rules. Both support
development restrictions, conflicting assignments and a lost confirmation.

1. [System specification](docs/system.md): pipeline, authorities, and invariants.
2. [Contract catalog](docs/catalog.md): every handoff, including deferred contracts.
3. [Common rules](docs/common-rules.md): identity, digests, versioning, and errors.
4. Initial detailed contracts:
   - [ProvisioningRecord](contracts/provisioning-record.md)
   - [DeviceBinding](contracts/device-binding.md)
   - [Publication](contracts/publication.md), including `PublishRequest`
   - [Existing-device pilot enrollment](contracts/pilot-enrollment.md)
   - [Explicit pilot renewal authorization](contracts/pilot-renewal-authorization.md)
   - [Pilot renewal installation and cutover](contracts/pilot-renewal-cutover.md)
5. [Conformance and examples](docs/conformance.md).

The original wire family remains in [schemas/0.1.0-draft.1](schemas/0.1.0-draft.1).
The new pilot family lives in [schemas/0.2.0-draft.1](schemas/0.2.0-draft.1).
The additive renewal authorization lives in [schemas/0.3.0-draft.1](schemas/0.3.0-draft.1).
All use exact contract/version dispatch; pilot records do not upgrade legacy
readiness or confer full qualification. They use JSON
Schema Draft 2020-12 and resolve entirely from local files. Examples use fictitious
identifiers and evidence references; they contain no credentials or live grants.

## Validate locally

Python 3.12 or newer:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/validate.py examples/valid/publish-request.json
```

On Windows, use `.venv\Scripts\python.exe`. Validation includes schema checks,
record-local semantic checks, linked fixture digests, and negative cases. Runtime
authorization obligations are listed separately and require subsystem tests.

## Ownership and adoption

The system contract belongs here. Each producer and affected consumer reviews
changes; implementation, deployment, key custody, and internal state remain in
the owning project. See [contributing](CONTRIBUTING.md) and the
[adoption checklist](docs/adoption.md).

The implementation owners are
[kaiba-provisioning](https://github.com/PseudoDesign/kaiba-provisioning) for the
ProvisioningRecord producer and
[kaiba-fleet](https://github.com/PseudoDesign/kaiba-fleet) for enrollment,
identity inventory and the DeviceBinding producer. Fleet implements the isolated
rehearsal; pilot runtime support and fully qualified admission remain separate
work. Naming owners does not establish contract adoption or production conformance.

The provisioning baseline is pinned in [sources](docs/sources.md). Its current
development posture cannot enter `enrollment_ready`. The proposed production
examples here do not change that status. The proposed pilot family needs explicit
producer/consumer adoption and its own authenticated policy before live use.

# Appliance wire reference runtime

Standard-library Go module for the additive production appliance protocol.
Run `go test -race ./...` here. Existing contract-family tooling is unchanged.
Consumers retain byte-identical copies with a source-commit/file-digest pin and
verify that pin in CI; no device trusts a downloaded runtime or record-supplied key.

Schemas/Python establish structural consistency. Signature, purpose, key and
certificate validation uses this runtime with independent installation trust.
Neither implementation establishes provisioning readiness or physical acceptance.

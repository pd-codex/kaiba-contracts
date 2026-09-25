# Proposed: separate supervised recovery after pilot expiry

An existing pilot can retain its private key and enrollment history after its
admission or certificate expires. Routine renewal requires an unexpired
predecessor, so an expired pilot needs a distinct, explicit approval path.

Introduce recovery authorization and a purpose-separated key challenge in a new
0.4 draft family. Use current authenticated management access to relay proof of
the retained device key; do not bypass expired TLS checks or reset enrollment.
Fresh admission, exact predecessor and current denial state remain prerequisites.
Reserve the predecessor across normal renewal and recovery to prevent signing or
idempotency controls being bypassed by switching modes.

This first contract slice stops at approval/key proof. Successor binding, issuer
ledger integration, installation, cutover, protected client recovery and real
service integration are subsequent gates. None of these records alone restores
access. Contract steward, fleet/issuer and provisioning/client owners must review
and adopt each wire transition before live execution.

# Proposed: explicit same-key pilot renewal authorization

The selected operating model is a seven-day window with explicit renewal.
Current fleet/issuer state supports one issuance and exact pinned record scope.
Extending timestamps or discarding history would bypass the intended boundary.

Introduce an additive authorization record in 0.3.0-draft.1. Preserve all 0.2
records and distinguish credential revision from key/storage generation. Bind
an exact predecessor to fresh successor records while the current credential is
still valid. Require authenticated current-source verification at runtime.

Do not combine authorization, signing, installation and activation into a single
record with an ambiguous "passed" flag. This first slice specifies authorization
only; successor binding, installation proof, cutover and expired recovery remain
separate implementation/contract gates. It grants no automatic renewal, production
qualification or new device permissions.

Owning reviews: contract steward, fleet/issuer consumer and provisioning/client
producer. Proposed until those owners adopt exact pins and demonstrate integration.

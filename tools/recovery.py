"""Offline recovery consistency only; no authentication, signature verification or authority."""
from tools.validate import validate, validate_pilot_handoff, record_ref, _time


def validate_pilot_recovery(authorization, predecessor, adoption, policy, decision,
                           *, checked_at, predecessor_certificate_digest,
                           predecessor_credential_revision, predecessor_access_expires_at):
    """Offline consistency only; certificate facts must come from authenticated runtime state."""
    errors = validate(authorization) + validate(predecessor)
    if (not isinstance(authorization, dict) or authorization.get('contract') != 'PilotRecoveryAuthorization'
            or not isinstance(predecessor, dict) or predecessor.get('contract') != 'PilotDeviceBinding'):
        errors.append('RECOVERY-TYPE: wrong record types')
    if errors:
        return errors
    errors += validate_pilot_handoff(adoption, policy, decision, checked_at=checked_at)
    if errors:
        return errors
    a, b = authorization, predecessor
    now = _time(checked_at)
    if _time(b['issued_at']) > now or _time(a['issued_at']) < max(_time(adoption['issued_at']), _time(policy['issued_at']), _time(decision['issued_at'])):
        errors.append('RECOVERY-TIME: future predecessor or authorization predates reviewed records')
    if b['state'] != 'active':
        errors.append('RECOVERY-PREDECESSOR: revoked, quarantined, retired or superseded state cannot recover')
    try:
        deadline = _time(predecessor_access_expires_at)
        if (a['predecessor_access_expires_at'] != predecessor_access_expires_at
                or not _time(b['credential']['not_before']) < deadline <= _time(b['credential']['not_after'])
                or not deadline <= _time(a['issued_at']) <= now):
            errors.append('RECOVERY-EXPIRY: exact expired access deadline required')
    except (TypeError, ValueError, AttributeError):
        errors.append('RECOVERY-EXPIRY: invalid runtime deadline')
    if not _time(a['valid_from']) <= now < _time(a['expires_at']) or _time(a['issued_at']) > now:
        errors.append('RECOVERY-WINDOW: authorization is not current')
    if a['predecessor_binding_ref'] != record_ref(b) or a['predecessor_certificate_digest'] != predecessor_certificate_digest:
        errors.append('RECOVERY-PREDECESSOR: exact binding/certificate mismatch')
    if b['contract_version'] == '0.3.0-draft.1' and (b['credential_revision'] != predecessor_credential_revision or b['certificate_digest'] != predecessor_certificate_digest):
        errors.append('RECOVERY-PREDECESSOR: runtime facts differ from versioned binding')
    if (b['contract_version'] == '0.2.0-draft.1' and predecessor_credential_revision != 1) or type(predecessor_credential_revision) is not int or a['predecessor_credential_revision'] != predecessor_credential_revision:
        errors.append('RECOVERY-REVISION: predecessor differs from runtime revision')
    for field in ('logical_device_id', 'instance_id', 'storage_generation', 'target', 'tenant_id', 'security_domain_id', 'audience', 'profile', 'permissions'):
        if a[field] != b[field]:
            errors.append(f'RECOVERY-IDENTITY: {field} changed')
    for field, old in [('credential_slot','slot'),('key_generation','key_generation'),('spki_digest','spki_digest'),('issuer_id','issuer_id')]:
        if a[field] != b['credential'][old]:
            errors.append(f'RECOVERY-IDENTITY: {field} changed')
    for field, value in [('adoption_ref',record_ref(adoption)),('policy_ref',record_ref(policy)),('admission_ref',record_ref(decision)),('target',adoption['target']),('tenant_id',adoption['tenant_id']),('security_domain_id',adoption['security_domain_id']),('audience',policy['enrollment_audience']),('profile',policy['profile']),('permissions',policy['permissions']),('issuer_id',policy['operational_issuer_id'])]:
        if a[field] != value:
            errors.append(f'RECOVERY-RECORDS: {field} mismatch')
    if _time(a['valid_from']) < max(_time(policy['valid_from']),_time(decision['valid_from']),_time(decision['issued_at'])) or _time(a['expires_at']) > min(_time(policy['expires_at']),_time(decision['expires_at'])):
        errors.append('RECOVERY-WINDOW: outside approved policy/decision interval')
    return errors



def validate_recovery_challenge(challenge, authorization, *, checked_at):
    errors = validate(challenge) + validate(authorization)
    if (not isinstance(challenge, dict) or challenge.get('contract') != 'PilotRecoveryKeyChallenge'
            or not isinstance(authorization, dict) or authorization.get('contract') != 'PilotRecoveryAuthorization'):
        errors.append('RECOVERY-PROOF: wrong record types')
    if errors: return errors
    c, a = challenge, authorization
    for field in ('operation_id','instance_id','tenant_id','security_domain_id','authority_id','predecessor_binding_ref','predecessor_certificate_digest','spki_digest'):
        if c[field] != a[field]: errors.append(f'RECOVERY-PROOF: {field} mismatch')
    if c['authorization_ref'] != record_ref(a): errors.append('RECOVERY-PROOF: wrong authorization')
    now = _time(checked_at)
    if not _time(a['valid_from']) <= _time(c['issued_at']) <= now < _time(c['expires_at']) <= _time(a['expires_at']):
        errors.append('RECOVERY-PROOF: challenge outside current authorization')
    return errors

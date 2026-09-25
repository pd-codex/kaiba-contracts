"""Offline renewal staging/cutover checks; not cryptographic or live authorization."""
from tools.validate import validate, validate_pilot_renewal, record_ref, digest, _time


def validate_staged(authorization, predecessor, staged, adoption, policy, decision,
                    *, checked_at, predecessor_certificate_digest,
                    predecessor_credential_revision):
    errors = validate(staged)
    if not isinstance(staged, dict) or (staged.get('contract'), staged.get('contract_version')) != ('PilotDeviceBinding', '0.3.0-draft.1'):
        errors.append('RENEWAL-STAGED: expected versioned successor binding')
    if errors:
        return errors
    errors += validate_pilot_renewal(authorization, predecessor, adoption, policy, decision,
        checked_at=checked_at, predecessor_certificate_digest=predecessor_certificate_digest,
        predecessor_credential_revision=predecessor_credential_revision)
    if errors:
        return errors
    a, b, s = authorization, predecessor, staged
    if s['state'] != 'staged' or s['record_id'] == b['record_id']:
        errors.append('RENEWAL-STAGED: requires distinct staged record')
    for field in ('logical_device_id','instance_id','storage_generation','target','audience','profile','permissions','tenant_id','security_domain_id','adoption_ref','admission_ref','policy_ref'):
        if s[field] != a[field]: errors.append(f'RENEWAL-STAGED: {field} mismatch')
    if s['bootstrap_identity_ref'] != b['bootstrap_identity_ref']:
        errors.append('RENEWAL-STAGED: bootstrap identity changed')
    for field, expected in [('credential_revision',a['successor_credential_revision']),('renewal_authorization_ref',record_ref(a)),('predecessor_binding_ref',record_ref(b))]:
        if s[field] != expected: errors.append(f'RENEWAL-STAGED: {field} mismatch')
    for field, source in [('slot','credential_slot'),('key_generation','key_generation'),('spki_digest','spki_digest'),('issuer_id','issuer_id')]:
        if s['credential'][field] != a[source]: errors.append(f'RENEWAL-STAGED: credential {field} mismatch')
    if s['certificate_digest'] == predecessor_certificate_digest or s['credential']['certificate_serial'] == b['credential']['certificate_serial']:
        errors.append('RENEWAL-STAGED: successor certificate must differ')
    start, end = _time(s['credential']['not_before']), _time(s['credential']['not_after'])
    now = _time(checked_at)
    if not _time(a['valid_from']) <= start <= now < end <= _time(a['expires_at']):
        errors.append('RENEWAL-STAGED: certificate outside authorized current window')
    if not _time(a['issued_at']) <= _time(s['issued_at']) <= now:
        errors.append('RENEWAL-STAGED: invalid issue time')
    return errors


def validate_cutover(authorization, predecessor, staged, receipt, active, adoption,
                     policy, decision, *, checked_at, predecessor_certificate_digest,
                     predecessor_credential_revision):
    errors = validate(receipt) + validate(active)
    if not isinstance(receipt,dict) or receipt.get('contract') != 'PilotRenewalInstallationReceipt':
        errors.append('RENEWAL-CUTOVER: wrong receipt type')
    if not isinstance(active,dict) or (active.get('contract'),active.get('contract_version')) != ('PilotDeviceBinding','0.3.0-draft.1'):
        errors.append('RENEWAL-CUTOVER: wrong active binding type')
    if errors: return errors
    errors += validate_staged(authorization,predecessor,staged,adoption,policy,decision,
        checked_at=checked_at,predecessor_certificate_digest=predecessor_certificate_digest,
        predecessor_credential_revision=predecessor_credential_revision)
    if errors: return errors
    a, s, r, n = authorization, staged, receipt, active
    for field, expected in [('operation_id',a['operation_id']),('authorization_ref',record_ref(a)),('predecessor_binding_ref',record_ref(predecessor)),('staged_binding_ref',record_ref(s)),('certificate_digest',s['certificate_digest']),('tenant_id',s['tenant_id']),('security_domain_id',s['security_domain_id'])]:
        if r[field] != expected: errors.append(f'RENEWAL-CUTOVER: receipt {field} mismatch')
    allowed = {'revision','issued_at','state','activation','installation_receipt_ref'}
    for field in set(s)|set(n):
        if field not in allowed and s.get(field)!=n.get(field): errors.append(f'RENEWAL-CUTOVER: successor {field} changed')
    if n['state']!='active' or n['revision']!=s['revision']+1:
        errors.append('RENEWAL-CUTOVER: invalid active revision/state')
    if n.get('installation_receipt_ref')!=record_ref(r):
        errors.append('RENEWAL-CUTOVER: wrong installation receipt')
    activation=n.get('activation',{})
    if activation.get('verifier_receipt_ref',{}).get('digest')!=digest(r):
        errors.append('RENEWAL-CUTOVER: verifier receipt digest mismatch')
    if activation.get('policy_ref')!=a['policy_ref']:
        errors.append('RENEWAL-CUTOVER: activation policy mismatch')
    now=_time(checked_at);verified=_time(r['verified_at'])
    if not _time(s['issued_at']) <= _time(r['challenge_issued_at']) <= verified <= _time(r['issued_at']) <= _time(n['issued_at']) <= now:
        errors.append('RENEWAL-CUTOVER: issue/verification order invalid')
    if (now-verified).total_seconds()>300:
        errors.append('RENEWAL-CUTOVER: installation proof stale')
    if 'activated_at' not in activation or not verified <= _time(activation['activated_at']) <= _time(n['issued_at']):
        errors.append('RENEWAL-CUTOVER: activation precedes installation proof')
    return errors

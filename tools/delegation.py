"""Offline delegation consistency. Authenticity/currentness require live readers."""
from datetime import timedelta
import copy

from tools.validate import _time, validate, digest


def check_delegation(record):
    errors = []
    start, end = _time(record['activated_at']), _time(record['expires_at'])
    if end - start != timedelta(days=30):
        errors.append('DELEGATION-TERM: term must be exactly thirty days')
    if record['owner_principal'] == record['automation_principal']:
        errors.append('DELEGATION-PRINCIPAL: owner and automation must differ')
    members = record['members']
    for field in ('enrollment_id', 'instance_id', 'logical_device_id', 'spki_digest'):
        if len({m[field] for m in members}) != len(members):
            errors.append(f'DELEGATION-MEMBER: duplicate {field}')
    if any(m['enrollment_id'] != m['instance_id'] for m in members):
        errors.append('DELEGATION-MEMBER: exact enrollment instance required')
    issued = _time(record['issued_at'])
    if record['state'] == 'active' and issued != start:
        errors.append('DELEGATION-TERM: activation and approval issuance must match')
    if record['state'] == 'revoked':
        if not start <= _time(record['revoked_at']) == issued:
            errors.append('DELEGATION-REVOCATION: invalid revocation time')
    return errors


def validate_delegation_transition(previous, successor):
    errors = validate(previous) + validate(successor)
    if errors:
        return errors
    if previous['contract'] != 'PilotRenewalDelegation' or successor['contract'] != 'PilotRenewalDelegation':
        return ['DELEGATION-TRANSITION: expected delegations']
    if previous['state'] != 'active' or successor['state'] != 'revoked':
        errors.append('DELEGATION-TRANSITION: only active to revoked is allowed')
    mutable = {'revision', 'issued_at', 'state', 'revoked_at', 'revocation_reason'}
    for field in previous.keys() | successor.keys():
        if field not in mutable and previous.get(field) != successor.get(field):
            errors.append(f'DELEGATION-TRANSITION: immutable {field} changed')
    return errors


def validate_delegated_renewal(delegation, authorization, *, checked_at, principal):
    """Additional bounds; does not replace the existing renewal/proof checks."""
    errors = validate(delegation) + validate(authorization)
    if errors:
        return errors
    if delegation['contract'] != 'PilotRenewalDelegation' or authorization['contract'] != 'PilotRenewalAuthorization':
        return ['DELEGATION-RENEWAL: wrong contract types']
    d, a, now = delegation, authorization, _time(checked_at)
    if d['state'] != 'active' or not _time(d['activated_at']) <= now < _time(d['expires_at']):
        errors.append('DELEGATION-RENEWAL: inactive term')
    if principal != d['automation_principal']:
        errors.append('DELEGATION-RENEWAL: wrong automation principal')
    if any(a[k] != d[k] for k in ('authority_id', 'tenant_id', 'security_domain_id')):
        errors.append('DELEGATION-RENEWAL: wrong authority scope')
    if not _time(d['activated_at']) <= _time(a['valid_from']) <= now < _time(a['expires_at']) <= _time(d['expires_at']):
        errors.append('DELEGATION-RENEWAL: authorization outside term')
    member = next((m for m in d['members'] if m['instance_id'] == a['instance_id']), None)
    if member is None:
        return errors + ['DELEGATION-RENEWAL: enrollment not delegated']
    for field in ('logical_device_id', 'instance_id', 'target', 'storage_generation',
                  'credential_slot', 'key_generation', 'spki_digest', 'issuer_id',
                  'audience', 'profile', 'permissions'):
        if member[field] != a[field]:
            errors.append(f'DELEGATION-RENEWAL: changed {field}')
    return errors


def delegation_evidence_digest(adoption):
    """Portable JCS evidence scope; observation refresh cannot alter facts."""
    errors = validate(adoption)
    if errors or adoption.get('contract') != 'PilotAdoptionRecord':
        raise ValueError('valid PilotAdoptionRecord required')
    normalized = copy.deepcopy(adoption)
    for field in ('contract', 'contract_version', 'record_id', 'issued_at',
                  'authority_id', 'tenant_id', 'security_domain_id', 'correlation_id'):
        normalized[field] = ''
    normalized['revision'] = 0
    normalized['source']['observation_id'] = ''
    normalized['source']['observed_at'] = ''
    return digest(normalized)

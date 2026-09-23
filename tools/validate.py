"""Offline draft-contract checks. No device authentication or authorization."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import rfc8785
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / 'VERSION').read_text().strip()
SUPPORTED_VERSIONS = ('0.1.0-draft.1', '0.2.0-draft.1')
SCHEMAS = {
    f'{version}/{p.stem}': json.loads(p.read_text())
    for version in SUPPORTED_VERSIONS
    for p in (ROOT / 'schemas' / version).glob('*.json')
}
REGISTRY = Registry().with_resources(
    (schema['$id'], Resource.from_contents(schema)) for schema in SCHEMAS.values()
)
FORMATS = FormatChecker()
for required_format in ('date-time', 'uri'):
    if required_format not in FORMATS.checkers:
        raise RuntimeError(f'Missing {required_format} validation; install requirements-dev.txt')
CONTRACTS = {
    ('ProvisioningRecord', '0.1.0-draft.1'): 'provisioning-record',
    ('DeviceBinding', '0.1.0-draft.1'): 'device-binding',
    ('PublishRequest', '0.1.0-draft.1'): 'publish-request',
    ('Publication', '0.1.0-draft.1'): 'publication',
    ('PilotAdoptionRecord', '0.2.0-draft.1'): 'pilot-adoption-record',
    ('PilotPolicy', '0.2.0-draft.1'): 'pilot-policy',
    ('PilotAdmissionDecision', '0.2.0-draft.1'): 'pilot-admission-decision',
    ('PilotDeviceBinding', '0.2.0-draft.1'): 'pilot-device-binding',
}



def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON property: {key}')
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f'non-JSON numeric constant: {value}')


def loads(text):
    value = json.loads(text, object_pairs_hook=_unique_object,
                       parse_constant=_reject_constant)
    # Also checks the JCS number range and Unicode representation.
    rfc8785.dumps(value)
    return value


def load(path):
    return loads(Path(path).read_text(encoding='utf-8'))


def digest(record):
    return 'sha256:' + hashlib.sha256(rfc8785.dumps(record)).hexdigest()


def _time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def validate(record):
    if not isinstance(record, dict):
        return ['unsupported contract']
    name, version = record.get('contract'), record.get('contract_version')
    if not isinstance(name, str) or not isinstance(version, str):
        return ['schema contract and version must be strings']
    if (name, version) not in CONTRACTS:
        return ['schema unsupported contract/version combination']
    schema = SCHEMAS[f'{version}/{CONTRACTS[name, version]}']
    validator = Draft202012Validator(schema, registry=REGISTRY,
                                     format_checker=FORMATS)
    errors = [f'schema {list(e.absolute_path)}: {e.message}'
              for e in validator.iter_errors(record)]
    if errors:
        return errors
    try:
        rfc8785.dumps(record)
    except (ValueError, UnicodeError) as error:
        return [f'encoding: {error}']
    if record['contract'] in ('DeviceBinding', 'PilotDeviceBinding'):
        credential = record['credential']
        start, end = _time(credential['not_before']), _time(credential['not_after'])
        if start >= end:
            errors.append('DB-TIME: certificate validity window is empty or reversed')
        if 'activation' in record:
            activated = _time(record['activation']['activated_at'])
            if not start <= activated < end:
                errors.append('DB-TIME: activation is outside certificate validity')
            if activated > _time(record['issued_at']):
                errors.append('DB-TIME: activation is after snapshot issuance')
    if record['contract'] in ('PublishRequest', 'Publication'):
        for key in ('instance_id', 'logical_device_id'):
            values = [t[key] for t in record['targets']]
            if len(set(values)) != len(values):
                errors.append(f'PUB-03: duplicate target {key}')
    if record['contract'] == 'Publication':
        if _time(record['accepted_at']) > _time(record['issued_at']):
            errors.append('PUB-TIME: acceptance is after record issuance')
    if record['contract'] in ('PilotPolicy', 'PilotAdmissionDecision'):
        if _time(record['valid_from']) >= _time(record['expires_at']):
            errors.append('PILOT-TIME: validity window is empty or reversed')
        if _time(record['issued_at']) >= _time(record['expires_at']):
            errors.append('PILOT-TIME: record was issued after its validity window')
    if record['contract'] == 'PilotAdoptionRecord':
        if _time(record['source']['observed_at']) > _time(record['issued_at']):
            errors.append('PILOT-TIME: observation is after record issuance')
    if record['contract'] == 'PilotPolicy':
        targets = record['targets']
        for field in ('asset_ref', 'identity_ref', 'storage_ref'):
            values = [t[field] if field == 'asset_ref' else t[field]['digest'] for t in targets]
            if len(set(values)) != len(values):
                errors.append(f'PILOT-TARGET: duplicate {field}')
    if record['contract'] == 'PilotDeviceBinding' and 'activation' in record:
        if record['activation']['policy_ref'] != record['policy_ref']:
            errors.append('PILOT-BINDING: activation policy differs from binding policy')
    return errors


def validate_publication_binding(publication, request):
    """Check linked records, not caller authorization or the deferred plan schema."""
    errors = validate(publication) + validate(request)
    if errors:
        return errors
    if publication['contract'] != 'Publication' or request['contract'] != 'PublishRequest':
        return ['expected Publication and PublishRequest']
    if publication['request_digest'] != digest(request):
        errors.append('PUB-05: request digest mismatch')
    for field in ('plan_ref', 'targets', 'idempotency_key'):
        if publication[field] != request[field]:
            errors.append(f'PUB-03: request/publication {field} mismatch')
    return errors


TRANSITIONS = {
    'staged': {'active', 'quarantined', 'revoked', 'retired'},
    'active': {'superseded', 'quarantined', 'revoked', 'retired'},
    'quarantined': {'active', 'revoked', 'retired'},
    'superseded': {'revoked', 'retired'},
    'revoked': {'retired'},
    'retired': set(),
}


def validate_binding_transition(previous, current):
    """Compare two snapshots; actual activation still needs external proof."""
    errors = validate(previous) + validate(current)
    if errors:
        return errors
    if (previous['contract'] not in ('DeviceBinding', 'PilotDeviceBinding')
            or current['contract'] != previous['contract']
            or current['contract_version'] != previous['contract_version']):
        return ['expected two bindings of the same contract/version']
    immutable = ('record_id', 'tenant_id', 'security_domain_id', 'logical_device_id',
                 'instance_id', 'storage_generation', 'bootstrap_identity_ref', 'credential')
    if previous['contract'] == 'PilotDeviceBinding':
        immutable += ('target', 'adoption_ref', 'admission_ref', 'policy_ref',
                      'audience', 'profile', 'permissions', 'full_qualification')
    for field in immutable:
        if previous[field] != current[field]:
            errors.append(f'DB-05: tuple field changed: {field}')
    if current['revision'] <= previous['revision']:
        errors.append('DB-REVISION: revision must increase')
    if _time(current['issued_at']) < _time(previous['issued_at']):
        errors.append('DB-TIME: snapshot time moved backwards')
    old, new = previous['state'], current['state']
    if old != new and new not in TRANSITIONS[old]:
        errors.append(f'DB-STATE: forbidden transition {old} to {new}')
    if old == 'quarantined' and new == 'active':
        activation = current['activation']
        if (_time(activation['activated_at']) < _time(previous['issued_at']) or
                activation == previous.get('activation')):
            errors.append('DB-STATE: reactivation requires new recovery verification')
    return errors


def record_ref(record):
    return {'record_id': record['record_id'], 'revision': record['revision'],
            'digest': digest(record)}


def validate_pilot_handoff(adoption, policy, decision, *, checked_at):
    """Offline consistency only; does not authenticate authorities or approve use.

    Runtime consumers must additionally retrieve current authoritative records,
    authenticate their distinct roles, verify evidence and enforce revocation.
    checked_at must come from the consumer's trusted clock, never the payload.
    """
    records = (adoption, policy, decision)
    expected = ('PilotAdoptionRecord', 'PilotPolicy', 'PilotAdmissionDecision')
    errors = []
    for record, name in zip(records, expected):
        errors.extend(validate(record))
        if not isinstance(record, dict) or record.get('contract') != name:
            errors.append(f'PILOT-TYPE: expected {name}')
    if errors:
        return errors
    time_schema = SCHEMAS['0.2.0-draft.1/common']['$defs']['timestamp']
    if not Draft202012Validator(time_schema, format_checker=FORMATS).is_valid(checked_at):
        return ['PILOT-TIME: checked_at must be a canonical UTC timestamp']
    now = _time(checked_at)
    for record in records:
        for field in ('tenant_id', 'security_domain_id'):
            if record[field] != adoption[field]:
                errors.append(f'PILOT-SCOPE: {field} mismatch')
        if _time(record['issued_at']) > now:
            errors.append('PILOT-TIME: future-issued record')
    for record in (policy, decision):
        if not _time(record['valid_from']) <= now < _time(record['expires_at']):
            errors.append('PILOT-TIME: record not currently valid')
    if (_time(decision['valid_from']) < _time(policy['valid_from'])
            or _time(decision['expires_at']) > _time(policy['expires_at'])):
        errors.append('PILOT-TIME: decision exceeds policy validity')
    if any(_time(decision['issued_at']) < _time(r['issued_at']) for r in (adoption, policy)):
        errors.append('PILOT-TIME: decision predates its inputs')
    age = (now - _time(adoption['source']['observed_at'])).total_seconds()
    if age < 0 or age > policy['max_observation_age_seconds']:
        errors.append('PILOT-TIME: observation outside policy freshness bound')
    if decision['adoption_ref'] != record_ref(adoption):
        errors.append('PILOT-REF: adoption revision/digest mismatch')
    if decision['policy_ref'] != record_ref(policy):
        errors.append('PILOT-REF: policy revision/digest mismatch')
    if adoption['qualification_policy_ref'] != policy['qualification_policy_ref']:
        errors.append('PILOT-REF: qualification baseline mismatch')
    if decision['target'] != adoption['target'] or adoption['target'] not in policy['targets']:
        errors.append('PILOT-TARGET: target not bound to decision and cohort')
    if decision['decision'] != 'approved':
        errors.append('PILOT-DENIED: decision is not approved')
    gaps = {name for name, value in adoption['qualification'].items()
            if value['outcome'] != 'passed'}
    if set(decision['accepted_gaps']) != gaps or not gaps <= set(policy['allowed_gaps']):
        errors.append('PILOT-GAPS: exact observed gaps must be permitted and accepted')
    for name, value in adoption['conditions'].items():
        required = name not in ('unresolved_mutation', 'conflicting_ownership', 'known_key_exposure')
        if value != required:
            errors.append(f'PILOT-BLOCKER: {name}')
    return errors


def validate_pilot_binding(binding, adoption, policy, decision, *, checked_at):
    """Check exact pilot links; a valid staged/denied snapshot grants no access."""
    errors = validate_pilot_handoff(adoption, policy, decision, checked_at=checked_at)
    errors.extend(validate(binding))
    if not isinstance(binding, dict) or binding.get('contract') != 'PilotDeviceBinding':
        errors.append('PILOT-TYPE: expected PilotDeviceBinding')
    if errors:
        return errors
    for field, value in (
        ('adoption_ref', record_ref(adoption)), ('policy_ref', record_ref(policy)),
        ('admission_ref', record_ref(decision)), ('target', adoption['target']),
        ('tenant_id', adoption['tenant_id']), ('security_domain_id', adoption['security_domain_id']),
        ('audience', policy['enrollment_audience']), ('profile', policy['profile']),
        ('permissions', policy['permissions']),
    ):
        if binding[field] != value:
            errors.append(f'PILOT-BINDING: {field} mismatch')
    if binding['credential']['issuer_id'] != policy['operational_issuer_id']:
        errors.append('PILOT-BINDING: issuer differs from pilot policy')
    if _time(binding['issued_at']) > _time(checked_at):
        errors.append('PILOT-TIME: future-issued binding')
    if _time(binding['issued_at']) < max(_time(decision['issued_at']), _time(decision['valid_from'])):
        errors.append('PILOT-TIME: binding predates effective admission decision')
    if 'activation' in binding:
        activated = _time(binding['activation']['activated_at'])
        if not max(_time(decision['issued_at']), _time(decision['valid_from'])) <= activated < _time(decision['expires_at']):
            errors.append('PILOT-TIME: activation outside admission decision')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        try:
            errors = validate(load(path))
        except (ValueError, OSError, UnicodeError) as error:
            errors = [str(error)]
        if errors:
            failed = True
            print(f'{path}: INVALID\n  ' + '\n  '.join(errors))
        else:
            print(f'{path}: valid record; authority and current policy not checked')
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())

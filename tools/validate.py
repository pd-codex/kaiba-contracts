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
SCHEMA_PATH = ROOT / 'schemas' / VERSION
SCHEMAS = {p.stem: json.loads(p.read_text()) for p in SCHEMA_PATH.glob('*.json')}
REGISTRY = Registry().with_resources(
    (schema['$id'], Resource.from_contents(schema)) for schema in SCHEMAS.values()
)
FORMATS = FormatChecker()
for required_format in ('date-time', 'uri'):
    if required_format not in FORMATS.checkers:
        raise RuntimeError(f'Missing {required_format} validation; install requirements-dev.txt')
CONTRACTS = {
    'ProvisioningRecord': 'provisioning-record',
    'DeviceBinding': 'device-binding',
    'PublishRequest': 'publish-request',
    'Publication': 'publication',
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
    if not isinstance(record, dict) or record.get('contract') not in CONTRACTS:
        return ['unsupported contract']
    schema = SCHEMAS[CONTRACTS[record['contract']]]
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
    if record['contract'] == 'DeviceBinding':
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
    if previous['contract'] != 'DeviceBinding' or current['contract'] != 'DeviceBinding':
        return ['expected two DeviceBinding records']
    immutable = ('record_id', 'tenant_id', 'security_domain_id', 'logical_device_id',
                 'instance_id', 'storage_generation', 'bootstrap_identity_ref', 'credential')
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

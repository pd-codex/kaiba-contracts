"""Offline RPC consistency checks, not authority authentication or live policy."""

import re

from jsonschema import Draft202012Validator

from tools.validate import FORMATS, SCHEMAS, _time, dns_workload_identity, validate


def validate_dns_workload_authorization(response, request, *, zone, now):
    """Check a response against caller-retained request context and trusted time.

    The consumer supplies its configured zone and authenticated peer ID through
    request, never from the response. This helper cannot prove nonce generation,
    non-reuse, authenticated transport, live PostgreSQL state or DNS assignment.
    """
    errors = validate(response)
    if not isinstance(response, dict) or response.get('contract') != 'DNSWorkloadAuthorization':
        errors.append('DNS-AUTH-TYPE: expected DNSWorkloadAuthorization')
    if errors:
        return errors
    if (not isinstance(request, dict) or set(request) != {'spiffe_id', 'request_id'}
            or dns_workload_identity(request.get('spiffe_id')) is None
            or not isinstance(request.get('request_id'), str)
            or re.fullmatch(r'[0-9a-f]{32}', request['request_id']) is None):
        return ['DNS-AUTH-REQUEST: expected canonical peer and fresh 32-lowerhex nonce']
    definitions = SCHEMAS['0.5.0-draft.1/dns-workload-authorization']['$defs']
    if not Draft202012Validator(definitions['dnsName']).is_valid(zone):
        return ['DNS-AUTH-ZONE: configured zone must use canonical DNS name syntax']
    if not Draft202012Validator(definitions['timestamp'], format_checker=FORMATS).is_valid(now):
        return ['DNS-AUTH-TIME: trusted current time must be canonical UTC']
    for field in ('request_id', 'spiffe_id'):
        if response[field] != request[field]:
            errors.append(f'DNS-AUTH-REQUEST: response {field} differs from the retained request')
    if response['hostname'] != f"pi-{response['dns_device_id']}.{zone}":
        errors.append('DNS-AUTH-NAME: response hostname differs from assigned ID and configured zone')
    if not _time(response['checked_at']) <= _time(now) < _time(response['expires_at']):
        errors.append('DNS-AUTH-TIME: response is future-dated or expired')
    return errors

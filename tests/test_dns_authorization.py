import copy
import unittest

from tools.dns_authorization import validate_dns_workload_authorization
from tools.validate import ROOT, load, loads, validate


def response():
    return load(ROOT / 'examples/valid/dns-authorization-current.json')


def request():
    return load(ROOT / 'examples/context/dns-authorization-request.json')


def consume(value, context=None, *, now='2026-09-29T12:00:02Z', zone='kaiba.network'):
    return validate_dns_workload_authorization(
        value, request() if context is None else context, zone=zone, now=now)


class DNSAuthorizationTests(unittest.TestCase):
    def test_independent_dns_assignment_preserves_logical_identity(self):
        original = response()
        self.assertEqual(consume(original), [])
        self.assertNotEqual(original['logical_device_id'], original['dns_device_id'])
        changed = copy.deepcopy(original)
        changed.update(dns_device_id='7654321', hostname='pi-7654321.kaiba.network')
        self.assertEqual(consume(changed), [])
        changed['hostname'] = 'pi-device-fixture-001.kaiba.network'
        self.assertTrue(validate(changed))

    def test_response_is_bound_to_nonce_and_authenticated_peer(self):
        for field, value in (
            ('request_id', 'fedcba9876543210fedcba9876543210'),
            ('spiffe_id', request()['spiffe_id'].replace('kaiba.network', 'owner.example')),
            ('spiffe_id', request()['spiffe_id'].replace('instance-fixture-001', 'replacement')),
        ):
            with self.subTest(field=field, value=value):
                context = request()
                context[field] = value
                self.assertTrue(any('DNS-AUTH-REQUEST' in e for e in consume(response(), context)))

    def test_consumer_binds_exact_configured_zone(self):
        value = response()
        value['hostname'] = 'pi-001.attacker.example'
        self.assertEqual(validate(value), [])
        self.assertTrue(consume(value))
        self.assertEqual(consume(value, zone='attacker.example'), [])
        for zone in ('Kaiba.Network', 'kaiba.network.', '', 'a_b.example', None):
            with self.subTest(zone=zone):
                self.assertTrue(consume(response(), zone=zone))

    def test_time_boundaries_and_fractional_precision(self):
        for now, accepted in (
            ('2026-09-29T11:59:59.999999Z', False),
            ('2026-09-29T12:00:00Z', True),
            ('2026-09-29T12:00:04.999999Z', True),
            ('2026-09-29T12:00:05Z', False),
            ('2026-09-29T12:00:05.000001Z', False),
        ):
            with self.subTest(now=now):
                self.assertEqual(not consume(response(), now=now), accepted)
        value = load(ROOT / 'examples/valid/dns-authorization-fractional-rollover.json')
        self.assertEqual(consume(value, now='2026-09-30T00:00:00.123456Z'), [])

    def test_only_exact_five_second_response_window_is_valid(self):
        for end in ('2026-09-29T11:59:59Z', '2026-09-29T12:00:00Z',
                    '2026-09-29T12:00:04.999999Z', '2026-09-29T12:00:05.000001Z'):
            with self.subTest(end=end):
                value = response()
                value['expires_at'] = end
                self.assertTrue(any('DNS-AUTH-TIME' in e for e in validate(value)))

    def test_noncanonical_time_is_not_normalized(self):
        for timestamp in ('2026-09-29T12:00:00+00:00', '2026-09-29t12:00:00z',
                          '2026-09-29T12:00:60Z', '2026-09-29T12:00:00.0000001Z',
                          '2026-09-29T12:00:00Z\n', '2026-02-30T12:00:00Z', None):
            with self.subTest(timestamp=timestamp):
                value = response()
                value['checked_at'] = timestamp
                self.assertTrue(validate(value))
                self.assertTrue(consume(response(), now=timestamp))

    def test_canonical_workload_identity_and_tuple(self):
        for uri in (response()['spiffe_id'].replace('dns-updater', 'dns_updater'),
                    response()['spiffe_id'].replace('kaiba.network', 'Kaiba.Network'),
                    response()['spiffe_id'].replace('kaiba.network', 'kaiba.network.'),
                    response()['spiffe_id'].replace('kaiba.network', 'kaiba.network:443'),
                    response()['spiffe_id'].replace('dns-updater', 'dns%2dupdater'),
                    response()['spiffe_id'] + '?query=1', response()['spiffe_id'] + '/'):
            with self.subTest(uri=uri):
                value = response()
                value['spiffe_id'] = uri
                self.assertTrue(validate(value))
        for field in ('logical_device_id', 'instance_id'):
            value = response()
            value[field] = 'different'
            self.assertTrue(validate(value))

    def test_hostname_and_dns_id_bounds(self):
        for device_id in ('00', '0' * 61, '１２３', '00a', '001\n'):
            with self.subTest(device_id=device_id):
                value = response()
                value.update(dns_device_id=device_id, hostname=f'pi-{device_id}.kaiba.network')
                self.assertTrue(validate(value))
        value = response()
        value.update(dns_device_id='0' * 60, hostname='pi-' + '0' * 60 + '.owner')
        self.assertEqual(consume(value, zone='owner'), [])
        zone = '.'.join(['a' * 63] * 3 + ['a' * 54])
        value = response()
        value['hostname'] = 'pi-001.' + zone
        self.assertEqual(len(value['hostname']), 253)
        self.assertEqual(consume(value, zone=zone), [])
        value['hostname'] += 'a'
        self.assertTrue(validate(value))

    def test_request_shape_is_closed_and_nonce_is_not_coerced(self):
        original = request()
        variants = [None, {}, dict(original, unexpected=True),
                    {'request_id': original['request_id']},
                    {'spiffe_id': original['spiffe_id']}]
        for nonce in ('', 'a' * 31, 'a' * 33, 'F' * 32, 123, 'a' * 32 + '\n'):
            variants.append(dict(original, request_id=nonce))
        for context in variants:
            with self.subTest(context=context):
                errors = validate_dns_workload_authorization(
                    response(), context, zone='kaiba.network', now='2026-09-29T12:00:02Z')
                self.assertTrue(errors)

    def test_response_has_no_durable_envelope_or_bearer_fields(self):
        for field, value in (('record_id', 'record-1'), ('revision', 1),
                             ('authority_id', 'untrusted'), ('tenant_id', 'tenant'),
                             ('token', 'bearer'), ('zone', 'kaiba.network'),
                             ('permission', 'fleet:admin')):
            with self.subTest(field=field):
                self.assertTrue(validate(dict(response(), **{field: value})))
        for key in response():
            value = response()
            del value[key]
            self.assertTrue(validate(value))

    def test_json_ambiguity_and_wire_family_relabelling_are_rejected(self):
        with self.assertRaises(ValueError):
            loads('{"request_id":"a","request_id":"b"}')
        for version in ('0.4.0-draft.1', '0.5.0', '0.6.0-draft.1'):
            self.assertTrue(validate(dict(response(), contract_version=version)))
        self.assertTrue(validate(dict(response(), contract='WorkloadBinding')))
        self.assertTrue(consume(load(ROOT / 'examples/valid/workload-binding-active.json')))

    def test_offline_checks_do_not_prove_authority_or_nonreuse(self):
        value = response()
        self.assertEqual(consume(value), [])
        self.assertEqual(consume(value), [])
        # The same bytes remain well formed. Only the runtime consumer can bind
        # them to one authenticated exchange and prohibit reuse or caching.


if __name__ == '__main__':
    unittest.main()

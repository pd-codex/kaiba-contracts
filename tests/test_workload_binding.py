import copy
import unittest

from tools.validate import ROOT, load, validate


def example(name='active'):
    return load(ROOT / 'examples' / 'valid' / f'workload-binding-{name}.json')


def matching_uri(record):
    return (f"spiffe://{record['trust_domain']}/device/{record['logical_device_id']}"
            f"/instance/{record['instance_id']}/workload/{record['workload']}")


class WorkloadBindingTests(unittest.TestCase):
    def test_canonical_identity_binds_every_registry_component(self):
        original = example()
        self.assertEqual(validate(original), [])
        for field, value in (
            ('trust_domain', 'another.example'),
            ('logical_device_id', 'other-device'),
            ('instance_id', 'replacement-instance'),
            ('workload', 'other-workload'),
        ):
            with self.subTest(field=field):
                record = copy.deepcopy(original)
                record[field] = value
                self.assertTrue(any('WB-IDENTITY' in e for e in validate(record)))
                record['spiffe_id'] = matching_uri(record)
                self.assertEqual(validate(record), [])

    def test_uri_aliases_cannot_select_the_same_membership(self):
        canonical = example()['spiffe_id']
        for uri in (
            canonical.replace('spiffe://', 'https://'),
            canonical.replace('spiffe://', 'SPIFFE://'),
            canonical.replace('kaiba.network', 'Kaiba.Network'),
            canonical.replace('kaiba.network', 'kaiba.network.'),
            canonical.replace('kaiba.network', 'kaiba.network:443'),
            canonical.replace('kaiba.network', 'caller@kaiba.network'),
            canonical.replace('/device/', '//device/'),
            canonical.replace('/device/', '/device/../device/'),
            canonical.replace('dns-updater', 'dns%2dupdater'),
            canonical + '/', canonical + '?operation=dns:update',
            canonical + '#identity',
        ):
            with self.subTest(uri=uri):
                record = example()
                record['spiffe_id'] = uri
                self.assertTrue(validate(record))

    def test_segments_reject_encoding_and_path_ambiguity_even_with_matching_uri(self):
        for field in ('logical_device_id', 'instance_id', 'workload'):
            for value in ('', 'Uppercase', 'café', 'device/id', '../device',
                          '.', '..', 'device.id', 'device:id', '%61', ' space',
                          'space ', 'line\n', '-first', '_first', 'a' * 65):
                with self.subTest(field=field, value=value):
                    record = example()
                    record[field] = value
                    record['spiffe_id'] = matching_uri(record)
                    self.assertTrue(any(e.startswith('schema ') for e in validate(record)))

    def test_domain_has_canonical_label_and_total_length_bounds(self):
        for value in ('', '.example', 'example.', 'a..example', 'Upper.example',
                      'café.example', 'a_b.example', '-a.example', 'a-.example',
                      'example:443', 'a' * 64, 'line\n',
                      '.'.join(['a' * 63] * 4)):
            with self.subTest(domain=value):
                record = example()
                record['trust_domain'] = value
                record['spiffe_id'] = matching_uri(record)
                self.assertTrue(any(e.startswith('schema ') for e in validate(record)))

    def test_longest_profile_identity_and_single_label_domain_are_valid(self):
        record = example()
        record['trust_domain'] = '.'.join(['a' * 63] * 3 + ['a' * 61])
        for field in ('logical_device_id', 'instance_id', 'workload'):
            record[field] = 'x' * 64
        record['spiffe_id'] = matching_uri(record)
        self.assertEqual(len(record['trust_domain']), 253)
        self.assertEqual(len(record['spiffe_id']), 482)
        self.assertEqual(validate(record), [])
        record.update(trust_domain='owner', logical_device_id='a',
                      instance_id='1', workload='dns_updater-1')
        record['spiffe_id'] = matching_uri(record)
        self.assertEqual(validate(record), [])

    def test_nonactive_state_and_empty_permissions_are_valid_denial_records(self):
        for state in ('active', 'quarantined', 'retired'):
            for permissions in ([], ['dns:update']):
                with self.subTest(state=state, permissions=permissions):
                    record = example()
                    record.update(state=state, permissions=permissions)
                    self.assertEqual(validate(record), [])
        for state in ('staged', 'revoked', 'superseded', 'unknown'):
            record = example()
            record['state'] = state
            self.assertTrue(validate(record))

    def test_permissions_are_closed_and_required(self):
        for permissions in (['dns:read'], ['dns:update', 'dns:update'],
                            ['dns:update', '*'], 'dns:update', None):
            with self.subTest(permissions=permissions):
                record = example()
                record['permissions'] = permissions
                self.assertTrue(validate(record))
        record = example()
        del record['permissions']
        self.assertTrue(validate(record))

    def test_schema_cannot_prove_authority_or_current_enrollment(self):
        record = example()
        record.update(authority_id='untrusted-registry',
                      issued_at='2000-01-01T00:00:00Z')
        self.assertEqual(validate(record), [])
        # Authentication, freshness and active enrollment remain independent
        # registry/consumer obligations; a payload cannot establish them.

    def test_unknown_fields_cannot_add_credentials_or_readiness(self):
        for field, value in (('certificate_serial', '1a2b'), ('svid', 'fake'),
                             ('production_ready', True), ('role', 'server')):
            with self.subTest(field=field):
                record = example()
                record[field] = value
                self.assertTrue(validate(record))

    def test_old_and_new_wire_families_cannot_be_relabelled(self):
        for version in ('0.1.0-draft.1', '0.2.0-draft.1', '0.3.0-draft.1',
                        '0.4.0-draft.1', '0.5.0'):
            with self.subTest(version=version):
                record = example()
                record['contract_version'] = version
                self.assertTrue(validate(record))
        for fixture in ('binding-active', 'pilot-binding-a-active'):
            record = load(ROOT / 'examples' / 'valid' / f'{fixture}.json')
            self.assertEqual(validate(record), [])
            record['contract_version'] = '0.5.0-draft.1'
            self.assertTrue(validate(record))
            record['contract'] = 'WorkloadBinding'
            self.assertTrue(validate(record))


if __name__ == '__main__':
    unittest.main()

import copy
import unittest

from jsonschema import Draft202012Validator

from tools.validate import (
    ROOT, SCHEMAS, digest, load, loads, validate,
    validate_binding_transition, validate_publication_binding,
)


def example(name):
    return load(ROOT / 'examples' / 'valid' / f'{name}.json')


class ContractTests(unittest.TestCase):
    def test_schemas_are_valid_2020_12_schemas(self):
        for name, schema in SCHEMAS.items():
            with self.subTest(schema=name):
                Draft202012Validator.check_schema(schema)

    def test_positive_and_negative_corpus(self):
        manifest = load(ROOT / 'examples' / 'manifest.json')
        for case in manifest:
            with self.subTest(path=case['path']):
                errors = validate(load(ROOT / case['path']))
                self.assertEqual(not errors, case['valid'], errors)
                if not case['valid']:
                    schema_error = any(e.startswith('schema ') for e in errors)
                    self.assertEqual(schema_error, case['level'] == 'schema', errors)

    def test_corpus_covers_every_record_example(self):
        declared = {x['path'] for x in load(ROOT / 'examples' / 'manifest.json')}
        actual = {str(p.relative_to(ROOT)) for kind in ('valid', 'invalid')
                  for p in (ROOT / 'examples' / kind).glob('*.json')}
        self.assertEqual(actual, declared)

    def test_development_record_is_valid_but_explicitly_not_ready(self):
        record = example('provisioning-development')
        self.assertEqual(validate(record), [])
        self.assertFalse(record['readiness']['production_ready'])
        self.assertFalse(record['readiness']['enrollment_ready'])
        self.assertEqual(record['source']['state'], 'security_applied')

    def test_binding_reference_matches_candidate_record(self):
        binding = example('binding-active')
        record = example('provisioning-production-candidate')
        self.assertEqual(binding['provisioning_ref'], {
            'record_id': record['record_id'], 'revision': record['revision'],
            'digest': digest(record),
        })
        self.assertEqual(binding['tenant_id'], record['tenant_id'])
        self.assertEqual(binding['security_domain_id'], record['security_domain_id'])

    def test_publication_matches_exact_request_and_plan_fixture(self):
        request = example('publish-request')
        publication = example('publication')
        self.assertEqual(validate_publication_binding(publication, request), [])
        plan = load(ROOT / 'examples' / 'context' / 'deployment-plan.stub.json')
        self.assertEqual(request['plan_ref'], {
            'record_id': plan['record_id'], 'revision': plan['revision'],
            'digest': digest(plan),
        })
        self.assertEqual(request['targets'], plan['eligible_targets'])
        self.assertEqual(publication['tenant_id'], plan['tenant_id'])
        self.assertEqual(publication['security_domain_id'], plan['security_domain_id'])

    def test_request_substitution_is_detected(self):
        request = example('publish-request')
        publication = example('publication')
        for field in ('plan', 'instance', 'revision', 'key'):
            changed = copy.deepcopy(request)
            if field == 'plan':
                changed['plan_ref']['revision'] += 1
            elif field == 'instance':
                changed['targets'][0]['instance_id'] = 'replacement-instance'
            elif field == 'revision':
                changed['targets'][0]['expected_desired_state_revision'] += 1
            else:
                changed['idempotency_key'] = 'different-request'
            with self.subTest(field=field):
                self.assertEqual(validate(changed), [])
                self.assertTrue(validate_publication_binding(publication, changed))

    def test_reordered_object_keys_keep_retry_digest(self):
        request = example('publish-request')
        rearranged = dict(reversed(list(request.items())))
        self.assertEqual(digest(request), digest(rearranged))
        self.assertEqual(validate_publication_binding(example('publication'), rearranged), [])

    def test_schema_valid_record_is_not_an_authenticity_claim(self):
        record = example('binding-active')
        record['authority_id'] = 'untrusted-fixture-authority'
        self.assertEqual(validate(record), [])
        # Origin and live inventory authorization are explicitly integration gates.

    def test_valid_binding_lifecycle(self):
        self.assertEqual(validate_binding_transition(
            example('binding-staged'), example('binding-active')), [])
        self.assertEqual(validate_binding_transition(
            example('binding-active'), example('binding-retired')), [])

    def test_retired_binding_cannot_reactivate(self):
        retired = example('binding-retired')
        changed = copy.deepcopy(retired)
        changed.update(state='active', revision=4, issued_at='2026-09-11T16:00:00Z')
        self.assertTrue(any('forbidden transition' in e
                            for e in validate_binding_transition(retired, changed)))

    def test_tuple_and_tenant_cannot_change_in_place(self):
        previous = example('binding-active')
        for field, replacement in [('instance_id', 'new-instance'),
                                   ('tenant_id', 'other-tenant'),
                                   ('storage_generation', 2)]:
            current = copy.deepcopy(previous)
            current['revision'] += 1
            current[field] = replacement
            with self.subTest(field=field):
                self.assertTrue(any('tuple field changed' in e
                                    for e in validate_binding_transition(previous, current)))

    def test_rekey_is_not_a_mutation_of_an_existing_tuple(self):
        previous = example('binding-active')
        current = copy.deepcopy(previous)
        current['revision'] += 1
        current['credential']['key_generation'] += 1
        self.assertTrue(validate_binding_transition(previous, current))

    def test_stale_snapshot_revision_is_rejected(self):
        active = example('binding-active')
        self.assertTrue(any('revision must increase' in e
                            for e in validate_binding_transition(active, active)))

    def test_recovery_requires_a_new_verification(self):
        previous = example('binding-active')
        previous.update(state='quarantined', revision=3, issued_at='2026-09-11T13:00:00Z')
        current = copy.deepcopy(previous)
        current.update(state='active', revision=4, issued_at='2026-09-11T13:05:00Z')
        self.assertTrue(any('new recovery verification' in e
                            for e in validate_binding_transition(previous, current)))

    def test_duplicate_keys_and_non_json_numbers_are_rejected(self):
        for raw in ['{"state":"staged","state":"active"}', '{"x":NaN}',
                    '{"x":Infinity}', '{"x":9007199254740992}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                loads(raw)

    def test_jcs_known_order_and_escape_behavior(self):
        # Canonical bytes for this small vector, independently specified here.
        import hashlib
        value = loads('{"z":1,"a":"line\\nend"}')
        expected = b'{"a":"line\\nend","z":1}'
        self.assertEqual(digest(value), 'sha256:' + hashlib.sha256(expected).hexdigest())

    def test_schema_registry_references_are_bundled(self):
        identifiers = {schema['$id'] for schema in SCHEMAS.values()}

        def check(value):
            if isinstance(value, dict):
                if '$ref' in value:
                    self.assertIn(value['$ref'].split('#')[0], identifiers)
                for child in value.values():
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)
        for schema in SCHEMAS.values():
            check(schema)

    def test_timestamp_precision_is_explicit(self):
        record = example('publication')
        record['issued_at'] = '2026-09-11T12:10:01.0000001Z'
        self.assertTrue(any(e.startswith('schema ') for e in validate(record)))


if __name__ == '__main__':
    unittest.main()

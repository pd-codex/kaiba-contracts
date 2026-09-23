import copy
import unittest

from tools.validate import (
    ROOT, load, record_ref, validate, validate_binding_transition,
    validate_pilot_binding, validate_pilot_handoff,
)


def example(name):
    return load(ROOT / 'examples' / 'valid' / f'pilot-{name}.json')


class PilotContractTests(unittest.TestCase):
    def setUp(self):
        self.adoption = example('adoption-a')
        self.policy = example('policy')
        self.decision = example('decision-a')
        self.now = '2026-09-23T12:10:00Z'

    def check(self):
        return validate_pilot_handoff(self.adoption, self.policy, self.decision,
                                      checked_at=self.now)

    def rebind(self):
        self.decision['adoption_ref'] = record_ref(self.adoption)
        self.decision['policy_ref'] = record_ref(self.policy)

    def test_portable_linked_corpus(self):
        cases = load(ROOT / 'examples/pilot-handoff-cases.json')
        names = [c['name'] for c in cases]
        self.assertEqual(len(names), len(set(names)))
        for case in cases:
            with self.subTest(case=case['name']):
                records = {k: load(ROOT / case[k])
                           for k in ('adoption', 'policy', 'decision', 'binding')}
                # The corpus tests linked semantics, not malformed single records.
                for record in records.values():
                    self.assertEqual(validate(record), [])
                errors = validate_pilot_binding(**records, checked_at=case['checked_at'])
                self.assertEqual(not errors, case['valid'], errors)
                if not case['valid']:
                    self.assertTrue(any(e.startswith(case['rule'] + ':') for e in errors), errors)

    def test_each_hard_blocker_survives_rebound_approval(self):
        for field in self.adoption['conditions']:
            with self.subTest(field=field):
                before = self.adoption['conditions'][field]
                self.adoption['conditions'][field] = not before
                self.rebind()
                self.assertIn(f'PILOT-BLOCKER: {field}', self.check())
                self.adoption['conditions'][field] = before

    def test_third_target_cannot_borrow_an_admission(self):
        self.adoption['target']['asset_ref'] = 'unapproved-third-device'
        self.decision['target'] = copy.deepcopy(self.adoption['target'])
        self.rebind()
        self.assertTrue(any(e.startswith('PILOT-TARGET:') for e in self.check()))

    def test_tenant_and_domain_are_compared_across_all_records(self):
        for field in ('tenant_id', 'security_domain_id'):
            for record in (self.policy, self.decision):
                before = record[field]
                record[field] = 'other-scope'
                self.rebind()
                self.assertTrue(any('PILOT-SCOPE' in e for e in self.check()))
                record[field] = before

    def test_exact_gaps_are_required_even_with_rebound_digests(self):
        self.policy['allowed_gaps'].remove('FA-01')
        self.rebind()
        self.assertTrue(any('PILOT-GAPS' in e for e in self.check()))
        self.policy['allowed_gaps'].append('FA-01')
        self.adoption['qualification']['FA-01'].update(
            outcome='passed', evidence_refs=[self.adoption['source']['inventory_ref']])
        self.rebind()
        self.assertTrue(any('PILOT-GAPS' in e for e in self.check()))
        self.decision['accepted_gaps'].remove('FA-01')
        self.assertEqual(self.check(), [])
        self.assertFalse(self.adoption['full_qualification'])

    def test_changed_prestate_invalidates_decision(self):
        self.adoption['source']['commit'] = 'b' * 40
        self.assertTrue(any('PILOT-REF' in e for e in self.check()))

    def test_qualification_baseline_cannot_be_substituted(self):
        self.adoption['qualification_policy_ref']['digest'] = 'sha256:' + 'b' * 64
        self.rebind()
        self.assertIn('PILOT-REF: qualification baseline mismatch', self.check())

    def test_clock_is_explicit_and_boundaries_are_exclusive(self):
        for now in ('bad', '2026-09-23T12:10:00', '2026-09-23T13:00:00Z',
                    '2026-09-23T11:59:59Z'):
            self.now = now
            self.assertTrue(self.check(), now)

    def test_decision_cannot_outlive_policy(self):
        self.decision['expires_at'] = '2026-09-24T13:00:00Z'
        self.assertTrue(any('exceeds policy' in e for e in self.check()))

    def test_unknown_contract_profile_and_missing_conditions_fail(self):
        for change in ('version', 'profile', 'qualification', 'condition'):
            record = copy.deepcopy(self.policy if change == 'profile' else self.adoption)
            if change == 'version':
                record['contract_version'] = '0.2.0'
            elif change == 'profile':
                record['profile'] = 'unknown-profile'
            elif change == 'qualification':
                del record['qualification']['FA-08']
            else:
                del record['conditions']['known_key_exposure']
            self.assertTrue(validate(record), change)

    def test_legacy_development_cannot_be_upgraded_or_used_as_adoption(self):
        old = load(ROOT / 'examples/valid/provisioning-development.json')
        self.assertEqual(validate(old), [])
        self.assertTrue(validate_pilot_handoff(old, self.policy, self.decision,
                                               checked_at=self.now))
        old['readiness']['enrollment_ready'] = True
        self.assertTrue(validate(old))

    def test_bindings_keep_distinct_keys_and_scopes(self):
        a, b = example('binding-a-active'), example('binding-b-active')
        for field in ('logical_device_id', 'instance_id', 'target'):
            self.assertNotEqual(a[field], b[field])
        self.assertNotEqual(a['credential']['spki_digest'], b['credential']['spki_digest'])
        for field in ('adoption_ref', 'policy_ref', 'admission_ref', 'audience',
                      'permissions', 'target'):
            changed = copy.deepcopy(a)
            if field.endswith('_ref'):
                changed[field]['revision'] += 1
            elif field == 'audience':
                changed[field] = 'rehearsal'
            elif field == 'permissions':
                changed[field].append('fleet:admin')
            else:
                changed[field] = b[field]
            self.assertTrue(validate_pilot_binding(changed, self.adoption, self.policy,
                                                  self.decision, checked_at=self.now), field)

    def test_staged_and_denied_states_are_not_offline_authorization(self):
        staged, active = example('binding-a-staged'), example('binding-a-active')
        self.assertEqual(validate_binding_transition(staged, active), [])
        revoked = copy.deepcopy(active)
        revoked.update(state='revoked', revision=3)
        self.assertEqual(validate_binding_transition(active, revoked), [])
        self.assertEqual(validate_pilot_binding(revoked, self.adoption, self.policy,
                                               self.decision, checked_at=self.now), [])
        # Consistency accepts a revoked snapshot; relying services MUST deny it.
        again = copy.deepcopy(active)
        again['revision'] = 4
        self.assertTrue(validate_binding_transition(revoked, again))

    def test_pilot_cannot_be_promoted_by_a_binding_transition(self):
        before = example('binding-a-active')
        after = copy.deepcopy(before)
        after['contract'] = 'DeviceBinding'
        after['contract_version'] = '0.1.0-draft.1'
        self.assertTrue(validate_binding_transition(before, after))
        for field in ('policy_ref', 'admission_ref', 'adoption_ref'):
            after = copy.deepcopy(before)
            after['revision'] += 1
            after[field]['revision'] += 1
            self.assertTrue(validate_binding_transition(before, after), field)

    def test_payload_authority_claim_is_not_authenticated_by_local_checks(self):
        self.adoption['authority_id'] = 'not-a-trusted-station'
        self.rebind()
        self.assertEqual(self.check(), [])
        # Only independently authenticated runtime resolution can reject this.


if __name__ == '__main__':
    unittest.main()

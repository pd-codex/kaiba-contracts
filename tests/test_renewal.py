import copy
import unittest
from tools.validate import ROOT, load, validate, validate_pilot_renewal, record_ref

class RenewalTests(unittest.TestCase):
    def setUp(self):
        def example(name): return load(ROOT / 'examples/valid' / (name + '.json'))
        self.a = example('pilot-renewal-authorization-a')
        self.b = example('pilot-binding-a-active')
        self.adoption = example('pilot-adoption-a')
        self.policy = example('pilot-renewal-policy')
        self.decision = example('pilot-renewal-decision-a')
        self.now = '2026-09-23T12:15:00Z'

    def check(self, **kwargs):
        return validate_pilot_renewal(self.a, self.b, self.adoption, self.policy, self.decision,
            checked_at=self.now, predecessor_certificate_digest='sha256:'+'a'*64,
            predecessor_credential_revision=kwargs.get('revision', 1))

    def test_seven_day_authorization(self): self.assertEqual(self.check(), [])

    def test_identity_substitution(self):
        for field in ('instance_id','logical_device_id','spki_digest','issuer_id','credential_slot','storage_generation','key_generation','audience','tenant_id','security_domain_id'):
            with self.subTest(field=field):
                original = self.a[field]
                self.a[field] = original+1 if type(original) is int else 'sha256:'+'b'*64 if field=='spki_digest' else 'other'
                self.assertTrue(self.check())
                self.a[field] = original

    def test_exact_predecessor(self):
        self.a['predecessor_binding_ref']['revision'] += 1
        self.assertTrue(any(e.startswith('RENEWAL-PREDECESSOR:') for e in self.check()))

    def test_certificate_substitution(self):
        self.a['predecessor_certificate_digest']='sha256:'+'b'*64
        self.assertTrue(any(e.startswith('RENEWAL-PREDECESSOR:') for e in self.check()))

    def test_runtime_revision_required(self):
        for value in (2, True, '1'):
            self.assertTrue(any(e.startswith('RENEWAL-REVISION:') for e in self.check(revision=value)))

    def test_inactive_predecessors(self):
        for state in ('quarantined','revoked','retired','superseded'):
            self.b['state']=state;self.a['predecessor_binding_ref']=record_ref(self.b)
            self.assertTrue(any(e.startswith('RENEWAL-PREDECESSOR:') for e in self.check()))

    def test_expired_predecessor(self):
        self.now = self.b['credential']['not_after']
        self.assertTrue(any(e.startswith('RENEWAL-PREDECESSOR:') for e in self.check()))

    def test_stale_observations_even_in_seven_day_window(self):
        self.now = '2026-09-24T12:15:00Z'
        self.assertTrue(any(e.startswith('PILOT-') for e in self.check()))

    def test_successor_reference_substitution(self):
        for field in ('adoption_ref','admission_ref','policy_ref'):
            original=copy.deepcopy(self.a[field]);self.a[field]['digest']='sha256:'+'b'*64
            self.assertTrue(any(e.startswith('RENEWAL-RECORDS:') for e in self.check()))
            self.a[field]=original

    def test_exact_deadline_and_future(self):
        for now in ('2026-09-23T12:14:59Z','2026-09-30T12:15:00Z'):
            self.now=now;self.assertTrue(self.check())

    def test_shorter_decision_bounds_window(self):
        self.decision['expires_at']='2026-09-24T12:15:00Z'
        self.a['admission_ref']=record_ref(self.decision)
        self.assertTrue(any(e.startswith('RENEWAL-WINDOW:') for e in self.check()))

    def test_unknown_fields_fail_closed(self):
        self.a['automatic_renewal']=True
        self.assertTrue(any(e.startswith('schema ') for e in validate(self.a)))

    def test_old_version_cannot_accept_new_record(self):
        self.a['contract_version']='0.2.0-draft.1'
        self.assertTrue(validate(self.a))

if __name__ == '__main__': unittest.main()

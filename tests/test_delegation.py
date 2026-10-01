import copy
import unittest

from tests.test_contracts import example
from tools.validate import validate
from tools.delegation import validate_delegation_transition, validate_delegated_renewal


class DelegationTests(unittest.TestCase):
    def setUp(self):
        self.delegation = example('pilot-renewal-delegation')
        self.authorization = example('pilot-renewal-authorization-a')

    def check(self, **kwargs):
        return validate_delegated_renewal(self.delegation, self.authorization,
            checked_at=kwargs.get('now', '2026-09-23T12:15:00Z'),
            principal=kwargs.get('principal', self.delegation['automation_principal']))

    def test_renewal_and_boundaries(self):
        self.assertEqual(self.check(), [])
        for now in ('2026-09-23T12:12:59Z', '2026-10-23T12:13:00Z'):
            self.assertTrue(self.check(now=now))
        self.assertTrue(self.check(principal=self.delegation['owner_principal']))

    def test_scope_changes_denied(self):
        for field in ('instance_id', 'logical_device_id', 'issuer_id', 'audience',
                      'credential_slot', 'spki_digest'):
            with self.subTest(field=field):
                old = self.authorization[field]
                self.authorization[field] = 'sha256:' + 'f'*64 if field == 'spki_digest' else 'substituted'
                self.assertTrue(self.check())
                self.authorization[field] = old

    def revoked(self):
        return {**copy.deepcopy(self.delegation), 'revision': 2, 'state': 'revoked',
                'issued_at': '2026-09-24T12:13:00Z', 'revoked_at': '2026-09-24T12:13:00Z',
                'revocation_reason': 'Owner stopped automation'}

    def test_revocation_only_transition(self):
        successor = self.revoked()
        self.assertEqual(validate(successor), [])
        self.assertEqual(validate_delegation_transition(self.delegation, successor), [])
        for field in ('owner_principal', 'automation_principal', 'correlation_id'):
            changed = {**successor, field: 'replacement'}
            self.assertTrue(validate_delegation_transition(self.delegation, changed))
        self.assertTrue(validate_delegation_transition(successor, self.delegation))
        self.delegation = successor
        self.assertTrue(self.check(now='2026-09-24T12:13:00Z'))

    def test_duplicate_instances_and_key_substitution(self):
        duplicate = copy.deepcopy(self.delegation['members'][0])
        duplicate['spki_digest'] = 'sha256:' + 'f'*64
        self.delegation['members'].append(duplicate)
        self.assertTrue(validate(self.delegation))

    def test_authorization_cannot_cross_term(self):
        self.authorization['issued_at'] = '2026-10-22T12:13:00Z'
        self.authorization['valid_from'] = '2026-10-22T12:13:00Z'
        self.authorization['expires_at'] = '2026-10-24T12:13:00Z'
        self.assertTrue(self.check(now='2026-10-22T12:13:00Z'))

    def test_unknown_authority_extension_rejected(self):
        self.delegation['allow_recovery'] = True
        self.assertTrue(validate(self.delegation))

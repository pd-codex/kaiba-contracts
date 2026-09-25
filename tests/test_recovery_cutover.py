import copy
import unittest
from tools.validate import ROOT,load,record_ref,digest,validate_binding_transition,validate_pilot_renewal
from tools.recovery_cutover import validate_recovery_cutover as validate_cutover, validate_recovery_staged as validate_staged

class RecoveryCutoverTests(unittest.TestCase):
    def setUp(self):
        def ex(name):return load(ROOT/'examples/valid'/('pilot-'+name+'.json'))
        self.a=ex('recovery-authorization-a');self.b=ex('recovery-predecessor')
        self.s=ex('recovery-staged-a');self.r=ex('recovery-installed-a');self.n=ex('recovery-active-a')
        self.adoption=ex('adoption-a');self.policy=ex('renewal-policy');self.decision=ex('renewal-decision-a')
        self.now='2026-09-23T12:19:00Z'
    def check(self):
        return validate_cutover(self.a,self.b,self.s,self.r,self.n,self.adoption,self.policy,self.decision,
            checked_at=self.now,predecessor_certificate_digest='sha256:'+'a'*64,predecessor_credential_revision=1,predecessor_access_expires_at='2026-09-23T12:14:00Z')
    def rebind_receipt(self):
        self.n['installation_receipt_ref']=record_ref(self.r)
        self.n['activation']['verifier_receipt_ref']['digest']=digest(self.r)
    def test_valid_cutover(self):self.assertEqual(self.check(),[])
    def test_staged_is_not_active(self):
        self.n=copy.deepcopy(self.s);self.assertTrue(self.check())
    def test_missing_installation_receipt(self):
        self.n.pop('installation_receipt_ref');self.assertTrue(self.check())
    def test_proof_cannot_bind_other_operation_or_certificate(self):
        for key,value in [('operation_id','other'),('certificate_digest','sha256:'+'f'*64),('tenant_id','other'),('security_domain_id','other')]:
            with self.subTest(key=key):
                old=self.r[key];self.r[key]=value;self.rebind_receipt();self.assertTrue(self.check());self.r[key]=old
        self.rebind_receipt()
    def test_proof_exact_reference_binding(self):
        for key in ['authorization_ref','predecessor_binding_ref','staged_binding_ref']:
            old=copy.deepcopy(self.r[key]);self.r[key]['revision']+=1;self.rebind_receipt();self.assertTrue(self.check());self.r[key]=old
    def test_active_tuple_substitution(self):
        for field in ['record_id','authority_id','instance_id','logical_device_id','certificate_digest','credential_revision','bootstrap_identity_ref']:
            with self.subTest(field=field):
                old=copy.deepcopy(self.n[field]);self.n[field]=old+1 if type(old) is int else {'uri':'urn:other','digest':'sha256:'+'f'*64} if isinstance(old,dict) else 'sha256:'+'f'*64 if field=='certificate_digest' else 'other'
                self.assertTrue(self.check());self.n[field]=old
    def test_active_before_proof(self):
        self.n['activation']['activated_at']='2026-09-23T12:16:00Z';self.assertTrue(self.check())
    def test_stale_proof(self):
        self.now='2026-09-23T12:22:01Z';self.assertTrue(self.check())
    def test_predecessor_revoked_after_staging(self):
        self.b['state']='revoked';self.assertTrue(self.check())
    def test_stale_proof_at_later_cutover(self):
        self.now='2026-09-23T13:00:00Z';self.assertTrue(self.check())
    def test_installation_does_not_extend_window(self):
        self.s['credential']['not_after']='2026-10-01T12:15:00Z';self.assertTrue(self.check())
    def test_generic_transition_cannot_replace_certificate(self):
        later=copy.deepcopy(self.n);later['revision']+=1;later['credential']['certificate_serial']='a3'
        self.assertTrue(validate_binding_transition(self.n,later))
    def test_generic_transition_cannot_replace_renewal_identity(self):
        for field in ['credential_revision','certificate_digest','recovery_authorization_ref','predecessor_binding_ref']:
            later=copy.deepcopy(self.n);later['revision']+=1
            if isinstance(later[field],dict):later[field]['revision']+=1
            elif type(later[field]) is int:later[field]+=1
            else:later[field]='sha256:'+'f'*64
            self.assertTrue(validate_binding_transition(self.n,later))
    def test_subsequent_renewal_uses_versioned_predecessor(self):
        a=load(ROOT/'examples/valid/pilot-renewal-authorization-a.json')
        a.update(record_id='fixture:renewal-a-3',operation_id='fixture-renewal-a-3',
            issued_at='2026-09-23T12:19:00Z',valid_from='2026-09-23T12:20:00Z',
            predecessor_binding_ref=record_ref(self.n),predecessor_certificate_digest=self.n['certificate_digest'],
            predecessor_credential_revision=2,successor_credential_revision=3)
        args=dict(checked_at='2026-09-23T12:20:00Z',predecessor_certificate_digest=self.n['certificate_digest'],predecessor_credential_revision=2)
        self.assertEqual(validate_pilot_renewal(a,self.n,self.adoption,self.policy,self.decision,**args),[])
        args['predecessor_credential_revision']=1
        self.assertTrue(validate_pilot_renewal(a,self.n,self.adoption,self.policy,self.decision,**args))
    def test_staged_authority_and_operation(self):
        for field in ('authority_id','correlation_id'):
            old=self.s[field];self.s[field]='other'
            with self.subTest(field=field):self.assertTrue(self.check())
            self.s[field]=old
    def test_wrong_supersedes_reference(self):
        self.s['supersedes']=dict(self.s['predecessor_binding_ref']);self.s['supersedes']['revision']+=1
        self.assertTrue(self.check())
    def test_challenge_cannot_outlive_successor(self):
        self.s['credential']['not_after']='2026-09-23T12:19:30Z'
        self.n['credential']['not_after']=self.s['credential']['not_after']
        self.r['staged_binding_ref']=record_ref(self.s)
        self.r['challenge_expires_at']='2026-09-23T12:20:00Z';self.rebind_receipt()
        self.assertTrue(self.check())
    def test_versioned_recovery_predecessor_revision(self):
        from tools.recovery import validate_pilot_recovery
        a=copy.deepcopy(self.a)
        a.update(record_id='fixture:recovery-a-3',operation_id='fixture-recovery-a-3',
            issued_at='2026-09-23T12:20:00Z',valid_from='2026-09-23T12:20:00Z',
            predecessor_access_expires_at='2026-09-23T12:19:00Z',
            predecessor_binding_ref=record_ref(self.n),predecessor_certificate_digest=self.n['certificate_digest'],
            predecessor_credential_revision=2,successor_credential_revision=3)
        args=dict(checked_at='2026-09-23T12:20:00Z',predecessor_certificate_digest=self.n['certificate_digest'],predecessor_credential_revision=2,predecessor_access_expires_at='2026-09-23T12:19:00Z')
        self.assertEqual(validate_pilot_recovery(a,self.n,self.adoption,self.policy,self.decision,**args),[])
        args['predecessor_credential_revision']=1
        self.assertTrue(validate_pilot_recovery(a,self.n,self.adoption,self.policy,self.decision,**args))
    def test_checks_do_not_mutate_inputs(self):
        before=copy.deepcopy((self.a,self.b,self.s,self.r,self.n));self.assertEqual(self.check(),[])
        self.assertEqual(before,(self.a,self.b,self.s,self.r,self.n))

if __name__=='__main__':unittest.main()

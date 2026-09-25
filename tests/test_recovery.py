import copy, unittest
from tools.validate import ROOT, load, record_ref, validate, validate_pilot_renewal
from tools.recovery import validate_pilot_recovery, validate_recovery_challenge
class RecoveryTests(unittest.TestCase):
 def setUp(self):
  ex=lambda n:load(ROOT/'examples/valid'/(n+'.json'))
  self.a=ex('pilot-recovery-authorization-a');self.b=ex('pilot-recovery-predecessor');self.c=ex('pilot-recovery-challenge-a')
  self.adoption=ex('pilot-adoption-a');self.policy=ex('pilot-renewal-policy');self.decision=ex('pilot-renewal-decision-a');self.now='2026-09-23T12:15:00Z'
 def check(self,**kw):
  args=dict(checked_at=self.now,predecessor_certificate_digest='sha256:'+'a'*64,predecessor_credential_revision=1,predecessor_access_expires_at='2026-09-23T12:14:00Z');args.update(kw)
  return validate_pilot_recovery(self.a,self.b,self.adoption,self.policy,self.decision,**args)
 def challenge(self):return validate_recovery_challenge(self.c,self.a,checked_at=self.now)
 def test_valid_offline_recovery(self):self.assertEqual(self.check(),[]);self.assertEqual(self.challenge(),[])
 def test_effective_admission_expiry_before_certificate(self):
  self.b['credential']['not_after']='2026-09-24T12:00:00Z';self.a['predecessor_binding_ref']=record_ref(self.b);self.assertEqual(self.check(),[])
 def test_unexpired_wrong_or_invalid_runtime_deadline(self):
  for d in ('2026-09-23T12:16:00Z','2026-09-23T12:13:00Z',None,'bad'):
   with self.subTest(d=d):self.assertTrue(self.check(predecessor_access_expires_at=d))
 def test_not_recovery_from_bad_state(self):
  for state in ('quarantined','revoked','retired','superseded'):
   self.b['state']=state;self.a['predecessor_binding_ref']=record_ref(self.b);self.assertTrue(self.check())
 def test_same_identity_and_permissions(self):
  for field in ('instance_id','logical_device_id','spki_digest','issuer_id','credential_slot','storage_generation','key_generation','audience','tenant_id','security_domain_id','permissions','target'):
   saved=copy.deepcopy(self.a[field]);self.a[field]=saved+1 if type(saved)is int else [] if type(saved)is list else {} if type(saved)is dict else 'other'
   with self.subTest(field=field):self.assertTrue(self.check())
   self.a[field]=saved
 def test_runtime_certificate_and_revision(self):
  self.assertTrue(self.check(predecessor_certificate_digest='sha256:'+'d'*64))
  for rev in (True,0,2,'1'):self.assertTrue(self.check(predecessor_credential_revision=rev))
 def test_fresh_admission_required(self):
  self.now='2026-09-24T12:15:00Z';self.assertTrue(self.check())
 def test_exact_expiry_and_future(self):
  for now in ('2026-09-23T12:14:59Z','2026-09-30T12:15:00Z'):
   self.now=now;self.assertTrue(self.check());self.assertTrue(self.challenge())
 def test_challenge_binding_substitutions(self):
  for field in ('operation_id','instance_id','authority_id','tenant_id','security_domain_id','spki_digest','predecessor_certificate_digest','predecessor_binding_ref','authorization_ref'):
   saved=copy.deepcopy(self.c[field]);self.c[field]='other' if type(saved)is str else {**saved,'revision':saved['revision']+1}
   with self.subTest(field=field):self.assertTrue(self.challenge())
   self.c[field]=saved
 def test_challenge_deadline_exclusive(self):
  self.now=self.c['expires_at'];self.assertTrue(self.challenge())
 def test_old_dispatch_and_unknown_fields(self):
  for version in ('0.2.0-draft.1','0.3.0-draft.1'):
   bad=copy.deepcopy(self.a);bad['contract_version']=version;self.assertTrue(validate(bad))
  self.a['bypass_expiry']=True;self.assertTrue(validate(self.a))
 def test_normal_renewal_still_rejects_expiry(self):
  a=load(ROOT/'examples/valid/pilot-renewal-authorization-a.json');a['predecessor_binding_ref']=record_ref(self.b)
  self.assertTrue(validate_pilot_renewal(a,self.b,self.adoption,self.policy,self.decision,checked_at=self.now,predecessor_certificate_digest='sha256:'+'a'*64,predecessor_credential_revision=1))
if __name__=='__main__':unittest.main()

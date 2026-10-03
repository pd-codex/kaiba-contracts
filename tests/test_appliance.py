import copy
import unittest
from tools.validate import validate

class ApplianceTests(unittest.TestCase):
    def release(self):
        digest = 'sha256:' + 'a'*64
        return dict(contract='ApplianceRelease',contract_version='0.7.0-draft.1',
                    release_id='two',profile_id='shipping',layout_digest=digest,
                    source_revision='a'*40,state_format=1,readable_state_formats=[1],
                    catalog_digest=digest,images=[dict(slot=slot,verity_root_hash=digest,
                    artifacts=[dict(role=role,digest=digest,size_bytes=64) for role in
                    ('boot','root','hash','metadata')]) for slot in ('A','B')])
    def test_release(self):
        self.assertEqual(validate(self.release()), [])
    def test_mutations(self):
        original=self.release()
        bad=copy.deepcopy(original);bad['images'][1]['slot']='A'
        self.assertTrue(validate(bad))
        bad=copy.deepcopy(original);bad['readable_state_formats']=[2]
        self.assertTrue(validate(bad))
        bad=copy.deepcopy(original);bad['images'][0]['artifacts'][0]['role']='root'
        self.assertTrue(validate(bad))
        bad=copy.deepcopy(original);bad['command']='sh'
        self.assertTrue(validate(bad))

from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

from heritage_workflow.cli import init_case, freeze, record_generation, record_review
from heritage_workflow.io import WorkflowError, dump, load, sha, inside
from heritage_workflow.pipeline import reproduce
from heritage_workflow.validation import verify_case

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='heritage-test-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.case=self.root/'case'
        init_case(self.case,'synthetic',True)

    def edit(self,fn):
        c=load(self.case/'case.json');fn(c);dump(self.case/'case.json',c)

    def test_offline_demo_build_and_zip(self):
        report=reproduce(self.case,self.root/'out')
        self.assertEqual(report['status'],'PASS')
        self.assertFalse(report['ai_images_regenerated'])
        self.assertEqual(report['historical_accuracy'],'UNVERIFIED')
        self.assertEqual(load(self.root/'out/ZIP_VERIFICATION.json')['status'],'PASS')

    def test_mutated_image_fails_hash(self):
        p=self.case/'synthetic.png';p.write_bytes(p.read_bytes()+b'altered')
        r=verify_case(self.case)
        self.assertEqual(r['status'],'FAIL')
        self.assertTrue(any('hash mismatch' in x for x in r['errors']))

    def test_unknown_claim_reference_fails(self):
        self.edit(lambda c:c['scenes'][0].update(claim_ids=['T999']))
        self.assertEqual(verify_case(self.case,False)['status'],'FAIL')

    def test_duplicate_source_id_fails(self):
        self.edit(lambda c:c['sources'].append(dict(c['sources'][0])))
        self.assertEqual(verify_case(self.case,False)['status'],'FAIL')

    def test_false_native_4k_fails(self):
        self.edit(lambda c:c['scenes'][0].update(native_4k=True))
        self.assertTrue(any('false native 4K' in x for x in verify_case(self.case,False)['errors']))

    def test_false_dimensions_fail(self):
        self.edit(lambda c:c['scenes'][0].update(final_dimensions=[3840,2160]))
        self.assertEqual(verify_case(self.case,False)['status'],'FAIL')

    def test_path_traversal_and_absolute_paths_fail(self):
        for value in ['../outside.png',str(self.root/'outside.png')]:
            with self.assertRaises(WorkflowError): inside(self.case,value)

    def test_symlink_escape_fails(self):
        outside=self.root/'outside';outside.mkdir()
        try:(self.case/'link').symlink_to(outside,target_is_directory=True)
        except (OSError,NotImplementedError):self.skipTest('Symlink creation is unavailable')
        with self.assertRaises(WorkflowError):inside(self.case,'link/data.json')

    def test_open_review_failure_blocks_and_resolution_preserves_history(self):
        self.edit(lambda c:c['reviews'].append({'scene_id':'SC01','criterion':'geometry','status':'FAIL'}))
        with self.assertRaises(WorkflowError):freeze(self.case)
        self.edit(lambda c:c['reviews'].append({'scene_id':'SC01','criterion':'geometry','status':'PASS'}))
        freeze(self.case)
        self.assertEqual(len(load(self.case/'case.json')['reviews']),2)
        self.assertEqual(verify_case(self.case)['status'],'PASS')

    def test_placeholder_case_is_not_release_ready(self):
        path=self.root/'draft';init_case(path,'unresearched',False)
        self.assertEqual(verify_case(path,False)['status'],'FAIL')

    def test_degenerate_camera_fails(self):
        self.edit(lambda c:c['scenes'][0]['camera'].update(look_at_m=c['scenes'][0]['camera']['position_m']))
        self.assertEqual(verify_case(self.case,False)['status'],'FAIL')

    def test_gallery_json_cannot_close_its_script(self):
        malicious='</script><img src=x onerror=alert(1)> and literal '+chr(92)+'u003c'
        self.edit(lambda c:c['scenes'][0].update(zh=[malicious]))
        freeze(self.case);reproduce(self.case,self.root/'escaped',False)
        html=(self.root/'escaped/gallery.html').read_text()
        block=re.search(r'<script id="caseData" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertNotIn('</script>',block)
        self.assertEqual(json.loads(block)['case']['scenes'][0]['zh'][0],malicious)

    def test_record_generation_preserves_previous_output(self):
        before=sha(self.case/'synthetic.png')
        a=argparse.Namespace(case=str(self.case),scene='SC01',image=str(self.case/'synthetic.png'),prompt=str(self.case/'synthetic.prompt.txt'),tool='synthetic-test-not-ai',model=None,seed=None,reference=[])
        rec=record_generation(a)
        self.assertEqual(rec['status'],'RECORDED_NOT_REVIEWED')
        self.assertEqual(sha(self.case/'synthetic.png'),before)
        self.assertEqual(load(self.case/'case.json')['new_generation_records'][0]['provider_model'],'UNVERIFIED_NOT_EXPOSED')

    def test_missing_reference_does_not_create_an_attempt(self):
        a=argparse.Namespace(case=str(self.case),scene='SC01',image=str(self.case/'synthetic.png'),prompt=str(self.case/'synthetic.prompt.txt'),tool='synthetic-test-not-ai',model=None,seed=None,reference=[str(self.root/'missing.png')])
        with self.assertRaises(WorkflowError):record_generation(a)
        self.assertFalse((self.case/'generated').exists())

    def test_new_image_requires_current_geometry_and_chronology_reviews(self):
        a=argparse.Namespace(case=str(self.case),scene='SC01',image=str(self.case/'synthetic.png'),prompt=str(self.case/'synthetic.prompt.txt'),tool='synthetic-test-not-ai',model=None,seed=None,reference=[])
        record_generation(a)
        with self.assertRaises(WorkflowError):freeze(self.case)
        for criterion in ['geometry','chronology']:
            record_review(argparse.Namespace(case=str(self.case),scene='SC01',criterion=criterion,status='UNVERIFIED',note='Synthetic test only; no historical certification',reviewer='test fixture'))
        freeze(self.case)
        self.assertEqual(verify_case(self.case)['status'],'PASS')

    def test_old_review_cannot_certify_a_changed_evidence_context(self):
        a=argparse.Namespace(case=str(self.case),scene='SC01',image=str(self.case/'synthetic.png'),prompt=str(self.case/'synthetic.prompt.txt'),tool='synthetic-test-not-ai',model=None,seed=None,reference=[])
        record_generation(a)
        for criterion in ['geometry','chronology']:
            record_review(argparse.Namespace(case=str(self.case),scene='SC01',criterion=criterion,status='PASS',note='Synthetic fixture',reviewer='test fixture'))
        freeze(self.case)
        self.edit(lambda c:c['claims'][0].update(text='Changed context after review'))
        with self.assertRaises(WorkflowError):freeze(self.case)

    def test_cli_runs_from_an_unrelated_cwd_without_pythonpath(self):
        entry=Path(__file__).resolve().parents[1]/'scripts/heritage.py'
        env=dict(os.environ);env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
        r=subprocess.run([sys.executable,'-I',str(entry),'verify','--case',str(self.case)],cwd=self.root,env=env,capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'],'PASS')

if __name__=='__main__':unittest.main()

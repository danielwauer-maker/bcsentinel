"""AI-PM 2.0: control plane never executes external models or writes to GitHub."""
import hashlib
import os
from unittest import mock
import project_store
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

import agent_control as a

SHA="c1978141c8ee70f52be07ba64df765364a56cb16fe51dea4b084951ade60142a"
TEXT="Review Sprint 4.01 evidence only. Report FAIL UNKNOWN PASS; no deployments. "*2

class ControlTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db=Path(self.temp.name)/"control.sqlite3"
        project_db=Path(self.temp.name)/'projects.sqlite3'
        rows=[{'id':f'{i+1}.01','title':'Task','area':'fiverr','sprint':'T',
               'technical_checked':False,'live_checked':False} for i in range(60)]
        rows.append({'id':'61.01','title':'Task','area':'fiverr','sprint':'T','technical_checked':False,'live_checked':False})
        rows.extend({'id':f'S{i}.01','title':'Task','area':'saas','sprint':'S',
                    'technical_checked':False,'live_checked':False} for i in range(24))
        project_store.import_rows({'state':'loaded','sha256':SHA,'filename':'test.xlsx','rows':rows},project_db)
        env=mock.patch.dict(os.environ,{'PROJECT_DB_PATH':str(project_db)})
        env.start()
        self.addCleanup(env.stop)
        self.assertEqual(a.read_status(self.db)["state"],"not_initialized")
        a.init(self.db,actor="owner",confirm=True)
    def proposal(self):
        return a.propose("4.01","evidence_review",SHA,TEXT,100,
                         path=self.db,actor="author",confirm=True)
    def funded(self):
        a.set_budget(500,path=self.db,actor="owner",confirm=True)
        created=self.proposal()
        return a.approve(created["id"],created["request_sha256"],
                         path=self.db,actor="reviewer",confirm=True)

    def test_defaults_zero_and_no_automatic_execution(self):
        s=a.read_status(self.db)
        self.assertEqual(s["budget"]["monthly_cap_cents"],0)
        self.assertEqual(s["execution"],"disabled")
        j=self.proposal()
        with self.assertRaises(ValueError):
            a.approve(j["id"],j["request_sha256"],path=self.db,actor="reviewer",confirm=True)
        self.assertEqual(a.read_status(self.db)["jobs"][0]["status"],"proposed")
        self.assertEqual(a.read_status(self.db)["global_release"],"NO_GO")

    def test_independent_approval_exact_sha_and_explicit_confirmation(self):
        a.set_budget(500,path=self.db,actor="owner",confirm=True)
        j=self.proposal()
        with self.assertRaises(ValueError):
            a.approve(j["id"],j["request_sha256"],path=self.db,actor="author",confirm=True)
        with self.assertRaises(ValueError):
            a.approve(j["id"],"0"*64,path=self.db,actor="reviewer",confirm=True)
        with self.assertRaises(ValueError):
            a.approve(j["id"],j["request_sha256"],path=self.db,actor="reviewer",confirm=False)
        a.approve(j["id"],j["request_sha256"],path=self.db,actor="reviewer",confirm=True)
        s=a.read_status(self.db)
        self.assertEqual(s["jobs"][0]["status"],"approved")
        self.assertEqual(s["budget"]["monthly_reserved_and_actual"][0]["reserved_or_actual_cents"],100)
        self.assertNotIn("request_text",s["jobs"][0])

    def test_only_one_claimed_slot_and_no_external_runner(self):
        self.funded()
        other=self.proposal()
        a.approve(other["id"],other["request_sha256"],path=self.db,actor="reviewer",confirm=True)
        s=a.read_status(self.db)
        first=min(j["id"] for j in s["jobs"])
        a.claim(first,path=self.db,actor="operator",confirm=True)
        with self.assertRaises(ValueError):
            a.claim(other["id"],path=self.db,actor="operator",confirm=True)
        self.assertEqual(a.read_status(self.db)["claimed_slots"],1)
        a.close(first,"completed",75,path=self.db,actor="operator",confirm=True)
        self.assertEqual(a.read_status(self.db)["claimed_slots"],0)
        a.claim(other["id"],path=self.db,actor="operator",confirm=True)
        self.assertEqual(a.read_status(self.db)["execution"],"disabled")

    def test_cancel_refunds_budget_reservation_and_completed_is_not_release(self):
        a.set_budget(100,path=self.db,actor="owner",confirm=True)
        j=self.proposal()
        a.approve(j["id"],j["request_sha256"],path=self.db,actor="reviewer",confirm=True)
        with self.assertRaises(ValueError):
            a.approve(self.proposal()["id"],hashlib.sha256(TEXT.encode()).hexdigest(),
                      path=self.db,actor="reviewer",confirm=True)
        a.close(j["id"],"cancelled",path=self.db,actor="owner",confirm=True)
        self.assertEqual(a.read_status(self.db)["budget"]["monthly_reserved_and_actual"],[])

    def test_no_overestimate_and_state_change_fails_closed(self):
        self.funded()
        job=a.read_status(self.db)["jobs"][0]["id"]
        with self.assertRaises(ValueError):
            a.close(job,"completed",200,path=self.db,actor="operator",confirm=True)
        with self.assertRaises(ValueError):
            a.close(job,"completed",0,path=self.db,actor="operator",confirm=True)
        with self.assertRaises(ValueError):
            a.claim(job,path=self.db,actor="author",confirm=True)
        a.claim(job,path=self.db,actor="operator",confirm=True)
        with self.assertRaises(ValueError):
            a.close(job,"completed",200,path=self.db,actor="operator",confirm=True)
        a.close(job,"completed",99,path=self.db,actor="operator",confirm=True)
        self.assertEqual(a.read_status(self.db)["global_release"],"NO_GO")
        self.assertEqual(a.read_status(self.db)["budget"]["monthly_reserved_and_actual"][0]["reserved_or_actual_cents"],99)

    def test_untrusted_inputs_and_confirmation(self):
        with self.assertRaises(ValueError):
            a.init(self.db,actor="owner",confirm=False)
        with self.assertRaises(ValueError):
            a.set_budget(-1,path=self.db,actor="owner",confirm=True)
        with self.assertRaises(ValueError):
            a.set_budget(200,path=self.db,actor="owner",confirm=False)
        with self.assertRaises(ValueError):
            a.propose("4.01","deploy",SHA,TEXT,1,path=self.db,actor="owner",confirm=True)
        with self.assertRaises(ValueError):
            a.propose("4.01","evidence_review","bad",TEXT,1,path=self.db,actor="owner",confirm=True)
        with self.assertRaises(ValueError):
            a.propose("4.01","evidence_review",SHA,"short",1,path=self.db,actor="owner",confirm=True)

    def test_only_verified_task_and_sha_can_be_proposed(self):
        with self.assertRaises(ValueError):
            a.propose('77.07','evidence_review',SHA,TEXT,100,
                      path=self.db,actor='author',confirm=True)
        with self.assertRaises(ValueError):
            a.propose('4.01','evidence_review','0'*64,TEXT,100,
                      path=self.db,actor='author',confirm=True)

    def test_budget_cannot_be_reduced_below_reserved_costs(self):
        self.funded()
        with self.assertRaises(ValueError):
            a.set_budget(99,path=self.db,actor='owner',confirm=True)
        self.assertEqual(a.read_status(self.db)['budget']['monthly_cap_cents'],500)

    def test_audit_is_only_local_metadata_no_secret_request_leaks(self):
        self.funded()
        s=a.read_status(self.db)
        self.assertTrue(any(x["event"]=="job.approved" for x in s["audit_recent"]))
        self.assertFalse(any("request_text" in x for x in s["jobs"]))

    def test_concurrent_claims_single_slot(self):
        a.set_budget(500,path=self.db,actor="owner",confirm=True)
        ids=[]
        for _ in range(2):
            j=self.proposal()
            a.approve(j["id"],j["request_sha256"],path=self.db,actor="reviewer",confirm=True)
            ids.append(j["id"])
        ready=threading.Barrier(2)
        result=[]
        def claim_job(i):
            ready.wait()
            try:
                a.claim(i,path=self.db,actor="operator",confirm=True)
                result.append("ok")
            except (ValueError,sqlite3.IntegrityError):
                result.append("denied")
        ts=[threading.Thread(target=claim_job,args=(i,)) for i in ids]
        for t in ts:t.start()
        for t in ts:t.join()
        self.assertEqual(sorted(result),["denied","ok"])

if __name__=="__main__":
    unittest.main()

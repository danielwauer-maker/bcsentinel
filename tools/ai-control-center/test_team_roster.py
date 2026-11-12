"""Team view never confuses proposed roles and real agent execution."""
import unittest
import copy
import datetime as dt
import team_roster as t

class TeamRosterTests(unittest.TestCase):
    def setUp(self):
        self.control={"state":"loaded","execution":"disabled","global_release":"NO_GO",
                      "jobs":[],"claimed_slots":0}
        self.daily={"state":"loaded","recommendation":{"task_id":"4.01",
                     "title":"Access-v2 Vertragsfreigabe"}}
        self.now=dt.datetime(2026,11,12,11,tzinfo=dt.timezone.utc)

    def view(self):
        return t.roster(self.control,self.daily,as_of=self.now)

    def test_eight_roles_are_disabled_without_fabricated_progress(self):
        result=self.view()
        self.assertEqual(result["state"],"loaded")
        self.assertEqual(result["agent_count"],8)
        self.assertEqual(result["active_agents"],0)
        self.assertEqual(result["assigned_agents"],0)
        self.assertEqual(result["waiting_for_operator"],8)
        self.assertFalse(result["role_assignments_supported"])
        self.assertTrue(all(r["runtime_state"]=="disabled" for r in result["members"]))
        self.assertTrue(all(r["current_sprint"] is None for r in result["members"]))
        self.assertTrue(all(r["progress_percent"] is None for r in result["members"]))
        pm=next(r for r in result["members"] if r["id"]=="pm")
        self.assertEqual(pm["suggested_review"]["task_id"],"4.01")
        self.assertFalse(pm["suggested_review"]["assigned"])
        self.assertTrue(all(x["id"]!="pm" for x in result["members"] if x["reports_to"]=="pm"))

    def test_claimed_job_is_unassigned_not_fictional_agent_activity(self):
        self.control["jobs"]=[{"id":7,"task_id":"4.01","status":"claimed",
                              "purpose":"evidence_review"}]
        x=self.view()
        self.assertEqual(x["pending_unassigned_jobs"][0]["id"],7)
        self.assertEqual(x["active_agents"],0)
        self.assertTrue(all(r["current_task"] is None for r in x["members"]))
        self.assertTrue(all(r["last_activity_at"] is None for r in x["members"]))

    def test_uninitialized_zero_budget_is_not_a_live_team(self):
        self.control={"state":"not_initialized","execution":"disabled","global_release":"NO_GO"}
        x=self.view()
        self.assertEqual(x["state"],"loaded")
        self.assertEqual(x["agent_count"],8)
        self.assertEqual(x["active_agents"],0)
        self.assertEqual(x["pending_unassigned_jobs"],[])

    def test_unavailable_or_unsafe_state_fails_closed(self):
        self.control["execution"]="enabled"
        self.assertEqual(self.view()["state"],"unavailable")
        self.control["execution"]="disabled"
        self.control["global_release"]="GO"
        self.assertEqual(self.view()["state"],"unavailable")
        self.control["global_release"]="NO_GO"
        self.control["state"]="unavailable"
        self.assertEqual(self.view()["state"],"unavailable")

    def test_no_recommendation_means_no_assigned_sprint(self):
        self.daily={"state":"unavailable"}
        result=self.view()
        self.assertTrue(all(r["suggested_review"] is None for r in result["members"]))
        self.assertEqual(result["active_agents"],0)

    def test_deterministic_and_read_only(self):
        before=copy.deepcopy((self.control,self.daily))
        self.assertEqual(self.view(),self.view())
        self.assertEqual((self.control,self.daily),before)

if __name__=="__main__":
    unittest.main()

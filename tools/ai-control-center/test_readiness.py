"""Excel-faithful readiness and planning projections; never treat legacy 65% as GO readiness."""
import datetime as dt
import unittest
from readiness import fiverr_readiness

def planning():
    hours=[2,3]+[4]*58+[53]
    # Total: 2+3+232+53=290; adjust last to 50 to yield 287
    hours[-1]=50
    rows=[{"area":"fiverr","id":f"{i}.01","sprint":"A" if i<2 else "B",
           "plan_hours":h,"technical_checked":i<2,"live_checked":i<2} for i,h in enumerate(hours)]
    rows.extend({"area":"saas","id":f"S{i}","plan_hours":999,
                 "technical_checked":True,"live_checked":True} for i in range(24))
    return {"state":"loaded","sha256":"test","hours_per_week":20,
            "legacy_start_fraction":0.65,"planning_issue_date":"Stand 11.11.2026  •  Fortschritt", "rows":rows}

class ReadinessTests(unittest.TestCase):
    def test_real_master_planning_arithmetic(self):
        r=fiverr_readiness(planning(),as_of=dt.date(2026,11,11))
        self.assertEqual(r["state"],"loaded")
        self.assertEqual(r["total_hours"],287)
        self.assertEqual(r["accepted_hours"],5)
        self.assertEqual(r["remaining_hours"],282)
        self.assertEqual(r["remaining_weeks"],14.1)
        self.assertEqual(r["remaining_workdays"],71)
        self.assertEqual(r["capacity_scenario_date"],"2027-02-18")
        self.assertAlmostEqual(r["gate_fraction"],5/287,places=5)
        self.assertAlmostEqual(r["legacy_estimate_fraction"],.65+.35*5/287,places=5)
        self.assertEqual(r["gate_count"],2)
        self.assertEqual(r["go_live"],"NO_GO")

    def test_saas_is_never_in_fiverr_readiness(self):
        r=fiverr_readiness(planning(),as_of=dt.date(2026,11,11))
        self.assertEqual(r["gate_total"],61)
        self.assertEqual(r["technical_count"],2)

    def test_fail_closed_without_workbook_or_capacity(self):
        self.assertEqual(fiverr_readiness({"state":"snapshot_only"})["state"],"unavailable")
        p=planning()
        p["hours_per_week"]=0
        self.assertEqual(fiverr_readiness(p)["state"],"unavailable")

    def test_no_fabricated_go_even_if_excel_checkboxes_all_set(self):
        p=planning()
        for row in p["rows"]:
            if row["area"]=="fiverr":
                row["technical_checked"]=True
                row["live_checked"]=True
        r=fiverr_readiness(p,as_of=dt.date(2026,11,11))
        self.assertEqual(r["remaining_hours"],0)
        self.assertEqual(r["go_live"],"ALL_GATES_CHECKED_REVALIDATION_REQUIRED")

if __name__=="__main__": unittest.main()

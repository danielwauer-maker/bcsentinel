"""AI-PM 2.2 executive layer contracts: no hidden sources or lost evidence."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parent

class ExecutiveViewTests(unittest.TestCase):
    def test_dashboard_keeps_full_detail_in_accessible_disclosure(self):
        html=(ROOT/"index.html").read_text()
        self.assertIn('id="executive-overview"',html)
        self.assertIn('id="executive-details"',html)
        self.assertIn('Alle Detailansichten öffnen',html)
        self.assertIn('id="evidence-list"',html)
        self.assertIn('id="pr-list"',html)
        self.assertIn('id="gates"',html)
        self.assertIn('id="exec-next"',html)
        self.assertIn('<script src="/executive.js"></script>',html)
        self.assertIn('window.renderExecutive(data)',html)
        self.assertLess(html.index('id="executive-overview"'),html.index('class="readiness-shell"'))
        self.assertLess(html.index('id="executive-details"'),html.index('id="evidence-list"'))
        self.assertEqual(html.count('id="executive-overview"'),1)
        self.assertEqual(html.count('id="executive-details"'),1)

    def test_executive_is_read_only_and_fails_closed(self):
        js=(ROOT/"executive.js").read_text()
        for required in ("NICHT FREIGEGEBEN", "Nicht verfügbar", "Kuratierte",
                         "plan.items", "review", "Snapshot:", "textContent",
                         "kein technischer Fortschritt"):
            self.assertIn(required.lower(),js.lower())
        for forbidden in ("innerHTML","localStorage","fetch(","XMLHttpRequest",
                          "POST","/api/approve","/api/agent/execute","eval("):
            self.assertNotIn(forbidden,js)

    def test_desktop_triage_has_filterable_readonly_sources(self):
        html=(ROOT/"index.html").read_text()
        for value in ('id="exec-triage-search"', 'id="exec-triage-kind"',
                      'id="exec-triage-limit"', 'id="exec-pr-items"',
                      'id="exec-work-list"', '<script src="/triage.js"></script>',
                      'window.renderTriage(data)'):
            self.assertIn(value,html)
        js=(ROOT/"triage.js").read_text()
        for expected in ("new Map()", "new Set(", "githubUrl(", "textContent",
                         "Keine passenden", "Quellen unvollständig"):
            self.assertIn(expected,js)
        for forbidden in ("innerHTML", "fetch(", "XMLHttpRequest", "localStorage",
                          "eval(", "POST", "/api/approve", "/api/agent/execute"):
            self.assertNotIn(forbidden,js)

    def test_js_packaged_inside_authenticated_image(self):
        dockerfile=(ROOT/"Dockerfile").read_text()
        self.assertIn("executive.js",dockerfile)
        self.assertIn("triage.js",dockerfile)
        app=(ROOT/"app.py").read_text()
        self.assertIn('request_path == "/executive.js"',app)
        self.assertIn('request_path == "/triage.js"',app)
        self.assertIn('"application/javascript; charset=utf-8"',app)

if __name__=="__main__":unittest.main()

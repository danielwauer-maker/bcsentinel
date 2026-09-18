"""Execute real dashboard JavaScript in Chromium; no server or tenant access."""
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    source = Path(__file__).resolve().parents[1] / 'backend/app/static/js/analytics-dashboard.js'
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        # Load after DOMContentLoaded: test normalization without starting dashboard fetches.
        page.set_content('<html><body></body></html>', wait_until='load')
        page.add_script_tag(content=source.read_text(encoding='utf-8'))
        result = page.evaluate("""() => {
          const rows = [
            {finding_id: 'group-a', code: 'CHECK_A', title: 'Same title', affected_count: 10, estimated_impact_eur: 100, recommendation: 'First'},
            {finding_id: 'group-b', code: 'CHECK_A', title: 'Same title', affected_count: 20, estimated_impact_eur: 250, recommendation: 'Second'}
          ];
          const data = {visibility: {is_premium: true}, top_findings: rows};
          const issues = normalizeIssuesForPage(data);
          const actions = normalizeActionsForPage({...data, actions_page: {items: [
            {finding_id: 'group-b', title: 'Same title'}, {finding_id: 'group-a', title: 'Same title'}
          ]}});
          const fallback = normalizeIssuesForPage({...data, top_findings: rows.map(({finding_id, ...row}) => row)});
          return {issues, actions, fallback, en: LOCAL_DASHBOARD_UI.en.business_impact_records,
            de: LOCAL_DASHBOARD_UI.de.business_impact_records};
        }""")
        assert [row['id'] for row in result['issues']] == ['group-a', 'group-b']
        assert [row['code'] for row in result['issues']] == ['CHECK_A', 'CHECK_A']
        assert [row['count'] for row in result['issues']] == [10, 20]
        assert [row['impact'] for row in result['issues']] == [100, 250]
        assert [row['action'] for row in result['actions']] == ['Second', 'First']
        assert len({row['id'] for row in result['fallback']}) == 2
        assert result['en'] == 'check occurrences'
        assert result['de'] == 'Prüftreffer'
        browser.close()
    print('PASS: distinct group rows, reordered action identity, legacy row keys, DE/EN occurrence units')


if __name__ == '__main__':
    main()

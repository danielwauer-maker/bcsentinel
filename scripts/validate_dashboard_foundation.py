from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / 'dashboard'

required = [
    DASH / 'package.json',
    DASH / 'src' / 'api' / 'client.ts',
    DASH / 'src' / 'foundation' / 'contexts.tsx',
    DASH / 'src' / 'foundation' / 'AppShell.tsx',
    DASH / 'src' / 'styles.css',
]
for path in required:
    assert path.exists(), f'missing {path}'

css = (DASH / 'src' / 'styles.css').read_text(encoding='utf-8')
shell = (DASH / 'src' / 'foundation' / 'AppShell.tsx').read_text(encoding='utf-8')
client = (DASH / 'src' / 'api' / 'client.ts').read_text(encoding='utf-8')
contexts = (DASH / 'src' / 'foundation' / 'contexts.tsx').read_text(encoding='utf-8')

assert '#FF921F' in css and '#082138' in css, 'brand orange contract missing'
assert '#14213D' in css, 'navigation token missing'
assert 'grid-template-columns: var(--sidebar-width) minmax(0, 1fr)' in css, 'desktop shell columns missing'
assert '.main-column { grid-column: 2' in css, 'main content must remain right of sidebar'
assert '.app-footer' in css and 'width: 100%' in css, 'footer missing from main column'
assert '@media (max-width: 1279px)' in css and 'translateX(-100%)' in css, 'tablet drawer missing'
assert '@media (max-width: 767px)' in css, 'mobile breakpoint missing'
assert 'prefers-reduced-motion' in css, 'reduced motion missing'
assert 'X-Tenant-Id' in client and 'X-Api-Token' in client, 'tenant API isolation headers missing'
assert "credentials: 'omit'" in client, 'ambient browser credentials must not be sent'
assert 'raw' not in client.lower() or 'raw provider' not in client.lower(), 'raw provider errors must not surface'
assert 'AuthContext' in contexts and 'TenantContext' in contexts and 'EntitlementContext' in contexts
assert "access !== 'granted'" in contexts, 'authentication must not imply entitlement access'
assert 'Settings' in shell and 'Monitoring' in shell and 'Actions' in shell, 'core navigation missing'
assert 'start_scan' not in shell.lower() and 'run scan' not in shell.lower(), 'web shell must not introduce BC write actions'
print('Dashboard Foundation Quality Gate: PASS')

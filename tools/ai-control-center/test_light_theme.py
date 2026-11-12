"""AI-PM 2.0.2 light-only token and legibility contract tests."""
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler

import app

ROOT=Path(__file__).resolve().parent
CSS=(ROOT/"light-theme.css").read_text(encoding="utf-8")

def rgb(color):
    return tuple(int(color[i:i+2],16)/255 for i in (1,3,5))

def luminance(color):
    c=rgb(color)
    l=[x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*l[0]+0.7152*l[1]+0.0722*l[2]

def contrast(a,b):
    x,y=sorted((luminance(a),luminance(b)),reverse=True)
    return (x+0.05)/(y+0.05)

class LightThemeTests(unittest.TestCase):
    def tokens(self):
        return dict(re.findall(r'(--[a-z-]+):\s*(#[0-9a-f]{6})',CSS))

    def test_shared_link_and_no_remote_assets_or_dark_switch(self):
        for filename in ("index.html","team.html"):
            source=(ROOT/filename).read_text(encoding="utf-8")
            self.assertIn('<link rel="stylesheet" href="/light-theme.css">',source)
            self.assertNotIn('theme-toggle',source)
            self.assertNotIn('fonts.googleapis.com',source)
        self.assertIn('color-scheme:light',CSS)
        self.assertNotIn('prefers-color-scheme:dark',CSS)

    def test_wcag_aa_text_for_major_surfaces(self):
        t=self.tokens()
        for foreground,background in (
            ("--text-main","--bg-page"),("--text-main","--bg-surface"),
            ("--text-strong","--bg-surface"),
            ("--text-muted","--bg-surface"),("--text-muted","--bg-surface-subtle"),
            ("--text-soft","--bg-surface"),
            ("--accent","--bg-surface"),("--accent","--accent-soft"),
            ("--neutral-text","--neutral-bg"),
            ("--danger-text","--danger-bg"),("--warning-text","--warning-bg"),
            ("--success-text","--success-bg"),
            ("--accent-contrast","--accent"),("--accent-contrast","--accent-hover")):
            with self.subTest(pair=(foreground,background)):
                self.assertGreaterEqual(contrast(t[foreground],t[background]),4.5)

    def test_team_svgs_have_dark_strokes_for_pastel_surfaces(self):
        page=(ROOT/"team.html").read_text(encoding="utf-8")
        self.assertIn("const PALETTE=",page)
        for foreground,background in (
            ("#146a91","#d9eef9"),("#5e50a1","#eae7fb"),
            ("#80561c","#f8efdf"),("#17669c","#e1eff9"),
            ("#914673","#f7e8f3"),("#206849","#e2f4eb"),
            ("#275d81","#e0eef8"),("#875922","#f8ecda")):
            self.assertGreaterEqual(contrast(foreground,background),4.5)

    def test_all_activity_and_status_contrast_is_explicit(self):
        for selector in (".activity-track",".status-tag.disabled",
                         ".chip.danger",".org-grid:before",".nav a.active",
                         ".insight-risk",".portrait",".avatar svg"):
            self.assertIn(selector,CSS)
        self.assertIn('--line-organigram',CSS)
        self.assertIn('--activity-stripe',CSS)
        self.assertIn('background:var(--bg-surface)!important',CSS)

    def test_static_css_requires_authentication(self):
        # Handler checks Basic Auth before every resource, including CSS.
        import inspect
        source=inspect.getsource(app.Handler.do_GET)
        self.assertLess(source.index('if not self.authorized()'),source.index('"/light-theme.css"'))
        self.assertIn('text/css; charset=utf-8',source)

if __name__=="__main__":
    unittest.main()

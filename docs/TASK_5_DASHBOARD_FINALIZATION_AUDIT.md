# Task 5 - Phase 2 - Dashboard Navigation Finalization Audit

Stand: 2026-06-16

## Analysierte Dateien

- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `backend/app/routers/analytics.py` lesend, zur Einordnung der vorhandenen SPA-/Payload-Strategie

## Geaenderte Dateien

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

## Finale Navigation

Main Navigation in der linken Sidebar:

1. Overview
2. Analytics
3. Scans
4. Issues
5. Actions
6. Reports
7. Subscription
8. Settings

Footer Navigation:

1. Support
2. Documentation
3. Logout

`Support` nutzt weiter den vorhandenen `mailto:support@bcsentinel.com` Link. `Documentation` nutzt weiter `/docs`. `Logout` bleibt als sichtbarer Footer-Button vorbereitet; es wurde keine neue Auth- oder Logout-Logik gebaut.

## Routing-/View-Strategie

Das Dashboard bleibt eine Single Page App innerhalb von `analytics_embed.html`.

- Keine neuen Backend-Routen wurden eingefuehrt.
- Bestehende Analytics-Endpunkte bleiben kompatibel.
- Das Dashboard-JS nutzt weiterhin den bestehenden Payload von `GET /analytics/embed/data`.
- Der neue `Scans`-Tab verwendet die bereits geladenen `recent_scans`-Daten.
- Die aktive Navigation wird clientseitig ueber `switchTab()` markiert und zusaetzlich mit `aria-current` versehen.

## Placeholder-Seiten

Folgende Views haben professionelle Page-Intro-/Placeholder-Bereiche erhalten:

- Analytics: Hinweis auf spaetere tiefere Analysen.
- Scans: neue stabile Zielseite mit Scan-History-Tabelle aus vorhandenen Daten und Hinweis auf spaetere Filter/Status/Drilldown.
- Issues: Hinweis auf spaetere Detailansicht; bestehende Locked Region und Tabelle bleiben erhalten.
- Actions: Hinweis auf spaetere Business-Central-Link-Anbindung; bestehende Tabelle bleibt erhalten.
- Reports: Hinweis auf spaetere Export-/Share-Anbindung; bestehende Report Cards bleiben erhalten.
- Subscription: Hinweis, dass Billing unveraendert bleibt; bestehende Produkt- und Access-Daten bleiben erhalten.
- Settings: Read-only Connection Context mit Hinweis auf spaetere editierbare Settings/Diagnostics.

Overview blieb als bestehende Startseite erhalten.

## Bekannte Luecken fuer spaetere Phasen

- Overview muss in Phase 3 fachlich finalisiert werden.
- Scans braucht spaeter Filter, Status/Progress, Detailansicht und klares Free-vs-Monitoring-Verhalten.
- Issues braucht spaeter echte Detailseiten, Statusfelder, Issue-spezifische Detected-On-Daten und ggf. Record-Level-Daten.
- Actions braucht spaeter Open-in-Business-Central-Buttons mit Disabled-State bei fehlendem Link.
- Reports braucht spaeter konkrete Links auf vorhandene Executive-Report-Endpunkte und saubere Download/Share-Flows.
- Settings bleibt vorerst read-only; echte Connection-Status-Quelle und Logout-Verhalten sind weiterhin offen.
- Critical Severity ist nur UI-kompatibel vorbereitet (`.severity-critical`), aber nicht fachlich erzwungen.

## Risiken / bewusst nicht geaendert

- Keine Lizenzlogik geaendert.
- Keine Billing-/Stripe-Logik geaendert.
- Keine Free-Scan-Logik geaendert.
- Keine Monitoring-Logik geaendert.
- Keine Scan-API oder Scan-Sync-Logik geaendert.
- Keine BC Extension geaendert.
- Keine Daten geloescht.
- Keine neuen externen Frameworks oder Dependencies eingefuehrt.
- Keine Severity-Werte kuenstlich geaendert.
- Keine neuen Backend-Routen erzwungen.

## Verifikation

- Navigation enthaelt die geforderten acht Main-Eintraege.
- Sidebar-Footer enthaelt Support, Documentation und Logout.
- SPA-View-Umschaltung wurde auf den neuen `Scans`-Tab erweitert.
- Das Dashboard laedt weiterhin ueber den bestehenden Datenendpunkt.
- Scans-View erzeugt keine zusaetzlichen API-Aufrufe.
- Mobile Layout nutzt weiterhin das bestehende einspaltige Sidebar-Verhalten und ergaenzende responsive Regeln fuer Page-Intros.

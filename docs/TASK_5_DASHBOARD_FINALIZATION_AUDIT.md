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

## Phase 3 - Overview Finalization

Stand: 2026-06-17

### Analysierte Dateien

- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`
- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `backend/app/routers/analytics.py` lesend, zur Zuordnung der vorhandenen Payload-Felder

### Geaenderte Dateien

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

### Verwendete Datenquellen

Es wurden ausschliesslich bestehende Dashboard-/Analytics-Payloads verwendet:

- `kpis.health_score`
- `kpis.estimated_loss_eur`
- `kpis.potential_saving_eur`
- `kpis.total_records`
- `kpis.checks_run`
- `kpis.issues_count`
- `kpis.roi_eur`
- `score_trend`
- `loss_trend`
- `free_insights.active_issues_summary`
- `free_insights.module_distribution`
- `free_insights.records_by_module`
- `free_insights.top_findings`
- `top_findings`
- `issue_groups`
- `visibility.is_premium`
- `product_access.monitoring_active`
- `subtitle`, `scan_mode_label`, `last_updated`, `selected_scan_id`

### Neue / ueberarbeitete Overview-Komponenten

- Executive Hero mit Kontext-Chips fuer Company/Environment, Scan-Modus und letzten Scan-Zeitpunkt.
- Fuenf KPI-Karten: Health Score, Estimated Loss, Potential Savings, Total Records, Validation Checks.
- Health-Score-Gauge mit Score-Band-Label.
- Score Trend und Loss Trend als fester Overview-Bereich mit Empty State bei weniger als zwei Scans.
- Issue Distribution mit UI-kompatiblen Severity-Stufen Critical, High, Medium, Low.
- Module Distribution mit Issue Distribution und Records by Module aus bestehenden Payload-Feldern.
- Recent Issues Panel mit maximal fuenf Eintraegen.
- Business Impact Panel mit management-orientierter Zusammenfassung aus bestehenden Commercial-Feldern.
- Professionelle Empty States fuer fehlende Scan-, Trend-, Distribution-, Issue- und Business-Impact-Daten.

### Free/Premium/Monitoring-Verhalten

- Overview bleibt immer sichtbar.
- Free User sehen KPI- und Business-Value-Daten, soweit im Payload vorhanden.
- Free User sehen Recent Issues anonymisiert als locked/high-impact Eintraege; gesperrte Details bleiben geschuetzt.
- Premium User sehen echte Top-Findings im Recent-Issues-Panel, soweit vorhanden.
- Monitoring-Historie wird nicht erfunden: Trends zeigen erst ab mindestens zwei vorhandenen Datenpunkten eine Kurve.
- Bestehende Monitoring-Anzeige fuer Recent Scans bleibt an `product_access.monitoring_active` gebunden.

### Bekannte Luecken

- Overview nutzt weiter vorhandene Payload-Felder; keine neuen Detaildaten fuer Issue-Drilldown.
- Trend-Delta, Zeitraumfilter und Benchmarking sind noch nicht umgesetzt.
- Critical Severity ist nur UI-kompatibel vorbereitet; fachliche Critical-Werte kommen erst mit einem separaten Severity-Task.
- Business Impact bleibt eine Darstellung vorhandener Backend-Werte und baut keine neue Commercial-Logik.
- Browser-Visual-Check wurde nicht ausgefuehrt, weil kein laufender lokaler Dashboard-Server mit gueltigem Analytics-Embed-Token bereitstand.

### Bewusst nicht geaendert

- Keine Lizenzlogik.
- Keine Billing-/Stripe-Logik.
- Keine Free-Scan-Logik.
- Keine Monitoring-Logik.
- Keine Scan Engine.
- Keine Backend-Routen.
- Keine BC Extension.
- Keine neuen externen Dependencies.
- Keine Severity-Fachlogik.

### Verifikation

- `node --check backend/app/static/js/analytics-dashboard.js` erfolgreich.
- Statische Suche bestaetigt Overview, Health Score, Estimated Loss, Potential Savings, Total Records, Validation Checks, Score Trend, Loss Trend, Issue Distribution, Module Distribution, Recent Issues und Business Impact.
- Statische Suche nach `undefined` und `NaN`: Treffer liegen in defensiven JS-Pruefungen bzw. bestehender Preislogik, nicht als sichtbarer UI-Text.
- `git` ist in dieser PowerShell-Umgebung nicht im PATH; `git status --short` konnte nicht ausgefuehrt werden.

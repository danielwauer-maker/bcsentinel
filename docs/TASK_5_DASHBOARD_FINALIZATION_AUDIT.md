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

## Phase 4 - Issues Page Finalization

Stand: 2026-06-17

### Analysierte Dateien

- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`
- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `backend/app/routers/analytics.py` lesend, zur Zuordnung der vorhandenen Issue-Payload-Felder

### Geaenderte Dateien

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

### Verwendete Datenquellen

Es wurden ausschliesslich bestehende Dashboard-/Analytics-Payloads verwendet:

- `issues_page.locked`
- `issues_page.items`
- `top_findings`
- `free_insights.top_findings`
- `free_insights.active_issues_summary`
- `premium_preview_findings` als letzter Fallback fuer eine gesperrte Preview-Liste
- `kpis.issues_count`
- `visibility.is_premium`
- `pages.issues.locked`
- `last_updated`

### Issues-Normalisierung

Die Issues-Seite normalisiert vorhandene Issue-/Finding-Objekte clientseitig auf:

- `title`
- `group` / `module`
- `severity`
- `severity_label`
- `count`
- `impact_eur`
- `status`
- `detected_on`

Feld-Fallbacks werden nur fuer Darstellung genutzt. Es wurde keine Backend- oder BC-Severity-Logik geaendert. `Critical`, `High`, `Medium` und `Low` werden als UI-Buckets angezeigt; `Critical` bleibt 0, wenn der vorhandene Payload keine Critical-Werte liefert. Unbekannte Severity-Werte werden als `Unknown` dargestellt.

### Neue / ueberarbeitete Issues-Komponenten

- Issues Page Header mit Management-Subtitle, Gesamtzahl, letztem Scan-Zeitpunkt und Access-Status.
- Severity-KPI-Karten fuer Critical, High, Medium und Low.
- Professionelle Issues-Tabelle mit Spalten: Issue, Module, Severity, Affected Records, Estimated Loss, Status und Action.
- Empty State: `No issues detected in the latest scan.`
- Locked Row State fuer Free User mit `Premium issue details`, `Locked` fuer geschuetzte Zahlen und CTA `Unlock full issue details`.
- Premium-kompatible volle Issue-Liste aus bestehenden `issues_page.items` bzw. `top_findings`.
- Vorbereiteter, deaktivierter Detail-Button fuer Phase 5 ohne neue Backend-Route.

### Free/Premium/Monitoring-Verhalten

- Issues bleibt fuer Free User sichtbar.
- Free User sehen Severity-Verteilung, Module, Status-Kontext und gesperrte Werte, aber keine konkreten Issue-Titel, Affected-Record-Zahlen oder Estimated-Loss-Details in der Tabelle.
- Premium User sehen die vollstaendigen Issue-/Finding-Felder, soweit im bestehenden Payload vorhanden.
- Monitoring erzeugt keine zusaetzliche Logik; vorhandene Scan-/Zeitkontexte werden nur angezeigt.
- Bestehendes Produkt-Gating wird nur lesend ausgewertet.

### Bekannte Luecken

- Issue Detail ist noch nicht implementiert.
- Der Action-Button in der Issues-Tabelle ist absichtlich deaktiviert und fuer Phase 5 vorbereitet.
- Echter Issue-Status fehlt weiterhin im Backend-Payload; die UI nutzt den Default `Open`, wenn kein Status vorhanden ist.
- Issue-spezifisches Erkennungsdatum fehlt weiterhin; die Seite nutzt den vorhandenen Scan-Zeitpunkt.
- Record-Level-Daten, Owner, SLA, History und konkrete Recommendations bleiben Phase 5 bzw. spaeteren Backend-/BC-Tasks vorbehalten.

### Bewusst nicht geaendert

- Keine Lizenzlogik.
- Keine Billing-/Stripe-Logik.
- Keine Free-Scan-Logik.
- Keine Monitoring-Logik.
- Keine Scan Engine.
- Keine Backend-Routen.
- Keine BC Extension.
- Keine neuen externen Dependencies.
- Keine fachliche Severity-Logik.

### Verifikation

- `node --check backend/app/static/js/analytics-dashboard.js` erfolgreich.
- Statische Suche bestaetigt Issues, Critical, High, Medium, Low, Affected Records, Estimated Loss, Unlock full issue details und severity-critical.
- Statische Suche nach `undefined`, `null` und `NaN`: Treffer liegen in defensiven JS-Pruefungen, Initialwerten und bestehender Preis-/Billing-Darstellung, nicht als sichtbare UI-Texte.
- Browser-Visual-Check konnte nicht ausgefuehrt werden, weil `http://localhost:8000/health` in der lokalen Umgebung nicht erreichbar war.
- `git` ist in dieser PowerShell-Umgebung nicht im PATH; `git status --short` konnte nicht ausgefuehrt werden.

## Phase 5 - Issue Detail Page Finalization

Stand: 2026-06-17

### Analysierte Dateien

- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`
- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `backend/app/routers/analytics.py` lesend, zur Zuordnung vorhandener Issue-Detail-Felder

### Geaenderte Dateien

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

### Verwendete Datenquellen

Es wurden ausschliesslich bestehende Dashboard-/Analytics-Payloads verwendet:

- `issues_page.items`
- `top_findings`
- `free_insights.top_findings`
- `premium_preview_findings`
- `visibility.is_premium`
- `pages.issues.locked`
- `last_updated`
- vorhandene Issue-Felder wie `code`, `title`, `group`, `severity`, `severity_label`, `count`, `impact_eur`, `recommendation_preview`, `open_in_bc_url`

### Issue-Detail-Normalisierung

Die bestehende Phase-4-Normalisierung wurde fuer die Detailansicht erweitert:

- `id` / Issue Code
- `rawTitle` und sichtbarer `title`
- `group`
- `severity` und `severityLabel`
- `count`
- `impact`
- `potentialSaving`
- `status`
- `detectedOn`
- `description`
- `recommendation`
- `scoreImpact`
- `openInBcUrl`
- `locked`

Fehlende Werte erzeugen professionelle Empty States wie `Detailed description is available after the full analysis.`, `Score impact details will appear when available.` und `Recommendation will be generated after the full analysis.`

### Neue / ueberarbeitete Issue-Detail-Komponenten

- Clientseitige SPA-Detail-View `issue-detail-tab` ohne neue Backend-Route.
- Einstieg ueber `View Details` in der Issues-Tabelle.
- Back Navigation `Back to Issues` ohne Dashboard-Reload.
- Detail Header mit Issue Title, Module, Severity Badge, Status, Affected Records und Estimated Loss.
- Karten fuer Issue Information, Description, Business Impact, Score Impact und Recommendation.
- Deaktivierter Fallback-Button `Business Central link not available`, wenn kein vorhandener BC-Link geliefert wird.

### Free/Premium/Monitoring-Verhalten

- Free User koennen die Detailansicht oeffnen, sehen aber nur einen geschuetzten Detail-State.
- Free User sehen generische Titel und gesperrte Werte; sensible Details, Affected Records und Estimated Loss bleiben geschuetzt.
- Free Detail State enthaelt CTA `Unlock full issue details`, der clientseitig zur Subscription-Seite fuehrt.
- Premium User sehen vollstaendige Issue-Detail-Daten, soweit im bestehenden Payload vorhanden.
- Monitoring erzeugt keine neue Logik; vorhandener Scan-/Zeitkontext wird nur angezeigt.

### Open-in-BC-Verhalten

- Wenn `open_in_bc_url` oder kompatible vorhandene Link-Felder im Payload vorhanden sind und der Zugriff nicht locked ist, wird `Open in Business Central` als externer Link angezeigt.
- Wenn kein Link vorhanden ist oder der Zugriff locked ist, wird `Business Central link not available` deaktiviert angezeigt.
- Es wurde keine neue BC-Link-Logik, keine Backend-Deep-Link-Logik und keine BC Extension geaendert.

### Bekannte Luecken

- Es gibt weiterhin keine Record-Level-Details im Dashboard-Payload.
- Beschreibung, Score Impact und Recommendation bleiben Empty States, wenn der vorhandene Payload diese Felder nicht liefert.
- Issue-spezifisches Erkennungsdatum, Owner, SLA und History fehlen weiterhin.
- Die Detailansicht nutzt clientseitige Issue-Auswahl; eine stabile direkte URL auf ein Issue ist noch nicht umgesetzt.
- Critical Severity bleibt UI-kompatibel, aber fachlich nicht neu eingefuehrt.

### Bewusst nicht geaendert

- Keine Lizenzlogik.
- Keine Billing-/Stripe-Logik.
- Keine Free-Scan-Logik.
- Keine Monitoring-Logik.
- Keine Scan Engine.
- Keine Backend-Routen.
- Keine BC Extension.
- Keine neuen externen Dependencies.
- Keine fachliche Severity-Logik.

### Verifikation

- `node --check backend/app/static/js/analytics-dashboard.js` erfolgreich.
- Statische Suche bestaetigt Issue detail, Issue Information, Description, Business Impact, Score Impact, Recommendation, Open in Business Central, Back to Issues, Business Central link not available und Unlock full issue details.
- Statische Suche nach `undefined` und `NaN`: Treffer liegen in defensiven JS-Pruefungen bzw. bestehender Preislogik, nicht als sichtbare UI-Texte.
- Browser-Visual-Check konnte nicht ausgefuehrt werden, weil `http://localhost:8000/health` in der lokalen Umgebung nicht erreichbar war.
- `git` ist in dieser PowerShell-Umgebung nicht im PATH; `git status --short` konnte nicht ausgefuehrt werden.

## Phase 6 - Actions Page Finalization

Stand: 2026-06-17

### Analysierte Dateien

- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`
- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `backend/app/routers/analytics.py` lesend, zur Zuordnung vorhandener Actions-/Issue-Felder

### Geaenderte Dateien

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

### Verwendete Datenquellen

Es wurden ausschliesslich bestehende Dashboard-/Analytics-Payloads verwendet:

- `actions_page.locked`
- `actions_page.items`
- `issues_page.items`
- `top_findings`
- `free_insights.top_findings`
- `premium_preview_findings`
- `kpis.potential_saving_eur`
- `visibility.is_premium`
- `pages.actions.locked`
- `pages.issues.locked`
- vorhandene Felder wie `recommendation`, `recommendation_preview`, `action`, `suggested_action`, `open_in_bc_url`, `impact_eur`, `potential_saving_eur`, `severity`, `count`, `group`

### Actions-Normalisierung

Die Actions-Seite normalisiert vorhandene Actions und Issue-/Finding-Daten clientseitig auf:

- `action`
- `relatedIssue`
- `module`
- `priority`
- `priorityLabel`
- `effort`
- `potentialSaving`
- `status`
- `openInBcUrl`
- `locked`

Wenn `actions_page.items` bei freigeschaltetem Zugriff vorhanden ist, wird diese Quelle bevorzugt. Fehlen Actions oder ist der Zugriff locked, werden die bereits normalisierten Issues/Finding-Quellen verwendet. Fehlende konkrete Actions werden nur als UI-Text aus vorhandener Recommendation oder Issue-Titel abgeleitet; es wird keine neue Scan-Regel oder Backend-Businesslogik gebaut.

### Priority-/Effort-Ableitung

- Priority wird UI-seitig aus vorhandener Severity/Priority uebernommen: Critical, High, Medium, Low.
- Fehlt die Severity/Priority, wird `Medium` als defensiver UI-Fallback verwendet.
- Effort wird nur fuer die Anzeige abgeleitet, wenn kein Payload-Wert vorhanden ist:
  - Critical/High oder viele betroffene Datensaetze: `Medium`
  - Medium: `Low / Medium`
  - Low: `Low`
  - sonst: `Not estimated`
- Es werden keine Werte gespeichert und keine Backend-Logik geaendert.

### Neue / ueberarbeitete Actions-Komponenten

- Actions Page Header mit Subtitle `Prioritized actions to reduce data quality risk and business impact.`
- Header-Metadaten fuer Anzahl Actions, vorhandenes Einsparpotenzial und Access-Status.
- Summary Cards fuer Recommended Actions, High Priority, Potential Saving und Open Items.
- Actions-Tabelle mit Action, Related Issue, Module, Priority, Effort, Potential Saving, Status und Open in Business Central.
- Empty State: `No recommended actions are available for the latest scan.`
- Free/Locked Row State mit `Unlock to view exact action`, `Premium issue`, gesperrten Werten und CTA `Unlock recommended actions`.

### Free/Premium/Monitoring-Verhalten

- Actions bleibt fuer Free User sichtbar.
- Free User sehen Wert und generische Actions, aber keine geschuetzten konkreten Empfehlungen oder Open-in-BC-Aktionen.
- Premium User sehen konkrete Actions und Empfehlungen, soweit im bestehenden Payload vorhanden.
- Monitoring erzeugt keine neue Logik; vorhandener Scan-/Zeitkontext wird nur ueber bestehende Daten beruecksichtigt.

### Open-in-BC-Verhalten

- Wenn `open_in_bc_url` oder kompatible vorhandene Link-Felder im Payload vorhanden sind und der Zugriff nicht locked ist, wird `Open in BC` als externer Link angezeigt.
- Wenn kein Link vorhanden ist, wird `BC link unavailable` deaktiviert angezeigt.
- Wenn der Zugriff locked ist, wird der Button deaktiviert mit `Unlock actions` angezeigt.
- Es wurde keine neue BC-Link-Logik, keine Backend-Deep-Link-Logik und keine BC Extension geaendert.

### Bekannte Luecken

- Action Status ist weiterhin ein UI-Default `Open`, wenn kein Payload-Status vorhanden ist.
- Effort, Owner, Due Date, SLA und Workflow-Status sind nicht als echte Datenquelle vorhanden.
- Open-in-BC Links sind nur verfuegbar, wenn der bestehende Payload sie bereits liefert.
- Record-Level-Action-Details bleiben separaten Backend-/BC-Datenvertragsfragen vorbehalten.

### Bewusst nicht geaendert

- Keine Lizenzlogik.
- Keine Billing-/Stripe-Logik.
- Keine Free-Scan-Logik.
- Keine Monitoring-Logik.
- Keine Scan Engine.
- Keine Backend-Routen.
- Keine BC Extension.
- Keine neuen externen Dependencies.
- Keine fachliche Severity-/Priority-/Effort-Logik im Backend.

### Verifikation

- `node --check backend/app/static/js/analytics-dashboard.js` erfolgreich.
- Statische Suche bestaetigt Actions, Recommended Actions, High Priority, Potential Saving, Open Items, Related Issue, Priority, Effort, Open in BC, BC link unavailable und Unlock recommended actions.
- Statische Suche nach `undefined` und `NaN`: Treffer liegen in defensiven JS-Pruefungen bzw. bestehender Preislogik, nicht als sichtbare UI-Texte.
- Browser-Visual-Check konnte nicht ausgefuehrt werden, weil `http://localhost:8000/health` in der lokalen Umgebung nicht erreichbar war.
- `git` ist in dieser PowerShell-Umgebung nicht im PATH; `git status --short` konnte nicht ausgefuehrt werden.

## Phase 7 - Reports Page Finalization

Stand: 2026-06-17

### Analysierte Dateien

- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`
- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `backend/app/routers/analytics.py` lesend, zur Zuordnung von `reports_page`, `selected_scan_id`, Product Access und Monitoring-/History-Daten
- `backend/app/routers/reports.py` lesend, zur Bestaetigung vorhandener Executive-Report-Routen

### Geaenderte Dateien

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

### Verwendete Datenquellen

Es wurden ausschliesslich bestehende Dashboard-/Analytics-Payloads und bereits vorhandene Report-Routen verwendet:

- `reports_page.locked`
- `reports_page.items`
- `reports_page.links`, falls spaeter vorhanden
- `report_links`, falls spaeter vorhanden
- `executive_report_url`, `pdf_report_url`, `share_url`, falls spaeter vorhanden
- `selected_scan_id`
- `last_updated`
- `latest_scan_id` / `scan_id`, falls spaeter vorhanden
- `product_access.monitoring_active` / `product_access.can_use_monitoring`
- `recent_scans`, `score_trend`, `loss_trend`
- vorhandene Routen `/reports/executive/{scan_id}/html` und `/reports/executive/{scan_id}/pdf`

### Report-Card-Logik

- Die Reports Page zeigt sechs feste Report Cards: Executive Summary, Data Quality Report, Issue Detail Report, Business Impact Report, Action Plan Report und Trend Report.
- Executive Summary nutzt bei freigeschaltetem Report-Zugriff und vorhandenem `selected_scan_id` die bereits bestehenden HTML-/PDF-Endpunkte.
- Weitere Report Cards aktivieren nur dann Links, wenn der bestehende Payload explizite Links wie `report_links`, `html_url`, `open_url`, `url` oder `pdf_url` liefert.
- Fehlt ein Link, bleibt der Button deaktiviert und zeigt einen professionellen Disabled State wie `Available after scan`.
- Trend Report bleibt deaktiviert mit `Available with monitoring history`, solange kein Monitoring mit vorhandener Historie aus bestehenden Payload-Feldern ableitbar ist.
- Share Links werden nur gezaehlt, wenn vorhandene Link-Felder im Payload existieren. Es wird kein `share-link` POST ausgefuehrt.

### Free/Premium/Monitoring-Verhalten

- Free/Locked User sehen die Reports Page, Summary Cards und alle Report Cards.
- Free/Locked User sehen keine geschuetzten Report-Links; Buttons bleiben deaktiviert oder fuehren als CTA zur Subscription-Seite.
- Premium User sehen aktive Links nur dort, wo ein bestehender Link oder die vorhandene Executive-Report-Route eindeutig nutzbar ist.
- Fehlende Report-Typ-Endpunkte werden nicht simuliert.
- Monitoring erzeugt keine neue Logik. Der Trend Report wird nur ueber vorhandene Monitoring-/History-Daten sinnvoll freigegeben.

### Vorhandene Links / deaktivierte Links

- Vorhanden und verlinkt: Executive Summary HTML ueber `/reports/executive/{scan_id}/html`.
- Vorhanden und verlinkt: Executive Summary PDF ueber `/reports/executive/{scan_id}/pdf`.
- Vorhanden im Backend, aber bewusst nicht automatisch erzeugt: `/reports/executive/{scan_id}/share-link`, weil dies bestehende Share-Link-Logik per POST ausloesen wuerde.
- Deaktiviert, sofern kein Payload-Link existiert: Data Quality Report, Issue Detail Report, Business Impact Report, Action Plan Report und Trend Report.

### Bekannte Luecken

- Es gibt weiterhin keine eigene Report-Bibliothek im Dashboard-Payload.
- Fuer Data Quality, Issue Detail, Business Impact, Action Plan und Trend Reports sind keine eindeutigen bestehenden UI-Links im Payload vorhanden.
- Trend Report braucht echte Monitoring-Historie und einen konkreten Report-Link, bevor er aktiv geoeffnet werden kann.
- Letzter Report-Zeitpunkt bleibt `Not available`, solange kein Feld wie `latest_report_at` oder `last_report_at` geliefert wird.
- Share-Link-Anzahl bleibt 0, solange kein vorhandener Share-Link im Payload geliefert wird.

### Bewusst nicht geaendert

- Keine Report-Engine.
- Keine Share-Link-Logik.
- Keine Backend-Routen.
- Keine Lizenzlogik.
- Keine Billing-/Stripe-Logik.
- Keine Free-Scan-Logik.
- Keine Monitoring-Logik.
- Keine Scan Engine.
- Keine BC Extension.
- Keine neuen externen Dependencies.
- Keine fachliche Severity-Logik.

### Verifikation

- `node --check backend/app/static/js/analytics-dashboard.js` erfolgreich.
- Statische Suche bestaetigt Reports, Executive Summary, Data Quality Report, Issue Detail Report, Business Impact Report, Action Plan Report, Trend Report, Unlock reports, Available with monitoring history und Available after scan.
- Statische Suche nach `undefined` und `NaN`: Treffer liegen in defensiven JS-Pruefungen bzw. bestehender Preislogik, nicht als sichtbare UI-Texte.
- Browser-Visual-Check konnte nicht ausgefuehrt werden, weil `http://localhost:8000/health` in der lokalen Umgebung nicht erreichbar war.
- `git` ist in dieser PowerShell-Umgebung nicht im PATH; `git status --short` konnte nicht ausgefuehrt werden.

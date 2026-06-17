# Task 5 - Phase 1 - Dashboard Ist-Analyse / Gap Analysis

Stand: 2026-06-16

Scope dieser Phase: reine Analyse und Dokumentation. Es wurden keine Dashboard-UI-, Lizenz-, Billing-/Stripe-, Free-Scan- oder Monitoring-Logiken geaendert.

## 1. Analysierte Dateien

| Datei | Zweck | Relevanz fuer Task 5 |
| --- | --- | --- |
| `backend/app/templates/analytics_embed.html` | Eingebettetes Kundendashboard mit Sidebar, Tabs, KPI-Karten, Overview, Analytics, Issues, Actions, Reports, Subscription und Settings. | Primaere UI-Struktur fuer Task 5. `Scans` fehlt als eigener Menuepunkt/Tab; Scan-Historie liegt derzeit nur im Overview und nur fuer Monitoring sichtbar. |
| `backend/app/templates/executive_report.html` | HTML-Template fuer Executive Report und shared Report Rendering. | Relevant fuer Reports-Zielseite und Report-Datenmodell. Nutzt eigene Reportstruktur, nicht direkt das Dashboard-Tab. |
| `backend/app/templates/admin_tenants.html` | Admin-Uebersicht fuer Tenants, Pricing Matrix, Issue-Kosten, Billing, Monitoring und Scan-Credits. | Indirekt relevant: zeigt vorhandene Admin-Daten und Konfigurationen, aber nicht Teil des Kundendashboards. |
| `backend/app/templates/admin_tenant_detail.html` | Admin-Detailseite mit Product Access, Scan Credits, Access Windows, Monitoring, Recent Scans, Billing und Invoices. | Indirekt relevant fuer Verifikation der vorhandenen Datenbasis; nicht Teil der spaeteren linken Kundennavigation. |
| `backend/app/static/js/analytics-dashboard.js` | Client-seitiges Rendering, Tabwechsel, Fetch von Dashboard-Daten, Lock-Overlays, Billing-CTA, Trends, Tabellen und Produktkarten. | Primaere Dashboard-Logik. Nutzt aktuell vor allem `/analytics/embed/data`; Section-Endpunkte existieren, werden vom JS aber nicht genutzt. |
| `backend/app/static/css/dashboard.css` | Styling fuer Kundendashboard und Admin-Seiten. Enthaelt Layout, Sidebar, Panels, Lock-Overlay, Tabellen, Trends, Severity-Klassen. | Primaeres Dashboard-CSS. Critical-Severity-Klasse fuer Issues fehlt; `critical` existiert nur fuer Score/Hero. |
| `backend/app/routers/analytics.py` | Erzeugt Embed-Token, rendert Dashboard, baut Dashboard-Payload, stellt Section-Daten und Analytics-Billing-Endpunkte bereit. | Wichtigste Backend-Datenquelle fuer Dashboard. Enthalten: KPIs, Trends, Issues, Actions, Reports, Settings, Gating. |
| `backend/app/routers/reports.py` | Executive-Report-API, HTML/PDF-Rendering, Share-Link. | Relevant fuer Reports-Zielseite. Zugriff ist premium-/produktbasiert gegated. |
| `backend/app/routers/scans.py` | Deep/Data-Health-Score Scan Start, Sync, Reconcile, Status. | Nur lesend analysiert. Relevant fuer Scan-Datenbasis, Scan Credits und Monitoring-Status, aber nicht direkt vom Dashboard-JS konsumiert. |
| `backend/app/main.py` | App-Setup plus Legacy-/Basis-Endpunkte `/scan/quick`, `/scan/history/{tenant_id}`, `/scan/trend/{tenant_id}`. | Relevant, weil historische Scan- und Trend-Endpunkte existieren, das Embed-Dashboard aber eigene Payload-Erzeugung verwendet. |
| `backend/app/models.py` | SQLAlchemy-Modelle fuer Tenant, Scan, ScanIssueRecord, ScanRunStatus, Subscription, Product Purchases, Scan Credits, Entitlements. | Bestimmt verfuegbare Felder fuer Dashboard und Gaps bei Issue Detail / Actions. |
| `backend/app/services/product_license_service.py` | Product Access Snapshot, Scan Credits, Monitoring, Access Windows und Feature-Aufloesung. | Primaere Quelle fuer Free/Premium/Monitoring-Gating. |
| `backend/app/services/executive_report_service.py` | Baut Executive Report aus Scan und Issues. | Relevant fuer Reports. Critical Findings werden aktuell aus `severity == "high"` abgeleitet. |
| `backend/app/schemas/scan.py` | Scan-API-Schemas. | Zeigt aktuell generische `severity: str`, aber keine Critical-Enum-Spezifikation. |
| `backend/app/schemas/report.py` | Report-API-Schemas. | Zeigt Report-Felder fuer KPIs, Findings, Kategorien und Critical Findings. |

## 2. Bestehende Dashboard-Struktur

### Vorhandene Seiten / Tabs

| Ziel | Aktueller Stand |
| --- | --- |
| Overview | Vorhanden als Default-Tab. Enthaelt Hero, KPI-Karten, Module Scores, Issues by Module, optional Monitoring-Scan-Historie/Trends, Unlock-Panel und Findings-Panel. |
| Analytics | Vorhanden als Tab mit Score Trend und Estimated Loss Trend. Premium Lock vorhanden. |
| Scans | Fehlt als eigener Menuepunkt und Tab. Scan-Historie existiert nur im Overview unter `monitoring-overview-panels`. |
| Issues | Vorhanden als Tab mit voller Issue-Tabelle. Premium Lock vorhanden. |
| Issue Detail | Fehlt als eigene Seite/View. Es gibt keine Drilldown-Route im Dashboard und keine Record-Level-Daten im Payload. |
| Actions | Vorhanden als Tab mit Recommended Measures Tabelle. Premium Lock vorhanden, aber Actions sind aktuell aus Findings abgeleitet. |
| Reports | Vorhanden als Tab mit Report Cards. Premium Lock vorhanden, Buttons oeffnen aktuell keinen echten Report. |
| Subscription | Vorhanden als Tab mit Produktzugriff, Scan Credits, Access Windows, Preis-/Produktkarten und CTAs. |
| Settings | Vorhanden als Tab mit Tenant ID, Company, Language, Last Scan, Connection Status. |

### Vorhandene Menuepunkte

Aktuell links vorhanden:

- Overview
- Analytics
- Issues
- Actions
- Reports
- Subscription
- Settings

Fehlt fuer Zielstruktur:

- Scans

Footer ist bereits vorhanden:

- Support
- Documentation
- Logout

Hinweis: `Logout` hat im Template einen Button (`#logout-button`), aber im analysierten JS keine registrierte Funktion. Ob Logout ausserhalb des Dashboard-JS gehandhabt wird, ist unbekannt.

### Vorhandene Widgets, Tabellen, Karten/KPIs

Vorhandene KPI-Karten:

- Health Score
- Estimated Loss
- Potential Savings
- Total Records
- Checks
- Issues Found

Vorhandene Widgets:

- Hero mit Score-Band-Text
- Data Scores by BC module
- Issues by BC module
- Recent Scans, nur im Monitoring-Overview sichtbar
- Score Trend, nur im Monitoring-Overview und Analytics-Tab sichtbar
- Loss Trend, nur im Monitoring-Overview und Analytics-Tab sichtbar
- Paid Scan Access Unlock Panel
- Scan Preview / Premium Preview Findings
- Estimated Monitoring Pricing Preview
- Findings-Tabelle
- Product Access / Scan Credits / Access Windows / Pricing
- Report Cards
- Settings Grid

Vorhandene Tabellen:

- Recent Scans: Date, Type, Score, Issues, Headline
- Findings: Issue, Area, Severity, Count, Impact, Access
- Issues: Issue, Module, Severity, Affected Records, Estimated Loss, Status, Detected On
- Actions: Issue, Suggested Action, Priority, Potential Saving, Effort

## 3. Vorhandene Datenbasis

Legende:

- Status: `vorhanden`, `teilweise vorhanden`, `fehlt`, `simuliert moeglich`
- API: `API vorhanden`, `API fehlt`, `unbekannt`

| Punkt | Status | API | Quelle / Kommentar |
| --- | --- | --- | --- |
| Health Score | vorhanden | API vorhanden | `kpis.health_score` aus `Scan.data_score` via `/analytics/embed/data`; auch in `/scan/history/{tenant_id}` und Reports. |
| Estimated Loss | vorhanden | API vorhanden | `kpis.estimated_loss_eur` aus Scan/Commercials; normalisiert in Analytics und Reports. |
| Potential Savings | vorhanden | API vorhanden | `kpis.potential_saving_eur` aus Scan/Commercials. |
| Total Records | vorhanden | API vorhanden | `kpis.total_records` aus `Scan.total_records`; Profilfelder in `Scan`. |
| Validation Checks | vorhanden | API vorhanden | `kpis.checks_run` aus `Scan.checks_count`; Label im UI derzeit `Checks`. |
| Score Trend | vorhanden | API vorhanden | `score_trend` aus letzten Scans im Analytics-Payload; Legacy `/scan/trend/{tenant_id}` liefert nur letzten Delta. |
| Loss Trend | vorhanden | API vorhanden | `loss_trend` aus letzten Scans im Analytics-Payload. |
| Issue Distribution | teilweise vorhanden | API vorhanden | `free_insights.active_issues_summary` zaehlt Severity-Buckets, aber UI nutzt es aktuell nicht sichtbar. `critical` Bucket existiert, bleibt wegen Normalisierung praktisch 0. |
| Module Distribution | vorhanden | API vorhanden | `issue_groups` und `free_insights.module_distribution` aus ScanIssueRecord-Kategorien bzw. Code-Ableitung. |
| Recent Issues | teilweise vorhanden | API vorhanden | `top_findings`, `issues_page.items`, `premium_preview_findings`; keine separate "recent" Semantik, sondern sortiert nach Impact/Count. |
| Business Impact | teilweise vorhanden | API vorhanden | `business_impacts` im `free_insights`, Estimated Loss/Potential Saving in KPIs, Reports mit Financial Risks. UI zeigt `free_insights.business_impacts` aktuell nicht als eigenes Widget. |
| Scan History | teilweise vorhanden | API vorhanden | `recent_scans` im Analytics-Payload, aber eigener Scans-Tab fehlt. Sichtbarkeit im Overview ist aktuell an Monitoring gekoppelt. |
| Subscription/Product Access | vorhanden | API vorhanden | `product_access`, `subscription`, `tenant_pricing`, `product_pricing`; Quelle `build_product_access_snapshot`. |
| Issue Access | vorhanden | API vorhanden | `product_access.can_view_issues`, `issue_access_until`, `pages.issues.locked`; UI-Lock vorhanden. |
| Dashboard Access | teilweise vorhanden | API vorhanden | `product_access.can_view_dashboard`, `dashboard_access_until`; Dashboard selbst zeigt fuer Free weiterhin Overview/Unlock statt komplettem Dashboard-Gate. |
| Scan Credits | vorhanden | API vorhanden | `product_access.scan_credits_available`, `subscription-scan-credits`; Admin zeigt Credits ebenfalls. |
| Open-in-BC Links | teilweise vorhanden | API vorhanden | `top_findings[].open_in_bc_url` wird aus `bc_issue_launch_url` im Embed-Token + Issue Code gebaut. Fehlt der Token-Wert oder Mapping, bleibt URL leer. |
| Reports | teilweise vorhanden | API vorhanden | Report Cards im Payload; echte Executive Report APIs existieren (`/reports/executive/{scan_id}`, HTML/PDF/Share). Dashboard-Buttons verlinken aktuell nicht. |

### Simuliert / abgeleitet statt eigener Quelle

- Actions werden aus Findings abgeleitet (`actions_items`): `suggested_action` aus `recommendation_preview` oder Fallback, `priority` aus Severity, `potential_saving_eur` aus Impact, `effort` ist `None`/TBD.
- Issue Status ist im JS hart als `Open` gesetzt; kein Statusfeld im `ScanIssueRecord`.
- Detected On in Issues nutzt `data.last_updated`, nicht ein Issue-spezifisches Erkennungsdatum.
- Reports Cards sind statische Karten im Analytics-Payload; keine dynamisch gelesene Report-Bibliothek.
- Connection Status in Settings ist hart `connected`.
- Issue Detail / Record Details fehlen als Datenmodell im analysierten Backend.

## 4. Free/Premium/Monitoring-Zustand

### Free User aktuell

Free User sehen:

- Dashboard-Shell und Overview.
- Health Score, Estimated Loss, Potential Savings, Total Records, Checks, Issues Found.
- Module Scores und Issues by Module, soweit Scan-Daten vorhanden.
- Unlock-Panel mit Full-Analysis/Validation/Monitoring CTA.
- Premium Preview Findings aus Top-Findings, aber ohne volle Findings-Tabelle.
- Subscription-Seite mit Product Access, Scan Credits, Access Windows und Produktkarten.
- Settings-Seite.

Free User sehen nicht bzw. gesperrt:

- Analytics-Tab-Inhalte werden per `locked-region` ueberlagert.
- Issues, Actions, Reports sind ueber `pages.*.locked` / `*_page.locked` gesperrt.
- Findings-Panel im Overview ist versteckt, wenn `visibility.is_premium` false ist.
- Recent Scans / Trends im Overview sind zusaetzlich nur bei `monitoring_active` sichtbar.

### Premium sichtbar

Premium bedeutet im Analytics-Payload effektiv:

`is_premium = is_premium_actions_enabled(tenant_features) and product_access["can_view_issues"]`

Sichtbar/entsperrt:

- Findings-Tabelle im Overview.
- Analytics Trends.
- Issues-Tabelle.
- Actions-Tabelle.
- Reports Cards, sofern `can_view_reports`.
- Open-in-BC Links in Findings, falls `open_in_bc_url` vorhanden.
- Buy More Credits Button, wenn paid access aktiv, aber Monitoring nicht aktiv.

### Monitoring sinnvoll / nur bei Monitoring

Nur bei `product_access.monitoring_active` sichtbar:

- `monitoring-overview-panels`
- Recent Scans im Overview
- Score Trend im Overview
- Loss Trend im Overview
- Subscription Plan Label/CTA als Monitoring / Manage Subscription

Monitoring-spezifisch sinnvoll:

- Scans-Zielseite mit kompletter Historie
- Analytics mit Trend- und Delta-Analysen
- Trend Report
- Periodische Scan-Vergleiche und Monitoring-Health

### Gating vorhanden

Vorhanden in Backend:

- `build_product_access_snapshot`: `can_view_issues`, `can_view_actions`, `can_view_reports`, `can_view_record_details`, `can_use_monitoring`, `can_run_deep_scan`, `dashboard_access_until`, `issue_access_until`, `scan_credits_available`.
- `_dashboard_page_state`: Locks fuer analytics, issues, actions, reports.
- `/analytics/embed/{section}`: liefert fuer `issues`, `actions`, `reports` bei Lock HTTP 402.
- `/reports/executive/*`: prueft `can_view_executive_report`.
- Scan-Start/Sync in `scans.py`: Deep Scan benoetigt Scan Credit oder Monitoring; Data Health Score ist gesondert behandelt.

Vorhanden in UI:

- `locked-region` Overlay fuer Analytics, Issues, Actions, Reports.
- Findings-Panel und Monitoring-Panels werden ueber Klassen versteckt.
- Subscription CTAs wechseln je Produktstatus.

### Gating fehlt oder ist unvollstaendig

- Kein eigener `Scans`-Page-State im Backend-Payload.
- Kein eigener Scans-Tab im Frontend.
- `Dashboard Access` existiert im Product Snapshot, aber das Embed-Dashboard zeigt fuer Free User weiterhin Dashboard-Overview/Unlock. Das kann fachlich korrekt sein, muss aber fuer Phase 2 bewusst entschieden werden.
- `free_insights` werden vom UI kaum genutzt; Free-Ansicht und Premium-Preview sind dadurch nicht klar getrennt.
- Reports-Buttons haben kein Ziel und nutzen die vorhandenen `/reports/executive/*` APIs nicht.
- Issue Detail / Record Detail Gating existiert im Snapshot (`can_view_record_details`), aber keine entsprechende UI/API-Datenstruktur im Dashboard.
- Actions haben noch keine Open-in-BC-Spalte und kein Disabled-State bei fehlendem BC-Link.
- Logout-Button hat keine erkennbare JS-Handler-Logik im analysierten Dashboard-JS.

## 5. Soll-Struktur fuer Task 5

Finale Navigation links:

1. Overview
2. Analytics
3. Scans
4. Issues
5. Actions
6. Reports
7. Subscription
8. Settings

Footer:

- Support
- Documentation
- Logout

Abgleich:

- Overview: vorhanden
- Analytics: vorhanden
- Scans: fehlt
- Issues: vorhanden
- Actions: vorhanden
- Reports: vorhanden
- Subscription: vorhanden
- Settings: vorhanden
- Footer: vorhanden

## 6. Gap Analysis pro Zielseite

### Overview

- Existiert bereits: ja.
- Vorhandene Daten: Health Score, Estimated Loss, Potential Savings, Total Records, Checks, Issues Found, Module Scores, Issues by Module, Unlock Copy, Pricing Preview, Premium Preview, Findings bei Premium.
- Fehlende Daten: sichtbare Severity Distribution, sichtbare Business Impact Liste, klare Free-Insights-Sektion, ggf. separates Dashboard-Access-Gate.
- UI-Aufwand: mittel. Bestehende Komponenten koennen wiederverwendet werden.
- Risiko: mittel, wegen Free/Premium-Gating und bestehender Upsell-Logik.
- Empfehlung Phase 2: Overview konsolidieren, Free Insights explizit rendern, Premium-Findings separat lassen, keine Gating-Regeln aendern ohne Produktentscheidung.

### Analytics

- Existiert bereits: ja.
- Vorhandene Daten: Score Trend, Loss Trend.
- Fehlende Daten: Issue Distribution sichtbar, Module Distribution als Chart/Matrix, Trend-Delta/Kontext, Monitoring-Hinweise.
- UI-Aufwand: mittel.
- Risiko: mittel, weil Analytics aktuell premium-locked ist und Monitoring-Mehrwert klar abgegrenzt werden sollte.
- Empfehlung Phase 2: Analytics als Premium/Monitoring-Analyse ausbauen; vorhandene `score_trend`, `loss_trend`, `free_insights.module_distribution`, `active_issues_summary` nutzen.

### Scans

- Existiert bereits: nein.
- Vorhandene Daten: `recent_scans`, Pagination, `selected_scan_id`, Legacy `/scan/history/{tenant_id}`, Scan Status APIs in `scans.py`.
- Fehlende Daten: eigener Page-State/Gating fuer Scans; Scan Detail View; Status/Progress im Embed-Payload; Filter nach Scan-Typ/Zeitraum.
- UI-Aufwand: mittel.
- Risiko: mittel bis hoch, weil Scan-Historie derzeit im Overview nur bei Monitoring sichtbar ist und eine neue Seite die Produktregeln beruehren kann.
- Empfehlung Phase 2: Zuerst Scans-Tab aus vorhandener Recent-Scans-Tabelle extrahieren. Gating fachlich klaeren: Free evtl. nur letzter Data Health Score, Monitoring volle Historie.

### Issues

- Existiert bereits: ja.
- Vorhandene Daten: title, group/module, severity, count, impact, detected on aus Scan-Zeitpunkt, locked state.
- Fehlende Daten: echter Issue Status, Issue-spezifisches Erkennungsdatum, SLA/Owner, Record-Level-Details, Critical Severity.
- UI-Aufwand: mittel.
- Risiko: mittel, wegen Premium-/Record-Detail-Gating.
- Empfehlung Phase 2: Tabelle verbessern, Filter fuer Severity/Module vorbereiten, Status weiter als simuliert markieren oder Backend-Feld einfuehren in separatem Task.

### Issue Detail

- Existiert bereits: nein.
- Vorhandene Daten: Issue-Level aus `top_findings` / `issues_page.items`: code, title, group, severity, count, impact, recommendation_preview, open_in_bc_url.
- Fehlende Daten: Datensatzliste, Record IDs, Felder, Owner, Status, Historie, konkrete Fix-Schritte, stabile Route.
- UI-Aufwand: hoch.
- Risiko: hoch, weil Record-Level-Details Datenschutz, Gating und BC-Payload betreffen.
- Empfehlung Phase 2: Nur leichte Issue-Detail-Schublade/Seite fuer vorhandene Issue-Level-Felder planen; Record-Level-Details als separaten Backend/BC-Task behandeln.

### Actions

- Existiert bereits: ja.
- Vorhandene Daten: issue, suggested_action, priority, potential_saving_eur, effort.
- Fehlende Daten: echter Effort, Status, Owner, Due Date, Open-in-BC Link-Spalte, Disabled-State bei fehlendem Link.
- UI-Aufwand: mittel.
- Risiko: mittel, weil Actions aktuell nur aus Findings abgeleitet werden.
- Empfehlung Phase 2: Actions-Tabelle um Open-in-BC Action erweitern, `open_in_bc_url` wiederverwenden, Button deaktivieren wenn URL fehlt. Keine neue BC-Logik in Phase 2 ohne Datenvertrag.

### Reports

- Existiert bereits: ja.
- Vorhandene Daten: statische Report Cards, Executive Report APIs fuer JSON/HTML/PDF/Share.
- Fehlende Daten: Button-Ziele, Report-Typ-Mapping, Download/Share UI, Report-Verfuegbarkeit je Scan/Monitoring-Historie.
- UI-Aufwand: mittel.
- Risiko: mittel, wegen Report-Gating und Shared-Link-Sicherheit.
- Empfehlung Phase 2: Executive Summary Card mit `/reports/executive/{scan_id}/html` bzw. `/pdf` verbinden; weitere Report Cards erst als disabled/coming-later oder mit klarer API hinterlegen.

### Subscription

- Existiert bereits: ja.
- Vorhandene Daten: Product Access, Scan Credits, Dashboard Access Until, Issue Access Until, Monthly/Annual Price, Product Cards, Checkout/Portal CTAs.
- Fehlende Daten: optional Kauf-/Invoice-Historie im Kundendashboard; genaue Produktstatus je Card; Fehlerfeedback bei Billing-Action.
- UI-Aufwand: niedrig bis mittel.
- Risiko: hoch, weil Billing/Stripe nicht veraendert werden darf.
- Empfehlung Phase 2: Nur Anzeige/Lesbarkeit verbessern; Checkout/Portal-Logik unveraendert lassen.

### Settings

- Existiert bereits: ja.
- Vorhandene Daten: Tenant ID, Company, Language, Last Scan, Connection Status.
- Fehlende Daten: echte Connection-Status-Quelle, Environment Details aus Tenant/Token, Support/Docs-Kontext, Logout-Funktion.
- UI-Aufwand: niedrig.
- Risiko: niedrig bis mittel, falls Logout/Session-Verhalten angefasst wird.
- Empfehlung Phase 2: Settings zunaechst als Read-only Context belassen; echte Connection-Status-Quelle spaeter definieren.

## 7. Besondere Hinweise

- Actions sollen spaeter Open-in-Business-Central-Links verwenden, falls vorhanden.
- Wenn kein BC-Link vorhanden ist, soll der Button spaeter deaktiviert angezeigt werden.
- Open-in-BC Link-Basis kommt aktuell ueber `bc_issue_launch_url` im Analytics-Embed-Token. Ohne diesen Wert bleibt `open_in_bc_url` leer.
- Die Funktion `_build_open_in_bc_url` baut fuer bekannte Issue Codes direkte BC-Seiten/Filter und faellt sonst auf einen generischen Filter auf `Issue Drilldown Code` zurueck.
- Severity-Ziel im Dashboard: Critical, High, Medium, Low.
- Aktuell kennt die eigentliche Issue-Severity im Backend/BC-Payload nur High, Medium, Low. Analytics normalisiert unbekannte Werte auf `low`.
- `free_insights.active_issues_summary` hat zwar schon einen `critical` Bucket, dieser wird mit aktueller Normalisierung praktisch nicht befuellt.
- Executive Report nennt eine Sektion "Critical Findings", meint aktuell aber High-Severity Findings (`finding.severity == "high"`).
- In Phase 1 wurde nur dokumentiert, nicht geaendert.

## 8. API-Nutzung des aktuellen Dashboards

Direkt vom Dashboard-JS genutzt:

- `GET /analytics/embed/data`
- `POST /analytics/billing/checkout`
- `POST /analytics/billing/portal`

Im Backend vorhanden, aber vom aktuellen Dashboard-JS nicht direkt genutzt:

- `GET /analytics/get-token`
- `GET /analytics/embed`
- `GET /analytics/embed/{section}` fuer `issues`, `actions`, `reports`
- `GET /reports/executive/{scan_id}`
- `POST /reports/executive/{scan_id}/share-link`
- `GET /reports/executive/{scan_id}/html`
- `GET /reports/executive/{scan_id}/pdf`
- `GET /scan/history/{tenant_id}`
- `GET /scan/trend/{tenant_id}`
- `POST /scan/start`
- `POST /scan/sync`
- `GET /scan/status/latest`
- `GET /scan/status/{run_id}`

Unsicherheiten:

- Ob `Logout` ausserhalb von `analytics-dashboard.js` implementiert ist, wurde in den analysierten Dashboard-Dateien nicht gefunden.
- Ob BC aktuell in allen Kundeninstallationen `bc_issue_launch_url` mitsendet, ist aus dem Backend allein nicht sicher ableitbar.
- Ob Free User fachlich den kompletten Overview sehen sollen oder nur eine reduzierte Data-Health-Score-Ansicht, muss fuer Phase 2 produktseitig bestaetigt werden.
- Ob `Dashboard Access Until` den Zugriff auf das gesamte Dashboard oder nur die Premium-Details meint, ist im aktuellen UI nicht eindeutig.

## Phase 2 Implementation Notes

Datum: 2026-06-16

Umgesetzte Navigation:

- Die linke Sidebar enthaelt nun exakt: Overview, Analytics, Scans, Issues, Actions, Reports, Subscription, Settings.
- Der Sidebar-Footer enthaelt weiterhin: Support, Documentation, Logout.
- Das Dashboard bleibt eine clientseitig umgeschaltete Single Page App innerhalb von `analytics_embed.html`.

Geaenderte Dateien:

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

Offene Punkte fuer Phase 3:

- Overview fachlich und visuell finalisieren.
- Free Insights, Premium Preview und Premium Findings klarer trennen.
- Keine Lizenz-/Billing-/Stripe-/Scan-/Monitoring-Logik wurde in Phase 2 geaendert.
- Critical Severity wurde nur UI-kompatibel vorbereitet, nicht fachlich eingefuehrt.
- Reports, Actions, Issues Detail und Scans Detail bleiben spaeteren Phasen vorbehalten.

## Phase 3 Implementation Notes

Datum: 2026-06-17

Umgesetzte Overview-Elemente:

- Page Header / Executive Hero mit professionellem Subtitle und Kontext-Chips.
- KPI Cards fuer Health Score, Estimated Loss, Potential Savings, Total Records und Validation Checks.
- Score Trend und Loss Trend als fester Overview-Bereich mit Empty State bei fehlender Historie.
- Issue Distribution mit UI-kompatiblen Buckets Critical, High, Medium, Low.
- Module Distribution fuer Issue- und Record-Verteilung aus bestehenden Payload-Feldern.
- Recent Issues mit maximal fuenf Eintraegen; fuer Free User werden Details anonymisiert/locked dargestellt.
- Business Impact Panel aus vorhandenen Feldern `estimated_loss_eur`, `potential_saving_eur`, `roi_eur`, `issues_count` und `health_score`.
- Robuste Zahlen-/EUR-/Prozentformatierung mit Fallbacks gegen leere oder nicht numerische Werte.

Geaenderte Dateien:

- `backend/app/templates/analytics_embed.html`
- `backend/app/static/js/analytics-dashboard.js`
- `backend/app/static/css/dashboard.css`
- `docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`
- `docs/TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`

Offene Punkte fuer Phase 4:

- Issues Page finalisieren.
- Issue-Filter, Issue-Status und Issue-Detail-Verhalten definieren.
- Open-in-BC-Links erst auf Actions/Issue Detail anwenden, wenn vorhandene Link-Daten stabil sind.
- Critical Severity weiterhin nicht fachlich einfuehren; separater Task 6 bleibt empfohlen.
- Keine neuen Backend-Routen oder Produktlogiken wurden in Phase 3 eingefuehrt.

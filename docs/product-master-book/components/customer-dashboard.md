# Customer Dashboard

## Zusammenfassung
Serverseitiges Portal mit Einladung/Login/Tenantwechsel und eingebettetem Analytics-Single-Page-UI.

## Erkannte Verantwortlichkeiten
Overview, Analytics, Scans, Issues/Detail, Actions, Reports, Subscription und Settings; Free-/Produkt-/Monitoring-Gates.

## Erkannte Unterbereiche
`dashboard_portal.html`, `analytics_embed.html`, `analytics-dashboard.js`, `dashboard.css`, Dashboard-/Analytics-Router.

## Vorhandene Features
DASH-AUTH-001, DASH-TEN-001, DASH-OV-001, DASH-AN-001, DASH-GATE-001.

## Teilweise vorhandene Features
DASH-PREF-001: Settings/Notification-State ist teilweise UI-abgeleitet und ohne eigene persistierte Preference-Entität.

## Stubs oder statische Inhalte
Keine ganze Seite als Stub; Empty/Locked States sind im JS implementiert. Einzelne Hilfetexte/Links sind statisch.

## APIs und Schnittstellen
Dashboard-Sessionrouten, Analytics-Embed/Data, Billing-Checkout/Portal, Executive Reportlinks und BC-Drilldown-URL.

## Datenmodelle
`DashboardUser`, `DashboardUserTenantMembership`, Tenant/Scan/Entitlement-Daten.

## Tests
Multi-Tenant-, Membership-, Embed-Security-, Licensing- und Dashboard-Vertragstests.

## Dokumentation
`docs/TASK_5_DASHBOARD_GAP_ANALYSIS.md`, `TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`.

## Technische Auffälligkeiten
Embed-Token wird in ein Cookie überführt; serverseitige Payloads sperren Premiumbereiche zusätzlich zur UI.

## Manuell zu prüfen
Responsivität, Accessibility, Browser, reale Nutzerführung.

## Belegverzeichnis
`backend/app/routers/dashboard.py`; `analytics.py`; Templates/Static-Dateien.

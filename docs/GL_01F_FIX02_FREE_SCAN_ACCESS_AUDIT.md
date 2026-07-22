# GL-01F-FIX02 – Free Scan Access Entitlement Repair

## Analyse vor der Implementierung

### Root Cause

Der kostenlose Scan wird beim Start korrekt und atomar über `ScanStartRequest.free_scan_slot = data_health_score` sowie `resolved_product_code = data_health_score` gebunden. Nach erfolgreicher Synchronisierung liegt außerdem ein persistiertes Scanergebnis vor und `ScanRunStatus` wird mit `status = completed`, `result_persisted_at_utc` und `completed_at_utc` finalisiert.

Der Lizenz-Snapshot wertet diesen erfolgreichen Abschluss jedoch nicht als zeitlich begrenzten Zugriff aus:

- `build_product_access_snapshot()` setzt `free_dashboard` und `can_view_free_insights` allein aufgrund irgendeines vorhandenen `Scan`-Datensatzes.
- `dashboard_access_until`, `issue_access_until` und `report_access_until` werden ausschließlich aus `premium_access_until` befüllt.
- `can_view_dashboard`, `can_view_issues`, `can_view_issue_details`, `can_view_reports` und `can_view_executive_report` hängen ausschließlich an Premium-/Monitoring-Zugriff.
- Der autoritative Snapshot leitet seine drei Guards korrekt aus diesen Feldern ab und verweigert deshalb Dashboard, Findings und Report.

Die BC Extension ist nicht die Ursache. `DH API Client.RefreshLicenseStatus()` übernimmt alle drei Capabilities und Zeitfelder bereits korrekt. `DH Access Guard` prüft die getrennten Schlüssel `dashboard_access`, `issues_access` und `report_access` und erzwingt auf den drei Aktionen einen frischen Backend-Snapshot. Der Deep-Scan-Runner aktualisiert den Produktzugriff nach erfolgreicher Synchronisierung bereits automatisch.

### Flow-Matrix vor dem Fix

| Schritt | Backend-Feld | API-Feld | BC-Feld | Access Guard | aktueller Wert nach Free Scan | erwarteter Wert |
|---|---|---|---|---|---|---|
| Dashboard | `premium_access_until` / `can_view_dashboard` | `dashboard_access_until[_bc]`, `capabilities.dashboard_access` | `Dashboard Access Until`, `Can View Dashboard` | `EnsureDashboardAccess()` | `NULL` / `false` | `completed_at + 7 Tage` / `true` |
| Findings | `premium_access_until` / `can_view_issue_details` + `can_view_issues` | `issue_access_until[_bc]`, `capabilities.issues_access` | `Issue Access Until`, `Can View Issue Details` | `EnsureIssuesAccess()` | `NULL` / `false` | `completed_at + 7 Tage` / `true` |
| Report | `premium_access_until` / `can_view_executive_report` + `can_view_reports` | `report_access_until`, `capabilities.report_access.valid_until_utc` | `Report Access Until`, `Can View Reports` | `EnsureReportAccess()` | `NULL` / `false` | `completed_at + 7 Tage` / `true` |

Die bestehende Backend-Konstante `ONE_TIME_ACCESS_DAYS = 7` und die vorhandene UTC-Berechnung `calculate_access_window_until()` bilden die bereits etablierte siebentägige Zugriffslogik. Es wird keine neue Laufzeit eingeführt.

### Datenbankzustand des konkret betroffenen Tenants

Im Workspace ist keine produktive/staging Datenbank, keine `.env`-Konfiguration und kein laufender Docker-Datenbankdienst verfügbar. Daher können Tenant-ID, Company SystemId und reale Tabellenwerte des konkret gemeldeten Mandanten nicht verifiziert werden. Die im Sprintauftrag genannten leeren Access-Felder sind ein gemeldeter Ausgangszustand, kein lokal gemessener Datenbankbefund.

Der reproduzierbare Quelltext- und Testdatenbefund vor dem Fix lautet:

- erfolgreicher Free-Start: `Tenant.free_assessment_used = true`
- Free-Bindung: `ScanStartRequest.free_scan_slot = data_health_score`
- erfolgreicher Abschluss: `ScanRunStatus.status = completed`, `completed_at_utc` gesetzt
- Access-Felder im Snapshot: `dashboard_access_until = NULL`, `issue_access_until = NULL`, `report_access_until = NULL`
- Capabilities: `dashboard_access = false`, `issues_access = false`, `report_access = false`

### Bewertete Implementierungsvarianten

1. Neue persistierte Free-Access-Felder auf `Tenant`: unnötige Schemaänderung und Backfill-Migration.
2. Neues Entitlement beim Scanabschluss: zusätzliche persistierte Produktsemantik und komplexere Idempotenz-/Recovery-Behandlung.
3. Lazy-Berechnung aus dem bestehenden, dauerhaften Abschlussdatensatz: keine Migration, ursprünglicher Abschlussanker, idempotent und automatisch rückwirkend wirksam.

Entscheidung: Variante 3.

## Geplanter Ziel-Flow

1. Der bestehende Scanstart bindet den einmaligen Free Scan technisch an `ScanStartRequest`.
2. Nur `completed` oder `completed_with_warnings` mit persistiertem Ergebnis und `completed_at_utc` gilt als erfolgreicher Abschluss.
3. Der Snapshot berechnet `free_access_until = completed_at_utc + ONE_TIME_ACCESS_DAYS`.
4. Dashboard-, Findings- und Reportzugriff verwenden jeweils `max(free_access_until, premium_access_until)`.
5. Premium-, Monitoring-, Actions-, Record-Detail- und Full-Report-Merkmale bleiben ausschließlich am höherwertigen Produktzugriff.
6. Der autoritative Snapshot liefert die drei vorhandenen Capabilities; BC übernimmt sie über das vorhandene Mapping.
7. Wiederholte Snapshot-Aufrufe verwenden denselben Abschlusszeitpunkt und verlängern den Zeitraum nicht.

## Auswirkungen

- Keine Änderung an Scanregeln, Score, Findings-Erzeugung, Credits, Monitoring, Scheduler oder Registrierung.
- Keine neue Capability und keine Umgehung des Access Guards.
- Keine Datenbankmigration.
- Bereits betroffene Mandanten werden beim nächsten Lizenz-/Access-Refresh aus dem ursprünglichen Abschlusszeitpunkt repariert.
- Ein fehlgeschlagener, abgebrochener, abgelaufener oder nur gestarteter Scan erzeugt keinen Zugriff.

## Implementierung und Validierung

### Implementierter Completion- und Snapshot-Flow

- `product_license_service._completed_data_health_score_at()` löst den ursprünglichen erfolgreichen Abschluss über die bestehende Bindung `ScanStartRequest -> ScanRunStatus -> Scan` auf.
- Anerkannt werden ausschließlich `completed` und `completed_with_warnings` mit gesetztem `completed_at_utc` und `result_persisted_at_utc`.
- Die Bindung muss `resolved_product_code = data_health_score` und `free_scan_slot = data_health_score` besitzen. Ein beliebiger oder ungebundener Scan-Datensatz genügt nicht.
- `free_access_until` wird bei jeder Snapshot-Berechnung deterministisch als `completed_at_utc + ONE_TIME_ACCESS_DAYS` berechnet.
- Die drei fachlichen Zugriffsfenster sind `max(free_access_until, premium_access_until)`. Ein höherwertiger Paid-/Monitoring-Zeitraum wird daher weder überschrieben noch verkürzt.
- `dashboard_access`, `issues_access` und `report_access` werden während dieses Fensters gewährt. `product_access`, `monitoring_access`, `subscription_active`, Actions, Empfehlungen, Record-Details und die Full-Premium-Merkmale bleiben gesperrt, solange kein echtes Paid-/Monitoring-Entitlement besteht.
- Der Free-Dashboard-Payload bleibt `is_premium = false`. Findings und der bestehende Free Report sind erreichbar; Paid Actions bleiben serverseitig gesperrt.
- Full Analysis bleibt während des Free-Zeitraums weiterhin kaufbar.

### BC-Mapping und automatischer Refresh

Das bestehende Mapping übernimmt weiterhin:

| API | BC Setup |
|---|---|
| `dashboard_access_until_bc` / `dashboard_access_until` | `Dashboard Access Until` |
| `issue_access_until_bc` / `issue_access_until` | `Issue Access Until` |
| `capabilities.report_access.valid_until_utc` | `Report Access Until` |
| `capabilities.dashboard_access.granted` | `Can View Dashboard` |
| `capabilities.issues_access.granted` | `Can View Issue Details` |
| `capabilities.report_access.granted` | `Can View Reports` |

`DH Access Guard` prüft unverändert die drei getrennten Capabilities und erzwingt einen frischen, tenant-/company-gebundenen Snapshot.

Der erfolgreiche Data-Health-Score-Abschluss war zuvor ausdrücklich vom automatischen Lizenz-Refresh ausgenommen. `DH Deep Scan Runner` ruft `TryRefreshLicenseAfterCompletion()` jetzt nach jeder erfolgreichen Backend-Synchronisierung auf, einschließlich Free Scan. Failed/Cancelled/Sync-Failure-Pfade erreichen diesen Aufruf weiterhin nicht.

Da Free-Findings nun korrekt `Can View Issue Details` setzen, wurden zwei bestehende Premium-Ableitungen entkoppelt: BC zeigt Free-Zugriff nicht als Full Analysis/Paid Access an und blendet den Kauf von Full Analysis nicht fälschlich aus. Die Premium-Sichtbarkeit basiert weiterhin ausschließlich auf `product_access` beziehungsweise `Premium Enabled`.

### Reparatur bereits betroffener Tenants

Es gibt keine Backfill-Migration. Beim nächsten `/license/status`-Abruf wird ein vorhandener, erfolgreich persistierter Free-Abschluss lazy aus seinem ursprünglichen `completed_at_utc` ausgewertet. Die Berechnung schreibt den Anker nicht neu und ist daher idempotent. Ist `completed_at_utc + 7 Tage` bereits abgelaufen, bleibt der Zugriff gesperrt; der Deployment-Zeitpunkt spielt keine Rolle.

### Automatisierte Tests

Die neue Suite `test_gl01f_fix02_free_access.py` deckt die acht geforderten Gruppen ab:

1. erfolgreicher Free Scan und drei Access-Zeitfenster/Capabilities
2. Cancelled ohne Grant
3. Failed ohne Grant
4. Snapshot unmittelbar nach Abschluss
5. BC-Feldmapping, getrennte Guards und automatischer Refresh
6. abgelaufener Free-Zugriff
7. historische idempotente Lazy-Reparatur aus ursprünglichem Abschluss
8. Paid-/Monitoring-Abgrenzung und keine Verkürzung höherwertiger Zugriffe

Zusätzlich wurden bestehende Produkt-, Billing-, Admin- und AL-Vertragstests an den verbindlichen Free-Zustand angepasst.

Ergebnisse:

- FIX02 plus fokussierte Regression: 14 bestanden
- kombinierte Product Licensing/Billing/Fresh Access Regression: 114 bestanden
- vollständige Backend-Suite: 330 bestanden, 7 übersprungen, 0 fehlgeschlagen
- bestehende Warnungen: 89 Deprecation-Hinweise aus Starlette/Jose, keine FIX02-Fehler
- AL-Quelltext-Eindeutigkeit: 89 Objektdeklarationen, bestanden
- AL Compiler 17.0.34.45391: 85 Dateien, 0 Fehler, 0 Warnungen

### Migration

Nein. Es wurden weder Tabellen noch Felder, Beziehungen oder Alembic-Revisionen ergänzt.

### Manueller Restnachweis

Die produktive/staging Datenbank und eine BC-Sandbox waren im Workspace nicht erreichbar. Deshalb bleiben die reale Abfrage des konkret betroffenen Pilot-Tenants und die manuelle BC-Abnahme der zwölf Schritte aus dem Sprintauftrag offen. Dieser Restpunkt wird nicht durch Testdaten als durchgeführt dargestellt.

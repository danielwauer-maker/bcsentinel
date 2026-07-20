# GL-EXT-P0D – Fresh License Enforcement for Local Findings & Access Revocation

Stand: 20.07.2026  
Scope: ausschließlich P0-05 aus GL-EXT-AUDIT-01

## Ergebnis

P0-05 ist im Code behoben. Geschützte lokale Findings, Issue-Details, Drilldowns, Dashboardzugriffe und Executive Reports beruhen nicht mehr auf einem unbefristeten lokalen Boolean. Kritische AL-Zugriffe erzwingen einen authentifizierten HTTPS-Refresh; Backend-Endpunkte autorisieren unabhängig davon. Ein fehlender, alter, unvollständiger oder kontextfremder Snapshot gewährt keinen Zugriff.

Die lokale BC-Sandbox-Verifikation bleibt ein Release-Gate und ist nicht als bestanden markiert.

## Ausgangsrisiko und Root Cause

`DH Setup` speicherte positive Werte wie `Premium Enabled`, `Can View Dashboard` und `Can View Issue Details` ohne belastbare TTL, Serverzeit, Snapshot-Version oder Bindung an Environment, Company und API-URL. Finding-Pages und Drilldowns verwendeten diese Werte direkt. Gleichzeitig konnten Report-HTML/PDF und Report-Share-Links ohne aktive Report-Capability abgerufen werden; Analytics-Tokens wurden ohne Dashboard-Capability ausgegeben. Bereits ausgestellte Tokens wurden nicht erneut gegen Revocation geprüft.

## Kanonisches Capability-Modell

| Capability | Gewährt durch | Ende | Verwendung |
|---|---|---|---|
| `product_access` | aktiver Full Analysis-/Validation-Zeitraum oder Monitoring; Scan-Credit allein gewährt Detailzugriff nicht | serverseitiges Premium-/Monitoring-Ende, inklusiv | Produktstatus |
| `dashboard_access` | aktiver Detailzugriff | `dashboard_access_until`, inklusiv | Tokenausgabe und jeder Dashboardabruf |
| `issues_access` | `can_view_issues` und `can_view_issue_details` | `issue_access_until`, inklusiv | lokale Findings, Details, Recommendations und Drilldowns |
| `report_access` | `can_view_reports` und `can_view_executive_report` | `report_access_until`, inklusiv | JSON, HTML, PDF und Share-Link |
| `monitoring_access` | aktives Monitoring | Monitoring-Ende, inklusiv | Monitoring-Funktionen |
| `subscription_active` | aktive/trialing Monitoring-Subscription oder entsprechendes Entitlement | Monitoring-Ende, inklusiv | Subscriptionstatus |
| `scan_start_access` | freier noch nicht verbrauchter Health Score, Scan-Credit oder Monitoring | produktabhängig | Scanstart; nicht gleichbedeutend mit Detailzugriff |

Die Entscheidung verwendet UTC des Backends. Die bis-Zeit ist wie im bestehenden Produktmodell am exakten Zeitstempel inklusiv; danach ist die Capability inaktiv. Es gibt keinen Admin- oder Support-Bypass für SaaS-Produktzugriff. BC-Administratoren benötigen ebenso eine aktive Capability. Lokal gespeicherte Details bleiben erhalten, werden aber nicht angezeigt.

## Serverseitige Autorität

`GET /license/status` liefert zusätzlich:

- `snapshot_version = p0d-v1`
- `current_time_utc`
- `snapshot_expires_at_utc`
- `cache_ttl_seconds = 60`
- `correlation_id`
- Tenant-, Entra-, Environment-, Environment-Type-, Company-ID- und Company-Name-Kontext
- alle sieben Capabilities mit `granted`, `valid_from_utc`, `valid_until_utc`, `end_inclusive` und `reason_code`

Die Verbindung bleibt durch P0A authentifiziert und HTTPS-only. AL darf lokale Zeit nur zum Verwerfen eines maximal 60 Sekunden alten UI-Caches verwenden; jede kritische Freigabe erzwingt einen neuen Backend-Entscheid. Manipulierte lokale Werte können deshalb keinen Detailzugriff gewähren.

## Lokaler Snapshot und TTL

Neue company-spezifische Felder in `DH Setup`:

- Received-at, Serverzeit UTC und Expires-at
- Snapshot-Version, Tenant-ID, Environment, Environment-Type und Company-ID
- API-URL-Referenz und Correlation-ID
- Report-, Monitoring- und Subscription-Flags sowie Report-Ende

`DH API Client.RefreshLicenseStatus` invalidiert positive Flags, persistiert diese Invalidation und committet sie vor dem HTTP-Aufruf. Erst eine vollständige, authentifizierte Antwort mit gültiger Zeit, Kontext und allen Capabilities schreibt einen neuen Snapshot. Teilantworten und JSON-/Netzwerkfehler können daher keinen alten positiven Zustand konservieren. Ein API-URL-Wechsel invalidiert den Snapshot unmittelbar. Legacy-Snapshots haben keine Version/Received-at-Werte und sind automatisch ungültig.

## Fail-Closed-Vertrag

| Zustand | Ergebnis |
|---|---|
| frisch, Capability aktiv | Zugriff erlaubt |
| frisch, Capability inaktiv | blockiert |
| alt, Backend aktiv | Refresh; neue Serverentscheidung gilt |
| alt, Backend nicht erreichbar | blockiert |
| nie geladen oder Legacy-Snapshot | blockiert |
| Tenant/Environment/Company/API-URL abweichend | blockiert |
| lokale Uhr rückwärts/vorwärts manipuliert | kritischer Zugriff refreshes; Serverentscheidung gilt |
| serverseitig widerrufen | nächster geschützter Zugriff oder Tokenabruf blockiert |

Es gibt keine Grace Period. Fehlermeldungen sind in Englisch und Deutsch vorhanden.

## Zentraler AL Access Guard

Codeunit `DH Access Guard` kapselt:

- `EnsureIssuesAccess()`
- `EnsureDashboardAccess()`
- `EnsureReportAccess()`
- `EnsureMonitoringAccess()`
- `HasFreshCapability(...)`
- `RefreshAccessSnapshot()`
- `InvalidateAccessSnapshot()`

Direkte Page-ID, Bookmark und Suche treffen auf `OnOpenPage`-Guards. Die fünf lokalen Findings-/Issue-Pages und die FactBox prüfen zusätzlich beim Datensatzwechsel. Kritische Monitor-, History-, Setup-, Dashboard-, Report- und Drilldown-Actions prüfen unmittelbar vor Ausführung. Dispatcher und Drilldown-Management besitzen einen zweiten zentralen Guard, sodass ein Aufruf aus anderem AL-Code keine Umgehung schafft.

Geschützt sind insbesondere:

- Deep Scan Findings und Findings List
- Dashboard Issues und Dashboard Issues List
- Scan Issues und Issues FactBox
- Issue Drilldown Launch, Drilldown Management und Dispatcher
- Customer-/Vendor-/Item-/Sales-/Purchase-/Duplicate-Worklists
- Scan History → Issues
- Monitor → Issues, Analytics Dashboard, Executive HTML/PDF
- Setup/DHM Analytics → Dashboard

## Backend-Endpunkte

Unabhängige Checks bestehen für:

- `GET /analytics/get-token`
- `GET /analytics/embed`
- `GET /analytics/embed/data`
- `GET /analytics/embed/{issues|actions|reports}`
- `GET /reports/executive/{scan_id}`
- `POST /reports/executive/{scan_id}/share-link`
- authentifiziertes und geteiltes Executive HTML/PDF

Fehlende Authentifizierung ergibt 401. Fehlende Capability ergibt 403. 404 bleibt fehlenden Ressourcen vorbehalten. Die Capability wird vor Reportaufbau geprüft, um Metadatenlecks zu vermeiden.

## Token und Revocation

Dashboard-Tokens leben fünf Minuten; das Browser-Cookie bleibt maximal 15 Minuten, aber jeder Request prüft die aktuelle Dashboard-/Issues-/Report-Capability erneut. Report-Share-Tokens leben 15 Minuten und werden bei jedem Abruf erneut gegen Report-Capability geprüft. Revocation wirkt damit beim nächsten Request und nicht erst am Tokenende.

Beide Tokenarten enthalten Token-Type, Audience `bcsentinel-protected-content`, Issued-at, Expiry, Tenant, Company und Capability; Analytics zusätzlich Scope. Falsche Audience, Tokenart, Capability, Tenant, Company, Scan oder Reportart werden abgewiesen. Tokens werden weder lokal protokolliert noch in strukturierte Events geschrieben.

## Daten nach Ablauf

- Findings und Reports bleiben technisch gespeichert.
- Finding-Details, Recommendations, Drilldowns und Reportdateien sind gesperrt.
- Scan-History und Health-Score-Summaries dürfen entsprechend dem Produktmodell sichtbar bleiben.
- Bereits heruntergeladene PDFs können technisch nicht zurückgerufen werden.
- Reaktivierung oder Verlängerung wirkt nach dem nächsten Fresh Check ohne Datenwiederherstellung.

## Permissions

BC-Permission und SaaS-Capability sind kumulativ erforderlich. `BCSENTINEL VIEWER` besitzt keine direkten TableData-Leserechte mehr auf `DH Scan Issue`, `DH Deep Scan Finding` oder `DH Dashboard Issue`. Kontrollierte Pages erhalten indirektes Lesen und führen vorher den Guard aus. Scan/Admin behalten die für Scanerzeugung und Administration notwendigen RIMD-Rechte; die SaaS-Guards gelten trotzdem auf den geschützten Pages und Actions. Schedulerrechte wurden nicht erweitert. Exceptions bleiben außerhalb des P0D-Produktdetail-Scope.

## Migration

Keine Backend-Migration nach 0024 ist erforderlich. Die Änderung betrifft ausschließlich zusätzliche AL-Tabellenfelder und Response-/Tokenverträge. BC synchronisiert die neuen Felder beim Extension-Upgrade. Es gibt bewusst kein positives Backfill: fehlende Version oder Received-at bedeutet invalid. Legacy-Tenants ohne P0A-Identitätskontext müssen neu registriert bzw. ihren Kontext serverseitig vervollständigen; bis dahin bleibt Detailzugriff sicher gesperrt.

## Observability

Strukturierte Backend-Ereignisse enthalten Tenant-/Company-Referenz, Capability, Reason-Code, Snapshot-Alter, Serverzeit, Ablauf und Correlation-ID, ohne Kontakt-E-Mail oder Token:

- `access_snapshot_requested`, `access_snapshot_refreshed`, `access_snapshot_failed`
- `capability_granted`, `capability_denied`
- `protected_endpoint_blocked`, `token_issuance_denied`

`access_cache_expired`, `protected_page_blocked` und die explizite Klassifizierung `capability_revoked` sind im AL-/Admin-Telemetriepfad noch als P1-Observability-Härtung offen; die Security-Entscheidung selbst ist davon unabhängig.

## Automatisierte Tests

`backend/tests/test_p0d_fresh_access.py` enthält 51 Szenarien und deckt Capability-Verträge, aktiven/fehlenden Zugriff, TTL/Serverzeit/Correlation, 403-Verhalten, Tokenclaims, Revocation, direkte AL-Pages, Partial Responses und Viewer-Least-Privilege ab. Bestehende Licensing-, Analytics-, Report-, Tenant-Isolation- und Gesamttests werden zusätzlich als Regression ausgeführt. Eine AL-Test-App existiert weiterhin nicht; AL wird kompiliert und durch reproduzierbare Sandbox-CATs ergänzt.

## Sandbox-CATs – noch auszuführen

1. Aktive Findings über Liste, Card, FactBox, History und Dashboard-Drilldown öffnen.
2. Zugriff serverseitig ablaufen/widerrufen und dieselben Wege inklusive Bookmark/Page-ID wiederholen; Blockmeldung erwarten.
3. Backend vor Refresh stoppen; Details müssen fail closed bleiben.
4. BC-Uhr abweichend konfigurieren; Serverentscheidung muss gelten.
5. Geöffnete Seite über Ablauf halten; Recordwechsel, Refresh und Action müssen blockieren.
6. Dashboard und Report nach Ablauf öffnen; keine Token-/Dateiausgabe.
7. Company und Environment wechseln; alter Snapshot darf nicht gelten.
8. Zugriff reaktivieren; Fresh Check erlaubt Details erneut.
9. Benutzer ohne BCSentinel-Permission sowie Benutzer mit BC-Permission ohne SaaS-Zugriff prüfen.

## Bekannte Grenzen und Release-Gates

- Keine automatisierte AL-Test-App; Sandbox-CAT-Evidenz fehlt.
- PostgreSQL-/Docker-Verifikation hängt von lokal verfügbarer Runtime ab.
- Ausführlichere AL- und Admin-Revocation-Telemetrie ist P1, kein Autorisierungsblocker.
- Die bestehende AppSourceCop-Baseline und historische Localization-/Pricing-Gates werden im Abschlusslauf separat ausgewiesen.

## Rollback

Backend und Extension müssen gemeinsam zurückgerollt werden, weil die neue Extension vollständige Snapshot-Metadaten verlangt. Ein Backend-only-Rollback führt absichtlich zu fail-closed Detailzugriff. Ein Rollback darf die alten unbefristeten positiven Felder nicht wieder als Autorität aktivieren. Vor Rollback Tokenausgabe sperren, Extension/Backend auf den gleichen Release-Stand bringen und danach Registration sowie Fresh Snapshot prüfen.

## Finale Verifikation

| Prüfung | Ergebnis | Einordnung |
|---|---|---|
| P0D-Suite | 51/51 als Teil der Gesamtsuite | grün |
| Backend vollständig | **255/255**, 70 Deprecation-Warnungen, 573,88 s | grün; Warnungen P2 |
| Licensing | 35/35 als Teil der Gesamtsuite | grün |
| Analytics/Report fokussiert | 17/17 | grün |
| Python compileall | Exit 0 | grün |
| Migration fresh / 0023→0024 | Exit 0 / Exit 0 | grün; P0D benötigt keine 0025 |
| JSON/XLF Parse | bestanden | grün |
| AL ReleaseCloud | 82 Dateien, Exit 0 | grün |
| CodeCop + PerTenantExtensionCop | Exit 0; bestehende Warnings/Infos | kein Fehler |
| AppSourceCop | AS0051 EULA/Logo/Help, AS0084 ID-Range; AS0092 Warning | bekannte Baseline, Release-Gate offen |
| Localization Check | bekannte harte/mischsprachige AL-Texte | Baseline offen; keine neue P0D-Regelverletzung |
| Pricing Check | Assessment-Fallback-Baseline | außerhalb P0D offen |
| Docker/PostgreSQL | Docker-Client vorhanden; Engine/API und Config ACL nicht zugreifbar | NOT_EXECUTED |
| `git diff --check` | Exit 0 | grün |
| BC-Sandbox | keine Sandbox verfügbar | 15 CATs NOT_EXECUTED |

Die endgültige Neubewertung ist **64 % Code-/Release-Readiness**, **100 % funktionale P0-Schließung** und weiterhin **NO-GO** für Pilot/Kunde bis GL-EXT-P0E die Sandbox-, Upgrade- und übrigen P1-Gates schließt.

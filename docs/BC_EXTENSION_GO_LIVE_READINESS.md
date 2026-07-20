# BCSentinel Extension – Go-Live-Readiness-Audit GL-EXT-AUDIT-01

Stand: 16.07.2026  
Prüfgegenstand: `bc-extension` und die von ihr genutzten Backend-Endpunkte  
Historische Anforderungsquelle: *BCSentinel – Sprintplan – 09.07.2026*  
Entscheidung: **NO-GO**

## 1. Executive Summary

Die Lösung besitzt einen funktionsreichen AL-Client und ein in vielen Bereichen gut getestetes, tenantgebundenes Backend. Sie ist dennoch nicht bereit für Pilot-, Kunden- oder AppSource-Betrieb. Fünf P0-Risiken betreffen Transportverschlüsselung, Registrierung/Wiederherstellung, atomare Credit-Nutzung, fehlersichere Scan-Abwicklung und die lokale Durchsetzung abgelaufener Zugriffsrechte. Diese Risiken können zu Klartextübertragung eines API-Tokens, verlorener Kundenidentität beziehungsweise gekaufter Zugänge, mehrfacher Credit-Nutzung, dauerhaft hängenden Scans und unberechtigtem Zugriff auf lokal gespeicherte Findings führen.

Zusätzlich fehlen eine AL-Test-App, ein reproduzierbarer aktueller AL-/Analyzer-Build, Install-/Upgrade-Codeunits, ein Sandbox-Installationsnachweis, eine belastbare Scheduler-Berechtigungsrolle und eine vollständige Lokalisierungsbereinigung. Die vorhandene `.app`-Datei belegt nur einen früheren Compile, nicht die Qualität des aktuellen Quellstands.

**Gesamtbewertung: 48 %.** Ein Go-Live ist erst nach Schließung aller P0-Gaps, erfolgreichem AL-/Analyzer-Build und einem vollständigen Sandbox-CAT-Lauf neu zu bewerten.

## 2. Methode und Evidenzgrenzen

- Vollständige statische Rückverfolgung der geforderten AL- und Backend-Flows.
- Inventarisierung von Manifest, Objekten, Permission Sets, Migrationen und Tests.
- Backend-Gesamttest sowie gezielter Wiederholungslauf fehlerhafter Fälle.
- Prüfung von Python-Syntax, JSON/XLF-Struktur, Lokalisierungsregeln und Build-Workspace-Erzeugung.
- Keine visuelle DOCX-Prüfung; sie ist laut Auditauftrag nicht erforderlich.
- Kein Business-Central-Sandboxmandant und kein lokaler AL-Compiler vorhanden. AL-Laufzeitverhalten, Installation, Upgrade und Analyzer bleiben deshalb dort `NOT_VERIFIABLE`, wo statische Evidenz nicht ausreicht.
- Es wurde kein Produktcode verändert.

## 3. Inventar

| Artefakt | Befund |
|---|---|
| AL-Manifest | `bc-extension/app.json`, Version 1.0.2.6; `app.cloud.json` abweichend 1.0.2.5 |
| AL-Objekte | 11 Tabellen, 31 Pages, 6 Page Extensions, 22 Codeunits, 5 Enum-Dateien, 2 Queries, 1 Control Add-in |
| Permission Sets | `BCS VIEWER`, `BCS SCAN`, `BCS SETUP`, `BCS ADMIN` |
| Fehlende Objekttypen | keine Report-, Install-, Upgrade- oder Test-Codeunit; keine Role-Center-Erweiterung |
| AL-Test-App | nicht vorhanden |
| Backend | FastAPI, SQLAlchemy, Migrationen 0001–0021, 150 gesammelte Pytest-Fälle |
| Paketartefakt | vorhandene `.app` Version 1.0.2.6; kein Nachweis eines Builds aus dem auditierten Quellstand |

## 4. Prozentbewertung

| Dimension | Bewertung | Begründung |
|---|---:|---|
| Funktionale Vollständigkeit | 58 % | Kernflows vorhanden; Registrierung, Scans und Ausnahmen haben kritische Lücken |
| UX und Bedienbarkeit | 62 % | Setup und Seiten vorhanden; synchrone Scans, fehlendes Polling und fehlendes Role Center |
| Sprache und Lokalisierung | 55 % | deutsche XLF vollständig befüllt, aber Regelprüfung und Quelltextbereinigung fehlgeschlagen |
| Sicherheit und Datenschutz | 58 % | gutes Tenant-Binding im Backend; HTTP zulässig, Token-Recovery/Rotation und Retention unzureichend |
| Berechtigungen | 45 % | vier Rollen vorhanden; Basisdatenrechte, Scheduler-Identität und Least Privilege nicht belastbar |
| Installation | 50 % | Assisted Setup vorhanden; keine Install-Codeunit und kein Sandboxnachweis |
| Upgradefähigkeit | 25 % | Obsolete-Markierungen vorhanden; keine Upgrade-Codeunit oder Migrationstests |
| Performance und Resilienz | 50 % | Aggregatübertragung; synchrone Scans, fehlende Retries und Page-OnOpen-Modifikationen |
| Supportfähigkeit | 42 % | Status-/Fehlerfelder vorhanden; keine durchgängige Correlation-ID-/Repair-Strategie |
| AppSource-Basis | 35 % | Analyzer konfiguriert, aber nicht ausgeführt; Manifest- und Testlücken |
| **Gesamt** | **48 %** | gewichtete Auditbewertung; P0-Gates überschreiben den Prozentwert |

## 5. Vollständige Readiness-Matrix

Statuswerte: `COMPLETE`, `PARTIAL`, `MISSING`, `DEFECTIVE`, `NOT_VERIFIABLE`.

| ID | Bereich | Anforderung | aktueller Status | Evidenz im Code | getesteter Benutzerfluss | bestehende Risiken | erforderliche Maßnahme | Priorität | geschätzter Aufwand | Go-Live-Blocker Ja/Nein |
|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | Installation | Setup bei Installation initialisieren | MISSING | `DHSetup.Page.al` erzeugt Setup erst beim Öffnen; keine `Subtype = Install` | statische Prüfung | uninitialisierte Mandanten, uneinheitlicher Erststart | Install-Codeunit mit idempotenter Initialisierung und Test | P1 | 1–2 PT | Ja |
| R-02 | Setup | Geführte Einrichtung | PARTIAL | `DHGuidedExperience.Codeunit.al`, `DHSetup.Page.al` | statische Prüfung | technische Felder und Recovery nicht kundengerecht | Flow vereinfachen, Wiederaufnahme und Validierung testen | P1 | 2–3 PT | Ja |
| R-03 | Transport | ausschließlich HTTPS | DEFECTIVE | `DHSetup.Table.al:383–396` akzeptiert `http://` und `https://` | statische Prüfung | Tenant-ID und API-Token können im Klartext übertragen werden | Produktion auf HTTPS festnageln; Dev-Ausnahme explizit isolieren | P0 | 0,5–1 PT | Ja |
| R-04 | Registrierung | stabile, idempotente Tenant-/Company-Registrierung | DEFECTIVE | `DHApiClient.Codeunit.al:135–163`; `backend/app/main.py:361` erzeugt zufällige Tenant-ID | Backend-Registrierungstests | Re-Registrierung erzeugt neue Identität; Käufe und Historie können verwaisen | stabile BC-Tenant-/Environment-/Company-ID, idempotentes Upsert, Recovery | P0 | 4–7 PT | Ja |
| R-05 | Registrierung | korrekte App-Version melden | DEFECTIVE | AL sendet hartkodiert `0.4.0`, Manifest ist 1.0.2.6 | statische Prüfung | falsche Support-/Kompatibilitätsdaten | Manifestversion zentral aus Buildinformation bereitstellen | P1 | 0,5 PT | Nein |
| R-06 | Portal | Portal-Einladung und Zugang wiederherstellen | PARTIAL | Backend erzeugt gehashte 7-Tage-Einladung; AL hat keinen Resend/Repair-Flow | Registrierungstests | SMTP-Fehler oder Ablauf erfordern Admin-Eingriff | kundenfähige Resend-/Status-/Recovery-Aktion | P1 | 2–3 PT | Ja |
| R-07 | Dashboard | mandantengebundener Kurzzeitzugang | COMPLETE | `DHApiClient.Codeunit.al:1029`; `analytics.py:1509–1788`; Secure/HttpOnly Cookie nach 303 | Embed-Security-Tests bestanden | Token steht beim ersten Aufruf kurz in URL/Logs | Tokenübergabe weiter härten und Logs redigieren | P2 | 1–2 PT | Nein |
| R-08 | Dashboard | Company-/Environment-Kontext | PARTIAL | Query enthält Company, `BC Cloud`, Tenant und Sprache | Embed-Security-Tests | Environment ist hartkodiert; keine Plattformidentität | tatsächlichen Environment-/Tenant-Kontext verwenden | P1 | 2 PT | Ja |
| R-09 | Lizenz | zentraler Access-Snapshot | COMPLETE | `product_license_service.py:360`; AL `RefreshLicenseStatus` | Lizenztests überwiegend bestanden | Datumswerte in AL als Text | DateTime-Felder und Ablaufgrenzen typisieren | P2 | 2–3 PT | Nein |
| R-10 | Lizenz | lokale Rechte nach Ablauf sofort sperren | DEFECTIVE | mehrere Pages und `DHIssueDrilldownMgt.Codeunit.al:38` prüfen stale `Premium Enabled`; Auto-Refresh deaktiviert | statische Prüfung | lokal gespeicherte Premium-Findings bleiben nach Ablauf sichtbar | vor jeder sensitiven Aktion Snapshot aktualisieren und `Can View Issue Details` erzwingen | P0 | 2–4 PT | Ja |
| R-11 | Credits | genau-einmalige, atomare Credit-Nutzung | DEFECTIVE | `product_license_service.py:575–596` liest und ändert ohne Row-Lock/Unique-Constraint | normale Credit-Tests bestanden; kein Paralleltest | parallele Scan-IDs können denselben Credit nutzen | DB-Constraint/Lock/atomisches Update plus Concurrency-Test | P0 | 3–5 PT | Ja |
| R-12 | Manuelle Scans | retry-sicherer Start | DEFECTIVE | AL commit vor `/scan/start`, Retry erzeugt neue Run-ID | statische Sequenzprüfung | Antwortverlust kann weiteren Credit verbrauchen | lokale Run-ID wiederverwenden, Resume-/Idempotency-Key, Recovery | P0 | 3–5 PT | Ja |
| R-13 | Scan-Ausführung | Fehler beendet Run deterministisch | DEFECTIVE | `DHDeepScanRunner.Run` direkt aufgerufen; `DH Deep Scan Failure` nicht verdrahtet | statische Call-Graph-Prüfung | Run bleibt `Running`, Credit ist verbraucht | TryFunction/Fehlergrenze, terminaler Failed-Status und Repair-Job | P0 | 3–5 PT | Ja |
| R-14 | Scan-Ausführung | asynchroner, beobachtbarer Scan | DEFECTIVE | `QueueDeepScanInBackground` ruft ebenfalls synchron Runner auf; Refresh-Task nicht enqueued | statische Prüfung | Client-/Task-Timeout, schlechte UX, kein Live-Fortschritt | echte Job-Queue-Ausführung und Polling | P1 | 4–7 PT | Ja |
| R-15 | Scan-Ausführung | Cancel/Partial Success | MISSING | keine belastbare Abbruch- oder Partial-State-Implementierung | statische Prüfung | Bediener kann lange/teilweise Scans nicht sauber beenden | Zustandsautomat und Abbruchsemantik | P2 | 3–5 PT | Nein |
| R-16 | Scheduler | tägliche/wöchentliche/monatliche Planung | PARTIAL | `DHScanSchedulerMgt.Codeunit.al`, `TaskScheduler.CreateTask` | statische Prüfung | DST/Zeitzone, verwaiste Tasks, keine Runtime-Evidenz | AL-Tests und Sandbox-DST-/Replan-Tests | P1 | 3–5 PT | Ja |
| R-17 | Job Queue | Ausführung mit minimalen Rechten | NOT_VERIFIABLE | Task läuft im Company-Kontext des Erstellers; keine Service-Rolle/Basisdatenrechte | keine BC-Runtime | Scan kann bei normalen Rollen an Standardtabellenrechten scheitern | Service-Permission-Set, dokumentierter Ausführer, Sandboxtest ohne SUPER | P1 | 3–5 PT | Ja |
| R-18 | Scan-Historie | Runs, Status, Score und Findings | PARTIAL | `DHDeepScanRuns.Page.al`, Header/Run/Issue-Tabellen | statische Prüfung | kein Partial-State; Altbestände ohne Migration | Statusmodell und Migrations-/Retention-Test | P2 | 2–3 PT | Nein |
| R-19 | Historie/Performance | Read-only-Seiten bleiben read-only | DEFECTIVE | mehrere `EnsureSortFields()` modifizieren Datensätze beim Öffnen | statische Prüfung | Viewer kann Permission-Fehler erhalten; unnötige Writes bei jedem Öffnen | Sortwerte beim Schreiben/Migration berechnen | P1 | 2–3 PT | Ja |
| R-20 | Currency | Werte korrekt in LCY anzeigen | DEFECTIVE | `DHCurrencyMgt` hängt LCY an; Datenfelder/Payload bleiben EUR, keine Umrechnung | statische Prüfung | EUR-Betrag wird als USD/GBP etc. falsch etikettiert | Währungssemantik festlegen: konvertieren oder ausdrücklich EUR anzeigen | P1 | 3–5 PT | Ja |
| R-21 | Findings | Detailzugriff server- und clientseitig schützen | DEFECTIVE | Backend schützt; AL nutzt stale `Premium Enabled`; Viewer hat Read auf Findings | Security-Backendtests; statische AL-Prüfung | Premium-Inhalt lokal unberechtigt sichtbar | Datenminimierung oder verschlüsselte/geschützte Ablage und frische Access-Prüfung | P0 | 3–5 PT | Ja |
| R-22 | Ausnahmen | begründete, nachvollziehbare Ausnahme | PARTIAL | Exception-Tabelle/-Pages/-FactBoxes; Gründe teilweise hartkodiert, nicht Pflicht | statische Prüfung | unbegründete Ausnahmen, irreführende Reactivate-Aktion | Pflichtgrund, Auditfelder, klare Include/Exclude-Aktionen und Tests | P1 | 2–4 PT | Ja |
| R-23 | Executive Report | tenantgebundener HTML-/PDF-Share-Link | COMPLETE | `reports.py:53–175`, Typ/Scan/Tenant/TTL gebunden | Executive-Report-Tests bestanden | Token in URL; Währungs-/Sprachkonsistenz offen | URL-Token minimieren, CAT in Sandbox | P2 | 1–2 PT | Nein |
| R-24 | Secrets | API-Token nicht in normaler Tabelle | COMPLETE | `DHSecretMgt.Codeunit.al` nutzt `IsolatedStorage`, Company Scope; Backend hasht API-Token | Backend-Auth-Tests | keine Rotation/Self-Service-Recovery; fixer Storage-Key | Rotation, Revocation und Recovery ergänzen | P1 | 3–5 PT | Ja |
| R-25 | Permissions | differenzierte Rollen und Least Privilege | PARTIAL | vier Permission Sets in `BCSentinelPermissionSets.al` | statische Prüfung | Scan-Rolle hat breite RIMD-Rechte; Standardtabellenrechte fehlen | Objekt-/Basisrechte minimieren, negative Sandboxtests | P1 | 3–5 PT | Ja |
| R-26 | Upgrade | Schema-/Datenupgrade ohne Verlust | MISSING | keine `Subtype = Upgrade`; nur Obsolete-Felder | statische Prüfung | künftige Updates können Setup/Secrets/History beschädigen | Upgrade-Codeunit, Version-Tags, N-1-Testmatrix | P1 | 4–6 PT | Ja |
| R-27 | Localization | EN/DE vollständig und quelltextsauber | DEFECTIVE | 1.021 XLF-Units mit Targets; `check_al_localization.py` schlägt fehl | Strukturprüfung; Regeltest fehlgeschlagen | Mischsprache, Mojibake, hartkodierte Texte | Labels/XLF konsolidieren, Encoding reparieren, Test grün | P1 | 3–5 PT | Ja |
| R-28 | Manifest | produktionsreife AppSource-Metadaten | PARTIAL | gehärtete Resource Exposure; placeholderartige ID, fehlende EULA/Logo/Locales/Target, Versionsdrift | JSON parse bestanden | Einreichung/Support nicht reproduzierbar | endgültige IDs/Publisher/Version, Metadaten und Paketsignierung | P1 | 2–3 PT | Ja |
| R-29 | Build | aktueller AL-Build und Analyzer grün | NOT_VERIFIABLE | Workspace-Erzeugung erfolgreich; kein `alc.exe`; vorhandenes Paket ohne Buildprovenienz | Buildvorbereitung bestanden | Quellstand kann Compile-/Analyzerfehler enthalten | CI mit AL-Go/Compiler und CodeCop/AppSourceCop/PTECop | P1 | 2–4 PT | Ja |
| R-30 | Tests | automatisierte AL-Regression | MISSING | keine Test-App, keine `Subtype = Test` | Inventarprüfung | zentrale BC-Flows ohne automatischen Schutz | AL-Test-App für Setup, Lizenz, Scans, Scheduler, Currency, Permissions, Upgrade | P1 | 7–12 PT | Ja |
| R-31 | Backend-Tests | Backendregression grün | PARTIAL | 143 bestanden, 2 reproduzierbar fehlgeschlagen, 5 Setup-Fehler im Rerun bestanden | Pytest komplett plus Rerun | Grant-Vertrag inkonsistent; Lokalisierungstest veraltet | Erwartung/Vertrag entscheiden und Suite vollständig grün machen | P1 | 1–2 PT | Ja |
| R-32 | Retention/Support | definierte Löschung, Retry und Correlation | PARTIAL | explizites Delete/Reconcile; Backend Request-ID; AL zeigt sie nicht konsistent | statische Prüfung | keine automatische Retention; generische Fehler; keine Backoff-Strategie | Retention-Policy technisch erzwingen, Request-ID/Retry-After durchreichen | P1 | 3–5 PT | Ja |
| R-33 | Role Center | auffindbarer Einstieg und Cues | MISSING | keine Role-Center-Extension | Inventarprüfung | geringe Auffindbarkeit/Adoption | Role-Center-Cues und Setup-/Scan-Aktionen | P2 | 2–3 PT | Nein |
| R-34 | Produktvertrag | Assessment-Preis-/Credit-Fallback konsistent | DEFECTIVE | `check_pricing_consistency.py` meldet fehlenden/abweichenden Assessment-Fallback in `pricing-snapshot.js` | Repositorycheck fehlgeschlagen; Admin-Grant-Test ebenfalls rot | UI, Admin-Grant und Lizenzsnapshot können unterschiedliche Leistung versprechen | Assessment-Vertrag festlegen und alle Quellen/Tests angleichen | P1 | 1–2 PT | Ja |

## 6. Bewertung der historischen Sprints EXT-01 bis EXT-08

| Sprint | Codebasierte Bewertung | Status | Begründung |
|---|---|---|---|
| EXT-01 Registrierung und Portalzugang | Flow vorhanden, aber nicht idempotent, ohne stabile Plattformidentität und ohne kundenfähigen Recovery-/Resend-Weg | DEFECTIVE | P0 R-04; P1 R-06 |
| EXT-02 Lizenz, Access Snapshot und Credits | Backend-Snapshot stark; lokale Ablaufprüfung und atomare Credit-Nutzung fehlerhaft | DEFECTIVE | P0 R-10/R-11; reproduzierbare Grant-Testabweichung |
| EXT-03 Lokalisierung EN/DE | XLF vollständig befüllt; harte/mischsprachige Texte, Encodingfehler und fehlgeschlagener Checker | PARTIAL | R-27 |
| EXT-04 Scan-Historie | Historie und Drilldowns vorhanden; kein Partial-State, Migration/Retention offen, Page-OnOpen-Writes | PARTIAL | R-18/R-19 |
| EXT-05 Currency Formatting | LCY-Labeling vorhanden, aber EUR-Werte werden nicht umgerechnet | DEFECTIVE | R-20 |
| EXT-06 Ausnahmen | lokale Ausnahmeobjekte und Integrationen vorhanden; Begründung/Audit/Reaktivierung unvollständig | PARTIAL | R-22 |
| EXT-07 Role Center | keine Extension oder Cues vorhanden | MISSING | R-33 |
| EXT-08 Executive Report | tenant-, scan- und typgebundene Kurzzeitlinks; HTML/PDF backendseitig getestet | COMPLETE | R-23; kleinere Token-/Locale-Risiken bleiben |

## 7. Test- und Build-Ergebnisse

| Prüfung | Ergebnis | Einordnung |
|---|---|---|
| `python -m compileall -q app tests` | bestanden | Python-Quellen syntaktisch importierbar |
| JSON- und XLF-Parsing | bestanden | Manifeste/Übersetzungsdateien strukturell gültig |
| `scripts/New-BCBuildWorkspace.ps1 -Profile ReleaseCloud` | bestanden | reproduzierbarer Build-Workspace erzeugt |
| aktueller AL-Compile | nicht ausführbar | `alc.exe`/AL-Compiler lokal nicht vorhanden; kein Blocker für die Dokumenterstellung, aber Release-Gate offen |
| CodeCop/AppSourceCop/PTECop | nicht ausführbar | Analyzer in Settings aktiviert, aber kein aktueller Lauf möglich |
| `scripts/check_al_localization.py` | fehlgeschlagen | zahlreiche harte/mischsprachige Strings und Encodingbefunde |
| `scripts/check_pricing_consistency.py` | fehlgeschlagen | Assessment-Fallback in `pricing-snapshot.js` fehlt oder weicht ab |
| Backend `pytest -q` | **143 bestanden, 2 fehlgeschlagen, 5 Setup-Errors** | Gesamtzeit 218,42 s; Setup-Errors Windows-Temp-bezogen |
| gezielter Rerun mit Workspace-Temp | **5 bestanden, 2 fehlgeschlagen** | Infrastrukturfehler aufgelöst; zwei Abweichungen reproduzierbar |

Die zwei reproduzierbaren Abweichungen:

1. `test_admin_product_management_grant_and_revoke_product`: erwartete 0, tatsächlich 1 verfügbarer Scan-Credit nach Grant von `assessment`. Produktvertrag und Test sind inkonsistent.
2. `test_analytics_payload_uses_tenant_language`: Produkt liefert korrektes `Überblick`, Test erwartet veraltetes `Ueberblick`. Das ist ein Testwartungsfehler, kein sprachlicher Produktfehler.

Warnungen: 61 im Gesamtlauf, insbesondere Starlette-`TemplateResponse`- und `datetime.utcnow()`-Deprecations. Sie sind nicht unmittelbar blockierend, gehören aber vor Framework-Upgrades bereinigt.

## 8. P0- bis P3-Übersicht

### P0 – vor jeder Pilotnutzung schließen

- P0-01: `http://` als API-Basis-URL verhindern.
- P0-02: Registrierung idempotent an stabile BC-Tenant-/Environment-/Company-Identität binden und Recovery bauen.
- P0-03: Scan-Credit atomar und genau einmal je Run verbrauchen; Parallel- und Antwortverlusttests ergänzen.
- P0-04: jeden Scanfehler in einen terminalen Status überführen und Credit-/Run-Recovery ermöglichen.
- P0-05: lokale Finding-/Drilldown-Rechte mit frischem Access-Snapshot statt stale `Premium Enabled` erzwingen.

### P1 – vor Kunden-Go-Live schließen

- aktueller AL-/Analyzer-/Sandbox-Build, Install-/Upgrade-Codeunits und AL-Test-App;
- echte asynchrone Scans, Scheduler-Serviceberechtigung und negative Permission-Tests;
- Currency-Semantik, Exception-Audit, Lokalisierungschecker und Backendtests bereinigen;
- Token-Rotation/Recovery, Portal-Resend, Retention, Timeouts/Retry/Correlation-ID;
- Manifest-/Versions-/AppSource-Metadaten finalisieren.
- Assessment-Produkt-/Creditvertrag in Pricing, Admin, Snapshot und Tests vereinheitlichen.

### P2 – vor breitem Rollout einplanen

- Role-Center-Cues, Cancel/Partial Success, Dashboard-Tokenübergabe, Performance-/Retentiontests;
- typisierte Lizenzdaten und DST-/Zeitzonentests;
- Deprecation-Warnungen und UX-Politur.

### P3 – nach Stabilisierung

- erweiterte Telemetrie-Dashboards, automatisierte Trend-/Delta-Benachrichtigung und zusätzliche Komfortfilter.

## 9. Verbindliche Entscheidung

**NO-GO.** Die Einstufungen `CONDITIONAL GO`, `PILOT GO`, `CUSTOMER GO` und `APPSOURCE READY` sind wegen der fünf offenen P0-Gaps sowie der fehlenden AL-/Sandbox-Releaseevidenz nicht vertretbar.

## Status-Delta GL-EXT-P0A (16. Juli 2026)

Die ursprünglichen Auditfeststellungen und die historische 48-%-Bewertung bleiben oben unverändert. Dieser Delta-Nachweis bewertet nur P0-01/P0-02; eine vollständige Neugewichtung war nicht Teil des Sprints.

| Requirement | Ursprünglicher Auditstatus | Umgesetzte Korrektur | Neue Evidenz | Aktueller Status |
|---|---|---|---|---|
| R-03 / P0-01 Transport | DEFECTIVE | zentrale AL-/Backend-URL-Policy, produktive HTTPS-Middleware, enge Loopback-Ausnahme | P0A Transporttests; AL ReleaseCloud Compile; CodeCop/PTE-Cop 0 Fehler | **COMPLETE – P0 behoben** |
| R-04 / P0-02 Registrierung | DEFECTIVE | Entra+Environment+Company Identity-Key, DB-Constraint, transaktionaler Upsert, authentisierte Legacy-Bindung | Parallel-/Retry-/Identity-/Migrationstests | **COMPLETE – P0 behoben** |
| R-05 App-Version | DEFECTIVE | AL liest aktuelle `ModuleInfo.AppVersion()` | AL Compile und Registration-Payloadtests | **COMPLETE** |
| R-06 Portal-Recovery | PARTIAL | Portaluser-Deduplizierung, Invite-Status, authentisierter expliziter Resend | Portal-/Resend-/Mailfehler-Tests | **COMPLETE für Registrierung; breitere Token-Recovery bleibt P1** |
| R-08 Dashboard-Kontext | PARTIAL | tatsächlicher Entra-/Environment-/Company-Kontext; serverseitiger Exact Match | Dashboard-Kontext Positiv-/Negativtests | **COMPLETE für Tenant Context** |

Gesamtentscheidung bleibt **NO-GO**: P0-03, P0-04 und P0-05 sowie der BC-Sandbox-CAT sind weiterhin offen. P0A ist bereit für den Folgesprint GL-EXT-P0B. Vollständige Evidenz: `docs/GL_EXT_P0A_HTTPS_TENANT_REGISTRATION.md`.

Ein erneutes Gate darf frühestens erfolgen, wenn:

1. alle P0-Gaps mit automatisierten Regressionstests geschlossen sind;
2. alle releaseblockierenden P1-Gaps geschlossen oder mit Owner, Datum und akzeptiertem Restrisiko formell freigegeben sind;
3. AL-Compile plus CodeCop, AppSourceCop und PerTenantExtensionCop grün sind;
4. Install, Upgrade N-1 und die 23 CATs in einer BC-Sandbox ohne SUPER bestanden sind;
5. Backendtests vollständig grün und das Releasepaket aus CI reproduzierbar erzeugt ist.

Die konkrete Abarbeitung steht in `BC_EXTENSION_OPEN_GAPS.md`, die Abnahmetests in `BC_EXTENSION_CUSTOMER_ACCEPTANCE_TEST.md` und die Release-Gates in `BC_EXTENSION_RELEASE_CHECKLIST.md`.

## Status-Delta GL-EXT-P0B (16. Juli 2026)

Die historische 48-%-Bewertung bleibt unverändert; P0B bewertet ausschließlich P0-03.

| Requirement | Ursprünglicher Status | Korrektur | Evidenz | Aktuell |
|---|---|---|---|---|
| R-13 / P0-03 atomarer Creditverbrauch | DEFECTIVE | tenantgebundene Idempotency, DB-Lock plus Conditional Update, atomarer Scan-/Credit-/Ledger-Commit | 12 P0B-Tests, 76 relevante Regressionstests, Migration und AL-Build | **COMPLETE – P0 behoben** |
| Assessment/Validation | PARTIAL/unklar | getrennte Credittypen und Snapshot-Zähler | Produkt- und Paralleltests | **COMPLETE für Charging** |
| Monitoring/Free | PARTIAL | aktives Monitoring ohne Credit; Free-Slot einmal je Tenant | Ablauf-, Retry- und Free-Slot-Tests | **COMPLETE für Startannahme** |

Der technische P0-Fortschritt beträgt damit **3 von 5 P0-Gaps (60 %) geschlossen**. Die Gesamtentscheidung bleibt **NO-GO**, da P0-04 und P0-05 offen sind; die ursprüngliche Gesamtreadiness wird erst nach der P0-Serie und einem Sandbox-Gate neu gewichtet. Detailnachweis: `docs/GL_EXT_P0B_ATOMIC_CREDIT_CONSUMPTION.md`.

## Status-Delta GL-EXT-P0C (16. Juli 2026)

Die historische 48-%-Bewertung und die EXT-01-bis-EXT-08-Bewertungen bleiben unverändert. P0C bewertet ausschließlich P0-04.

| Requirement | Ursprünglicher Status | Korrektur | Evidenz | Aktuell |
|---|---|---|---|---|
| R-15 / P0-04 terminaler Scan-Lifecycle | DEFECTIVE | kanonische State Machine, serverseitige Übergangsprüfung, Worker-Lease/Heartbeat, Execution Token und terminaler AL-Exception-Handler | P0C-/Scanstatus-Tests, AL ReleaseCloud Compile | **COMPLETE – P0 behoben** |
| stale Run / Backendrestart | MISSING/PARTIAL | Startup- plus periodische Batch-Recovery, begrenzter Retry/Backoff, Max Attempts und CAS gegen Doppel-Recovery | Parallel-/Recovery-/Legacy-Migrationstests | **COMPLETE auf Codeebene** |
| Completion / Findings | PARTIAL | Completion erst nach transaktionalem Pflichtresultat; Unique Findingcode/Modul; Late-Writer-Schutz | Partial-/Complete-/Duplicate-/Tokenrotationstests | **COMPLETE auf Codeebene** |
| BC Monitor / Scheduler | PARTIAL | Terminalstatus-Healing, RetryRequired mit demselben Run/Request, kein zweiter Credit, lokale Failure-Persistenz | AL Compile; P0B-Regression und Lifecycle-Tests | **COMPLETE auf Codeebene; Sandbox offen** |

P0-Fortschritt: **4 von 5 (80 %)**. P0C ist bereit für GL-EXT-P0D. Die Entscheidung bleibt **NO-GO**, weil P0-05, BC-Sandbox/PostgreSQL-Staging und weitere P1-Releasegates offen sind. Vollständige Evidenz: `docs/GL_EXT_P0C_SCAN_LIFECYCLE_RECOVERY.md`.

## Status-Delta GL-EXT-P0D (20. Juli 2026)

Die ursprüngliche Auditmatrix und 48-%-Baseline bleiben als Historie bestehen. P0D schließt P0-05 auf Codeebene.

| Requirement | Ursprünglicher Status | Korrektur | Evidenz | Aktuell |
|---|---|---|---|---|
| R-10 / P0-05 lokale Rechte nach Ablauf | DEFECTIVE | versionierter 60-s-Snapshot, Backend-UTC, Context-Bindung, persistente Vorab-Invalidation, zentraler Fresh Access Guard | 51 P0D-Szenarien, AL ReleaseCloud Compile | **COMPLETE auf Codeebene** |
| R-21 Findings-Schutz | DEFECTIVE | Page-, Recordwechsel-, Action- und Dispatcher-Guards; Backend-Recheck | direkte Page-/Drilldown-/Revocationtests | **COMPLETE auf Codeebene; Sandbox offen** |
| R-23 Report | PARTIAL hinsichtlich Ablauf | JSON/HTML/PDF/Share-Link benötigen Report-Capability; Share-Token wird bei Abruf revalidiert | Report-Regressionen und Revocationtest | **COMPLETE für Authorization** |
| R-25 Permissions | PARTIAL | Viewer ohne direkte geschützte TableData-Rechte; indirekter Pagezugriff plus SaaS-Guard | Source-Contract und AL Compile | **PARTIAL; negative Sandboxtests offen** |

Funktionaler P0-Fortschritt: **5 von 5 (100 %)**. Die neu gewichtete Code-/Release-Readiness beträgt **64 %**: Transport, Registrierung, Credits, Lifecycle und Access Enforcement sind deutlich verbessert; Install/Upgrade, AL-Test-App, Sandbox, Schedulerrollen, Currency, Localization und AppSource bleiben niedrig bewertet. Das Produkt-Gate bleibt **NO-GO** für Pilot/Kunde, nicht wegen eines offenen funktionalen P0, sondern wegen fehlender Sandbox-/Upgrade-/P1-Releaseevidenz. P0D ist bereit für GL-EXT-P0E. Detail: `docs/GL_EXT_P0D_FRESH_ACCESS_ENFORCEMENT.md`.

## Status-Delta GL-EXT-P0E (20. Juli 2026)

P0E hat erstmals echte PostgreSQL-15-, Mehrinstanz-, Migration-, Parallelitäts- und Restart-Evidenz erbracht. Backend-Produktionsimage, AL 1.0.2.7, Install-/Upgrade-Codeunits, Schedulerrolle und ein kompilierter N-1-Stand 1.0.2.6 liegen vor. Pricing ist konsistent.

Automatisierte Abschlussregression: **261/261 Backendtests gegen PostgreSQL bestanden**; P0A–P0D fokussiert 105/105; P0E plus Pricing nach Race-Fix 21/21.

Die Readiness wurde vollständig neu gewichtet: **Gesamt 67 %, Pilot 58 %, Customer 47 %, AppSource 28 %**. Das Gate bleibt **NO-GO**, weil keine echte BC-Sandbox angebunden war. Fresh Install, N-1-Upgrade, Rollen/Scheduler ohne `SUPER` und 47 CATs sind `BLOCKED`, nicht bestanden. Vollständige Evidenz: `docs/GL_EXT_P0E_SANDBOX_RELEASE_GATE.md`.

## Status-Delta GL-EXT-UX01 (20. Juli 2026)

UX01 ordnet die Setup-Page kundenorientiert, ohne Backend-, Datenmodell-, Permission-, Lizenz-, Credit-, Scan- oder Schedulerlogik zu verändern. Status/Produkt/letzter Scan/nächster Lauf stehen oben; technische Tenant-/Environment-/Snapshotwerte liegen in „Advanced Information“; sichere Hauptaktionen sind promoted und der Registrierungs-Cache-Reset ist separat mit `Confirm(..., false)` geführt. Dashboard, Findings und Report verwenden weiterhin die frischen P0D-Access-Guards.

Automatisierte Evidenz: ReleaseCloud Compile 84/84 Dateien und CodeCop/PTECop ohne Fehler; Setup-XLF 0 fehlende/0 leere/0 abweichende Targets; Backend 255 bestanden/6 übersprungen. AppSourceCop und globale Localization bleiben mit denselben Gapklassen rot. 20 UX01-Sandbox-CATs sind `BLOCKED`.

Die UX-Dimension steigt codebasiert, daraus ergibt sich als nachvollziehbare Delta-Schätzung **Gesamt 69 %, Pilot 60 %, Customer 49 %, AppSource 28 %**. Das Gate bleibt **NO-GO**: UX-Politur ersetzt weder Fresh-Install-/Upgrade-/Rollen-CAT noch die 47 P0A–P0D- und 20 UX01-Sandboxfälle. Detail: `docs/GL_EXT_UX01_SETUP_PAGE_REFINEMENT.md`.

## Status-Delta GL-EXT-UX02 (20. Juli 2026)

UX02 schließt die konkrete 81-Treffer-Baseline (Checker 0), synchronisiert 1.208 vollständige DE-Targets und führt für 20 Backend-Quick-Checks stabile tenantsprachige Codeauflösung ein. Historische Findings bleiben unverändert; fragile AL-Wortersetzung ist entfernt. Compile, CodeCop/PTE, 3/3 Zieltests und die Backend-Gesamtsuite mit 258 bestanden/6 übersprungen sind grün.

Offen bleiben 193 AL-Issue-Codes ohne vollständigen deutschen Katalog, 155 direkte englische Kundenliterale und 20 BLOCKED Sandbox-CATs. Neubewertung: **Gesamt 70 %, Pilot 61 %, Customer 50 %, AppSource 28 %**. Entscheidung **NO-GO**; UX02B ist vor UX03 erforderlich.

## Status-Delta REPO-01A (20. Juli 2026)

REPO-01A beseitigt die Ursache der lokalen AL-Duplicate-Object-Fehler: 246 generierte AL-Dateien und drei zusätzliche Manifeste wurden ausschließlich aus `bc-extension/.build` entfernt. Der kanonische Bestand bleibt bei 84 Dateien/88 Objekten; App-ID, Name, Publisher, ID-Range und Fachlogik sind unverändert. Der Buildworkspace liegt nun außerhalb des AL-Projekts unter `.build/bc-extension/<Profile>`, unsichere Ziele werden vor jeder Anlage abgewiesen und ein automatischer Source-Uniqueness-Guard ist positiv und negativ verifiziert.

ReleaseCloud Compile, CodeCop/PTECop, XLF/JSON, Source-Hashdiff und Python-Compile sind grün. AppSourceCop zeigt nur die bekannte Baseline. Das Readiness-Gate und die UX02-Prozentwerte bleiben unverändert, weil Repository-Hygiene keine fehlende Sandbox-/Install-/Upgrade-Evidenz ersetzt. Detailnachweis: `docs/GL_REPO_01A_BUILD_HYGIENE.md`.

## Status-Delta GL-PILOT-01-FIX01 (20. Juli 2026)

Der in BC 28.3 beobachtete globale E-Mail-/Tenant-Konflikt ist codebasiert geschlossen. Dashboard-Benutzer besitzen jetzt relationale, eindeutige Tenant-Memberships; bestehende 1:1-Zuordnungen werden durch Migration 0025 verlustfrei backfillt. Login, Liste, sichere Standardauswahl, Tenant-Wechsel und 403 bei fehlender Membership sind implementiert. BC-Embed-Tokens bleiben strikt Single-Tenant.

Automatisierte API-, Migrations-, Race-, Security-, AL- und Localization-Gates sind grün. Der reale Post-Fix-CAT in `BCSentinel-Pilot` bleibt `BLOCKED`; deshalb bleiben Readiness-Prozentwerte und Produktentscheidung vorerst unverändert. Detail: `docs/GL_PILOT_01_FIX01_MULTI_TENANT_DASHBOARD_ACCESS.md`.

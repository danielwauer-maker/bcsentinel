# BCSentinel Go-Live Action Plan – bis zu 10 Pilotkunden

**Stand:** 2026-08-04  
**Basis:** Extension `1.0.2.20`, Merge-Commit `685a1881bbac8016659849bed7afc3d150d532a5`  
**Ziel:** kontrollierter Start mit 1–3 Pilotkunden und anschließende Erweiterung auf bis zu 10 Kunden

## 1. Ausgangslage

Der technische Kern ist einsatzfähig. Manueller und geplanter Monitoring-Scan wurden in einer realen Business-Central-Sandbox erfolgreich abgeschlossen. Der letzte Lauf verarbeitete 10/10 Module und 199/199 Prüfungen. Die zentralen CI-Gates waren grün.

Der Plan konzentriert sich deshalb nicht auf einen Neuaufbau, sondern auf die letzten Betriebs-, Support-, Dokumentations- und Skalierungsschritte.

## 2. Freigabestufen

### Stufe 1 – interner Release Candidate

Erforderlich:

- Deployment von 1.0.2.20 bestätigt,
- Artefakt und Commit eindeutig dokumentiert,
- Health-/Readiness-Smoke erfolgreich,
- BC-Extension installierbar,
- manueller und geplanter Scan erfolgreich.

### Stufe 2 – 1 Design Partner

Zusätzlich:

- Backup aktiv,
- Supportkanal definiert,
- Onboarding-Checkliste fertig,
- tägliche Logkontrolle,
- erster Kundenscan begleitet.

### Stufe 3 – bis zu 3 Pilotkunden

Zusätzlich:

- Restore-Test bestanden,
- Alarmierung aktiv,
- Login-/Mail-E2E bestanden,
- Pilotvertrag/DPA verfügbar,
- Troubleshooting-Runbook fertig.

### Stufe 4 – bis zu 10 Pilotkunden

Zusätzlich:

- 10-Tenant-Lasttest bestanden,
- 72-Stunden-Scheduler-Soak bestanden,
- Recovery-Drill bestanden,
- Operator-/Incident-Kapazität geklärt,
- Support-SLA und Eskalationsplan final.

## 3. Priorisierter Maßnahmenplan

### P0 – vor dem ersten externen Pilotkunden

| ID | Aufgabe | Automatisch durch ChatGPT/Codex | Manuell durch Daniel | Aufwand | Abnahmekriterium |
| --- | --- | --- | --- | ---: | --- |
| P0-01 | 1.0.2.20 Produktionsdeployment attestieren | Workflow, Commit, Health und Deploymentlogs prüfen; Nachweis dokumentieren | Produktionsseite und API öffnen; BC-Verbindung bestätigen | 1–2 h | Commit, Version, Health und Smoke-Test eindeutig dokumentiert |
| P0-02 | Installationsartefakt archivieren | Workflow-Artefakt identifizieren und Hash dokumentieren | `.app` herunterladen und in Freigabeordner speichern | 30–60 min | unveränderliches Artefakt mit SHA/Hash vorhanden |
| P0-03 | frische Neuinstallation testen | Testcheckliste vorbereiten | neue Sandbox/Company nutzen und 1.0.2.20 installieren | 1–2 h | Setup, Registrierung und Free Scan PASS |
| P0-04 | Upgrade-Abnahme dokumentieren | Datenerhalt-Checkliste erstellen | Upgrade eines bestehenden Standes durchführen und Historie/Setup prüfen | 1–2 h | Konfiguration, Historie und Entitlements bleiben erhalten |
| P0-05 | Backup-Job verifizieren | Backup-Konfiguration und Logs prüfen | Server-/Providerzugriff und Speicherziel kontrollieren | 1–2 h | aktuelles Backup vorhanden und protokolliert |
| P0-06 | Restore-Test durchführen | Restore-Runbook und Prüfschritte erstellen | isolierte Restore-Umgebung freigeben/bedienen | 3–5 h | wiederhergestellte DB startet und Kernobjekte sind lesbar |
| P0-07 | Basis-Alerting aktivieren | Health-, DB-, Deployment- und Fehleralarme konfigurieren | Empfängerkanal bestätigen und Testalarm quittieren | 2–4 h | Testfehler erzeugt Alarm innerhalb definierter Zeit |
| P0-08 | Pilot-Onboarding-Checkliste finalisieren | technische Schritte und Abnahmepunkte schreiben | Ansprechpartner, Termine und Kundendaten ergänzen | 2–3 h | wiederholbarer Ablauf von Installation bis erstem Report |
| P0-09 | Supportkanal und Reaktionszeit festlegen | Supportvorlage und Ticketstruktur erstellen | E-Mail/Telefon/Zeiten verbindlich festlegen | 1 h | Pilotkunde kennt Kanal und Reaktionszeit |
| P0-10 | Datenschutz-/Pilotvertrag bereitstellen | technische Leistungsbeschreibung und Datenflüsse liefern | juristische Prüfung/Freigabe organisieren | 2–6 h plus extern | unterschriftsfähige Unterlagen vorhanden |

### P0 – vor Erweiterung auf drei Pilotkunden

| ID | Aufgabe | Automatisch | Manuell | Aufwand | Abnahmekriterium |
| --- | --- | --- | --- | ---: | --- |
| P0-11 | Login-/Einladungs-E2E | Testfälle und Logs prüfen | echte Mail empfangen, Einladung, Passwort, Sperrung und Reset testen | 2–4 h | vollständiger User-Lifecycle PASS |
| P0-12 | Mailzustellung härten | SMTP-Konfiguration, Retry und Templates prüfen | DNS/SPF/DKIM/DMARC und Spamordner prüfen | 2–4 h | definierte Testmails werden zuverlässig zugestellt |
| P0-13 | Fremdtenant-Isolation real testen | Negativtests vorbereiten | zweiten Tenant/User bedienen | 1–2 h | kein Zugriff auf fremde Daten möglich |
| P0-14 | Netzabbruch-/Retry-Test | API-Timeout-/Retrypfad prüfen | Scan während kurzer Unterbrechung beobachten | 2–3 h | keine Dublette, nachvollziehbarer Retry/Fehlerstatus |
| P0-15 | Operator-Troubleshooting finalisieren | Diagnosekommandos, Logs und Entscheidungsbaum dokumentieren | Schritte einmal praktisch durchspielen | 2–4 h | Operator kann häufige Fehler ohne Codeänderung behandeln |

### P0 – vor Erweiterung auf zehn Pilotkunden

| ID | Aufgabe | Automatisch | Manuell | Aufwand | Abnahmekriterium |
| --- | --- | --- | --- | ---: | --- |
| P0-16 | 10-Tenant-Lasttest | Testszenario, Datensätze, Parallelität und Auswertung implementieren | Testfenster freigeben | 4–8 h | keine Datenvermischung; Fehlerquote und Laufzeit innerhalb SLO |
| P0-17 | 72h Scheduler-Soak | automatische Auswertung der Läufe und Duplikate | drei Tage beobachten und Ausfälle dokumentieren | 72 h Laufzeit | alle erwarteten Läufe vorhanden, keine Doppelstarts oder Hänger |
| P0-18 | Recovery-Drill | Ausfall- und Wiederanlaufszenario vorbereiten | Container/DB kontrolliert stoppen und Wiederanlauf begleiten | 3–5 h | Dienst und Scans erholen sich nach Runbook |
| P0-19 | Incident-Prozess testen | Incident-Vorlage und Kommunikationsentwurf erstellen | Probeincident durchführen | 1–2 h | Erkennung, Eskalation, Statusupdate und Abschluss dokumentiert |
| P0-20 | Kapazitätsplan | Messwerte und Supportaufwand aus Pilot 1–3 auswerten | verfügbare Betreuungszeit festlegen | 1–2 h | klare Obergrenzen und Eskalationsregeln für zehn Kunden |

## 4. P1 – kurz nach Pilotstart

| ID | Aufgabe | Nutzen | Aufwand |
| --- | --- | --- | ---: |
| P1-01 | Permission-Set-Rollenmatrix vollständig testen | verhindert Über-/Unterberechtigung | 3–4 h |
| P1-02 | Deinstallations-/Reinstallationspfad testen | verbessert Supportfähigkeit | 2–3 h |
| P1-03 | englische Extension und Reports vollständig prüfen | internationale Pilotfähigkeit | 3–5 h |
| P1-04 | Dashboard-Leer-/Fehlerzustände verbessern | bessere Nutzerführung | 3–6 h |
| P1-05 | Reporttexte und Finanz-Disclaimer finalisieren | fachliche und rechtliche Klarheit | 2–4 h |
| P1-06 | Monitoring-Retention und Aufbewahrung dokumentieren | Datenschutz und Betrieb | 2–3 h |
| P1-07 | Stripe-Live-Smoke | spätere Self-Service-Fähigkeit | 3–5 h |
| P1-08 | Audit-/Supportexport | bessere Diagnose und Kundenkommunikation | 4–8 h |

## 5. Konkreter Ablauf für Pilotkunde 1

### Vor dem Termin

1. Kunde, Tenant, Environment und Company erfassen.
2. Pilotvertrag/DPA bestätigen.
3. Extension-Artefakt und Installationsanleitung bereitstellen.
4. Backup-/Rollback-Punkt beim Kunden klären.
5. Supporttermin und Ansprechpartner festlegen.

### Installation und Setup

1. Extension 1.0.2.20 installieren.
2. Permission Sets zuweisen.
3. Setup öffnen.
4. HTTPS-Endpoint und Registrierung prüfen.
5. Tenant-/Company-Zuordnung im Backend kontrollieren.
6. Free Scan starten.
7. Historie, Findings, Dashboard, HTML und PDF prüfen.

### Monitoring-Aktivierung

1. Monitoring-Entitlement setzen.
2. Check-Auswahl kontrollieren.
3. manuellen Monitoring-Scan ausführen.
4. erfolgreichen Abschluss mit Modulen/Checks/Findings protokollieren.
5. Scheduler konfigurieren.
6. ersten geplanten Lauf abwarten und prüfen.

### Abnahme

1. Kunde bestätigt sichtbaren Nutzen.
2. offene Findings und DH-Ausnahmen erläutern.
3. Report gemeinsam besprechen.
4. Supportkanal und nächste Review-Woche bestätigen.
5. Abnahmeprotokoll speichern.

## 6. Täglicher Pilotbetrieb

Jeden Werktag:

- `/health` und `/health/ready` prüfen,
- fehlgeschlagene Deployments prüfen,
- fehlgeschlagene oder hängende Scans prüfen,
- Backend-/DB-Fehlerlogs prüfen,
- offene Supportfälle priorisieren,
- Backupstatus kontrollieren.

Wöchentlich:

- Scheduler-Vollständigkeit je Tenant prüfen,
- Scanlaufzeiten und Fehlerquote auswerten,
- Speicher-/DB-Wachstum prüfen,
- Pilotfeedback sammeln,
- offene P0/P1-Maßnahmen aktualisieren.

## 7. Abbruch- und Rollback-Kriterien

Pilotaufnahme pausieren, wenn mindestens eines zutrifft:

- Tenantübergreifender Datenzugriff,
- wiederholter Credit-Doppelverbrauch,
- Datenverlust oder nicht wiederherstellbare DB,
- mehr als ein ungeklärter Scheduler-Ausfall je Tenant,
- Scan bleibt wiederholt ohne Recovery hängen,
- kritische Sicherheitslücke,
- keine funktionsfähige Alarmierung oder kein erreichbarer Operator.

Rollback:

1. neue Pilotaktivierungen stoppen,
2. betroffene Scheduler deaktivieren,
3. Version und Zeitpunkt dokumentieren,
4. Backend/DB sichern,
5. auf letzten verifizierten Stand zurückgehen oder Extension zurücksetzen,
6. Kunden transparent informieren,
7. Root-Cause und Wiederfreigabe dokumentieren.

## 8. Empfohlener Zeitplan

### Tag 1

- Deployment-/Artefaktnachweis,
- frische Installation,
- Upgrade-Smoke,
- Onboarding-Checkliste.

### Tag 2

- Backup-/Restore-Test,
- Alerting,
- Support-/Incident-Runbook.

### Tag 3

- Login-/Mail-E2E,
- Fremdtenant-Negativtest,
- Pilotunterlagen finalisieren.

### Tag 4

- Pilotkunde 1 installieren und ersten Scan begleiten.

### Tag 5–7

- Stabilität beobachten,
- Feedback beheben,
- Pilotkunden 2 und 3 nur bei stabilem Betrieb aufnehmen.

### Woche 2

- 10-Tenant-Lasttest,
- 72h Scheduler-Soak,
- Recovery-Drill,
- Freigabe für Erweiterung auf bis zu zehn Kunden.

## 9. Verantwortungsaufteilung

### ChatGPT/Codex

- Repository-, Workflow- und Loganalyse,
- automatisierte Tests und Regressionstests,
- Dokumentationsentwürfe,
- technische Checklisten,
- Last-/Soak-Auswertung,
- Fehleranalyse und gezielte Codefixes,
- PR-, CI- und Deploymentbegleitung.

### Daniel

- Business-Central-Sandbox- und Kundenzugriff,
- manuelle UI-/Berechtigungs-/Mailtests,
- Provider-/Serverzugriffe,
- juristische und kaufmännische Freigaben,
- Kundenkommunikation,
- Supportzeiten und Eskalationsentscheidungen,
- finale Go-/No-Go-Freigabe.

## 10. Aktuelle Empfehlung

BCSentinel sollte jetzt nicht weiter intern perfektioniert werden, ohne echtes Kundenfeedback zu sammeln. Der richtige nächste Schritt ist:

> **Pilotkunde 1 nach Abschluss von Deployment-, Backup-/Restore-, Alerting- und Onboarding-Gate aufnehmen.**

Bei sieben stabilen Betriebstagen können Pilotkunden 2 und 3 folgen. Die Erweiterung auf zehn Kunden erfolgt erst nach Lasttest, 72-Stunden-Scheduler-Soak und Recovery-Drill.
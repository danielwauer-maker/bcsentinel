# BCSentinel Go-Live Feature Audit – Stand 1.0.2.20

**Auditdatum:** 2026-08-04  
**Releasebasis:** `staging`, Merge-Commit `685a1881bbac8016659849bed7afc3d150d532a5`  
**Extension-Version:** `1.0.2.20`  
**Ziel:** kontrollierter Start mit bis zu zehn aktiv betreuten Pilotkunden  
**Entscheidung:** **CONDITIONAL GO für 1–3 eng betreute Pilotkunden; NO-GO für zehn parallele Pilotkunden ohne Abschluss der verbleibenden Betriebs- und Support-Gates**

## 1. Executive Summary

BCSentinel hat mit Version 1.0.2.20 einen wesentlichen Go-Live-Meilenstein erreicht. Der zuvor blockierende Monitoring-Pfad wurde in einer realen Business-Central-Sandbox erfolgreich nachgewiesen:

- manueller Monitoring-Scan erfolgreich gestartet und abgeschlossen,
- geplanter automatischer Monitoring-Task erfolgreich gestartet und abgeschlossen,
- zehn von zehn Modulen verarbeitet,
- 199 von 199 Prüfungen ausgeführt,
- Scan-Historie korrekt angelegt,
- 80 Findings und der berechnete Score 54/100 gespeichert,
- finanzielle Auswirkung 50.577,81 EUR angezeigt,
- frühere RowVersion-/Concurrency-Abbrüche in der Initialisierung nicht mehr reproduziert.

Die drei verpflichtenden Pull-Request-Gates für PR #24 waren grün:

- `BC AL Compile and Cop Gate #56`: PASS,
- `ARCH-02A Compatibility Gate #106`: PASS,
- `PILOT-E2E-01A Automated Readiness #39`: PASS nach erfolgreichem Re-Run.

Damit ist der zentrale Produktkern für einen betreuten Pilotbetrieb funktionsfähig. Die verbleibenden Risiken liegen nicht mehr primär im Scan-Algorithmus, sondern im produktiven Betrieb: Recovery, Backup/Restore, Alerting, Mailzustellung, Supportprozesse, finaler Produktionsnachweis, Last-/Soak-Evidence für zehn Tenants und vollständige Pilotunterlagen.

## 2. Bewertungsmaßstab

| Status | Bedeutung |
| --- | --- |
| VERIFIED | Implementiert und durch relevante automatisierte oder reale End-to-End-Evidence bestätigt |
| IMPLEMENTED_NOT_E2E_VERIFIED | Implementiert, aber noch nicht vollständig im finalen Produktionspfad geprüft |
| PARTIAL | Kern vorhanden, aber ein relevanter Teil fehlt oder ist nicht ausreichend belegt |
| EXTERNAL_MANUAL_CHECK_REQUIRED | Prüfung muss in externer Infrastruktur oder durch einen Operator erfolgen |
| NOT_APPLICABLE | Für den betreuten Pilotstart nicht erforderlich |

Bewertungsskala:

- 90–100 %: pilotbereit,
- 75–89 %: pilotbereit mit klaren Auflagen,
- 60–74 %: nur interner oder Design-Partner-Test,
- unter 60 %: nicht pilotbereit.

## 3. Gesamtbewertung

| Bereich | Readiness | Bewertung |
| --- | ---: | --- |
| Business-Central-Extension | 91 % | Pilotbereit mit kleinen Betriebsauflagen |
| Scan-Engine und Findings | 93 % | Kernfunktion verifiziert |
| Monitoring und Scheduler | 92 % | Manueller und geplanter Lauf real verifiziert |
| Backend/API | 86 % | Starker automatisierter Nachweis; Produktionsbetrieb weiter härten |
| Dashboard | 78 % | Grundfunktion vorhanden; UX, Rollen- und Pilotabnahme noch offen |
| Executive Report | 88 % | HTML/PDF real nutzbar; finale Branding-/Inhaltsabnahme offen |
| Loginportal/Mandantenfähigkeit | 82 % | Kern vorhanden; Rollen-/Einladungs- und Supportpfade weiter prüfen |
| Mailversand | 64 % | Funktional implementiert, aber Live-Zustellung und Betriebsnachweis fehlen |
| Billing/Lizenzierung | 80 % | Pilotfähig mit manueller Rechnungsstellung; Self-Service noch nicht zwingend |
| Landingpage/Recht | 76 % | Grundstruktur vorhanden; finale Inhalte, Badges und Produktionsabnahme offen |
| Infrastruktur/Deployment | 78 % | Deployment funktioniert; Recovery, Restore und Alerting sind offen |
| Dokumentation/Support | 69 % | Umfangreich begonnen, aber Operator- und Kundenpaket noch nicht vollständig abgenommen |
| Sicherheit/Datenschutz | 81 % | Gute technische Basis; externe Abnahme und Betriebsnachweise fehlen |
| **Gesamt – 1 bis 3 Pilotkunden** | **85 %** | **CONDITIONAL GO** |
| **Gesamt – zehn Pilotkunden gleichzeitig** | **74 %** | **NO-GO bis Betriebs- und Skalierungsgates geschlossen sind** |

## 4. Detaillierte Feature- und Komponentenbewertung

### 4.1 Business-Central-Extension

| Feature | Status | Aktuellster Nachweis | Restrisiko / offene Aufgabe | Readiness |
| --- | --- | --- | --- | ---: |
| Installation | VERIFIED | Versionen 1.0.2.12 bis 1.0.2.20 wurden in der Sandbox installiert bzw. aktualisiert | frische Neuinstallation von 1.0.2.20 auf leerem Tenant dokumentieren | 90 % |
| Upgrade | VERIFIED | Upgrade bis 1.0.2.20 erfolgreich; bestehende Historie blieb sichtbar | formale Datenerhalt-Checkliste und Rollback-Anweisung ergänzen | 88 % |
| Setup und Guided Setup | VERIFIED | Setup, API-Verbindung und Registrierung real bedient | finaler Kunden-Screenshot und kurze Ersteinrichtungsanleitung | 92 % |
| Registrierung | VERIFIED | Registrierung und Duplicate-Schutz praktisch sowie automatisiert belegt | Responseverlust-/Retry-Negativfall noch einmal im RC protokollieren | 92 % |
| Tenant-/Company-Zuordnung | VERIFIED | Tenant, Environment, Company und Membership korrekt zugeordnet | Mehrcompany-Negativfall für Pilot 2 ergänzen | 90 % |
| HTTPS/API-Kommunikation | VERIFIED | BC kommuniziert über HTTPS mit der Entwicklungs-API | finaler PROD-Zertifikats- und Endpoint-Nachweis | 88 % |
| Token-Speicherung | IMPLEMENTED_NOT_E2E_VERIFIED | IsolatedStorage und gehashte Backend-Tokens implementiert | Upgrade-, Reinstall- und Permission-Negativtest dokumentieren | 80 % |
| Permission Sets | IMPLEMENTED_NOT_E2E_VERIFIED | Viewer-, Scan-, Setup-, Admin- und Scheduler-Sets vorhanden | echte Rollenmatrix mit Positiv-/Negativtests | 76 % |
| Free Scan | VERIFIED | Scan, Historie, Findings, Dashboard und Reports praktisch nachgewiesen | RC-Smoke auf finaler Produktionsumgebung | 94 % |
| Assessment | VERIFIED | Freischaltung, Findings, Zugriffslaufzeit und Report praktisch nachgewiesen | kompakter PROD-Smoke | 90 % |
| Validation Check | VERIFIED | Credit-Verbrauch und Scanabschluss praktisch nachgewiesen | erneuter Konkurrenz-/Retryfall auf PostgreSQL ist sinnvoll | 88 % |
| Monitoring-Entitlement | VERIFIED | Monitoring erfolgreich freigeschaltet | Ablauf-/Renewal-Test noch offen | 88 % |
| Manueller Monitoring-Scan | VERIFIED | 1.0.2.20: vollständig abgeschlossen, 10/10 Module, 199/199 Checks | kein aktueller Blocker | 98 % |
| Geplanter Monitoring-Scan | VERIFIED | automatischer Task erfolgreich abgeschlossen | 24-Stunden-Nachweis mit mindestens zwei aufeinanderfolgenden Läufen | 94 % |
| Scan-Historie | VERIFIED | erfolgreiche und fehlgeschlagene Läufe transparent sichtbar | Filter-/Aufbewahrungsstrategie dokumentieren | 94 % |
| Findings und Drilldown | VERIFIED | Findings real angezeigt; 80 Probleme im aktuellen Lauf | Stichprobe „Open in BC“ für mehrere Datentypen | 90 % |
| DH-Ausnahmen | VERIFIED | Setzen, Ausschließen und spätere Scanberücksichtigung praktisch geprüft | Rollen-/Auditlog-Negativfall ergänzen | 90 % |
| Scheduler-Konfiguration | VERIFIED | geplanter Task lief erfolgreich | Zeitzone, verpasste Ausführung und Reaktivierung dokumentieren | 88 % |
| Lokalisierung DE/EN | IMPLEMENTED_NOT_E2E_VERIFIED | XLF-Struktur und deutsche Oberfläche vorhanden | vollständiger englischer UI-Smoke | 78 % |
| Deinstallation/Reinstallation | PARTIAL | Plattformstandard vorhanden | Datenbeibehaltung, Tokenzustand und Supportanweisung testen | 62 % |

**Extension-Gesamturteil:** Die Extension ist für einen kontrollierten Pilotbetrieb technisch geeignet. Der frühere P0-Blocker „Monitoring bricht in der Initialisierung ab“ ist geschlossen.

### 4.2 Scan-Engine, Score und Findings

| Komponente | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| Modulare Scan-Engine | VERIFIED | zehn Module werden vollständig durchlaufen | Laufzeitmessung auf größerem Tenant |
| Check-Katalog | VERIFIED | 199 Prüfungen aktiv und vollständig ausgeführt | fachliche Stichprobe der wichtigsten 20 Checks |
| Check-Auswahl | VERIFIED | Concurrency-Fix in 1.0.2.20 verhindert schreibende Kataloginitialisierung im Laufzeitpfad | Bedienbarkeit der individuellen Auswahl abnehmen |
| Score-Berechnung | VERIFIED | Score 54/100 im realen Lauf berechnet | fachliche Plausibilisierung an zwei weiteren Datenbeständen |
| Findings-Persistenz | VERIFIED | 80 Findings gespeichert und angezeigt | Retention und Löschkonzept dokumentieren |
| Finanzielle Auswirkung | VERIFIED | 50.577,81 EUR im Testlauf angezeigt | Methodik und Disclaimer im Kundenbericht klar erläutern |
| Exception-Verarbeitung | VERIFIED | Ausnahmen beeinflussen Folgescans | Massenpflege und Auditexport später ausbauen |
| Performance | IMPLEMENTED_NOT_E2E_VERIFIED | kleinere Sandbox läuft vollständig | Lasttest mit realistischem Datenvolumen und Laufzeit-SLO |

**Bewertung:** 93 %. Fachlich stark und für Pilotnutzen bereits überzeugend.

### 4.3 Backend und API

| Komponente | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| FastAPI-Kern | VERIFIED | umfangreiche Regressionstests erfolgreich | Produktions-SLOs und Fehlerbudgets definieren |
| Scan Start/Sync Lifecycle | VERIFIED | automatisierte Lifecycle-, Lease-, Heartbeat- und Recovery-Tests vorhanden | echter Netzabbruch während Scan synchronisieren |
| Atomarer Credit-Verbrauch | VERIFIED | PostgreSQL-Concurrency-Gate erfolgreich | sporadischen SQLite-Paralleltest weiter beobachten |
| Idempotenz | VERIFIED | Duplicate-/Retry-Verträge vorhanden | produktionsnahe Wiederholungs- und Timeout-Stichprobe |
| PostgreSQL/Alembic | IMPLEMENTED_NOT_E2E_VERIFIED | Migrationskette und PostgreSQL-Gate vorhanden | Upgrade/Downgrade/Upgrade auf Kopie des Produktionsschemas |
| Multi-Tenant-Isolation | VERIFIED | automatisierte Membership- und Isolationstests | zweiter realer Pilottenant als Negativtest |
| Access Control | VERIFIED | TTL/Entitlement/Guard implementiert und getestet | Ablauf und Wiederfreischaltung real prüfen |
| Observability | PARTIAL | strukturierte Logs und Health-Endpunkte vorhanden | produktive Alarmierung, Dashboard und Bereitschaftsweg fehlen |
| Rate Limiting/Abuse | IMPLEMENTED_NOT_E2E_VERIFIED | Schutzmechanismen vorhanden | externer Grenzwert-/IP-/Tenant-Test |
| API-Versionierung | PARTIAL | funktionierender aktueller Vertrag | formale Deprecation- und Kompatibilitätsstrategie |

**Bewertung:** 86 %. Für wenige betreute Piloten ausreichend; für zehn Kunden fehlen Betriebsnachweise.

### 4.4 Dashboard

| Feature | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| Dashboard-Aufruf aus BC | VERIFIED | real geöffnet | PROD-Smoke |
| Tenantbezogene Daten | VERIFIED | Membership-/Tenantmodell vorhanden | realer Fremdtenant-Negativtest |
| Score/KPIs/Findings | VERIFIED | Daten werden dargestellt | visuelle Abnahme mit finalen Pilotdaten |
| Verlauf/Trends | IMPLEMENTED_NOT_E2E_VERIFIED | Datenmodell vorhanden | Mehrscan-UX und Filter prüfen |
| Rollen und Login | IMPLEMENTED_NOT_E2E_VERIFIED | Dashboard User/Membership vorhanden | Einladung, Passwortwechsel, Sperrung, Reset vollständig testen |
| Responsive Design | PARTIAL | Weboberfläche vorhanden | mobile/tablet Abnahme |
| Fehler-/Leerezustände | PARTIAL | Grundzustände vorhanden | kein Scan, abgelaufener Zugriff, Backend nicht erreichbar |
| Export/Weitergabe | PARTIAL | Reportexport vorhanden | Dashboard-spezifische Exporte optional später |

**Bewertung:** 78 %. Für betreute Piloten nutzbar, aber noch nicht vollständig als selbstständiges SaaS-Portal ausgereift.

### 4.5 Executive Report

| Feature | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| HTML-Report | VERIFIED | real geöffnet | finaler Branding-Smoke |
| PDF-Report | VERIFIED | sauberer zweiseitiger A4-Render nachgewiesen | Browser-/Font-Konsistenz in PROD |
| Score/KPIs | VERIFIED | werden dargestellt | Begrifflichkeiten fachlich final abnehmen |
| Findings/Schweregrade | VERIFIED | enthalten | Priorisierung der Top-Maßnahmen weiter schärfen |
| Finanzielle Wirkung | VERIFIED | vorhanden | Methodik und Haftungshinweis finalisieren |
| CTA/Next Steps | IMPLEMENTED_NOT_E2E_VERIFIED | vorhanden | Texte an finales Pilotangebot anpassen |
| Mehrsprachigkeit | PARTIAL | deutsche Fassung stark | englischen Report vollständig prüfen |

**Bewertung:** 88 %. Einer der stärksten sichtbaren Produktbestandteile.

### 4.6 Loginportal, Benutzer und Mandanten

| Feature | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| Benutzerverwaltung | IMPLEMENTED_NOT_E2E_VERIFIED | User/Membership-Modell vorhanden | vollständiger Operator-Smoke |
| Einladungen | IMPLEMENTED_NOT_E2E_VERIFIED | Mail-/Tokenpfad implementiert | Live-Mailzustellung und Ablauf testen |
| Passwort setzen/ändern | IMPLEMENTED_NOT_E2E_VERIFIED | vorhanden | Reset, Lockout und Supportfall testen |
| Tenantwechsel | PARTIAL | Membership-Konzept vorhanden | UX und Berechtigungsprüfung |
| Adminportal | IMPLEMENTED_NOT_E2E_VERIFIED | Basic Auth/CSRF und Adminfunktionen vorhanden | MFA/SSO-Roadmap und Auditlogging |
| Supportzugriff | PARTIAL | technisch möglich | dokumentierte Freigabe, Zeitbegrenzung und Protokollierung |

**Bewertung:** 82 %. Für manuell betreute Nutzer ausreichend, aber nicht für vollständig selbstständiges Onboarding.

### 4.7 Mailversand

| Feature | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| SMTP-Integration | IMPLEMENTED_NOT_E2E_VERIFIED | Codepfad vorhanden | produktive Credentials und Zustelltest |
| Einladungsmails | IMPLEMENTED_NOT_E2E_VERIFIED | Vorlagen/Pfad vorhanden | SPF, DKIM, DMARC, Spamtest |
| System-/Fehlermails | PARTIAL | teilweise vorhanden | verbindliche Alarmierungsfälle definieren |
| Kundenreport per Mail | PARTIAL | nicht als vollständig verifizierter Pilotpfad belegt | Versand, Datenschutz und Wiederholung testen |
| Bounce/Retry | PARTIAL | kein vollständiger Betriebsnachweis | Retry-/Dead-Letter-Prozess |

**Bewertung:** 64 %. Kein Blocker, solange Pilotkommunikation manuell erfolgt; vor skalierendem Betrieb P0/P1.

### 4.8 Billing und Lizenzierung

| Feature | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| Produktmodell | VERIFIED | Assessment, Validation und Monitoring praktisch nutzbar | finale Preis-/Leistungstexte synchronisieren |
| Credits | VERIFIED | Validation Credit verbraucht | Erstattung und Fehlversuch-Regel dokumentieren |
| Entitlements | VERIFIED | Monitoring freigeschaltet | Ablauf, Renewal und Grace Period testen |
| Stripe Checkout | IMPLEMENTED_NOT_E2E_VERIFIED | Code vorhanden | Live-Smoke vor Self-Service |
| Webhooks | IMPLEMENTED_NOT_E2E_VERIFIED | implementiert | Retry, Signatur und Duplicate-Event in Live-Test |
| Rechnungsstellung | PARTIAL | manuell als Pilotprozess möglich | Vorlage und Buchhaltungsprozess definieren |
| Refund/Chargeback | NOT_APPLICABLE | für erste betreute Piloten nicht erforderlich | vor öffentlichem Self-Service ergänzen |

**Bewertung:** 80 %. Für Pilotkunden mit manueller Rechnung ausreichend.

### 4.9 Landingpage und rechtliche Seiten

| Feature | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| Hauptseite | IMPLEMENTED_NOT_E2E_VERIFIED | professionelle Grundlage vorhanden | finaler Produktions- und Mobile-Smoke |
| Produktbeschreibung | PARTIAL | umfangreich vorhanden | exakt mit 1.0.2.20 und Pilotangebot synchronisieren |
| Preise | PARTIAL | Modell definiert | finale Preisfreigabe und korrekte Darstellung |
| Datenschutz/Impressum | IMPLEMENTED_NOT_E2E_VERIFIED | Seiten vorhanden | juristische Endprüfung |
| AGB/Vertragsunterlagen | PARTIAL | Inhalte vorbereitet | Pilotvertrag/DPA finalisieren |
| Zertifizierungs-Badges | PARTIAL | Platzhalter vorgesehen | ungültige Platzhalter klar kennzeichnen oder entfernen |
| Lead-/Kontaktformular | IMPLEMENTED_NOT_E2E_VERIFIED | technisch vorhanden | Zustellung, Spam- und DSGVO-Test |

**Bewertung:** 76 %. Für gezielte Pilotansprache ausreichend, nicht für breiten öffentlichen Verkauf.

### 4.10 Infrastruktur, Deployment und Betrieb

| Komponente | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| GitHub Actions | VERIFIED | zentrale Gates grün | Docker-Windows-Runner bleibt gelegentlich instabil |
| Hetzner Deployment | VERIFIED | Deployment-Workflow lief bei vorherigen Merges erfolgreich | aktuellen 1.0.2.20 Deploystatus archivieren |
| Health/Readiness | VERIFIED | Endpunkte vorhanden | externe Verfügbarkeitsüberwachung |
| Backup | IMPLEMENTED_NOT_E2E_VERIFIED | technische Grundlage vorhanden | echter Backup-Job und Nachweis |
| Restore | MISSING/UNVERIFIED | kein aktueller erfolgreicher Restore-Nachweis | Restore-Test ist P0 vor zehn Piloten |
| Recovery | PARTIAL | Scan-Recovery im Code vorhanden | Prozess-/Container-/DB-Ausfall real testen |
| Alerting | PARTIAL | Logs vorhanden | Alarmkanal, Schwellenwerte und Eskalation einrichten |
| Secrets | IMPLEMENTED_NOT_E2E_VERIFIED | GitHub/Server-Secrets genutzt | Rotation und Notfallzugriff dokumentieren |
| Skalierung | PARTIAL | Architektur grundsätzlich geeignet | 10-Tenant-Last- und Soak-Test |
| Incident Response | DOCUMENTED_ONLY/PARTIAL | Entwürfe vorhanden | Bereitschaft, Ansprechpartner und Vorlagen finalisieren |

**Bewertung:** 78 %. Für wenige Pilotkunden mit enger Betreuung tragfähig; Hauptgrund gegen sofortige zehn parallele Kunden.

### 4.11 Dokumentation und Support

| Komponente | Status | Bewertung | Offene Punkte |
| --- | --- | --- | --- |
| Installationsanleitung | IMPLEMENTED_NOT_E2E_VERIFIED | Entwurf vorhanden | Screenshots 1.0.2.20 und Endabnahme |
| Setup-/Registrierungsanleitung | IMPLEMENTED_NOT_E2E_VERIFIED | Entwurf vorhanden | echte Schrittfolge mit Fehlerfällen |
| Benutzerhandbuch | PARTIAL | umfangreiche Dokumente begonnen | einheitliches finales Format und Screenshots |
| Monitoring-Handbuch | PARTIAL | Inhalte vorhanden | manuellen/geplanten Erfolgsnachweis einarbeiten |
| Operator-Runbook | PARTIAL | verschiedene Betriebsdokumente vorhanden | ein verbindliches Tages-/Wochen-/Incident-Runbook |
| Troubleshooting | PARTIAL | Erfahrungen vorhanden | Fehlercodes, Diagnosepfade und Supportdaten standardisieren |
| Pilot-Onboarding | PARTIAL | Ablauf ableitbar | Checkliste, Verantwortliche und Abnahmeprotokoll |
| Support-SLA | MISSING/PARTIAL | kein finaler Pilot-SLA | Reaktionszeiten und Kanäle definieren |

**Bewertung:** 69 %. Dokumentation ist der größte sichtbare organisatorische Restblocker.

## 5. Go-Live-Entscheidung nach Szenario

### Szenario A – ein Design Partner

**GO.** Technisch vertretbar, sofern Daniel den Kunden persönlich onboardet, den ersten Scan begleitet und täglich die Logs kontrolliert.

### Szenario B – drei eng betreute Pilotkunden

**CONDITIONAL GO.** Vorher müssen mindestens folgende Punkte erledigt sein:

1. produktiver 1.0.2.20 Deploymentnachweis,
2. Backup-Job und Restore-Test,
3. Alarmierung für API-/DB-/Scanfehler,
4. finales Onboarding- und Troubleshooting-Paket,
5. Supportkanal und Reaktionszeit.

### Szenario C – zehn parallele Pilotkunden

**NO-GO im aktuellen Stand.** Zusätzlich erforderlich:

1. 10-Tenant-Last-/Soak-Test,
2. mindestens 72 Stunden Scheduler- und Monitoring-Evidence,
3. Recovery- und Restore-Drill,
4. vollständige Rollen-/Login-/Mail-Abnahme,
5. Operator-Kapazitäts- und Eskalationsplan,
6. finaler Pilotvertrag/DPA und definierter Supportumfang.

## 6. Aktuell geschlossene Blocker

- Historieneintrag wird vor Background-Verarbeitung zuverlässig angelegt.
- manueller Monitoring-Scan startet und beendet den Scan erfolgreich.
- geplanter Monitoring-Task funktioniert.
- RowVersion-Konflikt im Fortschrittsupdate wurde behoben.
- Check-Katalog wird im Laufzeitpfad nicht mehr bei jeder Prüfung neu geschrieben.
- `AddCheck()` ist für unveränderte Metadaten idempotent.
- AL Compile/Cop, Architektur-Gate und Pilot-E2E-Gate sind grün.

## 7. Verbleibende P0-Gates für bis zu zehn Pilotkunden

| Gate | Verantwortlich | Aufwand | Erfolgskriterium |
| --- | --- | ---: | --- |
| PROD-Deployment 1.0.2.20 attestieren | Daniel/Codex | 1–2 h | Commit, Version, Health und Smoke-Test dokumentiert |
| Backup und Restore | Daniel/Codex | 0,5–1 d | Datenbank aus Backup erfolgreich in isolierter Umgebung wiederhergestellt |
| Alerting | Daniel/Codex | 0,5 d | API-, DB-, Deployment- und Scanfehler lösen Alarm aus |
| 72h Scheduler-Soak | Daniel | 3 d Beobachtungszeit | mehrere geplante Scans ohne Ausfall/Duplikat |
| 10-Tenant-Lasttest | Codex | 0,5–1 d | definierte SLOs ohne Datenvermischung oder Fehler erfüllt |
| Rollen-/Login-/Mail-E2E | Daniel/Codex | 0,5–1 d | Einladung, Login, Sperrung, Reset und Mailzustellung PASS |
| Pilotunterlagen | Daniel/Codex | 1–2 d | Installation, Onboarding, Support, Datenschutz und Abnahme vollständig |
| Incident-/Supportplan | Daniel | 0,5 d | Ansprechpartner, Zeiten, Eskalation und Kundenkommunikation festgelegt |

## 8. Finale Readiness-Einschätzung

BCSentinel ist nicht mehr in einem experimentellen Zustand. Der Kernnutzen – Business-Central-Daten prüfen, Score berechnen, Findings und finanzielle Wirkung darstellen, Reports erzeugen sowie manuelle und geplante Monitoring-Läufe ausführen – ist real funktionsfähig.

Die aktuelle Empfehlung lautet:

> **Mit einem bis maximal drei aktiv betreuten Pilotkunden starten, parallel die Betriebs- und Supportgates schließen und erst danach auf zehn Kunden erweitern.**

Die Produkt-Readiness für diesen kontrollierten Start liegt bei **85 %**. Die Readiness für zehn gleichzeitig betreute Pilotkunden liegt bei **74 %**.
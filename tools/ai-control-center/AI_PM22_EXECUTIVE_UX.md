# AI-PM 2.2 – Executive UX / Information Architecture

## Basis, Ziel und Scope

Die vom Betreiber am 12.11.2026 übermittelte Bildschirmaufnahme zeigt ein umfangreiches AI-PM-2.1-Dashboard mit viel scrollbarer Evidenz und mehreren nicht direkt vergleichbaren Fortschrittszahlen. Der gewählte erste AI-PM-2.2-Inkrement ist **rein frontendseitig** und **read-only**:

- **Executive-Überblick „above the fold“**: vier explizit getrennte Kennzahlen (technische Planstunden, historische Aufgaben-Gates (Excel-Markierungen, keine unabhängige Abnahme), historische qualitative Gesamtprojektschätzung, offene kuratierte P0-Kriterien); globaler NO-GO-Hinweis.
- **Manueller nächster Review** aus `ai_pm_brief.recommendation` (kein Agentenauftrag) und maximal fünf kuratierte P0-Aufgaben aus `blocker_plan.items`; fehlende Daten ergeben „Nicht verfügbar“, keine 0-%-Erfindung.
- **Zeitstempel/Quellstatus** und eindeutige Hinweise, dass GitHub-PR-Metadaten und Excel-Häkchen keine CI-/BC-Laufzeit-/Go-Live-Abnahmen ersetzen.
- **Vollständige bisherige Detailansichten** unter nativer, zugänglicher `<details>`-Disclosure: Readiness/Grafiken, Arbeits- und Evidence-Tabellen, Agenten-Kontrollbereich und GitHub-PRs bleiben im HTML und werden weiter durch den unveränderten Snapshot-Reload gerendert.
- Responsive Styles im bestehenden Light-Design; keine neuen Farbmodi, externe Frontend-Abhängigkeiten, neuen API-Schreibpfade, LLM- oder Kostenintegration.

## Datenquelle und epistemische Grenzen

Das Frontend liest weiterhin einmalig `GET /api/snapshot` je Aktualisierung (Basic Auth, no-store). Es gibt **keinen zweiten Fetch** für die Executive-Ebene, keine neue DB-Mutation oder externe API. Qualitative Gesamtschätzung wird nicht mit technischer Fiverr-Readiness verrechnet. Das manuell kuratierte Abhängigkeitsmodell umfasst nur 15 von 61 Fiverr-Aufgaben; die Reihenfolge ist keine belastbare globale Priorisierung. Es wird kein angeblicher Projekt-Go-Live-Termin und keine agentische Arbeitsausführung abgeleitet.

Bei fehlender oder fehlerhafter Quelle wird kein Success-Badge oder erfundener Prozentwert gezeigt. Alle dynamischen Inhalte verwenden `textContent`, damit GitHub-/Workbook-Daten nicht in HTML interpretiert werden.

## Security und QA

- `executive.js` wird ausschließlich hinter demselben Basic-Auth-Handler wie Dashboard/CSS/API ausgespielt und zusammen mit `index.html` im Docker-Image gepackt.
- `test_http_security.py` prüft neu den 401/200-Vertrag des JS-Assets; `test_executive_view.py` bewahrt den Detail-/Evidence-Bereich und Read-only-Vertrag; GitHub-CI prüft JS-Syntax zusätzlich via Node.
- PR als **Draft gegen den AI-PM-2.1-MVP-Branch**, nicht gegen PROD/main: keine Merge-/Deployment-Freigabe, keine Containeränderung oder Berührung des laufenden OneDrive-systemd-Timers.

## Verbleibende Abnahme

1. CI am finalen SHA PASS.
2. Lokale/browserseitige visuelle Abnahme bei 1440 px, 1024 px und Mobile; Open-/Close-Verhalten der Details sowie Fokusnavigation und CSS-Kontrast überprüfen.
3. DEV-only **separaten** Dashboard-Container mit erhaltenem lokalem Port-Override, Backup/Sync unverändert; Auth-/Quellstatus-/NO-GO-Safety-Prüfung.
4. Feedback zum Executive-Layout einarbeiten, anschließend weitere 2.2-Abschnitte: eigene Evidence-Filter/Detailansichten, PR-Deduplikation, Agenda-Status und Team-Aufgabenplanung (ohne Ausführung).

**Status:** Erster UI-Codekandidat, nicht abgenommen. Die BCSentinel-/Fiverr-Produktfreigabe bleibt global NO_GO.

## Desktop-Triage – Folgeinkrement

Das Executive-Dashboard enthält zwei getrennte, filterbare Listen: **kuratierte Sprint-Evidence** und **offene GitHub-Pull-Requests**. Suche nach Sprint/PR/Titel, Filter für Aufgaben oder PRs, Begrenzung auf 5/10/25/alle Einträge. Wiederholte Sprint-IDs werden mit deduplizierten Quellen gesammelt; PRs werden ausschließlich pro Repository und PR-Nummer dedupliziert. Keine heuristische oder automatische Zuordnung von PRs zu Aufgaben und keine Freigaben.

Nur der bereits geladene API-Snapshot wird dargestellt; alle dynamischen Strings werden über `textContent` gesetzt. Externe Links werden auf HTTPS-GitHub-Pull-Requests oder Issues der beiden BCSentinel-Repositories eingeschränkt. Fehlende oder unvollständige GitHub-Daten werden gekennzeichnet und nicht als „keine offenen PRs“ ausgegeben. Die ursprünglichen vollständigen Tabellen und Detaildaten bleiben unverändert erreichbar.

**Betreiberentscheidung:** ausschließlich Desktop-Abnahme; Mobile-/Tablet-QA ist N/A. Die bestehende responsive CSS-Basis bleibt erhalten. Die letzte Dashboard-Korrektur heißt „Historische Aufgaben-Gates“; Excel-Markierungen sind keine unabhängige DEV-/Go-Live-Abnahme.

**Noch offen:** aktualisiertes Preview-Image ausschließlich für Port 8093 bauen, visuelle Desktop-Prüfung mit authentifiziertem Zugriff und echter Filtereingabe; danach Betreiberabnahme. Bestehendes Dashboard 8092, Host-Backups und Produktumgebungen nicht ändern.

## Evidence-Synchronisierung 12.11.2026 – AI-PM 2.2

**Scope:** Reviewstatus der bestehenden 15 kuratierten Fiverr-Aufgaben auf den Stand vom 12.11.2026 gebracht. Die ursprünglichen 61 Fiverr- und 24 SaaS-Excel-Aufgaben, importierten 2/2-Häkchen und die unveränderliche Excel-SHA bleiben unangetastet. Das ist keine neue Excel-/SQLite-Importversion, keine manuelle Gate-Abnahme und keine Fiverr-Freigabe.

### Sichtbare Änderungen im Dashboard

- Der Executive-Header zeigt jetzt neben dem Live-Snapshot-Zeitpunkt einen ausdrücklich eigenständigen Sprint-Evidence-Reviewstand: 2026-11-12; ein neuer Live-Snapshot behauptet keinen neuen fachlichen Review.
- Die filterbaren Sprint-Evidence-Karten zeigen die aktualisierten Kuratierungen zu 1.03, 2.01, 3.02, 3.03, 3.04, 4.01, 6.02 und 7.03. Die GitHub-PR-Liste bleibt eine separat live geladene Datenquelle und zeigt eine Warnung bei unvollständigen Quellen.
- **3.02:** Full-v6 auf echtem Hetzner-Host als isolierter 127.0.0.1:3001-Container erfolgreich geprüft: HTTP 200 für fünf Routen, HTML-Assets/PNG 200, alte Website/Overview im Alt-/Neu-Vergleich unverändert. Operator-Log: tatsächlicher Container-Commit 01b15b9ab6dc. Neuerer PR #13 CI-Stand 60af4902a294 mit 243 Tests und isolierter Asset-Byteprüfung erfolgreich – nicht als auf dem Host deployed markieren.
- **1.03:** BC Extension 1.0.2.59 in Draft PR #168 hat AL-Compile bestanden. In-place-Upgrade/Non-SUPER und reale BC27-Runtime bleiben ausstehend.
- **2.01/2.02:** 199-Check-Lifecycle und Provenienz bleiben Code-/Teilkandidaten, reale BC27-Check-/Datensatz-Evidence weiter offen.
- **4.01:** Freigabe des Access-v2-Vertrags blockiert durch Legacy Quick/7-Tage-Verträge gegenüber Full14/Renewal-Target.
- **6.02/7.03:** redaktionell fertig, aber kein Website-/Fiverr-Editor-/Kunden-E2E-GO. Finale Fiverr-Landingpage fehlt.
- **AI-PM 2.2:** Source/CI ist kein Nachweis für ein laufendes Preview auf Port 8093 oder ein aktualisiertes bestehendes Control Center auf Port 8092.
- **Fiverr Scope:** Tenant-basiertes kundenseitiges Overview-Dashboard bleibt erhalten, gehört aber nicht zum ersten Fiverr-Go-Live.

### CI-/Governance-Schutz

test_ai_pm22_evidence_sync.py prüft ursprüngliche SHA, 61+24 Aufgaben, 2/2 historische Häkchen, den separaten Reviewzeitpunkt, 15 unverändert kuratierte Aufgaben, Full-v6-Teilstadium, den Unterschied zwischen Host- und CI-Commit, und dass keine Deployment-/Go-Live-/Agenten-Gates automatisch geändert werden. Der alte Staleness-Test berechnet jetzt das tatsächliche Alter ab reviewed_at statt einer fest eingebauten Anzahl Tage.

Die Felder observed_gates dokumentieren geprüfte/berichtete Fakten, werden aber nicht als Berechtigungen oder Release-Abnahmen verwendet. Operator-Daten sind mit source_kind=operator_logs_plus_github_ci versehen; ein aktueller lokaler Server-API-Abruf von 8092/8093 wurde in dieser Sitzung nicht ausgeführt.

### Offen für isolierten Browser-Preview auf 8093

1. Existierende Host-Compose-Umgebung und Zustand der zwei SQLite-Datenbanken read-only prüfen; keine Reimporte, keine DB-Datei per cp aus laufender WAL-DB kopieren.
2. Separaten Preview-Container mit eigenem Namen/Loopback-Port und separater Sicherung oder read-only DB-Kopie starten. Nie bestehenden 8092-Container, ai-pm-sync, .env, systemd-Backup-Timer, produktive Container/Netzwerke oder Datenbankvolumes ändern.
3. Port-8093-Smoketest mit 401 ohne Auth, Login über SSH-Tunnel, /api/snapshot mit sprint_evidence.reviewed_at=2026-11-12, 15 kuratierten Aufgaben, originalen Excel-Gates, NO_GO und 0 aktiven Agenten. Filter für 3.02, 6.02, 7.03 und PR #13/#168 manuell prüfen.
4. Danach Betreiberfreigabe für späteres 8092-Update gesondert einholen. Weiterhin kein Merge, kein PROD, kein Go-Live.

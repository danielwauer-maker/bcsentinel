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

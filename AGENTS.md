# BCSentinel Codex Instructions

## Scope

- BCSentinel ist eine Microsoft-Dynamics-365-Business-Central-Extension mit FastAPI-/PostgreSQL-Backend und Executive Reporting.
- Änderungen minimal, nachvollziehbar und sprintbezogen halten. Vor Neuentwicklung nach bestehender Implementierung suchen und vorhandenen Code erweitern, statt parallele Ersatzmodule zu bauen.

## Repository safety

- Keine Secrets, Tokens, Passwörter oder Zugangsdaten committen oder im Chat ausgeben; `.env`-Dateien niemals vollständig anzeigen.
- Unversionierte ZIP-, APP-, PDF- und Buildartefakte nicht verändern oder löschen. Generierte AL-Workspaces gehören ausschließlich unter `.build/bc-extension/<Profil>`.
- Keine Produktivumgebung und keine destruktiven Datenbank- oder Docker-Aktionen ohne ausdrückliche Freigabe verändern.
- Keine Commits erstellen, außer der Benutzer verlangt es ausdrücklich.

## Python, backend, and PostgreSQL

- Für lokale Python-Kommandos ausschließlich `backend\.venv\Scripts\python.exe` verwenden; Tests aus `backend` über die bestehende `pytest.ini` ausführen.
- PostgreSQL-spezifische Tests nicht durch SQLite ersetzen. Fehlt lokales `psql`, den Client im laufenden PostgreSQL-Container verwenden.
- Vor schreibendem SQL Datenbank und Umgebung eindeutig als Testumgebung bestätigen; keine produktiven Datenbanken verändern.
- Migrationen mit Upgrade-/Downgrade-/Upgrade-Nachweis testen. API-Kompatibilität und ältere Payloads erhalten.

## Business Central / AL

- Vor Änderungen den vollständigen AL-Objektbestand durchsuchen. Objekt-IDs und `app.json` nur mit ausdrücklichem Sprintgrund ändern.
- Buildworkspaces mit `bc-extension/scripts/New-BCBuildWorkspace.ps1` außerhalb des AL-Projektstamms erstellen; Source-Uniqueness und vorhandene GL-Vertragsskripte prüfen.
- CodeCop und PerTenantExtensionCop berücksichtigen. Die bekannte AppSourceCop-Baseline (3× AS0051, 1× AS0084, 1× AS0092) von neu verursachten Meldungen trennen.
- Bei neuen sichtbaren Texten DE-/EN-XLIFF pflegen. Keine `SUPER`-Abhängigkeit als Lösung für Berechtigungsprobleme verwenden.

## Tests and reports

- Erst fokussierte Tests, danach relevante Regression ausführen. `PASS`, `FAIL`, `SKIP` und `BLOCKED` getrennt berichten.
- Fehlende echte BC-Runtime-Tests nie als bestanden darstellen. Testbeweise mit repository-relativen Pfaden dokumentieren.
- Bei Fehlern zuerst reproduzieren, dann minimal beheben und erneut testen.
- Executive Reports mit echtem Chromium prüfen: Seitenzahl, Überläufe, Footer, Sprache und große Zahlen. Bestehendes Layout nicht ohne Anforderung neu gestalten.

## Git and communication

- Vor und nach Arbeiten `git status --short` und `git diff --check` ausführen. Scope-fremde oder vorhandene Benutzeränderungen nicht zurücksetzen; untracked Dateien nicht allein wegen ihres Status löschen.
- Am Ende Änderungen, Tests, Blocker und manuelle Restschritte nennen. Keine GO-Freigabe erteilen, solange Sandbox-, Berechtigungs- oder Upgrade-Gates offen sind.

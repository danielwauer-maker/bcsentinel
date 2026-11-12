# AI-PM 2.3 – Projektmediathek (Draft, read-only)

## Zweck und Umfang

Separate Desktop-Seite unter `/media.html` (Navigation: Dashboard / Team / Mediathek).
Das Inventar listet Image/Graphic, PDF, Excel/CSV sowie DOCX/PPTX-Dateien aus:
- `bcsentinel/main` (Core-Repo, veröffentlichter Git-Branch, **nicht PROD**)
- `bcsentinel-frontend/main` (Frontend main, **nicht deployter Zustand**)
- `bcsentinel-frontend/fix/dev-v6-main-safe-integration-20261112` (Frontend Draft PR #13)

Diese Ref-Liste ist bewusst allowlisted. Bestand im Draft ist kein Beleg für die tatsächliche Nutzung in DEV oder PROD. Die aktuelle Nennung von Brand-Logo-PNGs im Draft darf nicht als installierte Landing-/Report-Integration interpretiert werden.

## Funktionen
- Authentifiziertes, schreibgeschütztes Asset-Inventar und format-/quellenübergreifende Filter/Suche.
- Bildvorschau über dieselbe Basic Auth: PNG, JPEG, WebP, GIF, SVG; PDF separat im Browser unter geschütztem Endpunkt, XLSX/CSV als gekürzte Vorschau der ersten 8 Zeilen/Spalten (maximal fünf Sheets).
- GitHub-Links auf konkrete Dateien (Branch-Ref); Tree-SHA je Repository/Branch, Blob-SHA und Quelle je Datei.
- Verwendungsnachweise nur mit **nachweisbaren Code-Imports** (derzeit: `hero-mountains.jpg` in den drei separat überprüften Frontend-Draft-Dateien). Alle anderen Dateien mit explizitem `Keine belastbare Verwendungsstelle nachgewiesen`. Keine fiktiven Einsatzzwecke oder Schätzung anhand bloßer Dateinamen.
- Das Inventar wird beim Seitenaufruf/Refresh neu über GitHub bezogen und für höchstens zehn Minuten pro Repository/Branch im App-Prozess zwischengespeichert. Fehlende Tokens, zu große Dateien und unvollständige GitHub-Trees werden klar gemeldet.

## Sicherheitsgrenzen
- HTTP-Handler prüft Basic Auth vor sämtlichen `/media*`-Routen.
- Bei binären Vorschauen GitHub-Git-Blob nur für Dateiidentitäten, die in einem zuvor validierten erlaubten GitHub-Tree mit SHA und Größenlimit (6 MB) auftauchen.
- Kein allgemeiner URL-Proxy, keine freien Repo/Ref-/Pfadparameter, keine Up-/Downloads in Host-Verzeichnisse, keine schreibenden Endpunkte.
- Einzelne GitHub-Dateien über 6 MB können in GitHub geöffnet, aber nicht intern visualisiert werden. Excel/VBA-Makros werden nicht ausgeführt, PDFs werden nur als getrennte authentifizierte Ressource ausgeliefert.
- Neue Bibliotheksseite darf niemals eine agentische Aktion, Go-Live-Gate oder den historischen Excel-Tracker verändern.

## Bekannte Grenzen / spätere Erweiterungen
1. Die automatisierte Verwendungsanalyse von **allen** Source-Code-Dateien ist noch nicht enthalten. Der MVP dokumentiert nur geprüfte Importe und kennzeichnet andere Assets als **nicht verifiziert**. Ein zentraler, CI-generierter, SHA-gepinnter Referenzindex wäre die robuste Folgeausbaustufe.
2. PDF- und Office-Dateien werden per GitHub-Link bereitgestellt; ausschließlich XLSX/CSV bekommen tabellarische Inline-Vorschau. PDF-Bildseiten/-Thumbnails, PPTX-Folien- und DOCX-Seitendarstellung sind noch nicht verfügbar.
3. Binärassets sind nur aus allowlisteten GitHub-Refs aufgelistet, nicht aus Lovable, privaten Drives, lokalen Uploads, Container-Images oder einer Live-Website. Eine künftig gewünschte DEV/PROD-Verwendungszuordnung setzt einen separat bestätigten Deployment-Manifest-/SHA-Abgleich voraus.
4. Die Größe einzelner Repositories und Rate-Limits können die Laufzeit beeinflussen. Verfügbarkeitsfehler niemals als leeres, vollständiges Inventar ausgeben.

## Abnahme
- Draft PR gegen `feature/ai-pm22-executive-dashboard` (stacked), **kein automatischer Merge**.
- GitHub CI und Unit-/Security-Tests, JS-Syntax; danach isolierte Vorschau **neuer** Container/Port ohne Änderung von 8092/SQLite/Backups/Sync.
- Manuelle Desktop-QA: Logo-PNGs, SVG, PDF-Link, Tabellenstatus, Typ- und Repo-Filter, Deep-links; aktuelle GitHub-Draft-/main-Unterscheidung; 401 ohne Auth; kontrollierter Offline-Status.
- Nur nach separater Betreiberabnahme auf 8092 übernehmen. Erstes Fiverr-Go-Live weiterhin NO_GO.

## Regel für alle nächsten Sprints
Wer Assets neu hinzufügt oder ihren Einsatzort ändert, muss den GitHub-Pfad, die Branch-/Commit-Provenienz, die belegte Verwendung (Source-Import oder Deployment-Mapping) und die inhaltliche Rolle in der Mediathek dokumentieren. Keine ungeprüfte Behauptung von Live-Einbindung.

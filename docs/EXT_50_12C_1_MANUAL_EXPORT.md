> Superseded runtime status: the real SaaS export is now reconciled in [EXT-50-12C.2](EXT_50_12C_RUNTIME_DETECTION_RECONCILIATION.md). Historical evidence below is retained. The 165 runtime check count is correct; intermediate counter drift is overwritten.

# EXT-50-12C.1 — Manueller, lesender Runtime-Export

Status: **MANUAL_RUNTIME_EXPORT_REQUIRED**. Keine LARGE-Freigabe.

## Installierbares Paket

- App: **BCSentinel Runtime Evidence QA 1.0.0.0**
- Datei: `.build/bc-extension/DiagnosticsQA/BCSentinel.Runtime.Evidence.QA.1.0.0.0.app`
  relativ zum neuen Sprint-Worktree `.build/ext-50-12c-runtime-worktree`.
- SHA256: `ff3bc085726c4fd945c74911ccec31f19883539128e922c5c7f3a7e1011b9c46`
- Abhängigkeiten: BCSentinel **mindestens 1.0.2.20** (vorhandene 1.0.2.21 geeignet),
  BCSentinel Performance QA **mindestens 1.0.0.1**, BC27 / Runtime 16.
- Neue, separate App-ID `9f9817da-79ae-4ac6-ae84-b7372899b541`; reservierter QA-Bereich
  53450–53459 für diesen Sprint. Keine bestehenden Produkt-/Generator-Objekt-IDs geändert.
- Enthält ausschließlich eine Export-Codeunit, eine Seite und eine Leseberechtigung.
  Keine Tabellen, Install-/Upgrade-Trigger, Event-Subscriber, HTTP- oder Scan-Aufrufe.
  Installation registriert lediglich die neuen Erweiterungsobjekte; der Export schreibt
  keine Geschäfts-, Generator-, Setup-, Exception- oder Scan-Datensätze.

## Genau diese Schritte in BC

1. Die bestehende **BC27 SaaS-Sandbox** öffnen und Firma **BCS-PERF-DEV** auswählen.
   In der Erweiterungsverwaltung ausschließlich das oben genannte **Runtime Evidence QA**-
   Paket hochladen/installieren. Weder BCSentinel noch den Generator neu installieren,
   ersetzen, zurücksetzen oder einen Lauf starten. Falls eine Mindestabhängigkeit fehlt:
   stoppen und die Versionsmeldung mitteilen.
2. Dem ausführenden Benutzer den neuen Berechtigungssatz **BCR EVIDENCE** für diese Firma
   zuweisen. Vorhandene normale BC-Anmelde-/Systemberechtigungen bleiben erforderlich.
   **Kein SUPER erforderlich oder als Workaround vorgesehen.** Bei einer Berechtigungsfehlermeldung
   deren Objektnummer mitteilen; keine Daten oder Tokens exportieren, um den Fehler zu umgehen.
3. Über **Alt+Q** nach **BCSentinel Laufzeitnachweis** suchen
   (englisch: **BCSentinel Runtime Evidence**).
4. **DEV-Nachweis herunterladen** wählen (englisch: **Download DEV evidence**).
   Die Datei **BCSentinel-DEV-Run1-evidence.json** speichern.
5. Genau diese JSON-Datei hier zur Auswertung bereitstellen. Danach keine weiteren
   Scan-, Generator-, Recovery-, Cleanup- oder Korrekturaktionen ausführen.

Der Export ist absichtlich fest auf Firma BCS-PERF-DEV, Generatorlauf 1 und Scan
`RUN_20260916_000001_43F57A071BFF485BAF20C68FF578B` begrenzt. Außerhalb einer
SaaS-Sandbox oder bei nicht eindeutigem/abgeschlossenem Scan bricht er ab.
Die Generatorzähler müssen 6.000/2.000/12.000, Seed 5001, Rate 10 und 2.000 Szenarien sein.
Es werden keine Scan- oder Generatorläufe gestartet, auch nicht als Fallback.

## Was die JSON-Datei tatsächlich enthält

- Alle persistierten Zeilen aus **DH Deep Scan Finding** zum ausgewählten Run,
  unabhängig von der möglicherweise gruppierten Free-Scan-Oberfläche.
- BC Finding-ID, Run-ID, Check-ID, gespeicherter Titel, Modul/Kategorie, Severity,
  Affected Count und gespeicherter Zeilenimpact. Originalreihenfolge: Entry No. aufsteigend.
- Persistierte Run-Zähler, Modul-/Gesamtscores, Zeiten, Sync-Status, Gesamtimpact und Saving.
- Aktuelle Modulflags ausdrücklich als **aktueller Setupstand**, nicht als historischer Snapshot.
- Aktuell installierte Produkt-/Generatorversionen.
- Für die vier Generator-Szenarien: Ownership-Anzahl, tatsächlich passende Felder,
  ausgeschlossene Treffer, nicht dem Generatorlauf gehörende Treffer sowie fehlende oder
  seit Generierung geänderte Owned Records — jeweils nur als Zähler.
- Tabellen-/Feldzuordnung für die vier direkten Szenarien. Weitere Zuordnungen werden
  anschließend anhand des vorhandenen Quellkatalogs ergänzt, nicht erraten.

Keine API-/Execution-Tokens, Cookies, Tenant-Bindings, Kundennamen, Adressen, E-Mails,
Telefonnummern, Business-Record-IDs oder vollständigen Stammdatensätze werden exportiert.
Die ursprünglichen Duplicate-Gruppenwerte sind im Finding-Modell nicht gespeichert und
werden deshalb ausdrücklich als nicht verfügbar markiert. Der aggregierte Finding-Zähler
wird nicht fälschlich einem einzelnen Generator-Datensatz zugeordnet.

Wichtig: Die Feld-/Ownership-Auswertung ist ein lesender **aktueller** Zustand. Historische
Pre-Sync-Severities und Backend-Impact-Konfiguration sind damit noch nicht bewiesen.
Der Export enthält auch keine vorgetäuschte Backend-Inventarliste. Diese Unterschiede
bleiben in der anschließenden Reconciliation sichtbar.

## Lokal verifiziert / noch manuell offen

- BC27-Symbolkompilierung mit AL Compiler 17.0.34.45391: **PASS**.
- CodeCop / PerTenantExtensionCop: **0 Fehler, 0 Warnungen**; drei Namespace-Hinweise AA0247.
- DE-/EN-XLIFF: jeweils 12 vollständige Einträge; beide im APP-Paket enthalten.
- Fokus-Suite: **37 PASS, 3 XFAIL** für die bereits bekannten Produkt-Quellbefunde.
- Sicherheitsverträge: ausschließlich Tabellenrecht R, keine Mutations-/Netzwerkaufrufe,
  feste Sandbox-/Firmen-/Run-Guards, persistierte Einzelzeilen statt Free-UI-Aggregaten.
- APP-Manifest, Abhängigkeiten, Übersetzungen und SHA256 wurden geprüft.
- **Noch nicht ausgeführt:** Installation und Export in deiner SaaS-Sandbox. Ein Compilerlauf
  beweist weder die echten 95 Zeilen noch deine Benutzerrechte. Dieser manuelle Schritt
  ist der nächste Gate, kein bereits bestandener Runtime-Test.

## Reproduzierbarer Build und spätere Auswertung

Der vorhandene `bc-extension/scripts/New-BCBuildWorkspace.ps1` besitzt jetzt das separate
Profil `DiagnosticsQA`. Mit `-SymbolSourcePath` wird ein Verzeichnis mit unveränderten
BC27-Symbolen und den beiden Produkt-/Generator-Symbolpaketen angegeben. Ausgabe ausschließlich
unter `.build/bc-extension/DiagnosticsQA`, niemals im AL-Produktstamm. Compiler und beide
Cop-DLLs stammen aus der installierten Microsoft-AL-Erweiterung. Das neue Profil verändert
die bisherigen Buildprofile nicht. Vorhandene APP-/ZIP-Artefakte werden nicht gelöscht.

Nach Empfang der echten Datei kann ohne Veränderung des Originals ausgewertet werden:

```powershell
backend\.venv\Scripts\python.exe scripts/reconcile_ext_50_12c.py `
  --input quality/release/ext-50-12c-runtime-reported.json `
  --bc-export <Pfad-zur-BCSentinel-DEV-Run1-evidence.json> `
  --output <neue-lokale-Reconciliation-Datei.json>
```

Im separaten Worktree den absoluten Pfad zum bestehenden `backend\.venv\Scripts\python.exe`
des ursprünglichen Checkouts verwenden. Die Rohdatei wird nur gelesen; ihr SHA256 wird
mitprotokolliert. Fehlende Backend-/Scoring-Evidence bleibt BLOCKED, nicht stillschweigend PASS.

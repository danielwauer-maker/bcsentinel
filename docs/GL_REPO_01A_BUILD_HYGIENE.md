# GL-REPO-01A – AL Build Hygiene and Duplicate Source Prevention

Stand: 20. Juli 2026  
Branch: `staging`  
Ausgangscommit und lokaler Sicherheitstag `pre-repo-01a-build-hygiene`: `5b654f8ed22bf0f67fe7cd52d4540a884bbe72a6`

## Ergebnis

Die Root Cause ist bestätigt und behoben. Generierte vollständige AL-Quellbäume lagen unter `bc-extension/.build` und damit innerhalb des aktiven AL-Projektstamms. Nach der Bereinigung existiert unter `bc-extension` nur noch der kanonische Quellbaum `app/src`; neue Workspaces entstehen standardmäßig unter Repository-Root `.build/bc-extension/<Profile>`.

Der Sprint verändert keine AL-Fachlogik, keine Objektdeklaration, keine Objekt-ID, keine PermissionSet-Definition und keine Extension-Identität. Vorhandene, nicht zu REPO-01A gehörende UX02- und Backend-Arbeitskopien wurden nicht verworfen, gestasht oder überschrieben. Es wurde kein Commit erzeugt.

## Diagnose und Root Cause

| Befund | Vorher | Nachher |
|---|---:|---:|
| kanonische `.al` unter `bc-extension/app/src` | 84 Dateien / 88 Objekte | 84 Dateien / 88 Objekte |
| generierte `.al` unter `bc-extension/.build` | 246 Dateien / 256 Deklarationen | 0 |
| `app.json` unter `bc-extension` | 4, davon 3 generiert | 1 kanonisch |
| vollständige generierte `app/src`-Bäume | 3 | 0 |
| doppelte Gruppen nach Typ + ID | 88 | 0 |
| doppelte Gruppen nach Typ + Name | 88 | 0 |
| eigener BCSentinel-Symbolstand in `.alpackages` | 0 | 0 |

Ursprüngliche Quellkopien:

- `bc-extension/.build/ReleaseCloud/app/src` – 84 AL-Dateien
- `bc-extension/.build/P0E_N1_630d896/bc-extension/app/src` – 81 AL-Dateien
- `bc-extension/.build/P0E_N1_630d896/bc-extension/.build/ReleaseCloud/app/src` – 81 AL-Dateien

Die letzte Struktur belegt, dass die historische P0E-N-1-Arbeitskopie ihr eigenes `.build` erneut enthielt. Alle 256 generierten Deklarationen hatten anhand Typ + ID ein kanonisches Gegenstück; es gab kein ausschließlich im Build-Baum vorhandenes AL-Objekt. Beispiele für die jeweils vierfach sichtbaren Deklarationen waren Codeunit 53100 `DH API Client`, Page 53100 `DH Setup` und Table 53100 `DH Setup`.

Die vier Manifestpfade waren das kanonische `bc-extension/app.json` sowie je ein `app.json` in den drei oben genannten Workspaces. Alle trugen dieselbe App-ID `8c7f0f9c-0c1a-4a4e-9c6f-111111111111`; es bestand keine Selbstabhängigkeit. App-ID, Name `BCSentinel`, Publisher `BCSentinel Analytics - Daniel Wauer` und ID-Range `53100..53199` sind gegenüber dem Sicherheitstag unverändert.

Unter `bc-extension/.build` wurden vor dem Löschen 315 Dateien in 51 Verzeichnissen inventarisiert: 246 AL-Dateien, drei generierte `app.json`, mehrere kompilierte `.app`, ein N-1-ZIP, Release-Metadaten sowie Analyzer-/Hilfsartefakte. Top-Level waren `ReleaseCloud`, `P0E_N1_630d896`, `release`, elf ältere Buildpakete, das N-1-ZIP und `ux02-label-map.json`. Nach normalisierter Zielprüfung wurde ausschließlich `bc-extension/.build` entfernt; kanonische Quellen, Symbole, Übersetzungen, Dokumente und Umgebungsdateien blieben bestehen.

## Build- und Release-Skripte

`bc-extension/scripts/New-BCBuildWorkspace.ps1` ermittelt AL-Projekt- und Repository-Root unabhängig vom Aufrufverzeichnis. Der Standardoutput ist nun:

`<repository-root>/.build/bc-extension/<Profile>`

Vor jeder Verzeichniserzeugung oder Bereinigung normalisiert der Guard absolute Windows-Pfade und vergleicht sie case-insensitiv mit korrekter Separatorgrenze. Abgewiesen werden das AL-Projekt selbst, jeder Kindpfad – einschließlich `app` und `.alpackages` –, `..`-Varianten und jeder Output, der das Projekt als Kind enthalten würde. Es gibt kein stilles Fallback.

Die Kopie arbeitet als Allow-List: `app`, ausgewähltes Manifest als `app.json`, `app.ruleset.json`, `AppSourceCop.json`, `Translations`, benötigte `.alpackages`, `.vscode/settings.json` und nur für DevCloud `launch.json`. Repository, `.build`, `.git`, `.github`, Snapshots, Artefakte, Caches, virtuelle Umgebungen, ZIPs und bestehende APP-Pakete werden nicht als Projektbaum kopiert.

`scripts/New-P0EReleasePackage.ps1` verwendet ebenfalls Repository-Root `.build/bc-extension/...` und verweigert einen Release-Output innerhalb von `bc-extension`. Die Repository-Suche fand keinen eingecheckten separaten N-1-Workspace-Erzeuger; die historische Rekursion war ein generierter/manueller Vollbaum. Der verbleibende Release-Skriptablauf kopiert nur das kompilierte APP-Paket und eine feste Dokumentliste, nicht das AL-Projekt.

## Duplicate-Source-Guard

Neu ist `bc-extension/scripts/Test-ALSourceUniqueness.ps1`. Er prüft mit Exitcode 1 und Dateidetails:

- AL-Dateien unter `bc-extension/.build`
- zweite `app/src`-Bäume und verschachtelte `bc-extension`-Ordner
- zusätzliche `app.json` im Projekt-Unterbaum
- doppelte AL-Objekte nach Typ + ID sowie Typ + Name
- eigene BCSentinel-APP in `.alpackages`
- rekursive `.build`-Strukturen

Der Parser entfernt Block- und Zeilenkommentare vor der verankerten Objektdeklarationssuche und erfasst die geforderten Table-, Page-, Codeunit-, Enum-, Query-, Report-, PermissionSet-, ControlAddIn-, XmlPort- und Interface-Typen einschließlich Extensions. Procedures, Captions und Enum Values werden nicht als Objekte interpretiert.

Ergebnisse:

- Vor Bereinigung: **FAIL**, Exit 1, 430 Verstöße.
- Nach Bereinigung: **PASS**, 88 Deklarationen, ein kanonischer Source-Root.
- Temporäre doppelte Codeunit 53100: **FAIL**, exakt zwei Kollisionen (Typ + ID, Typ + Name).
- Nach vollständiger Entfernung der Testdatei und ihres Ordners: **PASS**.

## Git-Hygiene

Root `.gitignore` enthält nun zusätzlich `/.build/`; bereits vorhanden sind `bc-extension/.build/`, `.snapshots/`, `artifacts/`, `bc-extension/*.app` und `*.app`. `git ls-files` meldete keine getrackten Dateien aus `bc-extension/.build`, `.alpackages`, `.snapshots`, `artifacts` oder APP-Pakete. Daher war kein `git rm --cached` erforderlich.

## Verifikation

| Prüfung | Ergebnis |
|---|---|
| Dateisystem-Invarianten | PASS: kein `bc-extension/.build`, ein `app.json`, ein `app/src` |
| Codeunit/Page/Table 53100 | PASS: je Typ exakt eine Deklaration |
| OutputPath-Negativfälle | PASS: Projekt, `app`, `.alpackages`, normalisiertes `..` und Projektancestor jeweils Exit 1, keine Anlage |
| frischer ReleaseCloud-Workspace | PASS: `.build/bc-extension/ReleaseCloud`, 84 AL, ein Manifest, keine Verschachtelung |
| ReleaseCloud Compile | PASS, AL Compiler 17.0.34.45391, 84 Dateien, Exit 0 |
| Buildartefakt | `BCSentinel.app`, 857.967 Bytes, SHA-256 `E5829625990F080F83FD9846DC1B4E0632DC45011CAA7AA3ACFED572BC97275E` |
| CodeCop + PerTenantExtensionCop | PASS/Exit 0; 335 bestehende Hinweise, keine Build-Fehler |
| XLF Parsing | PASS |
| JSON Parsing | PASS |
| Workspace-vs.-Canonical-Source-Hashdiff | PASS, 0 Abweichungen |
| Python `compileall` | PASS mit gebündelter Laufzeit; direkter `python`-Aufruf war mangels PATH nicht verfügbar und nicht blockierend |
| vollständige Backend-Suite | PASS: 258 bestanden, 6 übersprungen, 40 bekannte Deprecation-Warnungen, Exit 0 |
| `git diff --check` | PASS, Exit 0; nur nicht blockierende LF/CRLF-Hinweise |

Der erste rein diagnostische PowerShell-Einzeiler scheiterte an Shell-Quoting und wurde ohne Dateisystemänderung mit quoting-sicherer Regex wiederholt. Der direkte Host-Python-Aufruf war nicht verfügbar; die gebündelte Python-Laufzeit lieferte `compileall` Exit 0. Beide Fehlschläge waren nicht blockierend und hatten eine gleichwertige alternative Prüfmethode.

AppSourceCop wurde ausschließlich als Baseline ausgeführt und endete erwartungsgemäß mit Exit 1: drei `AS0051` für EULA, Logo und Context-Sensitive-Help-URL, ein `AS0084` für die PTE-ID-Range sowie ein `AS0092`-Telemetriehinweis. Diese vorbestehenden AppSource-Gaps gehören nicht zu REPO-01A; Signierung und reale Marketplace-Prüfung bleiben ebenfalls offen.

## Business-Central-Sandbox und manuelle Abnahme

Publish/Install in einer echten BC-Sandbox ist **BLOCKED**, weil in diesem Lauf kein Sandboxzugriff vorlag. Es ist ausdrücklich kein PASS.

1. VS Code schließen oder `Developer: Reload Window` ausführen.
2. Im Ordner `bc-extension` `AL: Download Symbols` ausführen.
3. Das normale Package erneut erstellen; der automatisierte Releasepfad liegt unter `.build/bc-extension/ReleaseCloud`.
4. Prüfen, dass keine Meldung `is already declared` und keine mehrdeutige `BCSentinel`-Referenz erscheint.
5. Noch nichts in Business Central deinstallieren.
6. Keine Objekt-IDs ändern.
7. Danach Publish/Install und Upgrade separat in der vorgesehenen Sandbox protokollieren.

## Rollback

Der Sicherheitstag zeigt auf den unveränderten Ausgangscommit. Da vorbestehende uncommittete UX02-Arbeit vorhanden ist, darf kein pauschales Reset/Restore des Working Trees erfolgen. Für einen gezielten Rollback sind nur die REPO-01A-Dateien einzeln zurückzunehmen: Workspace-/Release-Skript, README und `.gitignore`; das neue Guard-Skript und die REPO-01A-Dokumentationsabschnitte sind zu entfernen. Den gelöschten alten `bc-extension/.build`-Baum nicht wiederherstellen – er enthielt ausschließlich generierte, ignorierte Artefakte. Benötigte Pakete sind mit dem Buildskript im neuen externen Workspace neu zu erzeugen.

## Entscheidung

- Root Cause bestätigt: **Ja**
- Sprint abgeschlossen: **Ja**
- Duplicate-Object-Fehler ursächlich behoben: **Ja**
- Buildprozess dauerhaft abgesichert: **Ja, auf Repository-/Skriptebene**
- Regressionen festgestellt: **Nein**
- Bereit für REPO-01B: **Ja**
- Produkt-/Sandbox-Gate: **unverändert NO-GO/BLOCKED; nicht Gegenstand dieses Hygiene-Sprints**

Commit-Vorschlag: `fix(build): prevent recursive AL source duplication`

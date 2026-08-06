# EXT-50-01 – Release-Baseline für 50-Kunden-Readiness

**Stand:** 2026-08-06  
**Basisbranch:** `staging`  
**Extension-Baseline:** `1.0.2.20`  
**Ziel:** Einen einzigen, reproduzierbaren und maschinenlesbar geprüften Ausgangsstand für alle weiteren Extension-Sprints festlegen.

## 1. Ergebnis

EXT-50-01 friert noch keinen produktiven Release ein. Der Sprint stellt die technische Baseline her, auf der frische Installation, Upgrade-Matrix, Rollenprüfung, Recovery, Last- und Soak-Tests reproduzierbar ausgeführt werden können.

Festgelegt sind:

- Extension-Name und App-ID,
- Publisher,
- Version `1.0.2.20`,
- BC-27-Plattform und -Application,
- Runtime 16.0,
- Objektbereich 53100–53201,
- PostgreSQL/Alembic als Backend-Schemaweg,
- verpflichtende CI-Gates,
- noch offene manuelle Release-Gates.

## 2. Behobener Baseline-Drift

Vor EXT-50-01 waren die beiden AL-Manifeste nicht synchron:

- `bc-extension/app.json`: Version 1.0.2.20, Objektbereich bis 53201,
- `bc-extension/app.cloud.json`: Version 1.0.2.7, Objektbereich bis 53199.

Der Cloud-Manifeststand wurde auf die bestehende freigegebene Extension-Baseline 1.0.2.20 ausgerichtet. Ein Contract-Test verhindert künftig erneuten Drift in releasekritischen Feldern.

## 3. Repository-Artefakte

| Artefakt | Zweck |
| --- | --- |
| `quality/release/ext-50-01-release-baseline.json` | Maschinenlesbare Release-Baseline |
| `backend/tests/test_ext_50_01_release_baseline_contract.py` | Manifest- und Baseline-Vertrag |
| `.github/workflows/ext-50-01-release-baseline.yml` | Eigenes CI-Gate und Evidence-Artefakt |
| `docs/EXT_50_01_RELEASE_BASELINE.md` | Audit- und Arbeitsnachweis |

## 4. Automatische Abnahmekriterien

Der Sprint ist repositoryseitig PASS, wenn:

1. `app.json` und `app.cloud.json` in allen releasekritischen Feldern übereinstimmen,
2. Version, Plattform, Application und Runtime der definierten Baseline entsprechen,
3. das maschinenlesbare Release-Manifest vollständig und konsistent ist,
4. offene manuelle Gates ausdrücklich benannt sind,
5. der bestehende BC-27-Compile-/Cop-Lauf und die Pilot-Regression auf dem PR-Head grün sind.

## 5. Noch manuell offen

Vor EXT-50-02 muss Daniel nur noch das grüne Build-Artefakt sichern:

1. GitHub Actions öffnen.
2. Den grünen Lauf `BC AL Compile and Cop Gate` des finalen EXT-50-01-PR-Heads öffnen.
3. Das veröffentlichte APP-Artefakt herunterladen.
4. Nur das APP-Paket aus diesem grünen Lauf in einen neuen Freigabeordner kopieren, zum Beispiel:
   `BCSentinel-Releases/1.0.2.20-EXT-50-01/`.
5. Dateiname und SHA-256 dokumentieren.
6. Alte APP-Dateien nicht löschen, sondern außerhalb des Freigabeordners archivieren.

PowerShell für den Hash:

```powershell
Get-FileHash -Algorithm SHA256 .\BCSentinel*.app
```

Die Werte werden anschließend in die Release-Baseline übernommen. Bis dahin bleiben `file_name` und `sha256` absichtlich auf `PENDING_CI_ARTIFACT`.

## 6. Explizit nicht Bestandteil

- frische BC-Installation – EXT-50-02,
- Upgrade-Matrix – EXT-50-03,
- Dashboard-Redesign,
- Landingpage-Redesign,
- Self-Service-Checkout,
- AppSource-Einreichung,
- Produktionsfreigabe.

## 7. Status

**Aktueller Status:** `IMPLEMENTED_AWAITING_CI_AND_ARTIFACT_ARCHIVE`

Nach grünen PR-Gates und dokumentiertem APP-Dateinamen inklusive SHA-256 kann EXT-50-01 auf `VERIFIED_IN_CI / PASS` gesetzt werden.

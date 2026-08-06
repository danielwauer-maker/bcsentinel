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
- finaler APP-Dateiname und SHA-256,
- noch offene manuelle Release-Gates.

## 2. Behobener Baseline-Drift

Vor EXT-50-01 waren die beiden AL-Manifeste nicht synchron:

- `bc-extension/app.json`: Version 1.0.2.20, Objektbereich bis 53201,
- `bc-extension/app.cloud.json`: Version 1.0.2.7, Objektbereich bis 53199.

Der Cloud-Manifeststand wurde auf die bestehende freigegebene Extension-Baseline 1.0.2.20 ausgerichtet. Ein Contract-Test verhindert künftig erneuten Drift in releasekritischen Feldern.

## 3. Verifiziertes Build-Artefakt

- Workflow: `BC AL Compile and Cop Gate #60`
- Run-ID: `31081200637`
- Workflow-Artefakt: `bc-al-compile-output`
- Artifact-ID: `8960052092`
- APP-Dateiname: `BCSentinel Analytics - Daniel Wauer_BCSentinel_1.0.2.20.app`
- APP-SHA-256: `62a5a5d380008f3d212bbc2834429ad4b3f3d36787b4ee567b7e68a2f4e78756`
- Workflow-ZIP-Digest: `sha256:9522aa0f90c2ea5078f3592142aa473598e6dd83f96cfe8eb1421abbde22eea5`

## 4. Repository-Artefakte

| Artefakt | Zweck |
| --- | --- |
| `quality/release/ext-50-01-release-baseline.json` | Maschinenlesbare Release-Baseline |
| `backend/tests/test_ext_50_01_release_baseline_contract.py` | Manifest-, Artefakt- und Baseline-Vertrag |
| `.github/workflows/ext-50-01-release-baseline.yml` | Eigenes CI-Gate und Evidence-Artefakt |
| `docs/EXT_50_01_RELEASE_BASELINE.md` | Audit- und Arbeitsnachweis |

## 5. Automatische Abnahmekriterien

Der Sprint ist repositoryseitig PASS, wenn:

1. `app.json` und `app.cloud.json` in allen releasekritischen Feldern übereinstimmen,
2. Version, Plattform, Application und Runtime der definierten Baseline entsprechen,
3. das maschinenlesbare Release-Manifest vollständig und konsistent ist,
4. APP-Dateiname, Run-ID, Artifact-ID und SHA-256 verbindlich dokumentiert sind,
5. offene manuelle Gates ausdrücklich benannt sind,
6. BC-27-Compile-/Cop-Lauf, Pilot-Regression und EXT-50-01-Gate auf dem finalen PR-Head grün sind.

## 6. Für Daniel verbleibender Archivierungsschritt

Vor EXT-50-02 das grüne Build-Artefakt lokal sichern:

1. GitHub Actions öffnen.
2. `BC AL Compile and Cop Gate #60` öffnen.
3. Artefakt `bc-al-compile-output` herunterladen.
4. Die APP-Datei in folgenden Freigabeordner kopieren:
   `C:\Users\Daniel\Documents\BCSentinel-Releases\1.0.2.20-EXT-50-01\`
5. Den Hash lokal gegen den oben dokumentierten SHA-256 prüfen.
6. Alte APP-Dateien nicht löschen, sondern außerhalb dieses Freigabeordners archivieren.

```powershell
Get-FileHash -Algorithm SHA256 "C:\Users\Daniel\Documents\BCSentinel-Releases\1.0.2.20-EXT-50-01\BCSentinel Analytics - Daniel Wauer_BCSentinel_1.0.2.20.app"
```

## 7. Explizit nicht Bestandteil

- frische BC-Installation – EXT-50-02,
- Upgrade-Matrix – EXT-50-03,
- Dashboard-Redesign,
- Landingpage-Redesign,
- Self-Service-Checkout,
- AppSource-Einreichung,
- Produktionsfreigabe.

## 8. Status

**Aktueller Status:** `VERIFIED_IN_CI / PASS`

Die Repository-, Manifest-, Build- und Artefaktidentität von EXT-50-01 ist abgeschlossen. Die frische BC-Runtime-Installation folgt separat in EXT-50-02.

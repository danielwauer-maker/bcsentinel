# BCSentinel Upgrade Test Report

Stand: 20.07.2026

## Pakete

| Rolle | Quelle | Version | Ergebnis |
|---|---|---:|---|
| N-1 | Commit `630d896` | 1.0.2.6 | 81 Dateien kompiliert |
| Target | P0E-Arbeitsbaum auf `bb55119` | 1.0.2.7 | 84 Dateien kompiliert |

Der Versionsblocker gleicher N-1-/Targetversion wurde durch Erhöhung des Targets auf 1.0.2.7 behoben.

## Backendupgrade

Revision 0021 wurde mit anonymem Tenant, Kauf, verfügbarem Credit, Scan, Finding und historischem `running` Run aufgebaut. Upgrade über 0022, 0023 und 0024 war erfolgreich. Alle Datensätze blieben 1:1 erhalten; Identity-Felder blieben sicher `NULL`; Credit und Status wurden nicht umgedeutet.

## AL-Upgradelogik

`DH Upgrade` erstellt fehlendes Setup idempotent, erhält bestehende Daten, invalidiert alte positive Access-Caches und schreibt das Event `extension_upgraded`. Es gibt kein positives Backfill. `DH Install` initialisiert Setup und Defaults pro Company.

## BC-Sandboxresultat

Fresh Install, N-1-Installation, Testdatenanlage, Publish/Sync/Upgrade, Upgrade-Codeunit, Datenprüfung, Uninstall/Reinstall und Zeitmessung: **BLOCKED – keine BC-Sandbox verfügbar**.

Ein Compile ist kein Ersatz für den Runtime-Upgradebeweis. Customer-/Pilot-Gate bleibt geschlossen.


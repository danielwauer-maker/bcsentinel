# BCSentinel – DEV-first Entwicklungs- und Release-Regeln (2026-11-11)

**Status:** Vom Projekteigentümer für die laufende Test-/Entwicklungsphase bestätigt. Diese Regeln präzisieren das Master-Tracker-Handoff und ersetzen in der operativen Planung die Annahme, `main` sei die aktuelle Entwicklungsbasis.

## Autorität und Releasepfad

1. **DEV ist die aktuelle integrierte Test-Laufzeit**, jedoch nicht automatisch die neueste Source: neuere ungemergte PRs/Integrationsbranches sind stets ebenfalls zu prüfen. Zu Beginn eines Entwicklungsauftrags deployed Commit-SHA, Docker-Image-Digest, Migration-HEAD, Frontend-Commit, BC-App-Version und PR-HEADs feststellen, soweit Zugriff besteht. Bei fehlendem SSH/API-Evidence nicht so tun, als wäre DEV verifiziert.
2. `main` kann bis zum Launch veraltet sein. **Kein automatischer Rebase auf `main` als neueste Produktwahrheit**. Alter `main`-Produkttext (Quick, 7 Tage, 1.0.2.29) ist historisch und nicht ohne DEV-/neue PR-Verifikation als aktueller Bug zu behandeln.
3. Codex entwickelt auf **isolierten GitHub-Feature-Branches** mit Draft-PR, CI und Nachweisen am exakten SHA. Parallele Tasks 3B.01 (Check-Lifecycle) und 3B.02 (Provenienz) sollen die verifizierte neueste gemeinsame Integrationsbasis nutzen, Schnittstellenkonflikte offenlegen und anschließend kontrolliert zusammengeführt werden.
4. **Kein direktes Arbeiten/Pushen nach `main`, `staging`, `dev-acceptance`**. Der `deploy.yml`-Workflow auf `main` verwendet `dev-acceptance` für automatische DEV-Deployments; `workflow_dispatch` kann zielgerichtete Deployments auslösen. Keine unbeabsichtigten Workflow-Auslöser.
5. DEV darf für Entwicklung/Integration umfassend verändert werden, **jedoch kontrolliert, mit vorheriger Sicherung und dokumentiertem Rollback**. Der Eigentümer bestätigt: Noch keine realen Kunden, keine kundenrelevanten Produktivdaten. Das erleichtert Testdaten-Resets und Code-/DB-Migrationen, rechtfertigt aber keine unbelegte technische Datenintegrität.
6. **Business Central Extension**: Bereits installierte Sandbox-App-Tabellen/-Felder und Upgrade-Grenzen gelten weiterhin. Keine ForceSync-/Recreate-/Datentilgung als verdeckter Ersatz für eine saubere Upgrade-Abnahme. Für bewusste Sandbox-Neuinstallation gesonderte Entscheidung, Testdaten-/Evidence-Sicherung und neue Abnahme.
7. `Product System` bleibt normative Produktvertragsquelle, deren v2-Änderung **explizit versioniert und freigegeben** werden muss. Zielbild: Free Initial Scan / Full 14d / Renewal 14d / Renewal+Validation (ein neuer Scan-Credit) / Monitoring. Alter Quick-/7d-Vertrag darf nach Entscheidung ersetzt werden; **keine nicht genehmigten Preis-/Entitlement-Annahmen**.
8. **Release:** geprüfte Feature-PRs → kontrollierte DEV-Integration → BC27-/Runtime-/Sicherheits-/Kunden-E2E → eingefrorener RC → `main` als freigegebener PROD-Code → explizit autorisierte PROD-Promotion. `main` darf für diesen kontrollierten Zeitpunkt an DEV-/RC-Stand angeglichen werden, nicht zuvor unkontrolliert.
9. **Master-Datei:** `BCSentinel_GoLive_Master_Tracker_DEV_First_v2.xlsx`. Fortan neueste vom Nutzer hochgeladene Excel führt Aufgabenstatus; Tab `DEV-Release-Regeln` erklärt diesen Vertrag. Fiverr: 61 Tasks, 287 Stunden; SaaS/Stripe: 24 Tasks, 217 Stunden, außerhalb Fiverr-Fortschritt. Keine Häkchen allein wegen Dokumentation/Planungsänderung.
10. **Task-Freigaben:** technisch fertig (tatsächlich getestete Umsetzung) und Go-Live abgenommen (reale Gate-Evidence) bleiben getrennt. Testumgebung ohne reale Kunden bedeutet **nicht** automatisches GO.

## Auswirkungen auf aktuelle Arbeit

- **Sprint 3B.01**: Fachziel 199 Check-Coverage unverändert. Prompt korrigieren: `main` nicht als Base; zuerst verifizierte DEV-/Integrationsbaseline samt PR #162 HEAD ermitteln. CI auf Feature-Branch; keine Deployments.
- **Sprint 3B.02**: Fachziel Scan-Provenienz unverändert. Dieselbe Baseline-Regel, getrennte Dateien/PRs, Fail-Closed-Regression. Keine ungeprüfte Runtime-Vervollständigung behaupten.
- **Sprint 4.01**: Audit PR #164 korrekt als Vergleich historischer Dokumente gegen Draft-Ziel behandeln, **nicht** als Nachweis, dass der aktuelle DEV-Stand defekt ist. Versionierten Normvertrag vor Marketing-Preisen/Access-Versprechen genehmigen.
- **Beim ersten neuen Chat:** Aktuelle Excel zuerst lesen; diesen DEV-first-Vertrag und das ursprüngliche Handoff-Dokument beachten; tatsächliche DEV- und Branch-SHAs erneut prüfen.

## Keine automatischen Änderungen durch dieses Dokument

Kein Merge, kein Deployment, kein Reset, keine Schemaänderung, keine Kundenabrechnung, keine Go-Live-Freigabe.

# Scan Engine & Reporting — Top Findings

Stand: 2026-07-21

Die Reihenfolge ist innerhalb jeder Liste eine Assessment-Priorisierung, keine freigegebene Product-Intelligence-`priority`.

## Top 10 Stärken

1. **End-to-End-Wertkette.** BC-Datenerhebung, Findings, Score, Impact und Executive Report sind als zusammenhängender Produktpfad implementiert.
2. **Business-Central-Nativität.** Die Prüfungen laufen in AL nahe an den Quelldaten und übertragen überwiegend Aggregate statt vollständiger Stammdatensätze.
3. **Breite Domänenabdeckung.** Zehn Module und 198 registrierte Default-Checks decken Finance, Sales, Purchasing, Inventory, CRM, Manufacturing, Service, Jobs, HR und System ab.
4. **Robuster Scan-Lifecycle.** Idempotenter Start, Lease, Heartbeat, Retry, Recovery und Late-Writer-Schutz sind im Backendvertrag vorhanden.
5. **Transaktionale Finding-Konsistenz.** Completion setzt persistierte Pflichtresultate voraus; Findings werden je Scan und Code dedupliziert.
6. **Erklärbare Impact-Formel als Basis.** Zeit, Wahrscheinlichkeit, Frequenz, Stundensatz und affected count bilden einen nachvollziehbaren Rechenansatz.
7. **Executive-First-Report.** Score, finanzielle Wirkung, Saving, betroffene Datensätze, Checkanzahl und Bereichsscores sind schnell erfassbar.
8. **Mehrformat-Reporting.** JSON, HTML, A4-PDF und zeitlich begrenzte Share Links sind vorhanden.
9. **Starker Backend-Testvertrag.** Reportdaten, Visual Edge Cases, Tenantisolation, Tokenbindung und PDF-Rendererpfad sind automatisiert geprüft.
10. **Lokale, releasefähige Assets.** Fonts, Logo und CSS vermeiden externe Reportabhängigkeiten und unterstützen reproduzierbares Rendering.

## Top 10 Risiken

1. **Finanzielle Scheingenauigkeit.** Eurobeträge erscheinen centgenau, obwohl Defaultannahmen und keine Kundenkalibrierung zugrunde liegen.
2. **Saving als pauschaler Faktor.** Standardmäßig werden 70 Prozent des Estimated Loss als Potential Saving verwendet, ohne Maßnahmenkosten oder Realisierbarkeit.
3. **Nicht versionierte Bewertungslogik.** Regeln, Severity, Penalties und Impactannahmen sind nicht als historisch reproduzierbarer Assessment Snapshot modelliert.
4. **Fehlende AL-Regressionsautomation.** Der größte fachliche Ausführungspfad besitzt keine AL-Test-App.
5. **Katalogdrift.** 198 Default-Checks stehen einer Reportkonstante von 165 gegenüber.
6. **Leere Kerndokumente.** Quick-/Deep-Check-Dokumente und Scoring Model enthalten im Baseline-Commit keinen Inhalt.
7. **Ungeklärte Severity-Semantik.** Ratio, statischer Risk Level und Impact-Eskalation können unterschiedliche Klassifikationen erzeugen.
8. **Zu schmales Findings-Modell.** Rule version, evidence source, confidence, scope und remediation lifecycle fehlen.
9. **Keine reale Scale-Evidenz.** Laufzeit, Locking und Ressourcenverhalten auf großen BC-Datenbeständen sind nicht belegt.
10. **Visueller Eindruck übertrifft Evidenztiefe.** Der professionelle Report kann eine höhere fachliche Sicherheit suggerieren, als das Modell derzeit belegt.

## Top 10 Quick Wins

1. Generierten Checkkatalog aus der ausführbaren Registry erzeugen und die Zahl `165` eliminieren oder begründen.
2. `docs/checks/quickscan-checks.md`, `docs/checks/deepscan-checks.md` und `docs/product/scoring-model.md` mit dem tatsächlichen Baseline-Vertrag füllen.
3. Reportbeträge explizit als „modellierte Schätzung“ kennzeichnen und Formel/Annahmen direkt verlinken.
4. Modellversion, Checkabdeckung und ausgeführte/übersprungene Checks in JSON, HTML und PDF ausweisen.
5. Unknown Severity nicht still auf `low` setzen, sondern als unbekannt sichtbar machen und prüfen.
6. Einen Golden Dataset Smoke Test für repräsentative Quick-/Deep-Findings definieren.
7. Top drei Findings mit konkretem Why/Impact/Action statt generischer Upgrade-CTA in den Pilotreport aufnehmen.
8. Sprachmodus vollständig durch das Template führen; `lang`, feste Texte und Labels konsistent machen.
9. PDF-Golden-Render mit Seitenzahl, Text-Extraktion, Overflow und visueller Freigabe etablieren.
10. Jede Pilotannahme – Stundensatz, Wahrscheinlichkeit, Frequenz, Saving-Faktor – im Report mit Owner und Bestätigungsdatum ausgeben.

## Top 10 Produktdifferenzierungsmerkmale

1. Native Analyse direkt im Business-Central-Kontext.
2. Verbindung technischer Datenqualitätschecks mit operativem Business Impact.
3. Breite, modulare BC-Domänenabdeckung statt generischem Datenprofiling.
4. Vom Einzelcheck bis zum Executive Report durchgängige Datenkette.
5. Potenzial für kundenspezifische Impactmodelle über persistierte Konfiguration.
6. Modulscore- und Findingstruktur für Executive-to-Evidence-Drilldown.
7. Sichere, kurzlebige Executive-Report-Freigabe.
8. Partnerfähige, kundenfertige Berichtsausgabe statt Rohdiagnostik.
9. Wiederholbare Scan-Historie und Score-/Finding-Delta als Outcome-Basis.
10. Datenschutzfreundliche Aggregation ohne standardmäßige Übertragung vollständiger Quelldatensätze.

Die Punkte 5, 6 und 9 sind derzeit Potenzial: Für einen belastbaren Moat fehlen Governance, Versionierung und validierte Outcome-Evidenz.

## Top 10 Go-Live Blocker

1. Kein automatisierter AL-Nachweis für Checkausführung und Scorebildung.
2. Kein versionierter, freigegebener Rule-/Score-/Severity-Vertrag.
3. Keine Kunden-/Fachexpertenkalibrierung der Impactannahmen.
4. Kein verantwortbarer Nachweis für den 70-Prozent-Saving-Faktor.
5. Keine reale Großdaten-, Locking- und Laufzeitevidenz in BC.
6. Keine Produktions-PDF-Abnahme mit realem Scan und repräsentativen Extremwerten.
7. Checkanzahl und tatsächlicher Katalog sind nicht konsistent ausgewiesen.
8. Findings enthalten keine vollständige Evidence Lineage und Modellversion.
9. Keine normative Product-System-Spezifikation für Reportinhalt und Freigabekriterien.
10. Keine belastbare Pilot-/Kunden-Outcome-Evidenz zu Relevanz, False Positives und realisiertem Nutzen.

## Evidenzanker

- **Product System:** `00-core/PRODUCT_VISION.md`, `00-core/PRODUCT_PRINCIPLES.md`, `03-ux/EXECUTIVE_UX.md`, `04-components/KPI.md`, `ISSUE_CARD.md`, `RECOMMENDATION_CARD.md`, `05-pages/reports/README.md`.
- **Product Master Book:** `components/scan-engine.md`, `components/executive-reporting.md`, `05-test-inventory.md`, `08-manual-review-required.md`, `10-inventory-quality-report.md`, `data/features.yaml`, `data/workflows.yaml`.
- **Repository:** AL Scan Codeunits und Findingtabellen; Backend scoring/impact/report services, schemas, models und tests; bestehende Scan-/Reportaudits.

Capabilitygenaue Dreiquellenbelege stehen im Evidence Register von `docs/SCAN_ENGINE_ASSESSMENT.md`.

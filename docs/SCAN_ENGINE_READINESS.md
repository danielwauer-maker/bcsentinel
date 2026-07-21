# Scan Engine & Reporting — Readiness Assessment

Stand: 2026-07-21

Baselines: Product System `4497029`; Product Master Book / Repository `46a8989`

## Entscheidungsrahmen

Die Zustände folgen dem Readiness Model: `not_assessed`, `blocked`, `conditional`, `ready`. Es werden keine Mittelwerte oder Prozentwerte gebildet. Diese Bewertung gilt nur für den Scope Scan Engine und Executive Reporting; ausgeschlossene Plattformbereiche sind keine Grundlage der Entscheidung.

## Readiness Summary

| Sicht | Status | Entscheidung |
|---|---|---|
| Business Readiness | `conditional` | Wertversprechen ist stark, Zahlungsbereitschaft und finanzielle Modellannahmen sind noch nicht kundenseitig validiert. |
| Product Readiness | `conditional` | End-to-End-Kern und breite Checkabdeckung existieren; Rule/Score/Severity Governance und Finding-Evidenz sind unvollständig. |
| Executive Readiness | `conditional` | Report ist in Sekunden lesbar; Berechnungsbasis, Confidence und konkrete findingspezifische Next Actions fehlen im sichtbaren Free-Template. |
| Pilot Readiness | `conditional` | Kontrollierter, handgeführter Pilot ist vertretbar, wenn finanzielle Aussagen als Schätzmodell begrenzt und die unten genannten Gates erfüllt werden. |
| Go-Live Readiness | `blocked` | Reale BC-/Großdatenevidenz, AL-Testautomation, fachlich freigegebene Bewertungslogik und visuelle PDF-Produktionsabnahme fehlen. |

## Business Readiness — `conditional`

**Zweck.** Prüft, ob der Scope einen klaren, monetarisierbaren und differenzierenden Kundennutzen trägt.

**Erfüllte Evidenz.** BC-native Datendiagnose, breite Modul-/Checkabdeckung, priorisierte Findings, Score, Eurostory und teilbarer Executive Report bilden ein verständliches Paket. Product Vision und Executive-First-Prinzip werden sichtbar umgesetzt.

**Bedingungen.** Ein Pilot muss das Wertversprechen als Hypothese messen: erkannte relevante Findings, bestätigte False-Positive-Rate, akzeptierte Prioritäten, realisierte Zeitersparnis und Bereitschaft zur Fortsetzung. Eurobeträge dürfen ohne bestätigte Annahmen nicht als realisierte Verluste oder Einsparungen präsentiert werden.

**Evidence Missing.** Kundeninterviews, bezahlte Nutzung, Win/Loss-Daten, Outcome- und Benchmarkdaten.

## Product Readiness — `conditional`

**Zweck.** Prüft, ob der aktuelle Produktumfang im definierten Pilotkontext zuverlässig den versprochenen Nutzen liefert.

**Erfüllte Evidenz.** Quick/Deep Scan, Module, 198 registrierte Default-Checks, Finding-Sync, Score, Impact und Report sind implementiert. Scan-Lifecycle und Ergebnisatomizität besitzen starke Backendverträge.

**Bedingungen.** Pilot-Scope und unterstützte Module/Checks müssen versioniert feststehen. Checkanzahl, Reportkonstante und tatsächlich ausgeführter Katalog müssen übereinstimmen. Score-, Severity- und Impactregeln müssen als Pilotvertrag dokumentiert sein.

**Evidence Missing.** AL-Test-App, Expected-Results-Datensatz, reale BC-Sandboxausführung, Großdatenprofil, vollständige Checkdokumentation.

## Executive Readiness — `conditional`

**Zweck.** Prüft, ob Geschäftsführer, CFO und CIO Risiko, Wirkung und nächste Handlung schnell und verantwortbar verstehen.

**Erfüllte Evidenz.** Zwei Seiten liefern Score, Business Impact, Potential Saving, affected records, checks, Bereichsscores und Severity. Visuelle Hierarchie, ruhiges Design, lokale Assets und Disclaimer sind vorhanden.

**Bedingungen.** Sichtbar sein müssen: Berechnungsbasis, Modellversion, Daten-/Scanzeitpunkt, Scope, Confidence, Top Findings und eine konkrete nächste Aktion. Der Pilotreport muss sprachlich konsistent sein.

**Evidence Missing.** Executive Usability Review, CFO-Fachabnahme, normativer Report Content Spec, Produktions-PDF-QA.

## Pilot Readiness — `conditional`

**Definierter Kontext.** Ein kontrollierter erster Enterprise-Pilot mit benanntem Kunden, vereinbarten Modulen, fachlichem Ansprechpartner, manueller Ergebnisprüfung, begrenzter Entscheidungsnutzung und dokumentiertem Feedback. Kein autonomer Compliance-, Audit- oder Finanzentscheid.

**Zwingende Pilot-Gates.** Alle `pilot_critical = true` Einheiten müssen im Pilotpfad funktionsfähig sein. Vor Start sind mindestens erforderlich:

1. versionierter Check-/Rule-/Score-/Severity-Snapshot für den Pilot;
2. Expected-Results-Lauf in einer BC-Sandbox;
3. visuelle Freigabe des tatsächlich erzeugten PDFs;
4. klare Kennzeichnung aller Eurobeträge als modellierte Schätzungen samt Annahmen;
5. manuelle fachliche Review aller High/Critical Findings vor Executive Präsentation;
6. dokumentierte ausgeschlossene Module, Datenvolumina und Entscheidungszwecke;
7. benannter Owner für Abweichungen und Pilotfeedback.

Sind diese Gates erfüllt, ist der Status für genau diesen Pilotkontext `conditional`; ohne Gate 1–5 ist er `blocked`.

## Go-Live Readiness — `blocked`

**Blocker.** Die aktuelle Evidenz erfüllt die strengere Freigabe für wiederholbaren, unbeaufsichtigten und skalierbaren Enterprise-Betrieb nicht:

- keine AL-Test-App und kein automatisierter End-to-End-Nachweis der 198 Default-Checks;
- keine belastbare Regel-/Score-/Severity-Versionierung und keine historische Reproduzierbarkeit;
- keine fachliche Kalibrierung von Impact und Saving;
- keine Last-/Großdatenmessung in realer Business-Central-Umgebung;
- keine visuelle Produktions-PDF-Regression;
- Findings-Modell ohne Evidence Lineage und Calculation Snapshot;
- Checkkatalog/Reportanzahl inkonsistent;
- Product System besitzt noch keine normative Report-Inhaltsspezifikation.

## Quality, Operational und Documentation Readiness als Einflussgrößen

| Sicht | Status | Kernaussage |
|---|---|---|
| Quality Readiness | `conditional` | Backend gut getestet; fachlicher Deep-Scan-Pfad und AL bleiben unterbelegt. |
| Operational Readiness | `conditional` | Lifecycle/Recovery stark; reale BC-Laufzeit, Scale und PDF-Runtime offen. |
| Documentation Readiness | `blocked` | Lifecycle-/Reportaudits sind gut, aber Check- und Scoring-Kerndokumente sind leer und die Bewertungslogik nicht kanonisch beschrieben. |

## Reproduzierbarkeit

Die Detailratings und Evidence Bundles stehen in `docs/SCAN_ENGINE_ASSESSMENT.md`. Änderungen an Product System, Checkkatalog, Bewertungslogik, Reporttemplate oder Runtime machen diese Readiness-Aussage `stale` und erfordern ein neues Assessment.

# Scan Engine & Reporting — Enterprise Product Assessment

Stand: 2026-07-21

Assessment Owner: Founder / Chief Product Officer / Enterprise SaaS Architecture

Assessment Status: `reviewed`

Repository-Baseline: `46a898934a488f74afb95109437c0b24292e7994`

Product-System-Baseline: `449702963f500096bce1837f4da69b84db7f99d0`

## 1. Executive Summary

BCSentinel besitzt einen glaubwürdigen Produktkern: Die native Business-Central-Extension führt einen breiten, modularen Deep Scan aus, synchronisiert aggregierte Findings in ein tenantgebundenes Backend, berechnet Score und finanzielle Wirkung und erzeugt daraus einen visuell ausgearbeiteten Executive Report. Das ist deutlich mehr als ein technischer Datenchecker und grundsätzlich monetarisierbar.

Für einen kontrollierten ersten Enterprise-Pilot ist der Kern jedoch nur unter Bedingungen verantwortbar. Die größte Lücke ist nicht die Anzahl der Checks, sondern die Beweisführung hinter den Aussagen. Severity, Risikoklassifikation, Score-Abzüge, Zeit-/Wahrscheinlichkeitsannahmen und der pauschale Saving-Faktor sind im Code vorhanden, aber nicht als versioniertes, fachlich freigegebenes und für Kunden nachvollziehbares Entscheidungsmodell dokumentiert. Damit kann ein CIO die technische Substanz anerkennen, während ein CFO die Belastbarkeit von Eurobeträgen und Einsparversprechen zu Recht hinterfragt.

Die stärksten Produktbausteine sind der BC-native Scanner, die modulare Abdeckung, die transaktionale Finding-Synchronisation und die HTML/PDF-Reportpipeline. Die größten Vertrauensrisiken sind fehlende AL-Automation, fehlende reale Großdaten-/Sandbox-Evidenz, leere Check-Dokumentation, ein Findings-Modell ohne Regelversion und Evidenzherkunft sowie ein Executive Template, das Berechnungsbasis und Annahmen nicht offenlegt.

## 2. Bewertungsvertrag

Es gilt das Authority Model `Product System → Product Master Book → Repository`. Das Product System ist normativ, das Product Master Book beschreibt den inventarisierten Stand, und der committed Repository-Stand verifiziert die Implementierung. Uncommitted Änderungen wurden nicht als Evidenz verwendet.

Ratings verwenden ausschließlich das Product Intelligence Model:

- Level `1–5` für Wert, Sichtbarkeit, Qualität und Risiko;
- `true`/`false`/`null` für Pilot- und Go-Live-Gates;
- `null` für `priority`, weil keine freigegebene Planungsentscheidung vorliegt;
- `unassigned` für `target_release`, weil dieses Assessment keine Roadmap erzeugt.

Die im Auftrag genannten, aber nicht im Modell definierten Begriffe `Differentiation`, `Architecture Quality`, `Executive Readability`, `Business Relevance`, `Actionability`, `Decision Support`, `Consistency` und `Business Risk` werden als qualitative Review-Linsen behandelt. `strategic_importance` bildet die langfristige Differenzierungsrelevanz ab; `product_risk` bildet das Risiko falscher oder nicht vertrauenswürdiger Kundenaussagen ab. Es werden keine neuen Attribute eingeführt.

| Auftragsbegriff | Modellkonforme Behandlung |
|---|---|
| Differentiation | qualitative Business-Review-Linse, gestützt durch `strategic_importance`, `customer_value` und `revenue_impact` |
| Architecture Quality | qualitative Architecture-Review-Linse, gestützt durch `maintainability`, `stability`, `technical_debt` und `operational_risk` |
| Documentation | `documentation_quality` |
| Business Risk | qualitative Risikolinse, gestützt durch `product_risk` und `operational_risk` |
| Executive Readability | qualitative Reporting-Review-Linse, gestützt durch `ux` und `customer_visibility` |
| Business Relevance | qualitative Reporting-Review-Linse, gestützt durch `business_value` und `customer_value` |
| Actionability | qualitative Reporting-Review-Linse, gestützt durch `functional_completeness`, `ux` und `product_risk` |
| Decision Support | qualitative Reporting-Review-Linse, gestützt durch `customer_value`, `documentation_quality` und `product_risk` |
| Consistency | qualitative Reporting-Review-Linse, gestützt durch `stability`, `maintainability` und `product_risk` |

Alle numerischen Bewertungen sind ordinal, werden nicht addiert und nicht zu einer Gesamtnote verdichtet. `Evidence Missing` ist ein Befund, keine Schätzung.

### Abkürzungen

`CV` Customer Value · `BV` Business Value · `RI` Revenue Impact · `SI` Strategic Importance · `FC` Functional Completeness · `Vis` Customer Visibility · `PC` Pilot Critical · `GC` Go-Live Critical · `St` Stability · `UX` UX · `M` Maintainability · `D` Documentation Quality · `T` Test Coverage · `TD` Technical Debt · `PR` Product Risk · `OR` Operational Risk.

## 3. Capability Assessment Matrix

Jede Zeile verweist auf ein Evidence Bundle in Abschnitt 5. Die dortigen drei Quellen und die Capability Review begründen sämtliche Werte der Zeile.

| # | Assessment Unit | Business | Product | Quality | Risk | Planning | Evidenz |
|---:|---|---|---|---|---|---|---|
| 1 | Scan Engine | CV 5 · BV 5 · RI 4 · SI 5 | FC 4 · Vis 4 · PC true · GC true | St 3 · UX 3 · M 3 · D 4 · T 3 | TD 3 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: BC Extension, Backend Scan API, DB | EB-01 |
| 2 | Scan Module Framework | CV 4 · BV 4 · RI 3 · SI 5 | FC 4 · Vis 2 · PC true · GC true | St 3 · UX 2 · M 3 · D 3 · T 1 | TD 3 · PR 4 · OR 4 | priority null · target `unassigned` · Dependencies: Setup, Module Scores, Check Framework | EB-02 |
| 3 | Scan Check Framework | CV 5 · BV 5 · RI 4 · SI 5 | FC 4 · Vis 3 · PC true · GC true | St 3 · UX 2 · M 2 · D 1 · T 1 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: AL tables, BC permissions, modules | EB-03 |
| 4 | Rule Engine | CV 4 · BV 4 · RI 3 · SI 5 | FC 2 · Vis 2 · PC true · GC true | St 2 · UX null · M 2 · D 1 · T 1 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: hard-coded AL checks, backend impact config | EB-04 |
| 5 | Findings | CV 5 · BV 5 · RI 4 · SI 5 | FC 4 · Vis 5 · PC true · GC true | St 4 · UX 4 · M 3 · D 3 · T 3 | TD 3 · PR 5 · OR 3 | priority null · target `unassigned` · Dependencies: Scan Sync, issue texts, access control | EB-05 |
| 6 | Severity Model | CV 4 · BV 5 · RI 4 · SI 5 | FC 3 · Vis 5 · PC true · GC true | St 3 · UX 3 · M 2 · D 2 · T 2 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: checks, impact logic, report ordering | EB-06 |
| 7 | Risk Classification | CV 4 · BV 5 · RI 4 · SI 5 | FC 2 · Vis 4 · PC true · GC true | St 2 · UX 3 · M 2 · D 1 · T 1 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: Severity, category normalization, impact | EB-07 |
| 8 | Impact Calculation | CV 5 · BV 5 · RI 5 · SI 5 | FC 3 · Vis 5 · PC true · GC true | St 3 · UX 3 · M 3 · D 2 · T 2 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: impact definitions, affected count, settings | EB-08 |
| 9 | Financial Impact | CV 5 · BV 5 · RI 5 · SI 5 | FC 3 · Vis 5 · PC true · GC true | St 3 · UX 4 · M 3 · D 2 · T 2 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: Impact Calculation, currency assumptions, report | EB-09 |
| 10 | Potential Savings | CV 5 · BV 5 · RI 5 · SI 5 | FC 2 · Vis 5 · PC true · GC true | St 3 · UX 4 · M 3 · D 1 · T 2 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: Financial Impact, saving factor, price | EB-10 |
| 11 | Health Score | CV 5 · BV 5 · RI 4 · SI 5 | FC 3 · Vis 5 · PC true · GC true | St 3 · UX 4 · M 2 · D 2 · T 3 | TD 4 · PR 5 · OR 4 | priority null · target `unassigned` · Dependencies: checks, penalties, modules, findings | EB-11 |
| 12 | KPI Calculation | CV 4 · BV 4 · RI 4 · SI 4 | FC 3 · Vis 5 · PC true · GC true | St 3 · UX 4 · M 3 · D 3 · T 4 | TD 3 · PR 4 · OR 3 | priority null · target `unassigned` · Dependencies: persisted scan and finding aggregates | EB-12 |
| 13 | Report Engine | CV 5 · BV 5 · RI 5 · SI 5 | FC 4 · Vis 5 · PC true · GC true | St 4 · UX 4 · M 4 · D 4 · T 4 | TD 2 · PR 4 · OR 3 | priority null · target `unassigned` · Dependencies: completed scan, entitlement, Jinja/Playwright | EB-13 |
| 14 | PDF Generation | CV 4 · BV 4 · RI 4 · SI 4 | FC 4 · Vis 5 · PC true · GC true | St 3 · UX 4 · M 3 · D 4 · T 3 | TD 3 · PR 4 · OR 4 | priority null · target `unassigned` · Dependencies: Chromium, fonts, HTML template | EB-14 |
| 15 | Executive Report | CV 5 · BV 5 · RI 5 · SI 5 | FC 3 · Vis 5 · PC true · GC true | St 4 · UX 4 · M 4 · D 4 · T 4 | TD 2 · PR 5 · OR 3 | priority null · target `unassigned` · Dependencies: Score, KPI, impact, findings, report engine | EB-15 |
| 16 | Report Templates | CV 4 · BV 4 · RI 4 · SI 4 | FC 2 · Vis 5 · PC true · GC true | St 3 · UX 4 · M 3 · D 4 · T 4 | TD 3 · PR 4 · OR 3 | priority null · target `unassigned` · Dependencies: schema, CSS/assets, localization | EB-16 |
| 17 | Findings Data Model | CV 4 · BV 5 · RI 4 · SI 5 | FC 3 · Vis 3 · PC true · GC true | St 4 · UX null · M 3 · D 3 · T 3 | TD 4 · PR 5 · OR 3 | priority null · target `unassigned` · Dependencies: migrations, AL tables, sync contract | EB-17 |

## 4. Capability Reviews

### 4.1 Scan Engine

**Executive Summary.** Der End-to-End-Kern ist implementiert und für Kunden erkennbar: native Datenerhebung, Quick/Deep Scan, modulare Checks, Findings, Score, Sync und Reportanschluss. Die Breite und BC-Nähe sind differenzierend; Enterprise-Belastbarkeit unter realen Datenmengen ist nicht belegt.

**Architecture Review.** Die Trennung zwischen lokaler AL-Datenerhebung und Backend-Lifecycle/Reporting reduziert Rohdatenübertragung. Lease, Heartbeat, Retry, idempotenter Start und transaktionale Resultatpersistenz sind starke Architekturmerkmale. Reale Mehrinstanz-, BC-Sandbox- und Großdatenläufe fehlen.

**Business Review.** Der Nutzen ist hoch, weil ein technischer Datenbestand in priorisierbare Managementinformationen überführt wird. Umsatzwirkung ist plausibel, aber Zahlungsbereitschaft wurde nicht durch Kunden- oder Pilotdaten belegt. Differentiation: hoch durch Business-Central-Nativität plus vollständige Story vom Check zum Bericht.

**Quality Review.** Backendverträge sind breit getestet; AL besitzt keine Test-App. Dokumentation zum Lifecycle ist gut, zur fachlichen Checklogik lückenhaft. Stability bleibt deshalb `3`, nicht `4` oder `5`.

**Reporting Review.** Executive Readability und Business Relevance sind hoch; Actionability ist mittel bis hoch. Decision Support und Consistency werden durch nicht erklärte Score-/Impactannahmen begrenzt.

**Risiken.** Falsche Positiv-/Negativbefunde, nicht skalierende Tabellenläufe und nicht nachvollziehbare Euroaussagen treffen den Kern des Kundenvertrauens.

**Founder-Fragen.** Geschäftsführer versteht den Nutzen: **Ja**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Ja, potenziell deutlich**. Vertrauenswürdig: **Unter Bedingungen**. Zahlungsbereitschaft: **Ja, nach fachlicher Kalibrierung und Pilotbeleg**.

**Empfehlungen.** Einen kontrollierten Referenzdatensatz samt Expected Results etablieren; Großdaten- und BC-Sandbox-Evidenz erzeugen; Score/Severity/Impact als gemeinsam versionierten Bewertungsvertrag offenlegen.

**Evidence.** Evidence Bundle `EB-01` in Abschnitt 5.

### 4.2 Scan Module Framework

**Executive Summary.** Zehn Module strukturieren den Scan nach realen Business-Central-Domänen. Das unterstützt Skalierung und Executive Drilldown, ist für Kunden aber nur indirekt sichtbar.

**Architecture Review.** Modulwahl, Fortschritt und persistierte Modulscores sind vorhanden. Die Zuordnung ist in AL-Verzweigungen und Namensnormalisierung verteilt; ein explizites versioniertes Modulmanifest ist nicht belegt.

**Business / Reporting Review.** Bereichsscores machen Verantwortlichkeiten greifbar. Nutzen und Entscheidungshilfe steigen, wenn jeder Bereich Scope, Abdeckung und ausgeschlossene Tabellen sichtbar erklärt; diese Evidenz fehlt.

**Quality Review.** Struktur ist verständlich, aber AL-Tests und reale Laufzeitmessungen je Modul fehlen.

**Risiken.** Ein Score von 100 kann bei nicht ausgeführtem oder unvollständig abgedecktem Modul als Qualität missverstanden werden.

**Founder-Fragen.** Nutzen unmittelbar: **Teilweise**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Ja, als Enabler**. Vertrauenswürdig: **Unter Bedingungen**. Bezahlbar: **Ja, als Teil des Scanprodukts**.

**Empfehlungen.** Modulmanifest mit Tabellen, Checks, Version, Ausführungsstatus und Coverage in die Reportevidenz aufnehmen.

**Evidence.** Evidence Bundle `EB-02` in Abschnitt 5.

### 4.3 Scan Check Framework

**Executive Summary.** Der Registry-Ansatz enthält 199 `AddCheck`-Vorkommen einschließlich der Hilfsprozedur, also 198 registrierte Default-Checks. Das ist substanzielle Domänenabdeckung; der Reportkonstantwert `165` und leere Check-Dokumente erzeugen jedoch einen direkten Vertrauenskonflikt.

**Architecture Review.** Aktivierung, Defaultzustand, Modul, Risk Level, Sortierung und letzte Ausführung werden verwaltet. Definition und Ausführung sind nicht in einem einzigen versionierten Katalog verbunden; unbekannte Codes werden als `CUSTOM` angelegt.

**Business / Reporting Review.** Die Checkbreite ist ein starkes Verkaufsargument. Ohne sichtbare Scope-, Versions- und Kriterienliste bleibt sie jedoch schwer prüfbar und nicht procurement-fest.

**Quality Review.** `docs/checks/quickscan-checks.md` und `docs/checks/deepscan-checks.md` sind im Baseline-Commit leer. Eine AL-Test-App fehlt. Das rechtfertigt `D 1` und `T 1` trotz vorhandener Implementierung.

**Risiken.** Katalogdrift, tote oder nicht ausgeführte Checks, inkonsistente Checkanzahl, fehlende Regressionssicherheit.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Ja, je Check**. Wettbewerbsvorteil: **Ja**. Vertrauenswürdig: **Noch nicht ausreichend belegt**. Bezahlbar: **Ja, sobald Katalog und Wirksamkeit nachweisbar sind**.

**Empfehlungen.** Einen generierten, versionierten Checkkatalog aus derselben Quelle wie die Ausführung etablieren und jeden Check mit Testfall, Business-Rationale und Datenumfang belegen.

**Evidence.** Evidence Bundle `EB-03` in Abschnitt 5.

### 4.4 Rule Engine

**Executive Summary.** Es existiert Regelverhalten, aber keine eigenständige Enterprise Rule Engine. Regeln sind überwiegend als AL-Prozeduren, feste Penalties und Backend-Fallbackheuristiken codiert.

**Architecture Review.** Konfigurierbare Impact-Parameter sind ein guter Ansatz. Für Checklogik fehlen versionierte Rulesets, Gültigkeit, Mandanten-/Branchenprofil, Freigabestatus, Simulation und Rollback.

**Business / Reporting Review.** Ein wartbares Regelmodell könnte zum langfristigen Moat werden. Der Ist-Stand ist implementierungszentriert und für Executive Nutzer unsichtbar.

**Quality Review.** Änderungen an Regeln erfordern Codeänderungen; fachliche Regression und Rückverfolgbarkeit sind nicht ausreichend belegt.

**Risiken.** Nicht reproduzierbare historische Ergebnisse nach Regeländerungen und langsame Anpassung an Branchen-/Länderkontexte.

**Founder-Fragen.** Nutzen: **Nicht unmittelbar**. Handlungsorientiert: **Indirekt**. Wettbewerbsvorteil: **Noch nicht als Engine**. Vertrauenswürdig: **Teilweise**. Bezahlbar: **Nicht separat im Ist-Stand**.

**Empfehlungen.** Zuerst einen fachlichen Rule Contract definieren: ID, Version, Scope, Querybasis, Severity, Scorewirkung, Impactannahmen, Evidenz und Freigabe.

**Evidence.** Evidence Bundle `EB-04` in Abschnitt 5.

### 4.5 Findings

**Executive Summary.** Findings verbinden Code, Titel, Kategorie, Severity, betroffene Anzahl, Empfehlung und Impact. Sie sind der zentrale Übergang von Diagnose zu Kundennutzen.

**Architecture Review.** Sync dedupliziert über `(scan_id, code)` und Completion verlangt konsistente Findings. Lokale und Backendmodelle sind klar verbunden.

**Business / Reporting Review.** Findings sind sichtbar und grundsätzlich handlungsorientiert. Empfehlungen sind teilweise checkspezifisch, teilweise generische Kategorie-Fallbacks; Owner, Status, Due Date und Resolution Evidence fehlen im Kernmodell.

**Quality Review.** Backendverträge prüfen Deduplizierung, Reporting und Zugriff. AL-Ausführung und End-to-End-Korrektheit sind nicht automatisiert belegt.

**Risiken.** Aggregation auf einen Code pro Scan kann heterogene Ursachen zusammenfassen; fehlende Evidenzdetails erschweren Audit und Remediation.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Überwiegend**. Wettbewerbsvorteil: **Ja, im BC-Kontext**. Vertrauenswürdig: **Unter Bedingungen**. Bezahlbar: **Ja**.

**Empfehlungen.** Evidence lineage, Regelversion, Scope, Confidence und Remediation Lifecycle ergänzen, bevor Findings als auditierbare Enterprise-Aussagen vermarktet werden.

**Evidence.** Evidence Bundle `EB-05` in Abschnitt 5.

### 4.6 Severity Model

**Executive Summary.** `critical/high/medium/low` wird durchgängig verwendet, aber aus verschiedenen Mechanismen abgeleitet: Quick-Scan-Ratio, statischer Check-Risk-Level und Impact-Eskalation.

**Architecture / Quality Review.** Die gemeinsame Taxonomie ist positiv. Kriterien sind jedoch verteilt; Backend normalisiert unbekannte Werte zu `low`, und High kann durch Codemarker, Anzahl oder Eurobetrag zu Critical eskalieren. Eine normative Entscheidungslogik ist nicht belegt.

**Business / Reporting Review.** Severity ist prominent und verständlich, erklärt aber nicht zuverlässig Priorität, Ursache, Aufwand und Businessprozess gemäß Product-System-Prinzip „Actionable Severity“.

**Risiken.** Gleiches Problem kann je Scanpfad anders klassifiziert werden; `low` als Fallback kann unbekannte Daten verharmlosen.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Nein, derzeit austauschbar**. Vertrauenswürdig: **Teilweise**. Bezahlbar: **Nur eingebettet**.

**Empfehlungen.** Eine einzige versionierte Severity Policy mit Begründungscode und sichtbarer Berechnungsbasis einführen.

**Evidence.** Evidence Bundle `EB-06` in Abschnitt 5.

### 4.7 Risk Classification

**Executive Summary.** Category, Severity und Impact ermöglichen eine implizite Risikosortierung; ein eigenständiges Risk Model mit Wahrscheinlichkeit, Auswirkung, Zeithorizont und Kontrollbezug ist nicht nachgewiesen.

**Architecture / Quality Review.** Kategorien werden teils geliefert, teils aus Codes inferiert. Das ist robust als Fallback, aber keine fachlich kontrollierte Klassifikation.

**Business / Reporting Review.** „Top Risks“ werden nach Impact, Severity und Anzahl sortiert. Der Report nennt Risiken, erklärt aber weder Risikotyp noch Unsicherheit oder Kontrollbezug.

**Risiken.** Management kann geschätzte Nacharbeitskosten mit finanzieller Exposition, Compliance-Risiko oder Eintrittswahrscheinlichkeit verwechseln.

**Founder-Fragen.** Nutzen: **Teilweise**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Noch nicht**. Vertrauenswürdig: **Evidence Missing für fachliche Validierung**. Bezahlbar: **Nicht separat**.

**Empfehlungen.** Risikoarten und Calculation Basis explizit trennen; „Risiko“, „Impact“ und „Saving“ nicht synonym verwenden.

**Evidence.** Evidence Bundle `EB-07` in Abschnitt 5.

### 4.8 Impact Calculation

**Executive Summary.** Die Formel `affected records × minutes × probability × annual frequency × hourly rate` ist nachvollziehbar und konfigurierbar. Das ist eine gute Basis für Financial Storytelling.

**Architecture Review.** Viele Codes besitzen explizite ImpactDefinitionen; unbekannte Codes erhalten heuristische Fallbacks. Defaultstundensatz ist 40 EUR. Version, Herkunft und Gültigkeitszeitraum der Annahmen fehlen.

**Business / Reporting Review.** Der Ansatz kann CFO-relevant werden, wenn Annahmen sichtbar und kundenspezifisch bestätigt werden. Im Report wird nur der Betrag, nicht die Formel oder Konfidenz gezeigt.

**Quality Review.** Normalisierung und Grenzwerte sind codiert; systematische Validierung gegen reale Kundenkosten ist `Evidence Missing`.

**Risiken.** Scheingenauigkeit auf Centniveau, additive Doppelzählung korrelierter Findings, ungeeignete Fallbackannahmen.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Ja, als Priorisierung**. Wettbewerbsvorteil: **Potenziell stark**. Vertrauenswürdig: **Nur als deklarierte Schätzung**. Bezahlbar: **Ja, nach Kalibrierung**.

**Empfehlungen.** Annahmen, Quelle, Konfidenz, Regelversion und Doppelzählungsregeln pro Betrag sichtbar machen.

**Evidence.** Evidence Bundle `EB-08` in Abschnitt 5.

### 4.9 Financial Impact

**Executive Summary.** Der aggregierte Jahresimpact schafft eine klare Managementstory. Er ist derzeit eine modellierte Arbeits-/Risikokostenschätzung, keine nachgewiesene finanzielle Verlustrechnung.

**Architecture / Business Review.** Werte werden aus Findings neu berechnet und persistiert. Das unterstützt Konsistenz, aber Currency, Land, Lohnniveau, Prozessvolumen und Materialität sind nicht im Reportmodell ausgewiesen.

**Reporting Review.** Sehr gut sichtbar und CFO-relevant; zugleich größtes Reputationsrisiko, wenn „finanzielle Auswirkung“ als faktischer Verlust verstanden wird.

**Risiken.** Doppelzählung, falscher Erwartungswert, fehlende Sensitivitätsspanne, fehlende fachliche Freigabe.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Ja**. Wettbewerbsvorteil: **Potenziell**. Vertrauenswürdig: **Unter transparenter Methodik**. Bezahlbar: **Ja, bei belastbarer Kalibrierung**.

**Empfehlungen.** Als „modellierte jährliche Aufwands-/Risikoexposition“ kennzeichnen und Basis/Spanne neben dem Betrag zeigen.

**Evidence.** Evidence Bundle `EB-09` in Abschnitt 5.

### 4.10 Potential Savings

**Executive Summary.** Potential Savings ist ein starkes Kaufargument, wird standardmäßig jedoch als 70 Prozent des Estimated Loss berechnet.

**Architecture / Quality Review.** Der Faktor ist konfigurierbar und auf 0–1 begrenzt; eine kunden-, check- oder Maßnahmen-spezifische Realisierbarkeit fehlt.

**Reporting Review.** Hohe Executive Readability, aber geringe Erklärbarkeit. Die Templateaussage „Potenzielle jährliche Einsparungen“ ist nur durch einen allgemeinen Disclaimer relativiert.

**Risiken.** Der Betrag kann als Einsparversprechen gelesen werden. Es fehlen Implementierungskosten, Realisierungsdauer, Adoption und Confidence.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Potenziell**. Vertrauenswürdig: **Noch nicht CFO-fest**. Bezahlbar: **Ja, wenn als Szenario statt Zusage geführt**.

**Empfehlungen.** Base/Low/High-Szenario oder kundenseitig bestätigten Faktor mit Herkunft und Datum verwenden; keine Scheingenauigkeit.

**Evidence.** Evidence Bundle `EB-10` in Abschnitt 5.

### 4.11 Health Score

**Executive Summary.** Der 0–100 Score ist das stärkste Executive-Signal, aber zugleich ein Trust Liability, solange Composition, Weighting, Coverage und Ausnahmen nicht sichtbar sind.

**Architecture Review.** Quick Scan verwendet feste Minor/Major-Abzüge; Deep Scan zieht Penalty Points ab und berechnet Modulscores aus Severity und affected count. Mehrere Schwellenmodelle und Report-Statusgrenzen existieren.

**Business / Reporting Review.** Sofort verständlich, trendfähig und hoch sichtbar. Eine externe Benchmark oder fachliche Kalibrierung ist nicht belegt.

**Quality Review.** Backend Quick-Scan-Tests existieren; Deep-Scan-AL-Scorepfad ist nicht durch eine AL-Test-App abgesichert. `docs/product/scoring-model.md` ist leer.

**Risiken.** Ein präziser Score kann mehr Gewissheit suggerieren als die Datenbasis trägt; nicht ausgeführte Checks und Moduldefaults können das Bild verzerren.

**Founder-Fragen.** Nutzen: **Ja, unmittelbar**. Handlungsorientiert: **Nur mit Breakdown**. Wettbewerbsvorteil: **Nein als Zahl, ja mit erklärbarer BC-Logik**. Vertrauenswürdig: **Noch nicht ausreichend erklärt**. Bezahlbar: **Ja als Teil des Produkts**.

**Empfehlungen.** Scorecard mit Version, ausgeführten/übersprungenen Checks, Gewichten, Abzügen, Ausnahmen und Delta zum Vorscan bereitstellen.

**Evidence.** Evidence Bundle `EB-11` in Abschnitt 5.

### 4.12 KPI Calculation

**Executive Summary.** Score, Impact, Saving, affected records, checks, Issueverteilung und Modulscores werden zentral aggregiert und konsistent formatiert.

**Architecture / Quality Review.** Pydantic-Grenzen, Clamping, lokale Zahlen-/Währungsformatierung und Edge-Case-Tests sind gute Grundlagen. `checks_total = max(165, checks_count)` ist kein belastbarer Katalognachweis.

**Reporting Review.** Lesbarkeit ist hoch. Kontextanforderungen des Product Systems – Quelle, Zeitraum und Bedeutung je KPI – sind nur teilweise erfüllt.

**Risiken.** Aggregatdefinitionen können driftieren; `issues_count` und Anzahl Findingtypen sind semantisch nicht immer dasselbe.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Als Paket**. Vertrauenswürdig: **Überwiegend, mit Definitionslücken**. Bezahlbar: **Ja als Reportbestandteil**.

**Empfehlungen.** KPI Dictionary mit Berechnung, Grain, Zeitraum, Quelle, Nullverhalten und Version veröffentlichen.

**Evidence.** Evidence Bundle `EB-12` in Abschnitt 5.

### 4.13 Report Engine

**Executive Summary.** JSON, HTML, PDF und zeitlich begrenzte Share Links sind implementiert. Der Service aggregiert Findings, KPIs, Severity, Bereiche und Maßnahmen in ein stabiles Schema.

**Architecture Review.** Tenantprüfung, Capabilityprüfung, lokalisierte Labels, Jinja Autoescape und an Scan/Typ gebundene Tokens sind starke Merkmale. Abhängigkeit von vollständigem Scan und Chromium ist klar.

**Business / Reporting Review.** Der Report macht Ergebnisse teilbar und schafft Partner-/Executive-Hebel. Die reicheren JSON-Bereiche werden im aktuellen Free-Template teilweise bewusst nicht gezeigt.

**Quality Review.** Die Backendtests decken Datenvertrag, HTML, PDFpfad, Sharelinks, Ablauf und Tenantisolation breit ab.

**Risiken.** Kein kanonisches Product-System-Content-Spec für Report Detail; reale End-to-End-/Visual-QA bleibt offen.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Ja**. Wettbewerbsvorteil: **Ja als End-to-End-Paket**. Vertrauenswürdig: **Technisch hoch, fachlich bedingt**. Bezahlbar: **Ja**.

**Empfehlungen.** Normative Report-Content-Spec und fachliche Acceptance-Gates ergänzen.

**Evidence.** Evidence Bundle `EB-13` in Abschnitt 5.

### 4.14 PDF Generation

**Executive Summary.** Playwright/Chromium erzeugt A4-PDFs mit eingebetteten Assets; ein einfacher Textfallback verhindert Totalausfall.

**Architecture / Quality Review.** Runtimepfad und Parameter sind getestet. Der Baseline-Readinessbericht bezeichnet Live-Rendering und visuelle PDF-Abnahme als offen; große reale Datensätze sind ebenfalls ungeprüft.

**Reporting Review.** Das visuelle Ergebnis ist professionell vorbereitet. Der Fallback ist funktional, aber nicht gleichwertig und könnte ohne klare Kennzeichnung an Kunden gelangen.

**Risiken.** Seitenumbrüche, Font-/Chromiumabweichungen, abgeschnittene Inhalte und Qualitätsdegradation im Fallback.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Als Transportformat**. Wettbewerbsvorteil: **Begrenzt**. Vertrauenswürdig: **Unter Runtime- und Visual-Gate**. Bezahlbar: **Ja, wenn visuell freigegeben**.

**Empfehlungen.** Golden-PDF-Regression plus Extraktions-/Seitenzahl-/Overflow-Prüfung im gebauten Produktionsimage.

**Evidence.** Evidence Bundle `EB-14` in Abschnitt 5.

### 4.15 Executive Report

**Executive Summary.** Die erste Seite beantwortet Score, finanzielle Wirkung, Einsparpotenzial, betroffene Datensätze, Checks, Bereiche und Severity. Das entspricht dem Executive-First-Zielbild gut.

**Architecture / Business Review.** Das Schema enthält Top Risks, Quick Wins, Critical Findings, Financial Risks, Actions und Priority Matrix. Das aktuelle zweitseitige Free-Template zeigt diese Detailstrukturen nicht, sondern führt primär zu Upgrades.

**Reporting Review.** Executive Readability: hoch. Business Relevance: hoch. Actionability: mittel, weil konkrete findingspezifische Maßnahmen im Free-PDF fehlen. Decision Support: mittel bis hoch. Consistency: mittel wegen nicht erklärter Zahlengrundlagen und Sprachpfad.

**Risiken.** Ein starker visueller Eindruck kann die noch nicht validierte Rechenbasis überstrahlen. Das Product System enthält noch keine normative Report-Inhaltsspezifikation.

**Founder-Fragen.** Nutzen: **Ja, in Sekunden erfassbar**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Ja, sofern Evidenz sichtbar wird**. Vertrauenswürdig: **Unter Bedingungen**. Bezahlbar: **Ja**.

**Empfehlungen.** Im Pilotreport mindestens Top Findings, konkrete Next Action, Calculation Basis und Confidence zeigen.

**Evidence.** Evidence Bundle `EB-15` in Abschnitt 5.

### 4.16 Report Templates

**Executive Summary.** Ein ausgearbeitetes deutsches Free-Report-Template mit CSS, lokalen Fonts und Branding ist vorhanden. Ein belastbarer Template-Katalog oder echtes sprachvariables Template ist nicht belegt.

**Architecture / Quality Review.** HTML ist strukturiert und getestet. `render_executive_report_html` baut unabhängig von der Reportsprache einen deutschen `display_report`, das Template trägt `lang="de"` und deutschen festen Text. Das steht einer international skalierbaren Templatearchitektur entgegen.

**Reporting Review.** Visuell konsistent und ruhig; inhaltlich upgradeorientiert. Executive Readability ist hoch, Internationalisierung und Variantenfähigkeit sind niedrig bis mittel.

**Risiken.** Sprachinkonsistenz, duplizierte feste Texte, fehlende Full-/Partner-/historische Templates, kein normativer Content Contract.

**Founder-Fragen.** Nutzen: **Ja**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Begrenzt**. Vertrauenswürdig: **Visuell ja, sprachlich/fachlich bedingt**. Bezahlbar: **Als Teil des Reports**.

**Empfehlungen.** Template-Varianten explizit versionieren und alle statischen Inhalte über einen gemeinsamen Localization-/Content-Contract führen.

**Evidence.** Evidence Bundle `EB-16` in Abschnitt 5.

### 4.17 Findings Data Model

**Executive Summary.** Das Modell trägt die wichtigsten Reportfelder und erzwingt Eindeutigkeit je Scan und Code. Für Enterprise-Nachvollziehbarkeit ist es zu schmal.

**Architecture Review.** Backend und AL speichern Code, Kategorie, Titel, Severity, Anzahl, Empfehlung, Premiumflag und Impact. Es fehlen unter anderem rule version, evidence source, evaluated scope, confidence, calculation inputs, first/last observed, resolution state, owner und exception linkage im Backendmodell.

**Business / Reporting Review.** Für einen Snapshotreport ausreichend; für Audit, Trend, Remediationsteuerung und beweisbare Outcome-Historie nicht ausreichend.

**Quality Review.** Unique Constraint und transaktionaler Ersatz sind stark. Änderungen an Text/Severity/Impact bleiben historisch nicht als Regelentscheidung erklärbar.

**Risiken.** Historische Reports sind nach späteren Modelländerungen schwer reproduzierbar; ein Aggregatfinding liefert keine betroffenen Record-IDs oder Evidenzstichprobe.

**Founder-Fragen.** Nutzen: **Indirekt hoch**. Handlungsorientiert: **Teilweise**. Wettbewerbsvorteil: **Noch nicht**. Vertrauenswürdig: **Für Snapshot, nicht für Audit**. Bezahlbar: **Als Enabler**.

**Empfehlungen.** Ein unveränderliches Finding Assessment Snapshot mit Rule-/Model-Version und Calculation Basis definieren.

**Evidence.** Evidence Bundle `EB-17` in Abschnitt 5.

## 5. Evidence Register

Jedes Bundle enthält normative Product-System-Evidenz (`PS`), deskriptive Product-Master-Book-Evidenz (`PB`) und Repository-Verifikation (`R`). `PB`-Pfade sind relativ zu `docs/product-master-book/`; Repositorypfade beziehen sich auf Baseline `46a8989`; Product-System-Pfade auf `4497029`.

### EB-01 — Scan Engine

- **PS:** `00-core/PRODUCT_VISION.md` (detect, explain, prioritize, improve); `00-core/PRODUCT_PRINCIPLES.md` (Microsoft Ecosystem Native, Enterprise Ready, Evidence Before Opinion).
- **PB:** `components/scan-engine.md`; `data/features.yaml` → `SCAN-CAP-001`; `data/workflows.yaml` → `WF-SCAN-001`, `WF-SCAN-003`–`005`, `WF-SCORE-001`.
- **R:** `DHDeepScanRunner.Codeunit.al`; `backend/app/routers/scans.py`; `backend/app/services/scan_status_service.py`; `docs/GL_EXT_P0C_SCAN_LIFECYCLE_RECOVERY.md`.
- **Evidence Missing:** real BC Sandbox, large-data runtime/locking profile, customer outcome evidence.

### EB-02 — Scan Module Framework

- **PS:** `PRODUCT_PRINCIPLES.md` (Progressive Disclosure, Explainable Scores); `EXECUTIVE_UX.md` (Score → risk → impact → evidence).
- **PB:** `components/scan-engine.md`; `SCAN-SCORE-001`; `WF-SCORE-001`.
- **R:** `DHDeepScanRunner.Codeunit.al` (ten enabled modules); `backend/app/models.py` (ten module score fields); `executive_report_service.py` (`MODULES`).
- **Evidence Missing:** module coverage contract, per-module benchmarks and AL automation.

### EB-03 — Scan Check Framework

- **PS:** `PRODUCT_PRINCIPLES.md` (Business Before Technology, Evidence Before Opinion, Microsoft Ecosystem Native).
- **PB:** `EXT-SCAN-001`, `EXT-SCAN-002`; `components/scan-engine.md`; `10-inventory-quality-report.md` (no AL tests).
- **R:** `DHScanCheckMgt.Codeunit.al` (198 default registrations plus helper signature); `DHDeepScanRunner.Codeunit.al`; empty `docs/checks/quickscan-checks.md` and `deepscan-checks.md`; report constant `165`.
- **Evidence Missing:** generated catalog, per-check expected-results tests, effectiveness/false-positive data.

### EB-04 — Rule Engine

- **PS:** `PRODUCT_PRINCIPLES.md` (Decision Traceability, Explainable Scores, Scalable Documentation).
- **PB:** no distinct Rule Engine feature; scan component names only check/profiling/scoring logic.
- **R:** hard-coded AL check procedures and penalties; `impact_service.py` explicit/fallback definitions and DB config tables.
- **Evidence Missing:** rule lifecycle, versioning, approval, effective dates, simulation, rollback and tenant/industry profiles.

### EB-05 — Findings

- **PS:** `ISSUE_CARD.md`; `ISSUE_TABLE.md`; `RECOMMENDATION_CARD.md`; `PRODUCT_PRINCIPLES.md` (Actionable Severity).
- **PB:** `WF-SCAN-005`; `SCAN-SYNC-001`; `components/scan-engine.md`.
- **R:** `ScanIssueRecord`; `DHDeepScanFinding.Table.al`; sync uniqueness and completion contract in `GL_EXT_P0C_SCAN_LIFECYCLE_RECOVERY.md`.
- **Evidence Missing:** real remediation outcome, owner/due-date workflow and evidence lineage.

### EB-06 — Severity Model

- **PS:** `PRODUCT_PRINCIPLES.md` (Actionable Severity, same model across surfaces); `ISSUE_CARD.md`.
- **PB:** findings workflow and report aggregation; no separate severity feature or policy.
- **R:** `_severity_from_ratio` in `scoring_service.py`; Risk Level in `DHScanCheckMgt`; `_impact_severity` in `impact_service.py`; `SEVERITY_WEIGHT` in report service.
- **Evidence Missing:** normative thresholds, calibration, disagreement tests across paths.

### EB-07 — Risk Classification

- **PS:** `PRODUCT_VISION.md` (business risk, financial exposure, remediation priority); `PRODUCT_PRINCIPLES.md` (Business Before Technology).
- **PB:** `REP-DATA-001` describes priorities and categories; no distinct risk-classification feature.
- **R:** category inference/normalization in impact/report services; top-risk ordering by impact, severity and count.
- **Evidence Missing:** risk taxonomy, likelihood, control mapping, horizon and expert validation.

### EB-08 — Impact Calculation

- **PS:** `PRODUCT_PRINCIPLES.md` (Financial Storytelling, Trust by Design, Evidence Before Opinion).
- **PB:** report and scan descriptions reference impact but define no formula.
- **R:** `impact_service.py` formula, explicit definitions, DB overrides, 40 EUR default rate and fallbacks.
- **Evidence Missing:** source provenance, customer calibration, versioning, double-count policy and validation dataset.

### EB-09 — Financial Impact

- **PS:** `PRODUCT_VISION.md`; `PRODUCT_PRINCIPLES.md` (quantify responsibly); `KPI.md` (context/source/status).
- **PB:** `REP-DATA-001`; `WF-REP-001`; executive-reporting component.
- **R:** `Scan.estimated_loss_eur`; scan commercial aggregation; executive template and disclaimer.
- **Evidence Missing:** accounting definition, currency/context, range/confidence and CFO acceptance.

### EB-10 — Potential Savings

- **PS:** Financial Storytelling and Trust by Design; `RECOMMENDATION_CARD.md` prohibits savings guarantees without basis.
- **PB:** reporting capability and scan model list potential saving without method.
- **R:** `DEFAULT_POTENTIAL_SAVING_FACTOR = 0.7`; clamping; report KPI and disclaimer.
- **Evidence Missing:** realization model, remediation cost, time-to-value, customer-specific factor approval.

### EB-11 — Health Score

- **PS:** `PRODUCT_PRINCIPLES.md` (Explainable Scores); `EXECUTIVE_UX.md`; `KPI.md`.
- **PB:** `SCAN-SCORE-001`; `WF-SCORE-001`; scan component.
- **R:** Quick Scan fixed deductions; Deep Scan penalty/module functions; report score bands; empty `docs/product/scoring-model.md`.
- **Evidence Missing:** canonical composition spec, benchmark/calibration, skipped-check semantics and AL golden tests.

### EB-12 — KPI Calculation

- **PS:** `KPI.md`; `EXECUTIVE_UX.md`.
- **PB:** `REP-DATA-001` and reporting component.
- **R:** `schemas/report.py`; aggregation functions in `executive_report_service.py`; `test_executive_report.py` edge cases.
- **Evidence Missing:** KPI dictionary, semantic compatibility tests across scan types, real-data reconciliation.

### EB-13 — Report Engine

- **PS:** Executive First, Partner Enablement, Release-Grade by Default; `05-pages/reports/README.md` says report contents are not yet specified.
- **PB:** `REP-CAP-001`, `REP-DATA-001`, `REP-HTML-001`, `REP-PDF-001`, `WF-REP-001`.
- **R:** `routers/reports.py`; `executive_report_service.py`; `schemas/report.py`; `test_executive_report.py`.
- **Evidence Missing:** normative report content spec and live customer acceptance.

### EB-14 — PDF Generation

- **PS:** `REPORT_CARD.md`; Release-Grade by Default; Executive UX.
- **PB:** `REP-PDF-001`; `08-manual-review-required.md` (visual PDF QA and large data outstanding).
- **R:** Playwright renderer and fallback; runtime docs; PDF contract tests and stored sample artifacts.
- **Evidence Missing:** production-image visual approval, overflow/golden regression and representative real dataset.

### EB-15 — Executive Report

- **PS:** `EXECUTIVE_UX.md`; Executive First; Financial Storytelling; Trust by Design.
- **PB:** executive-reporting component; `REP-DATA-001`; broad test status.
- **R:** report schema/build function, two-page template, CSS, tests; `EXECUTIVE_REPORT_READINESS.md` status PARTIAL.
- **Evidence Missing:** executive usability study, CFO validation and approved report content specification.

### EB-16 — Report Templates

- **PS:** Consistency Over Creativity, Calm Confidence, International/product scalability; reports README has no content spec.
- **PB:** `REP-HTML-001`; report component; visual design documentation.
- **R:** single German `executive_report.html`, CSS/assets, forced German display normalization, HTML contract tests.
- **Evidence Missing:** English/full/partner variants, cross-locale visual QA and template-version contract.

### EB-17 — Findings Data Model

- **PS:** Trust by Design, Decision Traceability, Evidence Before Opinion; Issue components require issue, impact, affected data and action.
- **PB:** `WF-SCAN-005`; database evidence; `SCAN-SYNC-001`.
- **R:** `ScanIssueRecord`, AL finding tables, migration/indexes and unique `(scan_id, code)` constraint.
- **Evidence Missing:** rule/evidence version, confidence, assessment scope, lifecycle/owner and immutable calculation snapshot.

## 6. Cross-Capability Conclusion

Die Scan Engine ist der wahrscheinlich stärkste USP-Kandidat von BCSentinel, aber der heutige Wettbewerbsvorteil liegt eher in der integrierten BC-nativen Produktkette als in einem bereits beweisbar überlegenen Bewertungsalgorithmus. Die nächste Wertstufe entsteht nicht durch noch mehr Checks, sondern durch Erklärbarkeit, Kalibrierung, Reproduzierbarkeit und beweisbare Outcomes.

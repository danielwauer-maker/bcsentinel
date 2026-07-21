# Customer Experience Assessment

Stand: 2026-07-21

Scope: ausschliesslich die im Auftrag benannten Customer-Experience-Oberflaechen

Entscheidungsgrundlage: Product System (normativ) > Product Master Book (deskriptiv) > Repository-Evidenz

## Executive Summary

BCSentinel besitzt einen glaubwuerdigen, differenzierenden Experience-Kern: Das Dashboard und insbesondere der Executive Report uebersetzen Datenqualitaet in Score, Risiko, finanzielle Auswirkung und naechste Handlung. Damit ist die zentrale Produktidee fuer Entscheider sichtbar. Die Experience ist jedoch noch kein durchgaengiges Enterprise-System. Landingpage, Portal, Support- und Rechtsseiten, Produktnavigation, Upgrade- und Checkout-Pfade sowie DE/EN-Texte wirken wie unterschiedlich reife Produktgenerationen.

Ein betreuter Pilot ist aus Customer-Experience-Sicht vertretbar, wenn die Journey kuratiert wird. Eine unbegleitete kommerzielle Go-Live-Journey ist nicht belegt. Ausschlaggebend sind nicht fehlende visuelle Effekte, sondern gebrochene Erwartungsketten: Pricing-CTAs fuehren zu Kontakt statt Checkout, ein direkter Free-Score-Einstieg fehlt, oeffentliche Seiten kennzeichnen sich als MVP, Mockup oder rechtlich vorlaeufig, und reale Browser-, Mobile-, Keyboard- sowie Payload-Varianten sind nicht nachgewiesen.

## Bewertungsmethode

Die angeforderten CX-Begriffe werden als qualitative Review-Linsen verwendet. Die eigentliche Bewertung nutzt ausschliesslich Attribute des Product Intelligence Model. Level 1 bis 5 bedeuten geringe bis sehr hohe Auspraegung; bei Risikoattributen bedeutet 5 sehr hohes Risiko. Gates sind keine Go-Live-Entscheidung. `priority=null` und `target_release=unassigned` vermeiden eine nicht autorisierte Roadmap. Security, Privacy und Compliance werden nicht bewertet.

Gemeinsame Planungswerte fuer alle Einheiten: `priority=null`; `target_release=unassigned`. Abhaengigkeiten werden pro Einheit benannt.

## Bewertungsuebersicht

| Capability | BV | CV | RI | SI | Sichtb. | Pilot | Go-live | Oper. | FC | Stabil. | UX | Wartb. | Doku | Tests | Tech. Debt | Produkt-Risiko | Oper. Risiko |
|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Landingpage | 4 | 4 | 4 | 4 | 5 | true | true | false | 3 | 3 | 3 | 2 | 3 | 1 | 4 | 4 | 2 |
| Dashboard | 5 | 5 | 5 | 5 | 5 | true | true | true | 4 | 3 | 4 | 2 | 4 | 3 | 4 | 4 | 3 |
| Analytics | 4 | 4 | 4 | 4 | 5 | true | true | false | 3 | 3 | 3 | 2 | 3 | 2 | 4 | 4 | 3 |
| Overview | 5 | 5 | 5 | 5 | 5 | true | true | true | 4 | 3 | 4 | 3 | 4 | 3 | 3 | 4 | 3 |
| Findings | 5 | 5 | 4 | 5 | 5 | true | true | true | 4 | 3 | 4 | 3 | 4 | 3 | 3 | 4 | 3 |
| Actions | 5 | 5 | 5 | 5 | 5 | true | true | true | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 5 | 3 |
| Navigation | 4 | 4 | 3 | 4 | 5 | true | true | false | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 2 |
| Informationsarchitektur | 5 | 5 | 4 | 5 | 5 | true | true | false | 3 | 3 | 3 | 3 | 5 | 2 | 3 | 4 | 2 |
| Visual Design | 4 | 4 | 4 | 4 | 5 | true | true | false | 3 | 3 | 4 | 3 | 4 | 1 | 3 | 4 | 2 |
| Design System | 4 | 4 | 3 | 5 | 4 | true | true | false | 2 | 3 | 3 | 2 | 5 | 1 | 4 | 4 | 2 |
| Branding | 4 | 4 | 4 | 5 | 5 | true | true | false | 3 | 3 | 3 | 2 | 4 | 1 | 4 | 4 | 2 |
| Free Experience | 4 | 4 | 5 | 5 | 5 | true | true | false | 3 | 3 | 3 | 3 | 4 | 2 | 3 | 5 | 2 |
| Full Experience | 5 | 5 | 5 | 5 | 5 | true | true | true | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 5 | 3 |
| Executive Experience | 5 | 5 | 5 | 5 | 5 | true | true | true | 4 | 3 | 4 | 3 | 5 | 3 | 3 | 5 | 3 |
| Onboarding | 5 | 5 | 5 | 5 | 5 | true | true | false | 2 | 2 | 2 | 3 | 3 | 2 | 3 | 5 | 3 |
| Registrierungsprozess | 4 | 4 | 4 | 4 | 5 | true | true | false | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 4 | 3 |
| Checkout Experience | 5 | 5 | 5 | 5 | 5 | true | true | false | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 5 | 3 |
| Upgrade Journey | 5 | 5 | 5 | 5 | 5 | true | true | false | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 5 | 3 |
| Report Presentation | 5 | 5 | 5 | 5 | 5 | true | true | true | 4 | 4 | 4 | 3 | 5 | 4 | 3 | 4 | 3 |
| Call-to-Action | 4 | 4 | 5 | 5 | 5 | true | true | false | 2 | 3 | 2 | 3 | 4 | 2 | 3 | 5 | 2 |
| Informationsdichte | 4 | 4 | 3 | 4 | 5 | true | true | false | 3 | 3 | 3 | 3 | 4 | 1 | 3 | 4 | 2 |
| Texte | 5 | 5 | 4 | 5 | 5 | true | true | false | 2 | 3 | 2 | 2 | 3 | 3 | 4 | 5 | 2 |
| Vertrauenssignale | 5 | 5 | 5 | 5 | 5 | true | true | false | 2 | 3 | 3 | 3 | 3 | 1 | 3 | 5 | 3 |

Abkuerzungen: BV Business Value, CV Customer Value, RI Revenue Impact, SI Strategic Importance, FC Functional Completeness. Die geringe Testbewertung bei visuellen Querschnittsthemen beschreibt fehlende visuelle End-to-End-Evidenz, nicht die Testabdeckung der Produktlogik.

## Capability Reviews

### 1. Landingpage

- **Executive Summary:** Die Seite erklaert Problem, finanziellen Nutzen und Produktstufen schnell, fuehrt aber mit alarmistischer Kostenbotschaft und vier gleichwertigen Angeboten statt mit dem normativen Free Score.
- **UX Review:** Lange Seite, starke visuelle Hierarchie, aber kein direkter Free-Score-CTA; Pricing-Buttons erzeugen falsche Checkout-Erwartung. Mobile, Fokusfuehrung und Screenreader-Verhalten sind nicht belegt.
- **Business Review:** CEO und Fachentscheider verstehen Datenqualitaet als Kosten- und Steuerungsthema. Die festen Beispielbetraege benoetigen erkennbaren Beispielkontext.
- **Commercial Review:** Kaufinteresse ist plausibel, Kaufvertrauen sinkt beim Sprung von Preis zu Kontaktformular. Upgrade-Motivation ist vorhanden, Conversion ist nicht durchgaengig.
- **Brand Review:** Eigenstaendig und hochwertig, zugleich dunkler, glaenzender und werblicher als das ruhige Dashboard und der Report.
- **Quality Review:** Zwei Landingpage-Baeume und nur statische/manual Evidenz erschweren Kanonizitaet und Wartung.
- **Risks / Recommendations:** Direkten Free-Score-Pfad herstellen, eine kanonische Site deklarieren, Preis-CTA wahrheitsgemaess benennen und Beispielrechnungen als Beispiele markieren.
- **Kundenfragen:** Bezahlen: eher nach Demo als unmittelbar. Vertrauen nach 5 Minuten: bedingt. CEO-Verstaendnis: ja. Enterprise-Eindruck: bedingt. Empfehlung: mit Vorbehalt. Upgrade-Motivation: ja. Emotion: Neugier mit Skepsis.
- **Evidence:** PS `LANDINGPAGE_UX.md`, `BRAND.md`; PB `components/landingpage.md`, `08-manual-review-required.md`; Repo `landingpage/index.html`, `landingpage/script.js`, `landingpage_neu/`. Abhaengigkeiten: Free Experience, CTA, Pricing-Kommunikation.

### 2. Dashboard

- **Executive Summary:** Der staerkste interaktive Produktbeweis; Score, Risiko, Business Impact und naechste Handlung sind sichtbar.
- **UX Review:** Vollstaendige Hauptnavigation und progressive Detailtiefe, jedoch sehr grosse Informationsmenge und ein monolithischer UI-Aufbau. Reale Varianten fuer Free, Premium und Monitoring wurden nicht visuell getestet.
- **Business / Commercial Review:** Hoher wahrnehmbarer Wert und gute Basis fuer Bezahlung sowie Upgrade. Entscheider erhalten eine Management-Sicht, operative Rollen koennen vertiefen.
- **Brand / Quality Review:** Helles, strukturiertes SaaS-Design wirkt enterprise-faehig; umfangreiche CSS/JS-Dateien und spaete Overrides mindern Wartbarkeit.
- **Risks / Recommendations:** Echten Cross-Browser-/Responsive-/Keyboard-Test mit realen Payloads ausfuehren; First View auf drei Entscheidungsfragen begrenzen; UI-Schichten modularisieren.
- **Kundenfragen:** Bezahlen: ja, bei glaubwuerdigen Daten. Vertrauen: bedingt ja. CEO: ja. Enterprise: ja. Empfehlung: bedingt ja. Upgrade: ja. Emotion: Kontrolle und Handlungsdruck.
- **Evidence:** PS `DASHBOARD_UX.md`, `EXECUTIVE_UX.md`; PB `components/customer-dashboard.md`; Repo `analytics_embed.html`, `analytics-dashboard.js`, `dashboard.css`, `TASK_5_DASHBOARD_FINALIZATION_AUDIT.md`. Abhaengigkeiten: Findings, Actions, Reports, reale Payloads.

### 3. Analytics

- **Executive Summary:** Liefert Vertiefung, ist aber gegenueber Overview, Scans und Findings nicht durchgaengig als eigene Managementfrage abgegrenzt.
- **UX / Business Review:** Kennzahlen und Trends unterstuetzen Analyse, die Navigation folgt jedoch Produktmodulen statt konsequenten Entscheidungsfragen. CEO-Nutzen entsteht erst mit Kontext.
- **Commercial / Brand Review:** Erhoeht den Wert einer Vollanalyse, ist allein kein klarer Kaufanker. Die Oberflaeche passt zum Dashboard, nicht vollstaendig zur oeffentlichen Marke.
- **Quality / Risks / Recommendations:** Reale Daten-, Empty- und Fehlerzustaende fehlen als visuelle Evidenz. Analytics auf eine klar benannte Frage und Interpretation pro Ansicht zuschneiden.
- **Kundenfragen:** Bezahlen: als Teil der Vollanalyse. Vertrauen: bedingt. CEO: teilweise. Enterprise: ja. Empfehlung: bedingt. Upgrade: mittel bis hoch. Emotion: analytische Neugier, teils Ueberforderung.
- **Evidence:** PS `EXECUTIVE_UX.md`, `VISUAL_HIERARCHY.md`; PB `components/customer-dashboard.md`; Repo Analytics-Section in `analytics_embed.html`/`analytics-dashboard.js`. Abhaengigkeiten: Overview, Datenkontext, Trends.

### 4. Overview

- **Executive Summary:** Nahe am normativen Executive Command Center und der klarste Einstieg in die Produktleistung.
- **UX / Business Review:** Health, Business Impact, Top Risks und Empfehlungen sind sichtbar; zusaetzliche Deep-Insight- und Breakdown-Bloecke machen die Seite laenger als fuer einen Erstblick ideal.
- **Commercial / Brand Review:** Sehr guter Premium-Beweis, ruhigere Enterprise-Wirkung als die Landingpage. Erklaerbare Score- und Geldgrundlagen muessen direkt erreichbar sein.
- **Quality / Risks / Recommendations:** Erste Bildschirmhoehe auf Zustand, Kosten, Top-Risiko und naechste Aktion fixieren; Evidenz und Berechnungsbasis an jedem kritischen KPI verlinken.
- **Kundenfragen:** Bezahlen: ja. Vertrauen: bedingt ja. CEO: ja. Enterprise: ja. Empfehlung: ja mit Evidenzvorbehalt. Upgrade: hoch. Emotion: Klarheit und Dringlichkeit.
- **Evidence:** PS `DASHBOARD_UX.md`, `EXECUTIVE_UX.md`; PB `DASH-OV-001`; Repo Overview-Markup und Renderer. Abhaengigkeiten: Score-Erklaerung, Findings, Actions.

### 5. Findings

- **Executive Summary:** Findings verbinden Schweregrad, Auswirkung und Detail und bilden den Kern der fachlichen Glaubwuerdigkeit.
- **UX / Business Review:** Listen und Detailansichten sind vorhanden; Owner, SLA, Verlauf, stabile Direktlinks und Record-Level-Kontext sind laut Audit nicht durchgaengig belegt.
- **Commercial / Brand Review:** Konkrete Befunde rechtfertigen die Vollanalyse. Ohne belastbare Evidenz und Verantwortlichkeit droht der Eindruck einer Diagnose ohne Umsetzungspfad.
- **Quality / Risks / Recommendations:** Pro Finding Ursache, Scope, Zeitpunkt, Berechnungsbasis, empfohlene Aktion und Ownership konsistent anzeigen.
- **Kundenfragen:** Bezahlen: ja. Vertrauen: bedingt. CEO: Summary ja, Detail delegierbar. Enterprise: bedingt ja. Empfehlung: nach Evidenzpruefung. Upgrade: hoch. Emotion: Sorge, dann Orientierung.
- **Evidence:** PS `EXECUTIVE_UX.md`, `CONTENT_STRATEGY.md`; PB `DASH-FIND-001`; Repo Issues- und Issue-Detail-Sections, Dashboard-Audit. Abhaengigkeiten: Actions, Evidence, Detaildaten.

### 6. Actions

- **Executive Summary:** Strategisch wichtigste Bruecke von Erkenntnis zu Wert, derzeit weniger reif als die Diagnose.
- **UX / Business Review:** Empfehlungen sind vorhanden, aber Umsetzungsstatus, Verantwortlichkeit, Priorisierungskontext und Erfolgskontrolle sind nicht als vollstaendiger Workflow belegt.
- **Commercial / Brand Review:** Die Bereitschaft zu zahlen steigt erst, wenn das Produkt nicht nur warnt, sondern nachweisbar zur Verbesserung fuehrt.
- **Quality / Risks / Recommendations:** Action Lifecycle mit Owner, Status, Ziel, BC-Kontext und Validierungsergebnis definieren; keine nicht ausfuehrbaren CTAs anbieten.
- **Kundenfragen:** Bezahlen: nur bei umsetzbaren Aktionen. Vertrauen: bedingt. CEO: ja auf Summary-Ebene. Enterprise: noch bedingt. Empfehlung: eingeschraenkt. Upgrade: hoch. Emotion: Handlungsfaehigkeit oder, bei Sackgassen, Frustration.
- **Evidence:** PS `CUSTOMER_JOURNEY.md`, `EXECUTIVE_UX.md`; PB `DASH-ACT-001`; Repo Actions-Section und Audit. Abhaengigkeiten: Findings, BC-Kontext, Validation Check.

### 7. Navigation

- **Executive Summary:** Funktional vollstaendig, aber nicht deckungsgleich mit der normativen Entscheidungssprache.
- **UX / Business Review:** Overview, Analytics, Scans, Issues, Actions, Reports, Subscription und Settings sind verstaendlich fuer Produktkundige; das Product System fordert Executive, Improve, Protect, Reports und Platform.
- **Commercial / Brand Review:** Sichtbare Subscription erleichtert Upgrade, kann aber den Arbeitsfluss kommerziell ueberfrachten. Unterschiedliche Navigation auf Landing-, Portal- und Dashboard-Ebene bricht Kontinuitaet.
- **Quality / Risks / Recommendations:** Informationsarchitektur als eine kanonische Taxonomie festlegen und aktuelle Ziele darauf mappen; aktive, locked und mobile states visuell pruefen.
- **Kundenfragen:** Bezahlen: indirekt. Vertrauen: bedingt. CEO: teilweise. Enterprise: ja, aber produktzentriert. Empfehlung: bedingt. Upgrade: sichtbar. Emotion: Orientierung mit Lernaufwand.
- **Evidence:** PS `INFORMATION_ARCHITECTURE.md`; PB `components/customer-dashboard.md`; Repo Sidebar und Site-Navigation. Abhaengigkeiten: IA, Terminologie, Rollen.

### 8. Informationsarchitektur

- **Executive Summary:** Gute lokale Struktur, aber keine durchgaengige Journey von Discover ueber Understand/Validate zu Protect/Improve.
- **UX / Business Review:** Dashboard und Report sind entscheidungsorientiert, Landingpage und Produktstufen fuehren anders. Scans und Analytics sind interne Kategorien, deren Nutzerfrage nicht immer sichtbar ist.
- **Commercial / Brand Review:** Uneinheitliche Produktbezeichnungen und Pfade erschweren Vergleich und Kaufentscheidung.
- **Quality / Risks / Recommendations:** Eine verbindliche Journey-Map mit Begriffen, Eintritts- und Austrittspunkten fuer Free, Full, Validation und Monitoring publizieren und gegen alle Oberflaechen pruefen.
- **Kundenfragen:** Bezahlen: bedingt. Vertrauen: bedingt. CEO: in Kernansichten ja. Enterprise: lokal ja, end-to-end nein. Empfehlung: mit Fuehrung. Upgrade: vorhanden, nicht reibungslos. Emotion: Klarheit im Kern, Unsicherheit an Uebergaengen.
- **Evidence:** PS `INFORMATION_ARCHITECTURE.md`, `CUSTOMER_JOURNEY.md`; PB Inventory/Komponentendokumente; Repo Landing-, Portal- und Dashboard-Struktur. Abhaengigkeiten: Navigation, Naming, CTA.

### 9. Visual Design

- **Executive Summary:** Einzelne Oberflaechen sind hochwertig, das Gesamtbild ist nicht aus einem Guss.
- **UX / Business Review:** Dashboard und PDF besitzen klare Hierarchie; Landingpage nutzt dunkle Gradients, Glassmorphism und 3D-Motiv; Portal ist stark reduziert. Dichte und Tonalitaet wechseln abrupt.
- **Commercial / Brand Review:** Hochwertige Einzelbilder steigern Interesse, Stilwechsel senken Reife- und Bestandsvertrauen.
- **Quality / Risks / Recommendations:** Einheitliche Token, Typografie, Iconografie, Dichte und Motion anwenden; keine Aussage ueber responsive Perfektion ohne Screenshots.
- **Kundenfragen:** Bezahlen: visuell plausibel. Vertrauen: bedingt. CEO: ja im Report. Enterprise: Dashboard/Report ja, Gesamtjourney bedingt. Empfehlung: bedingt. Upgrade: visuell unterstuetzt. Emotion: Eindruck, dann Inkonsistenz.
- **Evidence:** PS `DESIGN_BIBLE.md`, `BRAND.md`; Repo Screenshots, CSS, HTML und PDF-Renderings. Abhaengigkeiten: Design System, Branding, Accessibility.

### 10. Design System

- **Executive Summary:** Normativ stark dokumentiert, in der Repository-Umsetzung jedoch fragmentiert.
- **UX / Business Review:** Prinzipien fuer Hierarchie, Accessibility und Content sind klar. Landingpage, Dashboard, Portal und Report besitzen getrennte Stilwelten und keine belegte gemeinsame Komponentenbasis.
- **Commercial / Brand Review:** Ein gemeinsames System wuerde Reife, Geschwindigkeit und Vertrauen erhoehen; aktuell ist die Marke von der jeweiligen Oberflaeche abhaengig.
- **Quality / Risks / Recommendations:** Verbindliche Tokens und Kernkomponenten inventarisieren, Abweichungen dokumentieren, visuelle Regression fuer Schluesselpfade etablieren.
- **Kundenfragen:** Bezahlen: indirekt. Vertrauen: bedingt. CEO: nicht direkt. Enterprise: normativ ja, implementiert teilweise. Empfehlung: mit Vorbehalt. Upgrade: indirekt. Emotion: uneinheitliche Vertrautheit.
- **Evidence:** PS Design System und Components; PB Landing/Dashboard/Reporting; Repo getrennte CSS-/Template-Artefakte. Abhaengigkeiten: alle sichtbaren Oberflaechen.

### 11. Branding

- **Executive Summary:** Name, Datenqualitaetsversprechen und Blau/Orange-Wiedererkennung sind stark; Ausdruck und Reifegrad variieren.
- **UX / Business Review:** Business-Central-Naehe und Executive Story sind klar. Alarmistische Headline, glaenzendes 3D-Logo und aggressive Rot-/Kosteninszenierung stehen teils gegen „calm confidence“.
- **Commercial / Brand Review:** Differenzierung ist hoch, Social Proof und konsistente Enterprise-Signale sind schwach belegt.
- **Quality / Risks / Recommendations:** Eine Brand-Anwendung fuer Web, Product und Reports festlegen; Ton von Angst zu evidenzbasierter Handlungsfaehigkeit verschieben.
- **Kundenfragen:** Bezahlen: prinzipiell. Vertrauen: bedingt. CEO: ja. Enterprise: bedingt ja. Empfehlung: nach Proof. Upgrade: ja. Emotion: Dringlichkeit, teils Alarm.
- **Evidence:** PS `BRAND.md`, `PRODUCT_PRINCIPLES.md`; Repo Logo, Landingpage, Dashboard, PDF. Abhaengigkeiten: Text, Trust Signals, Visual Design.

### 12. Free Experience

- **Executive Summary:** Locked previews und Score-Versprechen koennen Wert zeigen, aber der oeffentliche Einstieg zum Free Score ist nicht durchgaengig.
- **UX / Business Review:** Im Dashboard sind gesperrte Detail-/Action-/Report-Zustaende vorgesehen. Die Landingpage fuehrt primaer zu Produkten statt zur ersten Analyse.
- **Commercial / Brand Review:** Gute Teaser-Mechanik, sofern der kostenlose Erkenntniswert eigenstaendig ist; zu viele Locks koennen wie ein Sales Gate wirken.
- **Quality / Risks / Recommendations:** Einen messbaren Free-Outcome, klaren Scope und genau einen naechsten Schritt definieren; komplette Free-Journey real testen.
- **Kundenfragen:** Bezahlen: nach belastbarem Free-Ergebnis wahrscheinlich. Vertrauen: erst nach Ergebnis. CEO: ja, wenn Score erklaert. Enterprise: bedingt. Empfehlung: bei eigenstaendigem Nutzen. Upgrade: hoch. Emotion: Neugier, bei Locks Frustration.
- **Evidence:** PS `CUSTOMER_JOURNEY.md`, `LANDINGPAGE_UX.md`; PB `DASH-GATE-001`; Repo locked previews und Landing-CTAs. Abhaengigkeiten: Onboarding, Score, Upgrade.

### 13. Full Experience

- **Executive Summary:** Breites Analyse-, Finding-, Action- und Reporting-Angebot, aber kein vollstaendig belegter Remediation-Lifecycle.
- **UX / Business Review:** Nutzer koennen von Summary zu Details navigieren. Umsetzung, Ownership, Erfolgsmessung und reale Langzeitnutzung bleiben lueckenhaft belegt.
- **Commercial / Brand Review:** Der Umfang rechtfertigt ein kostenpflichtiges Produkt; Wertrealisierung darf nicht beim Report enden.
- **Quality / Risks / Recommendations:** Einen End-to-End-Fall von Finding ueber Action bis Validation und Trend mit realer Payload abnehmen.
- **Kundenfragen:** Bezahlen: ja, unter Nachweis. Vertrauen: bedingt. CEO: ja. Enterprise: bedingt ja. Empfehlung: nach Pilotnachweis. Upgrade: ist Zielzustand. Emotion: Kontrolle, spaeter Erwartung an Umsetzung.
- **Evidence:** PS Customer Journey; PB Dashboard/Reporting; Repo Vollzugriffs-States. Abhaengigkeiten: Findings, Actions, Reports, Validation.

### 14. Executive Experience

- **Executive Summary:** Inhaltlich sehr stark und klar differenziert; Vertrauen haengt an Erklaerbarkeit der exakten Scores und Geldwerte.
- **UX / Business Review:** Report und Overview beantworten Zustand, Kosten, Risiko und Empfehlung. Report-Seite 2 ersetzt konkrete Remediation teilweise durch Kauf-CTAs.
- **Commercial / Brand Review:** Hoher Vorstandsnutzen und starkes Verkaufsartefakt. Exakte Eurobetraege ohne sichtbare Unsicherheit oder Basis koennen den Effekt umkehren.
- **Quality / Risks / Recommendations:** Berechnungsbasis, Scope, Zeitpunkt, Konfidenz und Ausnahmen unmittelbar zugreifbar machen; Empfehlung zuerst fachlich, dann kommerziell.
- **Kundenfragen:** Bezahlen: ja. Vertrauen: bei Evidenz. CEO: klar ja. Enterprise: ja. Empfehlung: bedingt ja. Upgrade: hoch. Emotion: Klarheit und Dringlichkeit.
- **Evidence:** PS `EXECUTIVE_UX.md`; PB Executive Reporting; Repo PDF-Seiten und Overview. Abhaengigkeiten: Explainability, Findings, Report.

### 15. Onboarding

- **Executive Summary:** Der normative Fuenf-Schritt-Pfad ist nicht als zusammenhaengende Kundenerfahrung belegt.
- **UX / Business Review:** Portal bietet Login, Aktivierung und Tenant-Auswahl, wirkt aber wie ein technisches MVP. Erklaerung von Pruefumfang, Fortschritt, Abbruch und erster Analyse ist nicht end-to-end sichtbar.
- **Commercial / Brand Review:** Betreute Einfuehrung kann die Luecke ueberbruecken; Self-Service-Kaufvertrauen entsteht so nicht.
- **Quality / Risks / Recommendations:** Guided Flow fuer Kontext, Verbindung, Scope, Free Score, Fortschritt und Ergebnis prototypisch und mit Neukunden testen.
- **Kundenfragen:** Bezahlen: nicht allein aufgrund dieses Flows. Vertrauen: gering bis bedingt. CEO: delegiert. Enterprise: noch nicht. Empfehlung: nur betreut. Upgrade: noch nicht relevant. Emotion: Unsicherheit.
- **Evidence:** PS `ONBOARDING_UX.md`; PB Dashboard-Komponente/manual review; Repo `dashboard_portal.html`. Abhaengigkeiten: Registrierung, Free Score, Progress/Errors.

### 16. Registrierungsprozess

- **Executive Summary:** Formular- und Aktivierungsoberflaechen existieren, die customer-facing Registrierung ist aber nicht als vollstaendige Journey dokumentiert.
- **UX / Business Review:** Wenige Felder sind positiv; Nutzen, Rollen, erwartete Dauer, naechster Schritt und Recovery sind nicht ausreichend sichtbar belegt. Authentifizierungsmechanik selbst ist ausser Scope.
- **Commercial / Brand Review:** Ein einfacher Prozess senkt Reibung, ein technischer Portalstil senkt Kauf- und Weiterempfehlungsvertrauen.
- **Quality / Risks / Recommendations:** Nur Experience-Vertrag definieren und testen: Einladung, Aktivierung, Tenant-Wahl, Erfolg, Fehler und Rueckkehr.
- **Kundenfragen:** Bezahlen: erst nach Produktbeweis. Vertrauen: bedingt. CEO: nicht relevant. Enterprise: funktional, nicht ausgereift. Empfehlung: betreut. Upgrade: neutral. Emotion: Pflichtschritt.
- **Evidence:** PS Onboarding/Forms; PB `DASH-TEN-001`; Repo Portal-Template. Abhaengigkeiten: Onboarding, Tenant Context, Support.

### 17. Checkout Experience

- **Executive Summary:** Die sichtbare Journey verspricht Kauf, fuehrt oeffentlich aber zu einem Kontaktformular; ein durchgaengiger Checkout ist nicht belegt.
- **UX / Business Review:** Preise sind sichtbar, Produktumfang und Begriffe teils uneinheitlich. Success/Cancel-Seiten existieren, der Weg dorthin ist im oeffentlichen Pfad nicht nachvollziehbar.
- **Commercial / Brand Review:** Groesster unmittelbarer Conversion-Blocker. „Open in Business Central“ bei Kontaktziel verletzt Erwartung und Vertrauen.
- **Quality / Risks / Recommendations:** Pro Angebot einen wahrheitsgemaessen CTA und klaren Ablauf vor Kauf, Zahlung, Aktivierung und Rueckkehr definieren; realen Sandbox-Kauf visuell abnehmen. Zahlungslogik selbst bleibt ausser Scope.
- **Kundenfragen:** Bezahlen: Interesse ja, Abschluss aktuell nein/unklar. Vertrauen: sinkt am CTA. CEO: Preis versteht er, Prozess nicht. Enterprise: nein im End-to-End. Empfehlung: nein ohne Begleitung. Upgrade: gebremst. Emotion: Verwirrung.
- **Evidence:** PS `SUBSCRIPTION_UX.md`; PB Pricing/Checkout/manual review; Repo Pricing-Links, `contact.html`, `billing-success.html`, `billing-cancel.html`. Abhaengigkeiten: Produktbenennung, CTA, Aktivierung.

### 18. Upgrade Journey

- **Executive Summary:** Wert und gesperrte Mehrleistung sind sichtbar, doch Produktstufen und Uebergaenge bilden keine reibungslose Kette.
- **UX / Business Review:** Locked states, Subscription und Report-CTA zeigen einen naechsten Schritt. Assessment, Full Analysis, Validation und Monitoring konkurrieren als Kaufobjekte.
- **Commercial / Brand Review:** Motivation ist hoch, Entscheidungssicherheit und Konsequenz des Kaufs sind geringer.
- **Quality / Risks / Recommendations:** Je Ausgangszustand genau einen nutzenbasierten Upgrade-Pfad mit enthaltenem Umfang, Preis, Aktivierung und Rueckkehr definieren.
- **Kundenfragen:** Bezahlen: wahrscheinlich bei Beratung. Vertrauen: bedingt. CEO: Nutzen ja, Planlogik teilweise. Enterprise: bedingt. Empfehlung: mit Erklaerung. Upgrade: hoch, aber Reibung hoch. Emotion: Wunsch nach mehr, dann Unsicherheit.
- **Evidence:** PS Customer Journey/Subscription UX; PB access gates; Repo locked previews, Subscription UI, Report-CTA. Abhaengigkeiten: Checkout, Naming, Entitlements-Anzeige.

### 19. Report Presentation

- **Executive Summary:** Visuell und inhaltlich das staerkste Enterprise-Artefakt.
- **UX / Business Review:** Executive Summary, Score, Geldwirkung, Module und Severity sind auf Seite 1 gut lesbar. Seite 2 ist sehr leer und kommerziell statt remediation-spezifisch.
- **Commercial / Brand Review:** Hohe Teilbarkeit und starker Wertbeweis; unerklaerte Exaktheit bei Geldwerten ist ein Vertrauensrisiko.
- **Quality / Risks / Recommendations:** Methoden-/Scope-Verweis, Konfidenz, fachliche Top-Actions und visuelle Tests fuer reale Datenmengen ergaenzen.
- **Kundenfragen:** Bezahlen: ja. Vertrauen: bei Methodenbeleg. CEO: ja. Enterprise: ja. Empfehlung: ja mit Vorbehalt. Upgrade: stark. Emotion: Ernsthaftigkeit und Entscheidungsdruck.
- **Evidence:** PS Executive UX/Reporting; PB `components/executive-reporting.md`; Repo gerenderte PDF-Seiten, Report-Tests. Abhaengigkeiten: Datenbasis, Actions, PDF-Rendering.

### 20. Call-to-Action

- **Executive Summary:** Viele CTAs sind sichtbar, aber nicht immer wahrheitsgemaess, priorisiert oder journey-konsistent.
- **UX / Business Review:** Hero priorisiert Produkte statt Free Score; vier Pricing-CTAs fuehren zum gleichen Kontaktziel; Reports priorisieren Upgrade vor konkreter fachlicher Aktion.
- **Commercial / Brand Review:** Hohe CTA-Dichte ohne klares Versprechen senkt Conversion und calm confidence.
- **Quality / Risks / Recommendations:** CTA-Inventar mit Label, Ziel, Erwartung und Erfolg definieren; pro View eine primaere Handlung; alle Ziele automatisiert pruefen.
- **Kundenfragen:** Bezahlen: CTA erzeugt Interesse, nicht Sicherheit. Vertrauen: sinkt bei Zielabweichung. CEO: teilweise. Enterprise: derzeit bedingt. Empfehlung: nein ohne Erklaerung. Upgrade: sichtbar, aber gebremst. Emotion: Impuls, dann Irritation.
- **Evidence:** PS Landingpage/Subscription/Content; Repo Links und Buttons auf Landing, Dashboard und Report. Abhaengigkeiten: IA, Checkout, Upgrade.

### 21. Informationsdichte

- **Executive Summary:** Hoher Informationswert, aber wechselnde Dichte zwischen Dashboard, Landingpage und Report.
- **UX / Business Review:** Overview enthaelt viele Karten und Vertiefungen; Landingpage ist lang; PDF Seite 1 ist dicht, Seite 2 auffallend leer. Kleine Schriftgrade koennen die Executive- und Accessibility-Wirkung mindern.
- **Commercial / Brand Review:** Detailreichtum signalisiert Substanz, kann Erstnutzer und CEO aber ueberfordern.
- **Quality / Risks / Recommendations:** Progressive Disclosure je Rolle testen; First View und PDF-Seiten mit realistischen Daten und 200-%-Zoom pruefen.
- **Kundenfragen:** Bezahlen: Substanz hilft. Vertrauen: meist positiv. CEO: Kern ja, Gesamtmenge nein. Enterprise: ja, aber dicht. Empfehlung: bedingt. Upgrade: indirekt. Emotion: Kompetenz, teils Ueberforderung.
- **Evidence:** PS Visual Hierarchy/Accessibility; Repo Dashboard-Markup/CSS, Landingpage und PDF. Abhaengigkeiten: Roles, Responsive, Accessibility.

### 22. Texte

- **Executive Summary:** Die Business-Impact-Sprache differenziert, die Ausfuehrung enthaelt jedoch go-live-kritische Sprach- und Platzhalterfehler.
- **UX / Business Review:** Viele Texte sind konkret und handlungsorientiert. Deutsche Ressourcen enthalten ASCII-Umschriften, gemischte englische Begriffe, sichtbare `EUR-`-Artefakte und generische Keys/Platzhaltertexte.
- **Commercial / Brand Review:** Sprachfehler auf Preis-, Hero-, Support- oder Rechtsseiten zerstoeren Vertrauen unverhaeltnismaessig schnell.
- **Quality / Risks / Recommendations:** Professionelles DE/EN-Lektorat, Terminologie-Glossar, Placeholder-Scan und gerenderte Locale-Abnahme als Release-Gate.
- **Kundenfragen:** Bezahlen: nicht bei sichtbaren Fehlern. Vertrauen: nein bei deutscher Fehlerdarstellung. CEO: Kernaussage ja. Enterprise: derzeit nicht durchgaengig. Empfehlung: nein vor Korrektur. Upgrade: durch Fehler geschwaecht. Emotion: Zweifel.
- **Evidence:** PS `CONTENT_STRATEGY.md`, Terminology; PB Localization; Repo `landingpage/lang/de.json`, Dashboard-Dictionary, Support/Terms. Abhaengigkeiten: Localization, Content Governance, alle Oberflaechen.

### 23. Vertrauenssignale

- **Executive Summary:** Es gibt starke produktnahe Signale, aber oeffentliche Gegenbeweise ueberwiegen an kritischen Stellen.
- **UX / Business Review:** Microsoft-Business-Central-Kontext, konkrete Scores, transparente Produktstufen, Methode-/Datumsfelder und ein professioneller Report helfen. Fehlende reale Kundenbelege und Runtime-Evidenz begrenzen die Wirkung.
- **Commercial / Brand Review:** Support nennt sich MVP und zeigt ein Mockup; Terms verlangen finale rechtliche Pruefung; Legal-/Dokuseiten enthalten vorlaeufige Inhalte; Pricing-CTA und Ziel widersprechen sich. Diese Aussagen sind customer-visible Findings, keine Security- oder Rechtsbewertung.
- **Quality / Risks / Recommendations:** Unfertige oeffentliche Seiten aus der Kaufjourney nehmen oder finalisieren; Claims, Rechenbasis, Supportversprechen, echte Produktbilder und Kunden-/Partnerbelege reviewen.
- **Kundenfragen:** Bezahlen: nur nach persoenlicher Validierung. Vertrauen nach 5 Minuten: bedingt bis nein, je Pfad. CEO: Produktwert ja. Enterprise: Kern ja, Rand nein. Empfehlung: erst nach Nachbesserung. Upgrade: vorhanden, aber Risiko. Emotion: Faszination plus Vorsicht.
- **Evidence:** PS Trust by Design/Brand; PB Landing/manual review/quality report; Repo Support-, Terms-, Landing-, Report- und Dashboard-Artefakte. Abhaengigkeiten: Texte, Report Explainability, Support, Legal Content.

## Evidence-Grenzen

- Kein erreichbarer lokaler oder authentifizierter Live-Flow; daher keine Behauptung ueber reales Rendering, Console, Form- oder Navigationsverhalten.
- Keine visuelle Abnahme bei 390/768/1024/1440 Pixel, 200-%-Zoom oder realen Free/Premium/Monitoring-Payloads.
- Keine Keyboard-, Screenreader-, Kontrast- oder Reduced-Motion-Pruefung; Accessibility bleibt Evidence Missing.
- Keine Kundeninterviews, Conversion-Daten, Supportdaten oder Usability-Sessions.
- Screenshots belegen nur den dargestellten Zustand; Repository-Code belegt Struktur, nicht Produktionsverhalten.
- Backend, Authentication, Licensing, Rule/Scan Engine, Monitoring, Scheduler, Security und AppSource wurden nicht bewertet.

## Assessment Governance

`assessment_status=reviewed`; `assessment_owner=Chief Product Architect`; `last_assessed_at=2026-07-21`; `assessment_confidence=medium`. Die Konfidenz ist wegen starker statischer, aber fehlender Live- und Nutzer-Evidenz nicht hoch.

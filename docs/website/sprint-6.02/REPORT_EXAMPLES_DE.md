---
title: Sprint 6.02 – Synthetische Report-Beispiele DE
status: editorial_demo_only
owner: Product Content
locale: de-DE
updated: 2026-11-11
---

# BCSentinel – Report-Beispiele (Deutsch)

> **AUSSCHLIESSLICH FIKTIVE DEMODATEN.** Alle Unternehmen, Scores, Mengen, Findings und Zeitpunkte auf dieser Seite sind erfunden. Keine realen Kundendaten, keine Referenz, kein Benchmark, keine Runtime-/Abnahme-Evidence. Zahlen dienen nur der Content- und Layoutprüfung. Produktive Report-Ausgaben müssen Daten, Sichtbarkeiten, Scopes und Entitlements aus dem Backend beziehen.

## Beispiel 1: Free Health Report

**H1:** Ihr Datenqualitätsüberblick  
**Unterzeile:** Aggregierte Hinweise für die erste Einordnung.  
**Kontext (Demo):** Beispiel GmbH · BC Online Sandbox · 10.11.2026 · Scan DEMO-FREE-001  
**Data Health Score (Demo):** 78/100  
**Analysierte Datensätze (Demo):** 24.000  
**Risikobereiche (Demo):** Einkauf 12 Auffälligkeiten · Lager 8 · Finanzen 3  
**Schweregrad-Verteilung (Demo):** Kritisch 2 · Hoch 7 · Mittel 10 · Niedrig 4  
**Business-Impact-Band (Demo):** Hoch

**Management-Einordnung:** Das Beispiel illustriert ein erhöhtes Prüfbedürfnis in Einkauf und Lager. Die aggregierte Darstellung erlaubt noch keine belastbare Aussage über Ursachen oder konkrete Maßnahmen.  
**CTA:** Weitere Prioritäten im Quick Assessment ansehen [nur bei gültigem Access und freigegebenem Kanal].  
**Free Disclosure:** Keine Titel einzelner Findings, Issue-Codes, Datensatzbeispiele, genauen Euro-Werte, Root Causes, vollständigen Handlungsempfehlungen oder verdeckten Detail-Links.

## Beispiel 2: Quick Assessment (festes Zwei-Seiten-Muster)

### Seite 1 – Executive Priorities

**Kontext (Demo):** Beispiel GmbH · BC Online Sandbox · 10.11.2026 · Scan DEMO-QUICK-001  
**Data Health Score:** 78/100 · **Business Impact:** Hoch · **Scan Scope:** 24.000 analysierte Datensätze; 10 Module

**Top 5 priorisierte Findings (sämtlich fiktiv):**

| # | Finding (Kurzbeschreibung) | Schweregrad | Risikobereich | Betroffene Datensätze | Impact-Band | Empfohlener nächster Schritt |
|---|---|---|---|---:|---|---|
| 1 | Unvollständige Zahlungsbedingungen in Lieferantenstammdaten | Hoch | Einkauf | 43 | Sehr hoch | Vollständigkeit der Zahlungsbedingungen fachlich prüfen |
| 2 | Widersprüchliche Lagerplatzreferenzen | Hoch | Lager | 85 | Hoch | Lagerplatzreferenzen mit den verantwortlichen Teams abgleichen |
| 3 | Fehlende Pflichtinformationen in Debitorenstammdaten | Mittel | Verkauf | 27 | Hoch | Betroffene Stammdatenfelder auf Prozessrelevanz prüfen |
| 4 | Uneinheitliche Dimensionenzuordnungen | Mittel | Finanzen | 64 | Moderat | Dimensionsregeln und Zuordnungen vergleichen |
| 5 | Veraltete Kontaktinformationen | Niedrig | Einkauf | 19 | Niedrig | Pflegeprozess für Kontaktdaten überprüfen |

**Management Interpretation:** Zwei der fünf Prioritäten sind als hoch eingestuft. Zwei betreffen den Einkauf. Zwei haben ein hohes oder sehr hohes Impact-Band. Das Ranking bildet modellierte Priorität ab, nicht garantierte Kosten oder Korrekturdauern.

### Seite 2 – Decision & Next Steps

**Severity × Impact Matrix (DEMO):** #1 Hoch/Sehr hoch · #2 Hoch/Hoch · #3 Mittel/Hoch · #4 Mittel/Moderat · #5 Niedrig/Niedrig. Achsen: *Schweregrad* × *Impact-Band*.  
**Empfohlene Reihenfolge:** Erst #1–#2 prüfen; anschließend #3–#4; danach #5. Diese Reihenfolge ist eine priorisierte Sichtung, **keine** bestätigte Umsetzungsplanung.  
**Quick vs Full:** Quick zeigt maximal fünf Titel, Umfang, Severity, Risk Area, Impact-Band und knappe nächste Schritte. Full kann nach gültiger Berechtigung den gesamten Finding-Umfang, detaillierte Ursachen/Empfehlungen und modellierte Euro-Beträge offenlegen.  
**Einzelner Haupt-CTA:** Full Assessment anfragen [nur über freigegebenen Kanal].  
**Quick Disclosure:** Keine exakten EUR-Beträge, Issue-Codes, vollständigen Root Causes, Record-Drilldowns oder vollständigen Remediation-Pläne. Quick allein qualifiziert **nicht** als Validation-Baseline. Das Beispiel folgt der eingefrorenen Zwei-Seiten-Informationsarchitektur aus `docs/QUICK_REPORT_GOLDEN_MASTER.md`, ist aber kein gerenderter PDF-Golden-Master.

## Beispiel 3: Full Assessment / Executive Report

**H1:** Datenqualität und modellierte Geschäftswirkung  
**Kontext (Demo):** Beispiel GmbH · BC Online Sandbox · Scan DEMO-FULL-001  
**Executive Summary:** Das Demo-Assessment zeigt fünf exemplarische Prioritäten. Ein Review sollte zuerst die Einkauf- und Lagerprozesse untersuchen.  
**Data Health Score (Demo):** 78/100  
**Finding-Tabelle:** Dieselben fünf Beispielthemen aus Quick, zusätzlich Platzhalter für Root Cause, vollständige Empfehlung, Verantwortlichkeit nach fachlicher Bestätigung und technische Referenzen – erst im Full-Entitlement sichtbar.

**Illustrative Modellrechnung (Demo, nicht kundenspezifisch):**
- Fiktive betroffene Vorgänge: 100
- Annahme: 15 Minuten pro Vorkommnis × 4 Vorkommnisse pro Jahr × 40 €/Stunde × Wahrscheinlichkeit 50 %
- **Estimated Loss:** 2.000 €/Jahr als modellierter Wert, **kein tatsächlich gebuchter Verlust**
- Annahme Recoverability 40 %: **Potential Saving:** 800 €/Jahr, **keine garantierte oder realisierte Einsparung**

Die Modellparameter dienen nur zur Erklärung von `fin-v1` und sind nicht Teil eines aktuellen Kunden-Reports. Kein ROI-/Realized-Saving-Claim.  
**Management Next Steps:** Datenherkunft und Regeln prüfen; fachliche Verantwortliche benennen; Korrekturen in Business Central durchführen; bei gültiger Full-Baseline eine spätere Validation erwägen.

## Beispiel 4: Validation Report

**H1:** Was hat sich nach der Prüfung verändert?  
**Status:** **Layout-/Inhaltssimulation, kein funktionaler Nachweis der derzeitigen Validation-Pipeline.**  
**Demo-Baseline:** DEMO-FULL-001 · **Demo-Folgescan:** DEMO-VAL-002. Nur bei nachweislich gleicher Company, passendem Scope, gültiger Provenienz und kompatibler Methodik direkt vergleichen.

| Beispiel-Finding | Baseline | Validation | Demo-Klassifikation |
|---|---:|---:|---|
| Fehlende Zahlungsbedingungen | 43 | 15 | Improved |
| Widersprüchliche Lagerplatzreferenzen | 85 | 0 | Resolved |
| Uneinheitliche Dimensionenzuordnungen | 64 | 64 | Remaining |
| Veraltete Kontaktinformationen | 19 | 24 | Regressed |
| Neu erkannte fehlende Adressdetails | 0 | 6 | New |

**Interpretation:** Diese fiktiven Counts zeigen fünf Vergleichsklassen. Sind Scan-Provenienz oder Scope nicht vergleichbar, muss der Report dies ausdrücklich zeigen und darf keinen validierten Delta als gesichert behaupten. Ein modellierter finanzieller Delta wäre selbst bei validiertem Scope **kein Realized Saving**.  
**CTA:** Ergebnisse mit dem BC-Fachteam prüfen.

## Beispiel 5: Monitoring – Konzept, nicht Launch-Funktion

**H1:** Datenqualität über Zeit beobachten  
**Status:** Geplante bzw. separat freizugebende Produktphase, **nicht Teil des ersten kontrollierten Fiverr-Piloten**.  
**Mögliche spätere Ansicht:** Zeitreihe Data Health Score · offene Schwerpunkte · Trends · Scan-Historie · Alerts, soweit entsprechend implementiert und freigegeben.  
**Beispiel-Texte:** „Vergleichen Sie die Entwicklung relevanter Datenqualitätsindikatoren“ / „Untersuchen Sie neue oder wiederkehrende Risiken im Kontext Ihrer Scans.“  
**CTA:** Über die Verfügbarkeit informieren [keine Bestellung ohne freigegebenes Monitoring].

## Visual- und Publikationshinweise

Layout nutzt Product-System Semantic Tokens; Brand Orange für Primary CTA, Blue für Analytik, Amber nur für Warning. Jedes Demo-Beispiel permanent sichtbar als „FIKTIVE BEISPIELDATEN“. Beim Export kein Kundename, keine Echtdaten, keine Übernahme des Beispiels als statistischer Benchmark. Free/Quick dürfen exakte finanzielle Werte **nicht** durch responsives UI, HTML/PDF, Exporte oder Screenreader offenbaren. Für echte Produktberichte ist separates Backend-/PDF-/Visual-QA notwendig.

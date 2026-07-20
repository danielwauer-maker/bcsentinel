# Product Intelligence Model

## Zweck und Geltungsbereich

Das Modell schafft ein dauerhaftes, evidenzbasiertes Vokabular für die spätere Bewertung von Capabilities, Features und Subfeatures. Es enthält keine Bewertung, Priorisierung oder Releasezuordnung bestehender Inventareinträge.

Das [Attribute Dictionary](ATTRIBUTE_DICTIONARY.md) definiert jedes Attribut exakt einmal. Der [Scoring Guide](SCORING_GUIDE.md) definiert Skalen. Das [Readiness Model](READINESS_MODEL.md) beschreibt daraus ableitbare, aber hier nicht berechnete Sichten.

## Modellvertrag

Jede Bewertungseinheit enthält:

- stabile Inventar-ID und Ebene;
- nur anwendbare Fachattribute;
- Governance-Metadaten für Evidenz, Owner, Status, Zeitpunkt und Konfidenz;
- explizites `null` statt geschätzter Werte;
- eine Begründung je gesetztem Fachwert;
- keine automatische Vererbung zwischen Capability, Feature und Subfeature.

## Business

| Attribut | Definition | Zweck | Werte | Generisches Beispiel | Bewertungshinweis |
|---|---|---|---|---|---|
| `business_value` | [Dictionary](ATTRIBUTE_DICTIONARY.md#business-value) | Geschäftsnutzen vergleichbar beschreiben | Level 1–5 | Verkürzt einen zentralen Monatsabschlussprozess | Ergebniswirkung, Reichweite und Dauer betrachten |
| `customer_value` | [Dictionary](ATTRIBUTE_DICTIONARY.md#customer-value) | Direkten Kundennutzen erfassen | Level 1–5 | Verhindert wiederkehrende manuelle Prüfung | Nur wahrnehmbaren Nutzen, nicht interne Eleganz bewerten |
| `revenue_impact` | [Dictionary](ATTRIBUTE_DICTIONARY.md#revenue-impact) | Umsatzbezug transparent machen | Level 1–5 | Voraussetzung eines kostenpflichtigen Leistungsumfangs | Keine Umsatzgarantie ohne belastbare Evidenz |
| `strategic_importance` | [Dictionary](ATTRIBUTE_DICTIONARY.md#strategic-importance) | Langfristige Bedeutung abbilden | Level 1–5 | Schafft eine wiederverwendbare Plattformfähigkeit | Strategiequelle und Zeithorizont nennen |

## Product

| Attribut | Definition | Zweck | Werte | Generisches Beispiel | Bewertungshinweis |
|---|---|---|---|---|---|
| `customer_visibility` | [Dictionary](ATTRIBUTE_DICTIONARY.md#customer-visibility) | Sichtbarkeit der Wirkung unterscheiden | Level 1–5 | Eine primäre Kundenseite ist unmittelbar sichtbar | Auch indirekt sichtbare Fehlerfolgen einbeziehen |
| `pilot_critical` | [Dictionary](ATTRIBUTE_DICTIONARY.md#pilot-critical) | Zwingende Pilotvoraussetzungen markieren | Boolean Gate | Ein vereinbarter Pilotablauf ist sonst nicht durchführbar | Pilotziel muss vor der Bewertung definiert sein |
| `go_live_critical` | [Dictionary](ATTRIBUTE_DICTIONARY.md#go-live-critical) | Zwingende Produktivstartvoraussetzungen markieren | Boolean Gate | Fehlen verhindert einen definierten Produktivbetrieb | Kein Ersatz für Go-Live-Entscheidung |
| `operational_critical` | [Dictionary](ATTRIBUTE_DICTIONARY.md#operational-critical) | Zwingende Regelbetriebsvoraussetzungen markieren | Boolean Gate | Ausfall verhindert den vereinbarten Kernbetrieb | Betriebsmodell und Wiederanlaufziel nennen |

## Quality

| Attribut | Definition | Zweck | Werte | Generisches Beispiel | Bewertungshinweis |
|---|---|---|---|---|---|
| `functional_completeness` | [Dictionary](ATTRIBUTE_DICTIONARY.md#functional-completeness) | Sollumfang und Zustände beurteilen | Level 1–5 | Haupt- und Fehlerpfade sind spezifiziert und umgesetzt | Gegen freigegebenen Scope, nicht Wunschbild bewerten |
| `stability` | [Dictionary](ATTRIBUTE_DICTIONARY.md#stability) | Reproduzierbarkeit und Zuverlässigkeit erfassen | Level 1–5 | Verhalten bleibt unter erwarteten Fehlern kontrolliert | Laufzeit- und Testevidenz unterscheiden |
| `ux` | [Dictionary](ATTRIBUTE_DICTIONARY.md#ux) | Nutzungsqualität abbilden | Level 1–5 | Aufgaben sind verständlich und tastaturbedienbar | Nur bei Nutzerberührung anwenden, sonst `null` |
| `maintainability` | [Dictionary](ATTRIBUTE_DICTIONARY.md#maintainability) | Änderbarkeit langfristig steuern | Level 1–5 | Verantwortlichkeiten und Tests begrenzen Änderungsrisiko | Struktur, Kopplung, Diagnose und Wissen einbeziehen |
| `documentation_quality` | [Dictionary](ATTRIBUTE_DICTIONARY.md#documentation-quality) | Wissensnutzbarkeit erfassen | Level 1–5 | Betrieb und Grenzen sind aktuell dokumentiert | Zielgruppenrelevante Dokumente prüfen |
| `test_coverage` | [Dictionary](ATTRIBUTE_DICTIONARY.md#test-coverage) | Angemessenheit der Prüfung beurteilen | Level 1–5 | Risiko- und Fehlerpfade besitzen passende Tests | Nicht mit reiner Zeilenabdeckung gleichsetzen |

## Security

| Attribut | Definition | Zweck | Werte | Generisches Beispiel | Bewertungshinweis |
|---|---|---|---|---|---|
| `security_criticality` | [Dictionary](ATTRIBUTE_DICTIONARY.md#security-criticality) | Schutzbedarf sichtbar machen | Level 1–5 | Gegenstand kontrolliert privilegierten Zugriff | Threat Context und betroffene Schutzziele nennen |
| `privacy_impact` | [Dictionary](ATTRIBUTE_DICTIONARY.md#privacy-impact) | Datenschutzwirkung einordnen | Level 1–5 | Verarbeitung berührt personenbezogene Identifikatoren | Datenarten, Zweck und Lebenszyklus betrachten |
| `compliance_relevance` | [Dictionary](ATTRIBUTE_DICTIONARY.md#compliance-relevance) | Kontroll- und Nachweispflichten erfassen | Level 1–5 | Gegenstand liefert verpflichtende Auditspur | Konkrete Anforderung statt pauschaler Compliance nennen |

## Planning

| Attribut | Definition | Zweck | Werte | Generisches Beispiel | Bewertungshinweis |
|---|---|---|---|---|---|
| `priority` | [Dictionary](ATTRIBUTE_DICTIONARY.md#priority) | Freigegebene Dringlichkeit ausdrücken | P0–P4 oder `null` | Wird im nächsten Planungshorizont behandelt | Keine automatische Ableitung aus Einzelscores |
| `target_release` | [Dictionary](ATTRIBUTE_DICTIONARY.md#target-release) | Lieferzuordnung referenzieren | Release-ID oder `unassigned` | Zugeordnet zu einem freigegebenen Releasebezeichner | Modelliert keine Roadmap und kein Datum |
| `dependencies` | [Dictionary](ATTRIBUTE_DICTIONARY.md#dependencies) | Voraussetzungen nachvollziehbar machen | Referenzliste | Benötigt eine andere Capability und externen Dienst | Richtung und Art der Abhängigkeit dokumentieren |

## Risk

| Attribut | Definition | Zweck | Werte | Generisches Beispiel | Bewertungshinweis |
|---|---|---|---|---|---|
| `technical_debt` | [Dictionary](ATTRIBUTE_DICTIONARY.md#technical-debt) | Technische Folgekosten sichtbar machen | Level 1–5 | Bekannter Workaround erschwert sichere Änderungen | Nur belegte Kompromisse bewerten |
| `product_risk` | [Dictionary](ATTRIBUTE_DICTIONARY.md#product-risk) | Risiko für Nutzen und Vertrauen erfassen | Level 1–5 | Fehlverhalten erzeugt falsche Kundenaussage | Eintrittskontext und Schadensart nennen |
| `operational_risk` | [Dictionary](ATTRIBUTE_DICTIONARY.md#operational-risk) | Betriebsrisiko erfassen | Level 1–5 | Wiederherstellung oder Beobachtbarkeit ist unzureichend | Betrieb, Ausfall und Recovery gemeinsam betrachten |

## Governance-Metadaten

| Attribut | Definition | Zweck | Werte | Beispiel | Bewertungshinweis |
|---|---|---|---|---|---|
| `assessment_evidence` | [Dictionary](ATTRIBUTE_DICTIONARY.md#assessment-evidence) | Nachvollziehbarkeit sichern | Referenzliste | Codepfad, Test, Messung, Review | Beobachtung und Quelle trennen |
| `assessment_owner` | [Dictionary](ATTRIBUTE_DICTIONARY.md#assessment-owner) | Verantwortung festlegen | Rollenbezeichner | Product, Engineering oder Security Owner | Keine anonyme Freigabe |
| `assessment_status` | [Dictionary](ATTRIBUTE_DICTIONARY.md#assessment-status) | Lifecycle steuern | Status Scale | `reviewed` | Nur freigegebene Werte für Entscheidungen nutzen |
| `last_assessed_at` | [Dictionary](ATTRIBUTE_DICTIONARY.md#last-assessed-at) | Aktualität sichtbar machen | ISO 8601 | Ein datierter Reviewzeitpunkt | Bei Kontextwechsel neu bewerten |
| `assessment_confidence` | [Dictionary](ATTRIBUTE_DICTIONARY.md#assessment-confidence) | Evidenzstärke ausdrücken | Confidence Scale | `medium` | Nicht mit Qualitätswert vermischen |

## Aggregation und Erweiterung

- Das Basismodell definiert keine Gesamtscores, Gewichte oder Prozentwerte.
- Readiness ist eine regelbasierte Sicht, kein arithmetischer Durchschnitt.
- Neue Attribute benötigen eindeutigen Zweck, Owner, Datentyp, Skala, Evidenzanforderung und Abgrenzung zu bestehenden Attributen.
- Erweiterungen werden zuerst im Dictionary definiert und danach in Modell, Guide und Readiness-Verwendung referenziert.
- Entfernte Attribute bleiben für historische Lesbarkeit reserviert und werden nicht unter neuer Bedeutung wiederverwendet.


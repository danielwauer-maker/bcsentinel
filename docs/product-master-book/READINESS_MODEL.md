# Readiness Model

## Zweck

Readiness ist eine kontextgebundene Entscheidungssicht auf freigegebene Product-Intelligence-Attribute. Dieses Dokument definiert keine Berechnung, Schwellenwerte für BCSentinel, Prozentwerte oder aktuelle Bereitschaft.

## Gemeinsamer Vertrag

Jede Readiness-Betrachtung benötigt:

- klaren Gegenstand und Hierarchieebene;
- definierten Zielkontext;
- freigegebene Kriterien und verantwortliche Entscheider;
- aktuelle Evidenz und Assessment-Metadaten;
- dokumentierte Blocker, Bedingungen und Ausnahmen;
- einen der Zustände `not_assessed`, `blocked`, `conditional` oder `ready`.

`ready` ist keine Garantie. Es bedeutet, dass die für den benannten Kontext vorab freigegebenen Kriterien anhand der vorhandenen Evidenz erfüllt sind. `conditional` verlangt benannte, akzeptierte Bedingungen. Readiness-Sichten dürfen nicht gegenseitig ersetzt werden.

## Go-Live Readiness

### Zweck

Beurteilt generisch, ob ein Gegenstand für einen definierten Produktivstart freigegeben werden kann.

### Einflussgrößen

- `go_live_critical`
- `functional_completeness`, `stability`, `test_coverage`
- `security_criticality`, `privacy_impact`, `compliance_relevance`
- `product_risk`, `operational_risk`, `technical_debt`
- relevante Dependencies sowie Dokumentations- und Betriebsnachweise

### Interpretation

Ein kritischer, nicht erfüllter Gate-Gegenstand blockiert. Nicht kritische Abweichungen können nur mit dokumentierter Risikoakzeptanz zu `conditional` führen. Die Sicht ist release- und umgebungsspezifisch.

## Pilot Readiness

### Zweck

Beurteilt generisch, ob ein Gegenstand den zuvor definierten Lern-, Validierungs- oder Nutzungskontext eines Piloten unter kontrollierten Bedingungen unterstützt.

### Einflussgrößen

- `pilot_critical`
- `customer_value`, `customer_visibility`, `functional_completeness`, `ux`
- `stability`, `test_coverage`, `documentation_quality`
- `product_risk`, `operational_risk`
- Pilot-Dependencies, Support- und Feedbackfähigkeit

### Interpretation

Pilot Readiness darf begrenzten Scope akzeptieren, aber keine unkontrollierten Security-, Privacy- oder Compliance-Risiken. Erfolgskriterien und ausgeschlossene Nutzung müssen vorab feststehen.

## Quality Readiness

### Zweck

Beurteilt generisch, ob funktionale und nichtfunktionale Qualität für den definierten Nutzungskontext hinreichend belegt ist.

### Einflussgrößen

- `functional_completeness`, `stability`, `ux`
- `maintainability`, `test_coverage`, `documentation_quality`
- `technical_debt`, `product_risk`
- Assessment Confidence und Aktualität der Evidenz

### Interpretation

Hohe Einzelwerte ersetzen keine fehlende Evidenz in einem kritischen Qualitätsbereich. Quality Readiness ist Voraussetzung für andere Sichten, aber allein keine Pilot- oder Go-Live-Freigabe.

## Operational Readiness

### Zweck

Beurteilt generisch, ob ein Gegenstand in einem definierten Betriebsmodell beobachtet, unterstützt, wiederhergestellt und verantwortet werden kann.

### Einflussgrößen

- `operational_critical`, `operational_risk`, `stability`
- `maintainability`, `documentation_quality`, `test_coverage`
- Security-/Privacy-/Compliance-Relevanz
- Dependencies, Monitoring, Incident Response, Backup/Restore und Owner

### Interpretation

Operational Readiness verlangt geklärte Verantwortung und handhabbare Fehlerpfade. Funktionierendes Normalverhalten ohne Diagnose- und Recovery-Fähigkeit reicht nicht aus.

## Documentation Readiness

### Zweck

Beurteilt generisch, ob die für Zielgruppen und Lifecycle erforderliche Dokumentation auffindbar, korrekt, aktuell und nutzbar ist.

### Einflussgrößen

- `documentation_quality`
- `customer_visibility`, `security_criticality`, `privacy_impact`, `compliance_relevance`
- `operational_critical` und Dependencies
- Owner, Assessment Status, Evidenz und Aktualität

### Interpretation

Erforderliche Dokumenttypen richten sich nach Zielgruppe und Risiko. Vollständige technische Dokumentation ersetzt keine Kunden- oder Betriebsdokumentation und umgekehrt.

## Entscheidungsregeln

- Keine Readiness wird aus einem einzelnen Attribut abgeleitet.
- Keine Readiness wird durch Mittelwertbildung erzeugt.
- Unbewertete kritische Einflussgrößen verhindern `ready`.
- Abweichungen benötigen Owner, Ablaufdatum, Begründung und akzeptierende Rolle.
- Capability Readiness ist eine eigene Kontextentscheidung und keine automatische Aggregation der Kinder.
- Eine Readiness-Aussage verfällt bei wesentlicher Scope-, Architektur-, Umgebungs- oder Evidenzänderung.


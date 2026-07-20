# Attribute Dictionary

## Zweck

Dieses Dokument ist die einzige kanonische Definitionsquelle aller Attribute des Product-Intelligence-Modells. Andere Dokumente verwenden die stabilen Schlüssel und verweisen hierher, statt Definitionen zu wiederholen.

## Konventionen

- Schlüssel sind dauerhaftes `snake_case`; Anzeigenamen dürfen lokalisiert werden.
- `null` bedeutet nicht bewertet und ist kein Skalenwert.
- Bewertungen benötigen Evidenz, Owner und Bewertungsstatus.
- Attribute gelten für Capabilities, Features und Subfeatures, sofern die jeweilige Ebene sinnvoll beurteilbar ist.

## Attribute

### Assessment Confidence

- **Schlüssel:** `assessment_confidence`
- **Definition:** Vertrauensgrad, mit dem die vorliegenden Belege die erfassten Attributwerte tragen.
- **Typ:** Confidence Scale

### Assessment Evidence

- **Schlüssel:** `assessment_evidence`
- **Definition:** Prüfbare Quellen, Beobachtungen und Begründungen, auf denen eine Bewertung beruht.
- **Typ:** Liste strukturierter Referenzen

### Assessment Owner

- **Schlüssel:** `assessment_owner`
- **Definition:** Verantwortliche Rolle oder Organisationseinheit für Inhalt, Aktualität und Freigabe einer Bewertung.
- **Typ:** Rollenbezeichner

### Assessment Status

- **Schlüssel:** `assessment_status`
- **Definition:** Governance-Zustand einer Bewertung von noch nicht vorgenommen bis freigegeben oder veraltet.
- **Typ:** Assessment Status Scale

### Business Value

- **Schlüssel:** `business_value`
- **Definition:** Ausmaß des erwarteten Nutzens für Geschäftsergebnisse, Entscheidungsqualität oder Prozessleistung des Kunden.
- **Typ:** Level Scale

### Compliance Relevance

- **Schlüssel:** `compliance_relevance`
- **Definition:** Bedeutung eines Gegenstands für vertragliche, regulatorische, auditbezogene oder interne Kontrollanforderungen.
- **Typ:** Level Scale

### Customer Value

- **Schlüssel:** `customer_value`
- **Definition:** Direkter, vom Kunden wahrnehmbarer Beitrag zur Problemlösung, Risikoreduktion, Zeitersparnis oder Ergebnisverbesserung.
- **Typ:** Level Scale

### Customer Visibility

- **Schlüssel:** `customer_visibility`
- **Definition:** Grad, in dem Kunden den Gegenstand oder seine Auswirkungen unmittelbar sehen, bedienen oder erleben.
- **Typ:** Level Scale

### Dependencies

- **Schlüssel:** `dependencies`
- **Definition:** Andere identifizierbare Gegenstände oder externe Voraussetzungen, die vor Nutzung, Lieferung oder Betrieb erfüllt sein müssen.
- **Typ:** Liste stabiler Referenzen

### Documentation Quality

- **Schlüssel:** `documentation_quality`
- **Definition:** Qualität, Vollständigkeit, Aktualität und Nutzbarkeit der erforderlichen Produkt-, Technik- und Betriebsdokumentation.
- **Typ:** Level Scale

### Functional Completeness

- **Schlüssel:** `functional_completeness`
- **Definition:** Grad, in dem der vereinbarte funktionale Sollumfang einschließlich relevanter Zustände und Fehlerpfade umgesetzt ist.
- **Typ:** Level Scale

### Go-Live Critical

- **Schlüssel:** `go_live_critical`
- **Definition:** Kennzeichnung, ob das Fehlen oder Versagen des Gegenstands einen definierten Produktivstart zwingend verhindert.
- **Typ:** Boolean Gate

### Last Assessed At

- **Schlüssel:** `last_assessed_at`
- **Definition:** Zeitpunkt, zu dem die Bewertung zuletzt auf Grundlage aktueller Evidenz bestätigt wurde.
- **Typ:** ISO-8601-Zeitstempel

### Maintainability

- **Schlüssel:** `maintainability`
- **Definition:** Fähigkeit, den Gegenstand sicher, verständlich und mit angemessenem Aufwand zu ändern, zu testen und zu betreiben.
- **Typ:** Level Scale

### Operational Critical

- **Schlüssel:** `operational_critical`
- **Definition:** Kennzeichnung, ob das Fehlen oder Versagen des Gegenstands einen vereinbarten Regelbetrieb zwingend verhindert.
- **Typ:** Boolean Gate

### Operational Risk

- **Schlüssel:** `operational_risk`
- **Definition:** Ausmaß möglicher Betriebsbeeinträchtigungen durch Ausfall, Fehlbedienung, unzureichende Wiederherstellung oder fehlende Beobachtbarkeit.
- **Typ:** Level Scale

### Pilot Critical

- **Schlüssel:** `pilot_critical`
- **Definition:** Kennzeichnung, ob das Fehlen oder Versagen des Gegenstands einen zuvor definierten Pilotzweck zwingend verhindert.
- **Typ:** Boolean Gate

### Priority

- **Schlüssel:** `priority`
- **Definition:** Governance-Entscheidung über die relative Bearbeitungsdringlichkeit im aktuell freigegebenen Planungskontext.
- **Typ:** Priority Class

### Privacy Impact

- **Schlüssel:** `privacy_impact`
- **Definition:** Ausmaß der Auswirkungen auf Verarbeitung, Schutz, Offenlegung, Aufbewahrung oder Rechte in Bezug auf personenbezogene Daten.
- **Typ:** Level Scale

### Product Risk

- **Schlüssel:** `product_risk`
- **Definition:** Ausmaß möglicher Schäden für Kundennutzen, Vertrauen, Produktversprechen oder Marktposition durch Fehlfunktion oder falsche Ausgestaltung.
- **Typ:** Level Scale

### Revenue Impact

- **Schlüssel:** `revenue_impact`
- **Definition:** Erwartete Bedeutung für Umsatzgewinnung, Umsatzsicherung, Expansion oder Vermeidung umsatzwirksamer Abwanderung.
- **Typ:** Level Scale

### Security Criticality

- **Schlüssel:** `security_criticality`
- **Definition:** Bedeutung des Gegenstands für Vertraulichkeit, Integrität, Verfügbarkeit, Authentizität oder Mandantentrennung.
- **Typ:** Level Scale

### Stability

- **Schlüssel:** `stability`
- **Definition:** Grad des zuverlässigen und reproduzierbaren Verhaltens unter erwarteten Last-, Daten-, Fehler- und Umgebungsbedingungen.
- **Typ:** Level Scale

### Strategic Importance

- **Schlüssel:** `strategic_importance`
- **Definition:** Beitrag zur langfristigen Positionierung, Differenzierung, Plattformfähigkeit oder zu verbindlichen Unternehmenszielen.
- **Typ:** Level Scale

### Target Release

- **Schlüssel:** `target_release`
- **Definition:** Freigegebener Releasebezeichner, dem die Lieferung eines Gegenstands aktuell zugeordnet ist.
- **Typ:** Release-Referenz oder `unassigned`

### Technical Debt

- **Schlüssel:** `technical_debt`
- **Definition:** Ausmaß bekannter technischer Kompromisse, die zukünftige Änderungen, Qualität, Sicherheit oder Betrieb erschweren.
- **Typ:** Level Scale

### Test Coverage

- **Schlüssel:** `test_coverage`
- **Definition:** Angemessenheit der vorhandenen Tests gegenüber Verhalten, Risiken, Fehlerpfaden, Integrationen und relevanten Umgebungen.
- **Typ:** Level Scale

### UX

- **Schlüssel:** `ux`
- **Definition:** Qualität der Nutzbarkeit, Verständlichkeit, Zugänglichkeit und Konsistenz der betroffenen Nutzererfahrung.
- **Typ:** Level Scale


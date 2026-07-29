# ARCH-02C – Runtime Policy Consistency & Drift Detection

Status: In Progress

## Ziel

Abweichungen zwischen dem kanonischen Produktmodell und den weiterhin aktiven Legacy-Zugriffsflags werden strukturiert sichtbar gemacht, ohne Capability-Entscheidungen oder bestehende Kundenrechte zu verändern.

## Umfang

- versionierte Runtime Policy `arch-02c-v1`
- strukturierte Drift-Erkennung für bezahlte Produkt-, Scan-, Findings-, Report- und Monitoring-Rechte
- `consistency_status`, `drift_count` und `drift_issues` im Product-Model-Snapshot
- Warn-Logging mit Tenant-, Company-, Correlation- und Drift-Code-Kontext
- Snapshot-Version `p0d-v4-runtime-policy-drift`
- fokussierte Regressionstests für konsistente und inkonsistente Zustände

## Sicherheitsgrenze

Die Drift-Erkennung ist rein beobachtend. Sie gewährt und entzieht keine Rechte. Die in ARCH-02B eingeführte doppelte Sicherheitsgrenze bleibt unverändert:

1. kanonisches Offer beziehungsweise Entitlement
2. bestehende Legacy-Freigabe

Free-Ergebnisrechte werden nicht als Paid-Policy-Drift bewertet.

## Nicht Bestandteil

- Entfernung von Legacy-Feldern
- Datenmigration
- Änderung von Checkout-, Stripe- oder Storage-Codes
- automatische Reparatur inkonsistenter Rechte
- Änderung bestehender Kundenrechte

## Abnahmekriterien

- konsistente Assessment-, Validation- und Monitoring-Zustände melden keinen Drift
- widersprüchliche Paid-Zustände werden mit stabilen Drift-Codes gemeldet
- Free Dashboard, Findings und Free Report bleiben unverändert verfügbar
- Capability-Ergebnisse entsprechen ARCH-02B
- vollständige Backend-Regression erfolgreich
- BC-27-AL-Compile, CodeCop und PTECop erfolgreich

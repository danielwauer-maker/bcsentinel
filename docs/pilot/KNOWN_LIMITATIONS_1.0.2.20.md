# BCSentinel Known Limitations – Pilot 1.0.2.20

Diese Liste ist vor jedem Pilot-Onboarding aktiv zu erläutern. Sie ist kein Ersatz für Release Notes oder Vertrag.

## Betrieb

- Der Nachweis eines realen Restore auf der finalen Pilot-/Hosting-Infrastruktur ist noch ausstehend.
- Produktive Alarmzustellung an Daniel plus Ersatzkontakt ist noch nicht vollständig abgenommen.
- Incident- und Backend-Rollback-Drill in der Pilot-Infrastruktur sind noch offen.
- Der 48- bis 72-Stunden-Soak- und 10-Tenant-Lasttest ist noch nicht abgeschlossen.

## Login und E-Mail

- Passwort-vergessen-/Passwortreset ist noch nicht als vollständiger Self-Service-Pfad vorhanden.
- Login-Throttling und zeitweilige Sperre müssen vor einem breiteren Self-Service-Start weiter gehärtet werden.
- SMTP-Retry mit Backoff und Bounce-Verarbeitung sind noch nicht vollständig umgesetzt.
- Reale Zustellung an Gmail und Outlook sowie SPF/DKIM/DMARC müssen vor Kunde 1 geprüft werden.
- Bei Mailausfall ist ein dokumentierter manueller Supportprozess erforderlich.

## Dashboard und Report

- Die technischen Dashboard- und Reportverträge sind verifiziert; die vollständige visuelle Abnahme auf Desktop, Tablet und Mobile steht noch aus.
- Lange Firmennamen, große Geldbeträge, sehr viele Findings und mehrseitige Reports müssen mit realen Pilotdaten abschließend geprüft werden.
- Englische Oberflächen und Reports sind noch nicht vollständig Ende-zu-Ende abgenommen.

## Extension

- Frische Neuinstallation des final freigegebenen APP-Artefakts auf einem leeren Tenant muss noch dokumentiert werden.
- Deinstallation/Reinstallation, Tokenzustand und Datenbeibehaltung benötigen eine formale Pilotcheckliste.
- Renewal-/Ablaufverhalten von Monitoring-Entitlements ist noch nicht vollständig real geprüft.

## Skalierung

- Die Freigabe gilt nicht für zehn gleichzeitig gestartete Kunden.
- Kunden werden in Wellen 1, 2–3, 4–5 und 6–10 aufgenommen.
- Für die Welle 6–10 sind Soak, Last, Operatorbetrieb, Ersatzkontakt und Kapazitätsfreigabe verpflichtend.

## Recht und Kaufmännisches

- Pilotvereinbarung, AVV/DSGVO, Nutzungsbedingungen, Datenschutzerklärung, Impressum und Rechnungsprozess müssen vor Kunde 1 final freigegeben sein.
- Stripe Live, Refunds und Chargebacks sind kein Blocker für betreute Piloten, aber Self-Service-Kauf ist noch nicht freigegeben.

## Zulässige manuelle Kompensation im Pilot

- manuelle Rechnung,
- manuelle Entitlement-/Creditfreischaltung mit Auditnachweis,
- manueller Einladungs- oder Passwortsupport nach Identitätsprüfung,
- eng begleitete Fehlerdiagnose und Kundenkommunikation.

Manuelle Kompensation ist nicht zulässig bei Datenleck, falscher Tenantzuordnung, Datenverlust, doppeltem Creditverbrauch, nicht wiederherstellbarem Betrieb oder fehlender rechtlicher Grundlage.

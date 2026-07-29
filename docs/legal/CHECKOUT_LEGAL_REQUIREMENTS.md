# BCSentinel Checkout – rechtliche Mindestanforderungen

Stand: 29. Juli 2026

## Geltungsbereich

BCSentinel wird ausschließlich Unternehmern im Sinne des § 14 BGB angeboten. Verbraucher werden nicht als Kunden angenommen. Daniel Wauer wendet derzeit die Kleinunternehmerregelung gemäß § 19 UStG an; deutsche Umsatzsteuer wird nicht ausgewiesen.

## Vor Einleitung einer Stripe-Checkout-Session

Der bestellende Kunde muss mindestens folgende Informationen sehen und bestätigen:

- Produktname und Leistungsumfang
- einmalige Zahlung oder wiederkehrendes Abonnement
- Preis in EUR
- Laufzeit, Verlängerung und Kündigungsbedingungen
- Hinweis auf die Kleinunternehmerregelung und den fehlenden deutschen Umsatzsteuerausweis
- ausschließliche B2B-Nutzung
- Nutzungsbedingungen und Datenschutzerklärung

Verbindliche Bestätigung:

> Ich bestätige, dass ich als Unternehmer im Sinne des § 14 BGB und nicht als Verbraucher handle. Ich habe die Nutzungsbedingungen und die Datenschutzerklärung zur Kenntnis genommen.

## Zu erfassende Bestelldaten

- Unternehmensname
- geschäftliche Anschrift
- geschäftliche E-Mail-Adresse
- Ansprechpartner
- gewähltes Produkt und Preis-ID
- Tenant-, Environment- und Company-Kontext, soweit für die Aktivierung erforderlich
- Zeitstempel, Version der Nutzungsbedingungen und Version der Datenschutzerklärung
- bestätigter B2B-Status

Eine Umsatzsteuer-Identifikationsnummer darf optional erfasst werden, ist jedoch keine Voraussetzung für den Unternehmerstatus.

## Technische Durchsetzung

1. Der Backend-Endpunkt darf keine Stripe-Checkout-Session erzeugen, wenn die B2B-Bestätigung fehlt.
2. Produkt und Preis-ID müssen serverseitig aus einer Allowlist aufgelöst werden.
3. Preis, Laufzeit und Produktstatus dürfen nicht aus untrusted Browserwerten übernommen werden.
4. Der bestätigte B2B-Status sowie die Dokumentversionen werden in Checkout-Metadaten oder einer eigenen Bestellreferenz protokolliert.
5. Stripe-Webhooks müssen signiert verifiziert und idempotent verarbeitet werden.
6. Vollständige Karten- oder Bankdaten werden nicht durch BCSentinel gespeichert.
7. Erfolgs- und Abbruchseiten dürfen keinen erfolgreichen Zugriff allein aufgrund von URL-Parametern behaupten; maßgeblich ist der serverseitig verifizierte Zahlungsstatus.

## Sichtbarer Landingpage-Stand

Die Preisreise weist bereits sichtbar auf die ausschließliche B2B-Nutzung und die Kleinunternehmerregelung hin. Vor Aktivierung eines direkten Self-Service-Checkouts ist die serverseitige Bestätigungspflicht nach dieser Datei umzusetzen und automatisiert zu testen.

## Abnahmekriterien

- B2B-Bestätigung ist Pflichtfeld.
- Ohne Bestätigung wird keine Checkout-Session erstellt.
- Nutzungsbedingungen und Datenschutz sind vor Checkout erreichbar.
- Einmalige und wiederkehrende Produkte zeigen die korrekte Laufzeit.
- Kleinunternehmerhinweis erscheint vor Zahlung und auf den BCSentinel-Rechnungsunterlagen.
- Bestellung, Dokumentversionen und Produkt-ID sind revisionsnah nachvollziehbar.

# Landingpage

## Zusammenfassung
Zwei getrennte Vanilla-HTML/CSS/JS-Bäume; `landingpage/` wird in das Backendimage kopiert und operativ referenziert, `landingpage_neu/` besitzt keine gefundene Deploymenteinbindung.

## Erkannte Verantwortlichkeiten
Produktdarstellung, Pricing, Trust/Security, Support/Docs, Rechtstexte, Partnerportal, Billing-Erfolg/Abbruch und DE/EN.

## Erkannte Unterbereiche
Produktwebsite `landingpage/` und alternative Seitenstruktur `landingpage_neu/`.

## Vorhandene Features
WEB-SITE-001, WEB-I18N-001, WEB-PRICE-001.

## Teilweise vorhandene Features
WEB-ALT-001: alternative Website ohne Deploymentnachweis.

## Stubs oder statische Inhalte
WEB-LEGAL-001 und WEB-SUPPORT-001: explizite Platzhalter/MVP-/Mockup-Texte.

## APIs und Schnittstellen
Öffentliche Pricing-/Visibility-/Loss-Config, Partner-API und Checkout-CTAs.

## Datenmodelle
Keine lokale DB; JSON-Sprachdateien und generierter `pricing-snapshot.js`.

## Tests
`test_landingpage_visibility.py`, `test_pricing.py`, `docs/LANDINGPAGE_SMOKE_TEST.md`; keine Browser-E2E-Suite.

## Dokumentation
`landingpage_neu/README.md`, Designkonzepte und Smoke-Test-Dokument.

## Technische Auffälligkeiten
Rechtstext-Platzhalter sind konkret im HTML sichtbar. Das Dockerfile belegt die Paketierung von `landingpage/`, aber keine statisch nachweisbare öffentliche Produktionsauslieferung des Sitebaums.

## Manuell zu prüfen
Welche Website kanonisch und öffentlich ausgeliefert sein soll, Formulare/CTAs, Rechtstexte, mobile/visuelle Qualität.

## Belegverzeichnis
`landingpage/`; `landingpage_neu/`; `backend/Dockerfile`.

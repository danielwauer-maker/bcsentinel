# Customer Experience Readiness

Stand: 2026-07-21

Grundlage: `docs/CUSTOMER_EXPERIENCE_ASSESSMENT.md`

## Entscheidungslogik

Readiness ist eine regelbasierte Sicht, kein Durchschnitt und keine Prozentzahl. Verwendete Zustaende:

- **Ready:** ausreichende positive Evidenz, keine offene Gate-Verletzung.
- **Ready with Conditions:** der vorgesehene Kontext ist nutzbar, wenn explizite Bedingungen kontrolliert werden.
- **Blocked:** mindestens ein notwendiges Gate ist verletzt oder nicht ausreichend belegt.
- **Evidence Missing:** eine belastbare Aussage ist ohne die fehlende Pruefung nicht moeglich.

Die Sichten nutzen die kanonischen Product-Intelligence-Attribute `customer_value`, `business_value`, `customer_visibility`, die Criticality-Gates, die Quality-Attribute und `product_risk`. Sie fuehren keine neue Scorelogik ein.

## Customer Readiness — Ready with Conditions

**Zweck:** Prueft, ob ein neuer Kunde den Nutzen verstehen, einen ersten Erfolg erreichen und einen sinnvollen naechsten Schritt erkennen kann.

**Einflussgroessen:** Landingpage, Free Experience, Onboarding, Overview, Findings, Actions, Texte, Navigation und Trust Signals.

**Interpretation:** Kernnutzen und Ergebnisdarstellung sind verstaendlich. Die Bedingung ist eine betreute Journey, weil direkter Free-Einstieg, Onboarding, Sprachqualitaet und CTA-Ziele nicht durchgaengig freigabefaehig belegt sind.

**Offene Gates:** professionelles DE/EN-Lektorat; kanonischer Einstieg; realer Free-to-Result-Test; keine oeffentlichen MVP-/Placeholder-Inhalte auf dem Pilotpfad.

## Executive Readiness — Ready with Conditions

**Zweck:** Prueft, ob Fuehrungskraefte Zustand, Business-Auswirkung, groesstes Risiko und naechste Entscheidung erfassen koennen.

**Einflussgroessen:** Overview, Executive Experience, Report Presentation, Informationsdichte, Findings, Actions und Trust Signals.

**Interpretation:** Dashboard und Report sind executive-faehig. Die Bedingung ist, dass Scores und Geldwerte Scope, Zeitpunkt, Berechnungsbasis, Unsicherheit und Ausnahmen erklaeren und der Report fachliche Actions vor Kauf-CTAs priorisiert.

**Offene Gates:** Erklaerbarkeit kritischer Kennzahlen; reale Datenmengen im PDF; klare fachliche Top-Actions.

## Commercial Readiness — Blocked

**Zweck:** Prueft, ob Produktwert, Angebot, Preis, Kaufhandlung und Aktivierung eine vertrauenswuerdige Conversion-Kette bilden.

**Einflussgroessen:** Landingpage, Pricing-Kommunikation, CTA, Free Experience, Upgrade Journey, Checkout Experience und Trust Signals.

**Interpretation:** Der wahrgenommene Wert ist hoch, aber der sichtbare Kaufpfad ist widerspruechlich. Pricing-CTAs fuehren zu Kontakt, obwohl einzelne Labels einen Produkt- oder Checkout-Schritt erwarten lassen; der Free Score ist nicht der primaere Einstieg. Interesse ist belegt, Abschlussfaehigkeit nicht.

**Blocker:** wahrheitsgemaesse CTA-Ziele; klare Produktstufen; durchgaengiger Checkout-/Aktivierungs-/Rueckkehrpfad; finale customer-visible Terms/Support-Inhalte.

## Brand Readiness — Blocked

**Zweck:** Prueft, ob alle Beruehrungspunkte wie ein konsistentes, ruhiges und vertrauenswuerdiges Enterprise-Produkt wirken.

**Einflussgroessen:** Branding, Visual Design, Design System, Texte, Report, Portal, Landingpage und Trust Signals.

**Interpretation:** Einzelne Touchpoints sind stark, das Gesamtsystem ist nicht konsistent. Dunkle glaenzende Landingpage, reduziertes technisches Portal, helles Dashboard und flacher Corporate Report wirken wie unterschiedliche Reifestufen. Sichtbare Sprach-, Mockup-, MVP- und Legal-Template-Hinweise verhindern Brand Readiness.

**Blocker:** gemeinsame Brand-Anwendung; Entfernung unfertiger oeffentlicher Inhalte; Locale-Qualitaetsgate; reale statt als Mockup gekennzeichnete Produktbilder.

## Pilot Readiness — Ready with Conditions

**Zweck:** Prueft, ob ein begrenzter, betreuter Pilot mit definiertem Nutzerkreis und klarer Erfolgserwartung vertretbar ist.

**Einflussgroessen:** Customer-, Executive- und Brand-Sicht; Onboarding; Dashboard; Report; Supportpfad; Evidence Confidence.

**Interpretation:** Ein High-Touch-Pilot ist vertretbar, weil Dashboard und Report den Wert demonstrieren. Er ist keine Freigabe fuer einen oeffentlichen Self-Service-Launch.

**Bedingungen:** kuratierte kanonische URL; vorab validierte Demo-/Pilotdaten; persoenlich gefuehrtes Onboarding; definierter Supportkontakt; bereinigte Locale; kundenspezifisch gepruefter Report; dokumentierte bekannte Grenzen; realer Desktop-/Mobile-/Keyboard-Smoke des Pilotpfads.

## Go-Live Readiness — Blocked

**Zweck:** Prueft, ob die gesamte Experience ohne Sonderbetreuung als konsistentes, kommerziell belastbares Enterprise-Produkt freigegeben werden kann.

**Einflussgroessen:** alle bewerteten Capabilities, insbesondere Go-live-Gates, Commercial/Brand Readiness und Live-Evidenz.

**Interpretation:** Nicht freigabefaehig. Die Blockade folgt aus gebrochener Conversion-Journey, vorlaeufigen oeffentlichen Inhalten, Sprachfehlern, fehlender End-to-End-Onboarding-Evidenz und fehlender Browser-/Responsive-/Accessibility-Abnahme.

**Blocker:** Commercial- und Brand-Blocker schliessen; E2E-Journey mit realen Produktzustaenden testen; Accessibility- und Responsive-Nachweise; explainable financial storytelling; Support- und Rechtsinhalte final freigeben.

## Nicht bewertete Readiness

Dieses Dokument trifft keine Aussage ueber Backend-, Security-, Authentication-, Licensing-, Scan-, Monitoring-, Scheduler- oder AppSource-Readiness. Deren Ausschluss darf nicht als positiver Nachweis interpretiert werden.

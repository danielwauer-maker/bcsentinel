# BCSentinel Fiverr Landing + LinkedIn Launch Runbook

Last reviewed: 2026-10-31  
Launch mode: controlled Fiverr pilot.

## Goal

Use the existing BCSentinel landing page and LinkedIn for discovery, while the actual Fiverr order/payment remains on Fiverr. Do not create a separate Fiverr product edition and do not send Fiverr customers to Stripe.

## Landing-page launch state

The current public frontend still uses a waiting-list CTA. Do **not** replace it with an invented or placeholder Fiverr URL.

When the real Gig is published, the primary hero CTA should become:

**Primary CTA:** `BCSentinel auf Fiverr starten`

**Supporting line:** `Kontrollierter Pilot für Microsoft Dynamics 365 Business Central Online.`

**Secondary CTA:** `So funktioniert der Check`

Recommended destination for the primary CTA: the actual published Fiverr Gig URL only.

## Recommended hero copy for pilot mode

### Eyebrow

`BCSentinel · Business Central Data Health`

### H1

`Wie gesund sind deine Business-Central-Daten?`

### Lead

`BCSentinel prüft deine Microsoft Dynamics 365 Business Central Online Daten mit bis zu 199 automatisierten Checks in 10 Geschäftsbereichen – und macht Risiken, Datenqualität und Business Impact verständlich.`

### Proof points

- `199 automatisierte Checks`
- `10 Geschäftsbereiche`
- `Free Health Report`
- `Assessment mit 7 Tagen Detailzugriff`
- `Validation nach der Optimierung`

### Primary CTA

`BCSentinel auf Fiverr starten`

### Trust note below CTA

`Bestellung und Bezahlung erfolgen über Fiverr. Die technische Analyse läuft über die reguläre BCSentinel-Plattform.`

## Product-flow section

### 1. Data Health Check

`Ein vollständiger Data Health Scan analysiert die aktivierten Business-Central-Bereiche. Der Einstieg zeigt Score, Severity, Risikobereiche und Impact Band – ohne kostenpflichtige Detailfindings.`

### 2. Full Assessment

`Das Assessment schaltet den vorhandenen Scan für 7 Tage vollständig frei: konkrete Findings, betroffene Datensätze, modellierter Business Impact, Ursachen-Kontext und priorisierte Maßnahmen.`

### 3. Validation

`Nach deinen Verbesserungen wird ein neuer vollständiger Scan ausgeführt. Der Validation Report zeigt, was behoben, verbessert, unverändert, schlechter oder neu ist.`

## Assessment CTA section

**Heading:** `Vom Datenproblem zur priorisierten Maßnahmenliste`

**Copy:** `Der Health Check zeigt, wo Risiken liegen. Das Full Assessment zeigt, was dahintersteckt, welchen modellierten Business Impact die Findings haben und welche Maßnahmen zuerst sinnvoll sind.`

**CTA:** `Full Assessment über Fiverr starten`

## Validation section

**Heading:** `Verbesserungen messbar machen`

**Copy:** `Validation ist kein zweiter Erstcheck. Sie ist der Folgeschritt nach einem bezahlten Assessment und vergleicht einen neuen Scan mit deiner Assessment-Baseline.`

**CTA:** `Validation nach dem Assessment anfragen`

This CTA should still route to Fiverr messaging/order flow, not to an external checkout.

## Footer / compliance

For controlled Fiverr-pilot traffic:

- keep legal/privacy links on BCSentinel;
- no direct Stripe checkout should be the primary CTA for Fiverr-pilot pages;
- do not imply Fiverr endorsement or partnership;
- do not use Fiverr logos unless current brand permissions clearly allow it;
- do not use a Fiverr customer conversation to move payment or commercial communication off-platform.

## Safe frontend implementation pattern

Recommended implementation after the real Gig URL exists:

1. Add an environment variable such as `VITE_FIVERR_GIG_URL`.
2. When set, render the Fiverr pilot CTA in the hero and relevant product sections.
3. When unset, retain the existing waiting-list/default direct-channel behavior.
4. Open Fiverr in a normal external link with appropriate `rel="noopener noreferrer"`.
5. Do not hard-code a temporary or guessed Fiverr URL.

This pattern keeps the same frontend for Fiverr and direct SaaS traffic and avoids a separate landing-page fork.

## LinkedIn launch strategy

Publish only after:

- final RC is promoted to PROD,
- real BC Online E2E is green,
- Gig is actually published,
- real Fiverr URL is available,
- sample report visuals have passed manual visual QA.

Use an anonymized report visual as the primary image. Prefer score/business-impact cards over a generic logo post.

## LinkedIn post — German default

**Hook:**

`Wie gesund sind eigentlich die Daten in einem Business-Central-System?`

**Post:**

`Viele Probleme in Microsoft Dynamics 365 Business Central wirken zunächst wie einzelne Stammdatenfehler oder Prozessausnahmen.`

`In Summe können daraus aber unzuverlässige Reports, unnötige manuelle Arbeit und vermeidbarer Business Impact entstehen.`

`Genau dafür habe ich BCSentinel entwickelt.`

`BCSentinel führt einen strukturierten Data Health Scan über bis zu 10 Geschäftsbereiche mit 199 automatisierten Checks durch und verdichtet die Ergebnisse zu einem Data Health Score.`

`Im Full Assessment kommen konkrete Findings, betroffene Datensätze, modellierter Estimated Loss / Potential Saving und priorisierte Maßnahmen hinzu.`

`Nach der Optimierung kann eine Validation zeigen, was wirklich besser geworden ist – inklusive Before/After-Vergleich.`

`Ich starte jetzt einen kontrollierten Pilot für Business Central Online über Fiverr.`

`Clean Data – Higher Impact.`

`#BusinessCentral #Dynamics365 #DataQuality #ERP #PowerBI`

Add the actual Fiverr link through LinkedIn's supported link surface at publication time. Do not publish a placeholder link.

## LinkedIn post — shorter version

`Business Central kann technisch sauber laufen – und trotzdem schlechte Datenqualität haben.`

`BCSentinel prüft bis zu 10 Geschäftsbereiche mit 199 automatisierten Checks und macht daraus einen Data Health Score, Risikobereiche und einen verständlichen Business-Impact-Blick.`

`Das Full Assessment liefert konkrete Findings und priorisierte Maßnahmen. Nach der Optimierung zeigt Validation den Before/After-Effekt.`

`Der kontrollierte BCSentinel Pilot für Business Central Online startet über Fiverr.`

`Clean Data – Higher Impact.`

`#BusinessCentral #DataQuality #Dynamics365 #ERP`

## LinkedIn post — English option

`How healthy is the data inside a Business Central environment?`

`Data-quality issues often look like isolated master-data problems or process exceptions. In combination, they can create unreliable reporting, manual work and avoidable business impact.`

`BCSentinel runs a structured Data Health Scan across up to 10 Business Central areas using 199 automated checks and turns the result into a clear Data Health Score.`

`The Full Assessment adds detailed findings, affected records, modeled Estimated Loss / Potential Saving and prioritized actions. After remediation, Validation measures what actually improved.`

`I am opening a controlled Business Central Online pilot through Fiverr.`

`Clean Data – Higher Impact.`

`#BusinessCentral #Dynamics365 #DataQuality #ERP`

## Recommended LinkedIn visual

Use a single clean 16:9 or 1.91:1 visual based on the Assessment Report:

- left: `Data Health Score 68/100` example,
- center: severity distribution,
- right: `Business Impact` and `Top Priority`,
- footer: `199 checks · 10 business areas`,
- small label: `Example / anonymized data`.

Avoid a dense screenshot of the whole PDF. The visual should communicate the product in under two seconds.

## Launch-day sequence

1. Final PROD E2E completes successfully.
2. Publish Fiverr Gig and verify its public URL.
3. Execute one real order dry-run / controlled test through Fiverr.
4. Set the real Fiverr URL in the landing-page pilot CTA configuration and deploy the frontend.
5. Verify landing CTA on desktop/mobile and confirm it opens the correct Fiverr Gig.
6. Publish LinkedIn launch post with anonymized report visual.
7. Watch only operational signals during the first pilot orders: registration, scan completion, lifecycle delivery, operator grants, report access and Fiverr delivery.

## What not to automate

- Do not scrape Fiverr orders/messages.
- Do not auto-grant a product based on an unverified external event.
- Do not publish LinkedIn before PROD/Gig readiness.
- Do not hard-code temporary Fiverr URLs.
- Do not redirect a Fiverr-origin purchase to Stripe.

## Manual inputs required to activate this runbook

- actual public Fiverr Gig URL,
- final approved report visual,
- final PROD release ref,
- confirmation that the real Fiverr order dry-run passed.

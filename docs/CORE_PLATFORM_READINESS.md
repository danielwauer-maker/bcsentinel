# Core Platform Readiness

## Assessment Basis

Diese Readiness-Sicht verwendet ausschließlich die Evidenz und Authority-Stände aus [Core Platform Assessment](CORE_PLATFORM_ASSESSMENT.md). Sie berechnet keine Prozentzahl und keinen Gesamtscore. Nicht commitierte Arbeitsbaumänderungen sind ausgeschlossen.

## Pilot Readiness: Conditional

Die Core Platform besitzt genug funktionale Substanz für einen streng kontrollierten Enterprise-Pilot: Registrierung, Tenantauthentifizierung, Entitlements, Checkout/Webhooks, Credits, Health und Observability sind implementiert und breit durch Python-Tests gestützt.

Ein Pilot ist jedoch erst vertretbar, wenn folgende Bedingungen vor Aufnahme des Kunden nachgewiesen sind:

- reale BC-Sandbox-Installation, Registrierung, Lizenzabruf und Wiederholungs-/Fehlerpfade;
- native AL-Testbasis oder gleichwertiges reproduzierbares Plattform-Gate;
- PostgreSQL-Lauf für Tenantparallelität, Credits und Migrationen;
- Stripe-Testmode-End-to-End für Kauf, Abo, Webhook, Fehler, Kündigung und Portal;
- Staging-Nachweis der Tenantisolation und Autorisierungs-Negativfälle;
- gehärteter, streng begrenzter Adminzugang;
- CI-Testgate auf dem exakt zu pilotierenden Commit;
- benannte On-call-/Supportverantwortung und Rollback-/Recoveryverfahren.

Akzeptierbar sind für einen begrenzten Pilot: ein modularer Monolith, ein einzelner kontrollierter Betriebsstandort und manuell begleitete Abläufe. Nicht akzeptierbar sind ungeprüfte Tenantgrenzen, echte Zahlungen ohne Reconciliation oder ein Pilot auf nicht reproduzierbar getestetem Code.

## Go-Live Readiness: Blocked

Ein allgemeiner Produktivstart ist nicht evidenzbasiert freigabefähig. Blockierend sind:

- fehlende CI-Testausführung;
- fehlende native AL-Regression und aktuelle Sandboxabnahme;
- keine reale Stripe-/Subscription-Lifecycle-Evidenz;
- fehlende zentrale IAM-/Autorisierungs- und Admin-RBAC-Governance;
- fehlender API-Versionierungs-/Compatibility-Vertrag;
- kein nachgewiesener Mehrinstanz-/Worker-/Recovery-Betrieb;
- Migrationsgleichheit wird in Standardtests nicht durchgehend geprüft;
- keine nachgewiesene Billing Reconciliation und Event-Recovery;
- keine kontrollierte Konfigurationspromotion mit Rollback/Vier-Augen-Prinzip;
- driftender Product-Master-Book-Stand gegenüber Repository-HEAD.

`Blocked` ist keine Aussage, dass die Funktionen fehlen. Es bedeutet, dass die für Enterprise-Produktivverantwortung erforderliche Beweiskette nicht geschlossen ist.

## Architecture Readiness: Conditional

Positiv:

- klare FastAPI-Router, Services, Schemas und SQLAlchemy-Persistenz;
- lineare Migrationen und tenantgebundene Datenmodelle;
- idempotente Registrierung, Webhooks und atomare Creditverarbeitung;
- Security-Module für Tenantauth, Hashing, CSRF und URL-Policy;
- native BC-Lifecycle-Codeunits.

Offen:

- Product System definiert keine hinreichend konkrete technische Enterprise-Zielarchitektur für Core Platform;
- kein belegtes API-Lifecycle-/Versionierungsmodell;
- heterogene Authmodelle ohne gemeinsames IAM-Zielbild;
- Autorisierung verteilt statt zentraler Policy;
- In-Process-Hintergrundarbeit ohne freigegebenes Skalierungsmodell;
- Billing-/Subscription-Reconciliation und Configuration Governance fehlen als Architekturverträge.

Die Architektur ist für einen begrenzten Pilot plausibel, aber noch nicht als global skalierbare SaaS-Basis freigegeben.

## Quality Readiness: Conditional

Die Python-Testbasis ist substanziell. Master Book und Repository belegen Tests für Registrierung, Tenantgrenzen, Billing, Entitlements, Credits, Security, Health und Recovery. Gleichzeitig fehlt die automatische Ausführung im Deploymentworkflow. Native AL-Tests fehlen, PostgreSQL- und reale Providerausführung sind nicht geschlossen, und das Master Book ist quantitativ hinter HEAD.

Quality Readiness kann für einen Pilot erst nach einem reproduzierbaren Release-Candidate-Lauf auf `ready` wechseln. Für allgemeinen Go-Live bleibt sie blockierend.

## Operational Readiness: Blocked

Health-/Readiness-Endpunkte, strukturierte Logs, Request IDs, Startupvalidierung und Deploymenthealthchecks sind gute Grundlagen. Nicht nachgewiesen sind jedoch:

- Mehrinstanzverhalten und verteilte Hintergrundverarbeitung;
- zentrale Log-/Metric-/Alert-Infrastruktur und SLOs;
- Billing- und Subscription-Reconciliation;
- vollständige Backup-/Restore-Automation und aktueller Drill;
- Incident Response, On-call, Eskalation und Kundenkommunikation;
- Konfigurationspromotion, Rollback und Secretrotation;
- Kapazitäts-/Lastprofil für tausende Kunden.

Da Operations als Capability außerhalb des Assessmentscopes liegt, können diese Nachweise nicht positiv hergeleitet werden. Fehlende Evidenz ist nach Assessmentregel ein Finding und blockiert eine unbedingte Freigabe.

## Documentation Readiness: Conditional

Das Master Book und zahlreiche technische Audits machen den Core gut nachvollziehbar. Die Knowledge Architecture ist stärker als bei typischen frühen Produkten. Für Enterprise-Verantwortung fehlen oder driften jedoch:

- technische Zielarchitektur der Core Platform;
- IAM-/RBAC- und Token-Lifecycle-Policy;
- API Compatibility Policy;
- Billing Reconciliation und Provider-Runbook;
- Konfigurationsgovernance;
- synchroner Inventarstand zum freigegebenen Commit.

## Decision

Die Core Platform ist **bedingt pilotfähig**, nicht allgemein go-live-fähig. Der erste Pilot darf nur als kontrollierte, explizit begrenzte Lern- und Lieferbeziehung mit geschlossenen P0-Gates starten.


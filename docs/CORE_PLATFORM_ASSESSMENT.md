# Core Platform Assessment

## Assessment Contract

Bewertet wird der freigegebene Stand vom 21. Juli 2026 nach dem Authority Model aus BOOK-000D:

1. Product System (Soll), Commit `449702963f500096bce1837f4da69b84db7f99d0`
2. Product Master Book (Ist), zuletzt Commit `01896a70f6bc439284d7ae34d88df3b3684cec9e`
3. BCSentinel Repository (Verifikation), HEAD `46a898934a488f74afb95109437c0b24292e7994`

Nicht commitierte Arbeitsbaumänderungen sind keine freigegebene Evidenz und wurden nicht bewertet. Skalen und Attribute folgen [Product Intelligence Model](product-master-book/PRODUCT_INTELLIGENCE_MODEL.md), [Scoring Guide](product-master-book/SCORING_GUIDE.md) und [Attribute Dictionary](product-master-book/ATTRIBUTE_DICTIONARY.md). `Architecture Quality` wird mangels kanonischem Attribut narrativ geprüft. `Business Risk` wird nicht neu erfunden, sondern durch `product_risk` und `operational_risk` abgedeckt. `Documentation` entspricht `documentation_quality`, `Pilot/Go-Live Criticality` den Boolean Gates.

### Bewertungslegende

- Level 1–5 entspricht dem Scoring Guide; bei Qualität ist 5 stark, bei Risiko/Kritikalität ist 5 hoch.
- Gates verwenden `true`, `false` oder `null`.
- Readiness ist `ready`, `conditional`, `blocked` oder `not_assessed` und kein Score.
- Alle Bewertungen sind `draft`, Owner `Chief Product Architect`, `last_assessed_at: 2026-07-21`, sofern nicht anders angegeben.

## Evidence Bundles

Jede Tabellenzeile referenziert ein Bundle mit allen drei Authority-Ebenen.

- **E-BACK:** PS `00-core/PRODUCT_ARCHITECTURE.md`, `PRODUCT_PRINCIPLES.md`; PB `BACK-CAP-001`, `BACK-OBS-001`, `BACK-HEALTH-001`, `BACK-JOB-001`, `GAP-OPS-002`; Repo `backend/app/main.py`, `backend/app/services/`, `docker-compose.prod.yml`, `.github/workflows/deploy.yml`.
- **E-EXT:** PS `03-ux/BC_EXTENSION_UX.md`, `PRODUCT_PRINCIPLES.md`; PB `EXT-CAP-001`, `EXT-REG-001`, `EXT-INSTALL-001`, `EXT-UPG-001`, `TEST-AL-001`; Repo `bc-extension/app.json`, `bc-extension/app/src/`, `bc-extension/Translations/`.
- **E-AUTH:** PS `PRODUCT_PRINCIPLES.md`, `AI_CONTEXT.md`; PB `AUTH-CAP-001`, `AUTH-TEN-001`, `AUTH-ADM-001`, `SEC-TEN-001`; Repo `backend/app/security/tenant.py`, `token_hash.py`, `token.py`, `backend/app/routers/admin.py`.
- **E-AUTHZ:** PS `PRODUCT_PRINCIPLES.md` (Trust by Design, Enterprise Ready); PB `SEC-TEN-001`, `BILL-ENT-001`, `AUTH-ADM-001`; Repo `backend/app/security/tenant.py`, `backend/app/services/access_control_service.py`, `entitlement_service.py`, `backend/app/routers/admin.py`.
- **E-REG:** PS `03-ux/ONBOARDING_UX.md`, `BC_EXTENSION_UX.md`; PB `EXT-REG-001`, `BACK-TEN-001`, `WF-REG-001`, `WF-REG-002`; Repo `DHApiClient.Codeunit.al`, `DHTenantIdentityMgt.Codeunit.al`, `tenant_registration_service.py`, migration `0022_tenant_registration_identity.py`.
- **E-LIC:** PS `03-ux/SUBSCRIPTION_UX.md`, `CUSTOMER_JOURNEY.md`; PB `BILL-CAP-001`, `BILL-ENT-001`, `BILL-CREDIT-001`, `WF-LIC-001`, `WF-LIC-002`; Repo `product_license_service.py`, `access_control_service.py`, `atomic_scan_start_service.py`.
- **E-SUB:** PS `03-ux/SUBSCRIPTION_UX.md`; PB `BILL-PORTAL-001`, `BILL-ENT-001`, `WF-BILL-003`; Repo `backend/app/routers/billing.py`, `billing_service.py`, `models.py`.
- **E-BILL:** PS `03-ux/SUBSCRIPTION_UX.md`, `PRODUCT_PRINCIPLES.md`; PB `BILL-CHECK-001`, `BILL-WEB-001`, `BILL-PRICE-001`, `WF-BILL-001` bis `WF-BILL-004`; Repo `backend/app/routers/billing.py`, `billing_service.py`, `product_pricing_service.py`, Tests `test_billing.py` und `test_pricing.py`.
- **E-API:** PS `00-core/PRODUCT_ARCHITECTURE.md`, `SYSTEM_ARCHITECTURE.md`; PB `BACK-CAP-001`, `evidence/api-endpoints.md`; Repo `backend/app/main.py`, `backend/app/routers/`, `backend/app/schemas/`.
- **E-CONF:** PS `PRODUCT_ARCHITECTURE.md` (Admin Portal), `PRODUCT_PRINCIPLES.md`; PB `ADM-CONF-001`, `BILL-PRICE-001`; Repo `backend/app/routers/admin.py`, `backend/app/models.py`, `config/pricing_canonical.json`, `backend/app/core/settings.py`.

## Backend

### Reviews

- **Executive Summary:** Substanzieller FastAPI-Monolith mit klaren Services, Persistenz, Health und Observability; für einen kontrollierten Pilot tragfähig, für globalen Mehrinstanzbetrieb nicht ausreichend belegt.
- **Architecture Review:** Gute modulare Trennung innerhalb eines Monolithen. In-Process-Recovery, synchroner DB-Zugriff, fehlende Worker-Topologie und nicht nachgewiesene externe Logaggregation begrenzen Skalierung und Failure Isolation.
- **Business Review:** Backend ist Voraussetzung nahezu jedes Kunden- und Umsatzflusses, aber für Kunden nur indirekt sichtbar.
- **Quality Review:** Breite Pytest-Basis und Healthchecks sind positiv; CI führt keine Tests aus, Standardtests umgehen teilweise Migrationen.
- **Risk Review:** Größtes Risiko ist nicht Funktionsbreite, sondern Betriebs- und Releaseevidenz unter Mehrinstanzlast.
- **Readiness Review:** Pilot `conditional`; Go-Live `blocked`; Quality `conditional`; Operational `blocked`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Trägt alle Kerntransaktionen und Mandantenprozesse. | E-BACK |
| Customer Value | 4 | Kundennutzen entsteht indirekt durch verlässliche Services. | E-BACK |
| Revenue Impact | 5 | Registrierung, Lizenzierung und Billing hängen am Backend. | E-BACK |
| Strategic Importance | 5 | Zentrale Plattformbasis für jede Skalierung. | E-BACK |
| Customer Visibility | 2 | Technisch verborgen, Ausfälle aber unmittelbar sichtbar. | E-BACK |
| Pilot Critical | true | Ohne Backend kein definierter Core-Pilot. | E-BACK |
| Go-Live Critical | true | Produktivbetrieb ist zwingend davon abhängig. | E-BACK |
| Operational Critical | true | Regelbetrieb endet bei Backendausfall. | E-BACK |
| Functional Completeness | 4 | Kernorchestrierung vorhanden; Enterprise-Betriebsgrenzen bleiben. | E-BACK |
| Stability | 3 | Lifecycle- und Recoverytests vorhanden, Mehrinstanzlauf fehlt. | E-BACK |
| UX | null | Keine eigenständige Nutzeroberfläche in diesem Assessment. | E-BACK |
| Maintainability | 3 | Services modular, Router und Monolith jedoch breit gekoppelt. | E-BACK |
| Documentation Quality | 3 | README/Audits vorhanden, Betriebsarchitektur nicht vollständig. | E-BACK |
| Test Coverage | 4 | Breite Suite, aber keine CI-Ausführung und Migrationslücke. | E-BACK |
| Security Criticality | 5 | Backend verarbeitet Auth-, Tenant-, Billing- und Konfigurationsdaten. | E-BACK |
| Privacy Impact | 4 | Tenant-, Kontakt-, Nutzer- und Betriebsdaten werden verarbeitet. | E-BACK |
| Compliance Relevance | 4 | Auditierbarkeit, Isolation und Verfügbarkeit sind wesentlich. | E-BACK |
| Technical Debt | 3 | In-Process-Jobs und monolithische Betriebsgrenze sind belegt. | E-BACK |
| Operational Risk | 4 | Single-Process-Hintergrundarbeit und fehlende Skalierungsevidenz. | E-BACK |
| Product Risk | 4 | Backendfehler verfälschen Zugriff, Abrechnung oder Datenzustand. | E-BACK |
| Priority | P0 | Pilot- und Unternehmensrisiko erfordern unmittelbare Absicherung. | E-BACK |
| Dependencies | PostgreSQL, Konfiguration, Extension, Stripe | Mehrere harte externe und interne Abhängigkeiten. | E-BACK |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-BACK |

**Empfehlungen:** CI-Gate, produktionsnahe PostgreSQL-/Migrationssuite, Mehrinstanztest und explizite Worker-/Recovery-Entscheidung vor breiterem Betrieb.

## Business Central Extension

### Reviews

- **Executive Summary:** Umfangreiche native AL-Integration mit Setup, Registrierung, Lifecycle und Lokalisierung; die fehlende AL-Test-App und unbestätigte Sandboxausführung verhindern Enterprise-Freigabe.
- **Architecture Review:** Native Codeunits und install/upgrade hooks passen zum BC-Modell. Clientlogik, API-Vertrag und Runtimeverhalten sind jedoch nur teilweise automatisch verifiziert.
- **Business Review:** Primärer Zugang zum Business-Central-Ökosystem und strategischer Differenzierer.
- **Quality Review:** Statische Python-Vertragstests ersetzen keine AL-Test-Codeunits oder reale Plattformausführung.
- **Risk Review:** Höchstes Risiko ist ein Fehler erst in Kundensandbox oder Upgrade.
- **Readiness Review:** Pilot `blocked` bis Sandbox-Abnahme; Go-Live `blocked`; Quality `blocked`; Operational `conditional`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Verankert BCSentinel im operativen Kundensystem. | E-EXT |
| Customer Value | 5 | Ermöglicht native Einrichtung und Nutzung aus BC. | E-EXT |
| Revenue Impact | 5 | Ohne Extension fehlt der primäre Distributions- und Nutzungskanal. | E-EXT |
| Strategic Importance | 5 | Microsoft-Ecosystem-Nähe ist Kernpositionierung. | E-EXT |
| Customer Visibility | 5 | Setup, Status und Fehler werden direkt erlebt. | E-EXT |
| Pilot Critical | true | Der definierte BC-Pilot benötigt die Extension. | E-EXT |
| Go-Live Critical | true | Produktivnutzung in BC hängt davon ab. | E-EXT |
| Operational Critical | true | Kernabläufe starten und enden in der Extension. | E-EXT |
| Functional Completeness | 4 | Lifecycle und Core-Flows vorhanden; Runtimenachweis offen. | E-EXT |
| Stability | 2 | Keine AL-Test-App und keine aktuelle Sandboxausführung belegt. | E-EXT |
| UX | 3 | UX-Regeln und Seiten existieren, reale Usability nicht belegt. | E-EXT |
| Maintainability | 3 | Codeunits strukturiert, automatisierte AL-Regression fehlt. | E-EXT |
| Documentation Quality | 4 | Release-, Upgrade-, UX- und Datenflussdokumente vorhanden. | E-EXT |
| Test Coverage | 2 | Statische Verträge vorhanden, keine nativen AL-Tests. | E-EXT |
| Security Criticality | 5 | Speichert und nutzt Tenantkontext sowie API-Zugang. | E-EXT |
| Privacy Impact | 3 | Unternehmens- und Kontaktkontext wird übertragen. | E-EXT |
| Compliance Relevance | 4 | Berechtigungen, Datenzugriff und Upgrade sind auditrelevant. | E-EXT |
| Technical Debt | 4 | Fehlende native Testinfrastruktur erhöht jede Änderungskosten. | E-EXT |
| Operational Risk | 4 | Plattform-, Berechtigungs- und Upgradefehler treffen Kunden direkt. | E-EXT |
| Product Risk | 5 | Ein BC-Fehler beschädigt Vertrauen in das Gesamtprodukt. | E-EXT |
| Priority | P0 | Native Laufzeitvalidierung ist erste Pilotvoraussetzung. | E-EXT |
| Dependencies | Backend API, BC-Version, Permission Sets, Netzwerk | Harte Plattform- und Serviceabhängigkeiten. | E-EXT |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-EXT |

**Empfehlungen:** Native AL-Test-App, reproduzierbare BC-Sandbox-Abnahme, Permission-Set-Negativtests sowie Install-/Upgrade-Drill.

## Authentication

### Reviews

- **Executive Summary:** Tenanttoken werden gehasht und kontextgebunden geprüft; mehrere Authmodelle existieren. Enterprise Identity Lifecycle und zentrale Rollensteuerung sind nicht vollständig belegt.
- **Architecture Review:** Klare Security-Module, aber Tenanttoken, Dashboardsession, Partner-JWT und Admin Basic bilden heterogene Authdomänen ohne dokumentiertes gemeinsames IAM-Zielbild.
- **Business Review:** Vertrauen und Zugang zu jeder wertschöpfenden Capability hängen davon ab.
- **Quality Review:** Gute Tenanttests; reale Account-, Passwort-, Rotation- und Recoveryabläufe bleiben unsicher.
- **Risk Review:** Fehlende Identity-Governance kann Isolation und Supportskalierung gefährden.
- **Readiness Review:** Pilot `conditional`; Go-Live `blocked`; Quality `conditional`; Operational `conditional`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Sichere Nutzung ist Grundvoraussetzung des SaaS-Angebots. | E-AUTH |
| Customer Value | 5 | Schützt Kundenzugang und Mandantenvertrauen. | E-AUTH |
| Revenue Impact | 5 | Bezahlte Leistungen benötigen verlässliche Identität. | E-AUTH |
| Strategic Importance | 5 | IAM-Fähigkeit bestimmt Enterprise-Skalierbarkeit. | E-AUTH |
| Customer Visibility | 4 | Anmeldung und Zugriffsfehler werden direkt erlebt. | E-AUTH |
| Pilot Critical | true | Kein sicherer Pilot ohne Authentifizierung. | E-AUTH |
| Go-Live Critical | true | Produktionszugang darf nicht ungeklärt sein. | E-AUTH |
| Operational Critical | true | Authausfall blockiert Nutzung und Support. | E-AUTH |
| Functional Completeness | 4 | Mehrere Pfade implementiert; Lifecycle-Governance unvollständig. | E-AUTH |
| Stability | 3 | Breite Tests, reale Accountflüsse nicht bestätigt. | E-AUTH |
| UX | 3 | Login-/Sessionpfade vorhanden; End-to-End-Nutzerprüfung fehlt. | E-AUTH |
| Maintainability | 3 | Getrennte Mechanismen erhöhen Policy- und Supportaufwand. | E-AUTH |
| Documentation Quality | 3 | Datenfluss dokumentiert, IAM-Zielbild und Rotation fehlen. | E-AUTH |
| Test Coverage | 4 | Tenantauth gut getestet; reale Identitätsabläufe offen. | E-AUTH |
| Security Criticality | 5 | Primäre Sicherheitsgrenze der Plattform. | E-AUTH |
| Privacy Impact | 5 | Nutzer-, Kontakt- und Zugangsdaten betroffen. | E-AUTH |
| Compliance Relevance | 5 | Zugriffskontrolle und Nachvollziehbarkeit sind zentral. | E-AUTH |
| Technical Debt | 3 | Heterogene Authmodelle und Legacy-Tokenfallback bestehen. | E-AUTH |
| Operational Risk | 4 | Rotation, Recovery und Supportpfade nicht voll belegt. | E-AUTH |
| Product Risk | 5 | Authfehler können Isolation oder Kundenvertrauen zerstören. | E-AUTH |
| Priority | P0 | Vor Pilot müssen Lifecycle und Adminzugang entschieden sein. | E-AUTH |
| Dependencies | Datenbank, Secret Management, Extension, Browser | Auth hängt von mehreren Vertrauenszonen ab. | E-AUTH |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-AUTH |

**Empfehlungen:** Einheitliches IAM-Zielbild, Tokenrotation/-widerruf, Account-Recovery-Test, Adminzugang härten und zentrale Auditierbarkeit nachweisen.

## Authorization

### Reviews

- **Executive Summary:** Tenantabgleich und Produktentitlements sind stark; feingranulare Rollen und Adminautorisierung bleiben schwach.
- **Architecture Review:** Authorization ist verteilt über Tenant Guards, Memberships, Entitlements und Routerlogik. Eine zentrale Policy-Schicht ist nicht belegt.
- **Business Review:** Verhindert Datenlecks und unberechtigte Nutzung kostenpflichtiger Leistungen.
- **Quality Review:** Tenant- und Gatingtests sind breit, rollenbasierte Negativmatrix fehlt.
- **Risk Review:** Basic Admin ohne rollenfeines Modell ist für globalen Betrieb nicht akzeptabel.
- **Readiness Review:** Pilot `conditional` bei streng begrenztem Adminzugang; Go-Live `blocked`; Quality `conditional`; Operational `blocked`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Schützt Mandanten und monetisierte Leistungsgrenzen. | E-AUTHZ |
| Customer Value | 5 | Sichert Datenisolation und korrekten Zugriff. | E-AUTHZ |
| Revenue Impact | 5 | Entitlements erzwingen kommerzielle Grenzen. | E-AUTHZ |
| Strategic Importance | 5 | Enterprise-Tenancy verlangt belastbare Policies. | E-AUTHZ |
| Customer Visibility | 3 | Gates sichtbar, Policy-Mechanik meist indirekt. | E-AUTHZ |
| Pilot Critical | true | Tenant- und Produktzugriff müssen kontrolliert sein. | E-AUTHZ |
| Go-Live Critical | true | Unautorisierter Zugriff ist ein harter Blocker. | E-AUTHZ |
| Operational Critical | true | Betrieb und Support benötigen sichere Rechte. | E-AUTHZ |
| Functional Completeness | 3 | Tenant-/Produktgates stark, Rollenmodell unvollständig. | E-AUTHZ |
| Stability | 3 | Tests vorhanden, Staging-Mehrtenantentest offen. | E-AUTHZ |
| UX | 3 | Gating vorhanden; Erklärbarkeit rollenbezogener Ablehnung begrenzt. | E-AUTHZ |
| Maintainability | 3 | Verteilte Guards erhöhen Inkonsistenzrisiko. | E-AUTHZ |
| Documentation Quality | 3 | Isolation dokumentiert, Policy-Matrix nicht geschlossen. | E-AUTHZ |
| Test Coverage | 4 | Tenant-/Entitlementtests breit; Rollenmatrix fehlt. | E-AUTHZ |
| Security Criticality | 5 | Direkte Mandanten- und Berechtigungsgrenze. | E-AUTHZ |
| Privacy Impact | 5 | Fehler können fremde Kundendaten offenlegen. | E-AUTHZ |
| Compliance Relevance | 5 | Least Privilege und Zugriffsnachweis sind wesentlich. | E-AUTHZ |
| Technical Debt | 4 | Kein einheitliches rollenfeines Policy-Modell. | E-AUTHZ |
| Operational Risk | 4 | Admin- und Supportzugriffe skalieren nicht belastbar. | E-AUTHZ |
| Product Risk | 5 | Autorisierungsfehler sind existenzielle Vertrauensrisiken. | E-AUTHZ |
| Priority | P0 | Harte Voraussetzung vor externem Enterprise-Zugriff. | E-AUTHZ |
| Dependencies | Authentication, Tenantmodell, Entitlements, Admin | Policies hängen an mehreren Domänen. | E-AUTHZ |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-AUTHZ |

**Empfehlungen:** Zentrale Policy-/Rollenmatrix, Admin-RBAC, systematische Negativtests und Staging-Tenant-Isolation als Pilot-Gate.

## Registration

### Reviews

- **Executive Summary:** Idempotente BC-Identitätsbindung und gehashte stabile Tokens sind technisch stark; reale BC-Registrierung und Recovery bleiben unbestätigt.
- **Architecture Review:** Saubere End-to-End-Kette mit DB-Constraint und Upsert. Stabiles deterministisches Tokenmodell verlangt explizite Rotation-/Kompromittierungsstrategie.
- **Business Review:** Erster Moment des Kundenerlebnisses und Grundlage jeder Tenantbeziehung.
- **Quality Review:** Gute Backend-/Vertragstests, aber keine native BC-Runtimeevidenz.
- **Risk Review:** Fehlerhafte Identitätsbindung kann Mandanten falsch zuordnen; fehlende Rotation erhöht Langzeitrisiko.
- **Readiness Review:** Pilot `blocked` bis Sandbox-End-to-End; Go-Live `blocked`; Quality `conditional`; Operational `conditional`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Erzeugt die belastbare Kunden-/Tenantbeziehung. | E-REG |
| Customer Value | 5 | Ermöglicht sicheren, wiederholbaren Einstieg. | E-REG |
| Revenue Impact | 5 | Ohne registrierten Tenant keine Monetarisierung. | E-REG |
| Strategic Importance | 5 | Skalierbares Onboarding ist Wachstumsvoraussetzung. | E-REG |
| Customer Visibility | 5 | Registrierung ist direkter erster Produktkontakt. | E-REG |
| Pilot Critical | true | Pilottenant muss reproduzierbar registriert werden. | E-REG |
| Go-Live Critical | true | Fehlerhafte Bindung verhindert sicheren Start. | E-REG |
| Operational Critical | true | Support und Zugriff hängen an korrekter Identität. | E-REG |
| Functional Completeness | 4 | Upsert, Constraint und Membership vorhanden; Recovery offen. | E-REG |
| Stability | 3 | Parallelität getestet, BC-End-to-End fehlt. | E-REG |
| UX | 3 | Setupflow spezifiziert, reale Bedienbarkeit nicht belegt. | E-REG |
| Maintainability | 4 | Service und Identity Management klar getrennt. | E-REG |
| Documentation Quality | 4 | Transport, Identität und Ablauf ausführlich dokumentiert. | E-REG |
| Test Coverage | 3 | Backend breit; native Plattform und Recovery fehlen. | E-REG |
| Security Criticality | 5 | Erzeugt Tenantidentität und Zugangstoken. | E-REG |
| Privacy Impact | 4 | Kontakt- und Unternehmensidentität betroffen. | E-REG |
| Compliance Relevance | 4 | Nachvollziehbare Identitätsbindung erforderlich. | E-REG |
| Technical Debt | 3 | Deterministischer stabiler Token benötigt Lifecycle-Kontrolle. | E-REG |
| Operational Risk | 4 | Fehlbindung oder fehlende Recovery blockiert Kunden. | E-REG |
| Product Risk | 5 | Onboardingfehler zerstört frühes Vertrauen. | E-REG |
| Priority | P0 | Vor erstem Pilot vollständig nachzuweisen. | E-REG |
| Dependencies | BC Identity, Backend, PostgreSQL, Netzwerk | Cross-System-Flow mit harten Voraussetzungen. | E-REG |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-REG |

**Empfehlungen:** Sandboxregistrierung inklusive Retry/Recovery, Tokenrotation und Support-Runbook als Pflichtabnahme.

## Licensing

### Reviews

- **Executive Summary:** Differenziertes Entitlement-/Creditmodell mit Ablauf, Transaktionen und frischen Snapshots ist Enterprise-nah; Produktbegriffe und externe Realvalidierung bleiben Risiken.
- **Architecture Review:** Gute Trennung von Preis, Kauf, Entitlement und atomarem Verbrauch. Mehrere Legacy-/Aliaspfade erhöhen Komplexität.
- **Business Review:** Direkte Monetarisierungs- und Produktsteuerung mit sehr hohem Unternehmenswert.
- **Quality Review:** Breite P0-Tests; PostgreSQL-Ausführung und reale Providerkette nicht im Book bestätigt.
- **Risk Review:** Falsche Freischaltung oder Creditbelastung erzeugt Umsatz- und Vertrauensschaden.
- **Readiness Review:** Pilot `conditional`; Go-Live `blocked` bis provider- und PG-E2E; Quality `conditional`; Operational `conditional`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Steuert kommerziellen Leistungszugang. | E-LIC |
| Customer Value | 4 | Macht Umfang und Verbrauch kontrollierbar. | E-LIC |
| Revenue Impact | 5 | Direkte Grundlage von Kauf und Zugang. | E-LIC |
| Strategic Importance | 5 | Ermöglicht skalierbares SaaS-Packaging. | E-LIC |
| Customer Visibility | 4 | Gates, Credits und Ablauf werden erlebt. | E-LIC |
| Pilot Critical | true | Pilotumfang muss eindeutig freigeschaltet sein. | E-LIC |
| Go-Live Critical | true | Falscher Zugang verhindert belastbare Monetarisierung. | E-LIC |
| Operational Critical | true | Zugriffsprüfung ist Laufzeitbestandteil. | E-LIC |
| Functional Completeness | 4 | Entitlements, Credits und Ablauf vorhanden. | E-LIC |
| Stability | 3 | Gute Tests, reale PostgreSQL-/Providerkette offen. | E-LIC |
| UX | 3 | Status lieferbar, Verständlichkeit nicht voll validiert. | E-LIC |
| Maintainability | 3 | Umfangreiche Alias-/Legacylogik erhöht Komplexität. | E-LIC |
| Documentation Quality | 4 | Produktmodell und Testmatrix vorhanden. | E-LIC |
| Test Coverage | 4 | Breite Zugriffs-, Ablauf- und Creditfälle. | E-LIC |
| Security Criticality | 5 | Kontrolliert bezahlte und tenantgebundene Fähigkeiten. | E-LIC |
| Privacy Impact | 3 | Tenant- und Kaufbezug, begrenzte Personendaten. | E-LIC |
| Compliance Relevance | 4 | Abrechnung und Zugriff müssen auditierbar sein. | E-LIC |
| Technical Debt | 3 | Legacyzugriff und Produktaliases bleiben. | E-LIC |
| Operational Risk | 4 | Fehler sperren Kunden oder geben Leistungen frei. | E-LIC |
| Product Risk | 5 | Falsche Gates beschädigen Vertrauen und Umsatz. | E-LIC |
| Priority | P0 | Kommerzielle Korrektheit ist Pilot-Gate. | E-LIC |
| Dependencies | Billing, PostgreSQL, Tenantauth, Produktkonfiguration | Mehrere transaktionale Abhängigkeiten. | E-LIC |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-LIC |

**Empfehlungen:** Produktcode-Taxonomie einfrieren, PostgreSQL-Konkurrenzlauf bestätigen, Freischalt-/Ablauf-E2E und kaufmännische Reconciliation durchführen.

## Subscription

### Reviews

- **Executive Summary:** Subscriptionstatus, Portal und Monitoringperioden sind implementiert; echte Providerzustände, Dunning und Lifecycle-Ausnahmen sind nicht nachgewiesen.
- **Architecture Review:** Providerdaten werden persistiert und in Entitlements übersetzt. Vollständiges Subscription-State-Modell und Reconciliation sind nicht belegt.
- **Business Review:** Grundlage wiederkehrender Umsätze und langfristiger Kundenbindung.
- **Quality Review:** Gute gemockte Status-/Portaltests, keine reale Stripe-Ausführung.
- **Risk Review:** Eventverlust oder falscher Status kann Leistung und Abrechnung entkoppeln.
- **Readiness Review:** Pilot `conditional` im Stripe-Testmodus; Go-Live `blocked`; Quality `conditional`; Operational `blocked`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Trägt wiederkehrendes SaaS-Modell. | E-SUB |
| Customer Value | 4 | Ermöglicht kontinuierlichen Zugang und Selbstverwaltung. | E-SUB |
| Revenue Impact | 5 | Direkter recurring-revenue Mechanismus. | E-SUB |
| Strategic Importance | 5 | Wiederkehrender Umsatz ist Kern des Zielmodells. | E-SUB |
| Customer Visibility | 4 | Status, Portal und Ablauf sind kundensichtbar. | E-SUB |
| Pilot Critical | true | Pilotzugang und Laufzeit müssen kontrolliert sein. | E-SUB |
| Go-Live Critical | true | Produktive Abos verlangen korrekte Zustände. | E-SUB |
| Operational Critical | true | Laufende Berechtigungen hängen davon ab. | E-SUB |
| Functional Completeness | 4 | Portal/Status/Perioden vorhanden; Dunning offen. | E-SUB |
| Stability | 3 | Mocktests vorhanden, Provider-End-to-End fehlt. | E-SUB |
| UX | 3 | Portalzugang vorhanden, realer Kundenflow unbestätigt. | E-SUB |
| Maintainability | 3 | Provider- und interne Statusmodelle müssen synchron bleiben. | E-SUB |
| Documentation Quality | 4 | Matrix und Produktmodell dokumentiert. | E-SUB |
| Test Coverage | 4 | Status-/Portalpfade getestet, externe Zustände fehlen. | E-SUB |
| Security Criticality | 4 | Tenant- und Zahlungszugang betroffen. | E-SUB |
| Privacy Impact | 4 | Kunden-, Provider- und Abrechnungsbezug. | E-SUB |
| Compliance Relevance | 5 | Abrechnung, Kündigung und Status sind auditrelevant. | E-SUB |
| Technical Debt | 3 | Reconciliation-/Dunningmodell nicht nachgewiesen. | E-SUB |
| Operational Risk | 5 | Event- oder Statusdrift kann Kunden falsch berechtigen. | E-SUB |
| Product Risk | 5 | Falscher Abostatus erzeugt direkte Vertrauensschäden. | E-SUB |
| Priority | P0 | Reale Lifecycle-Evidenz vor bezahltem Pilot nötig. | E-SUB |
| Dependencies | Stripe, Billing Webhooks, Entitlements, Tenantauth | Providerabhängiger Lifecycle. | E-SUB |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-SUB |

**Empfehlungen:** Stripe-Testmode-E2E für Start, Renewal, Failure, Cancel und Portal; periodische Reconciliation und Supportverfahren definieren.

## Billing Integration

### Reviews

- **Executive Summary:** Checkout, Signaturprüfung, Webhook-Idempotenz und Preisauflösung sind solide; echte Zahlung und Providerzustellung fehlen als Nachweis.
- **Architecture Review:** Tenantmetadaten, Eventreservierung und DB-Persistenz sind positiv. Manuelle Payloadpfade und komplexe Routerlogik erhöhen Angriffs- und Wartungsfläche.
- **Business Review:** Unmittelbarer Umsatzkanal und kaufmännische Vertrauensgrenze.
- **Quality Review:** Umfangreiche Mocks decken viele Typen; keine echte Provider-/Reconciliation-Evidenz.
- **Risk Review:** Doppelte, verlorene oder falsch zugeordnete Events wirken direkt finanziell.
- **Readiness Review:** Pilot `conditional` nur Testmode; Go-Live `blocked`; Quality `conditional`; Operational `blocked`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Wandelt Produktnutzung in Umsatz um. | E-BILL |
| Customer Value | 4 | Ermöglicht transparenten Kauf und Verwaltung. | E-BILL |
| Revenue Impact | 5 | Direkter Zahlungs- und Freischaltkanal. | E-BILL |
| Strategic Importance | 5 | Automatisierte Monetarisierung skaliert das Unternehmen. | E-BILL |
| Customer Visibility | 5 | Checkout, Erfolg, Fehler und Portal sind direkt sichtbar. | E-BILL |
| Pilot Critical | true | Bezahlter Pilot braucht kontrollierten Billingflow. | E-BILL |
| Go-Live Critical | true | Produktive Zahlung ohne Nachweis unvertretbar. | E-BILL |
| Operational Critical | true | Kauf-/Abozustände steuern Leistung. | E-BILL |
| Functional Completeness | 4 | Kernpfade vorhanden; Reconciliation und Sonderfälle offen. | E-BILL |
| Stability | 3 | Idempotenz getestet, Providerlauf nicht belegt. | E-BILL |
| UX | 3 | Checkoutpfade vorhanden, reale End-to-End-Erfahrung offen. | E-BILL |
| Maintainability | 3 | Großer Router mit Provider- und Geschäftslogik. | E-BILL |
| Documentation Quality | 4 | E2E-Matrix und Pricingquelle vorhanden. | E-BILL |
| Test Coverage | 4 | Viele Mockfälle, keine Live-Testmode-Kette. | E-BILL |
| Security Criticality | 5 | Signaturen, Tenantzuordnung und Secret Keys betroffen. | E-BILL |
| Privacy Impact | 4 | Kunden- und Abrechnungsmetadaten verarbeitet. | E-BILL |
| Compliance Relevance | 5 | Finanzielle Nachvollziehbarkeit und Audit sind zentral. | E-BILL |
| Technical Debt | 3 | Komplexe Routerlogik und manuelle Eventpfade. | E-BILL |
| Operational Risk | 5 | Provider- oder Eventfehler wirken finanziell. | E-BILL |
| Product Risk | 5 | Falsche Belastung/Freischaltung schädigt Marke unmittelbar. | E-BILL |
| Priority | P0 | Vor jeder realen Zahlung vollständig abzusichern. | E-BILL |
| Dependencies | Stripe, PostgreSQL, Pricing, Entitlements, Secrets | Kritische externe Transaktionskette. | E-BILL |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-BILL |

**Empfehlungen:** Provider-Testmode-E2E, Reconciliation, Event-Retry/Dead-letter-Verfahren, finanzielle Auditspur und Runbook vor echter Zahlung.

## API Layer

### Reviews

- **Executive Summary:** Breite funktionsfähige API mit Tenantguards und Schemas; normative Quelle beschreibt den API Layer noch als zukünftige Integrationsfläche. Versionierung, Deprecation und externe SLA sind nicht belegt.
- **Architecture Review:** Router-/Schemaaufteilung ist brauchbar, aber kein kanonischer Enterprise-API-Vertrag, Versionsmodell oder Compatibility Policy vorhanden.
- **Business Review:** Verbindet alle Oberflächen und schafft zukünftiges Integrationspotential.
- **Quality Review:** Viele API-Tests; CI- und Contract-Publishing fehlen.
- **Risk Review:** Unversionierte Verträge können Extension und Kundenintegrationen brechen.
- **Readiness Review:** Pilot `conditional`; Go-Live `blocked` bis Contract-/Compatibility-Gate; Quality `conditional`; Operational `conditional`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 5 | Ermöglicht alle Cross-System-Core-Flows. | E-API |
| Customer Value | 4 | Liefert verlässliche Integration, meist indirekt sichtbar. | E-API |
| Revenue Impact | 4 | Trägt Monetarisierung und künftige Integrationen. | E-API |
| Strategic Importance | 5 | Plattformskalierung verlangt stabile Verträge. | E-API |
| Customer Visibility | 2 | API selbst verborgen, Vertragsfehler direkt spürbar. | E-API |
| Pilot Critical | true | Extension und Billing benötigen API. | E-API |
| Go-Live Critical | true | Produktionsflüsse hängen an API-Verträgen. | E-API |
| Operational Critical | true | Ausfall blockiert Core Platform. | E-API |
| Functional Completeness | 4 | Breite Routen vorhanden; Lifecycle-Governance fehlt. | E-API |
| Stability | 3 | Tests vorhanden, Compatibility-/Lastnachweis fehlt. | E-API |
| UX | null | Kein direkter UI-Gegenstand. | E-API |
| Maintainability | 3 | Module vorhanden, aber breites unversioniertes Surface. | E-API |
| Documentation Quality | 3 | Endpunktinventar vorhanden, kanonischer Vertrag begrenzt. | E-API |
| Test Coverage | 4 | Viele API-Tests, keine CI- oder Consumer-Contracts. | E-API |
| Security Criticality | 5 | Primäre externe Angriffs- und Tenantgrenze. | E-API |
| Privacy Impact | 4 | Transportiert Tenant-, Nutzer- und Geschäftsdaten. | E-API |
| Compliance Relevance | 4 | Zugriff, Audit und Datenverarbeitung relevant. | E-API |
| Technical Debt | 4 | Fehlende Versionierung und Compatibility Policy. | E-API |
| Operational Risk | 4 | Breiter zentraler Ausfall- und Änderungspunkt. | E-API |
| Product Risk | 5 | Contract Breaks können alle Clients stoppen. | E-API |
| Priority | P0 | Contract-Governance vor externem Pilot erforderlich. | E-API |
| Dependencies | Backend, Auth, DB, Clients, Proxy | Zentrale Schnittstelle mehrerer Vertrauenszonen. | E-API |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-API |

**Empfehlungen:** Kanonischen API-Vertrag, Versionierungs-/Deprecation Policy, Consumer-Contract-Tests, Rate-/Size-Limits und Lastprofil definieren.

## Configuration

### Reviews

- **Executive Summary:** Preise, Matrix, Sichtbarkeit und Übersetzungen sind administrierbar; Governance, Vier-Augen-Prinzip, Secret Management und Rollenmodell sind nicht Enterprise-reif belegt.
- **Architecture Review:** DB-basierte Overrides plus Defaults sind flexibel. Admin Basic, verteilte Settings und fehlende Change-Promotion erzeugen Kontrollrisiko.
- **Business Review:** Ermöglicht schnelle Produktsteuerung, kann aber bei Fehlkonfiguration Umsatz und Kundenerlebnis direkt verändern.
- **Quality Review:** Pricing-/Admin-Tests gut; produktionsnahe Freigabe- und Rollbackprozesse fehlen.
- **Risk Review:** Unkontrollierte Konfigurationsänderungen sind ein hoher Blast-Radius.
- **Readiness Review:** Pilot `conditional` bei streng begrenztem Zugriff; Go-Live `blocked`; Quality `conditional`; Operational `blocked`.

| Attribut | Wert | Begründung | Evidenz |
|---|---|---|---|
| Business Value | 4 | Ermöglicht Produkt- und Preissteuerung. | E-CONF |
| Customer Value | 3 | Wirkung indirekt über korrekte Angebote und Inhalte. | E-CONF |
| Revenue Impact | 5 | Preis- und Produktmatrix wirken direkt auf Umsatz. | E-CONF |
| Strategic Importance | 4 | Flexible Steuerung unterstützt Skalierung. | E-CONF |
| Customer Visibility | 3 | Ergebnisse der Konfiguration sind sichtbar. | E-CONF |
| Pilot Critical | true | Pilotpreise und Zugang müssen korrekt sein. | E-CONF |
| Go-Live Critical | true | Fehlkonfiguration kann alle Kunden betreffen. | E-CONF |
| Operational Critical | true | Laufzeitverhalten hängt von Settings/Overrides ab. | E-CONF |
| Functional Completeness | 4 | Viele Adminpfade vorhanden; Governance fehlt. | E-CONF |
| Stability | 3 | Tests vorhanden, Change-Promotion nicht belegt. | E-CONF |
| UX | 3 | Adminoberfläche vorhanden, rollenbezogene UX begrenzt. | E-CONF |
| Maintainability | 3 | Defaults, DB-Overrides und Env-Settings sind verteilt. | E-CONF |
| Documentation Quality | 3 | Pricing gut, Gesamt-Konfigurationsmodell unvollständig. | E-CONF |
| Test Coverage | 4 | Pricing und Adminpfade breit getestet. | E-CONF |
| Security Criticality | 5 | Secrets, Preise und Produktzugriff betroffen. | E-CONF |
| Privacy Impact | 2 | Meist System-/Produktdaten, einzelne Kontaktdaten möglich. | E-CONF |
| Compliance Relevance | 4 | Preis-, Zugriff- und Auditänderungen nachweispflichtig. | E-CONF |
| Technical Debt | 4 | Kein zentrales typisiertes Konfigurations-/Promotionmodell. | E-CONF |
| Operational Risk | 5 | Fehländerung kann systemweiten Blast-Radius haben. | E-CONF |
| Product Risk | 5 | Falsche Preise/Gates schädigen Kundenvertrauen. | E-CONF |
| Priority | P0 | Governance vor externem Betrieb erforderlich. | E-CONF |
| Dependencies | Adminauth, Datenbank, Env Secrets, Pricing, Clients | Mehrere Quellen müssen konsistent bleiben. | E-CONF |
| Target Release | unassigned | Keine freigegebene Releasezuordnung nachgewiesen. | E-CONF |

**Empfehlungen:** RBAC und Vier-Augen-Freigabe, typisierte Konfigurationsquelle, Audit/Rollback, Environment-Promotion und Secret-Management-Nachweis.

## Cross-Capability Findings

1. **Evidence Missing:** Product System besitzt Prinzipien und Produktoberflächen, aber keine freigegebene technische Zielarchitektur für IAM, API Lifecycle, Multi-Instance, Billing Reconciliation oder Configuration Governance.
2. **Inventory Drift:** Master Book nennt 27 Testdateien, 224 Testfunktionen und 25 Migrationen; Repository-HEAD enthält 28 Testdateien, 247 Testfunktionen und 26 Migrationen. Der Ist-Index ist damit nicht auf HEAD synchron.
3. **Release Evidence Missing:** Alle zehn Assessment Units haben `target_release: unassigned`; das ist keine Roadmapforderung, sondern fehlende Zuordnungsevidenz.
4. **Execution Evidence Missing:** Kein CI-Testjob, keine native AL-Test-App, keine bestätigte reale Stripe-Zahlung und kein aktueller BC-Sandbox-Nachweis.
5. **Architecture Boundary:** Der Core ist funktional breit, doch Worker-, IAM-, API-Versionierungs-, Reconciliation- und Configuration-Governance sind nicht als Enterprise-Verträge belegt.

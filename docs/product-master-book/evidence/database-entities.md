# Datenbank-Entitäten

Quelle: `backend/app/models.py`; Migrationen: `backend/alembic/versions/`.

| Entität/Tabelle | Schlüssel und wichtige Felder | Beziehungen/Tenant/Audit |
|---|---|---|
| `Tenant` / `tenants` | `id`, eindeutige `tenant_id`, Tokenhash, Registration Identity, BC-/Entra-Kontext, Plan/Status, Sprache | Wurzel für Scans, Billing, Produkte, Memberships; Created/LastSeen |
| `DashboardUser` | eindeutige/normalisierte E-Mail, Passwort-/Invitehash, Status/Mailstatus | m:n über Membership; Created/Updated |
| `DashboardUserTenantMembership` | Unique User+Tenant, Rolle, aktiv, last selected | FK User/Tenant; Created/Updated |
| `Scan` | eindeutige `scan_id`, Score/KPIs/Modulscores/Counts | FK Tenant; Issues, Cascadebezug im ORM |
| `ScanIssueRecord` | Unique Scan+Code, Severity, Count, Impact | FK Scan |
| `ScanRunStatus` | eindeutige `run_id`, Status, Fortschritt, Lease, Retry, Correlation, Result timestamp | FK Tenant; Module/Events |
| `ScanRunModule` | Unique Run+Name, Status/Progress | FK Run |
| `ScanRunEvent` | Zeit, Level, Eventtype, Attempt/Worker/Correlation | FK Run; Metadaten JSON-Text |
| `IssueCostConfig` | Code PK, Cost, aktiv | globale Konfiguration |
| `IssueImpactConfig` | Code PK, Kategorie/Faktoren | globale Konfiguration |
| `ImpactSettingsConfig` | Key PK, Number/Title | globale Konfiguration |
| `LicensePricingConfig` | Plan PK, Basispreis/Records | globale Konfiguration |
| `ProductPricingConfig` | Product Key PK, Cent/Currency/Interval | Updated timestamp |
| `ProductPricingMatrixConfig` | Product+Tier, Grenze, Price ID, aktiv | Unique Constraint/Indexe; Updated |
| `LandingpagePageVisibility` | eindeutiger Page Key, sichtbar | Created/Updated |
| `Subscription` | eindeutige Provider Subscription ID, Status/Periode | FK Tenant; Created/Updated |
| `Invoice` | eindeutige Provider Invoice ID, Beträge/URL | FK Tenant; Created/Paid |
| `TenantProductPurchase` | Provider Checkout/Payment, Produkt/Status | FK Tenant; Created/Updated |
| `TenantScanCredit` | Produkt/Status, Grant/Consume/Ablauf | FK Tenant; Creditbestand als Zeilen |
| `ScanStartRequest` | eindeutige Client Request ID, Run/Produkt/Status | FK Tenant; Idempotenz |
| `CreditLedgerEntry` | Delta/Balance/Reason/Request | FK Tenant; Auditspur |
| `TenantProductEntitlement` | Produkt/Status/Quelle/Gültigkeit | FK Tenant; Created/Updated |
| `BillingWebhookEvent` | eindeutige Provider Event ID, Typ/Payload/Processed | Provider-Audit/Idempotenz |
| `Partner` | Code, Credentials/Reset, Status/Konditionen | Referrals/Commissions |
| `PartnerApplication` | Kontakt/Status/Mailstatus | Created/Updated |
| `PartnerReferral` | Partner+Tenant, Status | FKs Partner/Tenant |
| `PartnerCommission` | Partner/Tenant/Invoice/Betrag/Status | FKs; Zeitfelder |
| `AdminAuditEvent` | Actor, Action, Entity, Details, Zeit | Admin-Audit |
| `AdminEmailTemplate` | Template Key, Subject/HTML, aktiv | Updated timestamp |

Die obige Liste führt alle 29 tatsächlich deklarierten ORM-Klassen einzeln auf. Statuswerte sind überwiegend Strings; DB-Enumconstraints wurden nicht als einheitliches Modell gefunden. Löschverhalten ist je Beziehung/Migration zu prüfen und wird nicht pauschal behauptet.

## Migrationskette

`0001` Core; `0002` Commercial/Pricing; `0003` Tokenhash; `0004` Billing; `0005` Partner; `0006` Audit; `0007` Partnerauth; `0008` Applications; `0009` Mailstatus; `0010` Templates; `0011` Modulscores/Kategorie; `0012` Module; `0013` Lifecycle; `0014` Tokenhärtung; `0015` Produktlizenz; `0016` Produktpreise; `0017` Sprache; `0018` Page Visibility; `0019` Preismatrix; `0020` Contact Email; `0021` Dashboarduser; `0022` Registration Identity; `0023` Atomic Credit; `0024` Recovery; `0025` Memberships.

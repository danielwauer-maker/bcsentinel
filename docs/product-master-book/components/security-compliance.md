# Security und Compliance

## Zusammenfassung
Transport-, Token-, Tenant-, CSRF-, Rate-Limit-, URL-, Header- und Entitlementkontrollen sind im Code vorhanden; Compliance umfasst zusätzlich Dokumentation.

## Erkannte Verantwortlichkeiten
Tenantisolation, Secret-/Tokenhashing, sichere URLs/HTTPS, Sessions, CSRF, Adminauth, Audit, Datenschutz und Retention.

## Erkannte Unterbereiche
`backend/app/security/`, Middleware in `main.py`, AL URL/Secret/Access Guards, Privacy-Dokumente.

## Vorhandene Features
SEC-TEN-001, SEC-TRANS-001, SEC-CSRF-001, SEC-RATE-001, SEC-AUDIT-001.

## Teilweise vorhandene Features
SEC-COMP-001: Richtlinien dokumentiert, externe/fachliche Complianceprüfung nicht nachgewiesen.

## Stubs oder statische Inhalte
Keine Security-Stubs; Rechtstexte enthalten unfertige Platzhalter.

## APIs und Schnittstellen
HTTPS-Proxyheader, Headerauth, Cookies/JWT/Basic, CSRF-Token, Stripe-Signatur.

## Datenmodelle
Tokenhash, AuditEvent, WebhookEvent, Memberships/Entitlements.

## Tests
Security Header, Tenantregistration/isolation, Embed-Security, Transportpolicy, Tokenmigration und PostgreSQL-Konkurrenz.

## Dokumentation
`docs/privacy/`, Data Flow, Role Matrix, P0A/P0D/P0E-Audits.

## Technische Auffälligkeiten
Rate Limit ist ein In-Process-Modul; verteiltes Verhalten über mehrere Backendinstanzen ist nicht belegt.

## Manuell zu prüfen
Penetrationstest, DSGVO-/Legalreview, Secretrotation, verteiltes Rate Limiting und Retentionausführung.

## Belegverzeichnis
Obige Securitymodule, Tests und Dokumente.

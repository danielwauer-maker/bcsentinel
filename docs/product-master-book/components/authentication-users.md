# Authentifizierung und Benutzer

## Zusammenfassung
Vier Zugriffsmodelle: Tenant-Header/Token, Dashboarduser/-session, Partner-JWT und Admin HTTP Basic.

## Erkannte Verantwortlichkeiten
Registrierung, Tokenhashing/-migration, Einladung/Passwort, Multi-Tenant-Mitgliedschaft, Partnercredentials und Sessions.

## Erkannte Unterbereiche
`security/tenant.py`, `token*.py`, Dashboard-/Partner-/Adminrouter und CSRF.

## Vorhandene Features
AUTH-TEN-001, AUTH-DASH-001, AUTH-PART-001, AUTH-ADM-001.

## Teilweise vorhandene Features
Kein externer Identity Provider ist implementiert; Entra Tenant ID dient als Bindungsmerkmal.

## Stubs oder statische Inhalte
Keine Authentifizierungsstubs gefunden.

## APIs und Schnittstellen
Tenantheader, Cookies, Bearer/JWT, Basic Auth und Form-CSRF.

## Datenmodelle
Tenant, DashboardUser/Membership, Partner sowie Token-/Resetfelder.

## Tests
Tenantregistration, Multi-Tenant-Dashboard, Membershipmigration, Analytics-Security, Admin und Partnerpfade.

## Dokumentation
Data Flow, Role Permission Matrix und P0A-Audit.

## Technische Auffälligkeiten
Legacy-Klartext-Tenanttoken kann bei erfolgreicher Authentifizierung auf Hash migriert werden.

## Manuell zu prüfen
Sessionhärtung, Passwort-/Accountprozesse und reale Rollenabläufe.

## Belegverzeichnis
`backend/app/security/`; relevante Router/Modelle/Migrationen.

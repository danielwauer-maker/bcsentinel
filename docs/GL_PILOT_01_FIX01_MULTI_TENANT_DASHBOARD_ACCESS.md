# GL-PILOT-01-FIX01 – Multi-Tenant Dashboard Access by Contact Email

Stand: 20. Juli 2026  
Branch: `staging`  
Ausgangscommit: `e8145d5bd10fc0182a699daa7aa718e09395ad22`

## Ergebnis

Der gemeldete Konflikt ist auf Code-, Datenbank-, API-, Dashboard- und AL-Ebene behoben. Eine normalisierte E-Mail-Adresse identifiziert nun genau einen Dashboard-Benutzer, der über relationale Memberships mehreren Business-Central-Tenants, Umgebungen und Unternehmen zugeordnet werden kann. Die stabile Tenant-Identität aus Entra Tenant ID, Environment Name, Environment Type und Company System ID bleibt unverändert.

Der nach dem Fix erforderliche manuelle CAT in `BCSentinel-Pilot` / Business Central 28.3 konnte in diesem Lauf nicht ausgeführt werden und bleibt **BLOCKED**. Der Sprint ist damit technisch implementiert und automatisiert verifiziert, aber nach der Definition of Done noch nicht vollständig abgenommen.

## Ausgangsfehler und Root Cause

Die Registrierung antwortete mit `contact_email already belongs to another tenant dashboard user.`. Die Ursache bestand aus drei gekoppelten 1:1-Annahmen:

- `dashboard_users.tenant_id` band einen Benutzer direkt an genau einen Tenant.
- Migration 0022 legte den global eindeutigen Index `uq_dashboard_users_email` an.
- `prepare_dashboard_user()` suchte dieselbe E-Mail in einem anderen Tenant und warf explizit den Konflikt.

Es existierte keine Membership-Tabelle. Der eigenständige Dashboard-Login und Tenant-Wechsel waren noch nicht implementiert. Analytics-Embed-Tokens waren bereits korrekt auf einen Tenant und eine Company gebunden; diese Sicherheitsgrenze wurde beibehalten.

## Datenmodell vorher und nachher

Vorher:

`DashboardUser -> tenant_id -> Tenant` (1:1 aus Benutzersicht)

Nachher:

`DashboardUser 1:n DashboardUserTenantMembership n:1 Tenant`

`DashboardUser` enthält weiterhin Login- und Invite-Daten sowie `email`; hinzugekommen ist das eindeutig indizierte `normalized_email`. Die direkte `tenant_id`-Spalte wurde entfernt.

`DashboardUserTenantMembership` enthält:

- `dashboard_user_id`
- `tenant_id`
- `role`
- `is_active`
- `created_at_utc`, `updated_at_utc`
- `last_selected_at_utc`
- Unique Constraint auf `(dashboard_user_id, tenant_id)`

Bestehende Passwort-Hashes, Invite-Status und Login-Zugangsdaten bleiben am Benutzer erhalten. Tenant-, Scan-, Lizenz-, Credit-, Billing-, Finding- und Reporttabellen wurden nicht verändert.

## Migration 0025

`0025_dashboard_memberships` führt vor jeder Mutation anonymisierte Konsistenzprüfungen aus:

- Dashboard-Benutzer ohne gültigen Tenant
- leere E-Mail-Adressen
- Konflikte nach `lower(trim(email))`

Bei Konflikten bricht die Migration kontrolliert mit ausschließlich aggregierten Zählwerten ab; E-Mail-Adressen werden nicht protokolliert. Anschließend normalisiert sie E-Mails, erzeugt die Membership-Tabelle, backfillt jede bestehende 1:1-Zuordnung als aktive `owner`-Membership und entfernt erst danach die direkte Tenant-Spalte.

Der Downgrade ist nur zulässig, wenn jeder Benutzer wieder exakt eine Membership besitzt. Multi-Tenant-Benutzer führen zu einem kontrollierten Abbruch, statt Zuordnungen still zu verlieren.

Automatisierte SQLite-Evidenz:

- Legacy-Upgrade und Backfill: PASS
- kontrollierter Abbruch bei case-insensitivem E-Mail-Konflikt: PASS
- Downgrade mit einer Membership: PASS
- kontrollierter Downgrade-Abbruch bei mehreren Memberships: PASS

Echte PostgreSQL-15-Evidenz in einer isolierten Testdatenbank:

- Fresh Upgrade bis 0024: PASS
- synthetischer Legacy-Benutzer: 1 Benutzer / 1 Tenant
- 0024→0025: PASS
- danach: 1 Benutzer / 1 Tenant / 1 Membership
- fehlende Normalisierungen, Orphans und Duplikate: jeweils 0
- Downgrade auf 0024 und Re-Upgrade auf 0025: PASS
- temporäre Testdatenbanken anschließend entfernt

Vor einer produktiven Migration ist ein Datenbankbackup Pflicht. Empfohlene Vorher-Zählwerte ohne personenbezogene Daten: Tenants, Dashboard-Benutzer und Konfliktgruppen nach normalisierter E-Mail. Die Produktivmigration wurde nicht ausgeführt.

## Registrierungsablauf und Membership-Logik

1. Tenant anhand der stabilen BC-Identität suchen oder idempotent erzeugen.
2. Dashboard-Benutzer anhand `normalized_email` suchen.
3. Neuen Benutzer nur anlegen, wenn die E-Mail noch nicht existiert.
4. Deaktivierten Benutzer oder deaktivierte bestehende Membership mit stabilem Fehlercode ablehnen.
5. Fehlende Membership anlegen; vorhandene Membership idempotent wiederverwenden.
6. Bei parallelen Inserts Unique Constraints und `IntegrityError` kontrolliert behandeln und nach Rollback erneut auflösen.
7. Einladung nur für einen wirklich neuen Benutzer senden; bestehende Zugangsdaten und Invite-Zustände bleiben unverändert.
8. Additive Response-Felder: `dashboard_user_id`, `membership_id`, `dashboard_access_count`, `existing_dashboard_user`, `membership_created`.

Ein PostgreSQL-Race-Test mit zwei parallelen neuen Tenant-Registrierungen derselben E-Mail erzeugte genau einen Benutzer und zwei eindeutige Memberships.

## Dashboard-Login und Tenant-Auswahl

Neu verfügbar:

- `/dashboard` und `/dashboard/invite` als responsive Login-/Aktivierungs- und Tenant-Auswahlseite
- `POST /dashboard/invite/activate`
- `POST /dashboard/login`
- `POST /dashboard/logout`
- `GET /dashboard/tenants`
- `GET /dashboard/tenant/{tenant_id}`
- `POST /dashboard/tenant/switch`
- `POST /dashboard/analytics-token`

Bei einer Membership wird der Tenant automatisch gewählt. Bei mehreren Memberships zeigt die Seite Company-/Tenantname, Environment Name und Environment Type. `last_selected_at_utc` bestimmt beim nächsten Login die sichere letzte Auswahl. Ein Wechsel stellt ein neues Session-JWT aus und rotiert das HttpOnly-/Secure-/SameSite-Strict-Cookie.

## Autorisierungsmodell

Benutzeridentität und aktiver Tenant sind getrennt. Das Dashboard-Session-JWT enthält `user_id`, `active_tenant_id`, `membership_id` und Rolle, aber keine ungefilterte Tenant-Datenliste. Jeder Zugriff lädt Benutzer, aktive Membership und Tenant erneut aus der Datenbank.

Ein manipulierter `active_tenant_id`-Claim, direkter Fremd-Tenant-Pfad oder Switch ohne Membership endet mit 403 `TENANT_ACCESS_FORBIDDEN`. Der Analytics-Token wird erst nach Membership- und Produktzugriffsprüfung erstellt und bleibt wie zuvor an genau einen Tenant und eine Company gebunden. Damit bleiben Overview, Findings, Scan History, Reports, Lizenzen, Credits, Billing und Embed-Daten im ausgewählten Tenant-Kontext.

Neue Memberships und Tenant-Wechsel werden ohne E-Mail-Adresse im bestehenden Auditlog protokolliert.

## Strukturierte Fehler

Die Registrierung liefert keine Stacktraces und verwendet ein additives Format mit `code`, `message`, `message_de`, `details` und `request_id`. Implementiert oder verwendet werden:

- `REGISTRATION_IDENTITY_CONFLICT`
- `TENANT_MEMBERSHIP_NOT_ALLOWED`
- `TENANT_NOT_FOUND`
- `TENANT_ACCESS_FORBIDDEN`
- `INVALID_REGISTRATION_PAYLOAD`
- `DASHBOARD_USER_DISABLED`
- `TENANT_MEMBERSHIP_DISABLED`
- `REGISTRATION_TEMPORARILY_UNAVAILABLE`
- `REGISTRATION_UNEXPECTED_ERROR`

Pydantic-Validierungsfehler und Rate-Limits auf `/tenant/register` werden ebenfalls strukturiert ausgegeben. Unerwartete technische Details bleiben ausschließlich im Serverlog.

## AL-Fehlermapping und Busy-State

`DH API Client` setzt für die Registrierung einen 30-Sekunden-Timeout und mappt stabile Fehlercodes auf echte AL-Labels. Netzwerk/Timeout, ungültige Daten, fehlende Berechtigung, Identitätskonflikt, deaktivierter Benutzer/Membership, temporäre Nichtverfügbarkeit und interne Fehler besitzen vollständige DE-/EN-XLF-Targets. Es gibt keine Volltext- oder Wortersetzung und keinen rohen JSON-Dialog.

Bei einer neuen Membership für einen bestehenden Benutzer erscheint die spezifische Meldung mit Environment Name und Hinweis auf den Dashboard-Wechsel.

Die Setup-Aktion zeigt keine vorgeschaltete dauerhafte „Wird bearbeitet“-Meldung mehr. Registrierung und Lizenzrefresh laufen in einer TryFunction; bei jedem Fehler werden `GetLastErrorText`, Page-State und Anzeige kontrolliert aktualisiert. Ein leerer Fehlertext hat einen Label-Fallback, die Seite bleibt bedienbar und die Aktion kann erneut ausgeführt werden.

Mangels AL-Test-App wurden Parser-/Mapping-, Busy-State- und XLF-Verträge durch drei automatisierte Source-Contract-Tests geprüft. Die reale Clientdarstellung bleibt Bestandteil des Sandbox-CAT.

## Tests

| Prüfung | Ergebnis |
|---|---|
| FIX01-Zieltests | 23/23 PASS |
| PostgreSQL Same-Email-Race | 1/1 PASS |
| SQLite Migration Upgrade/Konflikt/Downgrade | 3/3 PASS |
| PostgreSQL Fresh/Legacy Upgrade, Downgrade, Re-Upgrade | PASS |
| ReleaseCloud Compile | PASS, 84 Dateien, Exit 0 |
| CodeCop + PTECop | PASS, keine neuen Fehler/Warnungen gegenüber Baseline |
| AL Source Uniqueness | PASS, 88 Objekte |
| AL Localization Checker | PASS |
| XLF / JSON Parsing | PASS |
| Python compileall | PASS |
| vollständige Backend-Suite | PASS: 275 bestanden, 7 übersprungen, 40 bekannte Warnungen; nach Monolith-Timeout vollständig in drei isolierten Shards ausgeführt |
| AppSourceCop | bekannte Baseline, Exit 1: 3x AS0051, 1x AS0084, 1x AS0092; keine FIX01-Regression |
| git diff --check | PASS, Exit 0; nur nicht blockierende LF/CRLF-Hinweise |

Der erste Backend-Gesamtlauf verwendete ein älteres Docker-Testimage und bestätigte nur die bestehende Baseline mit 258/258; er wurde nicht als FIX01-Gesamtnachweis gewertet. Das aus dem aktuellen Arbeitsbaum neu gebaute monolithische Image überschritt anschließend das 20-Minuten-Befehlslimit ohne ausgegebenen Testfehler (Exit 124). Erste Shard-Aufrufe machten ausschließlich Aufruf-/Isolationfehler sichtbar: fehlender Repository-Root im Image, aus `.env.dev` geerbtes SMTP und eine nicht beschreibbare SQLite-Datei im read-only Mount. Keiner dieser Fehler blockierte den Audit. Die gleichwertige Abschlussmethode mountete den Quellbaum read-only, verwendete `BCSENTINEL_TEST_DATABASE_URL` mit drei getrennten `/tmp`-Datenbanken, deaktivierte SMTP und führte alle 25 Testmodule vollständig in drei Shards aus. Ergebnis: 275 PASS, 7 erwartete PostgreSQL-Skips im SQLite-Lauf und 40 bekannte Deprecation-Warnungen. Die relevante neue PostgreSQL-Parallelitätsprüfung wurde zusätzlich separat mit 1/1 PASS ausgeführt.

## Sicherheitsprüfung

- keine Autorisierung allein über E-Mail
- aktive Membership bei jedem tenantbezogenen Dashboard-Request
- keine Tenant-Liste in Session/JWT
- Fremd-Tenant-Pfad, Switch und manipulierter Claim mit 403 getestet
- Analytics-Embed bleibt Single-Tenant/Single-Company
- keine Änderung an Scan-, Report-, Lizenz-, Credit-, Stripe- oder Pricinglogik
- keine unnötige zweite Einladung; bestehende Passwort-Hashes bleiben bestehen
- eindeutige Benutzer-E-Mail und eindeutige User/Tenant-Membership
- Session-Rotation bei Login und Tenant-Wechsel; HttpOnly, Secure in PROD, SameSite Strict

## Manueller Sandbox-CAT

Ziel: `BCSentinel-Pilot`, Business Central 28.3.

1. Backend mit Migration 0025 und neuem Code bereitstellen; vorher Datenbankbackup und anonymisierte Zählwerte sichern.
2. Extension-Paket aus dem aktuellen Stand publishen/upgraden, nicht deinstallieren und keine Objekt-ID ändern.
3. API-Verbindung testen und Datenverarbeitung bestätigen.
4. Mit einer E-Mail registrieren, die bereits einem anderen BCSentinel-Tenant zugeordnet ist.
5. Erfolgreiche spezifische DE-/EN-Meldung und das Ende des Busy-State prüfen.
6. Produktzugriff aktualisieren; Setup muss bedienbar bleiben.
7. Dashboard mit derselben E-Mail öffnen; mehrere verständlich benannte Dashboards müssen sichtbar sein.
8. Jeden Tenant öffnen und Overview, Findings, Scan History, Reports, Lizenz, Credits und Billing auf strikte Trennung prüfen.
9. Fremde Tenant-ID direkt und durch manipulierten Switch versuchen; erwartetes Ergebnis 403.
10. Zurück in BC identisch erneut registrieren; dieselbe Membership muss idempotent wiederverwendet werden.
11. Screenshots, Request IDs, Benutzer-/Tenant-/Membership-Zählwerte und Ergebnis protokollieren – ohne E-Mail-Adressen im Auditbericht.

Status: **BLOCKED / nicht ausgeführt**. Die vor dem Fix bereits bestätigten Schritte Fresh Install, Publish, Install, Setup, Permission Set, HTTP-Freigabe und Verbindungstest bleiben historische PASS-Evidenz.

## Rollback

1. Vor Deployment vollständiges DB-Backup erstellen.
2. Solange jeder Dashboard-Benutzer exakt eine Membership hat, ist `alembic downgrade 0024_scan_lifecycle_recovery` sicher getestet.
3. Sobald ein Benutzer mehrere Memberships besitzt, bricht der Downgrade absichtlich ab. Vor einem Rollback muss fachlich entschieden werden, welche Zuordnung erhalten bleibt; keine automatische Löschung durchführen.
4. Backend-Code und Extension gemeinsam auf den vorherigen Release zurücksetzen; keine BC-Extension deinstallieren und keine Objekt-IDs ändern.
5. Tenant-, Benutzer- und Membership-Zählwerte sowie Orphans/Duplikate nach jedem Schritt prüfen.

## Offene Risiken und Entscheidung

- Der reale BC-28.3-CAT nach dem Fix fehlt.
- Produktivbackup, Migrationsfenster und Deployment-Reihenfolge müssen freigegeben werden.
- Passwort-Reset/Recovery und optionale Benachrichtigung eines aktiven Benutzers über eine neue Membership sind Folgeverbesserungen, nicht Blocker für die registrierungsseitige Zuordnung.
- AppSource-Baseline bleibt außerhalb dieses Sprints offen.

- Root Cause bestätigt: **Ja**
- Migration erstellt und bestehende Daten backfillbar: **Ja**
- gleiche E-Mail mehrfach zulässig: **Ja**
- Registrierung idempotent / doppelte Membership verhindert: **Ja**
- Multi-Tenant-Liste und Tenant-Wechsel implementiert: **Ja**
- serverseitige Membership-Prüfung / Fremdzugriff blockiert: **Ja**
- AL-Busy-State und DE/EN-Fehlerbehandlung behoben: **Ja auf Codeebene**
- Sprint abgeschlossen: **Nein – manueller Sandbox-CAT BLOCKED**
- Multi-Tenant-Login funktionsfähig: **Ja, automatisiert verifiziert**
- Tenant-Trennung sicher: **Ja auf Code-/API-Testebene; Sandbox-CAT offen**
- Registrierung in `BCSentinel-Pilot` erfolgreich: **Noch nicht verifiziert**
- bereit zur Fortsetzung von GL-PILOT-01: **Code-ready für den erneuten Sandbox-CAT; formales GO erst danach**

Commit-Vorschlag: `fix(auth): support multi-tenant dashboard access per email`

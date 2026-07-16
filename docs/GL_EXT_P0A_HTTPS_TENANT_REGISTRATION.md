# GL-EXT-P0A – Production Transport Security & Tenant-Bound Registration

Stand: 16. Juli 2026  
Scope: ausschließlich P0-01 und P0-02 aus GL-EXT-AUDIT-01

## Ergebnis

P0-01 und P0-02 sind auf Code-, Datenbank- und Backend-Testebene behoben. Der AL-ReleaseCloud-Build ist erfolgreich. Ein Business-Central-Sandbox-CAT konnte mangels Sandbox nicht ausgeführt werden und bleibt vor einem Pilot verpflichtend. Der Gesamtstatus des ursprünglichen Audits bleibt **NO-GO**, weil P0-03 bis P0-05 außerhalb dieses Sprints weiterhin offen sind.

| Gate | Ursprünglicher Status | Korrektur | Neue Evidenz | Aktueller Status |
|---|---|---|---|---|
| P0-01 Production HTTP | offen / DEFECTIVE | zentrale AL- und Backend-URL-Policy; produktive Request-Middleware | Backend-Negativtests; AL-Compile; CodeCop/PTE-Cop ohne Fehler | **behoben** |
| P0-02 stabile Registrierung | offen / DEFECTIVE | kanonische BC-Identität, Unique Constraint, transaktionaler Upsert, Legacy-Bindung | Parallel-, Retry-, Portal- und Dashboard-Kontexttests; Migrationsproben | **behoben** |
| Pilot-/Customer-Gate | NO-GO | nicht Gegenstand dieses Sprints | drei weitere P0 und Sandbox-CAT offen | **NO-GO** |

## Ausgangsrisiken und Root Causes

### P0-01

Die AL-Validierung akzeptierte jedes `http://`-Schema. Der Schutz lag nur an einzelnen UI-/Default-Stellen, während duplizierte URL-Builder die Basis-URL direkt verwendeten. Dadurch konnten Tenant-ID und API-Token zu einem beliebigen externen HTTP-Endpunkt gesendet werden. Das Backend erzwang außerdem keinen sicheren Transport am produktiven Request-Eingang.

### P0-02

Jeder Registrierungsaufruf erzeugte eine zufällige Backend-Tenant-ID und einen neuen Token. Entra Tenant, tatsächliche BC-Umgebung und Company SystemId waren nicht Bestandteil eines serverseitig eindeutigen Schlüssels. Ein lokaler Reset entfernte die Wiederanbindungsdaten, während der Backend-Tenant bestehen blieb. Portal-Account und Einladung waren dadurch ebenfalls nicht Teil eines vollständig idempotenten Vertrags.

## Geänderte Architektur

1. AL ermittelt Entra Tenant ID, Environment Name/Type, Company SystemId/Name und die tatsächliche Extension-Version.
2. Jeder AL-Endpunkt wird durch `DH API URL Policy` aus einer erneut validierten Basis-URL gebaut.
3. `/tenant/register` normalisiert die Identität und bildet einen SHA-256-Identity-Key.
4. Ein Unique Constraint serialisiert konkurrierende Registrierungen derselben Identität.
5. Tenant-ID und ausgegebener API-Token werden deterministisch aus der Identität abgeleitet; gespeichert wird nur der Tokenhash.
6. Das Portal verwendet genau einen DashboardUser pro Tenant. Einladungen werden bei Retry nicht automatisch erneut versendet.
7. Dashboard-Token werden für gebundene Tenants nur bei exakt passendem Entra-/Environment-/Company-Kontext ausgegeben.

## HTTPS Policy

Die zentrale Policy gilt in AL beim Speichern und vor jedem Request sowie im Backend für Konfiguration und produktive Requests.

- Produktion akzeptiert ausschließlich absolute HTTPS-URLs.
- Scheme-Vergleich ist case-insensitive; gespeichert wird ein normalisierter Wert ohne abschließenden Slash.
- Whitespace innerhalb der URL, fehlendes Scheme, leere Authority, eingebettete Credentials, Query/Fragment in einer API-Basis-URL und ungültige Ports werden abgelehnt.
- Relative AL-Requestpfade müssen mit genau einem lokalen `/` beginnen; absolute oder schemarelative Ziele und Backslashes werden abgelehnt.
- Produktions-HTTP wird vor der Applikationsverarbeitung mit einer strukturierten Fehlermeldung blockiert.
- Produktions-CORS-Origins und externe Billing-/Partner-/App-URLs durchlaufen dieselbe Policy. Billing-Redirectziele dürfen Queryparameter enthalten, API-Basis-URLs nicht.
- Die Anwendung folgt selbst keinen konfigurierten HTTPS-zu-HTTP-Redirects. Das endgültige Proxy-/Redirect-Verhalten ist im manuellen CAT zu prüfen.

Fehlermeldung:

- EN: `Unsafe API connection blocked. HTTPS is required for production environments.`
- DE: `Unsichere API-Verbindung blockiert. Für Produktionsumgebungen ist HTTPS erforderlich.`

### Erlaubte Dev-Ausnahmen

HTTP ist ausschließlich außerhalb von Production und ausschließlich für die exakten Loopback-Hosts `localhost`, `127.0.0.1` und `::1` zulässig. Private IPs, externe Hosts, Localhost-Suffixe und beliebige lokale Hostnamen sind nicht erlaubt. Eine generische „Development“-Freischaltung externer HTTP-Ziele existiert nicht.

## Tenant Identity Model

Kanonische Company-Registrierungsidentität:

```text
lower(EntraTenantId)
+ lower(EnvironmentName)
+ lower(EnvironmentType)
+ lower(CompanySystemId as UUID)
```

Der kanonische String wird mit Zeilenumbrüchen separiert und SHA-256 gehasht. Veränderliche Werte wie Company Name, Kontakt-E-Mail, Sprache, App-Version und API-URL sind ausdrücklich kein Teil des Identity Keys.

Die aktuelle Lizenz-/Accountstruktur bleibt companybezogen: Jede unterschiedliche Kombination aus Entra Tenant, BC Environment und Company erzeugt bewusst einen eigenen BCSentinel-Tenant. Eine spätere accountweite Lizenzaggregation wäre ein eigenes Datenmodell und ist nicht Teil von P0A.

### Identity Contract

- Entra Tenant ID: `TenantId()` aus der BC-Plattform.
- Environment: Name und Typ aus `Environment Information` (`production`, `sandbox`, sonst `onprem`).
- Company: persistente `Company Information.SystemId`.
- Company Name: nur veränderliches Anzeigeattribut.
- App-Version: `NavApp.GetCurrentModuleInfo(...).AppVersion()` statt Hardcoding.
- Backend Tenant ID: `ten_` plus stabiler Prefix des Identity Keys.

## Idempotency Contract

| Fall | Ergebnis |
|---|---|
| erster Aufruf | Tenant und Portaluser werden erzeugt; initiale Einladung wird einmal versucht |
| identischer Retry | gleiche Tenant-ID, gleicher logischer Token, kein zweiter Tenant/User, keine automatische zweite Mail |
| Antwortverlust nach Commit | Retry findet den Identity-Key und liefert denselben Kontext |
| parallele identische Aufrufe | Unique Constraint plus IntegrityError-Recovery führen auf denselben Datensatz |
| neue Kontakt-E-Mail | mutable Felder und derselbe Portaluser werden aktualisiert; keine neue Identität |
| andere Company/Environment/Entra Tenant | bewusst anderer Identity-Key und eigener Tenant |
| vorhandener Legacy-Tenant | Bindung nur mit passender Tenant-ID und gültigem API-Token in Authheadern |

Registrierung verbraucht keine Credits und erzeugt keine Lizenzinstanz. Die bestehenden Lizenz-/Creditflows wurden nicht geändert.

## Datenbank und Unique Constraints

Migration `0022_tenant_registration_identity` ergänzt nullable:

- `registration_identity_key`
- `entra_tenant_id`
- `bc_environment_name`
- `bc_environment_type`
- `bc_company_id`
- `bc_company_name`

Zusätzlich werden ein Unique Constraint auf `tenants.registration_identity_key`, Suchindizes und ein global eindeutiger Index auf `dashboard_users.email` angelegt. Nullable Legacy-Felder sind Absicht: vorhandene Zuordnungen werden nicht geraten oder überschrieben. Vor dem Dashboard-E-Mail-Index prüft die Migration bestehende Duplikate und bricht mit einer expliziten Meldung ab.

Die bestehende Alembic-Umgebung erhielt einen minimalen SQLAlchemy-2-Fix: Nach dem Anlegen der benutzerdefinierten Versionstabelle wird die implizite Transaktion committed. Ohne diesen Fix wurden SQLite-Upgrades zwar geloggt, aber nicht verlässlich gestempelt.

## Portal-Account und Willkommensmail

- `prepare_dashboard_user` erstellt oder aktualisiert genau einen User, versendet aber nicht selbst.
- Nur ein neu erstellter Portaluser löst den initialen Invite-Versuch aus.
- Ein SMTP-Fehler rollt Tenant und Portaluser nicht zurück; der gespeicherte Invite-Status bleibt nachvollziehbar.
- Wiederholte Registrierung versendet keine weitere Einladung.
- Kontrollierter Resend erfolgt über `POST /tenant/dashboard-invite/resend` mit Tenant-ID/API-Token-Authentisierung.
- Eine Kontaktänderung aktualisiert einen noch nicht aktivierten Portaluser, ohne Tenantwechsel.
- Ein Konflikt mit einer bereits anderweitig gebundenen E-Mail liefert HTTP 409 statt eines zweiten Accounts.

## Dashboard Tenant Context

Gebundene Tenants müssen bei `/analytics/get-token` exakt dieselben normalisierten Werte für Entra Tenant, Environment Name/Type und Company SystemId liefern. Fehlender Kontext liefert HTTP 409, ein Mismatch HTTP 403. Die bestehende Authentisierung per Tenant-ID/API-Token bleibt vorgeschaltet; der Query-Tenant-Identifier allein autorisiert nichts. Der bestehende kurzlebige, tenant- und scopegebundene Dashboard-Token wurde nicht neu gestaltet.

Legacy-Tenants ohne Identity-Bindung bleiben bis zur authentisierten Re-Registrierung rückwärtskompatibel. Diese Ausnahme ist migrationsbedingt und wird nicht automatisch auf eine BC-Identität gemappt.

## Reset und Re-Registrierung

Der AL-Reset:

- besitzt `Confirm(..., false)`;
- löscht nur gecachten Registrierungs-/Lizenzstatus;
- behält Tenant-ID, API-Token, Käufe und Scan-Historie;
- fordert danach eine idempotente Registrierung zum Backend-Abgleich auf.

Re-Registrierung ist auch bei bereits vorhandener Tenant-ID erlaubt. Der AL-Client sendet dann die vorhandenen Credentials, wodurch ein noch ungebundener Legacy-Tenant nur authentisiert übernommen werden kann. Company- oder Environmentwechsel erzeugt bewusst eine neue Company-Registrierung; der alte Backend-Tenant wird weder gelöscht noch umgebunden.

Setup-, Register-, Reset- und URL-Änderungen bleiben über das bestehende `BCSENTINEL SETUP`-PermissionSet auf Administratoren/entsprechend berechtigte Benutzer begrenzt.

## Tests und Verifikation

### Bestanden

- Neue P0A-Backendtests: Production HTTP/HTTPS, enge Dev-Ausnahme, manipulierte URLs, erste/idempotente/parallele Registrierung, Timeout-Retry, Kontaktänderung, Identity-Differenzierung, Portal-Deduplizierung/Resend, Dashboard-Kontext und Legacy-Bindung.
- P0A plus bestehende Registrierungstests: **31 bestanden**.
- Betroffene Regressionstests: **26 bestanden**.
- Vollständiges pytest: **171 bestanden, 2 bekannte Altfehler, 66 Warnungen**.
- Python `compileall`: bestanden.
- Frische Alembic-Datenbank bis `0022`: bestanden.
- Upgrade eines `0021`-Testbestands: Tenant und Portaluser erhalten; Identity-Felder bewusst `NULL`.
- AL ReleaseCloud Compile: **bestanden**, 81 Dateien inklusive P0A-Codeunits.
- CodeCop + PerTenantExtensionCop: **0 Fehler**, 303 bestehende Warnungen, 81 Namespace-Infos.
- JSON- und XLF-Parsing: bestanden.
- `git diff --check`: bestanden.

### Bekannte, nicht durch P0A verursachte Fehler

1. Vollständiges pytest: Product-Management-Test erwartet nach Assessment 0 Credits, Istwert 1. Das ist der bereits auditierte Credit-Scope und bleibt für P0B.
2. Vollständiges pytest: Localization-Test erwartet den fehlerhaften Text `Ueberblick`, die Anwendung liefert korrekt `Überblick`.
3. `check_al_localization.py`: bestehende deutsche Inline-Texte in mehreren Altdateien. Die neuen P0A-URL-/Identity-Labels liegen in EN im AL-Quelltext und mit DE-Targets in XLF vor.
4. `check_pricing_consistency.py`: bestehender Assessment-Fallback-Mismatch; Pricing ist explizit außerhalb dieses Sprints.
5. `check_entitlements.py` ist nur mit `backend` im Python-Modulpfad ausführbar; der korrekt konfigurierte Lauf ist in der Abschlussprüfung zu verwenden.
6. AppSourceCop: bestehende Manifest-Gaps (`EULA`, `logo`, `contextSensitiveHelpUrl`) und nicht AppSource-fähiger 53xxx-ID-Bereich. Der normale AL-Build sowie CodeCop/PTE-Cop sind grün.
7. Docker-Build: Docker CLI vorhanden, aber Docker Desktop Linux Engine nicht gestartet; daher nicht als bestanden markiert.

## Reproduzierbarer manueller BC-Sandbox-CAT

1. Extension in einer Production-artigen Sandbox installieren und Setup mit `https://...` speichern; Verbindung muss funktionieren.
2. `http://` zu einem externen Host konfigurieren; Speichern/Request muss mit der lokalisierten Unsafe-Connection-Meldung abbrechen.
3. In Production-Kontext `http://localhost` testen; muss ebenfalls blockieren.
4. In einer nicht produktiven Dev-Umgebung exaktes `http://localhost:<port>` testen; nur dieser Loopback-Fall darf funktionieren.
5. Registrieren; Tenant-ID und Portalstatus notieren.
6. Identisch erneut registrieren; Tenant-ID bleibt gleich und es entsteht keine zweite Mail/kein zweiter Portalaccount.
7. Backendantwort nach erfolgreichem Commit simuliert verlieren und erneut registrieren; derselbe Tenant muss zurückkommen.
8. Kontakt-E-Mail ändern und registrieren; Tenant-ID bleibt gleich, Portaluser wird kontrolliert aktualisiert.
9. Dashboard öffnen; danach Company-/Environment-Kontext manipulieren und 403/409 verifizieren.
10. Reset bestätigen (Default Nein prüfen), danach re-registrieren; Tenant-ID, Token, Käufe und Historie bleiben erhalten.

Diese zehn Punkte sind mangels verfügbarer BC-Sandbox **nicht ausgeführt** und vor Pilot als Pflichtnachweis offen.

## Production Configuration

- `ENV`/`APP_ENV` auf Production setzen.
- `APP_BASE_URL`, erlaubte CORS-Origins sowie Billing-/Partner-URLs ausschließlich mit HTTPS konfigurieren.
- TLS am vertrauenswürdigen Reverse Proxy terminieren und `X-Forwarded-Proto` dort überschreiben; ungeprüfte Clientwerte dürfen nicht durchgereicht werden.
- Den Backend-Port nur intern/loopback exponieren. Der Compose-Healthcheck ist ein interner Loopback-Check und setzt den vertrauenswürdigen Forwarded-Proto explizit.
- HTTP am öffentlichen Listener deaktivieren oder ausschließlich auf HTTPS umleiten; zusätzlich testen, dass kein HTTPS-Endpunkt auf HTTP zurückleitet.
- `SECRET_KEY`, SMTP-, Payment- und andere Secrets nur über Secret Management bereitstellen, niemals im Repository.

## Bekannte Grenzen und verbleibende Risiken

- Der deterministische Registrierungstoken hängt von `SECRET_KEY` ab. Eine Rotation ändert den bei Re-Registrierung abgeleiteten Token; koordinierte Tokenrotation/Recovery bleibt P1.
- Die Forwarded-Proto-Auswertung setzt einen korrekt gehärteten, vertrauenswürdigen Reverse Proxy voraus.
- Legacy-Tenants bleiben ungebunden, bis sie sich mit ihren bestehenden Credentials erneut registrieren.
- Eine BC-Sandbox und eine AL-Test-App fehlen. Der kompilierte Kern ist isoliert, aber der UI-/Runtime-CAT ist offen.
- P0-03 atomare Creditnutzung, P0-04 Scan-Lifecycle und P0-05 lokaler Findings-Zugriff bleiben offen.

## Rollback

1. Vor Rollback Datenbanksicherung erstellen.
2. Anwendung auf die vorherige Version zurücksetzen.
3. Migration `0022` nur dann downgraden, wenn keine neue gebundene Registrierung produktiv genutzt wurde; der Downgrade entfernt die Identity-Felder und Constraints.
4. Bereits angelegte Tenants oder Portaluser nicht manuell löschen. Bei produktiver Nutzung ist ein Forward-Fix sicherer als ein Schema-Downgrade.
5. HTTPS am Proxy darf auch während eines Applikationsrollbacks nicht deaktiviert werden.

Commit-Vorschlag: `fix(security): enforce https and make tenant registration idempotent`

# Task 4.1 Audit: BC Setup Onboarding & Scan Menu Cleanup

Datum: 2026-06-16

## Gefundene aktuelle Logik

- `DHSetup.Table.al`
  - Enthielt Tenant ID, API Base URL, Legacy API Token, Invite Code, Lizenz-/Produktzugriffsstatus und Scan-Modulschalter.
  - Kein Contact-Email-Feld.
  - Kein lokales Feld fuer `can_run_data_health_score` oder `has_completed_data_health_score`.
- `DHSetup.Page.al`
  - `Register Tenant` war aktiv, sobald Data Processing Consent und API Base URL vorhanden waren.
  - Bestehende Tenant ID deaktivierte Registrierung nicht sicher.
  - `Reset Registration` hatte eine kurze Warnung, aber keinen expliziten Hinweis auf neue Tenant-Identitaet und verlorene Kauf-/Credit-Verknuepfung.
  - `Request Access` oeffnete die Landingpage.
  - Invite-Code-Feld und Invite-Hinweis waren sichtbar.
  - Scan-Menue enthielt Free Score, Premium Deep Scan und Scan History.
- `DHApiClient.Codeunit.al`
  - Registrierung sendete `environment_name`, `app_version`, `preferred_language` und `invite_code`.
  - License Refresh wertete `can_run_data_health_score` und `has_completed_data_health_score` noch nicht aus.
- Backend `/tenant/register`
  - Request enthielt keine Contact Email.
  - Tenant-Modell enthielt kein Tenant-Contact-Email-Feld.

## Geaenderte UI-Aktionen

- `Register Tenant`
  - Ist nur aktiv, wenn:
    - keine Tenant ID vorhanden ist,
    - Data Processing Consent gesetzt ist,
    - API Base URL vorhanden ist,
    - Contact Email lokal valide ist.
  - Wenn Tenant ID vorhanden ist, wird keine erneute Registrierung ausgefuehrt.
- `Reset Registration`
  - Hat jetzt eine deutliche Sicherheitsabfrage:
    - Reset erzeugt neue Tenant-Identitaet.
    - Bestehende Kaeufe, Credits, Full Analysis, Validation Check und Monitoring sind nicht mehr mit dieser BC-Company verknuepft.
    - Abbruch laesst alles unveraendert.
  - Reset leert lokale Registrierung, Produktzugriffsstatus und Data-Health-Score-Flags.
- `Request Access`
  - In der UI ausgeblendet.
- Invite-Code-Feld und Invite-Hinweis
  - In der UI ausgeblendet.
  - Feld bleibt technisch erhalten und wird weiter im Payload gesendet, falls eine Umgebung noch Invite-Code verlangt.

## Scan-Menue

Unter `Actions > Scan` sind fachlich nur noch sichtbar:

- `Start Free Data Health Score`
- `Start Validation Check`
- `Scan History`

Umsetzung:

- Der alte Premium-Deep-Scan-Button wurde fachlich zu `Start Validation Check` umbenannt.
- Technisch nutzt Validation Check weiterhin `EnsureReadyForScan()` und `QueueDeepScan()`.
- Dadurch bleiben Full Analysis, Validation Check, Scan Credit und Monitoring Gates erhalten.
- Vor dem Free Score wird eine deaktivierte `Start Validation Check`-Aktion mit Tooltip `Run the free Data Health Score first.` angezeigt.
- Nach abgeschlossenem Free Score wird die aktive `Start Validation Check`-Aktion angezeigt.
- Nach abgeschlossenem Free Score wird statt der aktiven Free-Score-Aktion eine deaktivierte Aktion mit Tooltip `Free Data Health Score already completed.` angezeigt.

## Neue / angepasste Felder

- `DH Setup`
  - `Contact Email` `Text[100]`
  - `Can Run Data Health Score` `Boolean`
  - `Data Health Score Completed` `Boolean`
- `Tenant` Backend-Modell
  - `contact_email` `String(255)`, nullable, indexiert.
- Alembic Migration
  - `backend/alembic/versions/0020_tenant_contact_email.py`

## E-Mail-Validierung

BC-validiert vor Registrierung:

- nicht leer,
- enthaelt `@`,
- Domainteil nach `@` enthaelt `.`,
- endet nicht mit `.`,
- keine Leerzeichen.

Fehlermeldung:

- `Please enter a valid contact email before registering.`

Backend-validiert optional gesendete Contact Email ebenfalls minimal und speichert normalisiert lower-case.
Alte Clients ohne `contact_email` bleiben kompatibel.

## Free / Validation Button State Logik

- Free Score abgeschlossen, wenn:
  - `Data Health Score Completed = true`, oder
  - ein lokaler `DH Deep Scan Run` mit `Scan Mode = data_health_score` und Status `Completed` existiert.
- `Can Run Data Health Score` wird aus `/license/status` gemappt, aber nicht allein als Completion-Beweis genutzt, damit bestehende Setup-Datensaetze nach einem App-Update nicht faelschlich gesperrt werden.
- `Start Free Data Health Score`:
  - aktiv bei registriertem Tenant und noch nicht abgeschlossenem Free Score.
  - nach erfolgreichem Start setzt BC lokal `Data Health Score Completed = true` und `Can Run Data Health Score = false`.
- `Start Validation Check`:
  - vor Free Score deaktiviert.
  - nach Free Score aktiv sichtbar.
  - Start selbst bleibt durch bestehende Premium-/Credit-/Monitoring-Pruefung geschuetzt.

## Backend-Email-Status

- Backend kann `contact_email` jetzt bei `/tenant/register` entgegennehmen und speichern.
- Kein Passwort wird generiert.
- Kein Mail-Versand wurde gebaut.
- Kein unsicherer Login-/Passwort-Flow wurde improvisiert.

## Verifikation

- Python Syntax:
  - `python -m py_compile backend/app/main.py backend/app/models.py backend/tests/test_tenant_registration.py`
  - Ergebnis: erfolgreich.
- Backend Tests:
  - `pytest backend/tests/test_tenant_registration.py`
  - Ergebnis: 6 passed.
  - `pytest backend/tests/test_tenant_registration.py backend/tests/test_product_licensing_p0.py backend/tests/test_pricing.py backend/tests/test_billing.py backend/tests/test_admin.py`
  - Ergebnis: 88 passed, 47 warnings.
- AL statische Pruefung:
  - Quellsuche nach neuen Feldern, ausgeblendeten Invite-/Request-Access-Elementen und Scan-Aktionen durchgefuehrt.
  - Kein lokaler `alc.exe` wurde gefunden; ein echter AL Compile/Package-Build wurde daher nicht ausgefuehrt.

## Offene Folge-Tasks

- In der BC-Entwicklungsumgebung einen echten AL Package Build ausfuehren.
- Backend Login-Ziel:
  - Bei Registrierung Dashboard-User erzeugen.
  - Sicheres Passwort oder Einmal-Login erzeugen.
  - Passwort/Einmallink an Contact Email senden.
  - Login ueber Landingpage/Dashboard mit Email + Passwort oder Magic Link.
- Invite-Code backendseitig fuer Self-Service-Pilotphase final entfernen oder per Konfiguration deaktivieren.
- Optional: Admin UI fuer Tenant Contact Email anzeigen und bearbeiten.

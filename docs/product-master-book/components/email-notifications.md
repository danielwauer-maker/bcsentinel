# E-Mail und Notifications

## Zusammenfassung
SMTP-Code für Dashboardeinladungen, Partneranträge/-Passwortreset und administrierbare Templates.

## Erkannte Verantwortlichkeiten
HTML-Mail, Versandstatus/-fehler, Templateverwaltung und Testversand.

## Erkannte Unterbereiche
`dashboard_invite_service.py`, SMTP-Helfer in `partners.py`, `email_template_service.py`, Admin-Template-Routen.

## Vorhandene Features
MAIL-TPL-001.

## Teilweise vorhandene Features
MAIL-INV-001, MAIL-PART-001: Code und Statuspersistenz vorhanden; externe Zustellung nicht bestätigt.

## Stubs oder statische Inhalte
Fallbacktexte sind im Code hinterlegt; bei fehlendem SMTP wird Versand protokolliert/übersprungen.

## APIs und Schnittstellen
SMTP/TLS, Admin-Testsend, Registrierung/Invite, Partnerreset.

## Datenmodelle
`AdminEmailTemplate`; Invite- und Partner-Mailstatusfelder.

## Tests
Registrierungs-/Admin-/Partnerpfade mocken Versandteile; keine Mailclient-E2E-Suite.

## Dokumentation
Konfiguration in `backend/README.md`/Settings; manuelle Checklisten.

## Technische Auffälligkeiten
Mehrere SMTP-Helfer existieren in unterschiedlichen Modulen.

## Manuell zu prüfen
Zustellung, Spam, TLS, HTML-Rendering und Clients.

## Belegverzeichnis
Obige Services, Router und Migrationen `0009`, `0010`, `0020`.

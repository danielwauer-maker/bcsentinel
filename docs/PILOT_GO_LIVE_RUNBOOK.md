# Pilot Go-Live Runbook

Datum: 2026-06-10

Ziel: handgefuehrter Pilot-Go-Live fuer den ersten Kunden ohne Self-Service-Annahme.

## Voraussetzungen

- DEV/PROD Deployment-Dry-Run erfolgreich.
- `alembic upgrade head` erfolgreich.
- `/health/ready` gruen.
- `APP_BASE_URL` oeffentlich gesetzt.
- `CORS_ALLOW_ORIGINS` ohne Dev-Origin in PROD.
- Admin Login funktioniert.
- Admin Translations koennen `landingpage/lang/de.json` und `en.json` lesen.
- Stripe Testmodus oder manuelle Admin-Lizenzvergabe entschieden.
- BC Extension fuer Pilotumgebung installiert.

## Kunden-Onboarding

1. Pilotkunde und Ansprechpartner erfassen.
2. BC Tenant/Company bestimmen.
3. Datenschutz-/Consent-Hinweis mit Kunde bestaetigen.
4. Invite-Code oder manuelle Registrierung vorbereiten.
5. Supportkontakt und Eskalationsweg festlegen.

## Tenant registrieren

1. DH Setup Page in Business Central oeffnen.
2. API URL setzen.
3. Consent bestaetigen.
4. Tenant registrieren.
5. API Token sicher speichern.
6. Lizenzstatus aktualisieren.

## Lizenz / Scan-Credit vergeben

Variante A: Stripe Testkauf

1. Checkout fuer Produkt starten.
2. Success-Seite pruefen.
3. Webhook-Verarbeitung pruefen.
4. License Status in BC aktualisieren.

Variante B: handgefuehrte Admin-Vergabe

1. Admin Tenant Detail oeffnen.
2. Passenden Product Access oder Scan Credit vergeben.
3. Admin Audit Log pruefen.
4. License Status in BC aktualisieren.

## BC Extension konfigurieren

1. API URL pruefen.
2. Verbindungstest ausfuehren.
3. Sprache pruefen: Deutsch -> `de`, sonst `en`.
4. License Refresh ausfuehren.
5. Dashboard Link pruefen.

## Scan starten

1. Quick Scan optional ausfuehren.
2. Deep Scan starten.
3. Confirm Dialog bestaetigen.
4. Backend Log pruefen: Start-Endpunkt muss sichtbar sein.
5. Scan History pruefen.
6. Credit-Abzug oder Monitoring-Berechtigung pruefen.

## Dashboard pruefen

1. Analytics Dashboard oeffnen.
2. Data Health Score pruefen.
3. Issue-Liste pruefen.
4. Open in BC pruefen.
5. Monitoring-Panels nur bei Monitoring-Zugriff pruefen.

## Executive Report erzeugen

1. HTML Report oeffnen.
2. PDF Report oeffnen.
3. Management Summary pruefen.
4. Risiko-Matrix pruefen.
5. Next Best Action pruefen.
6. Sprache DE/EN pruefen.

## Report teilen

1. Share Link erzeugen.
2. HTML Share Link in privatem Browser oeffnen.
3. PDF Share Link in privatem Browser oeffnen.
4. Ablaufzeit dokumentieren.
5. Kein localhost in Link.

## Fehlerfall

- Bei API-Fehler: Request-ID/Backend-Log sichern.
- Bei Stripe-Fehler: Stripe Event ID sichern.
- Bei Scan-Fehler: Scan Run ID und Tenant ID sichern.
- Bei Report-Fehler: Scan ID und Report-Typ sichern.
- Keine API Tokens oder Secrets in Support-Tickets kopieren.

## Rollback

Keine Daten loeschen.

1. API Container auf vorheriges Image zuruecksetzen.
2. Nginx Config auf letzte gueltige Version zuruecksetzen.
3. `sudo nginx -t && sudo systemctl reload nginx`.
4. Tenant-Zugriff im Admin deaktivieren, falls noetig.
5. Stripe Subscription im Portal/Testmodus stornieren, falls noetig.

## Supportprozess

- Reaktionszeit Pilot: gleicher Werktag.
- Primaerer Kanal: vereinbarter Supportkontakt.
- Kritische Fehler: Scan startet nicht, falscher Lizenzstatus, Report nicht erzeugbar, Datenzugriff falsch.
- Jeder Eingriff wird im Admin Audit Log dokumentiert.

## Go/No-Go-Checkliste

Go:

- Deployment-Dry-Run bestanden.
- Healthchecks gruen.
- Tenant Registrierung erfolgreich.
- License Refresh erfolgreich.
- Deep Scan erzeugt History-Eintrag.
- Credit/Access korrekt.
- Dashboard zeigt Ergebnisse.
- Executive HTML/PDF funktioniert.
- Share Links funktionieren ohne localhost.
- Admin Audit Log protokolliert manuelle Eingriffe.

No-Go:

- Migrationen nicht auf Head.
- Healthcheck rot.
- Scan startet nicht.
- Credits/Access falsch.
- Report Share Links zeigen localhost.
- Admin Translations oder Landingpage bricht nach Deployment.
- Stripe/Webhook unklar, wenn Kauf produktiv genutzt werden soll.

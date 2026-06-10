# Manual Go-Live Checklist

Datum: 2026-06-10

Status: MANUAL EXECUTION REQUIRED.

Diese Checkliste enthaelt alle Go-Live-relevanten Pruefungen, die nicht vollstaendig durch Codex in der lokalen Umgebung ausgefuehrt werden koennen. Ergebnisse bitte direkt in diesem Dokument oder in einer Kopie pro Testlauf dokumentieren.

## DEV Live-Smoke-Test

- [ ] DEV Backend und Public Health pruefen
  - Ziel: Sicherstellen, dass DEV Backend lokal und oeffentlich erreichbar ist.
  - Voraussetzung: Aktueller `staging`-Stand ist deployed; `.env.dev` ist gesetzt.
  - Exakte Schritte:
    1. `docker compose --env-file .env.dev -f docker-compose.dev.yml up -d --build backend`
    2. `docker compose --env-file .env.dev -f docker-compose.dev.yml ps`
    3. `curl -i http://127.0.0.1:8001/health`
    4. `curl -I https://dev-api.bcsentinel.com/health`
  - Erwartetes Ergebnis: Backend ist `Up`; beide Healthchecks liefern HTTP 200.
  - PASS-Kriterium: Kein Container-Restart-Loop, kein HTTP 502/503.
  - FAIL-Kriterium: Backend `Restarting`, lokaler Healthcheck fehlschlaegt oder Public Health liefert 502/503.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Landingpage oeffnen
  - Ziel: DEV Landingpage ist erreichbar.
  - Voraussetzung: nginx ist geladen; Landingpage-Dateien liegen auf dem Server.
  - Exakte Schritte:
    1. `https://dev.bcsentinel.com/` im Browser oeffnen.
    2. HTTP Status und sichtbares Rendering pruefen.
  - Erwartetes Ergebnis: Seite laedt ohne 404/502 und ohne sichtbare Platzhalter.
  - PASS-Kriterium: HTTP 200, Header/Footer sichtbar, Hauptinhalt geladen.
  - FAIL-Kriterium: 404/502, leere Seite, kaputte Assets.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Docs oeffnen
  - Ziel: `docs.html` wird statisch ausgeliefert, nicht zur FastAPI Swagger-Route geleitet.
  - Voraussetzung: nginx docs Routing ist aktiv.
  - Exakte Schritte:
    1. `curl -I https://dev.bcsentinel.com/docs`
    2. `curl -I https://dev.bcsentinel.com/docs.html`
    3. Beide URLs im Browser oeffnen.
  - Erwartetes Ergebnis: Beide URLs liefern HTML 200.
  - PASS-Kriterium: Kein Backend-404, kein Swagger UI auf `dev.bcsentinel.com/docs`.
  - FAIL-Kriterium: 404, 502 oder Swagger UI.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Admin Login
  - Ziel: Admin-Bereich ist geschuetzt und Login funktioniert.
  - Voraussetzung: Admin Credentials liegen vor.
  - Exakte Schritte:
    1. `https://dev.bcsentinel.com/admin` oeffnen.
    2. Login ausfuehren.
  - Erwartetes Ergebnis: Ohne Login kein Zugriff; mit Login Admin Dashboard sichtbar.
  - PASS-Kriterium: Authentifizierung funktioniert, keine 500-Fehler.
  - FAIL-Kriterium: Admin ist ohne Login erreichbar oder Login fuehrt zu Fehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Admin Dashboard
  - Ziel: Admin Startseite laedt alle wichtigen Bereiche.
  - Voraussetzung: Admin Login erfolgreich.
  - Exakte Schritte:
    1. Admin Dashboard oeffnen.
    2. Bereiche Tenants, Partner, Audit und Pricing Navigation pruefen.
  - Erwartetes Ergebnis: Dashboard laedt ohne Template- oder Datenfehler.
  - PASS-Kriterium: Keine 500-Seite, keine fehlenden Menuepunkte fuer Go-Live-kritische Funktionen.
  - FAIL-Kriterium: Templatefehler, fehlende Product Pricing Navigation, kaputte Tabellen.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Admin Translations
  - Ziel: Landingpage- und Unterseiten-Texte sind im Admin erreichbar.
  - Voraussetzung: `SITE_TRANSLATIONS_PATH` zeigt im Backend-Container auf vorhandene `de.json` und `en.json`.
  - Exakte Schritte:
    1. Admin Translations oeffnen.
    2. Gruppen, Common / Shared und Seitentexte pruefen.
    3. Eine harmlose Textaenderung in DEV speichern und danach rueckgaengig machen.
  - Erwartetes Ergebnis: Keine FileNotFoundError-Meldung, Speichern funktioniert.
  - PASS-Kriterium: `de.json`/`en.json` werden geladen, alle Keys sind sichtbar.
  - FAIL-Kriterium: Dateien fehlen, 500, leere Gruppen oder Speichern scheitert.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Admin Product Pricing
  - Ziel: Alle vier Produkte sind zentral sichtbar und editierbar.
  - Voraussetzung: Admin Login erfolgreich.
  - Exakte Schritte:
    1. `/admin/config/license-pricing` oeffnen.
    2. Produkte `assessment`, `validation_check`, `monitoring_monthly`, `monitoring_annual` pruefen.
    3. Einen Preis in DEV aendern, Public Pricing API pruefen, Wert rueckgaengig machen.
  - Erwartetes Ergebnis: Aenderungen werden gespeichert und in `/pricing/public` sichtbar.
  - PASS-Kriterium: Alle vier Produkte vorhanden, valide EUR-Preise, Audit-Eintrag wird erzeugt.
  - FAIL-Kriterium: Produkt fehlt, Preis wird nicht gespeichert, Public API bleibt alt.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Admin Audit Log
  - Ziel: Kritische Admin-Aktionen sind nachvollziehbar.
  - Voraussetzung: Mindestens eine Pricing- oder Translation-Aenderung wurde in DEV ausgefuehrt.
  - Exakte Schritte:
    1. Admin Audit oeffnen.
    2. Benutzer, Zeitpunkt, Aktion und vorher/nachher Details pruefen.
  - Erwartetes Ergebnis: Aenderung ist auditierbar.
  - PASS-Kriterium: Wer, wann, was und relevante Details sichtbar.
  - FAIL-Kriterium: Keine Audit-Zeile oder unbrauchbare Details.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Stripe Testmode

- [ ] Assessment kaufen
  - Ziel: One-time Checkout fuer Assessment funktioniert.
  - Voraussetzung: DEV nutzt Stripe Testmode; `STRIPE_PRICE_ID_ASSESSMENT` ist gesetzt.
  - Exakte Schritte:
    1. Checkout fuer Assessment aus BC oder Dashboard starten.
    2. Stripe Testzahlung erfolgreich abschliessen.
    3. Zur Success-Seite zurueckkehren.
  - Erwartetes Ergebnis: Stripe Checkout zeigt Assessment-Testartikel und leitet zur Success-Seite zurueck.
  - PASS-Kriterium: Checkout Session erfolgreich, Webhook erzeugt Purchase und +1 Scan-Guthaben.
  - FAIL-Kriterium: 503/500, falscher Artikel, kein Webhook, kein Credit.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Validation Check kaufen
  - Ziel: One-time Checkout fuer Validation Check funktioniert.
  - Voraussetzung: `STRIPE_PRICE_ID_VALIDATION_CHECK` ist gesetzt.
  - Exakte Schritte:
    1. Checkout fuer Validation Check starten.
    2. Stripe Testzahlung erfolgreich abschliessen.
    3. License Status aktualisieren.
  - Erwartetes Ergebnis: Validation Check-Testartikel, Success-Seite, +1 Scan-Guthaben.
  - PASS-Kriterium: License API zeigt Validation-Zugriff und Credit.
  - FAIL-Kriterium: Falsches Produkt, kein Credit, Webhook-Fehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Monitoring Monthly kaufen
  - Ziel: Subscription Checkout monatlich funktioniert.
  - Voraussetzung: `STRIPE_PRICE_ID_MONITORING_MONTHLY` ist gesetzt und recurring monthly.
  - Exakte Schritte:
    1. Checkout fuer Monitoring Monthly starten.
    2. Stripe Testzahlung abschliessen.
    3. Webhook und License Status pruefen.
  - Erwartetes Ergebnis: Subscription wird aktiv, Monitoring Access ist aktiv.
  - PASS-Kriterium: `monitoring_active=true`, Subscription im Admin sichtbar.
  - FAIL-Kriterium: Payment Mode statt Subscription Mode, kein Monitoring Access.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Monitoring Annual kaufen
  - Ziel: Subscription Checkout jaehrlich funktioniert.
  - Voraussetzung: `STRIPE_PRICE_ID_MONITORING_ANNUAL` ist gesetzt und recurring yearly.
  - Exakte Schritte:
    1. Checkout fuer Monitoring Annual starten.
    2. Stripe Testzahlung abschliessen.
    3. Webhook und License Status pruefen.
  - Erwartetes Ergebnis: Jahres-Subscription wird aktiv, Monitoring Access ist aktiv.
  - PASS-Kriterium: `monitoring_active=true`, korrektes Annual-Produkt in Stripe/Admin.
  - FAIL-Kriterium: Falscher Intervall, kein Monitoring Access.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Success-Seite pruefen
  - Ziel: Erfolgreiche Stripe Rueckleitung ist verstaendlich und produktneutral.
  - Voraussetzung: Mindestens ein erfolgreicher Test-Checkout.
  - Exakte Schritte:
    1. Nach Stripe-Zahlung auf Success-Seite landen.
    2. Text, Sprache und Links pruefen.
  - Erwartetes Ergebnis: Kein Legacy Free/Trial/Premium, keine i18n Keys.
  - PASS-Kriterium: Success-Seite bestaetigt Kauf ohne falsche Produktversprechen.
  - FAIL-Kriterium: Falsche Begriffe, kaputte Links, Mojibake.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Cancel-Seite pruefen
  - Ziel: Abgebrochener Checkout ist sauber dargestellt.
  - Voraussetzung: Stripe Checkout kann geoeffnet werden.
  - Exakte Schritte:
    1. Checkout starten.
    2. Im Stripe Checkout abbrechen.
    3. Cancel-Seite pruefen.
  - Erwartetes Ergebnis: Abbruchtext ist klar, keine Lizenz-/Credit-Aenderung.
  - PASS-Kriterium: Keine Purchase/Subscription/Credit-Erzeugung.
  - FAIL-Kriterium: Credit trotz Abbruch oder kaputte Cancel-Seite.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Webhook im Backend-Log pruefen
  - Ziel: Stripe Events werden empfangen und verarbeitet.
  - Voraussetzung: Stripe Webhook zeigt auf DEV `/billing/webhook`.
  - Exakte Schritte:
    1. Nach Checkout Backend-Logs lesen.
    2. `checkout.session.completed` und Eventverarbeitung suchen.
  - Erwartetes Ergebnis: Webhook Event wird ohne Fehler verarbeitet.
  - PASS-Kriterium: Event verarbeitet, keine Signature- oder Duplicate-Fehler.
  - FAIL-Kriterium: Kein Event, HTTP 400/500, Signaturfehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Stripe Event ID dokumentieren
  - Ziel: Jeder Test ist gegen Stripe nachvollziehbar.
  - Voraussetzung: Stripe Dashboard Zugriff.
  - Exakte Schritte:
    1. Stripe Event im Testmode oeffnen.
    2. Event ID in Notizen eintragen.
  - Erwartetes Ergebnis: Event ID ist dokumentiert.
  - PASS-Kriterium: Event ID passt zum getesteten Produkt/Tenant.
  - FAIL-Kriterium: Event nicht auffindbar.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] License Status danach pruefen
  - Ziel: Lizenzstatus entspricht Kauf.
  - Voraussetzung: Webhook wurde verarbeitet.
  - Exakte Schritte:
    1. License Refresh in BC ausfuehren.
    2. Backend `/license/status` pruefen.
  - Erwartetes Ergebnis: Produktzugriff, Access Windows und Status stimmen.
  - PASS-Kriterium: One-time Zugriff 7 Tage; Monitoring aktiv bei Subscriptions.
  - FAIL-Kriterium: Kein Zugriff oder falscher Status.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Scan Credits danach pruefen
  - Ziel: One-time Produkte erzeugen Scan-Guthaben.
  - Voraussetzung: Assessment oder Validation Check wurde gekauft.
  - Exakte Schritte:
    1. License Status und BC Setup anzeigen.
    2. Scan-Guthaben vor/nach Kauf vergleichen.
  - Erwartetes Ergebnis: +1 Credit pro One-time Kauf.
  - PASS-Kriterium: Credit ist verfuegbar und wird beim Deep Scan korrekt verbraucht.
  - FAIL-Kriterium: Kein Credit, doppelter Credit oder falscher Verbrauch.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Monitoring Access danach pruefen
  - Ziel: Monitoring-Produkte aktivieren Monitoring-Zugriff.
  - Voraussetzung: Monthly oder Annual wurde gekauft.
  - Exakte Schritte:
    1. License Refresh ausfuehren.
    2. Dashboard und BC Setup auf Monitoring aktiv pruefen.
  - Erwartetes Ergebnis: Monitoring aktiv, wiederholte Scans erlaubt.
  - PASS-Kriterium: `monitoring_active=true`, Trends/Recent Scans erscheinen nur bei Monitoring.
  - FAIL-Kriterium: Monitoring bleibt inaktiv oder erscheint bei Nicht-Monitoring.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Business Central Extension

- [ ] Aktuelle `.app` veroeffentlichen
  - Ziel: DEV BC nutzt die aktuelle Extension-Version.
  - Voraussetzung: AL Build/Package liegt vor.
  - Exakte Schritte:
    1. Aktuelle `.app` in BC Sandbox veroeffentlichen.
    2. App installieren/aktualisieren.
  - Erwartetes Ergebnis: Installation ohne Fehler.
  - PASS-Kriterium: App ist installiert und aktiv.
  - FAIL-Kriterium: Publish/Install/Upgrade scheitert.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] App-Version pruefen
  - Ziel: Sicherstellen, dass keine alte Extension getestet wird.
  - Voraussetzung: App ist installiert.
  - Exakte Schritte:
    1. Extension Management oeffnen.
    2. Version mit `app.json` vergleichen.
  - Erwartetes Ergebnis: Version stimmt.
  - PASS-Kriterium: Installierte Version entspricht Teststand.
  - FAIL-Kriterium: Alte Version aktiv.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Setup Page oeffnen
  - Ziel: Setup ist fuer Admins erreichbar und lokalisiert.
  - Voraussetzung: App installiert.
  - Exakte Schritte:
    1. BCSentinel Setup suchen und oeffnen.
    2. Texte, Felder und Aktionen pruefen.
  - Erwartetes Ergebnis: Seite laedt ohne Fehler, deutsche BC-Umgebung zeigt deutsche Texte.
  - PASS-Kriterium: Keine englischen Pflichttexte ausser definierte Produktbegriffe.
  - FAIL-Kriterium: Page-Fehler, viele englische Texte, Mojibake.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] API URL setzen
  - Ziel: Extension zeigt auf DEV API.
  - Voraussetzung: DEV API Health ist gruen.
  - Exakte Schritte:
    1. API-Basis-URL auf `https://dev-api.bcsentinel.com` setzen.
    2. Setup speichern.
  - Erwartetes Ergebnis: URL wird gespeichert.
  - PASS-Kriterium: Keine lokale/alte API URL aktiv.
  - FAIL-Kriterium: URL wird nicht gespeichert oder zeigt auf falsche Umgebung.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Connection Test
  - Ziel: BC kann Backend erreichen.
  - Voraussetzung: API URL gesetzt.
  - Exakte Schritte:
    1. Connection Test Aktion ausfuehren.
    2. Backend-Log parallel beobachten.
  - Erwartetes Ergebnis: Erfolgreicher Health/API-Test.
  - PASS-Kriterium: BC zeigt Erfolg, Backend erhaelt Request.
  - FAIL-Kriterium: Timeout, 401/500/502.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Tenant registrieren
  - Ziel: BC Mandant wird im Backend angelegt.
  - Voraussetzung: Invite/Self-Service Flow fuer DEV geklaert.
  - Exakte Schritte:
    1. Registrieren aus Setup ausfuehren.
    2. Admin Tenants pruefen.
  - Erwartetes Ergebnis: Tenant existiert mit Sprache, Company-Kontext und Tokenstatus.
  - PASS-Kriterium: Tenant sichtbar, keine Secrets in UI.
  - FAIL-Kriterium: Registrierung scheitert oder falscher Tenant.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] API Token speichern
  - Ziel: Token wird sicher gespeichert und nicht sichtbar angezeigt.
  - Voraussetzung: Registrierung erfolgreich.
  - Exakte Schritte:
    1. Setup pruefen.
    2. Token-Anzeige und gespeicherten Status pruefen.
  - Erwartetes Ergebnis: Token ist konfiguriert, aber nicht im Klartext sichtbar.
  - PASS-Kriterium: Keine Token-Leaks in Page, Fehlertexten oder Logs.
  - FAIL-Kriterium: Token sichtbar oder in URL/Log.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] License Refresh
  - Ziel: BC zeigt aktuellen Lizenz-/Produktstatus.
  - Voraussetzung: Tenant registriert und API Token gueltig.
  - Exakte Schritte:
    1. Lizenz aktualisieren ausfuehren.
    2. Produktzugriff, Credits und Monitoring Status pruefen.
  - Erwartetes Ergebnis: Werte entsprechen Backend.
  - PASS-Kriterium: Keine Rohfehler, korrekte DE/EN Sprache.
  - FAIL-Kriterium: Falsche Werte oder 401/500.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Checkout aus BC starten
  - Ziel: BC-Kaufaktionen starten Stripe Checkout.
  - Voraussetzung: Billing DEV ist gruen.
  - Exakte Schritte:
    1. Jede Kaufaktion aus Setup starten.
    2. Stripe Artikel pruefen.
  - Erwartetes Ergebnis: Assessment, Validation Check, Monthly und Annual starten korrekt.
  - PASS-Kriterium: Kein 503, richtige Testartikel.
  - FAIL-Kriterium: Falscher Artikel, Backend-Fehler, kein Redirect.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Scan Credits Anzeige pruefen
  - Ziel: BC zeigt Scan-Guthaben korrekt.
  - Voraussetzung: One-time Kauf oder Admin Grant.
  - Exakte Schritte:
    1. License Refresh ausfuehren.
    2. Scan-Guthaben auf Setup Page pruefen.
  - Erwartetes Ergebnis: Anzeige entspricht Backend.
  - PASS-Kriterium: Zahl stimmt vor/nach Scan.
  - FAIL-Kriterium: Veralteter oder falscher Wert.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Monitoring Anzeige pruefen
  - Ziel: BC zeigt Monitoring aktiv/inaktiv korrekt.
  - Voraussetzung: Monitoring-Kauf oder Nicht-Monitoring-Tenant.
  - Exakte Schritte:
    1. License Refresh ausfuehren.
    2. Monitoring-Feld pruefen.
  - Erwartetes Ergebnis: Anzeige passt zum Produktzugriff.
  - PASS-Kriterium: Monitoring nur bei Monthly/Annual aktiv.
  - FAIL-Kriterium: Monitoring faelschlich aktiv/inaktiv.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Scan E2E

- [ ] Quick Scan starten
  - Ziel: Quick Scan funktioniert aus BC.
  - Voraussetzung: Tenant registriert, API erreichbar.
  - Exakte Schritte:
    1. Quick Scan Aktion starten.
    2. Ergebnis und Backend-Log pruefen.
  - Erwartetes Ergebnis: Scan Request und Ergebnis ohne Fehler.
  - PASS-Kriterium: Ergebnis sichtbar, keine Rohfehler.
  - FAIL-Kriterium: Request fehlt oder Fehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Deep Scan starten
  - Ziel: Deep Scan startet wirklich und erzeugt History.
  - Voraussetzung: Credit oder Monitoring Access vorhanden.
  - Exakte Schritte:
    1. Deep Scan bestaetigen.
    2. Backend-Log auf Start-Endpunkt pruefen.
    3. Scan History pruefen.
  - Erwartetes Ergebnis: Neuer Scan Run wird angelegt.
  - PASS-Kriterium: Start-Endpunkt aufgerufen, History-Eintrag vorhanden.
  - FAIL-Kriterium: Nur `/scan/status/update`, kein Start, kein History-Eintrag.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Scan History pruefen
  - Ziel: Vergangene Scans werden korrekt angezeigt.
  - Voraussetzung: Mindestens ein abgeschlossener Scan.
  - Exakte Schritte:
    1. Scan History Page oeffnen.
    2. Datum, Status, Score und Verlustwerte pruefen.
  - Erwartetes Ergebnis: Kein Mojibake, korrekte Werte.
  - PASS-Kriterium: Scan sichtbar und konsistent.
  - FAIL-Kriterium: Fehlender Scan, falscher Status, Encodingfehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Scan Monitor oeffnen
  - Ziel: Laufender Scan ist nachvollziehbar.
  - Voraussetzung: Deep Scan wurde gestartet.
  - Exakte Schritte:
    1. Deep Scan Monitor oeffnen.
    2. Status und Fortschritt beobachten.
  - Erwartetes Ergebnis: queued/running/completed werden korrekt angezeigt.
  - PASS-Kriterium: Monitor aktualisiert sich, kein kaputter Progress.
  - FAIL-Kriterium: Monitor haengt oder zeigt Mojibake.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] ScanMonitorFix v2 pruefen
  - Ziel: Der bekannte Monitor-Fix ist in der aktuellen Extension aktiv.
  - Voraussetzung: Aktuelle `.app` installiert.
  - Exakte Schritte:
    1. Deep Scan starten.
    2. Monitor und History parallel pruefen.
  - Erwartetes Ergebnis: Statuswechsel und History-Sync laufen stabil.
  - PASS-Kriterium: Kein leerer/alter Monitorzustand nach Start.
  - FAIL-Kriterium: Monitor zeigt keinen neuen Run.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Status queued/running/completed pruefen
  - Ziel: Scan-Lifecycle ist sichtbar.
  - Voraussetzung: Deep Scan mit ausreichender Laufzeit.
  - Exakte Schritte:
    1. Start ausloesen.
    2. Statusfolge im Backend/BC beobachten.
  - Erwartetes Ergebnis: Status wandert korrekt.
  - PASS-Kriterium: Kein direkter Fake-Erfolg ohne echten Run.
  - FAIL-Kriterium: Status bleibt haengen oder springt falsch.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Fehlerfall pruefen
  - Ziel: Scan-Fehler werden sicher und verstaendlich gemeldet.
  - Voraussetzung: Testtenant oder absichtlich ungueltige API-Konfiguration.
  - Exakte Schritte:
    1. Fehlerfall kontrolliert ausloesen.
    2. BC-Meldung und Backend-Log pruefen.
  - Erwartetes Ergebnis: Keine Tokens/Interna in UI.
  - PASS-Kriterium: Sichere Meldung, Request-ID oder Supporthinweis.
  - FAIL-Kriterium: Rohes JSON, Tokens, Stacktrace.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Credit-Verbrauch pruefen
  - Ziel: Deep Scan verbraucht Credit nur bei erfolgreichem Start.
  - Voraussetzung: One-time Credit vorhanden.
  - Exakte Schritte:
    1. Credit vor Scan notieren.
    2. Deep Scan starten.
    3. License Refresh ausfuehren.
  - Erwartetes Ergebnis: Credit wird genau einmal verbraucht.
  - PASS-Kriterium: Kein Verbrauch bei abgelehntem Start.
  - FAIL-Kriterium: Doppelter Verbrauch oder Verbrauch ohne Run.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Monitoring ohne Credit pruefen
  - Ziel: Monitoring-Tenants koennen ohne One-time Credit scannen.
  - Voraussetzung: Monitoring Monthly oder Annual aktiv.
  - Exakte Schritte:
    1. Credits auf 0 pruefen.
    2. Deep Scan starten.
  - Erwartetes Ergebnis: Scan startet wegen Monitoring Access.
  - PASS-Kriterium: Kein Credit-Blocker bei aktivem Monitoring.
  - FAIL-Kriterium: Scan wird faelschlich wegen 0 Credits blockiert.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Dashboard

- [ ] Dashboard aus BC oeffnen
  - Ziel: BC oeffnet Analytics Dashboard fuer den Tenant.
  - Voraussetzung: Tenant registriert, Token/Embed Flow aktiv.
  - Exakte Schritte:
    1. Dashboard Aktion in BC ausfuehren.
    2. Rendering im Browser/ControlAddIn pruefen.
  - Erwartetes Ergebnis: Dashboard laedt ohne Tokenanzeige.
  - PASS-Kriterium: Kein sichtbarer Token, kein 401/500.
  - FAIL-Kriterium: Token sichtbar, Dashboard leer oder Fehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Analytics Embed Token pruefen
  - Ziel: Keine API Tokens in URL/Logs.
  - Voraussetzung: Dashboard wurde geoeffnet.
  - Exakte Schritte:
    1. Browser URL/Network grob pruefen.
    2. Backend-Logs auf Token-Leaks pruefen.
  - Erwartetes Ergebnis: Kein API Token sichtbar oder geloggt.
  - PASS-Kriterium: Nur erlaubter kurzlebiger Embed-Flow, kein API Token.
  - FAIL-Kriterium: API Token in URL, UI oder Log.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Data Health Score pruefen
  - Ziel: Score wird konsistent angezeigt.
  - Voraussetzung: Scan mit Findings vorhanden.
  - Exakte Schritte:
    1. Dashboard oeffnen.
    2. Score mit Scan/Report vergleichen.
  - Erwartetes Ergebnis: Score plausibel und lokalisiert.
  - PASS-Kriterium: Keine Platzhalter, konsistente Werte.
  - FAIL-Kriterium: `undefined`, falsche Sprache, Wert fehlt.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Issue Details pruefen
  - Ziel: Findings/Issues sind oeffenbar und verstaendlich.
  - Voraussetzung: Dashboard mit Issues.
  - Exakte Schritte:
    1. Issue Detail oeffnen.
    2. Severity, Modul, Betrag und Empfehlung pruefen.
  - Erwartetes Ergebnis: DE/EN konsistent, keine Rohdaten.
  - PASS-Kriterium: Details passen zum Scan.
  - FAIL-Kriterium: Sprachmix, leere Details, falsche Betrage.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] ScoreTrend nur bei Monitoring
  - Ziel: Monitoring-spezifische Trends erscheinen nur bei Monitoring.
  - Voraussetzung: Vergleich Tenant mit und ohne Monitoring.
  - Exakte Schritte:
    1. Dashboard ohne Monitoring oeffnen.
    2. Dashboard mit Monitoring oeffnen.
  - Erwartetes Ergebnis: ScoreTrend nur beim Monitoring-Tenant.
  - PASS-Kriterium: Keine falsche Trendanzeige bei Assessment/Validation.
  - FAIL-Kriterium: Trend bei Nicht-Monitoring sichtbar.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] LossTrend nur bei Monitoring
  - Ziel: Verlusttrend ist Monitoring-spezifisch.
  - Voraussetzung: Vergleich Tenant mit und ohne Monitoring.
  - Exakte Schritte:
    1. LossTrend-Anzeige in beiden Tenants pruefen.
  - Erwartetes Ergebnis: LossTrend nur mit Monitoring.
  - PASS-Kriterium: Nicht-Monitoring zeigt passende eingeschraenkte Ansicht.
  - FAIL-Kriterium: LossTrend erscheint ohne Monitoring.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Recent Scans nur bei Monitoring
  - Ziel: Historien-/Automationsmehrwert ist korrekt eingeschraenkt.
  - Voraussetzung: Vergleich Tenant mit und ohne Monitoring.
  - Exakte Schritte:
    1. Recent Scans Bereich pruefen.
  - Erwartetes Ergebnis: Voller Recent-Scans-Bereich nur bei Monitoring.
  - PASS-Kriterium: Keine irrefuehrende Anzeige fuer One-time Produkte.
  - FAIL-Kriterium: Nicht-Monitoring sieht Monitoring-Verlauf.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Nicht-Monitoring-Ansicht pruefen
  - Ziel: Assessment/Validation Kunden sehen passende eingeschraenkte Ansicht.
  - Voraussetzung: One-time Produkt aktiv, kein Monitoring.
  - Exakte Schritte:
    1. Dashboard oeffnen.
    2. CTA und Access-Hinweise pruefen.
  - Erwartetes Ergebnis: Kein Monthly/Annual als aktiver Status, passende CTA.
  - PASS-Kriterium: Klare Anzeige fuer One-time Access.
  - FAIL-Kriterium: Falsche Subscription-Infos.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] DE/EN Sprache pruefen
  - Ziel: Dashboard folgt BC-/Tenant-Sprache.
  - Voraussetzung: Testtenant DE und EN.
  - Exakte Schritte:
    1. DE Tenant Dashboard oeffnen.
    2. EN Tenant Dashboard oeffnen.
  - Erwartetes Ergebnis: DE fuer deutsche BC-Sprache, sonst EN.
  - PASS-Kriterium: Keine sichtbare Sprachmischung.
  - FAIL-Kriterium: Gemischte Labels oder fehlende Keys.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Reports

- [ ] Executive HTML oeffnen
  - Ziel: HTML Executive Report ist erreichbar.
  - Voraussetzung: Scan mit Reportdaten vorhanden.
  - Exakte Schritte:
    1. Executive HTML Link oeffnen.
    2. Inhalt und Layout pruefen.
  - Erwartetes Ergebnis: Professioneller Report ohne Platzhalter.
  - PASS-Kriterium: Management Summary, Befunde und Empfehlungen sichtbar.
  - FAIL-Kriterium: 404/500, leere Bereiche, Platzhalter.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Executive PDF oeffnen
  - Ziel: PDF Report wird generiert.
  - Voraussetzung: PDF Renderer im Backend verfuegbar.
  - Exakte Schritte:
    1. PDF Link oeffnen.
    2. Dateityp und Layout pruefen.
  - Erwartetes Ergebnis: PDF laedt und ist lesbar.
  - PASS-Kriterium: Kein HTML-Fehler als PDF, keine kaputten Umlaute.
  - FAIL-Kriterium: 500, leeres PDF, Encodingfehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] PDF herunterladen
  - Ziel: Kunde kann PDF speichern.
  - Voraussetzung: PDF Report laedt.
  - Exakte Schritte:
    1. PDF herunterladen.
    2. Datei lokal oeffnen.
  - Erwartetes Ergebnis: Datei ist vollstaendig und korrekt benannt.
  - PASS-Kriterium: PDF oeffnet offline.
  - FAIL-Kriterium: Beschaedigte Datei.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Share Link HTML oeffnen
  - Ziel: Geteilter HTML Report funktioniert ohne Login im erlaubten Rahmen.
  - Voraussetzung: Share Link erzeugt.
  - Exakte Schritte:
    1. Share HTML Link oeffnen.
    2. Tenant-Isolation und Ablaufhinweis pruefen.
  - Erwartetes Ergebnis: Report sichtbar, Link enthaelt kein localhost.
  - PASS-Kriterium: Oeffentlich nutzbar bis Ablauf, keine falschen Daten.
  - FAIL-Kriterium: localhost, falscher Tenant, 500.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Share Link PDF oeffnen
  - Ziel: Geteilter PDF Report funktioniert.
  - Voraussetzung: PDF Share Link erzeugt.
  - Exakte Schritte:
    1. PDF Share Link oeffnen.
    2. Inhalt pruefen.
  - Erwartetes Ergebnis: PDF ist erreichbar und korrekt.
  - PASS-Kriterium: Kein Login erforderlich, aber Token/Ablauf gueltig.
  - FAIL-Kriterium: 404/500 oder falscher Tenant.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Share Link im privaten Browser oeffnen
  - Ziel: Share Link ist nicht von lokaler Session abhaengig.
  - Voraussetzung: Gueltiger Share Link.
  - Exakte Schritte:
    1. Privates Browserfenster oeffnen.
    2. Share Link einfuegen.
  - Erwartetes Ergebnis: Report laedt ohne Admin/BC Session.
  - PASS-Kriterium: Nur gueltiger Share Token reicht.
  - FAIL-Kriterium: Session-Abhaengigkeit oder Login-Fehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Ablaufzeit pruefen
  - Ziel: Share Links laufen ab.
  - Voraussetzung: Testlink mit kurzer TTL oder simulierter Ablauf.
  - Exakte Schritte:
    1. Link vor Ablauf pruefen.
    2. Link nach Ablauf pruefen.
  - Erwartetes Ergebnis: Vor Ablauf 200, nach Ablauf gesperrt.
  - PASS-Kriterium: Abgelaufener Link liefert sichere Fehlermeldung.
  - FAIL-Kriterium: Link bleibt unbegrenzt gueltig.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Kein localhost in Links
  - Ziel: Reports nutzen `APP_BASE_URL`/oeffentliche Base URL.
  - Voraussetzung: `APP_BASE_URL` in DEV/PROD gesetzt.
  - Exakte Schritte:
    1. Executive Report mit Share Links erzeugen.
    2. HTML/PDF Linkziele pruefen.
  - Erwartetes Ergebnis: Keine `localhost` oder `127.0.0.1` Links.
  - PASS-Kriterium: Links beginnen mit oeffentlicher Base URL.
  - FAIL-Kriterium: Link enthaelt localhost.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] DE/EN pruefen
  - Ziel: Reports folgen Tenant-Sprache.
  - Voraussetzung: DE und EN Testtenant.
  - Exakte Schritte:
    1. Report fuer DE Tenant erzeugen.
    2. Report fuer EN Tenant erzeugen.
  - Erwartetes Ergebnis: Sprache konsistent.
  - PASS-Kriterium: Keine gemischten Labels ausser definierte Produktbegriffe.
  - FAIL-Kriterium: Sprachmix oder fehlende Uebersetzung.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Management Summary pruefen
  - Ziel: Management Summary ist kundentauglich.
  - Voraussetzung: Executive Report vorhanden.
  - Exakte Schritte:
    1. Summary lesen.
    2. Bezug zu Score, Verlust und Hauptproblemen pruefen.
  - Erwartetes Ergebnis: Klar, kurz, ohne Platzhalter.
  - PASS-Kriterium: Management-tauglicher Text.
  - FAIL-Kriterium: Generisch, leer oder technisch.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Priority/Risk Matrix pruefen
  - Ziel: Priorisierung ist sichtbar.
  - Voraussetzung: Report mit mehreren Findings.
  - Exakte Schritte:
    1. Risk/Priority Bereich pruefen.
  - Erwartetes Ergebnis: Risiken und Prioritaeten sind nachvollziehbar.
  - PASS-Kriterium: Matrix oder aequivalente Priorisierung vorhanden.
  - FAIL-Kriterium: Keine Priorisierung.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Next Best Action pruefen
  - Ziel: Report enthaelt konkrete naechste Schritte.
  - Voraussetzung: Executive Report vorhanden.
  - Exakte Schritte:
    1. Next Best Action Abschnitt pruefen.
  - Erwartetes Ergebnis: Handlungsempfehlung ist sichtbar und sprachlich passend.
  - PASS-Kriterium: Klare naechste Aktion fuer Kunde.
  - FAIL-Kriterium: Abschnitt fehlt oder ist Platzhalter.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Open in BC

- [ ] Issue im Dashboard oeffnen
  - Ziel: Ein konkretes Issue ist im Dashboard auswaehlbar.
  - Voraussetzung: Dashboard mit Issues.
  - Exakte Schritte:
    1. Issue Detail oeffnen.
    2. Open-in-BC Aktion lokalisieren.
  - Erwartetes Ergebnis: Aktion ist sichtbar, wenn BC-Ziel existiert.
  - PASS-Kriterium: Aktion passt zum Issue.
  - FAIL-Kriterium: Aktion fehlt trotz BC-Ziel.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Open in BC klicken
  - Ziel: Link oeffnet Business Central.
  - Voraussetzung: BC Session im Browser vorhanden.
  - Exakte Schritte:
    1. Open in BC klicken.
    2. Browser/BC Ziel pruefen.
  - Erwartetes Ergebnis: BC oeffnet ohne unnoetige Zwischenseite.
  - PASS-Kriterium: Nutzer landet direkt am relevanten Ziel.
  - FAIL-Kriterium: Generische Drilldown-Zwischenseite.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Direkt zur korrekten BC-Seite springen
  - Ziel: Issue-Kontext fuehrt zur passenden BC-Werteseite.
  - Voraussetzung: Issue enthaelt Zielkontext.
  - Exakte Schritte:
    1. Open-in-BC Ziel mit Issue vergleichen.
  - Erwartetes Ergebnis: Relevanter Datensatz oder relevante Liste oeffnet.
  - PASS-Kriterium: Tenant, Company und Datensatz passen.
  - FAIL-Kriterium: Falsche Seite oder falscher Datensatz.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Tenant/Company-Kontext stimmt
  - Ziel: Kein Cross-Tenant/Company-Sprung.
  - Voraussetzung: Testtenant mit bekannter Company.
  - Exakte Schritte:
    1. Open-in-BC Link und Zielcompany pruefen.
  - Erwartetes Ergebnis: Kontext bleibt korrekt.
  - PASS-Kriterium: Kein fremder Mandant, keine fremde Company.
  - FAIL-Kriterium: Falscher Kontext.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Kein unnoetiger Zwischenschritt
  - Ziel: UX ist direkt.
  - Voraussetzung: Open-in-BC Ziel vorhanden.
  - Exakte Schritte:
    1. Klickpfad dokumentieren.
  - Erwartetes Ergebnis: Maximal Browser/BC-Auth, keine interne Drilldown-Zwischenseite.
  - PASS-Kriterium: Direkter Zielaufruf.
  - FAIL-Kriterium: Nutzer muss manuell suchen.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Fehlerfall bei fehlender Berechtigung pruefen
  - Ziel: Fehlende BC-Berechtigungen werden verstaendlich behandelt.
  - Voraussetzung: Testnutzer ohne Zielberechtigung.
  - Exakte Schritte:
    1. Open in BC mit eingeschraenktem Nutzer ausfuehren.
  - Erwartetes Ergebnis: BC zeigt sichere, verstaendliche Fehlermeldung.
  - PASS-Kriterium: Kein Datenleck, klare Meldung.
  - FAIL-Kriterium: Falscher Zugriff oder technische Rohmeldung.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Landingpage

- [ ] Desktop Light
  - Ziel: Landingpage sieht im hellen Theme korrekt aus.
  - Voraussetzung: Browser mit leerem oder Light localStorage.
  - Exakte Schritte:
    1. Jede oeffentliche Pflichtseite im Desktop Viewport oeffnen.
    2. Light Theme pruefen.
  - Erwartetes Ergebnis: Layout sauber, Text lesbar.
  - PASS-Kriterium: Keine Ueberlappungen, keine kaputten Farben.
  - FAIL-Kriterium: Text unlesbar oder Layout kaputt.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Desktop Dark
  - Ziel: Dark Theme funktioniert.
  - Voraussetzung: Theme Toggle sichtbar.
  - Exakte Schritte:
    1. Dark Theme aktivieren.
    2. Pflichtseiten pruefen.
  - Erwartetes Ergebnis: Theme bleibt per localStorage erhalten.
  - PASS-Kriterium: Kein sichtbarer Text `Light`/`Dark`, nur Icon/Button.
  - FAIL-Kriterium: Toggle ohne Wirkung oder Textfehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Mobile
  - Ziel: Mobile Navigation und Layout sind nutzbar.
  - Voraussetzung: Browser DevTools oder echtes Smartphone.
  - Exakte Schritte:
    1. Pflichtseiten mobil oeffnen.
    2. Navigation, CTA und Footer pruefen.
  - Erwartetes Ergebnis: Keine horizontalen Ueberlaeufe, Menue funktioniert.
  - PASS-Kriterium: Alle Links klickbar, Text passt.
  - FAIL-Kriterium: Menue blockiert, Text ueberlappt.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Header/Footer
  - Ziel: Einheitlicher Site-Shell-Look.
  - Voraussetzung: Aktuelle Landingpage deployed.
  - Exakte Schritte:
    1. Alle Pflichtseiten oeffnen.
    2. Header/Footer vergleichen.
  - Erwartetes Ergebnis: Gleicher Look; Header-Mitte seitenspezifisch; Footer global.
  - PASS-Kriterium: Keine alten abweichenden Header.
  - FAIL-Kriterium: Unterschiedliche Header-Strukturen oder zusammengeklebte Links.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] DE/EN Umschaltung
  - Ziel: Sprache laesst sich auf jeder Seite umschalten.
  - Voraussetzung: `de.json` und `en.json` erreichbar.
  - Exakte Schritte:
    1. Sprache auf DE stellen.
    2. Sprache auf EN stellen.
    3. localStorage Persistenz pruefen.
  - Erwartetes Ergebnis: Texte wechseln ohne Reloadfehler.
  - PASS-Kriterium: Keine i18n Keys oder `undefined`.
  - FAIL-Kriterium: Toggle ohne Wirkung oder fehlende Texte.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Theme Toggle
  - Ziel: Theme Toggle funktioniert ohne sichtbaren Light/Dark-Text.
  - Voraussetzung: Header geladen.
  - Exakte Schritte:
    1. Toggle mehrfach klicken.
    2. Reload ausfuehren.
  - Erwartetes Ergebnis: Theme bleibt gespeichert.
  - PASS-Kriterium: Icon/Button korrekt, keine Textreste.
  - FAIL-Kriterium: localStorage wird ignoriert.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Pricing
  - Ziel: Preise stammen aus Product Pricing/Public API.
  - Voraussetzung: Backend `/pricing/public` erreichbar.
  - Exakte Schritte:
    1. Pricing Cards oeffnen.
    2. Preise mit Admin Product Pricing vergleichen.
  - Erwartetes Ergebnis: 79, 49, 99/Monat, 990/Jahr.
  - PASS-Kriterium: Keine alten Preise sichtbar.
  - FAIL-Kriterium: Alte Premium/Trial/Free oder falsche Preise.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Partner-Seiten
  - Ziel: Partner Login/Register/Reset/Portal sind erreichbar.
  - Voraussetzung: Landingpage deployed.
  - Exakte Schritte:
    1. Partner-Seiten oeffnen.
    2. Header/Footer und Formulare pruefen.
  - Erwartetes Ergebnis: Seiten laden ohne kaputte Navigation.
  - PASS-Kriterium: Kein 404/500, Formulare plausibel.
  - FAIL-Kriterium: Kaputte Seite oder falsche Links.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Billing Success
  - Ziel: Success-Seite ist erreichbar und sauber lokalisiert.
  - Voraussetzung: Landingpage deployed.
  - Exakte Schritte:
    1. `billing-success.html` oeffnen.
    2. DE/EN und CTA pruefen.
  - Erwartetes Ergebnis: Kein kaputter Text.
  - PASS-Kriterium: Kein Mojibake, keine alten Begriffe.
  - FAIL-Kriterium: Textfehler oder falsche Produktlogik.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Billing Cancel
  - Ziel: Cancel-Seite ist erreichbar und sauber lokalisiert.
  - Voraussetzung: Landingpage deployed.
  - Exakte Schritte:
    1. `billing-cancel.html` oeffnen.
    2. DE/EN und CTA pruefen.
  - Erwartetes Ergebnis: Klarer Abbruchtext.
  - PASS-Kriterium: Kein Mojibake, keine alten Begriffe.
  - FAIL-Kriterium: Textfehler oder falsche Produktlogik.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Keine i18n Keys sichtbar
  - Ziel: Keine technischen Keys erscheinen im UI.
  - Voraussetzung: Alle Pflichtseiten erreichbar.
  - Exakte Schritte:
    1. Seiten visuell pruefen.
    2. Nach Mustern wie `nav_`, `docs_`, `undefined` suchen.
  - Erwartetes Ergebnis: Nur fertige Texte sichtbar.
  - PASS-Kriterium: Keine Keys/undefined.
  - FAIL-Kriterium: Sichtbare Keys.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Keine Free/Trial/Premium-Reste sichtbar
  - Ziel: Alte Produktbegriffe sind aus Kundentexten entfernt.
  - Voraussetzung: Alle Pflichtseiten, Dashboard, Admin und BC Setup pruefbar.
  - Exakte Schritte:
    1. Sichtpruefung aller relevanten UIs.
    2. Browser-Suche nach Free, Trial, Premium.
  - Erwartetes Ergebnis: Nur neue Produktstruktur sichtbar.
  - PASS-Kriterium: Keine alten Kundentexte.
  - FAIL-Kriterium: Sichtbarer alter Produkttext.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Keine Mojibake
  - Ziel: Keine Encodingfehler sichtbar.
  - Voraussetzung: Alle Pflichtseiten erreichbar.
  - Exakte Schritte:
    1. Sichtpruefung.
    2. Besonders Euro-Zeichen und Progress/Charts pruefen.
  - Erwartetes Ergebnis: Keine Zeichen wie `Ã`, `â`, `�`.
  - PASS-Kriterium: Umlaute und Euro-Zeichen korrekt.
  - FAIL-Kriterium: Mojibake sichtbar.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## PROD Dry Run

- [ ] PROD ENV vollstaendig
  - Ziel: PROD-Konfiguration ist startfaehig und sicher.
  - Voraussetzung: `.env.prod` vorhanden.
  - Exakte Schritte:
    1. Pflichtvariablen ohne Secret-Werte pruefen.
    2. `APP_BASE_URL`, Stripe Live Keys, CORS, DB, Secret Key, Site Translation Path pruefen.
  - Erwartetes Ergebnis: Keine DEV-Defaults in PROD.
  - PASS-Kriterium: Keine dev.bcsentinel.com-Origin in PROD-CORS, keine Test-Stripe-Keys.
  - FAIL-Kriterium: Fehlende Pflichtvariable oder DEV/Test-Werte.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Docker Build PROD
  - Ziel: PROD Image baut ohne Tests im Image.
  - Voraussetzung: Docker auf Server verfuegbar.
  - Exakte Schritte:
    1. `docker compose --env-file .env.prod -f docker-compose.prod.yml build`
  - Erwartetes Ergebnis: Build erfolgreich.
  - PASS-Kriterium: Keine Buildfehler, production target wird genutzt.
  - FAIL-Kriterium: Build bricht ab.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Migration Service
  - Ziel: DB ist auf Alembic Head.
  - Voraussetzung: Backup vorhanden.
  - Exakte Schritte:
    1. `docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm migration`
    2. `alembic_version` pruefen.
  - Erwartetes Ergebnis: Migration laeuft ohne destruktive Datenloeschung.
  - PASS-Kriterium: DB Head entspricht Alembic Head.
  - FAIL-Kriterium: Migration bricht ab oder Schema Drift.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Backend Start
  - Ziel: PROD Backend startet stabil.
  - Voraussetzung: Migration erfolgreich.
  - Exakte Schritte:
    1. `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d backend`
    2. `docker compose --env-file .env.prod -f docker-compose.prod.yml ps`
  - Erwartetes Ergebnis: Backend bleibt Up.
  - PASS-Kriterium: Kein Restart-Loop.
  - FAIL-Kriterium: Container Restarting oder exited.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Nginx Test
  - Ziel: Reverse Proxy-Konfiguration ist gueltig.
  - Voraussetzung: nginx Config deployed.
  - Exakte Schritte:
    1. `sudo nginx -t`
    2. `sudo systemctl reload nginx`
  - Erwartetes Ergebnis: Syntax OK und Reload erfolgreich.
  - PASS-Kriterium: Kein nginx Fehler.
  - FAIL-Kriterium: Syntaxfehler oder Reload-Fehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] TLS/HTTPS
  - Ziel: Oeffentliche Domains laufen per HTTPS.
  - Voraussetzung: Zertifikate vorhanden.
  - Exakte Schritte:
    1. `curl -I https://api.bcsentinel.com/health`
    2. `curl -I https://www.bcsentinel.com/`
  - Erwartetes Ergebnis: Gueltiges TLS, HTTP 200/301 wie erwartet.
  - PASS-Kriterium: Kein Zertifikatsfehler.
  - FAIL-Kriterium: TLS-Fehler oder 502.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Health Ready
  - Ziel: Backend Readiness ist gruen.
  - Voraussetzung: Backend gestartet.
  - Exakte Schritte:
    1. `curl -i http://127.0.0.1:8000/health/ready`
    2. `curl -I https://api.bcsentinel.com/health`
  - Erwartetes Ergebnis: 200 lokal und oeffentlich.
  - PASS-Kriterium: Readiness prueft DB/Schema erfolgreich.
  - FAIL-Kriterium: 500/502/503.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Backup erstellen
  - Ziel: Vor PROD-Start ist ein Restore-faehiges Backup vorhanden.
  - Voraussetzung: DB Zugriff.
  - Exakte Schritte:
    1. `pg_dump "$DATABASE_URL" > backup-before-golive.sql`
    2. Datei sicher ablegen.
  - Erwartetes Ergebnis: Backup-Datei vorhanden.
  - PASS-Kriterium: Backup groesser 0 Byte und ohne Fehler erstellt.
  - FAIL-Kriterium: Backup fehlt oder pg_dump Fehler.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Restore testen
  - Ziel: Backup ist praktisch wiederherstellbar.
  - Voraussetzung: Separate Restore-Testdatenbank.
  - Exakte Schritte:
    1. `psql "$RESTORE_TEST_DATABASE_URL" < backup-before-golive.sql`
    2. App/Schema pruefen.
  - Erwartetes Ergebnis: Restore laeuft durch.
  - PASS-Kriterium: Tabellen und `alembic_version` vorhanden.
  - FAIL-Kriterium: Restore bricht ab oder DB unbrauchbar.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Rollback testen
  - Ziel: Fehlerhafter Release kann zurueckgenommen werden.
  - Voraussetzung: Vorheriger stabiler Release/Branch bekannt.
  - Exakte Schritte:
    1. Rollback-Befehl aus `DEPLOYMENT_DRY_RUN.md` trocken durchgehen oder in DEV ausfuehren.
    2. Healthcheck danach pruefen.
  - Erwartetes Ergebnis: System laeuft nach Rollback.
  - PASS-Kriterium: Kein Datenverlust, Health gruen.
  - FAIL-Kriterium: Rollback unklar oder bricht ab.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Security / Datenschutz

- [ ] Keine Secrets im Repo
  - Ziel: Keine Secrets sind versioniert.
  - Voraussetzung: Repo Zugriff.
  - Exakte Schritte:
    1. Secret-Scan oder manuelle Suche nach Keys/Tokens ausfuehren.
    2. `.env*` Status pruefen.
  - Erwartetes Ergebnis: Keine echten Secrets im Git.
  - PASS-Kriterium: Nur Beispiele/Platzhalter.
  - FAIL-Kriterium: Live/Test Secret im Repo.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Keine Tokens in URLs
  - Ziel: API Tokens werden nicht in Querystrings genutzt.
  - Voraussetzung: Dashboard/Reports/BC Flows getestet.
  - Exakte Schritte:
    1. Browser URL/Network pruefen.
    2. Backend-Logs pruefen.
  - Erwartetes Ergebnis: Keine API Tokens in URL/Log.
  - PASS-Kriterium: Embed/Share Tokens sind kurzlebig und keine API Tokens.
  - FAIL-Kriterium: API Token in URL oder Log.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Admin nicht ohne Login erreichbar
  - Ziel: Admin ist geschuetzt.
  - Voraussetzung: Private Browser Session.
  - Exakte Schritte:
    1. `/admin` und Unterseiten ohne Login oeffnen.
  - Erwartetes Ergebnis: Auth Challenge/Login erforderlich.
  - PASS-Kriterium: Kein Admin-Inhalt ohne Login.
  - FAIL-Kriterium: Admin-Daten sichtbar.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Share Links laufen ab
  - Ziel: Geteilte Reports sind zeitlich begrenzt.
  - Voraussetzung: Share Link mit bekannter TTL.
  - Exakte Schritte:
    1. Ablauf wie im Report-Abschnitt pruefen.
  - Erwartetes Ergebnis: Abgelaufener Link gesperrt.
  - PASS-Kriterium: Kein unbegrenzter Zugriff.
  - FAIL-Kriterium: Link bleibt dauerhaft aktiv.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Tenant-Isolation geprueft
  - Ziel: Tenant A kann keine Daten von Tenant B sehen.
  - Voraussetzung: Zwei Testtenants.
  - Exakte Schritte:
    1. Mit Tenant-A Token Tenant-B Ressourcen anfragen.
    2. Dashboard/Report/Scan APIs pruefen.
  - Erwartetes Ergebnis: Zugriff verweigert.
  - PASS-Kriterium: 403/404 ohne Datenleck.
  - FAIL-Kriterium: Cross-Tenant-Daten sichtbar.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] CORS korrekt
  - Ziel: PROD erlaubt keine DEV-Origin implizit.
  - Voraussetzung: PROD/DEV ENV bekannt.
  - Exakte Schritte:
    1. `CORS_ALLOW_ORIGINS` und Response Header pruefen.
  - Erwartetes Ergebnis: DEV und PROD sauber getrennt.
  - PASS-Kriterium: PROD ohne `https://dev.bcsentinel.com`.
  - FAIL-Kriterium: DEV-Origin in PROD-CORS.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Security Headers vorhanden
  - Ziel: Basis-Security-Header werden gesetzt.
  - Voraussetzung: Backend/Landingpage erreichbar.
  - Exakte Schritte:
    1. `curl -I` auf API, Dashboard und Landingpage.
  - Erwartetes Ergebnis: Security Header vorhanden.
  - PASS-Kriterium: Mindestens `X-Content-Type-Options`, Referrer Policy und sinnvolle Frame/CSP-Regeln.
  - FAIL-Kriterium: Fehlende kritische Header.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Logs enthalten keine sensiblen Kundendaten
  - Ziel: Logs sind supportfaehig, aber datensparsam.
  - Voraussetzung: Testflows ausgefuehrt.
  - Exakte Schritte:
    1. Backend-Logs nach Token, Headern, Kundendetails, kompletten Payloads pruefen.
  - Erwartetes Ergebnis: Keine Secrets oder sensiblen Rohdaten.
  - PASS-Kriterium: Nur IDs/Request-IDs und noetige technische Metadaten.
  - FAIL-Kriterium: Tokens, Header, sensible Kundendaten im Log.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## AppSource / BC Analyzer

- [ ] AL Compile
  - Ziel: Extension kompiliert sauber.
  - Voraussetzung: AL Toolchain verfuegbar.
  - Exakte Schritte:
    1. AL Package Build ausfuehren.
  - Erwartetes Ergebnis: `.app` wird erzeugt.
  - PASS-Kriterium: Keine Compile Errors.
  - FAIL-Kriterium: Compile Error.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] CodeCop
  - Ziel: CodeCop Analyzer ist aktiv und Ergebnisse sind dokumentiert.
  - Voraussetzung: AL Analyzer Setup.
  - Exakte Schritte:
    1. Build mit CodeCop ausfuehren.
    2. Warnings exportieren/dokumentieren.
  - Erwartetes Ergebnis: Keine neuen Blocker.
  - PASS-Kriterium: Keine kritischen CodeCop-Errors.
  - FAIL-Kriterium: Errors oder unbewertete kritische Warnings.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] UICop
  - Ziel: UI-relevante Captions/ToolTips sind sauber.
  - Voraussetzung: Analyzer verfuegbar.
  - Exakte Schritte:
    1. UICop ausfuehren.
    2. Fehlende ToolTips/Captions pruefen.
  - Erwartetes Ergebnis: Keine sichtbaren UI-Blocker.
  - PASS-Kriterium: Keine kritischen UI-Warnings.
  - FAIL-Kriterium: Fehlende Captions/ToolTips auf sichtbaren Controls.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] AppSourceCop
  - Ziel: AppSource-relevante Blocker sind bekannt.
  - Voraussetzung: AppSourceCop aktiv.
  - Exakte Schritte:
    1. Build mit AppSourceCop ausfuehren.
    2. Restwarnings dokumentieren.
  - Erwartetes Ergebnis: Nur bekannte finale Metadaten/ID-Range Themen offen.
  - PASS-Kriterium: Keine unbekannten technischen Blocker.
  - FAIL-Kriterium: Neue AppSourceCop Errors.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] app.json pruefen
  - Ziel: Manifest ist AppSource-nahe.
  - Voraussetzung: Aktuelle Extension Quellen.
  - Exakte Schritte:
    1. `app.json` auf Publisher, Version, URLs, idRanges, runtime pruefen.
  - Erwartetes Ergebnis: Keine Placeholder fuer Submission.
  - PASS-Kriterium: Finale Werte oder dokumentierte offene Submission-TODOs.
  - FAIL-Kriterium: Fehlende Pflichtmetadaten ohne TODO.
  - Screenshot/Log erforderlich: Nein
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Logo vorhanden
  - Ziel: AppSource Logo-Artefakt ist vorhanden.
  - Voraussetzung: Finales Logo liegt vor.
  - Exakte Schritte:
    1. Logo-Pfad in `app.json` und Datei pruefen.
  - Erwartetes Ergebnis: Logo existiert und ist korrekt referenziert.
  - PASS-Kriterium: Datei vorhanden, Pfad korrekt.
  - FAIL-Kriterium: Logo fehlt.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Privacy URL
  - Ziel: Datenschutz-URL ist final.
  - Voraussetzung: Finaler Datenschutztext veroeffentlicht.
  - Exakte Schritte:
    1. URL in Manifest/Listing oeffnen.
  - Erwartetes Ergebnis: URL liefert 200 und passenden Inhalt.
  - PASS-Kriterium: Keine Placeholder.
  - FAIL-Kriterium: 404 oder unfertiger Inhalt.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Terms/EULA URL
  - Ziel: Terms/EULA URL ist final.
  - Voraussetzung: Finaler Terms/EULA Text veroeffentlicht.
  - Exakte Schritte:
    1. URL oeffnen.
  - Erwartetes Ergebnis: URL liefert 200 und passenden Inhalt.
  - PASS-Kriterium: Keine Placeholder.
  - FAIL-Kriterium: 404 oder unfertiger Inhalt.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Help URL
  - Ziel: Hilfe-Dokumentation ist verlinkt.
  - Voraussetzung: Docs Seite veroeffentlicht.
  - Exakte Schritte:
    1. Help URL oeffnen.
  - Erwartetes Ergebnis: Dokumentation erreichbar.
  - PASS-Kriterium: 200 und brauchbare Setup-Hilfe.
  - FAIL-Kriterium: 404 oder leere Docs.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Support URL
  - Ziel: Support-Kanal ist erreichbar.
  - Voraussetzung: Support/Contact Seite veroeffentlicht.
  - Exakte Schritte:
    1. Support URL oeffnen.
    2. Kontaktweg pruefen.
  - Erwartetes Ergebnis: Kunde kann Support kontaktieren.
  - PASS-Kriterium: Klarer Kontaktweg.
  - FAIL-Kriterium: Kein Supportweg.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Screenshots
  - Ziel: AppSource Listing Assets sind vorbereitet.
  - Voraussetzung: Aktuelle UI Screenshots.
  - Exakte Schritte:
    1. Screenshots fuer Setup, Dashboard, Report und Scan pruefen.
  - Erwartetes Ergebnis: Aktuelle, saubere Screenshots vorhanden.
  - PASS-Kriterium: Keine DEV-Daten/Secrets, hochwertige Darstellung.
  - FAIL-Kriterium: Screenshots fehlen oder zeigen unfertige UI.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

- [ ] Alte Free/Premium/Trial-Begriffe in BC UI/XLF pruefen
  - Ziel: BC Extension zeigt keine alten Produktbegriffe.
  - Voraussetzung: Aktuelle XLF und installierte App.
  - Exakte Schritte:
    1. BC Pages visuell pruefen.
    2. XLF/AL nach sichtbaren Altbegriffen durchsuchen.
  - Erwartetes Ergebnis: Nur Assessment, Validation Check, Monitoring Monthly, Monitoring Annual sichtbar.
  - PASS-Kriterium: Keine alten Kundentexte.
  - FAIL-Kriterium: Free/Premium/Trial sichtbar.
  - Screenshot/Log erforderlich: Ja
  - Ergebnis: PASS / FAIL / BLOCKED
  - Notizen:

## Manuelles Go/No-Go Ergebnis

- [ ] Alle BLOCKER geprueft
- [ ] Alle CRITICAL geprueft
- [ ] Stripe One-Time PASS
- [ ] Stripe Subscription PASS
- [ ] BC Deep Scan PASS
- [ ] Dashboard PASS
- [ ] Executive Report PASS
- [ ] Share Links PASS
- [ ] PROD Dry Run PASS
- [ ] Backup/Restore PASS

Abschlussbewertung:

- Handgefuehrter Pilot: GO / NO-GO
- Erster zahlender Kunde: GO / NO-GO
- AppSource: GO / NO-GO


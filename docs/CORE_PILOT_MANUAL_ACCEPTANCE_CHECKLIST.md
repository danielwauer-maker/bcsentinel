# BCSentinel Core — Manual Pilot Acceptance Checklist

Ziel: letzter manueller Nachweis vor Start und Ausbau des kontrollierten Piloten bis maximal 50 Tenants.

> Alles, was automatisierbar ist, gehört nicht in diese Liste. Ein Punkt darf nur mit realer Runtime-/Operator-Evidence auf PASS gesetzt werden.

## M01 — Business Central Rollenmatrix ohne SUPER

Testumgebung: Business Central SaaS Sandbox, BCSentinel 1.0.2.25, derselbe dokumentierte Non-SUPER-Basisbenutzer.

### SETUP
- [ ] Nur `BCSENTINEL SETUP` zusätzlich zur dokumentierten Standard-BC-Basis zuweisen.
- [ ] Setup öffnen und Tenant registrieren/aktualisieren.
- [ ] Check-Auswahl ändern.
- [ ] Scheduler konfigurieren.
- [ ] Nachweisen, dass direkte Scan-Ergebnis-Schreiboperationen nicht als SETUP-Rolle möglich sind.
- [ ] Effective Permissions + Ergebnis-Screenshots sichern.

### SCHEDULER
- [ ] Nur `BCSENTINEL SCHEDULER` zusätzlich zur Standard-BC-Basis zuweisen.
- [ ] geplanten Scan ausführen lassen.
- [ ] Scan muss vollständig laufen und zum Backend synchronisieren.
- [ ] Setup-Änderung muss verweigert werden.
- [ ] Effective Permissions + Scan-History/Status sichern.

### ADMIN
- [ ] Nur `BCSENTINEL ADMIN` zusätzlich zur Standard-BC-Basis zuweisen; SUPER bleibt aus.
- [ ] Dashboard öffnen.
- [ ] manuellen Scan vollständig ausführen.
- [ ] Setup ändern.
- [ ] Finding/Exception/Correction-Workflow ausführen.
- [ ] Scheduler konfigurieren und ausführen.
- [ ] Effective Permissions + Ergebnisse sichern.

### VIEWER / SCAN Rest-Spotchecks
- [ ] VIEWER: Finding-Drilldown mit realen Findings lesen.
- [ ] VIEWER: Exception anlegen muss verweigert werden.
- [ ] VIEWER: Finding als korrigiert markieren muss verweigert werden.
- [ ] SCAN: Exception anlegen.
- [ ] SCAN: Finding als korrigiert markieren.
- [ ] SCAN: Setup-Änderung bleibt verweigert.

PASS-Kriterium: keine Rolle benötigt SUPER; alle erlaubten Aktionen funktionieren und alle verbotenen Aktionen scheitern kontrolliert.

## M02 — Produkt-/Checkout-Runtime-Smoke

Mit Testtenant und Test-Zahlungs-/Grant-Prozess:

- [ ] Assessment/Full Analysis erzeugt den erwarteten zeitlich begrenzten Zugriff.
- [ ] Validation erzeugt genau den vorgesehenen Validation-Zugriff/Credit.
- [ ] Monitoring Monthly aktiviert Monitoring mit monatlicher Billing-Variante.
- [ ] Monitoring Annual aktiviert Monitoring mit jährlicher Billing-Variante.
- [ ] historischer `premium`-Planname allein aktiviert **kein** Monitoring.
- [ ] bestehende historische Rechte gehen beim aktuellen Codepfad nicht verloren.

PASS-Kriterium: UI/API/License Snapshot zeigen dieselbe kanonische Produktwahrheit.

## M03 — E-Mail-/Domain-Abnahme

- [ ] echte Einladung an Gmail empfangen.
- [ ] echte Einladung an Outlook/Microsoft empfangen.
- [ ] Password-Reset-Mail empfangen und Link einmal erfolgreich verwenden.
- [ ] SPF für die verwendete Absenderdomain validieren.
- [ ] DKIM validieren.
- [ ] DMARC validieren.
- [ ] absichtlich ungültige Empfängeradresse testen und Provider-/Operator-Verhalten dokumentieren.
- [ ] `support@bcsentinel.com` von extern erreichbar und beantwortbar.

PASS-Kriterium: reale Pilotbenutzer können Invite und Reset zuverlässig empfangen; Domain-Authentifizierung ist sauber dokumentiert.

## M04 — Vollständige Pilot-Journey

Mit einem frischen Pilottenant:

- [ ] BC Extension installieren/öffnen.
- [ ] Consent/Setup konfigurieren.
- [ ] Tenant registrieren.
- [ ] Invite empfangen.
- [ ] Dashboard-Zugang aktivieren/Passwort setzen.
- [ ] Login durchführen.
- [ ] Data Health Score/Scan ausführen.
- [ ] Synchronisierung im Dashboard prüfen.
- [ ] Findings öffnen.
- [ ] Executive Report erzeugen.
- [ ] Validation/Monitoring-Zugriff gemäß Pilotkonfiguration prüfen.
- [ ] Tenant suspendieren und Zugriff verweigert sehen.
- [ ] Tenant reaktivieren und Zugriff wiederherstellen.

PASS-Kriterium: die Journey funktioniert ohne Daten- oder Tenant-Leak und ohne manuelle Datenbankkorrekturen.

## M05 — Customer UX / Visual Acceptance

Realtenant mit echten Scan-Daten:

- [ ] DE Desktop hell.
- [ ] DE Desktop dunkel.
- [ ] EN Desktop hell.
- [ ] EN Desktop dunkel.
- [ ] Tablet-Breite.
- [ ] Mobile-Breite.
- [ ] Loading-State.
- [ ] Empty-State.
- [ ] Locked-State.
- [ ] API-Fehler-State.
- [ ] Finding-Remediation/Correction in BC visuell und funktional.
- [ ] Executive PDF DE visuell prüfen.
- [ ] Executive PDF EN visuell prüfen.

PASS-Kriterium: keine abgeschnittenen Inhalte, Mojibake, falschen Claims, unverständlichen Locks oder kritischen Layoutfehler.

## M06 — Recovery / Rollback

Auf Pilot-/Staging-Infrastruktur, nicht auf produktiven Kundendaten:

- [ ] verwertbares PostgreSQL-Backup erzeugen.
- [ ] Restore in isolierter Umgebung durchführen.
- [ ] RPO dokumentieren.
- [ ] RTO messen und dokumentieren.
- [ ] BC-Sandbox Roll-forward/Rollback-Szenario mit 1.0.2.25 durchführen.
- [ ] Tenantbindung, Scans, Findings, Historie und Scheduler danach prüfen.

PASS-Kriterium: Wiederherstellung ist reproduzierbar und ohne Tenant-/Historienverlust.

## M07 — Staged Operational Soak

Nicht 50 Tenants auf einmal freischalten.

- [ ] Welle 1: 1 Tenant mindestens 24 h beobachten.
- [ ] Welle 2: bis 5 Tenants; keine P0/P1-Isolations-, Scan- oder Auth-Probleme.
- [ ] Welle 3: bis 10 Tenants; Betriebs-/Supportaufwand prüfen.
- [ ] Welle 4: bis 25 Tenants; Ressourcen/DB/Fehlerquote prüfen.
- [ ] Welle 5: bis 50 Tenants nur nach Review der vorherigen Welle.

Bei P0: Aufnahme neuer Tenants stoppen, Incident schließen, betroffene Gates wiederholen.

PASS-Kriterium: jede Welle wird explizit freigegeben; keine implizite SLA-Behauptung.

## M08 — Final Release Sign-off

Erst nach M01–M07:

- [ ] grünen CI-Build und `core-pilot-rc-build-manifest.json` sichern.
- [ ] APP-Datei und SHA-256 gegen Manifest prüfen.
- [ ] Known Limitations final lesen.
- [ ] öffentliche Pilot-/Trust-/Privacy-/Legal-Texte final lesen.
- [ ] finalen Pilot-RC-Commit dokumentieren.
- [ ] Pilotfreigabe mit Datum dokumentieren.

PASS-Kriterium: exakt ein nachvollziehbarer Pilot-RC ist freigegeben.

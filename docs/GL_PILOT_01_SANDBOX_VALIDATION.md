# GL-PILOT-01 – Sandbox Validation

Stand: 20. Juli 2026  
Umgebung: `BCSentinel-Pilot`, Business Central 28.3

## Vor GL-PILOT-01-FIX01 bestätigte Evidenz

- [x] Sandbox aktiv
- [x] Symbole geladen
- [x] Extension-Package erstellt
- [x] Publish erfolgreich
- [x] Extension installiert
- [x] Setup-Seite öffnet
- [x] Permission Set gesetzt
- [x] Backend erreichbar
- [x] externe HTTP-Anforderung freigegeben
- [x] Verbindungstest erfolgreich
- [ ] Registrierung – blockiert durch den damaligen globalen E-Mail-/Tenant-Konflikt

## Delta GL-PILOT-01-FIX01

Der Konflikt ist durch ein relationales DashboardUser/Tenant-Membership-Modell auf Code- und Migrationsebene behoben. ReleaseCloud Compile, API-/Dashboard-/Migrations-/Securitytests und PostgreSQL-Race-Test sind grün. Detail: `docs/GL_PILOT_01_FIX01_MULTI_TENANT_DASHBOARD_ACCESS.md`.

Noch in derselben Sandbox auszuführen:

- [ ] Backendbackup und Migration 0025
- [ ] Extension-Upgrade ohne Deinstallation
- [ ] gleiche E-Mail in zweitem Tenant erfolgreich registrieren
- [ ] spezifische Erfolgsmeldung; kein dauerhafter Busy-State
- [ ] mehrere Dashboards beim Login sichtbar
- [ ] Tenant-Wechsel und strikte Datenisolation
- [ ] Fremd-Tenant-Zugriff 403
- [ ] identische Wiederholung idempotent

Aktuelles Gate: **BLOCKED – Fix implementiert, erneuter Sandbox-CAT noch nicht ausgeführt.**

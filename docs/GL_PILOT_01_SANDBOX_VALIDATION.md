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

## Delta GL-PILOT-01-FIX03

Der erste kostenlose Scan scheiterte trotz gültigem Access Snapshot mit 409, weil die lokal erzeugte ID `RUN_20260720_000001` nicht tenantglobal eindeutig war, die Backend-Schlüssel aber global eindeutig sind. Zusätzlich blieb nach einer erwarteten Dashboard-Ablehnung der BC-Busy-Dialog sichtbar.

- [x] Root Cause auf Code-/Schlüsselebene bestätigt
- [x] global kollisionsfeste, lesbare BC-Run-ID implementiert
- [x] Client-Request-ID bleibt über Retry stabil
- [x] Same-Tenant-Pending-Orphan-Recovery streng abgesichert
- [x] Fremd-Tenant-/Fremd-Request-Adoption weiterhin 409
- [x] terminaler lokaler Reject-State mit `Finished At` und ohne Heartbeat
- [x] strukturierte DE-/EN-409-Meldungen
- [x] Dashboard-Access-Ablehnung beendet Action nach genau einer Meldung normal
- [x] Extension-Version 1.0.2.9 und ReleaseCloud Compile PASS
- [ ] fokussierte Backendtests und Gesamtsuite – BLOCKED durch lokales Docker-Nutzungslimit
- [ ] `CAT-PILOT-SCAN-START` – Post-Fix BLOCKED
- [ ] `CAT-PILOT-DASHBOARD-BUSY` – Post-Fix BLOCKED

Detail und Retest-Anleitung: `docs/GL_PILOT_01_FIX03_SCAN_START_RECOVERY.md`.

Aktuelles Gate bleibt **NO-GO**, bis Backendtests und beide realen BC-28.3-CATs PASS sind.

## Delta GL-PILOT-01-FIX04

Der erste reale Scan nach FIX03 wurde lokal vollständig abgeschlossen, verlor aber während eines langen synchronen Moduls seine Backend-Lease. Recovery rotierte wegen eines 15-Minuten-Heartbeat-Fensters das noch auf 20 Minuten ausgestellte Token. Folgeupdates und der finale Sync wurden korrekt als stale abgewiesen; BC führte jedoch weitere Calls aus und zeigte lokal widersprüchliche Completed-/Failed-Zustände.

- [x] gültige Lease ist bis zu ihrem Ablauf autoritativ
- [x] Defaultlease und Stale-Fenster auf vier Stunden, Hard Runtime auf sechs Stunden
- [x] Statusupdates verlängern unverändert Heartbeat und Lease
- [x] strukturierte Lease-Codes und DE-/EN-Meldungen
- [x] explizite Tenantprüfung vor Statusmutation
- [x] lokaler Scanstatus und Backend-Sync-Status getrennt
- [x] terminaler Lease-Konflikt stoppt weitere Statuscalls
- [x] lokale Findings bleiben bei Sync-Fehler erhalten
- [x] Extension 1.0.2.10; ReleaseCloud Compile PASS
- [x] fokussierte Backend-/Contract-Tests PASS
- [ ] vollständige Backend-Suite und Analyzer-Abschlusslauf
- [ ] autoritative Pilot-DB-Evidenz
- [ ] Post-Fix-CAT in BC 28.3

Detail: `docs/GL_PILOT_01_FIX04_WORKER_LEASE_STABILITY.md`.

Aktuelles Gate: **NO-GO bis vollständige Regression und realer Post-Fix-CAT PASS sind.**

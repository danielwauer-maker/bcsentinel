# BCSentinel Extension – Release Checklist

Stand: 16.07.2026  
Audit: GL-EXT-AUDIT-01  
Aktueller Gate-Status: **BLOCKED / NO-GO**

## Freigaberegel

Ein Release darf nur erzeugt oder verteilt werden, wenn alle `MUST`-Einträge belegt und keine P0-/releaseblockierende P1-Abweichung offen ist. Ein vorhandenes `.app`-Artefakt ersetzt keinen reproduzierbaren Build des freizugebenden Commits.

## A. Source und Manifest

- [ ] MUST: Releasecommit und Branch sind eindeutig, Worktree ist kontrolliert.
- [ ] MUST: `app.json` und Cloudprofil tragen dieselbe SemVer.
- [ ] MUST: endgültige App-ID, Name, Publisher, ID-Ranges und Runtime sind bestätigt.
- [ ] MUST: EULA, Privacy/Terms, Help/Support-URLs, Logo, unterstützte Sprachen und Target sind releasegerecht gesetzt.
- [x] Resource Exposure Policy deaktiviert Debugging, Download und Source Include.
- [ ] Keine Test-/Dev-URL oder `http://` kann im Produktionspaket verwendet werden.
- [ ] Hartkodierte gemeldete App-Version `0.4.0` ist entfernt.

## B. Build und Analyzer

- [x] `scripts/New-BCBuildWorkspace.ps1 -Profile ReleaseCloud` erfolgreich.
- [ ] MUST: Symbole aus der Ziel-BC-Version reproduzierbar bezogen.
- [ ] MUST: `alc.exe` kompiliert den aktuellen Releasecommit ohne Fehler/Warnungen.
- [ ] MUST: CodeCop grün.
- [ ] MUST: AppSourceCop grün.
- [ ] MUST: PerTenantExtensionCop grün.
- [ ] MUST: Analyzer-Log und Paket-Hash als CI-Artefakt archiviert.
- [ ] Paket signiert beziehungsweise AppSource-Upload technisch validiert.

Aktueller Befund: Der lokale AL-Compiler fehlt. Das vorhandene Paket 1.0.2.6 besitzt keine nachgewiesene Buildprovenienz für diesen Auditstand.

## C. Automatisierte Tests

- [x] Python-Compileall bestanden.
- [x] JSON-/XLF-Strukturprüfung bestanden.
- [ ] MUST: AL-Lokalisierungscheck grün; aktuell fehlgeschlagen.
- [ ] MUST: Backend-Pytest vollständig grün; aktuell 143 bestanden, 2 reproduzierbar fehlgeschlagen.
- [ ] MUST: `scripts/check_pricing_consistency.py` grün; aktuell Assessment-Fallback inkonsistent.
- [ ] MUST: AL-Test-App vorhanden und alle Tests grün.
- [ ] Credit-Concurrency-/Antwortverlust-/Idempotency-Tests grün.
- [ ] Registrierung Idempotency/Recovery grün.
- [ ] Lizenzablauf-/Finding-Access-Tests grün.
- [ ] Scheduler-DST-/Failure-/Replan-Tests grün.
- [ ] Install-/Upgrade-/Permission-Tests grün.

## D. Sicherheit und Datenschutz

- [ ] MUST: HTTPS-only und Produktionshost-Allowlist.
- [ ] MUST: stabile Tenant-/Environment-/Company-Bindung und Cross-Tenant-Negativtests.
- [ ] MUST: API-Token Rotation, Revocation und Recovery.
- [ ] MUST: lokale Premiumdaten werden nach Ablauf zuverlässig gesperrt.
- [ ] Secrets/Tokens werden in Logs, URLs und Fehlerdialogen redigiert.
- [ ] Dashboard-/Reporttokens sind kurzlebig und scope-/tenantgebunden.
- [x] Backend speichert API-Token gehasht; AL nutzt Isolated Storage.
- [ ] Retention und Löschung für Tenant, Scans, Findings, Events, Invites und Share-Links technisch erzwungen und dokumentiert.
- [ ] Datenschutzdokumentation stimmt mit `BC_EXTENSION_DATA_FLOW.md` und realen Payloads überein.
- [ ] Threat Model und Security-Sign-off dokumentiert.

## E. Funktionale Gates

- [ ] MUST: Registrierung ist idempotent; Portalinvite kann kundenseitig erneut gesendet werden.
- [ ] MUST: Creditverbrauch ist atomar und retry-sicher.
- [ ] MUST: jeder Scan endet in Completed/Failed/Cancelled/Partial; kein ewiges Running.
- [ ] MUST: manuelle/geplante Scans laufen asynchron und Fortschritt aktualisiert sich.
- [ ] MUST: Scheduler läuft ohne SUPER mit dokumentierter Serviceberechtigung.
- [ ] MUST: Currency-Werte werden fachlich korrekt konvertiert oder als EUR bezeichnet.
- [ ] MUST: Findings-/Drilldown-Zugriff folgt einem frischen Access Snapshot.
- [ ] Ausnahmen verlangen Grund und besitzen vollständigen Audittrail.
- [ ] Executive Report besteht HTML-/PDF-/Ablauf-/Manipulationstest.
- [ ] Scan-Historie und Reconcile/Delete sind konsistent.

## F. Installation und Upgrade

- [ ] MUST: Install-Codeunit initialisiert Setup idempotent.
- [ ] MUST: Upgrade-Codeunit und Version-Tags vorhanden.
- [ ] Frische Sandboxinstallation ohne SUPER-spezifischen Workaround bestanden.
- [ ] N-1 → Releasekandidat mit Setup, Secret, History, Exceptions und Scheduler bestanden.
- [ ] Deinstall/Reinstall-Auswirkung dokumentiert und geprüft.
- [ ] Roll-forward-/Recovery-Runbook erprobt; kein destruktives Rollbackversprechen.

## G. UX, Sprache und Support

- [ ] MUST: vollständiger EN-US- und DE-DE-CAT-Lauf bestanden.
- [ ] Keine harten kundensichtbaren Texte, Mojibake oder gemischte Statuswerte.
- [ ] Leere, Lade-, Fehler-, Ablauf- und No-Credit-Zustände verständlich.
- [ ] Role-Center-/Such-Einstieg und Assisted Setup auffindbar.
- [ ] Fehlerdialog zeigt sichere Request-/Run-ID und konkrete nächste Aktion.
- [ ] Support-Runbook für Registrierung, Token, Scan, Scheduler, Credit und Report erprobt.
- [ ] Monitoring/Alerts für API-Fehlerrate, hängende Runs, Mailfehler und Credit-Anomalien aktiv.

## H. Customer Acceptance und Freigabe

- [ ] MUST: CAT-01 bis CAT-23 ohne offenen P0/P1-Fehler bestanden.
- [ ] Product Owner bestätigt Produkt-/Creditvertrag.
- [ ] Security/Privacy bestätigt Datenfluss und Retention.
- [ ] BC Technical Owner bestätigt Build, Permissions, Install und Upgrade.
- [ ] Backend Owner bestätigt Migration, Tests und Betriebsmonitoring.
- [ ] Support Owner bestätigt Runbook und Eskalationsweg.
- [ ] Go-Live-Entscheidung mit Datum, Version, Commit, Paket-Hash und Unterzeichnern dokumentiert.

## Empfohlener Releaseablauf

1. P0-Fix-Sprints abschließen und Security-Review durchführen.
2. P1-Hardening abschließen; Produkt-/Credit-/Currency-Verträge einfrieren.
3. AL-Test-App und Backendregression vollständig grün machen.
4. Manifestversion einmal erhöhen und Releasebranch einfrieren.
5. CI baut aus sauberem Checkout, führt Compiler und drei Analyzer aus.
6. Paket in frischer Sandbox installieren; CAT-01 bis CAT-23 ausführen.
7. N-1-Upgrade in zweiter Sandbox und Last-/Paralleltest im Staging durchführen.
8. Datenschutz-, Support- und Betriebsfreigaben einholen.
9. Pilot mit internem/Design-Partner-Tenant, Feature Flag und täglichem Monitoring.
10. Nach Pilot-Retrospektive getrennte Entscheidung für Customer Go beziehungsweise AppSource treffen.

## Entscheidungsleiter

| Stufe | Minimale Voraussetzung |
|---|---|
| NO-GO | mindestens ein P0 offen oder Build/CAT nicht verifizierbar – aktueller Zustand |

## Gate-Delta GL-EXT-P0A (16. Juli 2026)

Die ursprüngliche Checkliste bleibt als Audit-Baseline erhalten. Nur P0A-betroffene Gates wurden neu bewertet:

- [x] Production HTTP wird in AL-Konfiguration, jedem AL-Request und am produktiven Backend-Eingang blockiert.
- [x] Dev-HTTP ist auf non-production plus exakte Loopback-Hosts begrenzt.
- [x] Registrierung ist an Entra Tenant, Environment und Company SystemId gebunden.
- [x] Identische, parallele und Timeout-Retry-Registrierung erzeugt keine Duplikate.
- [x] Portaluser wird nicht dupliziert; Invite-Resend ist explizit und authentisiert.
- [x] Dashboard-Token verlangt für gebundene Tenants den exakt registrierten Plattformkontext.
- [x] Reset besitzt Default Nein und erhält Tenant-ID, Token, Käufe und Historie.
- [x] Migration funktioniert frisch und von 0021 mit erhaltenem Legacy-Bestand.
- [x] AL ReleaseCloud Compile sowie CodeCop/PerTenantExtensionCop ohne Fehler.
- [ ] AppSourceCop grün: bestehende Manifest-/ID-Range-Gaps bleiben offen.
- [ ] Reproduzierbarer 10-Punkte-BC-Sandbox-CAT ausgeführt: Sandbox nicht verfügbar.
- [ ] Docker-Testimage gebaut: Docker Desktop Linux Engine war nicht gestartet.

P0A-Entscheidung: **P0-01 und P0-02 geschlossen; bereit für GL-EXT-P0B.** Produkt-Gate bleibt **BLOCKED / NO-GO**, bis die übrigen P0 und der Sandbox-CAT geschlossen sind.

## Gate-Delta GL-EXT-P0B (16. Juli 2026)

- [x] Assessment und Validation claimen genau einen passenden Credit.
- [x] Monitoring mit aktiver Laufzeit und Free Score erzeugen keine Creditbuchung.
- [x] Tenant + Client Request GUID ist persistenter Idempotency-Scope; Payload-Mismatch ergibt 409.
- [x] Scan, Runstatus, Creditclaim, Request und Ledger committen oder rollen gemeinsam zurück.
- [x] Parallele identische und unterschiedliche Starts sind mit echten Threads/separaten Sessions getestet.
- [x] AL speichert die GUID vor HTTP und verwendet sie für Pending-/Timeout-/Scheduler-Retry wieder.
- [x] Migration 0023 ist frisch und von 0022 mit Legacy-Bestand getestet.
- [x] P0B-Suite 12/12 und relevante Regression 76/76 bestanden.
- [x] AL ReleaseCloud Compile sowie CodeCop/PerTenantExtensionCop ohne Fehler.
- [ ] PostgreSQL-Concurrency-/Restart-Test im Staging: Docker Engine lokal nicht verfügbar.
- [ ] Zehn BC-Sandbox-CATs: vorbereitet, Sandbox nicht verfügbar.
- [ ] AppSourceCop: bekannte EULA-/Logo-/Help-URL-/ID-Range-Gaps.

P0B-Entscheidung: **P0-03 geschlossen; bereit für GL-EXT-P0C.** Produkt-Gate bleibt **NO-GO** wegen P0-04 und P0-05.

## Gate-Delta GL-EXT-P0C (16. Juli 2026)

- [x] kanonische Statusübergänge werden serverseitig validiert; Completion ohne Pflichtresultat ist blockiert.
- [x] jeder neue nichtterminale Run hat Queuefrist oder aktive Lease/Heartbeat.
- [x] Claim ist atomar; parallele Worker und Late Writer sind getestet.
- [x] stale Queued/Running, Leaseverlust, Max Attempts und Backoff sind abgedeckt.
- [x] Startup- und periodische Batch-Recovery sind implementiert und idempotent.
- [x] Recovery verwendet denselben Run, denselben Startrequest und keinen neuen Credit/Ledgerposten.
- [x] Findings und Module sind runbezogen eindeutig; Partial Result wird nicht Completed.
- [x] AL persistiert Exceptions terminal und setzt lokalen Completed-Status erst nach Backend-Sync.
- [x] AL ReleaseCloud Compile sowie CodeCop/PerTenantExtensionCop ohne Fehler.
- [x] Migration 0024 frisch und von 0023 mit historischen Running-/Completed-Runs getestet.
- [ ] finaler PostgreSQL-Mehrinstanz-/Restart-Test: lokale Docker-/PostgreSQL-Umgebung nicht verfügbar.
- [ ] zwölf BC-Sandbox-CATs: vorbereitet, Sandbox nicht verfügbar.
- [ ] AppSourceCop: bestehende EULA-/Logo-/Help-/ID-Range-Fehler.
- [ ] P0-05 Findings-Zugriffsschutz geschlossen.

P0C-Entscheidung: **P0-04 geschlossen; bereit für GL-EXT-P0D.** Produkt-Gate bleibt **NO-GO**, bis P0-05 und die externen Releasegates bestanden sind.
| CONDITIONAL GO | keine P0; nur zeitlich begrenzte, akzeptierte P1 außerhalb des Pilotumfangs |
| PILOT GO | P0/P1 im Pilotumfang geschlossen; Build, Upgrade und CAT grün; enges Monitoring |
| CUSTOMER GO | vollständige Betriebs-, Support-, Security- und Upgradeevidenz |
| APPSOURCE READY | Customer Go plus AppSourceCop/Submission/Legal/Marketing vollständig |

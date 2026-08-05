# BCSentinel Operatorhandbuch

**Produktstand:** 1.0.2.20  
**Zielgruppe:** Betreiber eines betreuten Pilotbetriebs mit bis zu zehn Kunden  
**Status:** Pilotfassung – reale Kontaktdaten, Infrastrukturpfade und Screenshots vor Kunde 1 ergänzen

## 1. Betriebsmodell

BCSentinel wird während der Pilotphase kontrolliert und gestaffelt betrieben. Neue Kunden werden nicht gleichzeitig, sondern in Wellen aufgenommen. Jeder Tenant besitzt eine eindeutige Kombination aus Tenant, Environment, Company und Membership.

### Verantwortlichkeiten

- Produkt-/Technikverantwortung: Daniel
- Ersatzkontakt: vor Kunde 1 festlegen
- Recht/Datenschutz: Daniel plus externe Prüfung
- Support: dokumentierter Eingangskanal mit nachvollziehbarer Ticket- oder Vorgangsnummer

## 2. Täglicher Systemcheck

Der Operator prüft mindestens einmal pro Werktag:

1. API-Readiness ist grün.
2. PostgreSQL ist erreichbar.
3. Worker und Scheduler sind bereit.
4. Keine dauerhaft laufenden Scans ohne aktuellen Heartbeat.
5. Keine unerwartet alte Queue oder abgelaufene Lease.
6. Keine wiederholten Scan-, Recovery- oder SMTP-Fehler.
7. Datenträgerauslastung unter der Warnschwelle.
8. Letztes Backup innerhalb des vereinbarten RPO.
9. TLS-Zertifikate nicht im Warn- oder Alarmfenster.
10. Keine Container-Restartschleife.

Die automatisierten Schwellenwerte und Runbook-Zuordnungen sind im P0-06-Audit dokumentiert.

## 3. Onboarding

Vor der Freischaltung müssen vorliegen:

- Pilotvereinbarung und gegebenenfalls AVV,
- Kundenhauptkontakt und technischer Kontakt,
- Tenant, Environment, Company SystemId und BC-Version,
- Installationsfenster und Rückfallplan,
- freigegebenes APP-Artefakt mit SHA-256,
- Produkt, Entitlement und Laufzeit,
- Supportkanal und Reaktionszeiten.

Ablauf:

1. Extension installieren oder aktualisieren.
2. Setup und Registrierung durchführen.
3. Tenant-/Company-Zuordnung prüfen.
4. Produkt und Entitlement zuweisen.
5. Free- oder Validation-Scan durchführen.
6. Historie und Findings prüfen.
7. Dashboardbenutzer einladen.
8. Login und Tenantzuordnung bestätigen.
9. HTML- und PDF-Report öffnen.
10. Monitoring aktivieren und nächsten Lauf dokumentieren.
11. Known Limitations erläutern.
12. Pilot-Abnahmeprotokoll abschließen.

## 4. Freischaltung und Credits

Sensible Adminaktionen müssen nachvollziehbar dokumentiert werden. Für manuelle Produkt- oder Creditzuweisungen gilt während des Piloten:

- eindeutiger Tenantbezug,
- Anlass und Laufzeit dokumentieren,
- keine stillen Änderungen,
- nach Möglichkeit Vier-Augen-Prinzip,
- Reconciliation gegen Rechnung oder Pilotvereinbarung.

## 5. Scan- und Monitoringbetrieb

### Sollzustand

- Scan wechselt kontrolliert von `queued` zu `running` und anschließend zu einem finalen Status.
- Jeder erfolgreiche Lauf erzeugt genau einen Historieneintrag.
- Heartbeat und Lease bleiben aktuell.
- Credits werden höchstens einmal verbraucht.
- Findings werden nicht doppelt erzeugt.

### Auffälligkeiten

- Scan länger als vereinbart in `running`: Runbook `RB-SCAN-02` beziehungsweise Recovery prüfen.
- Mehrere Scanfehler in kurzer Zeit: P0-Alarm und `RB-SCAN-01`.
- Scheduler nicht bereit: `RB-SCHED-01`.
- Queue älter als Schwellenwert: `RB-QUEUE-01`.

## 6. Incidentablauf

1. Eingang des Alarms bestätigen.
2. Schweregrad P0/P1/P2 bestimmen.
3. Betroffene Tenants und Funktionen eingrenzen.
4. Änderungen und Zeitpunkte protokollieren.
5. Passendes Runbook ausführen.
6. Kundenauswirkung bewerten.
7. Dienst wiederherstellen oder Rollback durchführen.
8. Readiness- und Produkt-Smoke-Tests ausführen.
9. Betroffene Kunden informieren.
10. Ursache, Maßnahmen und Prävention dokumentieren.

## 7. Backup und Restore

Die CI-seitige Backup-/Restore-Prüfung ist abgeschlossen. Für den realen Betrieb gilt zusätzlich:

- RPO und RTO schriftlich festlegen,
- Backupzeitpunkt und Prüfsumme dokumentieren,
- Restore ausschließlich in eine getrennte Zielumgebung,
- niemals ungeprüft das laufende System überschreiben,
- nach Restore Revision, Tabellen, Zeilenanzahlen und Kernfunktionen prüfen,
- gemessene Restorezeit dokumentieren.

## 8. Rollback

Vor jedem produktionsrelevanten Deployment müssen bekannt sein:

- vorherige freigegebene Backend-Version,
- zugehörige Datenbankrevision,
- erlaubte Downgrade-Grenzen,
- Konfigurationsänderungen,
- Smoke-Test nach Rollback.

Ein Rollback ist erst abgeschlossen, wenn API-Readiness, Login, Tenant-Isolation, Scan, Findings und Report geprüft wurden.

## 9. SMTP-Ausfall

Bei fehlgeschlagener Einladung:

1. `invite_mail_status` und Fehlertext prüfen.
2. SMTP-Konfiguration, TLS und Zugangsdaten prüfen.
3. Absenderdomain sowie SPF/DKIM/DMARC prüfen.
4. Keine mehrfachen Einladungen ohne Statuskontrolle senden.
5. Kunden über manuellen Ersatzprozess informieren.
6. Wiederholte Fehler als Operatoralarm behandeln.

## 10. Offboarding

- Monitoring deaktivieren.
- Offene Jobs kontrolliert beenden.
- Entitlement und Membership entziehen.
- Offene Einladungen ungültig machen.
- Datenexport oder Löschung vertragsgemäß ausführen.
- Deinstallation erst nach Datenerhalt-/Löschentscheidung.
- Abschlussfeedback und offene Punkte dokumentieren.

## 11. Vor Kunde 1 zu ergänzen

- reale Kontakt- und Eskalationsdaten,
- Hosting-/Logpfade,
- Backup-Speicherort,
- produktive SMTP-Konfiguration,
- Wartungsfenster,
- Screenshots der Operatoransichten,
- unterschriebene Freigabe des Betriebsmodells.

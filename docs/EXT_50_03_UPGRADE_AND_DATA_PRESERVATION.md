# EXT-50-03 – Upgrade und Datenbestandserhalt

## Ziel

Nachweis, dass eine bestehende BCSentinel-Installation von Version 1.0.2.16 auf 1.0.2.20 aktualisiert werden kann, ohne Setup, Registrierung, Historie, Findings, Scheduler-Konfiguration oder bestehende lokale Daten zu verlieren.

## Verbindliche Baseline

- Ausgangsversion: 1.0.2.16
- Zielversion: 1.0.2.20
- Zielplattform: Business Central SaaS Sandbox
- Backend: DEV (`https://dev-api.bcsentinel.com`)
- Ausgangszustand: bereits registrierter Mandant mit mindestens einem abgeschlossenen Scan

Die Ausgangsversion 1.0.2.16 wird verwendet, weil sie bereits praktisch installiert und als frühere produktnahe Extension-Version getestet wurde. Eine andere Ausgangsversion darf nur ergänzend getestet werden.

## Automatische Vorabprüfungen

1. `bc-extension/app.json` enthält Zielversion 1.0.2.20.
2. App-ID, Name und Publisher bleiben unverändert.
3. Plattform, Application, Runtime und Objektbereich entsprechen der freigegebenen Baseline.
4. Der Evidence-Status darf vor dem realen BC-Runtime-Test nicht auf PASS gesetzt werden.
5. Alle Pflichtnachweise sind im Evidence-Dokument enthalten.

## Manueller Runtime-Test

### A. Ausgangszustand 1.0.2.16 dokumentieren

Vor dem Upgrade Screenshots und Werte sichern:

- installierte Extension-Version 1.0.2.16
- Registrierungsstatus
- API-URL
- aktueller Produktplan und Zugriffsfristen
- letzter Data Health Score
- Anzahl Einträge in der Scan-Historie
- Run-ID des letzten Scans
- Scheduler aktiv/inaktiv
- Häufigkeit, Uhrzeit und nächster geplanter Scan
- Job-Queue-Eintrag vorhanden
- Zugriff auf Findings, Dashboard und Report

### B. Upgrade durchführen

1. Version 1.0.2.20 als `.app` in der Extension-Verwaltung hochladen.
2. Option für Upgrade/Schema-Synchronisierung verwenden, nicht deinstallieren.
3. Keine Tabellen- oder Extension-Daten löschen.
4. Installation vollständig abschließen lassen.
5. Installierte Version kontrollieren.

### C. Datenbestand nach Upgrade prüfen

Pflichtprüfungen:

- Extension zeigt 1.0.2.20
- Setup-Seite öffnet fehlerfrei
- Registrierungsstatus bleibt `Registriert`
- API-URL bleibt erhalten
- Produktzugriff bleibt erhalten oder wird nach „Produktzugriff aktualisieren“ korrekt erneut geladen
- vorhandene Scan-Historie ist vollständig erhalten
- vorhandene Run-IDs bleiben unverändert
- letzter Score und letzte Bewertung bleiben erhalten
- Findings des letzten Scans sind weiterhin sichtbar
- letzter HTML- und PDF-Report öffnen
- Dashboard öffnet
- Scheduler-Konfiguration bleibt erhalten
- genau ein BCSentinel-Job-Queue-Eintrag ist vorhanden
- kein doppelter Job-Queue-Eintrag
- keine Schema-, Installations- oder Berechtigungsfehler

### D. Funktionsprüfung nach Upgrade

1. Produktzugriff aktualisieren.
2. Manuellen Monitoring-Scan starten.
3. Abschluss und neuen Historieneintrag prüfen.
4. Scheduler auf wenige Minuten in die Zukunft setzen.
5. Geplanten Scan abwarten.
6. Neuen Historieneintrag und nächsten geplanten Scan prüfen.
7. Prüfen, dass keine Dubletten und keine doppelte Creditbuchung entstanden sind.

## Technisches Problem: Registrierung meldet „Dienst nicht erreichbar“

### Symptom

Nach einer frischen Installation kann die BCSentinel-Registrierung mit einer Meldung scheitern, dass der Dienst nicht erreichbar sei, obwohl die konfigurierte API-URL im Browser erreichbar ist.

### Beobachteter Fall

- Business Central SaaS Sandbox neu erstellt
- BCSentinel 1.0.2.16 als PTE erfolgreich installiert
- API-Basis-URL `https://dev-api.bcsentinel.com` korrekt eingetragen
- Registrierung schlug wiederholt fehl
- Backend-Logs zeigten zum Registrierungszeitpunkt keinen eingehenden Registrierungs-Request
- In den Business-Central-Erweiterungseinstellungen war `HttpClient-Anfragen zulassen` deaktiviert
- Nach Aktivierung der Option konnte die Registrierung erfolgreich durchgeführt werden

### Ursache

Business Central blockiert externe HTTP-Aufrufe einer Extension, wenn für die betreffende PTE `HttpClient-Anfragen zulassen` nicht aktiviert ist. In diesem Zustand erreicht der Registrierungsrequest das BCSentinel-Backend nicht. Die Fehlermeldung in der Extension kann deshalb wie ein Backend-/Netzwerkfehler wirken, obwohl die eigentliche Ursache eine lokale Erweiterungseinstellung in Business Central ist.

### Lösung für Administratoren

1. In Business Central `Erweiterungsverwaltung` öffnen.
2. BCSentinel auswählen.
3. `Erweiterungseinstellungen` öffnen.
4. `HttpClient-Anfragen zulassen` aktivieren.
5. Einstellung speichern.
6. BCSentinel-Einrichtung erneut öffnen.
7. Registrierung erneut ausführen.

### Support-Diagnose

Wenn die Registrierung weiterhin scheitert:

1. API-Basis-URL prüfen.
2. `HttpClient-Anfragen zulassen` prüfen.
3. Registrierung erneut auslösen und genaue Uhrzeit notieren.
4. Backend-Logs zu diesem Zeitpunkt prüfen.
5. Fehlt dort der Registrierungsrequest vollständig, liegt das Problem vor dem Backend-Aufruf.
6. Ist ein Request sichtbar, HTTP-Status und Backendfehler analysieren.

### Dokumentationshinweis für Go-Live

Dieser Punkt muss in die Kunden-/Administrator-Dokumentation unter `Technische Probleme / Registrierung` aufgenommen werden. Besonders bei frisch hochgeladenen Per-Tenant-Extensions sollte `HttpClient-Anfragen zulassen` als verpflichtender Installations-Check aufgeführt werden.

## Abnahmekriterien

EXT-50-03 ist PASS, wenn:

- das Upgrade 1.0.2.16 → 1.0.2.20 ohne Deinstallation gelingt,
- alle vorhandenen Daten und Konfigurationen erhalten bleiben,
- manueller und geplanter Monitoring-Scan nach dem Upgrade erfolgreich sind,
- keine doppelten Scheduler-/Job-Queue-Einträge entstehen,
- alle CI- und Contract-Gates grün sind.

## Stop-Kriterien

Sofort stoppen und nicht als PASS bewerten bei:

- notwendiger Deinstallation,
- Datenverlust,
- Verlust der Registrierung,
- Verlust oder Duplizierung der Scan-Historie,
- doppeltem Job-Queue-Eintrag,
- Schema- oder Upgradefehler,
- fehlgeschlagenem Scan nach Upgrade.

## Verschobene Prüfung

Der vollständige Rollen- und Berechtigungstest ohne SUPER bleibt Bestandteil von EXT-50-04.

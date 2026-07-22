# GL-01F-FIX02A – Permanent Free Result Access

## Analyse vor der Implementierung

### Ursache der falschen Laufzeit

`product_license_service._free_access_until()` ermittelt den autoritativen Abschlusszeitpunkt eines technisch eindeutig gebundenen kostenlosen Data Health Score und addiert anschließend `ONE_TIME_ACCESS_DAYS` (7 Tage). `build_product_access_snapshot()` behandelt dieses berechnete Datum danach gemeinsam mit Paid- und Monitoring-Zeiträumen als `protected_access_until`. Damit sind die drei Free-Ergebnisrechte zwar technisch getrennt von Premium-Aktionen, werden aber fälschlich zeitlich befristet.

Die Sieben-Tage-Konstante ist für Full Analysis und Validation Check weiterhin fachlich korrekt. Nur ihre Wiederverwendung für den kostenlosen Ergebniszugriff ist falsch.

### Autoritativer Free-Nachweis

Der vorhandene Query ist bereits ausreichend streng und bleibt die einzige Quelle des Grants:

- Run-Status `completed` oder `completed_with_warnings`
- `completed_at_utc` gesetzt
- `result_persisted_at_utc` gesetzt
- zugehöriger `ScanStartRequest` gehört zum Tenant
- `resolved_product_code = data_health_score`
- `free_scan_slot = data_health_score`
- persistierter `Scan` gehört zum selben Tenant

Queued, Running, Failed, Cancelled, Expired und unvollständig persistierte Runs erfüllen diese Bedingungen nicht.

### Architekturentscheidung

1. Der erfolgreiche persistierte Free Scan wird bei jedem Snapshot als dauerhafter boolescher Grant abgeleitet.
2. `dashboard_access`, `issues_access` und `report_access` werden dadurch gewährt und erhalten `valid_until_utc = null`.
3. Das bestehende Snapshot-Modell erhält im abwärtskompatiblen `product_access`-Objekt den expliziten Status `free_access_permanent`.
4. Legacy-Zeitfelder für Dashboard, Findings, Report und `free_access_until` bleiben bei dauerhaftem Free-Zugriff leer. Es wird kein Sentinel- oder Fernzukunftsdatum eingeführt.
5. `product_access`, Premium-Aktionen, Record Details, Full Report, Monitoring und Subscription bleiben ausschließlich von ihren bestehenden Paid-/Monitoring-Nachweisen abhängig.
6. Besteht gleichzeitig Paid- oder Monitoring-Zugriff, bleiben dessen eigene Zeitfelder unverändert. Die drei Ergebnis-Capabilities bleiben wegen des Free-Grants zeitlich unbefristet; nach Paid-Ablauf bleiben nur die Free-Rechte erhalten.
7. Business Central entscheidet weiterhin über die Capability-Booleans. Leere Ergebnis-Ablaufdaten werden bei `free_access_permanent = true` ausschließlich in der Anzeige als `Unlimited`/`Unbegrenzt` dargestellt.

### Geprüfte Verbraucher

- `access_control_service.py` verwendet getrennte Capabilities für Dashboard, Findings, Report, Produkt und Monitoring. Ein `null`-Ablauf ist bereits ein gültiger dauerhafter Capability-Zustand.
- Analytics-, Dashboard- und Report-Routen schützen Zugriffe über diese Capabilities. Premium-Inhalte bleiben zusätzlich über `premium_active`, `can_view_actions`, `can_view_record_details` und `executive_report_full` gesperrt.
- Billing und Checkout verwenden weiterhin Paid-Produktcodes und werden vom Free-Grant nicht erweitert.
- `DH Access Guard` wertet die Capability-Booleans aus und benötigt kein Ablaufdatum für eine positive Entscheidung.
- `DH API Client` mappt die drei Capabilities bereits getrennt; ergänzt werden nur der explizite Permanent-Status und die sichere Unterdrückung irreführender Fallback-Daten.
- `DH Setup` benötigt keine neuen Tabellenfelder. Lokalisierte Anzeigeprozeduren können die vorhandenen Booleans und Zeitfelder verwenden.

## Auswirkungen

- Keine Datenbankmigration und keine globale Datenmutation.
- Lazy Repair ist idempotent und unabhängig vom Deployment-Zeitpunkt.
- Keine Änderung an Scan Engine, Regeln, Scores, Findings, Credits, Preisen, Registrierung, Monitoring oder Scheduler.
- Keine Änderung bestehender API-Feldtypen oder Capability-Namen.

## Implementierung und Prüfergebnisse

### Implementierung

- `_free_access_until()` wurde durch `_has_permanent_free_result_access()` ersetzt. Der bestehende strenge Query liefert jetzt ausschließlich einen booleschen fachlichen Grant.
- `free_access_permanent` wird im bestehenden flexiblen `product_access`-Objekt ausgegeben.
- Dashboard-, Findings- und Report-Zugriff werden bei diesem Grant unabhängig vom Scan-Alter gewährt; ihre kombinierten Ablaufzeitfelder und `free_access_until` bleiben `null`.
- Die autoritativen Capabilities `dashboard_access`, `issues_access` und `report_access` sind gewährt und besitzen `valid_until_utc = null`.
- `product_access`, `monitoring_access`, `subscription_active` und `scan_start_access` behalten ihre bestehende zeit- und produktgebundene Auswertung.
- Full Analysis, Empfehlungen, Aktionen, Datensatzdetails, Premium Analytics und `executive_report_full` werden durch den Free-Grant nicht aktiviert.
- `DH API Client` erkennt den expliziten Permanent-Status und entfernt nur die drei irreführenden Ergebnis-Ablaufanzeigen. Produkt- und Monitoring-Zeitfelder bleiben erhalten.
- Die Setup-Seite zeigt die drei Ergebnisrechte über lokalisierte Anzeigeprozeduren als `Unlimited`/`Unbegrenzt`, als vorhandenes Zeitdatum oder als `Not available`/`Nicht verfügbar`.

### Paid- und Monitoring-Fallback

Während Paid oder Monitoring aktiv ist, bleiben alle höherwertigen Capabilities und deren eigene Zeitfelder unverändert. Nach deren Ablauf werden Premium-Aktionen, Record Details, Deep-Scan-/Scheduler- und Monitoring-Rechte gesperrt. Der permanente Free-Grant für Dashboard, Findings und Free Report bleibt erhalten.

### Historische Mandanten und Idempotenz

Jeder Snapshot prüft den ursprünglichen erfolgreichen, persistierten und eindeutig gebundenen Free Scan. Es wird weder ein Grant-Datensatz geschrieben noch ein Datum verlängert. Wiederholte Snapshot-Aufrufe liefern daher denselben Zustand und verändern keine Daten.

### Tests und Qualitätsgates

- FIX02A-Suite: 15 Tests bestanden.
- Lokalisierungs- und FIX02A-Kombination: 22 Tests bestanden.
- Access-/Licensing-/Billing-/Report-/Admin-/Analytics-Regression: nach Anpassung der fachlich überholten Sieben-Tage-Erwartung vollständig bestanden.
- Vollständige Backend-Suite: 344 bestanden, 7 übersprungen; nur bestehende Deprecation-Warnungen.
- de-DE-XLF: alle sechs neuen Caption-/ToolTip-IDs vorhanden, `Unlimited` ist weiterhin als `Unbegrenzt` übersetzt.
- AL Source Uniqueness Guard: bestanden, 89 Objektdeklarationen und ein kanonischer Source Tree.
- AL-Compiler 17.0.34.45391: 85 Dateien, 0 Fehler, 0 Warnungen.
- `git diff --check`: wird im finalen Gate ausgeführt.

### Migration

Keine Migration. Es gibt keine neue Tabelle, kein neues Tabellenfeld, keinen Backfill und keine globale Datenmutation.

### Manuelles Abnahme-Gate

Die lokale Umgebung enthält keine verbundene Business-Central-Sandbox. Nach Deployment bleibt deshalb die im Masterprompt beschriebene manuelle Prüfung eines historischen Mandanten erforderlich: Produktzugriff zweimal aktualisieren, Seite neu öffnen, Free-Dashboard, Free-Findings und Free-Report öffnen und gleichzeitig die Sperre aller Premium-/Monitoring-Funktionen bestätigen.

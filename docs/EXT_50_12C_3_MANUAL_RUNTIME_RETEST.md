# EXT-50-12C.3 – manueller BC27-SaaS-Retest

Diese Anleitung erteilt keine LARGE-Freigabe. Zuerst die Fresh-/Upgrade-CI des Repair-PR #41 prüfen. Die bestehende Company BCS-PERF-DEV und deren 20.000 Generator-Datensätze bleiben vollständig unverändert.

Nachweis für Implementierung `44c9a4b8b3b2e003926f579fbde3c5098eb66c81`:
[BC-CI 35313449737](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35313449737)
ist für Neuinstallation und Upgrade grün, jeweils **3 PASS / 0 FAIL / 0 SKIP**.
Der abschließende Dokumentationscommit ändert diesen Implementierungsstand nicht.
Die in dieser CI geprüften Produkt-/QA-Apps liegen lokal unter
`.build/ci-al-44c9a4b/bc-al-compile-output/`.
Dateinamen und SHA256 stehen im [Sprintnachweis](EXT_50_12C_3_LOSSLESS_FINDING_IDENTITY.md).
Backend-CI enthält weiterhin ausschließlich den dokumentierten Billing-Baseline-FAIL;
PostgreSQL- und Migrationsprüfungen sind grün. Ein echter SaaS-Retest wurde noch nicht ausgeführt.

1. Eine **separate BC27-SaaS-Sandbox** mit Company **BCS-FINDING-QA** verwenden. Nicht über die bestehende DEV-Umgebung installieren: Dieser gestapelte Repair enthält die offene PR39-Recovery-Funktion noch nicht. Ein Betreiber stellt dort zuerst den Kandidaten-Backendstand inklusive Alembic `0029_finding_identity` bereit. Dies ist ein zukünftiger manueller QA-Schritt; durch Codex wurde nichts deployed.
2. Produkt-App **1.0.2.22**, danach **BCSentinel Finding Identity Tests 1.0.0.0** installieren. Normale BCSentinel-Berechtigungen für Einrichtung/Scan verwenden, zusätzlich **BCS FINDING QA** für den Export; keine SUPER-Abhängigkeit. Company regulär registrieren und Verbindung prüfen. Keine Tokens weitergeben.
3. Den Check **CUSTOMERS_DUPLICATE_NAME_POST_CITY** aktivieren. Fünf kleine, valide Debitoren nur in dieser neuen QA-Company anlegen: zwei mit Name `QA Group A` und identischer gültiger, nicht leerer PLZ/Stadt; drei mit Name `QA Group B` und ebenfalls gruppenintern identischer gültiger, nicht leerer PLZ/Stadt. Eindeutige Debitorennummern und eindeutige gültige E-Mails verwenden. Normale Buchungs-/Validierungsregeln beibehalten. Keine vorhandenen Datensätze dürfen die beiden Namen/Adresskombinationen teilen.
4. Einen normalen berechtigten BCSentinel-Scan ausführen. Auf **Completed / Synchronized** warten. Für den genannten Check müssen genau zwei Finding-Zeilen mit Counts **2 und 3**, unterschiedlichen `finding_id` und `group_key` bestehen. Bei unveränderten Backend-Standardparametern entspricht das **100 EUR und 150 EUR**, insgesamt **250 EUR** für diesen Check (25/60 × 0,25 × 12 × 40 EUR je Treffer). Konfigurierte abweichende Impactparameter dokumentieren, nicht ändern.
5. Alt+Q → **BCSentinel Finding-QA-Nachweis** (EN: BCSentinel Finding QA Evidence). Den abgeschlossenen Run auswählen → **Gruppennachweis herunterladen** (EN: Download group evidence). Datei `BCSentinel-Finding-QA.json` sichern. Der Export liest nur und startet weder Scan noch Generator noch Cleanup.
6. Prüfen: zwei Zielgruppen, fünf Prüftreffer für diesen Check; Gesamtimpact des Runs entspricht der Summe aller exportierten Zeilenimpacts. Andere Checks erzeugen zusätzliche Prüftreffer – deshalb nicht pauschal fünf für den gesamten Run erwarten. In berechtigtem Full-Zugriff müssen beide Gruppen auch im Dashboard und den Aktionen erscheinen; Free bleibt aggregiert. Betreiberseitig die gespeicherten Backend-Gruppen für genau diesen Run read-only gegenprüfen und ohne Secrets bereitstellen.
7. Identische/reihenfolgegeänderte Retries sind automatisiert geprüft. Ein manueller Retry-Nachweis darf nur eine vorhandene unterstützte Synchronisationswiederholung nach einem tatsächlichen vorübergehenden Sync-Fehler nutzen. Keine Statusfelder oder Tabellen manipulieren. Falls das nicht möglich ist: **manueller Retry NICHT AUSGEFÜHRT** dokumentieren. Ein neuer Scan ist kein Retry.
8. JSON, Screenshot der beiden Gruppen und berechtigte Backend-Evidence zur Auswertung bereitstellen. Erst danach SaaS-Runtime-PASS beurteilen. LARGE bleibt bis zu den weiteren Recovery-/Cleanup-/Berechtigungs-Gates blockiert.

# FULL-SCOPE-01 – Read-only Audit von Free-/Full-Scope und Finding-Differenzen

Stand: 2026-11-20
Basis: `origin/staging` nach Integration PR #221 (`8c91473`)
Scan im Untersuchungsauftrag: `RUN_20261116_000001_8870C7F3D8814DD1B1EE109EE7D38`
## Ergebnis vor dem DEV-Audit

Der Repository-Code belegt eine unterschiedliche Bewertungsgrundlage:

* Der Free Health Report übernimmt alle `ScanIssueRecord`-Zeilen des Scans. Die automatische Scope-Erkennung wird dort nicht als Finding-Filter verwendet (`backend/app/services/free_health_report_service.py:163-166`). Der Free-Score kommt aus `Scan.data_score` (`:199`), und das Impact-Band summiert die Impact-Werte aller Findings (`:200-202`).
* Der Full-Report lädt die zuletzt bestätigte Scope-Version und filtert Findings gegen die ursprüngliche Kategorie (`backend/app/services/executive_report_v2_service.py:156-176`). Nicht unterstützte oder nicht im bestätigten Scope enthaltene Kategorien werden ausgeschlossen. Danach werden Anzahl, betroffene Datensätze, Bereichs-Impact, Gesamt-Impact und potenzielle Einsparung aus den verbleibenden Findings neu berechnet (`:184-237`, `:253-270`).
* Der Full-v6-Renderer prüft diese Konsistenz erneut: bestätigter Scope, Score, Finding-Anzahl, eindeutige Codes, Prioritäten und Impact-Reconciliation müssen zusammenpassen (`backend/app/services/full_report_render_service.py:51-84`, `:159-170`).

Damit ist `95 → 79` durch den Code grundsätzlich erklärbar: 95 vollständige Free-Zeilen können auf 79 bestätigte Full-Scope-Zeilen reduziert werden. Welche 16 konkreten Codes betroffen sind, ist ohne DEV-Abfrage nicht bewiesen.

## Automatische Modulerkennung

Die Scope-Erfassung wird beim erfolgreichen v2-Scan-Sync in derselben Transaktion vorbereitet (`backend/app/routers/scans.py:955-961`). `get_or_create_auto_scope()` verwendet diese Scan-Profilfelder (`assessment_scope_service.py:64-79`):

| Modul | Aktiv-Signal | Ergebnis ohne Signal |
|---|---|---|
| System | immer Core-/Setup-Bereich | `active` |
| Finance | `gl_entries_count > 0` | `not_detected` |
| Sales | Kunden-, Kundenledger-, Verkaufsheader- oder Verkaufszeilen > 0 | `not_detected` |
| Purchasing | Lieferanten-, Lieferantenledger-, Einkaufsheader- oder Einkaufszeilen > 0 | `not_detected` |
| Inventory | Artikel-, Artikelledger-, Wert- oder Lagerposten > 0 | `not_detected` |
| Manufacturing, Service, Jobs, HR | kein zuverlässiges Profil-Signal vorhanden | `unknown` |

Bei mindestens einem Profilsignal wird `active` automatisch in den Score aufgenommen; `not_detected` und `unknown` werden nicht aufgenommen (`assessment_scope_service.py:197-225`). Bei einem vollständig signal-losen Legacy-Profil greift der Kompatibilitätsmodus: `enabled_modules` wird ausgewertet; eine leere Liste fällt aus Kompatibilitätsgründen auf alle Standardmodule zurück (`:174-203`). Dieser Legacy-Fall muss im DEV-Audit separat ausgewiesen werden.

`active`, `not_detected` und `unknown` sind keine nachträglichen Finding-Klassifikationen, sondern Zustände der automatisch gespeicherten Modulzeilen mit Erkennungsgrund, Konfidenz und Modulscore.

## Kundenbestätigung des Full-Scopes

`confirm_scope()` akzeptiert ausschließlich `include`, `exclude` und `inherit`; unbekannte Module/Werte sowie ein Ausschluss von `system` werden abgewiesen (`assessment_scope_service.py:234-244`). Für jede Standardmodulzeile gilt:

* `include`: immer in den bestätigten Score aufnehmen.
* `exclude`: nicht aufnehmen.
* `inherit`: den automatisch erkannten Include-Zustand übernehmen.
* `system`: wird unabhängig von der Nutzereingabe als `include` gespeichert.

Die bestätigte Version erhält `state=confirmed`, `source=customer_confirmation`, einen eigenen Scope-Versionszähler und einen gewichteten Durchschnitt der enthaltenen Modulscorewerte (`:246-298`). Die v2-API erlaubt nach der ersten bestätigten Baseline keine spätere Änderung mit Entscheidungen (`backend/app/routers/assessment_scope.py:215-236`).

## Bewertungsgrundlage Free versus Full

| Merkmal | Free Preliminary | Full Assessment v6 |
|---|---|---|
| Findings | alle physischen Scan-Issue-Zeilen | nur Codes, deren ursprüngliche Kategorie im bestätigten Scope liegt |
| Score | gespeicherter `scans.data_score` | `confirmed_scope.score_value` |
| Finding Count | Anzahl aller Scan-Issue-Zeilen | Anzahl der nach Scope-Filter verbleibenden Findings |
| Affected Records | Summe aller `affected_count` | Summe der verbleibenden Findings |
| Business Impact | Impact-Band aus allen Finding-Impacts; Detailwerte bleiben geschützt | Summe der verbleibenden Finding-Impacts; Bereichswerte und Anteile werden neu aggregiert |
| Custom/unknown category | Free normalisiert teils über Finding-Code auf einen Bereich | Full verwendet die ursprüngliche Kategorie und ordnet unbekannte/custom Kategorien als `unsupported` aus |

Wichtig: Die beiden Zahlen dürfen deshalb nicht als derselbe Messwert interpretiert werden. Der Full-Report ist keine bloße Freischaltung des Free-Finding-Arrays, sondern eine bestätigte Scope-Projektion.

## Was den Full-Report ausschließt

Nachweisbar ausgeschlossen werden:

1. Findings mit Kategorie außerhalb der exakten Full-Kategorien (`finance`, `sales`, `purchasing/purchase`, `inventory`, `crm/customer`, `manufacturing`, `service`, `jobs/job`, `hr`, `system/setup`).
2. Findings aus unterstützten Kategorien, deren Modul im bestätigten Snapshot `included_in_score=0` hat.
3. Custom-/Extension-Kategorien, auch wenn der Free-Report sie über Kategorie- oder Code-Fallback sichtbar macht.

Duplikate werden nicht stillschweigend entfernt; doppelte Finding-Codes führen im Full-Pfad zu einem Evidence-Fehler (`:165-172`).

## Erklärung der 16er-Differenz

Repository-belegt ist nur die Ursacheklasse: Scope-Projektion und/oder fail-closed Ausschluss von nicht unterstützten Originalkategorien. Die konkrete Erklärung `95 - 79 = 16` ist erst bewiesen, wenn das SQL-Audit für jeden der 95 Codes den bestätigten Modulentscheid und einen Ausschlussgrund ausgibt. Ohne diese Daten werden keine Codes rekonstruiert oder dem Full-Report nachträglich zugeschrieben.

## Read-only SQL-Audit

Das parametrisierte Audit liegt unter [`tools/sql/full_scope_01_historical_scan_audit.sql`](../../tools/sql/full_scope_01_historical_scan_audit.sql). Es enthält ausschließlich `SELECT`-Abfragen und verwendet keine Zugangsdaten. Es liefert:

* Scan-/Tenant-/Company-/Run-Identität und bestätigte Scope-Version;
* Profilfelder und gespeicherte Auto-Detection-Zeilen;
* alle bestätigten Modulentscheidungen;
* alle Original-Findings mit `finding_id`, Kategorie, Full-Modulklassifikation und Include-/Exclude-Grund;
* gruppierte 95er-/79er-Abgleiche sowie Score-, Affected- und Impact-Reconciliation.

Die Ausführung wurde in diesem Arbeitsbereich nicht vorgenommen: Es existiert kein autorisierter DEV-PostgreSQL-Zugang und es wurden keine DEV- oder PROD-Verbindungen versucht. Die Ergebnisse des Audits sind deshalb ausdrücklich noch unbestätigt.

Beispielausführung durch einen autorisierten DEV-Operator:

```text
psql "$DEV_DATABASE_URL" -v scan_id='RUN_20261116_000001_8870C7F3D8814DD1B1EE109EE7D38' \
  -f tools/sql/full_scope_01_historical_scan_audit.sql
```

`DEV_DATABASE_URL` darf nur in der Shell/Secret-Verwaltung gesetzt werden und gehört nicht in dieses Repository.

## Sichere zweite Free-Report-Seite

Auf belegbarer Datenbasis wären nur aggregierte, nicht geschützte Werte sicher:

* Scope-Status und Scope-Version, sofern bereits persistiert;
* `supported_modules`, `included_modules`, `unknown_modules`;
* `modules_analyzed` aus dem Scan-/Run-Kontext, klar als Scan-Metadatum bezeichnet;
* Free-Score, Finding Count, Affected Count und Impact-Band;
* ein Hinweis, dass Full nach Kundenbestätigung eine andere Bewertungsgrundlage verwendet.

Nicht auf einer Free-Seite ausgeben: einzelne Modulentscheidungen, Finding-Codes/-Titel, Ausschlusslisten, geschützte Details oder aus Zählern rekonstruierte Findings. Die aktuelle Scope-API liefert Modulzeilen nur bei Full-Berechtigung (`backend/app/routers/assessment_scope.py:179-183`).

## Folgeentscheidungen

Keine Korrektur ist aus dem Repository-Befund allein gerechtfertigt. Nach dem DEV-Audit ist zu entscheiden, ob die 16 Zeilen tatsächlich aus bestätigten Entscheidungen/unsupported Kategorien stammen oder ob ein Daten-/Zuordnungsfehler vorliegt. Erst im zweiten Fall wäre eine separate, gezielte Korrektur zu planen. Layouts, v6-Vorlagen, PDF-Export und Navigation wurden nicht geändert.

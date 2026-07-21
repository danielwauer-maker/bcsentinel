# GL-01A-2 – Unified Scan Start Dialog & Deep Scan Consolidation

## Architekturentscheidung vor Implementierung

Alle neuen, aus Business Central gestarteten Scans verwenden den vorhandenen Deep-Scan-Runner. Assessment, Validation und Monitoring bleiben Lizenz- beziehungsweise Triggerkontexte; sie definieren keinen abweichenden Checkumfang.

Die Dialogentscheidung wird zentral im `DH Deep Scan Mgt.` anhand eines technischen Trigger-Kontexts getroffen. Nur der Kontext `Manual` zeigt die Bestätigung. `Scheduled`, `Monitoring`, `Retry`, `System` und `API` bleiben dialogfrei. Damit ist die Entscheidung nicht allein von `GuiAllowed` abhängig.

Der bestehende Backend-Endpunkt `POST /scan/quick` bleibt zur API-Kompatibilität adressierbar, erzeugt aber keine neuen Scan-, Finding-, Lifecycle- oder Credit-Datensätze mehr. Er antwortet mit einem eindeutigen Deaktivierungshinweis. Historische Datensätze mit `scan_type=quick` und die AL-Enum-Ausprägung `Quick` bleiben unverändert lesbar; eine Datenmigration ist nicht erforderlich.

## Entry-Point-Matrix

| Einstiegspunkt | manuell | automatisch | Scan-Typ vor Sprint | Dialog vor Sprint | Änderung |
|---|---:|---:|---|---|---|
| Setup – kostenloser Data Health Score | ja | nein | Deep Runner / `data_health_score` | nur Mo–Fr 08:00–18:00 | zentraler manueller Dialog; gleicher Deep-Pfad |
| Setup – Validation Check | ja | nein | Deep Runner / `validation` | nur Mo–Fr 08:00–18:00 | zentraler manueller Dialog |
| Setup – Monitoring Scan | ja | nein | Deep Runner / `monitoring` | nein | zentraler manueller Dialog |
| Dashboard-Liste – Run Scan | ja | nein | Quick-Codeunit / `POST /scan/quick` | nein | Deep Runner im manuellen Kontext |
| Setup – Scheduled Scan „Run Now“ | Scheduled-Trigger | nein | Deep Runner / `monitoring` | nein | expliziter `Scheduled`-Kontext, dialogfrei |
| TaskScheduler – geplanter Lauf | nein | ja | Deep Runner / `monitoring` | nein | expliziter `Scheduled`-Kontext, dialogfrei |
| Monitoring-/Recovery-/Retry-Infrastruktur | nein | ja | Deep Lifecycle/Sync | nein | dialogfrei; keine Dialoglogik in Hintergrundpfaden |
| Backend `POST /scan/start` | nein | API | Deep Start | nein | unverändert und GUI-los |
| Backend `POST /scan/quick` | nein | API | reduzierter Quick Scan | nein | keine neuen Runs; kompatible Deaktivierungsantwort |
| Backend `POST /scan/sync` mit produktivem Trigger-Typ | nein | API | `monitoring` wurde historisch als `quick` normalisiert | nein | Assessment, Validation, Monitoring, Scheduled und Manual auf `deep` normalisieren; `quick` ablehnen |
| Historische Quick-Datensätze | nein | nein | `quick` | entfällt | lesbar lassen, keine Migration |

Für Monitor- und Scan-History-Seiten existiert im analysierten Stand kein eigener manueller Scan-Neustart. Ihre Recovery- und Backend-Synchronisationspfade starten keinen neuen fachlichen Scan und erhalten deshalb keinen Dialog.

## Quick-Scan-Klassifikation

| Fundstelle | Kategorie | Entscheidung |
|---|---|---|
| `DH Dashboard List.RunQuickScan` | A – aktiver Quick-Einstieg | auf zentralen Deep-Start umstellen |
| `DH QuickScan Mgt.` | B – interne Quick-Implementierung mit aktivem Aufrufer | nach Umstellung des Aufrufers entfernen |
| `DH API Client.RunQuickScan` und `ExecuteScan` | B – ausschließlich Quick-Implementierung | entfernen |
| Backend `POST /scan/quick` | A – aktiver Quick-API-Einstieg | ohne Datenmutation deaktivieren |
| Backend `scoring_service.py` | B – reduzierter 20-Regel-Rechner | aus produktiver Laufzeit entfernen; nur Katalog-/Kompatibilitätsbezug bei Bedarf erhalten |
| `DH Scan Header.Scan Type::Quick`, Backend-Scans mit `scan_type=quick` | C – historische Daten | erhalten und weiterhin anzeigen |
| Dokumentation mit Baseline-/Historienbezug | C – historische Evidenz | nicht rückwirkend verfälschen; operative Dokumentation aktualisieren |
| 14 Quick-Alias-IDs im Enterprise Check Catalog | D/C – Kompatibilitäts-IDs | unverändert erhalten, nicht als neue oder doppelte Regeln ausführen |

## Checkumfang und Abweichung zur Erwartung 213

Die AL-Registry enthält 199 eindeutige produktive Deep-Checks. Der Enterprise Check Catalog enthält 213 IDs. Die Differenz sind 14 alte Quick-Aliase:

- `CUSTOMERS_MISSING_COUNTRY_CODE`
- `CUSTOMERS_MISSING_CUSTOMER_POSTING_GROUP`
- `CUSTOMERS_MISSING_GEN_BUS_POSTING_GROUP`
- `CUSTOMERS_MISSING_PHONE_NO`
- `CUSTOMERS_MISSING_POSTCODE`
- `ITEMS_MISSING_BASE_UNIT`
- `ITEMS_MISSING_GEN_PROD_POSTING_GROUP`
- `ITEMS_MISSING_INVENTORY_POSTING_GROUP`
- `ITEMS_MISSING_VAT_PROD_POSTING_GROUP`
- `ITEMS_MISSING_VENDOR_NO`
- `VENDORS_MISSING_COUNTRY_CODE`
- `VENDORS_MISSING_GEN_BUS_POSTING_GROUP`
- `VENDORS_MISSING_PHONE_NO`
- `VENDORS_MISSING_VENDOR_POSTING_GROUP`

Das zusätzliche Ausführen dieser Alias-IDs würde Prüfungen duplizieren und Bewertungslogik verändern. Das ist ein ausdrückliches Nichtziel. Deshalb führen Assessment, Validation, manuelles Monitoring und Scheduled Monitoring künftig identisch die vorhandenen 199 Deep-Regeln aus. Die 14 Alias-IDs bleiben für historische/Katalog-Kompatibilität erhalten.

## Zielreihenfolge des manuellen Starts

1. lokale Setup- und Modulprüfung,
2. zentrale Bestätigung,
3. Lizenz-/Zugriffsprüfung,
4. atomare Annahme und gegebenenfalls Credit-Verbrauch im Backend,
5. vorhandener Deep-Scan-Runner,
6. einheitliche Erfolgsmeldung.

Bei „Nein“ endet der Ablauf vor API-Aufruf, Credit-Verbrauch, Run-Erzeugung, Queue- oder Statusänderung.

## Implementierungsergebnis und Verifikation

- Der Dashboard-Einstieg verwendet `DH Scan Dispatcher` und anschließend ausschließlich `DH Deep Scan Mgt.`/`DH Deep Scan Runner`.
- `DH QuickScan Mgt.` und die AL-Aufrufe von `/scan/quick` wurden entfernt.
- Der Backend-Quick-Endpunkt und Quick-Sync liefern HTTP 410, bevor eine Datenmutation möglich ist.
- Historische Schemas, Scan-Typen, Entitlement-Namen und Report-Mappings bleiben zur Lesbarkeit und API-Kompatibilität erhalten.
- Die zentrale BC-Confirm-Abfrage zeigt Ja/Nein; Titelzeile, Frage und Laufzeithinweis sind in de-DE und en-US vorhanden.
- Backend: final 329 Tests gesammelt. Kombinierte vollständige Abdeckung ergibt 322 bestandene Tests und sieben ohne PostgreSQL-DSN erwartungsgemäß übersprungene Tests; nach der letzten Normalisierungsänderung liefen zusätzlich die 48 betroffenen Licensing-/Sync-/Konsolidierungstests grün. Ein SQLite-Parallelitätstest war einmalig flaky und bestand im unmittelbaren isolierten Wiederholungslauf.
- AL: Build fehlerfrei; zwei bereits bekannte AL0432-Kompatibilitätswarnungen zum obsoleten Feld `Assessment Credits Available`.
- `git diff --check`: Exit Code 0.

## Releaseentscheidung

GO für die Scan-Pfad- und Dialog-Konsolidierung. Fachlicher Restpunkt außerhalb des erlaubten Sprintumfangs: Die vorhandene Deep-Registry umfasst 199 ausführbare Regeln statt der erwarteten 213; die Differenz sind die oben dokumentierten 14 historischen Alias-IDs. Eine Aktivierung als zusätzliche Regeln wäre eine Änderung von Prüf- und Bewertungslogik und benötigt eine eigene Product-Owner-Entscheidung.

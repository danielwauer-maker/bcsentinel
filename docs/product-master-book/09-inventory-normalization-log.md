# Inventar-Normalisierungslog

## Umfang und Regeln

BOOK-000C normalisiert ausschließlich `docs/product-master-book/` auf Basis des Repository-Stands vom 20. Juli 2026. Produktcode, Abhängigkeiten, Prioritäten und Releaseaussagen wurden nicht verändert. Ein Inventareintrag beschreibt jetzt entweder eine `capability`, ein stabiles `feature` oder ein untergeordnetes `subfeature`; reine Zählungen, Dateibestände, Testausführungsversuche und Dokumentationslücken sind keine Features.

## Strukturänderung

| Kennzahl | BOOK-000B | BOOK-000C |
|---|---:|---:|
| Inventareinträge gesamt | 81 | 93 |
| Capabilities | 0 | 16 |
| Features | 81 | 65 |
| Subfeatures | 0 | 12 |
| Workflows | 24 | 24 |
| Testsuite-Einträge | 6 | 6 |
| Technische Gaps | 10 | 10 |

Jede der 16 Komponenten besitzt jetzt genau eine Capability als Wurzel. Alle 77 Feature-/Subfeature-Einträge besitzen einen gültigen Elternknoten; Capability-Eltern sind `null`.

## Entfernte, zusammengeführte und neu geschnittene IDs

| Bisherige ID | Behandlung | Kanonisches Ziel / Begründung |
|---|---|---|
| `BACK-API-001` | entfernt | Routerbestand ist Komponentenbeleg, keine stabile Produktfunktion; konkrete Backendfunktionen bleiben einzeln erhalten. |
| `SCAN-QUICK-001` | zusammengeführt | `EXT-SCAN-001` beschreibt jetzt die komplette Quick-/Data-Health-Score-Kette von AL bis `POST /scan/quick`. |
| `SCAN-SCHED-001` | zusammengeführt | `EXT-SCHED-001` beschreibt Scheduler, Scheduled Runner und Dispatcher als zusammenhängende Funktion. |
| `DASH-AUTH-001` | zusammengeführt | `AUTH-DASH-001` umfasst Einladung, Login, Membership und Session; Dashboardfeatures referenzieren diese Authfunktion. |
| `TEST-RUN-001` | entfernt | Ein Sprint-Ausführungsversuch ist Testmetadatum, keine Produktfunktion. |
| `DOC-ROOT-001` | verschoben | Das leere Root-README bleibt `GAP-DOC-001` und ist kein Feature. |
| `OPS-PERF-001` | verschoben | Eine fehlende Performance-Suite bleibt Test-/Reviewbefund und ist keine vorhandene Betriebsfunktion. |

`DASH-AN-001` wurde auf Trends und Verteilungen begrenzt. Die zuvor darin gebündelten Seiten wurden als `DASH-SCAN-001`, `DASH-FIND-001` und `DASH-ACT-001` getrennt. `SEC-AUDIT-001` beschreibt nur noch Security Header und Log-Redaction; persistentes Admin-Audit bleibt separat unter `ADM-AUDIT-001`.

Folgende vorhandene Einträge wurden als Subfeatures eingeordnet: `BACK-TEN-001`, `SCAN-DEEP-001`, `SCAN-SYNC-001`, `WEB-LEGAL-001`, `WEB-SUPPORT-001`, `REP-HTML-001`, `REP-PDF-001`, `REP-SHARE-001`, `ADM-MAIL-001`, `TRANS-SITE-001`, `DB-CHECK-001` und `TEST-PG-001`.

## Komponentenvergleich

| Komponente | Vorher | Nachher |
|---|---:|---:|
| admin-backend | 6 | 7 |
| authentication-users | 4 | 5 |
| backend-api | 5 | 5 |
| business-central-extension | 7 | 8 |
| customer-dashboard | 6 | 9 |
| database-migrations | 4 | 5 |
| documentation-release | 3 | 3 |
| email-notifications | 3 | 4 |
| executive-reporting | 4 | 5 |
| infrastructure-operations | 5 | 5 |
| landingpage | 6 | 7 |
| licensing-billing | 6 | 7 |
| scan-engine | 7 | 6 |
| security-compliance | 6 | 7 |
| testing-quality | 5 | 5 |
| translations-localization | 4 | 5 |

Die Differenzen entstehen durch 16 neue Capability-Wurzeln, drei getrennte Dashboardfeatures und sieben entfernte/zusammengeführte Wrapper-IDs. Sie sind keine Aussage über neu implementierten Produktcode.

## Status- und Evidenzkorrekturen

- `EXT-SCHED-001`, `BACK-JOB-001`, `ADM-MAIL-001`, `MAIL-INV-001`, `MAIL-PART-001` und `TEST-PG-001` stehen auf `implemented`, weil die jeweilige statische Implementierungskette vorhanden ist. Externe Ausführung oder Zustellung bleibt als Unsicherheit beziehungsweise Teststatus getrennt.
- `TEST-CI-001` steht auf `not_found`: `.github/workflows/deploy.yml` enthält Deployment und Healthchecks, aber keinen Pytest-, Browser- oder AL-Testjob.
- Teststatus wurden auf `none`, `identified`, `partial`, `broad`, `manual_only` und `execution_unconfirmed` begrenzt. Keine vorhandene, aber nicht ausgeführte Suite wird als erfolgreich dargestellt.
- Workflows enthalten jetzt Komponenten und Ausführungsmodus. Die vier Referenzen auf zusammengeführte IDs wurden auf `EXT-SCHED-001` beziehungsweise `AUTH-DASH-001` umgestellt.
- Die Datenbankdokumentation wurde von 22 auf 29 ORM-Klassen korrigiert.

## Bewusst nicht statisch aufgelöst

- `landingpage/` ist im Backendimage paketiert und operativ referenziert. Ob und wie der statische Baum öffentlich in Produktion ausgeliefert wird, ist ohne Produktionsrouting nicht abschließend belegbar. `landingpage_neu/` besitzt keine gefundene Deploymenteinbindung.
- SMTP-Sendewege und Statuspersistenz sind implementiert; reale Zustellung und Clientdarstellung sind nicht automatisiert verifiziert.
- Scan-Recovery läuft per `asyncio.create_task` im Backendprozess; ein separater Worker-Service ist in den Compose-Dateien nicht vorhanden. Die Eignung für eine konkrete Topologie bleibt eine Betriebsentscheidung.
- Backup und Restore sind als Runbook dokumentiert; eine Automationsimplementierung wurde nicht gefunden.

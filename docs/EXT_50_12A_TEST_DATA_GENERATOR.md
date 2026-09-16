# EXT-50-12A — BCSentinel Performance Test Data Generator

Status: **AWAITING_MANUAL_BC_RUNTIME_EVIDENCE**. No merge, production deployment,
or XL/STRESS execution is authorized by this implementation.

## 1. Repository audit and decision

Audit on 2026-09-15: the checkout started on clean local `staging`, behind the
fetched `origin/staging`. The sprint branch starts at the fetched integration
branch; existing local staging commits were not reset. GitHub identified one
open PR, **#37**, `sprint/ext-50-04-permission-role-matrix` -> `staging`. Neither
that branch nor its permission design is changed here.

The current product manifest is **1.0.2.20**, application/platform **27.0.0.0**,
runtime **16.0**, range **53100–53202**. The older local manifest ended at 53201;
the integration branch already includes remediation objects at 53202. Object
IDs are unique per object type, not across all types. The existing manual
installation evidence records BC 28.3; that does not change the BC 27 build target.

Audited architecture:

- `bc-extension/app/src/codeunits/DHDeepScanRunner.Codeunit.al` runs the actual
  productive checks. `DHScanDispatcher`, `DHDeepScanMgt`, background runners and
  scheduler own scan execution; `DHApiClient` synchronizes aggregates with FastAPI.
- `DHDataProfilingMgt` counts Customer, Vendor, Item, customer/vendor/item ledgers,
  sales/purchase headers and lines, G/L, value and warehouse entries.
- `DH Deep Scan Run/Finding`, scan headers/issues, setup, exceptions, action logs,
  scan check selection and dashboard tables remain unchanged. This tool writes
  **no BCSentinel findings, scores, scan history, or backend data**.
- `DHInstall` initializes setup; `DHUpgrade` preserves data and invalidates access
  snapshots. Neither installs, invokes, or depends on the generator.
- Five product permission sets exist (VIEWER, SCAN, SETUP, ADMIN, SCHEDULER).
  None receives generator access. EXT-50-04 remains a separate release gate.
- No existing AL Test app or reusable BC seed/demo generator was present.
  Existing automation uses Python source/evidence contracts, PowerShell source
  uniqueness/GL contracts, and the central Windows AL/Cop workflow. Legacy quick
  scoring in `scoring_service.py` is not the scenario oracle.

**Architecture A: separate sandbox-only extension**, `bc-performance/app.json`,
app ID `1bf95437-93b6-4329-bc49-40585f1272a0`, version 1.0.0.0, schema 1,
reserved range **53400–53449**. No dependency on the customer extension is needed:
both operate on the same standard company tables. Separate packaging keeps the
tool out of normal customer installations and install/upgrade hooks. A customer
release must select the BCSentinel package, never the QA package from CI artifacts.

## 2. Profiles and counting

The single source of profile defaults is `BCP Policy.SetProfile`. Custom runs
configure each count separately; presets intentionally overwrite custom counts.

| Profile | Customer (18) | Vendor (23) | Item (27) | Business records | Supporting Item UOM (5404) | Ownership rows |
|---|---:|---:|---:|---:|---:|---:|
| DEV | 6,000 | 2,000 | 12,000 | 20,000 | 12,000 | 32,000 |
| LARGE | 150,000 | 50,000 | 300,000 | 500,000 | 300,000 | 800,000 |
| XL | 600,000 | 200,000 | 1,200,000 | 2,000,000 | 1,200,000 | 3,200,000 |
| STRESS | 1,500,000 | 500,000 | 3,000,000 | 5,000,000 | 3,000,000 | 8,000,000 |

One run metadata row is additional. Setup and three configuration source records
are existing supporting data and never count toward the generated profile.
Custom requires 1–5,000,000 per entity and at most 10,000,000 business records.
Batch size defaults to 1,000; allowed range 1–5,000. Seed range: 0–1,000,000.

This is deliberately a **master-data scan workload**: structurally valid synthetic
customers, vendors and a large product catalog stress existing scan loops,
duplicate checks and aggregation. It is not a claim that a typical tenant has
these entity ratios. No unposted/posted transaction counts are fabricated to
reach the target. Ledger aging, stock balances, posting, sales/purchase line,
warehouse and scheduler load coverage must be added through real posting flows
in a later workload. EXT-50-12 must benchmark those separately.

## 3. Configuration and deterministic data

Create a dedicated disposable **SaaS sandbox** company named `BCS-PERF-...`.
Use configured synthetic Customer, Vendor and Item source records. The dialog
copies only nonempty setup codes into immutable JSON snapshots on the run:

- Customer/Vendor: posting group, general/VAT business posting group, country,
  payment terms and payment method.
- Item: base UOM, inventory/general/VAT product posting groups and item category.

Names, addresses, VAT identifiers, dimensions, financial balances, media and
other fields are never copied from source records. Source records/setup are not
modified. The synthetic address is intentionally independent of the source
country; this is a scan fixture, not postal-validation evidence.

Numbers are `BCP` + six-digit run ID + `C`/`V`/`I` + seven-digit sequence, e.g.
`BCP000001I0000001` (17 characters, within Code[20]). No collision is overwritten;
an existing number makes the batch fail atomically. Run IDs over 999999 fail.
Email addresses use reserved `example.invalid`, never a real delivery domain.

For sequence `n`, scenario membership is
`((n mod 100) * 37 + (seed mod 100)) mod 100 < error_rate`.
This is an exact permutation of each full block of 100; configured rates are
**1, 5, 10, 20 %**. Item scenario type alternates every 100 records so that price
and cost problems each receive half the item error budget. Prices/costs also
vary by seed and sequence. Identity/run timestamps/SystemIds necessarily vary.
The same schema, configuration snapshots, seed, profile, BC version and installed
extensions reproduce business structure and scenario positions. Seeds separated
by 100 share scenario positions; the seed is not a cryptographic random source.
Changing reference setup or installed subscribers can change validation results.

## 4. Scenario mapping and expected observations

| Scenario | BC data | Actual Deep Scan check | Category | Error allocation | LARGE, seed 5001, 10% |
|---|---|---|---|---|---:|
| Missing customer email | Customer.`E-Mail` = blank | `CUSTOMERS_MISSING_EMAIL` | CUSTOMER | r% of customers | 15,000 records |
| Missing vendor phone | Vendor.`Phone No.` = blank | `VENDORS_MISSING_PHONE` | VENDOR | r% of vendors | 5,000 records |
| Missing item selling price | Item.`Unit Price` = 0 | `ITEMS_WITHOUT_UNIT_PRICE` | ITEM | r/2% of items | 15,000 records |
| Missing item cost | Item.`Unit Cost` = 0 | `ITEMS_WITHOUT_UNIT_COST` | ITEM | r/2% of items | 15,000 records |

All four are deterministic. `Expected Scenarios` should be **50,000** for the
first LARGE run. The ownership record stores each injected check ID. The product
uses `AddCountFinding` for these checks: expect aggregate finding rows and their
affected-record counts, **not 50,000 finding rows**. Enabled check selections,
exceptions, entitlements, pre-existing data and scan thresholds still apply.

Baseline noise is explicit: vendors have no generated bank accounts; new masters
have no transaction history/default dimensions; other checks may report those
conditions. Missing unit cost can also trigger related cost checks. Capture a
pre-generation scan, evaluate the four mapped check deltas, and retain ownership
counts as the oracle. The error rate controls these four injected scenarios,
not the total fraction of records flagged by all 199 checks. There is no claim
of an otherwise completely clean dataset.

Not implemented: negative inventory, overdue open entries, negative prices,
invalid email formats, deliberate duplicates, missing dimensions/posting setup.
Negative stock/aging would require proper journal/document posting and is not
safely reversible through deleting master records. Invalid email validation is
not bypassed. Posting setup is reused and validated rather than corrupted.

## 5. Import behavior, batches, recovery and metrics

Configuration relation fields use `FieldRef.Validate`; names/descriptions and
item vendor/base UOM use their standard Validate logic. Synthetic contact text,
explicit number, prices and the intentional blank/zero scenario fields use direct
assignment. The customer/vendor/item `Insert(false)` is a controlled master-data
import: it avoids number series consumption, automatic contacts, default dimension
propagation and implicit item unit group creation. Blank global dimensions are
intentional. No ledger tables are written. Unit-of-measure rows use Validate and
`Insert(true)`; item base UOM is validated after its supporting row exists.
Standard integration events/installed subscribers still execute according to BC
semantics; use the clean QA baseline and verify side effects during DEV first.
The import explicitly calls the standard `UpdateReferencedIds` methods and sets
master modification timestamps; API reference IDs are not left stale merely
because the OnInsert trigger is skipped. UOM ownership is captured after final
item validation so its timestamp reflects the final state of the batch.
Category OnValidate can inherit attribute mappings even before Item.Insert.
Configuration creation and each batch therefore reject categories with mappings
at any ancestor, including cyclic hierarchies, before inserting business rows.
This preserves the explicit one-UOM-per-item support contract.

Generation order: vendors -> customers -> items. Every item references a vendor
from its own run. `BCP Batch` locks and rereads the run, performs at most one
configured batch and writes counters and ownership in the same transaction.
`CommitBehavior::Error` rejects explicit commits inside the worker. The Boolean
`Codeunit.Run` boundary commits on success and rolls back the failed batch.
The coordinator persists the failure text and increments failed batches after
rollback. No TryFunction write transactions are used.

The core is GUI independent. `Execute(runId, true)` executes one bounded batch;
`Execute(runId, false)` continues until completion. The UI offers both. `Running`
may mean a paused checkpoint with no active session; resuming is safe because
workers serialize on the run lock and reread counters. A second caller cannot
recreate a committed sequence. Cancel serializes on that same lock and is observed
at the next boundary; it keeps tracked data. Cancelled is terminal for generation.
Resume Pending/Running/Failed; cleanup requires Completed/Cancelled/Failed/Cleaning.
Cleaned is terminal. Completed is only assigned at exact target equality.

Hard session termination may leave Running without a caught diagnostic; the last
committed batch timestamp/checkpoint remains authoritative. Resume that run.
Counts preserve historical generation totals after cleanup; Cleanup Count records
actual deletions separately. No resuming a cleaned run or silent reclassification.

Page metrics: run ID/profile/seed/rate, entity counters, target/progress, phase,
batch, start/end, wall duration, average business records/sec, injected scenarios,
failed batches, error text and cleanup count. Refresh in a second client while
generation runs; there is no claim of automatic UI refresh or a measured throughput.
Wall duration includes pauses and retries. A future Job Queue wrapper can call
the same bounded API; automatic queue installation is intentionally absent.
STRESS requires substantial database capacity: business + support + tracking
totals **16 million rows**, before indexes and normal BC data.

## 6. Sandbox and least-privilege design

Every mutation entry point/worker checks `Environment Information.IsSaaS`,
`IsSandbox`, `IsProduction` and the `BCS-PERF-` company name. Unknown environments,
on-prem containers and production fail closed. A company name alone never enables
production. Sources:
[Environment Information](https://learn.microsoft.com/en-us/dynamics365/business-central/application/system-application/codeunit/system.environment.environment-information),
[Codeunit.Run transaction semantics](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/methods-auto/codeunit/codeunit-run-method).

- `BCP GENERATE`: QA pages/worker execution; read setup/master data; **indirect**
  insert on owned masters/support/ownership and modify on run/item where needed.
- `BCP CLEANUP`: independent capability; indirect delete on the three masters,
  item UOM and ownership; indirect modify on run. No generation permission is
  included. Assign both only to a QA operator who needs both actions.
- Neither permission set gives direct write access to ownership or persistent
  run configuration. UI configuration uses a temporary record. Product roles,
  installer and customer manifest are unchanged. No SUPER dependency is present.
- Normal BC sign-in/system execution permissions are still needed. Cleanup's
  conservative reference inventory requires **read-only access to every inspected
  table** and standard delete-trigger dependencies. A missing permission refuses
  cleanup; it is never skipped. Capture denied objects during DEV and grant only
  the needed read/standard execution permissions in the QA operator role. This
  exact non-SUPER runtime matrix remains an acceptance gate, not a compile claim.

## 7. Ownership and safe cleanup

`BCP Owned Record` stores run ID, allowlisted table ID, SystemId, RecordId,
reserved number, original SystemModifiedAt, supporting flag and scenario.
Ownership and the business insert commit together. Cleanup never searches only
by a prefix to choose deletion targets and never calls DELETEALL on a business
table. Prefixes serve as an additional guard and as conservative dependency filters.

Preview reports the tracked **candidate count**, including supporting rows. It
is not a full dry run of BC delete triggers or a claim all candidates are deletable.
UI confirmation defaults to No and displays the count. Cleanup API is itself a
dedicated privileged capability; unattended callers must explicitly authorize it.

Deletion order: items with their owned UOM -> customers -> vendors. Each batch:

1. Locks/rereads the run and requires Cleaning.
2. Scans declared references plus conservative polymorphic number fields for the
   run/entity namespace. Foreign references refuse the phase before deleting it.
   Missing read permissions fail closed. This check is per batch, not per row.
3. Locks each tracked target and verifies table allowlist, run namespace, exact
   SystemId, exact RecordId and original modification timestamp. Missing, renamed,
   replaced or externally edited targets refuse the batch; there is no force flag.
4. Refuses record links/approval records and the standard item's GUID-based
   Entity Text/Unit Group cascades. The metadata scan covers active local normal
   tables; removed fields and nonpersistent/external tables are not queried.
   For items, every UOM row must be tracked
   by the same run and unchanged before the standard item cascade can delete it.
5. Calls standard `Delete(true)` and verifies supporting records disappeared,
   then removes ownership. The batch's deletes/counters commit atomically.

No existing setup, configuration-source record, unrelated customer or unrelated
prefix collision is deleted. Ordinary existing BC delete checks remain active.
Reference probes are deliberately conservative: a same-number polymorphic
reference may block cleanup even if semantically unrelated. Cleanup is more
expensive than generation and may require several attempts after genuine issues
are investigated. Do not manually remove ownership to suppress a refusal.

**Operational boundary:** no concurrent business entry/posting, extension install,
or editing of generated records during cleanup. Standard relation metadata and
known RecordId links do not describe arbitrary third-party subscriber side effects
or arbitrary GUID/text references. Such extensions require an expanded safety
audit and DEV cleanup test first. The tool is for an isolated disposable sandbox
company, not mixed customer operations. Never grant broad delete permissions as
a shortcut. Uninstall only after cleanup: uninstall/delete-extension-data can
remove ownership while leaving standard master rows; BC does not provide a safe
automatic master-data uninstall rollback. Retain the QA package and ownership.

## 8. Build, source tests and CI

Build workspaces must be created with
`bc-extension/scripts/New-BCBuildWorkspace.ps1 -Profile PerformanceQA`, under
`.build/bc-extension/PerformanceQA`. This copies only QA sources and BC 27 symbols,
never nests a second project inside the customer AL root. Existing APP/ZIP/PDF
artifacts are not removed. Use a new output APP filename for each local compile.

The existing `.github/workflows/bc-al-compile.yml` compiles customer and QA apps
with CodeCop/PTECop. The separate `ext-50-12a-test-data-generator.yml` runs source,
safety, evidence and existing extension regression contracts plus GL/source checks.
BC runtime tests are not enabled by the central compile workflow.

`BCP Self Tests` contains four real AL test methods: preset counts; exact rates
across 10,000 sequences and multiple seeds; namespace isolation/bounds; rejected
configuration values. They require the BC Test Tool to execute. Merely compiling
them is **not PASS** for AL behavior. Python tests are explicitly source contracts,
not an emulator of BC insertion, triggers, permissions, rollback or cleanup.

Local contracts: from `backend`, use only `.venv/Scripts/python.exe -m pytest
--noconftest ...` with the repository pytest.ini. No PostgreSQL migration, database
write or SQLite substitution is part of this sprint. Existing product AppSourceCop
baseline remains 3×AS0051, 1×AS0084, 1×AS0092; QA uses CodeCop/PTECop and is not an
AppSource customer release. No existing test is removed or weakened.

## 9. Manuelle Abnahme: zuerst DEV, danach separat LARGE

**Noch nicht ausgeführt.** Dies ist eine Testanleitung, kein Runtime-Nachweis.
LARGE setzt einen bestandenen DEV-Lauf einschließlich Sicherheitsfällen voraus.
XL/STRESS werden nicht automatisch gestartet.

### 9.1 Paket und Vorbereitung

- Workflow **BC AL Compile and Cop Gate**, Artifact **bc-al-compile-output**.
  QA-Datei: `BCSentinel Analytics - Daniel Wauer_BCSentinel Performance QA_1.0.0.0.app`.
  Extension **BCSentinel Performance QA**, Publisher **BCSentinel Analytics - Daniel Wauer**,
  Version **1.0.0.0**, ID `1bf95437-93b6-4329-bc49-40585f1272a0`.
  Erfolgreichen Run und Paket-SHA256 aus dem Evidence-Dokument verwenden.
  Das Artifact enthält auch das Produktpaket; dieses nicht mit der QA-App verwechseln.
- Keine BCSentinel-Abhängigkeit im QA-Manifest. BC-Anwendung/Plattform mindestens
  27.0.0.0, Runtime 16.0. Für Findings zusätzlich BCSentinel 1.0.2.20 mit gültigem
  Scan-Zugang und freigegebenem Testbackend verwenden.
- Ausdrücklich ausgewiesene **BC-27-SaaS-Sandbox**, isolierte Firma **BCS-PERF-DEV**.
  Version und App-Inventar festhalten. Keine parallelen Buchungen, Stammdatenpflege
  oder App-Installationen während der Tests.
- Admin: **Erweiterungsverwaltung > Erweiterung hochladen**, QA-Datei auswählen,
  Name/Version prüfen und erfolgreichen Installationsstatus abwarten. Danach als
  separater QA-Operator neu anmelden. Installation ist kein Generierungsnachweis.
- QA-Operator: **BCP GENERATE** und **BCP CLEANUP**, auf diese Firma begrenzt,
  zusätzlich normale BC-Anmeldung/Systemausführung und erforderliche Leserechte.
  **Kein SUPER**, auch nicht aus Gruppen. Effektive Rechte exportieren. Keine
  direkten Schreibrechte auf Ownership/Run-Tabellen vergeben. Zwei Negativtest-
  Benutzer vorbereiten: Generate-only und Cleanup-only, ohne breite Codeunit-Rechte.
- Die genaue Standard-BC-Lese-/Ausführungsmatrix bleibt ein SaaS-Abnahme-Gate.
  Bei Verweigerung Objekt/Operation festhalten und nur erforderliche Rechte ergänzen.
  Kein SUPER, kein Überspringen unlesbarer Referenztabellen. Ein Standardrollenname
  ist kein Beweis für ausschließlich lesende Rechte.
- Synthetische Quellen außerhalb des BCP-Nummernraums vorbereiten, beispielsweise
  `QA-SOURCE-C`, `QA-SOURCE-V`, `QA-SOURCE-I`. Customer/Vendor: gültige nichtleere
  Buchungsgruppe, Geschäftsbuchungsgruppe, MwSt.-Geschäftsbuchungsgruppe,
  Länder-/Regionscode, Zahlungsbedingungscode und Zahlungsformcode. Item: Basiseinheit,
  Lagerbuchungsgruppe, Produktbuchungsgruppe, MwSt.-Produktbuchungsgruppe,
  Artikelkategorie **ohne eigene/geerbte Attribute**. Bestehende gültige Setup-Codes dieser QA-Firma verwenden.
- Vorher-Bestand normaler Cronus-/Teststammdaten, Quellen, Setup, Contacts, Item UOM,
  Item References, Extended Text und Default Dimensions mit Schlüsseln, SystemIds
  und Änderungszeiten exportieren. Keine echten Kundendaten ins Evidence-Repository.

Lesende Kontrolle: dieselbe Tenant-/Sandbox-URL mit
`?company=BCS-PERF-DEV&table=53401` öffnen, vorhandene Seitenparameter ersetzen.
Tabelle 53400 = Run, 53401 = Ownership, 18 = Customer, 23 = Vendor, 27 = Item,
5404 = Item UOM. Die Ansicht ist schreibgeschützt und benötigt Tabellen-Leserecht
sowie direkte Ausführung von Systemobjekt **1350 Run table**.
[Microsoft Tabellenansicht](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-view-table-data).
Ownership nach Run ID filtern. Exakte Zahlen aus vollständigem lesendem Export
oder Tabellenstatistik erfassen; eine sichtbare Browserseite reicht nicht.

### 9.2 Vollständiger erster DEV-Lauf

1. Alt+Q: **INTERNAL QA - Performance runs**; alternativ in derselben Sandbox
   `?company=BCS-PERF-DEV&page=53401`. Deutsche Beschriftungen sind übersetzt.
2. **Create DEV / LARGE / XL / STRESS / Custom**: **DEV**, Seed **5001**, Error Rate
   **10**, Batch Size **1000**, drei Quellen wählen. OK und QA-Bestätigung.
3. Pending-Run ID notieren, Ziel **20.000** prüfen. Baseline-Scan der vier relevanten
   BCSentinel-Prüfungen vor dem Start sichern.
4. **Start / resume**, Run ID und Zielzahl bestätigen. Zweiten Client regelmäßig
   aktualisieren: Phase, Fortschritt, Zähler, Batch, Start/Ende, Fehler festhalten.
5. Soll: **Completed**, **100 %**, **6.000 Customers / 2.000 Vendors / 12.000 Items**,
   **20 Batches** ohne Unterbrechung/Fehler, **2.000 Injected scenarios**.
6. Originaltabellen kontrollieren: Nummernpräfix `BCP` + sechsstellige Run ID +
   C/V/I; Run 1 beispielsweise `BCP000001C*`. Zähler unabhängig überprüfen.
7. **12.000 Item UOM**, **32.000 Ownership**: Table ID 18=6.000, 23=2.000,
   27=12.000, 5404=12.000. Nur 5404 hat Supporting=true. Zusätzlich ein Run-Datensatz.
8. Stichproben bei Seed 5001: `...C0000011` E-Mail leer; `...V0000011` Telefon leer;
   `...I0000011` Preis=0, Kosten positiv; `...I0000111` Kosten=0, Preis positiv.
   Sequenz 1 jeweils ohne diesen Fehler. Buchungsgruppen, eigene Vendor-Relation,
   Basis-UOM und UOM-Menge=1 prüfen. SystemId/RecordId/Modified At mit Ownership vergleichen.
9. Szenariomengen **600 / 200 / 600 / 600**. Normale BCSentinel-Prüfung ausführen;
   betroffene Datensätze gegenüber Baseline vergleichen. Aggregierte Findings sind
   keine 2.000 einzelnen Finding-Zeilen. Weitere Checks können Baseline-Probleme melden.
10. Keine zusätzlichen Contacts, Item References, Extended Text oder Default Dimensions
    erwarten. Ungeplante Subscriber-Effekte sind ein zu untersuchender FAIL, kein
    Anlass, ungetrackte Daten zu löschen.
11. **Preview cleanup** für diesen Run: **32.000 Kandidaten**. Exporte sichern.
    Die Vorschau zählt Kandidaten, sie beweist keine Löschbarkeit.
12. **Cleanup run**: Kandidatenzahl prüfen, bewusst bestätigen. Soll **Cleaned**,
    Cleanup Count **32.000**, Ownership für Run ID **0**, eigene Stammdaten/UOM **0**.
    Historische Generierungszähler bleiben erhalten. Fehlertext bei Verweigerung sichern.
13. Normale Cronus-/Testdaten, Quellen und Setup müssen in Schlüssel, SystemId,
    relevanten Werten und Änderungszeit unverändert sein. Vorher-/Nachher-Vergleich
    dokumentieren. QA-App/Ownership nicht vor erfolgreichem Cleanup deinstallieren.

### 9.3 Sicherheits- und Recovery-Fälle vor LARGE

Pro Fall eigene Run ID und Vorher-/Nachher-Beweise. Zusätzliche Daten legt ein
separater Vorbereiter ausschließlich synthetisch in dieser QA-Firma an. Operator
bleibt ohne SUPER. Keine unbekannten/echt verwendeten Daten entfernen.

| Fall | Konkrete Schritte | Erwartung |
|---|---|---|
| Checkpoint + Resume | Custom: Customer 3, Vendor 2, Item 5, Seed 5001, Rate 10, Batch 2. Run one batch, schließen, neu öffnen, Start / resume. | Erst Running/Vendor=2/Ownership=2; danach Completed mit 10 Business + 5 UOM, Ownership=15, keine Duplikate. Cleanup=15. |
| Echte Unterbrechung | Zusätzlichen DEV-Run starten. Admin beendet gezielt dessen dokumentierte Benutzersitzung über die Sandbox-Sitzungsverwaltung. Nach Stillstand Zähler/Ownership sichern, neu anmelden, Resume. Browser-Schließen allein beweist keinen Serverabbruch. | Vollständig committete Batches bleiben, laufender Batch ganz oder gar nicht. Running ohne Fehlertext möglich. Nach Resume genaue DEV-Zahlen. Ohne Sitzungsverwaltung bleibt dieser Fall PENDING. |
| Fehler / Kollision | Custom 3/2/5, Batch 2, Pending anlegen. Vorbereiter legt ungetrackten synthetischen Vendor mit dessen zweiter Nummer `BCPrrrrrrV0000002` an, Identität sichern. Run one batch. | Failed, Failed Batches=1, Start/Ende gesetzt, Zähler/Ownership=0; Vendor 1 aus dem fehlgeschlagenen Batch fehlt ebenfalls. Kollisionsdatensatz unverändert. Nur diesen synthetischen Datensatz in freie `QA-COLLISION-...`-Nummer umbenennen, Resume testen. Er bleibt nach Cleanup erhalten. |
| Teil-Cleanup | Custom 3/2/5, Batch 2, ein Batch, Cancel run, Preview/Cleanup. | Cancelled; Preview=2 Vendors, Cleanup=2, Cleaned. Start nach Cancelled/Cleaned erzeugt nichts. |
| Geänderter Datensatz | Eigenen Custom-Run abschließen. Vorbereiter ändert Artikelbeschreibung auf normaler Karte, Identität/Zeiten sichern, Cleanup versuchen. | Betroffener Artikel/UOM bleiben; Fehler wegen geänderter Identität. Frühere Cleanup-Batches können schon committet sein. Text zurückändern stellt SystemModifiedAt nicht wieder her: zur Untersuchung stehenlassen, kein Tracking-Reset. |
| Fremde Referenz | Eigener abgeschlossener Custom-Run. Über Artikelkarte > Referenzen synthetischen Item-Reference-Eintrag hinzufügen; prüfen, dass Artikel selbst unverändert bleibt. Cleanup. | Phase verweigert Löschung, Referenz und Artikel bleiben. Ändert die UI auch den Artikel, ist dies zusätzlich Änderungsfall und kein isolierter Referenzbeweis. Künstliche Referenz nur nach bewusster manueller Prüfung entfernen. |
| Fremde UOM | Eigener abgeschlossener Custom-Run, zusätzliche Artikel-Einheit anlegen, Cleanup. | Keine Löschung der ungetrackten UOM über Standardkaskade, betroffener Batch rollt zurück. |
| Ohne Cleanup | Generate-only-Benutzer erzeugt kleinen Run, versucht Preview/Cleanup. Effektive Rechte prüfen. | Zugriff verweigert, keine Löschungen. Sichtbare Aktion ist kein Berechtigungsnachweis. |
| Ohne Generate | Cleanup-only-Benutzer versucht Create / Start / Run one batch am vorhandenen Pending-Run. | Zugriff verweigert, keine neuen Stammdaten/Ownership. Cleanup eines vorbereiteten terminalen Runs separat möglich. |
| Kategorieattribute | Eigene synthetische Kategorie mit Attribut oder Elternkategorie mit Attribut als Quelle wählen. Zusätzlich bei Pending-Run danach ein Attribut an dessen QA-Kategorie ergänzen und Run one batch ausführen. | Anlage bzw. Batch verweigert; keine ungetrackten Artikelattribute. Im Batch-Fall Failed und vollständiger Rollback. Änderungen nur an dedizierter Testkonfiguration. |
| No-SUPER | Vollständiger DEV-Lauf und Cleanup mit effektiven Operator-Rechten aus 9.1. | Beide ohne SUPER erfolgreich. Verweigerte Standardobjekte gezielt ergänzen, kein pauschaler Vollzugriff. |
| Firmen-Guard | In anderer Testfirma ohne BCS-PERF- die QA-Seite öffnen. | Verweigerung ohne Datenänderung. Keine Installation in Produktion für einen Guard-Test. |

Vier AL-Selbsttests der Codeunit **53407 BCP Self Tests** mit einem für diese
Sandbox bereitgestellten AL-Test-Runner ausführen und Ergebnisse exportieren.
Die QA-App enthält keinen Runner. Ist er nicht verfügbar, bleibt AL-Runtime PENDING;
Source Contracts ersetzen weder AL-Ausführung noch Transaktions-/Berechtigungstests.

### 9.4 LARGE nach erfolgreicher DEV-Abnahme separat

**LARGE / Seed 5001 / 10 % / Batch 1000**. Gegen SetProfile, CreateItem und Track
verifiziert: **150.000 Customers + 50.000 Vendors + 300.000 Items = 500.000 Business**,
**300.000 explizite UOM**, **800.000 Ownership/Cleanup-Kandidaten**, ein Run-Datensatz.
Weitere Subscriber-Effekte müssen im DEV ausgeschlossen sein.

Baseline, Ist-Tabellenzahlen, Laufzeit, Reaktionsfähigkeit, Fehler und Scan-Deltas
**15.000 / 5.000 / 15.000 / 15.000** sichern. Danach bewusst Cleanup mit Preview=800.000:
Cleaned, Cleanup Count=800.000, eigene Stammdaten/UOM/Ownership=0, normale Daten unverändert.
Run IDs, Zeiten, Ergebnisse und repository-relative Beweispfade im Evidence-JSON
hinterlegen. Gesamtstatus bis zu echten Nachweisen:
**AWAITING_MANUAL_BC_RUNTIME_EVIDENCE**.

## 10. Later XL/STRESS and EXT-50-12

Do not automatically start XL or STRESS after LARGE. Evaluate generation and scan
duration, database growth, memory/locking, BC responsiveness, timeout behavior,
finding counts, dashboard/report behavior and cleanup first. Only then approve XL;
STRESS comes last. This sprint supplies fixtures and generation metrics. It does
not certify 50-tenant/customer readiness, production performance, scheduler scale,
or a GO decision for release. Outstanding sandbox and permission gates block GO.

## 11. CI dependency incident, 2026-09-16

Failed run `35010288574` compiled both extensions, then failed installing the
unchanged product app through the BC Administration Shell. The retained event log
reports `ReflectionTypeLoadException` in
`Microsoft.Dynamics.Nav.Types.SerializationUtilities.TypesToBeAddedAsKnownTypes`
and `ChangeNavAppStateResponse.NavBaseExceptions`: the administration response
serializer could not resolve `Microsoft.Bcl.AsyncInterfaces, Version=10.0.0.11`.
This is a managed dependency of the BC administration type-loading path, not an
AL extension dependency. The exact referring assembly and whether the DLL was
absent on disk versus unavailable to that load context were not captured; the
old container has been removed. A runner-update causal claim is not established.

Observed environment: BcContainerHelper 6.1.14; host PowerShell 7.6.5;
Windows Server 2022 host 10.0.20348.5499, container 10.0.20348.5622;
BC artifact 27.5.46862.54684/w1, platform 27.0.54564.0. The helper release notes
identify .NET 10 assembly-loading problems with remote PowerShell sessions.
The exact container .NET runtime inventory was not retained.

Correction: pin **BcContainerHelper 6.1.18** for all three module references.
Its published package defaults `usePsSessionForBc27=false` and selects `docker exec`
for BC 27 administration calls, avoiding the affected remote session. The earlier
6.1.14 fix addressed System.IO.Pipelines only; 6.1.18 extends the general BC 28
remote-session workaround to BC 27. No install/publish gate is removed, no errors
are ignored, and no business/security rules are changed to address this failure.
The independent pending start-time correction preserves the timestamp of a first
failed generation batch after rollback; it is not a CI-install workaround.

Primary references:
[Microsoft helper release notes](https://github.com/microsoft/navcontainerhelper/blob/main/ReleaseNotes.txt),
[pinned package](https://www.powershellgallery.com/packages/BcContainerHelper/6.1.18),
[Microsoft known admin-shell issue (page currently labels BC 28)](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/upgrade/known-issues#business-central-admin-shell-modules-fail-in-powershell7-remote-sessions).
The helper's BC 27-specific implementation is the applicability evidence for this
pipeline. Re-running the complete install gate is required to verify the fix.

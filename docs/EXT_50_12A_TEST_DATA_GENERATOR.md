# EXT-50-12A — BCSentinel Performance Test Data Generator

Status: **AWAITING_MANUAL_BC_RUNTIME_EVIDENCE**. Current QA version: **1.0.0.1**.
The first actual SaaS test found a New Run dialog defect in 1.0.0.0; see section 14. No merge, production deployment,
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
app ID `1bf95437-93b6-4329-bc49-40585f1272a0`, current version 1.0.0.1, schema 1,
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
The central workflow now executes eight pure AL behavior tests in both fresh
and upgrade containers. SaaS UI, generation and cleanup remain separate manual gates.

`BCP Self Tests` originally contained four AL test methods, now extended to eight: preset counts; exact rates
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

**DEV-Erzeugung/Cleanup noch nicht ausgeführt.** Installation und Firmen-Guard
wurden vom Benutzer in SaaS bestätigt; die Run-Anlage scheiterte in 1.0.0.0.
Nach Upgrade auf 1.0.0.1 zuerst den Dialog-Retest in Abschnitt 14 ausführen.
LARGE setzt einen bestandenen DEV-Lauf einschließlich Sicherheitsfällen voraus.
XL/STRESS werden nicht automatisch gestartet.

### 9.1 Paket und Vorbereitung

- Workflow **BC AL Compile and Cop Gate**, Artifact **bc-al-compile-output**.
  QA-Datei: `BCSentinel Analytics - Daniel Wauer_BCSentinel Performance QA_1.0.0.1.app`.
  Extension **BCSentinel Performance QA**, Publisher **BCSentinel Analytics - Daniel Wauer**,
  Version **1.0.0.1**, ID `1bf95437-93b6-4329-bc49-40585f1272a0`.
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

Acht AL-Selbsttests der Codeunit **53407 BCP Self Tests** mit einem für diese
Sandbox bereitgestellten AL-Test-Runner ausführen und Ergebnisse exportieren.
Die QA-App enthält keinen Runner; die CI installiert ihn separat und führt die
Request-/Policy-Tests aus. Ein optionaler SaaS-Wiederholungslauf benötigt ebenfalls
einen Runner. Source Contracts ersetzen weder AL-Ausführung noch die manuellen
Transaktions-/Berechtigungstests.

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
pipeline. The complete install gate passed in run `35038536708`, and again for reviewed
code `573d6fc` in run `35039164370`: both apps compiled, published, synchronized
and installed. BC artifact/platform, PowerShell and OS versions match the failed
run; the first successful container event log has no AsyncInterfaces entry.

## 12. Abschließender Code-Review

Prüfung gegen den tatsächlichen BC-27-Standardquellcode aus den Symbolpaketen,
nicht allein gegen die Python-Verträge. Scope: kompletter PR gegen die dokumentierte
staging-Baseline; Produkt-AL und Produktberechtigungen bleiben unverändert.

| Bereich | Statischer Befund | Offener Runtime-Nachweis |
|---|---|---|
| Security | SaaS/Sandbox/Production/Firmen-Guard an mutierenden Eintrittspunkten; getrennte BCP GENERATE/BCP CLEANUP, indirekte Datenrechte, kein SUPER | Effektive Standard-BC-Rechte und Negativtests in SaaS |
| Ownership | Eindeutiger Table/SystemId-Schlüssel, Run ID, RecordId, ModifiedAt, zusätzlicher Nummernraum; Insert und Tracking gemeinsam | Unveränderte Zuordnung nach echten Inserts/Triggern |
| Cleanup | Item/UOM vor Customer vor Vendor; Metadaten-/Polymorphie-Referenzscan, RecordId-/GUID-Schutz, Standard Delete(true); keine eigenen Business-DeleteAll-Aufrufe | Referenzen, veränderte/fehlende/ersetzte Daten und fremde UOM verweigern |
| Transaktionen | Bounded worker, Run-Lock, CommitBehavior Error, Boolean Codeunit.Run, Fehlerstatus erst nach Rollback; erster Fehlversuch behält Startzeit | Unterbrechung, Resume, Rollback, Teil-Cleanup |
| Determinismus | Explizite Modulo-Permutation, genaue Quoten je 100er-Block, feste 100er-Item-Szenariowechsel; Run-Identität/Zeiten variieren | Reproduzierbare Werte unter identischem Setup |
| Standard-Seiteneffekte | Insert(false) vermeidet Contacts/Default Dimensions/Unit Group; eine explizit getrackte UOM; Kategorieattribute inklusive Eltern vor jedem Batch verweigert | Keine weiteren durch Subscriber erzeugten Datensätze |
| Performance | Maximal 5.000 Business-Zeilen je Batch; Kategorieprüfung einmal je Batch, Referenzscan einmal je Cleanup-Batch; kein Vollbestand im Speicher | Keine gemessene Durchsatz-/Skalierbarkeitszusage; Referenzscans können teuer sein |
| Szenarien | Vier IDs entsprechen produktiven Deep-Scan-Prüfungen; Generator schreibt keine Findings | Normale Scans und reale Check-Deltas |

Die Standard-Delete-Trigger enthalten selbst kaskadierende Löschungen. Deshalb
prüft der Generator fremde Referenzen vorher und behandelt eigene Item-UOM-Zeilen
explizit. Das ist kein Beweis für beliebige Drittanbieter-Codeunits/Subscribers.
Nur die isolierte, vorab geprüfte QA-App-Konfiguration verwenden; kein paralleler
Geschäftszugriff und nur ein Cleanup-Operator je Firma. Geänderte Tracking-Ziele
bleiben zur Untersuchung stehen; kein Force-Cleanup oder manuelles Zurücksetzen
von Ownership/Änderungszeiten.

Standardquellen zur erneuten Prüfung: Customer/Vendor/Item OnInsert, OnDelete,
validierte Konfigurationsfelder; Item Unit of Measure OnInsert; Item Category Code
OnValidate und Item Attribute Management.InheritAttributesFromItemCategory sowie
Item Attribute Value.LoadCategoryAttributesFactBoxData (einschließlich Eltern).
Letztere Prüfung führte zum zusätzlichen Category-Guard in diesem PR.

Assembly-Diagnose: Version 10.0.0.11 ist die im Fehler verlangte Assembly-Identität,
kein Nachweis der installierten .NET-Runtime-Version. Der unmittelbare Verbraucher
ist der BC-Administrations-/Response-Serialisierungspfad. BcContainerHelper bestimmt
dessen Sitzungsart; die AL-Apps enthalten diese .NET-Abhängigkeit nicht. Ein Defekt
im Generator oder der Lizenzlogik ist dafür nicht belegt. DLL-Dateibestand und die
exakte direkt referenzierende Binärdatei sind im alten Diagnosepaket nicht enthalten.
Runner-Image des Fehlerlaufs: windows-2022, 20260907.297.1. Ohne vorheriges Vergleichs-
image lässt sich kein konkretes Runner-Update als Auslöser behaupten.

## 13. Automated evidence snapshot (2026-09-16)

Reviewed AL/backend code commit: `573d6fcf37385acf26c876e49295afad47c56453`.
The subsequent evidence/warning-report update changes no AL or backend behavior.

| Gate | Actual result | Evidence |
|---|---|---|
| Generator contracts + extension regression | PASS: 42 (18 new + 24 existing) | [Run 35039164196](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35039164196) |
| Backend | PASS: 459; SKIP: 7 PostgreSQL-specific cases in this suite | [Pilot 35039164219](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35039164219) |
| Real PostgreSQL | PASS: 7, no failures/skips | Separate gate in the same Pilot run; overlapping tests, do not add totals |
| QA + product BC 27 compile/publish/sync/install | PASS | [AL run 35039164370](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35039164370) |
| QA CodeCop/PTECop | PASS: zero warnings/errors | Local compile-final.log; CI transcript |
| Product CodeCop/PTECop | PASS with 270 existing warnings, zero errors | Local compile-cops-final.log; CI transcript |
| AppSourceCop product baseline | EXPECTED BASELINE FAILURE: AS0051 x3, AS0084 x1, AS0092 x1 | Prior local probe; product source unchanged |
| Source uniqueness / GL | PASS: 109 objects; GL-01C 7; GL-01F | Contract workflow |
| Translations | PASS: 115 units in each language match generated source | Local catalog comparison and source contracts |
| AL behavior + SaaS generation/cleanup | PENDING, not executed | DEV procedure in section 9 |

The original warning summary missed GitHub annotation syntax and falsely displayed
zero warnings. The corrected parser accepts both raw compiler and annotation lines;
the archived transcript reproduces exactly 270 warnings. No gate is relaxed.

Historical 1.0.0.0 package (superseded by the runtime fix in section 14):
[bc-al-compile-output, artifact 10425301221](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35039164370/artifacts/10425301221).
The exact filename, local path and SHA256 are in the evidence JSON. Artifacts expire
after 14 days; retain the verified QA package locally. It contains the final AL
sources. Container install success is not SaaS, non-SUPER or generation evidence.

**Overall: AWAITING_MANUAL_BC_RUNTIME_EVIDENCE. No merge, production deployment or GO.**

## 14. Echter SaaS-Runtime-Fund: leerer New-Run-Dialog (1.0.0.0)

**Quelle: manueller Benutzer-Test in BC 27 SaaS, Firma BCS-PERF-DEV.**
Installation und Sandbox-/Firmen-Guard waren erfolgreich. Die Firma ist eine
bewusste CRONUS-DE-Kopie, deren vorhandene Daten als Fremddaten-Baseline erhalten
bleiben. QA-SOURCE-C, QA-SOURCE-V und QA-SOURCE-I sind bereits vorbereitet.

**Expected:** DEV / Seed 5001 / Rate 10 / Batch 1000 / Targets 6000, 2000, 12000.
**Actual:** Alle sieben an Rec gebundenen Felder waren leer und ausgegraut;
die drei variablengebundenen Quellenfelder funktionierten. Nach OK und korrekt
angezeigter Safety-Abfrage verweigerte CreateRun die ungültige Konfiguration.
Es entstand laut Benutzer kein gültiger Run. Dies ist ein echter Runtime-Fund,
kein Fehler der eingegebenen CRONUS-Konfiguration.

### Ursache und Korrektur

Die StandardDialog-Seite hat SourceTableTemporary=true. OnOpenPage setzte nur
Felder des Record-Puffers, fügte aber keinen temporären Datensatz ein. Damit
fehlte die SourceTable-Zeile für die gebundenen Felder. Die Variablenfelder für
CustomerNo/VendorNo/ItemNo benötigen diese Zeile nicht. Zusätzlich fehlten der
initiale SetProfile-Aufruf und OnValidate für Profilwechsel. Der Enum-Wert 0
ist bereits DEV; eine vermeintlich fehlende neue Enum-Option war nicht die Ursache.
Das nachgelagerte Management.Init kopiert die Eingabeoptionen aus TempRequest
zurück und setzt vor ValidateRun die Policy-Targets; es kann verlorene Seed-/Rate-/
Batch-Eingaben des Dialogs jedoch nicht ersetzen.

`BCP Policy.InitializeTemporaryRequest` verweigert echte/persistente und bereits
vorhandene Requests. Es initialisiert DEV, 5001, 10, DefaultBatchSize(), Schema 1,
ruft SetProfile und ValidateRun auf und **fügt eine temporäre Zeile ein**.
OnOpenPage ruft zuerst unverändert RequireSandbox und danach diesen Initializer.
Profil-OnValidate ruft ausschließlich die zentrale SetProfile-Policy auf; keine
Preset-Zahlen werden in der Page dupliziert. Nur bei Custom werden die drei
Zielzahlen editierbar. Seed, Rate und Batch bleiben konfigurierbar. Die temporäre
Identität wird vor Übergabe an CreateRun auf 0 gesetzt; echte Run-IDs entstehen
weiterhin ausschließlich im Management. Source-Snapshot, Kategorieprüfung,
Sicherheitsabfrage und alle bestehenden Guards bleiben erhalten.

App-Version **1.0.0.1**, unveränderte App-ID/Name/Publisher/Objekt-IDs und unveränderte
Tabellenstruktur. Kein Datenreset und kein neues Upgrade-Codeunit erforderlich.
Upgrade erfolgt durch normale BC-App-Synchronisierung/Datenaktualisierung.

### Automatisierte Regression

Acht AL-Tests: ursprüngliche Quoten-/Namespace-/Validierungsprüfungen, genaue
Preset-Zahlen, eingefügter und erneut gelesener temporärer Default-Request,
Profilwechsel mit Erhalt von Seed/Rate/Batch/Schema, Custom-Wechsel und Abweisung
persistenter/bereits vorhandener Requests. Ungültige Seeds, Schema, Batchgrößen,
Raten und Null-Targets bleiben abgewiesen. Die Page-Verknüpfung und Editable-Regeln
werden zusätzlich durch Source Contracts geschützt. Source Contracts allein
beweisen keine Webclient-Darstellung.

Die CI behält einen **fresh**-Installationspfad bei und ergänzt einen unabhängigen
**upgrade**-Pfad. Die alte QA-Version wird aus dem unveränderlichen Git-Commit
78dc59d gebaut; es besteht keine Abhängigkeit von ablaufenden Artifacts. Beide Pfade
müssen 1.0.0.1 installiert melden und alle acht AL-Tests ohne Skip ausführen.
Die AL-Tests prüfen Request-Verhalten, keine Umgehung des SaaS-Guards. Ein BC-
Container ersetzt weder SaaS-Webclient- noch No-SUPER-Nachweise. Der Upgrade-Pfad
prüft Schema-/Installationskompatibilität; er erzeugt keine synthetischen SaaS-Daten.

### Verifizierte CI-Nachweise für 1.0.0.1

Geprüfter Code-Commit: `89faeb721ed5488ee97c07a620c5184deba6f2e8`.

| Gate | Ergebnis |
| --- | --- |
| Generator-/bestehende Extension-Contracts | **44 PASS** (20 + 24) |
| [Pilot / vollständiges Backend](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35069195958) | **461 PASS, 7 SKIP**, 468 gesammelt |
| PostgreSQL im separaten Pilot-Gate | **7 PASS**, keine Skips; Überschneidung mit Gesamtsuite |
| [Contracts-Workflow](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35069195980) | **PASS** |
| [BC 27 Fresh und Upgrade](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35069195954) | **beide PASS** |
| AL-Verhaltenstests | **8/8 PASS nach Fresh, 8/8 PASS nach Upgrade**, keine Skips |
| QA CodeCop / PTECop | **PASS**, keine Warnungen/Fehler |
| Produkt CodeCop / PTECop | **PASS**, unverändert 270 Baseline-Warnungen |
| Lokales Produkt AppSourceCop | **EXPECTED BASELINE FAILURE**: 3× AS0051, 1× AS0084, 1× AS0092 |
| Echter SaaS-Dialog / Berechtigungen / DEV-/LARGE-Lauf | **PENDING**, keine Runtime-Freigabe |

Upgrade-Protokoll: erst Installation von QA 1.0.0.0 aus `78dc59d`, danach
`Upgrading BCSentinel Performance QA on tenant default` für 1.0.0.1. Die installierte
Version und alle acht AL-Tests werden anschließend geprüft. Das belegt die
Schema-/Installationskompatibilität, keine Migration erzeugter Geschäftsdaten.

**Neues Installationspaket:**
[bc-al-compile-output, Artifact 10436411621](https://github.com/danielwauer-maker/bcsentinel/actions/runs/35069195954/artifacts/10436411621)

Datei: `BCSentinel Analytics - Daniel Wauer_BCSentinel Performance QA_1.0.0.1.app`.
SHA256: `4268fcb76232038ea7de6c9fde5e2d425c01578c0806b10d4af0f9190deb87c4`.

Lokale Nachweise liegen unter `.build/ext-50-12a/runtime-fix-fresh-diagnostics/`,
`.build/ext-50-12a/runtime-fix-upgrade-diagnostics/` und
`.build/ext-50-12a/runtime-fix-pilot-ci/backend/`. Details und Paketpfad im Evidence-JSON.
Die CI verwendet BC `27.5.46862.54684/w1`, Plattform `27.0.54564.0` und
BcContainerHelper `6.1.18`. Kein Guard oder Installations-Gate wurde abgeschwächt.

### Retest exakt an der bisherigen Stelle

1. Neue **BCSentinel Performance QA 1.0.0.1** über Erweiterungsverwaltung hochladen
   und die vorhandene App regulär aktualisieren. **Nicht deinstallieren** und keine
   App-Daten löschen. Version 1.0.0.1 und unveränderte App-ID anschließend prüfen.
2. In **BCS-PERF-DEV** bleiben alle CRONUS-Daten und die drei vorhandenen Quellen.
   Als QA-Benutzer ohne SUPER neu anmelden bzw. den alten Dialog schließen.
3. **Performance-Läufe > Create** öffnen. Unmittelbar sichtbar: **DEV, 5001, 10,
   1000, 6000, 2000, 12000**. Profil/Seed/Rate/Batch müssen bedienbar sein. Die drei
   Targets sind beim Preset bewusst schreibgeschützt, aber nicht leer.
4. LARGE wählen: **150000 / 50000 / 300000**; XL: **600000 / 200000 / 1200000**;
   STRESS: **1500000 / 500000 / 3000000**. Nicht erzeugen. Custom wählen und
   Editierbarkeit der Ziele prüfen; anschließend wieder DEV wählen.
5. DEV, Seed 5001, Rate 10, Batch 1000 prüfen. **QA-SOURCE-C**, **QA-SOURCE-V** und
   **QA-SOURCE-I** auswählen. OK und die Safety-Abfrage bewusst bestätigen.
6. Erwartet: genau ein **Pending**-Run mit Ziel **20.000**, Zählern 0, korrekten
   Optionen und Schema 1. Run ID und Screenshots der Defaults/des Pending-Runs sichern.
   Erst mit diesem tatsächlichen SaaS-Ergebnis wird RUNTIME-001 auf PASS gesetzt.
7. Danach den eigentlichen DEV-Test aus Abschnitt 9 fortsetzen. LARGE bleibt bis
   zur DEV- und Sicherheitsabnahme gesperrt.

**Runtime-Fund bleibt OPEN_RETEST_REQUIRED. Gesamtstatus:
AWAITING_MANUAL_BC_RUNTIME_EVIDENCE.** Code-Fix oder Container-Tests sind kein
SaaS-Retest-PASS. Historische Nachweise aus Abschnitt 13 gelten für 1.0.0.0;
maßgeblich für das neue Paket ist der aktuelle Runtime-Fix-Eintrag im Evidence-JSON.

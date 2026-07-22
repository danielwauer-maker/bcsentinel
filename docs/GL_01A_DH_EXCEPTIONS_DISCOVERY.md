# GL-01A DH Exceptions Discovery

**Stand:** 22. Juli 2026

**Baseline:** `staging@5177b8e969a0cc1e0d7fad1bec4fdcbe3dae8c55`
**Entscheidungsstatus:** Discovery abgeschlossen; irreversible fachliche Entscheidungen offen

## 1. Ergebnis in einem Satz

BCSentinel besitzt bereits eine lokale, scorewirksame BC-Suppression für Customer, Vendor und Item, aber noch keinen vollständigen, normativ abgesicherten DH-Ausnahmen-Domain-Contract. Die vorhandenen Fragmente müssen zunächst eingefroren, fachlich klassifiziert und mit Rohscore-/Disclosure-Sicherheiten versehen werden.

## 2. Vorhandene Implementierungsfragmente

| Layer | Vorhanden | Bewertung |
|---|---|---|
| BC-Datenmodell | Tabelle 53150 `DH Issue Exception` | PARTIAL: Record/Check, Active, Reason, Created/Deactivated vorhanden; Typ, Frist, Review, Version fehlen |
| BC-Audit | Tabelle 53151 `DH Issue Action Log` | PARTIAL: Actions `EXCLUDED`, `INCLUDED`, `CORRECTED`; kein normativer Ereignisvertrag oder Unveränderbarkeitsnachweis |
| Management | Codeunit 53152 `DH Exception Mgt.` | PARTIAL: Add/Reactivate, deactivate, corrected log; keine Genehmigung, Expiry, Concurrency oder Sync |
| BC-UI | Page 53153, FactBox 53154, Customer/Vendor/Item Card/List Extensions | PARTIAL: sichtbar und bedienbar; Grund teils automatisch/hartcodiert, keine geführte Typ-/Fristwahl |
| Scan | `DH Deep Scan Runner` | WIRKSAM: mindestens 42 direkte Customer/Vendor/Item-Prüfpfade plus Duplicate-Helfer berücksichtigen aktive Ausnahmen |
| Score/Finding | Datensätze werden vor `AddCountFinding` nicht gezählt | KRITISCH: Ausnahme kann Score erhöhen und Findings reduzieren; keine Rohsicht/Disclosure |
| Permission Sets | R bzw. RIMD und Page Execute verteilt | PARTIAL: technische Rechte vorhanden, fachliche Rollenmatrix fehlt |
| Backend/API/Migration | kein Exception-Model/Router/Service/Test gefunden | NOT IMPLEMENTED |
| Dashboard/Analytics | keine Ausnahmeansicht/Reconciliation gefunden | NOT IMPLEMENTED |
| Executive Report/PDF | keine Ausnahmeoffenlegung gefunden | NOT IMPLEMENTED |
| Tests | keine AL-Testapp und keine Exceptions-E2E-Tests gefunden | EVIDENCE MISSING |

Die BC-Tabellen besitzen keine `DataPerCompany = false`-Eigenschaft und verwenden damit den Business-Central-Standard für companybezogene Daten. Das ist ein plausibler technischer Isolationsbaustein, aber kein ausreichender Cross-Company-/Tenant-Testnachweis.

## 3. Fachlich ungeklärte Fragen

- Ist die Ausnahme an einen einzelnen Datensatz, ein Finding-Vorkommen oder eine Check-/Record-Kombination gebunden?
- Bleibt sie über Scans hinweg wirksam, und wie wird ein gelöschter/neu angelegter Datensatz behandelt?
- Welche Ausnahmegründe sind zulässig und welche benötigen Genehmigung?
- Welche Typen sind zeitlich befristet, wann erfolgt Re-Check, wer ist Owner?
- Bedeutet `CORRECTED` wirklich fachlich behoben oder lediglich manuell dokumentiert?
- Darf der Hauptscore bereinigt werden? Müssen Rohscore und bereinigter Score parallel bestehen?
- Wie erscheinen ausgenommene Risiken in Findings, Dashboard, Analytics, Executive Report und PDF?
- Wie wirkt eine neue Check-Version auf bestehende Ausnahmen?
- Was geschieht offline oder bei nicht erreichbarem Backend?
- Wie werden bestehende aktive Datensätze ohne Typ/Frist sicher migriert?

## 4. Mindest-Domain-Contract

Ein späterer Vertrag sollte mindestens folgende Konzepte eindeutig benennen, ohne die konkrete Persistenz vorwegzunehmen:

| Konzept | Mindestanforderung |
|---|---|
| Identity | stabile Exception-ID; Tenant; Company; Check-ID; Check-Version/Kompatibilität; Record-Typ und stabile Record-ID |
| Classification | accepted, temporary, permanent, false positive, not assessable, review required; resolved/corrected getrennt |
| Lifecycle | draft/requested, active, expired, revoked; klare erlaubte Übergänge |
| Reason | strukturierter Reason Code plus verpflichtender Kommentar |
| Validity | valid from/until, next review at, optional owner/approver |
| Audit | Actor, UTC-Zeit, vorher/nachher, Quelle, Correlation/Request ID; kein stilles Überschreiben |
| Score | Rohscore unveränderlich nachvollziehbar; bereinigte Wirkung explizit und reconciliierbar |
| Disclosure | Anzahl/Einfluss aktiver Ausnahmen in BC, Dashboard und Report sichtbar |
| Isolation | Tenant und Company auf jedem Lese-/Schreibpfad erzwungen |
| Idempotency | wiederholte Requests erzeugen keine Duplikate oder widersprüchliche Ereignisse |

## 5. Datenmodelloptionen

### Option A – BC bleibt alleinige Autorität

Vorteile: geringer Umbau, natürliche Company-Isolation, lokale Scanverfügbarkeit.

Nachteile: Dashboard/Report benötigen Synchronisation; zentrale Audit-/Supportsicht schwach; Konflikte und Multi-Company schwer.
Bewertung: für einen reinen BC-Report denkbar, für das bestehende SaaS-Dashboard nicht nachhaltig.

### Option B – Backend ist alleinige Autorität

Vorteile: einheitliche API, Dashboard/Report/Audit, Tenant-/Company-Policy zentral.

Nachteile: lokale Scans werden netzabhängig; Offline-/Timeout-Verhalten kann Score inkonsistent machen; Migration komplexer.
Bewertung: nur mit klarer Fail-closed-/Snapshot-Strategie vertretbar.

### Option C – Zentraler Backend-Vertrag mit versioniertem BC-Snapshot

Vorteile: zentrale Wahrheit für Anzeige/Audit, deterministischer lokaler Scan über einen versionierten Snapshot, Reconciliation möglich.

Nachteile: Sync-, Staleness- und Konfliktregeln müssen explizit gebaut und getestet werden.
Bewertung: nachhaltigste Enterprise-Richtung, aber in kleine Pilotinkremente zu zerlegen.

## 6. Founder Decision Matrix

| Entscheidung | A | B | C / Empfehlung | Entscheidung vor |
|---|---|---|---|---|
| Scoreanzeige | nur bereinigt | Ausnahme ändert Score nie | **Rohscore primär; bereinigte Sicht separat, mit Delta und Count** | GL-01C |
| Persistenzautorität | BC-only | Backend-only | **Backend-Vertrag + versionierter BC-Snapshot** | GL-01C |
| Legacy-Ausnahmen | automatisch accepted | löschen | **`legacy_unclassified`, sichtbar und reviewpflichtig** | Migration |
| Dauerhafte Ausnahme | ohne Frist | verboten | **zulässig mit Genehmigung und Review-Datum** | GL-01C |
| Behoben | Ausnahmegrund | Finding-Status | **separater Remediation-/Finding-Status** | Domain Contract |
| Netzfehler beim Scan | alte Daten still nutzen | alle Ausnahmen ignorieren | **bekannten Snapshot mit Alter offenlegen; ohne validen Snapshot fail-safe gemäß Pilotentscheidung** | Scan-Integration |

Die Empfehlungen sind keine normative Festlegung, solange das Product System nicht verfügbar bzw. ergänzt ist. Founder/Product Owner muss die Matrix signieren.

## 7. API-Auswirkungen

Nach Domain-Entscheidung wird voraussichtlich benötigt:

- tenant- und companygebundene List/Get/Create/Transition-Endpunkte;
- idempotenter Command-Key und optimistische Version für Änderungen;
- serverseitig kontrollierte Statusübergänge und Rollenprüfung;
- Snapshot-/Delta-Endpunkt für die BC Scan Engine;
- Reconciliation-/Audit-Endpunkt für Dashboard und Support;
- keine Änderung bestehender Scan-API-Verträge ohne versionierte, rückwärtskompatible Erweiterung;
- strukturierte Fehlercodes für Conflict, Stale Version, Forbidden, Expired und Invalid Transition.

## 8. BC-User-Flow

Empfohlener Pilotfluss:

1. User öffnet ein betroffenes Finding/Record.
2. Aktion „Ausnahme beantragen“ zeigt Check, Record, aktuelle Wirkung und Pflichtfelder Typ/Grund/Gültigkeit.
3. Für dauerhafte oder scorewirksame Ausnahmen ist eine separate Genehmigung erforderlich.
4. Die aktive Ausnahme ist am Record und am Finding sichtbar; Ablauf/Review werden hervorgehoben.
5. „Widerrufen“ erzeugt ein Ereignis, löscht nicht die Historie.
6. „Als behoben markieren“ bleibt getrennt und löst beim nächsten Scan eine fachliche Revalidierung aus.
7. Bei veraltetem/fehlendem Snapshot wird kein stiller Erfolg angezeigt.

Die vorhandene Page/FactBox kann wiederverwendet werden, ihre heutigen hartcodierten englischen Gründe und das einfache `Active`-Modell reichen nicht als Ziel-UX.

## 9. Berechtigungsmodell

Mindestens zu trennen:

- Viewer: lesen, Wirkung nachvollziehen;
- Operator: temporäre Ausnahme beantragen/widerrufen im erlaubten Umfang;
- Approver/Admin: dauerhafte/scorewirksame Ausnahme genehmigen;
- Auditor/Support: tenantgebundene Historie lesen, keine fachliche Änderung.

Tests müssen fehlende Rechte, falsche Company, manipulierte Record-/Check-ID, fremden Tenant und direkte API-Aufrufe abdecken. `RIMD` auf der Tabelle allein ist kein fachliches Autorisierungsmodell.

## 10. Isolation und Audit

- Tenant- und Company-ID müssen Teil jedes Backend-Schlüssels und Filters sein.
- Record SystemId darf nie ohne Company-Kontext aufgelöst werden.
- Auditereignisse sind append-only; Korrekturen erfolgen durch neue Ereignisse.
- Actor, UTC-Zeit, Quelle (BC/Dashboard/API/System), Request-/Correlation-ID und alte/neue Version werden protokolliert.
- Supportzugriff benötigt explizite Rolle und Audit.
- Retention und Export müssen vor Pilot vertraglich dokumentiert sein.

## 11. Scan-, Score- und Reporting-Auswirkung

Aktuell wird der betroffene Datensatz vor der Finding-Zählung übersprungen. Dadurch sinkt `AffectedCount`, gegebenenfalls entfällt das Finding, und der Score verliert Penalty Points. Das ist funktional wirksam, aber nicht transparent.

Empfohlene Zielmessung je Check:

- `raw_affected_count`;
- `excepted_count` nach Typ;
- `effective_affected_count`;
- `raw_penalty` und `effective_penalty`;
- verwendete Exception-Snapshot-Version und Zeit;
- Disclosure im Report: Anzahl, Delta, ablaufende/reviewpflichtige Ausnahmen.

Executive Report und Dashboard dürfen keine „gesunde“ Lage zeigen, ohne aktive Ausnahmen und ihre Scorewirkung offenzulegen. Financial Impact darf nicht still auf null fallen; mindestens Rohwert, bereinigte Sicht und Begründung müssen reconciliierbar sein.

## 12. Migrationsbedarf

Für Backend-Modelle ist nach Entscheidung eine neue Alembic-Revision erforderlich. Die existierende Migration `0027` betrifft den Check Catalog, nicht Exceptions.

BC-seitig dürfen vorhandene aktive Ausnahmen nicht still umklassifiziert oder gelöscht werden. Empfohlener Ablauf:

1. Inventar/Backup und Count pro Company;
2. neue Felder/Mapping rückwärtskompatibel;
3. Legacy-Einträge als `legacy_unclassified` und reviewpflichtig;
4. idempotente Synchronisation;
5. Reconciliation-Report;
6. erst nach Abnahme Nutzung im neuen Scorepfad.

## 13. Testbedarf

- Domain-Transition- und Validierungs-Unit-Tests;
- API-Tenant-/Company-/Role-Negativtests;
- Idempotenz, Concurrency und Stale-Version;
- Migration Upgrade/Downgrade nach Projektstandard und Legacy-Reconciliation;
- AL-Testapp für CRUD/Transitions, Company-Isolation und Snapshot-Verhalten;
- Contract-Tests zwischen Backend und AL;
- Golden Dataset: mit/ohne Ausnahme, Ablauf, Widerruf, Check-Version-Wechsel;
- Dashboard-/Report-Reconciliation;
- BC-Sandbox-CAT mit Rollen ohne `SUPER`;
- Failure Tests für Timeout, stale snapshot und teilweise Synchronisation.

## 14. Risiken

Höchste Risiken sind Scoremanipulation, unsichtbare Risikounterdrückung, Cross-Company-Fehlzuordnung, dauerhafte Ausnahmen ohne Review, Legacy-Fehlklassifikation und divergierende Wahrheiten zwischen BC, Dashboard und Report. Jede Implementierungsstufe benötigt deshalb ein eigenes Fail-safe- und Rollback-Kriterium.

## 15. Empfohlene Implementierungsreihenfolge

1. **GL-01B – Domain Contract & Safety Freeze:** Entscheidungen, Zustandsautomat, Score-/Disclosure-Vertrag, Legacy-Regel, Rollenmatrix, Testvektoren.
2. **GL-01C1 – Backend Persistence & Audit:** Tabellen/Migration/Service ohne UI-Verbraucher.
3. **GL-01C2 – Versioned API & Snapshot:** sichere Commands, Query, Snapshot, Contract-Tests.
4. **GL-01D1 – BC Migration & Client:** Legacy-Mapping, Secret-/Retry-/Idempotenzpfad, zunächst Feature-flagged bzw. nicht scorewirksam.
5. **GL-01D2 – BC Guided UX & Permissions:** Beantragen, Genehmigen, Widerrufen, Review; AL-Tests.
6. **GL-01E1 – Scan/Score Integration:** Roh-/bereinigte Messung und Golden Tests.
7. **GL-01E2 – Dashboard/Report Disclosure:** Reconciliation und End-to-End-CAT.

Erst nach erfolgreicher Reconciliation darf der neue Ausnahmevertrag Pilotdaten beeinflussen.

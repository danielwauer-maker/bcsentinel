# GL-01 Product Completion Baseline

**Stand:** 22. Juli 2026

**Baseline:** Branch `staging`, Commit `5177b8e969a0cc1e0d7fad1bec4fdcbe3dae8c55`

**Zweck:** belastbare Delivery-Baseline für einen streng betreuten Design-Partner-Pilot
**Scope dieser Arbeit:** Analyse und Planung; keine Produktimplementierung

## 1. Executive Summary

BCSentinel besitzt einen realen, differenzierten Produktkern. Die im Executive Assessment getroffene Entscheidung bleibt gültig: **betreuter Pilot und erster zahlender Design-Partner unter Bedingungen: ja; Public Go-Live und Enterprise-Rollout: nein**.

GL-01 ist nicht „fast fertig“, sondern in zwei Klassen zu trennen:

1. Mehrere Customer-Journey- und Access-Themen wurden nach dem Executive Assessment technisch deutlich verbessert. Registrierung, Multi-Tenant-Dashboard, einheitlicher Scanstart, Background-Recovery und permanenter Zugriff auf das kostenlose Ergebnis sind im Code und durch fokussierte Tests belegt. Echte BC-Sandbox-, SMTP- und Pilotabnahmen fehlen jedoch.
2. DH-Ausnahmen sind nicht nur geplant. In der BC Extension existiert bereits ein lokales Ausnahmemodell, das mindestens 42 Kunden-, Lieferanten- und Artikelprüfungen vor der Aggregation ausfiltert und damit Findings und Score beeinflusst. Der fachliche Vertrag, Gültigkeit, Statussemantik, Check-Versionierung, Backend/API, Dashboard-/Report-Transparenz und automatisierte AL-/End-to-End-Tests fehlen. Das ist ein Pilotrisiko und muss vor einer Erweiterung normativ geklärt werden.

Empfehlung: **GL-01B als kleiner Domain-Contract- und Safety-Sprint zuerst durchführen.** Keine weitere Ausnahmefunktion implementieren, bevor Founder/Product Owner die Score- und Offenlegungssemantik entschieden hat. Danach vorhandene Fragmente kontrolliert konsolidieren. Release Safety, fachliche Golden-Result-Validierung und ein fester Release Candidate bleiben eigenständige Pilot-Gates und dürfen nicht durch UI-Fertigstellung ersetzt werden.

## 2. Authority und Evidenzgrenzen

| Priorität | Quelle | Befund |
|---|---|---|
| 1 | Product System | In diesem Repository nicht direkt vorhanden. Executive-Unterlagen referenzieren extern den Commit `449702963f500096bce1837f4da69b84db7f99d0`; das Objekt ist lokal nicht auflösbar. Normative Detailaussagen zu DH-Ausnahmen sind daher **EVIDENCE MISSING**. |
| 2 | Product Master Book | Vorhanden und intern validierbar; beschreibt den Stand vom 20. Juli 2026. Einzelne Kennzahlen sind gegenüber HEAD veraltet. |
| 3 | Executive Assessments/Risk Register | Konsistent: Pilot nur unter Bedingungen; Public/Enterprise nicht freigegeben. |
| 4 | Repository und Tests | Maßgeblich für technische Verifikation am aktuellen HEAD. |
| 5 | Git-Historie | Vier Commits nach dem Assessment-Dokument-Commit enthalten zusätzliche GL-01F-/Scan-Fixes; Commit-Betreffs sind nicht aussagekräftig (`Commits`). |
| 6 | Arbeitsbaum | Zu Analysebeginn sauber; keine Paralleländerungen vorhanden. |

Widerspruch: Das Master Book nennt 25 Migrationen, 88 AL-Objekte und 224 Testfunktionen/27 Testdateien. Am aktuellen HEAD wurden 27 Migrationen, 90 AL-Objektdeklarationen sowie 281 Backend-Testfunktionen in 32 Testdateien gezählt. Die Baseline verwendet deshalb aktuelle Repository-Zahlen und behandelt das Master Book als zeitlich älteren Snapshot.

## 3. Git- und Repository-Stand

| Merkmal | Verifizierter Stand |
|---|---|
| Branch | `staging` |
| HEAD | `5177b8e969a0cc1e0d7fad1bec4fdcbe3dae8c55` |
| HEAD-Zeit | `2026-07-22T16:57:15+02:00` |
| Letzter ermittelbarer Assessment-Dokument-Commit | `807626eab402b295ddf4b2923b9d301482961fa6` (22. Juli 2026, 00:25:50 +02:00) |
| Arbeitsbaum zu Analysebeginn | sauber; keine geänderten oder untracked Dateien |
| Relevante Tags | keine Tags aufgelistet |
| Backend-Version | `0.7.0` in `backend/app/main.py` |
| BC-App-Version | `1.0.2.11` in `bc-extension/app.json` |
| BC-Ziel | Platform/Application `27.0.0.0`, Runtime `16.0` |
| Migrationen | 27 Revisionen, `0001` bis `0027_enterprise_check_catalog.py` |
| Backend-Tests | 32 Dateien, 281 Testfunktionen |
| AL-Tests | kein AL-Testobjekt nachgewiesen |
| AL-Quelle | 85 `.al`-Dateien, 90 Objektdeklarationen |
| Übersetzung | `BCSentinel.g.xlf` und `BCSentinel.de-DE.xlf` vorhanden |
| CI | `.github/workflows/deploy.yml`: Deployment und Health Checks, aber kein vorgelagertes Backend-/AL-Testgate |
| Release-Artefakte | `.build/BCSentinel-GL01F-FIX01.app`, `.build/BCSentinel-GL01F-FIX02A.app`; nicht als signierter/fixierter RC nachgewiesen |
| Repository-Einstieg | Root-`README.md` ist leer |

Die vorhandenen `.app`-Dateien sind Build-Artefakte einzelner Fixes. Ohne Tag, Manifest, Signatur, vollständige Testakte und Sandbox-Abnahme sind sie keine freigegebenen Release Candidates.

## 4. Scope von GL-01

GL-01 schließt die Produktfunktion und die Pilotverständlichkeit für **einen betreuten, vertraglich begrenzten Design-Partner**. Enthalten sind:

- sicherer fachlicher Vertrag und konsistente End-to-End-Behandlung von DH-Ausnahmen;
- Abschluss und Runtime-Abnahme von Registrierung, Welcome/Invite, erstem Login und Dashboard-Zugriff;
- verständliche Setup Experience in Business Central;
- Pilot-UX-Polish in BC und Dashboard;
- vollständige Pilotdokumentation einschließlich Known Issues und Grenzen;
- ein reproduzierbarer, eindeutig identifizierter Product-Completion Release Candidate.

Nicht in GL-01 gehören der breite Self-Service-Marktstart, vollständige Public-Customer-Journey, Enterprise-HA/Multi-Host, AppSource, organisatorische Founder-Entkopplung oder eine allgemeine Plattform-Neuarchitektur. Pilotkritische Release-, Recovery- und fachliche Validierungsgates müssen trotzdem vor GL-04/GL-05 geschlossen werden.

## 5. Product-Completion-Inventur

### 5.1 Bewertungsmatrix

| Thema | Status | Technische Evidenz | Fachliche/Runtime-Evidenz | Pilotkritikalität | Nächster Schritt |
|---|---|---|---|---|---|
| Executive-Entscheidungsbasis | COMPLETE | Executive-Dokumente konsistent | Pilotbedingungen klar benannt | hoch | Als Gate-Katalog weiterverwenden |
| Einheitlicher manueller Scanstart | COMPLETE, EVIDENCE LIMITED | `DHDeepScanMgt`, GL-01A-2-Vertragstests; früher dokumentierter AL-Build | echte BC-Sandbox-Interaktion offen | hoch | in Sandbox-Akzeptanz aufnehmen |
| Background-Scan/Orphan-Recovery | COMPLETE, EVIDENCE LIMITED | Lifecycle-/Recovery-Code und fokussierte Tests | Scheduler-Nachlauf in BC-Sandbox offen | hoch | End-to-End in Pilot-Sandbox |
| Kostenloser Erstscan und permanenter Ergebniszugriff | COMPLETE, EVIDENCE LIMITED | Access-Service, BC-Mapping, Regressionstests | historischer Tenant und BC-Sandbox offen | hoch | Snapshot-/UI-CAT durchführen |
| Registrierung/Identity-Bindung | COMPLETE, EVIDENCE LIMITED | stabile BC-Identity, idempotentes Upsert, Token-Hashing, strukturierte Fehler | reale Umgebung/Rate/Reset-Pfade nicht vollständig pilotabgenommen | hoch | Sandbox-CAT mit Wiederholung |
| Dashboard Invite/Welcome-Mail | COMPLETE, EVIDENCE LIMITED | Invite-Token gehasht, 7 Tage TTL, DE/EN-Template, Mailstatus | SMTP-Zustellung real nicht nachgewiesen | hoch | SMTP-/Mail-CAT und Recovery |
| Erster Login und Session | COMPLETE, EVIDENCE LIMITED | Invite-Aktivierung, HttpOnly Session Cookie, Logout, Tenant-Switch mit Rotation | Browser-/Pilotabnahme offen | hoch | Browser-CAT inkl. Manipulation |
| Mehrere Tenant-Mitgliedschaften | COMPLETE, EVIDENCE LIMITED | Membership-Modell und Tests für Auswahl, Wechsel und Manipulationsschutz | UI-Verständlichkeit real offen | mittel/hoch | Usability-CAT |
| Dashboard-Link/Embed | PARTIAL | tenant-/company-/scope-gebundener Kurzzeittoken, Cookie-Austausch | Token wird initial weiterhin in URL transportiert; Log-Redaction offen | mittel | für Pilot dokumentieren/härten; Public-Gate |
| Lizenz-/Access-Snapshot | COMPLETE, EVIDENCE LIMITED | getrennte Capabilities, Snapshot-Metadaten, Permanent-Free-Status | reale Staging-/BC-Konsistenz offen | hoch | Matrix-CAT Free/Full/Validation/Monitoring |
| DH-Ausnahmen – lokales BC-Modell | PARTIAL | Tabellen 53150/53151, Management-Codeunit, Liste/FactBox, Card/List Extensions | kein normativer Domain Contract | sehr hoch | GL-01B Entscheidung und Safety Contract |
| DH-Ausnahmen – Scan/Score | PARTIAL | 42 direkte Prüfpfade filtern betroffene Datensätze vor Finding-/Score-Aggregation | keine Offenlegung, kein Golden-Result-Nachweis | sehr hoch | Semantik festlegen, Baseline-/Golden Tests |
| DH-Ausnahmen – Status/Gültigkeit | NOT IMPLEMENTED | nur `Active` Boolean; Created/Deactivated Metadaten | keine Typen, Frist, Review, Check-Version | sehr hoch | Statusmodell entscheiden |
| DH-Ausnahmen – Audit/Widerruf | PARTIAL | append-artiges Action Log für `EXCLUDED`, `INCLUDED`, `CORRECTED`; kein Delete in UI | kein vollständiger Auditvertrag/Backend-Beleg | hoch | Ereignismodell und Retention definieren |
| DH-Ausnahmen – Tenant/Company-Isolation | COMPLETE, EVIDENCE LIMITED | BC-Tabellen sind standardmäßig companybezogen; Tenant-Isolation durch BC-Umgebung | kein expliziter Cross-Company-/Cross-Tenant-Test; Backend fehlt | sehr hoch | Isolationstest und Contract |
| DH-Ausnahmen – Berechtigung | PARTIAL | Permission Sets enthalten R bzw. RIMD; Page Execute vorhanden | Rollenmatrix/Least-Privilege-CAT fehlt | hoch | Rollenvertrag und Negativtests |
| DH-Ausnahmen – Backend/API | NOT IMPLEMENTED | kein Model, keine Migration, kein Router/Service/Test gefunden | keine zentrale Quelle | hoch | Zielarchitektur nach GL-01B |
| DH-Ausnahmen – Dashboard/Report | NOT IMPLEMENTED | keine Ausnahmeansicht oder Disclosure im Backend/Report nachgewiesen | Risiken könnten unsichtbar werden | sehr hoch | offenlegen und reconciliieren |
| Enterprise Check Catalog | COMPLETE, EVIDENCE LIMITED | Migration `0027`, Admin-/Catalog-Code und Tests vorhanden | operative Pflege/Upgrade in Staging nicht hier erneut abgenommen | mittel | RC-Schema-/Inhaltsvalidierung |
| Setup Informationsarchitektur | PARTIAL | Statusgruppen, Registration Preparation, Aktionen, Advanced Information vorhanden | Seite ist sehr umfangreich; Pilotverständlichkeit nicht beobachtet | hoch | GL-01G Task-basiertes Review |
| Setup Captions/Tooltips/XLF | COMPLETE, EVIDENCE LIMITED | DE-XLF vorhanden; Localization Validator erfolgreich | visuelle BC-Sandbox-Abnahme offen; einzelne Ausnahmetexte hartcodiert/englisch | mittel/hoch | CAT plus gezielter Restkatalog |
| Access-/Capability-Anzeige | COMPLETE, EVIDENCE LIMITED | getrennte Dashboard/Issues/Report-Felder und Snapshot-Diagnostik | Endnutzerverständlichkeit offen | hoch | Pilot-Matrix testen |
| Empty/Loading/Error/Confirmation States | PARTIAL | mehrere gezielte GL-Audits und UI-Zustände vorhanden | kein vollständiger Journey-übergreifender CAT | mittel/hoch | GL-01H Journey-Matrix |
| Pilotdokumentation | PARTIAL | Runbooks, Release-/Acceptance-Checklisten, DPA-Checkliste vorhanden | kein konsolidiertes Kundenset; Ausnahmen/aktuelle Known Issues unvollständig | hoch | GL-01I Paket erstellen |
| Release Candidate | NOT IMPLEMENTED | Versionen/Builds vorhanden | kein Tag, fixer Manifestbezug, vollständiges Gate oder Sandbox-Protokoll | sehr hoch | GL-01J reproduzierbaren RC bauen |
| Fachliche Golden-Result-Validierung | EVIDENCE MISSING | Scanregeln vorhanden | kein freigegebenes Golden Dataset mit erwarteten Score/Severity/Impact-Ergebnissen | sehr hoch | vor Pilot-Freigabe schließen |
| CI-Testgate | PARTIAL | Deploy-Workflow und Health Check vorhanden | Deploy kann ohne Backend-/AL-Testgate starten | sehr hoch | spätestens GL-03, für Pilot als manuelles RC-Gate kompensieren |
| Backup/Restore/Rollback | PARTIAL | Dokumente/Compose- und Deploy-Pfade vorhanden | kein Restore-/Rollback-Drill-Nachweis | sehr hoch | GL-03 und GL-04 Gate |
| Public Self-Service/Legal/Stripe Live | OUT OF GL-01 SCOPE | Teilkomponenten vorhanden | Public-Nachweise fehlen | nicht Pilotkern | GL-02/GL-06 |
| Enterprise HA/AppSource/Scale | OUT OF GL-01 SCOPE | keine ausreichende Gesamt-Evidenz | Enterprise-Freigabe explizit nein | nicht für ersten Pilot | GL-07 |

### 5.2 DH-Ausnahmen: tatsächlich vorhandener Stand

Vorhanden sind:

- `DH Issue Exception` mit Record-Bezug, Issue Code, `Active`, Grund sowie Created/Deactivated User und Zeit;
- `DH Issue Action Log` mit Action Type, Kommentar, User und Zeit;
- Management-Codeunit zum Anlegen/Reaktivieren, Deaktivieren und Protokollieren von „korrigiert“;
- Listen-/Kartenaktionen und FactBox für Customer, Vendor und Item;
- Ausfilterung in 16 Customer-, 16 Vendor- und 10 Item-Checks sowie in Duplicate-Zählungen;
- Berechtigungsfragmente in mehreren Permission Sets.

Nicht vorhanden oder nicht belegt sind:

- fachliche Typen wie akzeptiert, temporär, dauerhaft, falsch positiv, nicht prüfbar, erneut prüfen;
- Valid-from/Valid-until, Review-/Expiry-Mechanik und Check-Version-Bindung;
- konsistentes Lösch-/Widerrufsmodell und unveränderbarer vollständiger Audit-Trail;
- Backend-Persistenz/API und Synchronisationskonfliktmodell;
- Dashboard-, Analytics- und Report-Disclosure;
- explizite Erklärung, ob Score roh, bereinigt oder beides angezeigt wird;
- AL-Unit-, Cross-Company-, Cross-Tenant-, Upgrade- und Golden-Result-Tests.

Die aktuelle Implementierung ist deshalb **kein abgeschlossenes Exceptions Management**. Sie ist ein wirksames, aber fachlich unterdefiniertes Suppression-Fragment.

## 6. Abhängigkeiten

1. Product-System-/Founder-Entscheidung zur Ausnahme- und Scoresemantik.
2. Stabiler Check-Identifier und Check-Version-/Catalog-Bezug.
3. Festlegung der autoritativen Persistenz und Offline-/Sync-Grenzen zwischen BC und Backend.
4. Rollen- und Company-/Tenant-Isolationsvertrag.
5. Golden Dataset für Rohscore, bereinigten Score, sichtbare Findings und Report-Disclosure.
6. Erst danach BC UX, API, Dashboard und Report in sicheren Schritten.
7. Product-Completion RC erst nach Customer-Journey-CAT, Dokumentation und Pilot-Gates.

## 7. Risiken

| Risiko | Wirkung | Einstufung | Behandlung |
|---|---|---|---|
| stille Score-Erhöhung durch Ausnahme | fachliche Irreführung | kritisch | Roh-/bereinigte Werte und Disclosure entscheiden/testen |
| dauerhafte Unterdrückung ohne Review | Risiken verschwinden | hoch | Typ, Frist, Owner, Review und Widerruf |
| Ausnahme trifft falsche Check-Version | falsche Ergebnisse nach Update | hoch | Check-ID plus Versions-/Compatibility-Regel |
| lokale BC-only-Wahrheit | Dashboard/Report widersprechen BC | kritisch | Autorität und Sync-Vertrag definieren |
| ungetestete Isolation/Berechtigung | Daten-/Kontrollverletzung | kritisch | Cross-Company/Tenant- und Least-Privilege-Tests |
| erfolgreiche Unit-Tests werden als Pilotnachweis missverstanden | falsche Freigabe | hoch | Sandbox-/SMTP-/Browser-/Golden-CAT separat signieren |
| Deploy ohne Testgate | Regression erreicht Umgebung | kritisch | manueller RC-Gate kurzfristig, CI-Testgate GL-03 |
| veraltete beschreibende Dokumentation | falsche Planung | mittel | Master Book nach Delivery aktualisieren, nicht in diesem Sprint |

## 8. Offene Entscheidungen

Vor GL-01C sind mindestens folgende Founder/Product-Entscheidungen erforderlich:

1. Darf eine Ausnahme den offiziellen Health Score verändern? Empfehlung: Rohscore unverändert bewahren, bereinigte Sicht separat und vollständig offengelegt.
2. Welche Status-/Grundtypen sind für v1 zwingend? Empfehlung: `accepted`, `temporary`, `permanent`, `false_positive`, `not_assessable`, `review_required`; „behoben“ bleibt Finding-/Remediation-Status, keine Ausnahme.
3. Welche Typen benötigen zwingend ein Ablaufdatum? Empfehlung: temporär und review-required; dauerhafte Ausnahme mit periodischem Review.
4. Ist Backend oder BC autoritativ? Empfehlung: zentraler Backend-Vertrag für konsistente Dashboard-/Report-Sicht; BC als transaktionaler Client mit sicherer Idempotenz. Eine Offline-Strategie ist separat zu entscheiden.
5. Wie werden alte aktive BC-Ausnahmen migriert? Empfehlung: nicht automatisch als fachlich „akzeptiert“ klassifizieren; als `legacy_unclassified` sperren/kennzeichnen und manuell reviewen.
6. Wer darf Ausnahmen anlegen, genehmigen, widerrufen und reporten? Empfehlung: Operator beantragt, Administrator genehmigt dauerhafte/scorewirksame Ausnahmen.

## 9. Empfehlung

Die strategische GL-01A–J-Reihenfolge bleibt grundsätzlich sinnvoll, wird aber evidenzbasiert präzisiert:

- GL-01B ist ein **Domain Contract & Safety Freeze**, nicht sofort Backendbau.
- GL-01C–E konsolidieren DH-Ausnahmen in kleinen, einzeln testbaren Grenzen.
- GL-01F ist technisch weit fortgeschritten und wird als Runtime-/Pilot-Acceptance-Sprint behandelt.
- GL-01G/H schließen Setup und Journey-Polish, ohne Architekturumbau.
- GL-01I liefert das konsolidierte Pilotpaket.
- GL-01J erzeugt einen fixierten RC; fachliche Golden-Result-, Sandbox-, Recovery- und Release-Gates bleiben Freigabebedingungen.

**Founder-Empfehlung:** DH-Ausnahmen zuerst angehen, weil bereits produktiv wirksamer Code ohne vollständigen fachlichen Vertrag existiert. Der vorgelagerte Blocker ist nicht Technik, sondern die verbindliche Entscheidung über Status, Gültigkeit, Scorewirkung, Disclosure und Datenautorität.

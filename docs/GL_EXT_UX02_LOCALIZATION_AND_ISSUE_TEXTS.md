# GL-EXT-UX02 – Localization and Issue Texts

Stand: 20. Juli 2026  
Entscheidung: **Sprint teilweise abgeschlossen; NO-GO bleibt bestehen**

## Ausgangslage und Klassifikation

Der UX01-Abschlusslauf meldete 81 Checker-Verletzungen auf 59 Quellzeilen in sieben AL-Objekten. Eine Zeile konnte als Text- und Umlautverstoß doppelt zählen.

| Kategorie | Meldungen | Zeilen | Ergebnis |
|---|---:|---:|---|
| A – kundenrelevanter harter UI-Text | 48 | 39 | behoben: EN-Label, DE-XLF |
| E – Issue-Titel/Empfehlung aus AL | 1 | 1 | fragiler Wortersatz entfernt |
| I – `DEU=`-Metadaten/False Positive | 32 | 19 | Übersetzung in XLF erhalten; AL-Kommentar entfernt |
| B/C/D/F/G/H/J | 0 | 0 | kein ursprünglicher Treffer |
| **Gesamt** | **81** | **59** | **81 behoben; final 0** |

Betroffen waren `DH API Client`, `DH Scan Check Mgt.`, `DH Scan Scheduler Mgt.`, `DH Deep Scan Runs`, `DH Scan Modules`, `DH Setup` Page und Table. 71 eindeutige `LocalizeText(EN, DE)`-Paare wurden echte Labels; fünf lokale `LocalizeText`-/`IsGermanLanguage`-Hilfspfade entfielen. Der Checker wurde nicht gelockert.

## Sprachmodell und Terminologie

AL-Source-Language ist `en-US`; Deutsch liegt in `BCSentinel.de-DE.xlf`. Das Backend normalisiert `de`/`de-*` auf Deutsch, alles andere kontrolliert auf Englisch. Es gibt kein separates persistiertes AL-Setupfeld für eine BCSentinel-Sprache; die Extension sendet die BC-Session-Sprache als `preferred_language`, der Backend-Tenant speichert `de` oder `en`. Priorität: Request-/Session-Sprache, persistierte Tenant-Sprache, Englisch. Keine Ableitung aus E-Mail, Land oder Währung.

| Englisch | Deutsch |
|---|---|
| Data Health Score | Data Health Score |
| Finding / Issue | Befund / Problem |
| Recommendation | Empfehlung |
| Full Analysis | Full Analysis |
| Validation Check | Validierungsprüfung |
| Monitoring | Monitoring |
| Scan History | Scan-Historie |
| Scheduled Scan | Geplanter Scan |
| Critical / High / Medium / Low | Kritisch / Hoch / Mittel / Niedrig |
| Completed / Running / Failed | Abgeschlossen / Wird ausgeführt / Fehlgeschlagen |
| Customer / Vendor | Debitor / Kreditor |

## Herkunft und Issue-Text-Architektur

Die Rückverfolgung bestätigt stabile Schlüssel:

- 199 AL-`Check Code`/`Issue Code`-Werte in Scan Check Management und Deep Scan Runner;
- 20 Backend-Quick-Check-`code`-Werte;
- `ScanIssueRecord.code` plus gespeicherte Freitextfelder `title` und `recommendation_preview`;
- Dashboard und Executive Report lesen überwiegend gespeicherte Texte; das Report-Template selbst ist tenantsprachig.

Für die 20 produktiven Backend-Quick-Checks enthält `issue_text_service.py` einen zentralen, codebasierten DE/EN-Katalog. `scoring_service.py` enthält nur Metrik-, Punkte- und Vertragsschlüssel; Titel, Empfehlung und Summary werden einmal je neuem Finding mit der normalisierten Tenant-Sprache gerendert. Es gibt keinen Vollsatzvergleich, keine Laufzeit-Maschinenübersetzung, keine zusätzliche API-Anfrage und keine Änderung an Score, Severity, Kosten, Credits oder API-Codes.

Die frühere AL-Funktion `BuildGermanCheckName` mit `.Replace('Customers', …)` wurde vollständig entfernt. Module, Risk-Level und sechs Duplicate-Finding-Titel verwenden stabile Codes und Labels. Neue AL-Findings durchlaufen vor dem Insert die Auflösung. Für die übrigen 193 AL-Deep-Scan-Codes ist der kontrollierte Fallback weiterhin der englische hinterlegte Freitext. Deshalb ist die vollständige DE-Abdeckung noch nicht erreicht; sie wird nicht durch generischen Wortersatz vorgetäuscht.

## Historische Findings

Bestehende Finding-Zeilen bleiben unverändert. Es gibt keine Textmigration und keinen Match gegen alte englische oder deutsche Sätze. Neue Backend-Quick-Scan-Findings werden in Tenant-Sprache gespeichert. Neue AL-Deep-Scan-Findings verwenden für bekannte Katalogcodes Labels, sonst Englisch. Ein Ausbau darf ausschließlich `Issue Code` als Schlüssel verwenden.

## XLF und Tests

Der finale Compiler erzeugte 1.208 Units. Source- und DE-XLF sind synchron; 1.208/1.208 deutsche Targets sind nichtleer. Deutsche Übersetzungen wurden aus AL-`DEU=`-Kommentaren entfernt; Placeholder-Kommentare beschreiben `%1`/`%2` fachlich.

| Prüfung | Ergebnis |
|---|---|
| Localization-Checker | PASS, 0 Treffer |
| XLF Parsing / Targets | PASS, 1.208/1.208 |
| ReleaseCloud Compile | PASS, 84 Dateien, 0 Fehler |
| CodeCop + PTECop | PASS, 0 Fehler; 251 Warnungen, 84 Infos |
| AppSourceCop | bekannte Baseline: EULA, Logo, Help-URL, ID-Range; AS0092 Warnung |
| UX02 Backend-Zieltests | PASS, 3/3 |
| Python `compileall` | PASS |
| `git diff --check` | PASS; nur Zeilenenden-Hinweise |
| vollständiges Backend-pytest | PASS, 258 bestanden, 6 übersprungen, 40 Warnungen, 751,44 s |

Der Host-Test scheiterte nur am fehlenden `pytest`-Modul. Ein erster Dockerlauf nutzte ein altes Image und fand den neuen Test nicht. Ein Volltest ohne Repository-Root-Mounts erzeugte 21 Pfadfehler; ein weiterer Fehler wurde durch aktivierte reale SMTP-Konfiguration im Testcontainer verursacht. Die 54 betroffenen Mount-Tests bestanden nach Read-only-Mounts; der finale Einzelcontainerlauf mit deaktiviertem Test-SMTP bestand vollständig. Diese Fehlversuche sind Harnessbefunde, keine Produktfehler.

## Bekannte Grenzen

- Eine strengere Inventur fand 155 bereits vorhandene direkte englische `Error`/`Message`/`Confirm`/`StrSubstNo`-Literale in 23 Dateien. Der bisherige Checker erkennt diese Klasse nicht. Sie gehören nicht zu den ursprünglichen 81, widersprechen aber dem vollständigen UX02-DoD.
- 193 AL-Deep-Scan-Codes besitzen noch keinen redaktionell geprüften deutschen Titel-/Empfehlungskatalog.
- Dashboard-Dictionaries und Demo-Texte benötigen eine separate Terminologieprüfung.
- Kein Datenmodell, Enum-Ordinalwert, Permission Set, Manifest oder ID-Bereich wurde verändert.
- Die 20 vorbereiteten UX02-Sandbox-CATs sind mangels Sandbox **BLOCKED**.

## Abschluss

- 81/81 ursprüngliche Treffer behoben: **Ja**
- verbleibende Checker-Treffer: **0**
- kundenrelevante DE/EN-Lokalisierung vollständig: **Nein**
- Issue-Texte DE/EN vollständig: **Nein; Backend-Top-20 ja, AL-Gesamtkatalog nein**
- fragile Volltext-/Wortersetzung verbleibt: **Nein**
- historische Daten sicher: **Ja**
- Sprint abgeschlossen: **Nein**
- kritische Localization-Gaps: **Ja, P1 für Customer Go**
- bereit für UX03: **Nein**

Empfohlener Folgesprint: **GL-EXT-UX02B – AL Message and Issue Catalog Completion**. Definition of Done: 199/199 AL-Codes mit redaktionell geprüften DE/EN-Titeln und Empfehlungen, 155 Kundenliterale als Labels, verschärfter Checker, keine leeren oder englischen DE-Targets, große Finding-Liste ohne messbare Regression und 20/20 Sandbox-CATs.

Commit-Vorschlag nach UX02B: `fix(localization): complete de and en customer-facing texts`

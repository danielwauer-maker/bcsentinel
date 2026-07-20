# BCSentinel Extension – Localization Gaps

Stand: 16.07.2026  
Audit: GL-EXT-AUDIT-01  
Status: **DEFECTIVE / P1 releaseblockierend**

## Ergebnis

Die deutsche XLF-Datei ist formal vollständig: 1.021 Translation Units wurden geparst und alle besitzen ein nichtleeres Target. Das reicht nicht für Go-Live-Readiness. Der repositoryeigene Check `scripts/check_al_localization.py` schlägt fehl und die statische Prüfung findet harte UI-Texte, gemischte Sprachlogik, Umlaute und beschädigte Zeichenfolgen direkt in AL-Quellen. Insgesamt wurden 1.129 textnahe Quellvorkommen nur 93 Aufrufen der lokalen `LocalizeText`-Hilfslogik gegenübergestellt; diese Zahl ist ein Suchindikator, keine exakte Fehlermenge.

## Nachgewiesene Gap-Klassen

| ID | Klasse | Evidenz | Auswirkung | Priorität |
|---|---|---|---|---|
| L-01 | Harte UI-Texte | Captions, ToolTips, Messages und Statusstrings in mehreren Pages/Codeunits | Texte umgehen XLF und bleiben in der Quellsprache | P1 |
| L-02 | Gemischte Laufzeitlokalisierung | `LocalizeText(English, German)` neben XLF-Labels | zwei konkurrierende Übersetzungswege, schwer wartbar | P1 |
| L-03 | Deutsche Texte im AL-Quellcode | unter anderem `DHScanSchedulerMgt.Codeunit.al:33–34` | Checkerfehler, AppSource-/Wartungsrisiko | P1 |
| L-04 | Encodingfehler | Vorkommen wie `Verf?gbar`, `N?chster` und Mojibake wie `fÃ¼r` | sichtbare Qualitätsmängel | P1 |
| L-05 | Unübersetzte technische Begriffe | beispielsweise `Unlocked`, TaskScheduler-/API-Texte | inkonsistente Kundensprache | P2 |
| L-06 | Uneinheitliche deutsche Schreibweise | XLF enthält teils `naechste/verfuegbar`, teils korrekte Umlaute | uneinheitliches Erscheinungsbild | P2 |
| L-07 | Veralteter Backend-Test | Produkt liefert `Überblick`, Test erwartet `Ueberblick` | vollständige Test-Suite bleibt rot | P1 |
| L-08 | Währungsbegriffe | sichtbare Caption meist neutral, interne Felder/Payloads weiterhin `(EUR)` | erschwert fachlich korrekte Übersetzung und Currency-Fix | P1 |

## Betroffene Oberflächen

- Setup, Assisted Setup und Scheduler-Texte.
- Scanstart, Monitor, Historie, Ergebnis- und Findings-Seiten.
- Dashboard, Issue Drilldown und Access-/Lizenzstatus.
- Ausnahmeaktionen und FactBoxes.
- Fehlertexte aus API-/SMTP-Pfaden; technische Rohmeldungen sind nicht durchgängig kundenfreundlich lokalisiert.
- Backend-Dashboard und Executive Report verwenden eine eigene JSON-/JavaScript-Lokalisierung und müssen mit AL/XLF terminologisch abgeglichen werden.

## Prüfergebnisse

| Prüfung | Resultat |
|---|---|
| Parse `BCSentinel.g.xlf` | bestanden |
| Parse `BCSentinel.de-DE.xlf` | bestanden |
| deutsche Units/Targets | 1.021 / 1.021 nichtleer |
| `python scripts/check_al_localization.py` | fehlgeschlagen; zahlreiche Regelverletzungen |
| Backend-Lokalisierungstest | 1 reproduzierbarer Fehler: erwartetes `Ueberblick` vs. geliefertes `Überblick` |

Der Backendfehler ist als veraltete Testerwartung zu korrigieren. Das Produktverhalten mit `Überblick` ist sprachlich richtig.

## Zielbild

1. Alle kundensichtbaren AL-Texte liegen als `Label` vor und werden durch die generierte XLF übersetzt.
2. `LocalizeText` bleibt höchstens als zeitlich begrenzte Kompatibilitätsschicht und wird nicht für neue Texte verwendet.
3. AL-Dateien sind UTF-8 ohne Mojibake; XLF verwendet echte deutsche Zeichen.
4. Produktbegriffe sind in AL, Portal, Dashboard, E-Mail und Executive Report identisch.
5. Englisch und Deutsch werden in einer BC-Sandbox vollständig per Sprachwechsel geprüft.

## Definition of Done

- `scripts/check_al_localization.py` läuft ohne Fehler; unvermeidbare False Positives sind eng und dokumentiert ausgeschlossen.
- Keine harte deutsche oder gemischte kundensichtbare Zeichenfolge in `bc-extension/app/src`.
- Keine `?`-Ersatzzeichen oder Mojibake-Vorkommen in AL/XLF.
- XLF-Neugenerierung erzeugt keinen unerklärten Unit-Verlust; 100 % der DE-Targets sind nichtleer.
- Backend-Lokalisierungstest erwartet `Überblick` und die gesamte Suite ist grün.
- CAT-13 und CAT-14 bestehen in einer Sandbox mit EN-US und DE-DE.

## Delta GL-EXT-P0D (20. Juli 2026)

P0D ergänzt ausschließlich neue Access-Snapshot-Captions und Guard-Fehlertexte. Die sechs kundensichtbaren Guardmeldungen sowie vierzehn neue technische Snapshot-/Capability-Captions besitzen deutsche Targets in `BCSentinel.de-DE.xlf`. Besonders geprüft sind die geforderten Texte für abgelaufene bzw. nicht bestätigbare Findings, Dashboard und Reports. Die XLF muss im Abschlusslauf strukturell geparst werden; die historische, breitere Localization-Baseline bleibt unverändert offen und wird nicht durch P0D als gelöst markiert.

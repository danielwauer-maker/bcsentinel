# Scoring Guide

## Zweck

Dieser Leitfaden definiert wiederverwendbare Skalen. Er bewertet weder BCSentinel noch einzelne Inventareinträge. Attributdefinitionen stehen ausschließlich im [Attribute Dictionary](ATTRIBUTE_DICTIONARY.md).

## Grundregeln

- Skalenwerte beschreiben beobachtbare Zustände, keine gefühlte Präferenz.
- `null` bedeutet nicht bewertet; es darf nicht als niedrigster Wert interpretiert werden.
- Ein Wert benötigt Evidenz, Begründung, Owner, Status und Bewertungszeitpunkt.
- Ordinalwerte dürfen nicht ohne ein separat freigegebenes Verfahren addiert, gemittelt oder in Prozent umgerechnet werden.
- Die gleiche Skala behält über alle Hierarchieebenen dieselbe Bedeutung; nur die Evidenzgranularität ändert sich.

## Level Scale 1–5

Diese Skala gilt für Wert, Sichtbarkeit, Qualität, Kritikalität und Risiko. Die fachliche Richtung wird vom Attribut bestimmt: Bei Qualität bedeutet ein hoher Wert stärker; bei Risiko bedeutet er höheres Risiko.

| Wert | Bezeichnung | Allgemeine Interpretation |
|---:|---|---|
| 1 | Minimal | Kaum nachweisbare Bedeutung oder Ausprägung im definierten Kontext |
| 2 | Begrenzt | Lokal oder selten relevant; Auswirkungen bleiben kontrollierbar |
| 3 | Wesentlich | Klar erkennbar und für mehrere typische Fälle relevant |
| 4 | Hoch | Breite oder erhebliche Auswirkungen; aktive Steuerung erforderlich |
| 5 | Kritisch/Prägend | Bestimmt den Kontext oder kann ihn grundlegend beeinflussen |

Bewertungshinweise:

- Vor der Zahl muss der betrachtete Kontext benannt sein.
- Benachbarte Werte werden durch konkrete Schwellen oder Beispiele der jeweiligen Domäne operationalisiert.
- Capabilities verwenden aggregierte Evidenz, dürfen aber nicht automatisch den höchsten oder mittleren Kindwert erben.

## Boolean Gate

Zulässige Werte sind `true`, `false` und `null` für nicht bewertet.

- `true`: Ein vorab definierter Erfolgskontext wird ohne den Gegenstand zwingend verhindert.
- `false`: Der Gegenstand ist für diesen Kontext nicht zwingend; dies bedeutet nicht unwichtig.
- `null`: Kontext oder Evidenz reichen für die Entscheidung nicht aus.

Boolean Gates werden nur für Pilot-, Go-Live- und Betriebskritikalität verwendet. Sie ersetzen keine Risiko- oder Prioritätsbewertung.

## Priority Class

| Wert | Bedeutung |
|---|---|
| `P0` | Sofortige, explizit freigegebene Behandlung wegen akutem Blocker oder unvertretbarem Risiko |
| `P1` | Nächster verbindlicher Planungshorizont |
| `P2` | Geplante Behandlung nach P1-Verpflichtungen |
| `P3` | Sinnvolle Verbesserung ohne aktuelle Lieferverpflichtung |
| `P4` | Beobachtung oder bewusst zurückgestellte Option |
| `null` | Nicht priorisiert |

Priorität ist eine Entscheidung, kein berechneter Score. Sie benötigt Planungskontext und Freigabe.

## Confidence Scale

| Wert | Bedeutung |
|---|---|
| `low` | Indirekte, unvollständige oder veraltete Evidenz |
| `medium` | Mehrere plausible Belege, aber relevante Unsicherheit bleibt |
| `high` | Direkte, aktuelle und konsistente Evidenz für den bewerteten Kontext |
| `null` | Konfidenz nicht beurteilt |

Konfidenz bewertet die Beleglage, nicht den Gegenstand.

## Assessment Status Scale

`not_assessed` → `draft` → `reviewed` → `approved`; `stale` kennzeichnet eine zuvor nutzbare Bewertung, deren Aktualitätsgrenze überschritten oder deren Kontext wesentlich verändert wurde.

## Referenztypen

- Dependencies verwenden stabile Feature-, Capability-, Subfeature- oder externe Systemreferenzen.
- Target Release verwendet einen freigegebenen Releasebezeichner oder `unassigned`.
- Evidence enthält Quelle, Fundstelle, Beobachtung und optional Erhebungszeitpunkt.
- Zeitpunkte verwenden ISO 8601 mit Zeitzone, wenn Tageszeit relevant ist.

## Wahl der Skala

| Fragestellung | Skala |
|---|---|
| Wie stark ist eine Ausprägung? | Level Scale 1–5 |
| Verhindert etwas zwingend einen definierten Kontext? | Boolean Gate |
| Wann soll etwas relativ bearbeitet werden? | Priority Class |
| Wie belastbar ist die Evidenz? | Confidence Scale |
| Wie weit ist die Bewertung freigegeben? | Assessment Status Scale |
| Welche Objekte oder Zeitpunkte sind gemeint? | Referenztyp statt Score |

Eine 1–10-Skala wird nicht verwendet: Sie erzeugt Scheingenauigkeit, ohne für dieses Modell zusätzliche belastbare Abstufungen zu liefern. High/Medium/Low bleibt auf Evidenzkonfidenz beschränkt.


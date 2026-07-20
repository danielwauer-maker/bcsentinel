# BCSentinel Knowledge Architecture

## Zielbild

BCSentinel sollte zwei komplementäre, nicht konkurrierende Wissenssysteme betreiben:

- Das **Product Master Book** beantwortet: *Was existiert im Produkt und Repository nachweisbar?* Es ist die deskriptive, code- und evidenznahe Quelle.
- Das **BCSentinel Product System** beantwortet: *Wie soll BCSentinel gestaltet, beschrieben, entschieden und weiterentwickelt werden?* Es ist die normative Quelle.

Die Trennlinie lautet damit **Ist/Evidenz** gegen **Soll/Regel**. Kein Dokument darf beide Rollen gleichzeitig beanspruchen. Code bleibt die primäre technische Realität; das Master Book ist deren kuratierter Wissensindex.

## Architekturprinzipien

1. Jede Wissensdomäne hat genau eine autoritative Zielquelle.
2. Zweitquellen enthalten nur Kontext und Links, keine kopierte Wahrheit.
3. Normative Aussagen tragen Owner, Status und Gültigkeitsbereich; deskriptive Aussagen tragen Stichtag und Evidenz.
4. Produkt-System-Releases und Produkt-Releases werden begrifflich getrennt.
5. Entwurf, freigegebener Standard, implementierter Stand und Laufzeitnachweis bleiben verschiedene Zustände.
6. Beziehungen zwischen Soll und Ist werden über stabile IDs oder explizite Links hergestellt.
7. Statusseiten werden aktualisiert oder als historische Snapshots gekennzeichnet; sie dürfen nicht dauerhaft „current“ heißen, wenn sie nicht gepflegt werden.

## Empfohlenes logisches Modell

```text
Product System (normativ)                 Product Master Book (deskriptiv)
Vision, Prinzipien, Terminologie          Capabilities, Features, Subfeatures
Governance, Entscheidungen, Standards  -> Implementierungs- und Evidenzstatus
UX, Design, Komponenten, Templates        Workflows, Tests, Gaps, Komponenten
Prompt- und Entwicklungsregeln            Release- und Betriebsnachweise
              \___________________________/
                Traceability-Verweise
```

Die physische Trennung in zwei Repositories kann bestehen bleiben. Erforderlich ist ein kurzer, beidseitig verlinkter Authority Contract, der diese Grenze verbindlich festlegt. Eine Zusammenlegung der Repositories ist nicht notwendig.

## Wissensdomänen

### Produkt und Sprache

Vision, Positionierung, Prinzipien, Personas, Terminologie, Ziel-Journeys und Ziel-Informationsarchitektur gehören ins Product System. Aktuelle Capabilities, konkrete Features, Produktzugänge und belegte Workflows gehören ins Master Book. Preis- und Packaging-Absichten werden im Product System entworfen; der aktuell implementierte und kanonisch angebotene Stand wird im Master Book nachgewiesen.

### Technik und Qualität

Technische Ist-Architektur, APIs, Datenmodelle, Integrationen, Security Controls, Tests und Operationsnachweise gehören ins Master Book. Zielarchitektur, Coding Standards, Quality Gates und Security Policies gehören ins Product System. Architekturentscheidungen werden nur im Product System geführt und verweisen auf betroffene Master-Book-IDs.

### Experience und Produktion

Design System, UX-Regeln, Komponentenverträge, Figma-Spezifikationen, Content-Regeln, Prompts und Templates bleiben im Product System. Implementierte UI-Flächen und deren Belege bleiben im Master Book. Build-Spezifikationen sind Arbeitsartefakte; nach Umsetzung sollten sie auf einen historischen Status wechseln und nur auf die dauerhafte Seitenspezifikation verweisen.

### Release und Betrieb

Produktrelease-Notizen, technische Release-Evidenz, Deployment- und Betriebsnachweise gehören ins Master Book. Regeln für Versionierung, Branches, Commits und Release-Erstellung bleiben im Product System. `09-release/RELEASE_NOTES_v1.0.0.md` darf als historischer Release des *Product Systems* bestehen, ist aber keine Produktrelease-Quelle.

## Lifecycle

1. Product System definiert eine normative Absicht oder Entscheidung.
2. Spezifikation referenziert vorhandene Feature-IDs oder beantragt eine spätere ID-Zuordnung.
3. Implementierung erfolgt außerhalb der Wissenssysteme.
4. Master Book erfasst den belegten Stand und Abweichungen.
5. Review vergleicht Soll und Ist; Unterschiede werden als Entscheidung, Gap oder Spezifikationskorrektur behandelt.
6. Release aktualisiert das Master Book; das Product System ändert sich nur bei normativen Folgen.

## Fünfjahresbewertung

Die vorhandene Zweiteilung ist langfristig tragfähig, wenn Autorität, Statuspflege und Traceability verbindlich werden. Ohne diese Regeln wachsen zwei parallele Produktgedächtnisse, deren Widersprüche für Menschen und AI-Systeme nur schwer erkennbar sind.

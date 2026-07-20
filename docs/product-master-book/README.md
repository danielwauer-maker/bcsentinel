# BCSentinel Product Master Book

## Zweck

Dieses Master Book ist die belegbasierte technische Inventur des Repository-Stands vom 20. Juli 2026. Es beschreibt nachgewiesenen Code, Tests, Konfiguration und Dokumentation. Es ist keine Produkt-, Release- oder Go-Live-Bewertung.

## Statusmodell

Zulässig sind ausschließlich `implemented`, `partial`, `stub`, `documented_only`, `not_found`, `manual_review` und – nur mit konkretem Ablösebeleg – `deprecated_or_legacy`. Codeexistenz, automatisierter Test, ausgeführter Test, Integration, End-to-End-Nachweis und Produktionsreife sind getrennte Aussagen.

## Feature-IDs

Die Präfixe `EXT`, `BACK`, `SCAN`, `DASH`, `ADM`, `WEB`, `REP`, `AUTH`, `BILL`, `MAIL`, `TRANS`, `DB`, `OPS`, `SEC`, `TEST` und `DOC` ordnen Features ihren technischen Bereichen zu. IDs sind in [data/features.yaml](data/features.yaml) eindeutig.

## Darstellung und Pflege

- YAML unter `data/` ist die strukturierte Datenbasis.
- Markdown ist die menschenlesbare Sicht und verweist auf konkrete Repository-Pfade.
- Eine Statusänderung benötigt einen neuen Code-, Test- oder Dokumentbeleg.
- Nicht statisch entscheidbare Aussagen werden als `manual_review` beziehungsweise „Manuell zu prüfen“ geführt.
- Widersprüche werden dokumentiert, nicht durch Annahmen aufgelöst.
- Versionen, Prioritäten und Go-Live-Zuordnungen werden erst in späteren Sprints ergänzt.

> Jede zukünftige funktionale Produktänderung muss mindestens einer Feature-ID, einem Sprint und einer Release-Zuordnung zugeordnet werden, sobald die spätere Roadmap-Struktur freigegeben wurde.

## Einstieg

[Inventurzusammenfassung](00-inventory-summary.md) · [Repository Map](01-repository-map.md) · [Features](03-feature-inventory.md) · [Workflows](04-workflow-inventory.md) · [Tests](05-test-inventory.md) · [Gaps](07-technical-gaps.md) · [manuelle Prüfungen](08-manual-review-required.md)

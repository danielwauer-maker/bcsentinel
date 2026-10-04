# S07 Canonical Repository & History Traceability

Stand: 04.10.2026

## Ziel

S07 trennt historische Entwicklungs-Evidence von der kanonischen Produktstruktur, ohne Git-Historie umzuschreiben oder alte Artefakte vorschnell zu löschen.

## Ergebnis dieses automatisierten Vorziehens

- Pull-Request-Historie #1 bis #52 ist maschinenlesbar katalogisiert.
- GitHub Releases sind aktuell nicht vorhanden; Release-Evidence wird deshalb explizit über PRs, Merge-Commits, `quality/release/*` und Dokumentation gebunden.
- Kanonische Repository-Zonen sind als Vertrag definiert.
- Legacy-/Transition-Verzeichnisse sind auf ihre kanonischen Nachfolger gemappt.
- Unmerged historische PRs werden als Evidence-Herkunft erhalten und nicht nachträglich als "merged" umgedeutet.
- CI prüft, dass kanonische Pfade existieren und Traceability-Ziele gültig bleiben.

## Bewusst offen

- S07-D02: finalen verifizierten RC-Baseline-Commit auswählen; hängt an den verbleibenden S06 Release-/Recovery-Gates.
- S07-D06: Design-Partner-Betriebsfeedback integrieren; externe Abhängigkeit.

## Sicherheitsregel

Keine historische Branch-/PR-Evidence wird für kosmetische Repository-Bereinigung gelöscht. Erst Mapping, dann optionales Cleanup.

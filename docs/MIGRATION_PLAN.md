# Knowledge Architecture Migration Plan

## Leitplanken

Dieser Plan ist eine Empfehlung. Er führt keine Verschiebung, Löschung, Umbenennung oder Inhaltsmigration durch. Historische Git-Historie und Releaseartefakte bleiben erhalten.

## Phase 0: Autorität sichern

1. Owner für beide Wissenssysteme und jede Domäne bestätigen.
2. Authority Contract beschließen: Product System normativ, Master Book deskriptiv.
3. Begriffe `Knowledge Release`, `Product Release` und `Deployment Evidence` festlegen.
4. Schreibsperre für neue doppelte Status-, Feature- und Regeldefinitionen vereinbaren.

**Exit:** Jede Domäne der Responsibility Matrix hat genau eine akzeptierte Zielquelle.

## Phase 1: Kritische Drift kennzeichnen

1. `CURRENT_STATUS.md`, `ROADMAP.md`, Root-/Pages-/Dashboard-READMEs gegen den tatsächlichen Stand prüfen.
2. Widersprüchliche Ordnerzielbilder in `SYSTEM_ARCHITECTURE.md` und `REPOSITORY_STRUCTURE.md` entscheiden.
3. Historische Dokumente mit Snapshot-/Superseded-Status kennzeichnen, ohne sie zu löschen.
4. Produkt-System-Release v1.0 explizit von Produktreleases abgrenzen.

**Exit:** Kein als „current“ oder „approved“ bezeichnetes Navigationsdokument widerspricht der vorhandenen Struktur.

## Phase 2: Traceability etablieren

1. Dashboard-, UX-, Pricing- und Security-Spezifikationen den relevanten Master-Book-IDs zuordnen.
2. Master-Book-Einträge auf normative Quellen verweisen lassen, ohne Regeln zu kopieren.
3. Standardbeziehung definieren: `specifies`, `implements`, `evidences`, `supersedes` oder `historical`.
4. Review-Checkliste um Soll-/Ist-Abgleich und Quellenautorität ergänzen.

**Exit:** Eine Stichprobe kritischer Features ist von Vision/Spec bis Implementierung/Test navigierbar.

## Phase 3: Redundanz reduzieren

1. Design Bible gegen Design System abgrenzen: Bible = Prinzipien, Design System = konkrete Regeln.
2. Writing, Style, Prompt Rules und Contributing je Thema auf eine Regelquelle reduzieren.
3. Figma- und Page-Specs auf Abweichungen und Handoff beschränken.
4. Dashboard-Build-Dateien nach Abschluss als historische Ausführungsartefakte klassifizieren.
5. Navigation-only-READMEs nicht mit Fachregeln anreichern.

**Exit:** Sekundärdokumente referenzieren statt replizieren.

## Phase 4: Fehlende Domänen schließen

1. Normative Engineering-/Coding-Standards definieren.
2. Security-/Compliance-Policy mit Owner, Risikoakzeptanz und Reviewzyklus definieren.
3. Dokument-Retention und Archivierungsregeln festlegen.
4. Automatisierte Checks für Links, Frontmatter, Status, Authority und verwaiste Dokumente planen.

**Exit:** Governance deckt Produkt, Design, Engineering, Security, Operations und AI-Arbeit ab.

## Phase 5: Betrieb

- Quartalsweiser Knowledge-Architecture-Review.
- Stichtagsbasierte Master-Book-Aktualisierung je Produktrelease.
- Product-System-Änderung nur bei normativer Änderung.
- Jährliche Prüfung historischer Dokumente auf Nutzen und Retention.
- Kennzahlen: verwaiste Dokumente, widersprüchliche Statusangaben, fehlende Traceability, Alter aktueller Statusseiten und doppelte Definitionen.

## Reihenfolge und Risiko

Phase 0 und 1 sind vor „Phase 1 – Product Intelligence“ verpflichtend. Phase 2 sollte deren erste technische Wissensgrundlage bilden. Phasen 3 bis 5 können inkrementell erfolgen. Eine Big-Bang-Migration wird nicht empfohlen.

# Overlap Analysis

## Bewertungsmaßstab

- **P0:** Autoritäts- oder Entscheidungsrisiko; vor neuer AI-/Produktintelligenz klären.
- **P1:** Hohe Wartungs- und Driftgefahr; im ersten Konsolidierungszyklus klären.
- **P2:** Redundanz oder historischer Ballast; kontrolliert bereinigen, nicht akut.

## Überschneidungen und Widersprüche

| Priorität | Bereich | Evidenz | Befund | Empfehlung |
|---|---|---|---|---|
| P0 | Globaler SSOT-Anspruch | Master Book `README.md`; Product System `README.md`, `DECISIONS.md` | Beide Systeme beanspruchen Produktwahrheit ohne Scope-Grenze. | Authority Contract „normativ vs. deskriptiv“ einführen. |
| P0 | Aktueller Status | `CURRENT_STATUS.md`, `ROADMAP.md`, Root-README | „Sprint 5 startet“ und „nächster Sprint“, obwohl Sprint-5-Dashboard-Spezifikationen und 14 Builds existieren. | Status aktualisieren oder als datierten Snapshot umbenennen. |
| P0 | Repository-Architektur | `SYSTEM_ARCHITECTURE.md`, `docs/REPOSITORY_STRUCTURE.md` | Zielordner `03-experience/` bis `06-release/` widersprechen `03-ux/`, `04-components/`, `05-pages/`, `06-figma/`, `07-prompts/`, `09-release/`. | Eine aktuelle Struktur als normativ bestimmen; andere nur historisch referenzieren. |
| P1 | Pages-Status | `05-pages/README.md`, Dashboard-README | Behauptung „noch keine Fachspezifikationen“ bzw. „startet“, obwohl drei umfangreiche Specs vorliegen. | Indexseiten zur reinen Navigation machen und Status aus Metadaten ableiten. |
| P1 | Produktvision | Product System Core; Hauptrepo `docs/product/vision.md` | Zwei Visionstexte können unabhängig driften. | Product System autoritativ; Hauptrepo verweist nur. |
| P1 | Ziel- vs. Ist-Architektur | Product System `PRODUCT_ARCHITECTURE.md`/`SYSTEM_ARCHITECTURE.md`; Master Book Komponenten/Evidenz | Begriffe wie API, Portal und Monitoring erscheinen als Soll und Ist ohne Kennzeichnung. | Dokumenttyp und Zeitbezug sichtbar machen; gegenseitige Links ergänzen. |
| P1 | Dashboard und Features | Product System `05-pages/dashboard/`; Master Book `DASH-*` | Entwurfs-Specs haben keine stabile Zuordnung zu Feature-IDs; implementierter Stand kann unbemerkt abweichen. | Jede dauerhafte Spec auf relevante Master-Book-IDs verweisen lassen. |
| P1 | Pricing/Planbegriffe | Product System UX/Content Specs; Master Book Billing-/Entitlement-Features | Free, Full Analysis, Assessment, Validation und Monitoring werden in verschiedenen Ebenen verwendet. | Product System definiert Taxonomie; Master Book belegt aktuelle Implementierung. |
| P1 | Release | Product System `09-release/`; Hauptrepo-Release- und Go-live-Dokumente | „Release“ bezeichnet Wissenssystemrelease, Produktrelease und Betriebsfreigabe. | Drei Begriffe verbindlich trennen: Knowledge Release, Product Release, Deployment Evidence. |
| P1 | Qualität und Tests | Product System Quality Gate; Master Book Testinventar | Freigabekriterien und reale Testausführung stehen getrennt, ohne Traceability. | Quality Gate auf Master-Book-Teststatus und Gaps verweisen lassen. |
| P1 | Security/Compliance | Product System Prinzipien; Master Book Security-/Privacy-Evidenz | Normative Security Policy und Risk Ownership fehlen, während technische Controls inventarisiert sind. | Policy im Product System definieren; Controls nur im Master Book. |
| P2 | Designregeln | Design Bible, `02-design-system/`, `04-components/`, Figma Specs, Dashboard Visual Spec | Semantische Wiederholung von Accessibility, Layout, Motion, Dark Mode und Hierarchie. | Grundlagen nur im Design System; Komponenten/Seiten/Figma referenzieren und spezifizieren nur Abweichungen. |
| P2 | Schreib-/Promptregeln | `.codex/RULES.md`, `STYLE_GUIDE.md`, `WRITING_GUIDE.md`, `CONTRIBUTING.md`, Templates | Viele gleiche Regeln zu Frontmatter, Links, Sprache, Do/Don't. | Eine Regelquelle je Thema; Checklisten und Templates nur operationalisieren. |
| P2 | Build-Slices | 14 Dashboard-Build-Dateien | Wertvoll für Ausführung, aber nach Umsetzung potentiell tote Dokumentation. | Nach Abschluss als historische Build Records markieren; dauerhafte Wahrheit in drei Dashboard-Specs. |
| P2 | Platzhalter-READMEs | `05-pages/admin`, `bc-extension`, `landingpage`, `reports`; Prompt-READMEs | Sehr geringer eigener Informationswert, teilweise nur Zukunftslisten. | Als Navigation behalten, bis Inhalt existiert; keine fachliche Wahrheit dort pflegen. |
| P2 | Einmalige Git-Anleitung | `09-release/GIT_RELEASE.md` | Begründung „Git nicht verfügbar“ ist umgebungsgebunden und altert. | Historischen Kontext kennzeichnen; dauerhafte Release-Regel in Governance referenzieren. |

## Tote oder schwache Dokumentation

Es wurden keine gebrochenen internen Markdown-Links im Product System gefunden. „Tot“ bedeutet daher nicht unauffindbar, sondern ohne aktuelle Entscheidungsfunktion. Kandidaten sind veraltete Current-/Next-Sprint-Aussagen, leere Zielbereich-READMEs, erledigte Build-Pläne und umgebungsbezogene Git-Anweisungen. Sie sollten nicht gelöscht, sondern später als historisch, superseded oder navigation-only klassifiziert werden.

## Positive Befunde

Das Product System besitzt durchgängiges Frontmatter in 131 Markdown-Dateien, klare Owner, 107 freigegebene und 24 Draft-Dokumente sowie keine gebrochenen relativen Links. Das Master Book trennt Implementierung, Tests, Evidenz, Gaps und Unsicherheiten bereits deutlich. Exakte Langtextduplikate sind selten; das Hauptproblem ist semantische Überlappung, nicht Copy-and-paste.

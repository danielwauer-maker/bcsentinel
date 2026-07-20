# Knowledge Architecture Audit Summary

## Executive Summary

Die aktuelle Wissensarchitektur ist fachlich stark, aber autoritativ noch nicht sauber geschlossen. Das Product Master Book liefert ein belastbares, evidenzbasiertes Ist-Modell. Das Product System liefert eine außergewöhnlich breite normative Basis für Vision, UX, Design, Komponenten, Prompts und Governance. Zusammen bilden sie ein gutes Enterprise-Fundament.

Das Hauptrisiko ist nicht fehlender Inhalt, sondern **unklare Zuständigkeit**. Beide Systeme beanspruchen Single Source of Truth. Status-, Release-, Architektur- und Produktaussagen können dadurch unabhängig driften. AI-Systeme sind davon besonders betroffen, weil formal freigegebene, aber zeitlich überholte Aussagen plausibel wirken.

## Positive Erkenntnisse

- Master Book: 93 hierarchische Inventareinträge, strukturierte Workflows, Tests, Gaps und konkrete Evidenz.
- Product System: 131 Markdown-Dokumente mit vollständigem Frontmatter, Ownern und Status; keine gebrochenen internen Links.
- Klare Design-, UX-, Komponenten-, Accessibility- und Promptgrundlagen.
- Gute Trennung von Testexistenz, Ausführung und externer Unsicherheit im Master Book.
- Wenige exakte Langtextduplikate; modulare Dokumente und relative Verweise sind bereits etabliert.
- Historische Entscheidungen und Releaseartefakte sind grundsätzlich nachvollziehbar.

## Risiken

1. Zwei globale SSOT-Ansprüche ohne Authority Contract.
2. Veraltete „Current“-/„Next Sprint“-Aussagen trotz vorhandener Folgeartefakte.
3. Widerspruch zwischen geplanter und tatsächlicher Product-System-Ordnerarchitektur.
4. Keine stabile Traceability zwischen Soll-Spezifikationen und Master-Book-Feature-IDs.
5. Mehrdeutiger Begriff „Release“ für Knowledge System, Produkt und Deployment.
6. Semantische Redundanz bei Design-, Schreib-, Review- und Promptregeln.
7. Fehlende geschlossene Engineering-Standards und normative Security-/Compliance-Policy.
8. Build-Pläne und Platzhalter-READMEs können ohne Lifecycle-Regel zu toter Dokumentation werden.

## Konsolidierungsempfehlungen

- Product System als normative Quelle, Product Master Book als deskriptive/evidenzbasierte Quelle festlegen.
- Genau eine Quelle je Domäne gemäß `RESPONSIBILITY_MATRIX.md` bestätigen.
- Status- und Strukturwidersprüche zuerst korrigieren; keine Big-Bang-Reorganisation.
- Normative Specs und Master-Book-IDs wechselseitig verknüpfen.
- Historische, navigation-only und superseded Dokumente sichtbar klassifizieren.
- Design- und Schreibgrundregeln zentral halten; Figma-, Komponenten- und Seitendokumente nur konkretisieren.
- Engineering, Security Governance und Dokument-Retention als fehlende normative Domänen schließen.

## Langfristige Bewertung

Die Zwei-System-Architektur ist für fünf Jahre geeignet und skalierbarer als ein monolithisches Dokumentationsrepository. Sie benötigt jedoch dieselbe Disziplin wie eine verteilte Softwarearchitektur: klare Boundaries, Verträge, Versionen und Observability. Mit Authority Contract und Traceability kann BCSentinel ein sehr belastbares Produktgedächtnis für Menschen und AI aufbauen.

## Gesamtbewertung

**7 von 10.** Inhaltliche Reife und Abdeckung sind hoch; Governance über die Grenze beider Systeme ist noch unzureichend.

## Empfehlung

**GO** für den Übergang in **Phase 1 – Product Intelligence**, unter zwei verbindlichen Eintrittsbedingungen:

1. Authority Contract und Responsibility Matrix werden vor neuen dauerhaften Intelligence-Artefakten bestätigt.
2. Die P0-Widersprüche zu Status und Repository-Struktur werden als aktuell oder historisch eindeutig klassifiziert.

Ohne diese Gates sollte Product Intelligence keine neue Produktwahrheit erzeugen, da sie sonst bestehende Ambiguität automatisiert vervielfältigt.

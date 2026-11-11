# BCSentinel — Go-Live Master Tracker: Wiederaufnahmeprotokoll

**Status:** Operative Planungs- und Fortschrittsrichtlinie; kein eigenständiger Beweis für Produkt-/Release-Freigaben  
**Erstellt:** 2026-11-11  
**Geltungsbereich:** Fiverr-Go-Live (Pflicht) plus separater Self-Service-SaaS-/Stripe-Launch (nicht in Fiverr-Fortschritt enthalten)  
**Führendes Arbeitsdokument:** `BCSentinel_GoLive_Master_Tracker_Fiverr_und_SaaS.xlsx` (vom Nutzer gepflegte jeweils neueste Fassung)

## 1. Wiederaufnahme in einem neuen Chat

Wenn der Nutzer eine aktuelle Fassung der Excel-Arbeitsmappe hochlädt und „weitermachen“ sagt:

1. **Zuerst die hochgeladene XLSX vollständig lesen** (nicht einen historischen Wert oder eine gespeicherte Chat-Zusammenfassung als Aufgabenstatus übernehmen).
2. Datei-/Versionskennung, Tabellenblätter und Task-IDs prüfen; bei neuerer Datei ist **die hochgeladene Fassung führend für Aufgabenplanung und manuell gepflegte Häkchen**.
3. `Dashboard`, `Sprint-Tracker`, `Parallelplan`, `Anleitung & Gates` und `SaaS-Stripe Roadmap` auswerten. Insbesondere: technische Häkchen, Go-Live-Abnahme, berechnete Gesamtstatus, Stunden, Vorgänger, Parallelfreigabe, Evidence-Links.
4. **Fiverr und späteres SaaS/Stripe getrennt bewerten.** Aufgaben/Stunden/Erfolge aus `SaaS-Stripe Roadmap` dürfen niemals den Fiverr-Fortschritt oder das Fiverr-GO/NO-GO erhöhen.
5. Nach Task-Abhängigkeiten zuerst **STARTKLAR** filtern, nach P0/Release-Risiko und verfügbaren Tools priorisieren; parallelisierbare Arbeiten auf unabhängigen Branches vorschlagen.
6. Für als erledigt markierte P0-Gates **echte Nachweise gegen GitHub, CI, BC-Sandbox, DEV/PROD und dokumentierte Abnahme-Evidence gegenprüfen**. Ein Excel-Häkchen ist eine Arbeitsstatusangabe, *kein* Ersatz für technische Evidenz. Bei Widerspruch als „Review nötig / NO-GO“ kennzeichnen, nicht blind überschreiben.
7. In der Antwort die folgenden Werte getrennt nennen: (a) technischer Fertigstellungsgrad der Aufgaben, (b) evidenzbasierte Fiverr-Go-Live-Readiness, (c) offener geschätzter Aufwand, (d) blockierte und startklare Aufgaben, (e) nächster sicherer Arbeitsschritt.
8. Nach substantiellen Änderungen XLSX und relevante Release-State-/Evidence-Dokumente konsistent aktualisieren, mit Versionsvermerk. Aufgabenstatus nicht allein aus Chat-Erzählungen als PASS eintragen.

**Vorgeschlagener Startprompt:** „Hier ist meine aktuelle BCSentinel-Go-Live-Master-Excel. Nutze sie als führende Aufgabenliste, verifiziere die offenen P0-Gates mit GitHub und den neuesten Abnahmen, unterscheide technisch fertig von Fiverr-Go-Live-freigegeben, zeige mir die jetzt parallel startklaren Aufgaben und setze den nächsten Sprint fort. SaaS/Stripe bleibt separat.“

## 2. Baseline der ursprünglichen Arbeitsmappe

- Ursprungsdatei: `BCSentinel_GoLive_Master_Tracker_Fiverr_und_SaaS.xlsx`
- SHA-256 der am 2026-11-11 ausgegebenen Datei: `504ce0bcfb5601c5c0e1bf353b3b808368b7c678dd6d5101958c6e8fd6d401c7`
- Tabs:
  - `Dashboard`
  - `Sprint-Tracker`
  - `Anleitung & Gates`
  - `Parallelplan`
  - `SaaS-Stripe Roadmap`
- Fiverr: **8 operative Sprints** (3A.2, 3B, 4, 5, 6, 7, 8, 9), **61 Unteraufgaben**, ungefähr **287 Planstunden**.
- Späterer direkter SaaS-/Stripe-Vertrieb: **5 separate Sprints**, **24 Aufgaben**, ungefähr **217 Planstunden**. **Aus Fiverr-Summen ausschließen.**
- Ursprünglich hatten nur zwei vorbereitende Aufgaben einen belegten Abschluss; deshalb startet die streng auf Aufgaben/Häkchen basierende Fortschrittsanzeige niedrig. Der historische Projektschätzwert von ca. 65 % ist **keine** gleichwertige Release-Gate-PASS-Quote.
- Da der Nutzer die Datei fortschreibt, ändern sich SHA, Häkchen, Stunden und gegebenenfalls Aufgaben. Die **hochgeladene neue Version ersetzt diese reine Initial-Baseline**.

**Speicherhinweis:** Diese GitHub-Dokumentation enthält zunächst das *Wiederaufnahmeprotokoll, Struktur und den initialen Dateifingerprint*; die XLSX-Binärdatei selbst wurde mit dieser Dokumentationsänderung **nicht** in das Git-Repository committet. Im neuen Chat die vom Nutzer hochgeladene aktuelle Datei verwenden.

## 3. Definition „technisch fertig“ vs. „Go-Live fertig“

- **Technisch fertig:** Code/Setup/Content vorhanden und passende technische Checks bestanden; keine Freigabeannahme.
- **Go-Live fertig:** Das spezifische Abnahmekriterium ist mit nachvollziehbarer Evidence bestanden; bei P0 insbesondere reale Runtime, Security, Legal und Kunden-End-to-End-Gates.
- **Gesamt erledigt:** Beide Bedingungen laut Workbook erfüllt. P0-Release kann trotz hoher durchschnittlicher Quote NO-GO bleiben.
- **Fiverr-GO:** Alle im Workbook markierten verpflichtenden Fiverr-P0-Gates mit nachvollziehbarer Evidence PASS; abschließende Freigabe, kompatibler RC und PROD-E2E inklusive erster externer Kauf-/Lieferprozesse. Keine implizite Freigabe von Stripe oder SaaS.
- **SaaS-GO:** eigener produktiver Direktvertrieb inklusive Stripe-Checkout, Webhook-Sicherheit, Subscriptions, Rechnungs-/Steuerlogik, Self-Service, Support/Datenschutz und getrenntem PROD-E2E; niemals Bestandteil der Fiverr-Zähler.

## 4. Technische Autoritäten und Freeze-Regeln

- `danielwauer-maker/bcsentinel/main`: freigegebene Core-/Backend-/Extension-Release-Produktwahrheit nach Merge, nicht automatisch laufendes PROD.
- `danielwauer-maker/bcsentinel-frontend/main`: freigegebene Frontend-Quelle.
- `danielwauer-maker/bcsentinel-product-system/main`: normative Produkt-/UX-/Contract-Wahrheit.
- `docs/BCSENTINEL_MASTER_STATE.md` und `release/current-product-state.json` gegen aktuelle, überprüfte Evidence abgleichen; **historische Versionen können vom neueren Draft-Access-v2-Modell abweichen**.
- Offene Entwicklungszweige, insbesondere PR #154 (14-Tage-Access-v2) und PR #162 (BC 1.0.2.58 / Sprint 3A.2), sind keine automatisch freigegebenen Releases. `staging` und `main` dürfen nicht nur für eine Tracker-Dokumentation gepusht werden, wenn dadurch Deployment-Workflows aktiviert werden.
- Fiverr-Verkaufs-/Preis-/Access-Texte müssen **vor Veröffentlichung** einheitlich eingefroren werden; ältere Quick-/7-Tage-Modelle nicht unbesehen mit 14-Tage-v2 vermischen.
- Keine ForceSync-/Recreate-/Datenlösch-Workarounds für BC-Upgrades; keine P0-Evidence erfinden; keine Tests mit realen Kundengeheimnissen.

## 5. Letzter in dieser Arbeitsreihe berichteter technischer Übergabepunkt (2026-11-11)

- Sprint **3A.2**, unmittelbar vor echtem **BC27-Sandbox-In-place-Upgrade von Extension 1.0.2.58** und den Szenarien **BC27-01 bis BC27-08**.
- DEV-Backend/Migration 0040/Backup und Health waren zuvor als vorbereitet und erfolgreich berichtet; **bei einer neuen Sitzung Betriebszustand erneut gegen tatsächliche Quelle prüfen**.
- Historische referenzierte Commit-SHA für PR #162: `a8b870eb41d29913cc0837a558c30637be8c57f2`; neuere Commits/Builds haben Vorrang nach überprüfter Zuordnung.
- Runbook: `docs/SPRINT3A2_BC27_ACCEPTANCE_RUNBOOK.md` auf dem Integrationsbranch `integration/sprint3a2-consolidated-20261110`.
- Template: `quality/release/sprint3a2-bc27-acceptance-template.json`.
- Vor Installation genaue .app-Herkunft/Hash, DEV-Backend-Revisionsstand, BC-Test-Sandbox, Non-SUPER-Benutzer und **zwei legitim autorisierte** Scans verifizieren.
- Releaseentscheidung weiterhin **NO-GO**, bis reale BC27-Evidence plus spätere obligatorische Fiverr-Gates bestanden sind.

## 6. Pflegeprozess

- Bei jedem abgeschlossenen Task Evidence-Link/Commit/Run/Datum im Workbook führen.
- Ist ein Task nur teilweise entwickelt, nur „technisch fertig“ setzen, wenn sein eigenes technisches Exit-Kriterium wirklich erfüllt ist; Go-Live-Abnahme nicht automatisch übernehmen.
- Fehlgeschlagene/blockierte Tasks nicht als fertig zählen; Ursache und Abhängigkeit dokumentieren.
- Aufgaben-IDs beibehalten, wenn Aufgaben umbenannt werden; neue Tasks mit eindeutigen IDs und expliziten Vorgängern ergänzen.
- Vor Go-Live einen finalen menschenlesbaren GO/NO-GO-Bericht und aktuellen RC-/Produktstatus erzeugen.

**Hinweis:** Dieses Dokument ist die Wiederaufnahme- und Arbeitssteuerungsregel. Die normative fachliche Produktwahrheit und die technische Runtime-Evidence bleiben bei den oben genannten Repositories und Abnahme-Artefakten.

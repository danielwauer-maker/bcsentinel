# Responsibility Matrix

| Wissensdomäne | Aktuelle Quelle(n) | Empfohlene Single Source of Truth | Begründung |
|---|---|---|---|
| Produktvision und Positionierung | Product System Core; `docs/product/vision.md` | Product System | Normative, langfristige Richtung |
| Produktprinzipien und Manifest | Product System Core | Product System | Entscheidungsregeln, kein Ist-Inventar |
| Terminologie und Schreibstil | Product System Core und `.codex/` | Product System | Einheitliche Sprache für Menschen und AI |
| Personas und Customer Journey | Product System `03-ux/` | Product System | Zielerlebnis und Zielgruppenmodell |
| Capabilities, Features, Subfeatures | Product Master Book | Product Master Book | Evidenzbasiertes Ist-Modell mit stabilen IDs |
| Implementierte Workflows | Product Master Book | Product Master Book | Code- und Schnittstellenbezug |
| Produkt- und Packaging-Absicht | Beide Systeme | Product System | Normative Angebotslogik |
| Aktuell implementiertes Pricing/Entitlements | Master Book und Hauptrepository | Product Master Book | Belegter, stichtagsbezogener Stand |
| Ziel-Produktarchitektur | Product System Core | Product System | Soll-Grenzen und Produktoberflächen |
| Technische Ist-Architektur | Master Book, Hauptrepository-Dokumente | Product Master Book | APIs, Datenmodelle und Integrationen mit Evidenz |
| Architekturentscheidungen | Product System `DECISIONS.md` | Product System | Eine dauerhafte Entscheidungsakte |
| UX und Information Architecture | Product System `03-ux/`, `05-pages/` | Product System | Normative Experience-Spezifikation |
| Design System und Tokens | Product System `02-design-system/` | Product System | Wiederverwendbarer visueller Standard |
| UI-Komponentenverträge | Product System `04-components/` | Product System | Soll-Verhalten und Varianten |
| Implementierte UI-Flächen | Master Book Komponenten/Evidenz | Product Master Book | Tatsächlich vorhandene Seiten und Routen |
| Figma-Spezifikationen | Product System `06-figma/` | Product System | Tool-Handoff, abgeleitet aus Designstandards |
| Prompt-Regeln und AI-Kontext | Product System `.codex/`, `07-prompts/` | Product System | Normative Arbeitsanweisungen |
| Templates | Product System `templates/` | Product System | Wiederverwendbare Erzeugungsstandards |
| Coding Standards | Fragmentarisch im Product System | Product System | Normative Engineering-Regeln fehlen als geschlossene Domäne |
| Teststrategie und Quality Gate | Product System `.codex/` | Product System | Soll-Kriterien für Freigabe |
| Testbestand und Ausführungsstatus | Product Master Book | Product Master Book | Trennung von Existenz und Ausführung |
| Security-/Compliance-Policy | Product System nur fragmentarisch | Product System | Normative Anforderungen und Risk Ownership |
| Implementierte Security Controls | Product Master Book | Product Master Book | Code- und Testevidenz |
| Operations- und Deploymentstand | Master Book und Hauptrepository | Product Master Book | Tatsächliche Runbooks und Automationsgrenzen |
| Governance und Reviewprozess | Product System | Product System | Rollen, Freigaben und Statusmodell |
| Roadmap | Product System | Product System | Zukunftsabsicht, nicht Implementierungsinventar |
| Technische Gaps und Unsicherheiten | Product Master Book | Product Master Book | Belegter Abstand im Ist-System |
| Produktrelease-Notizen | Hauptrepository, Master Book, Checklisten | Product Master Book | Release muss auf implementierten Stand zeigen |
| Product-System-Releasehistorie | Product System `09-release/` | Product System | Meta-Release des Wissenssystems |
| Dokumentkatalog und Repository-Evidenz | Product Master Book | Product Master Book | Vollständige Auffindbarkeit und Stichtagsbezug |

Sekundärdokumente sollen die jeweilige Zielquelle verlinken. Sie dürfen Begriffe oder Status nicht erneut definieren.

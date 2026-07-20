# Feature-Inventur

Die strukturierte Quelle ist [data/features.yaml](data/features.yaml). Insgesamt wurden **93 hierarchische Inventareinträge** erfasst:

| Ebene | Anzahl |
|---|---:|
| `capability` | 16 |
| `feature` | 65 |
| `subfeature` | 12 |

| Status | Anzahl |
|---|---:|
| `implemented` | 71 |
| `partial` | 16 |
| `stub` | 2 |
| `documented_only` | 1 |
| `not_found` | 2 |
| `manual_review` | 1 |

## Bereiche

- `EXT`: Registrierung, lokale Einrichtung, Quick-/Deep-Scan, Scheduler, Drilldown, Installation und Upgrade.
- `BACK`/`SCAN`: HTTP-Vertrag, Scanpersistenz, Statusmaschine, Recovery und Scoring.
- `DASH`/`ADM`/`WEB`: Kundenportal, Analytics, Administration und statische Websites.
- `REP`/`BILL`/`MAIL`: Report/PDF, Produktzugriff, Stripe und SMTP.
- `AUTH`/`SEC`: Tenant-, Dashboard-, Partner- und Adminzugriff sowie Schutzkontrollen.
- `TRANS`/`DB`/`OPS`/`TEST`/`DOC`: Lokalisierung, Persistenz, Betrieb, Qualität und Dokumentation.

Capabilities sind keine zusätzlichen Produktversprechen, sondern stabile Eltern der Komponentenstruktur. Eine `high`-Konfidenz wird nur bei eindeutigen Codebelegen verwendet. Teststatus in einem Feature bedeutet vorhandene Zuordnung, nicht bestätigte Ausführung.

# Feature-Inventur

Die strukturierte Quelle ist [data/features.yaml](data/features.yaml). Insgesamt wurden **81 Features** erfasst:

| Status | Anzahl |
|---|---:|
| `implemented` | 61 |
| `partial` | 13 |
| `stub` | 2 |
| `documented_only` | 1 |
| `not_found` | 1 |
| `manual_review` | 3 |

## Bereiche

- `EXT`: Registrierung, lokale Einrichtung, Quick-/Deep-Scan, Scheduler, Drilldown, Installation und Upgrade.
- `BACK`/`SCAN`: HTTP-Vertrag, Scanpersistenz, Statusmaschine, Recovery und Scoring.
- `DASH`/`ADM`/`WEB`: Kundenportal, Analytics, Administration und statische Websites.
- `REP`/`BILL`/`MAIL`: Report/PDF, Produktzugriff, Stripe und SMTP.
- `AUTH`/`SEC`: Tenant-, Dashboard-, Partner- und Adminzugriff sowie Schutzkontrollen.
- `TRANS`/`DB`/`OPS`/`TEST`/`DOC`: Lokalisierung, Persistenz, Betrieb, Qualität und Dokumentation.

Eine `high`-Konfidenz wird nur bei mehreren eindeutigen Codebelegen verwendet. Teststatus in einem Feature bedeutet vorhandene Zuordnung, nicht bestätigte Ausführung.

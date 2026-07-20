# Inventurzusammenfassung

## Stichtag und Umfang

Inventarisiert wurde der Git-Arbeitsbaum am 20. Juli 2026. Er enthält eine FastAPI-Anwendung, eine Business-Central-AL-Erweiterung, zwei statische Website-Bäume, PostgreSQL/Alembic, Docker-/Nginx-/GitHub-Actions-Konfiguration, Berichts- und PDF-Code sowie umfangreiche Betriebs- und Auditdokumente.

## Messbare Bestände

| Bestand | Anzahl | Nachweis |
|---|---:|---|
| FastAPI-Routendeklarationen | 120 | `backend/app/main.py`, `backend/app/routers/*.py` |
| SQLAlchemy-Modelle | 29 | `backend/app/models.py` |
| Alembic-Revisionen | 25 | `backend/alembic/versions/0001_*.py` bis `0025_*.py` |
| AL-Objektdeklarationen | 88 | `bc-extension/app/src/` |
| Python-Testfunktionen | 224 | `backend/tests/test_*.py` |
| Backend-Testdateien | 27 | `backend/tests/test_*.py` |

## Hauptbefund

Zusammenhängender Code ist für Registrierung, tenantgebundene API-Nutzung, Quick-/Deep-Scan-Synchronisation, Scan-Lifecycle, Produktberechtigungen, Stripe-Checkout/Webhooks, Dashboard, Admin, Executive Report/PDF, SMTP-E-Mails, Lokalisierung, AL-Scheduler sowie Installation/Upgrade vorhanden. Statische Analyse bestätigt keine reale BC-Sandbox-Ausführung, echte Stripe-Zahlung, SMTP-Zustellung, Produktionsperformance oder Produktionsreife.

## Abgrenzungen

- `landingpage/` wird im `backend/Dockerfile` paketiert und operativ referenziert; eine öffentliche Produktionsauslieferung des statischen Baums ist aus dem Repository allein nicht abschließend belegbar.
- `landingpage_neu/` ist ein separater alternativer statischer Baum; eine Deployment-Referenz wurde nicht gefunden.
- `go-live-readiness-2026/`, `docs/` und `output/pdf/` enthalten Nachweise und Beispielartefakte, sind aber kein Ersatz für Code- oder Laufzeitnachweise.
- Der Root-`README.md` ist leer.

Die normalisierte Zählung nach Ebene und Featurestatus steht in [03-feature-inventory.md](03-feature-inventory.md).

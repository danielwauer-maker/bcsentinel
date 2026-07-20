# Datenbank und Migrationen

## Zusammenfassung
29 SQLAlchemy-ORM-Klassen und 25 lineare Alembic-Revisionen für PostgreSQL.

## Erkannte Verantwortlichkeiten
Tenant/Scan, Lifecycle, Pricing/Billing, Partner, Audit, E-Mail, Produktlizenzierung, Websitevisibility und Dashboardusers.

## Erkannte Unterbereiche
`models.py`, `db.py`, `alembic/env.py`, Revisionen `0001`–`0025`.

## Vorhandene Features
DB-ORM-001, DB-MIG-001, DB-TEN-001.

## Teilweise vorhandene Features
DB-CHECK-001: nicht jede Testausführung nutzt Migrationen; SQLite-Metadatenaufbau dominiert.

## Stubs oder statische Inhalte
Keine Modellstubs nachgewiesen.

## APIs und Schnittstellen
SQLAlchemy 2, psycopg 3, Alembic; `DATABASE_URL`.

## Datenmodelle
Vollständig in [database-entities.md](../evidence/database-entities.md).

## Tests
Migrationstests für Memberships/Deployment sowie optionale PostgreSQL-Konkurrenztests.

## Dokumentation
Backend-README, Deployment-/Stagingberichte.

## Technische Auffälligkeiten
Tenantbindung erfolgt überwiegend über `tenant_id`-Foreign-Keys/Indizes; mehrere Statuswerte sind Strings statt DB-Enums.

## Manuell zu prüfen
`alembic upgrade head` gegen Produktionskopie, Downgradegrenzen, Datenvolumen und Löschfolgen.

## Belegverzeichnis
`backend/app/models.py`; `backend/alembic/versions/`.

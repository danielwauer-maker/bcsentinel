# BCSentinel PostgreSQL Staging Report

Stand: 20.07.2026  
Status: **ausgeführt**

## Topologie

- PostgreSQL 15, persistentes Docker-Volume `bcsentinel_p0e_pgdata`.
- zwei Backendinstanzen desselben frisch gebauten Produktionsimages.
- getrennte Datenbanken für Fresh Migration, Upgrade-Fixture und Runtime-Failure-Test.
- keine SQLite-Ersatzbewertung.
- reproduzierbare `docker-compose.p0e.yml` mit Required-Secret-Variablen, Migration-Gate und skalierbarem Backend.

## Ergebnisse

| Prüfung | Ergebnis |
|---|---|
| Fresh Alembic → 0024 | PASS |
| 0021-Fixture → 0024 | PASS, keine Datenverluste |
| P0A–P0D PostgreSQL | 105/105 PASS |
| P0E-Concurrency plus Pricing nach Race-Fix | 21/21 PASS |
| parallele identische Registrierung über 2 Instanzen | 8 Antworten, 1 Tenant, 1 User |
| Backend-A-Ausfall | Backend B blieb ready |
| Backend-A-Restart | ready, Retry `existing` |
| PostgreSQL-Ausfall | kein positiver Readiness-Entscheid |
| PostgreSQL-Restart | beide Instanzen ready, Daten persistent |
| Docker Compose Up, Backendscale 2 | PostgreSQL und zwei Backends healthy |
| vollständiges pytest | 261/261 PASS, 40 Warnungen, 601,46 s |

## Locking und Integrität

Isolation: PostgreSQL `READ COMMITTED`. Zusätzliche Kontrollen: `FOR UPDATE SKIP LOCKED`, bedingte Claims, Unique Constraints, Lifecycle-Version/CAS, Lease-Token und idempotente Client Request IDs. Es entstanden keine negativen Credits, doppelten Ledgerzeilen, doppelten Tenants oder doppelten Findings.

Ein paralleler Erstzugriff auf den Access-Snapshot deckte eine Default-Pricing-Insert-Race auf. Die Korrektur isoliert jeden Default-Insert in einem Savepoint; ein gleichzeitig bereits angelegter identischer Schlüssel lässt die äußere Transaktion verwendbar. Der reproduzierende PostgreSQL-Test ist grün.

## Grenzen

Der lokale Test nutzte keinen echten externen TLS-Reverse-Proxy, keine managed PostgreSQL-HA/Backup-Restore-Infrastruktur und keinen Netzwerk-Proxy für verlorene Responses. HTTPS-Policy und Forwarded-Proto sind automatisiert geprüft; ein produktiver Proxy-/Backup-Drill bleibt P1.

# BCSentinel Release Package

Stand: 20.07.2026  
Kandidat: `1.0.2.7-p0e`

## Inhalt

- kompilierte Extension `BCSentinel_1.0.2.7_P0E.app`
- N-1-Referenzpaket aus Commit `630d896`, Version 1.0.2.6
- P0E-Hauptbericht, Upgrade-, PostgreSQL- und Rollenbericht
- Release-/Install-/Upgrade-/Rollbackanleitung in diesem Dokument
- SHA-256-Prüfsummen

Build-Evidenz dieses Arbeitsstands:

- Target `.app`: `cf3189ad2db198f624d6a339aa2813d69a2347cd96f7c9179a07fe08fd392a27`
- N-1 `.app`: `1a2a8aca1e52379df61355dc7cdea2d30442c279c6effc77cea06e93f031d225`
- Backendimage: `sha256:928059e0671da73738420fbb8f39fc2c45cf203de08e9944fdc6e36a2198c3e6`
- Dirty Release-Candidate-ZIP: `bab947b64ef890e35c4910e5cb50c3329d4803ad0ce88d0d853f8a39b2ab1c2e`

## Installation

1. PostgreSQL bis Alembic Head 0024 migrieren.
2. Backend mit Production-Settings, HTTPS-Reverse-Proxy und Secret Management deployen.
3. `.app` in einer unterstützten BC-27-Sandbox publizieren und synchronisieren.
4. Extension installieren; `DH Install` muss Setup pro Company anlegen.
5. Rollen ohne `SUPER` zuweisen, Consent/HTTPS-API konfigurieren und registrieren.
6. Health, Dashboard, Report, manuellen Scan und Scheduler-CAT ausführen.

## Upgrade 1.0.2.6 → 1.0.2.7

Backup und N-1-Evidenz sichern, Backend zuerst kompatibel deployen, Targetpaket publizieren, Schema synchronisieren und Upgrade ausführen. Danach Setup, Tenantbindung, Request IDs, Runs, Findings, Scheduler, Currency und invalidierten Access-Snapshot prüfen. Snapshot muss frisch neu geladen werden.

## Rollback

Traffic stoppen, PostgreSQL sichern, Backendimage und Extensionversion als gemeinsam getestetes Paar behandeln. Nach ausgeführtem Schema-/Extensionupgrade bevorzugt Roll-forward. Keine Backend-Tenants oder lokalen Extensiondaten automatisch löschen. Bei Backend-/AL-Versionsmismatch bleibt Detailzugriff fail-closed.

## Releasegrenzen

- Kandidat ist uncommitted und daher mit `dirty` zu kennzeichnen.
- Kein Signing-Zertifikat verfügbar; Paket ist **nicht signiert**.
- Keine BC-Sandbox-Install-/Upgradeevidenz.
- AppSourceCop nicht grün.
- Unterstützte Zielbasis aus Manifest: Runtime 16.0, Application/Platform 27.0.0.0.

Ein finaler Release-Artefaktname darf erst nach P0E-Commit, sauberem Checkout, erneutem Build, Sandbox-PASS und Signierung vergeben werden.

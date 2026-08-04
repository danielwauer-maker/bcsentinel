# P0-08 Loginportal und E-Mail Audit

**Stand:** 2026-08-05  
**Produktstand:** BCSentinel 1.0.2.20  
**Gate:** Loginportal / Mailversand / Sprint P0-08

## 1. Ziel

P0-08 schützt die bestehende Dashboard-Anmeldung, Einladungsaktivierung und SMTP-Einladungszustellung gegen Regressionen. Der CI-Nachweis konzentriert sich auf generische Loginfehler, sichere Einladungstoken, Kennwortmindestlänge, Tokeninvalidierung, Mailstatus und den technischen SMTP-Vertrag.

## 2. Umgesetzte Komponenten

| Komponente | Pfad | Zweck |
| --- | --- | --- |
| Contract- und Security-Tests | `backend/tests/test_p0_08_login_email_contract.py` | prüft Login-, Invite- und SMTP-Verträge |
| GitHub-Gate | `.github/workflows/p0-08-login-email-contract.yml` | führt die Tests aus und erzeugt Evidenz |
| Evidenzartefakt | `build/p0-08/` | JUnit, Pytest-Log und Markdown-Zusammenfassung |

## 3. Login- und Einladungsprüfungen

- Login, Logout und Einladungsaktivierung sind vorhanden.
- Fehlgeschlagene Anmeldung verwendet eine generische Fehlermeldung und verrät nicht, ob eine E-Mail-Adresse existiert.
- Ein neues Kennwort muss mindestens zwölf Zeichen enthalten.
- Einladungstoken werden kryptografisch zufällig erzeugt.
- In der Datenbank wird nur der Hash des Einladungstokens gespeichert.
- Einladungstoken laufen nach sieben Tagen ab.
- Nach erfolgreicher Aktivierung werden Tokenhash und Ablaufdatum entfernt.
- Der Benutzerstatus wird erst nach erfolgreicher Aktivierung auf `active` gesetzt.

## 4. Mailversandprüfungen

- fehlende SMTP-Konfiguration liefert einen eindeutigen Fehlerstatus,
- SMTP-Verbindung verwendet einen festen Timeout,
- TLS kann aktiviert werden,
- SMTP-Authentifizierung wird bei vorhandenen Zugangsdaten verwendet,
- Versandstatus wird als `pending`, `sent` oder `failed` gespeichert,
- der konkrete Versandfehler wird am Dashboard-Benutzer gespeichert,
- deutsche und englische Einladungsvorlagen sind angebunden,
- Dashboard-Link basiert auf der öffentlichen Basis-URL,
- Login-E-Mail und Supportadresse werden der Vorlage übergeben.

## 5. Akzeptanzkriterien

| ID | Kriterium | Status |
| --- | --- | --- |
| 08.1 | Login-/Logout-/Invite-Routen vorhanden | PASS |
| 08.2 | generische Loginfehler verhindern Benutzerermittlung | PASS |
| 08.3 | starke Kennwort- und Tokenregeln | PASS |
| 08.4 | Token wird nach Aktivierung ungültig | PASS |
| 08.5 | SMTP TLS/Auth/Timeout/Fehlerstatus | PASS |
| 08.6 | DE/EN-Vorlagen und öffentliche Dashboard-URL | PASS |
| 08.7 | JUnit-, Log- und Markdown-Evidenz | PASS |

## 6. CI-Evidenz

- Workflow: `P0-08 Login Email Contract`
- Run: `#2`
- Run-ID: `30959466337`
- Ergebnis: `success`
- Head-SHA: `c221b29ffb3a86e847397a9e4f0ca879199648e3`
- Evidenzartefakt: `p0-08-login-email-evidence`
- Artefakt-ID: `8912357582`
- Digest: `sha256:2382d89c20358610b44ca90b8440282cbee560eaabb72636932b6669781957db`
- Aufbewahrung bis: `2026-09-03`

Der parallele Pilot-E2E-Lauf scheiterte unabhängig davon erneut am bereits bekannten flakigen SQLite-Paralleltest `test_parallel_identical_requests_create_one_scan_and_ledger` mit einem einzelnen HTTP-409 bei vier identischen gleichzeitigen Requests. Alle 408 übrigen Backendtests sowie das echte PostgreSQL-Konkurrenz-/Transaktionsgate waren erfolgreich. Der fehlgeschlagene Workflowlauf wurde erneut angestoßen.

## 7. Auditstatus

**Aktueller Status:** `VERIFIED_IN_CI / PASS`

Die technische Login-, Invite- und SMTP-Vertragsprüfung ist auf dem aktuellen PR-Head erfolgreich durchgelaufen.

## 8. Bewusst noch offene Punkte

Der aktuelle Sprint belegt den vorhandenen Einladungs- und Loginpfad, ersetzt aber nicht folgende noch nötige Funktionen und Realtests:

1. Passwort-vergessen-/Passwortreset-Funktion,
2. Rate-Limit und zeitweilige Sperre bei wiederholten Fehlanmeldungen,
3. Retry mit Backoff für vorübergehende SMTP-Fehler,
4. echte Zustellung an Gmail und Outlook,
5. SPF-, DKIM- und DMARC-Nachweis,
6. Bounce-/Unzustellbarkeitsbehandlung,
7. Betreiberwarnung bei wiederholten Versandfehlern,
8. vollständige Einladung, Aktivierung, Logout und erneute Anmeldung in der Pilotumgebung.

## 9. Bewertung

P0-08 ist auf Repository- und CI-Ebene abgeschlossen. Für einen professionellen Betrieb mit zehn Pilotkunden bleiben Passwortreset, Login-Throttling, SMTP-Retry und reale Zustellbarkeit priorisierte Folgearbeiten.

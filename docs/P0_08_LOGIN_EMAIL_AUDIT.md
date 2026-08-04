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

| ID | Kriterium | Status vor Workflowlauf |
| --- | --- | --- |
| 08.1 | Login-/Logout-/Invite-Routen vorhanden | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 08.2 | generische Loginfehler verhindern Benutzerermittlung | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 08.3 | starke Kennwort- und Tokenregeln | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 08.4 | Token wird nach Aktivierung ungültig | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 08.5 | SMTP TLS/Auth/Timeout/Fehlerstatus | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 08.6 | DE/EN-Vorlagen und öffentliche Dashboard-URL | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |
| 08.7 | JUnit-, Log- und Markdown-Evidenz | IMPLEMENTIERT, CI-NACHWEIS AUSSTEHEND |

## 6. Auditstatus

**Aktueller Status:** `IMPLEMENTED_NOT_YET_CI_VERIFIED`

Nach grünem Workflow kann die technische Login-/Invite-/SMTP-Vertragsprüfung auf `VERIFIED_IN_CI / PASS` gesetzt werden.

## 7. Bewusst noch offene Punkte

Der aktuelle Sprint belegt den vorhandenen Einladungs- und Loginpfad, ersetzt aber nicht folgende noch nötige Funktionen und Realtests:

1. Passwort-vergessen-/Passwortreset-Funktion,
2. Rate-Limit und zeitweilige Sperre bei wiederholten Fehlanmeldungen,
3. Retry mit Backoff für vorübergehende SMTP-Fehler,
4. echte Zustellung an Gmail und Outlook,
5. SPF-, DKIM- und DMARC-Nachweis,
6. Bounce-/Unzustellbarkeitsbehandlung,
7. Betreiberwarnung bei wiederholten Versandfehlern,
8. vollständige Einladung, Aktivierung, Logout und erneute Anmeldung in der Pilotumgebung.

## 8. Bewertung

P0-08 schafft einen reproduzierbaren Mindestnachweis für den bereits vorhandenen Login- und Einladungsversand. Für einen professionellen Betrieb mit zehn Pilotkunden bleiben Passwortreset, Login-Throttling, SMTP-Retry und reale Zustellbarkeit weiterhin priorisierte Folgearbeiten.

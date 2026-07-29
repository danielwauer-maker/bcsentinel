# BCSentinel Public Contact Delivery

Stand: 29. Juli 2026

## Ziel

Das öffentliche Kontaktformular sendet keine Daten mehr an FormSubmit. Die Landingpage übermittelt JSON an den eigenen BCSentinel-Endpunkt `POST /public/contact`. Das Backend validiert die Eingaben, schützt den Endpunkt mit Honeypot und Rate Limiting und stellt die Nachricht über Brevo SMTP an `support@bcsentinel.com` zu.

## Erforderliche Umgebungsvariablen

Brevo SMTP kann mit den bestehenden generischen Mail-Einstellungen betrieben werden:

```env
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=<Brevo-SMTP-Login>
SMTP_PASSWORD=<Brevo-SMTP-Key>
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=<verifizierte-Absenderadresse>
SMTP_FROM_NAME=BCSentinel
CONTACT_RECIPIENT_EMAIL=support@bcsentinel.com
CONTACT_RATE_LIMIT_ATTEMPTS=5
CONTACT_RATE_LIMIT_WINDOW_SECONDS=600
```

`SMTP_PASSWORD` darf ausschließlich im Server-Secret-Store liegen. Es darf weder in der Landingpage noch in Logs, Screenshots oder Repository-Dateien erscheinen.

## API-Verhalten

### Request

```http
POST /public/contact
Content-Type: application/json
```

Felder:

- `name`: 2 bis 120 Zeichen
- `email`: 5 bis 254 Zeichen, syntaktisch gültig
- `company`: optional, maximal 160 Zeichen
- `topic`: `General`, `Demo`, `Pilot`, `Pricing`, `Partner` oder `Support`
- `message`: 10 bis 5.000 Zeichen
- `locale`: `de` oder `en`
- `website`: Honeypot; muss bei echten Nutzern leer sein

### Responses

- `202`: Anfrage angenommen und zugestellt oder als Honeypot neutral bestätigt
- `422`: ungültige Eingaben
- `429`: Rate Limit überschritten
- `502`: Brevo-/SMTP-Zustellung fehlgeschlagen
- `503`: Mailzustellung ist nicht konfiguriert

Responses enthalten eine `request_id`, soweit der Request-Kontext verfügbar ist. Inhalte der Nachricht werden nicht in strukturierte Betriebslogs geschrieben.

## Frontend-API-Basis

Die Kontaktseite nutzt dieselbe Domainlogik wie das Partner-Frontend:

- `bcsentinel.com` / `www.bcsentinel.com` → `https://api.bcsentinel.com`
- `dev.bcsentinel.com` → `https://dev-api.bcsentinel.com`
- `localhost` / `127.0.0.1` → `http://localhost:8000`
- andere Hosts → Same-Origin

Optionaler Override:

```html
<meta name="bcsentinel-api-base" content="https://api.example.com">
```

oder:

```javascript
window.__BCSENTINEL_API_BASE__ = "https://api.example.com";
```

## Lokaler Test

Backend:

```powershell
cd backend
$env:SMTP_HOST = "smtp-relay.brevo.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "<Brevo-SMTP-Login>"
$env:SMTP_PASSWORD = "<Brevo-SMTP-Key>"
$env:SMTP_USE_TLS = "true"
$env:SMTP_FROM_EMAIL = "<verifizierte-Absenderadresse>"
$env:CONTACT_RECIPIENT_EMAIL = "support@bcsentinel.com"
python -m uvicorn app.main:app --reload --port 8000
```

Landingpage:

```powershell
cd landingpage
python -m http.server 8080
```

Für den Cross-Origin-Test von `http://localhost:8080` auf `http://localhost:8000` muss `CORS_ALLOW_ORIGINS` lokal `http://localhost:8080` enthalten.

## Go-Live-Checkliste

1. Brevo-Absenderdomain oder Absenderadresse verifizieren.
2. SMTP-Key im produktiven Secret Store setzen.
3. `CONTACT_RECIPIENT_EMAIL` prüfen.
4. Produktions-CORS auf die öffentlichen Landingpage-Domains begrenzen.
5. Testnachricht auf DE und EN senden.
6. Reply-To-Funktion prüfen.
7. 422-, 429-, 502- und 503-Verhalten testen.
8. FormSubmit-Konfiguration und eventuell vorhandene Secrets vollständig entfernen.
9. Brevo-Auftragsverarbeitungsvertrag und Unterauftragnehmer prüfen.
10. Datenschutzerklärung und Unterauftragsverarbeiterliste bei Dienstleisteränderungen aktualisieren.

# Billing E2E Test Matrix

Datum: 2026-06-10

Status: PREPARED / PARTIAL CODE EVIDENCE / NOT EXECUTED live.

Diese Matrix dokumentiert die erforderlichen E2E-Tests fuer die vier aktuellen Produkte. In dieser Umgebung konnten Stripe, Backend Runtime und Webhooks nicht live ausgefuehrt werden.

## Produkte

| Produkt | product_code | Typ | Erwartung |
|---|---|---|---|
| Assessment | `assessment` | one-time | 1 Scan Credit, 7 Tage Access Window |
| Validation Check | `validation_check` | one-time | 1 Scan Credit, 7 Tage Access Window |
| Monitoring Monthly | `monitoring_monthly` | subscription/month | Monitoring aktiv, wiederholte Scans moeglich |
| Monitoring Annual | `monitoring_annual` | subscription/year | Monitoring aktiv, Jahresabo |

## Code-Befund

PASS:

- Vier Produktcodes sind in `backend/app/services/product_license_service.py` definiert.
- Checkout verarbeitet `product_code` in `backend/app/routers/billing.py`.
- Stripe Price IDs bleiben ENV-basiert.
- Webhook-Verarbeitung unterscheidet one-time Produkte und Monitoring-Produkte.
- Tests in `backend/tests/test_product_licensing_p0.py` decken Checkout-Mode, one-time Credits und Monitoring-Aktivierung ab.

WARN:

- Legacy `premium` bleibt intern als Kompatibilitaetsalias aktiv.
- Alte Tests und interne Services enthalten noch Free/Premium-Begriffe.
- Sichtbare Landingpage-Reste wurden in diesem Block bereinigt; BC-Extension-Altbegriffe koennen wegen bestehender AL-Objekte/Enums noch sichtbar sein und muessen separat im BC-Client verifiziert werden.

## Matrix

| Check | Assessment | Validation Check | Monitoring Monthly | Monitoring Annual |
|---|---|---|---|---|
| Checkout Session | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| Stripe Redirect Success | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| Stripe Redirect Cancel | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| Webhook-Verarbeitung | NOT EXECUTED live; unit coverage vorhanden | NOT EXECUTED live; unit coverage vorhanden | NOT EXECUTED live; unit coverage vorhanden | NOT EXECUTED live; unit coverage vorhanden |
| License Status nach Kauf | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| Scan Credits | Erwartet: +1 | Erwartet: +1 | Erwartet: Monitoring statt Einzelcredit | Erwartet: Monitoring statt Einzelcredit |
| Dashboard Access Window | Erwartet: 7 Tage | Erwartet: 7 Tage | Erwartet: aktiv solange Subscription aktiv | Erwartet: aktiv solange Subscription aktiv |
| Issue Access Window | Erwartet: 7 Tage | Erwartet: 7 Tage | Erwartet: aktiv solange Subscription aktiv | Erwartet: aktiv solange Subscription aktiv |
| Monitoring Access | Nein | Nein | Ja | Ja |
| Customer Portal | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| Subscription Cancel | Nicht relevant | Nicht relevant | NOT EXECUTED | NOT EXECUTED |
| Ablauf/Expired | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| Admin-Anzeige | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |
| BC Setup Anzeige | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED | NOT EXECUTED |

## Manuelle Testschritte fuer DEV

1. DEV starten und Migrationen ausfuehren.
2. Testtenant registrieren.
3. Pro Produkt `POST /billing/checkout/session` mit `product_code` ausfuehren.
4. Success-URL oeffnen und Status-Sync pruefen.
5. Cancel-URL oeffnen und neutrale Produkttexte pruefen.
6. Stripe CLI Webhook senden:

```bash
stripe listen --forward-to https://dev-api.bcsentinel.com/billing/webhook
```

7. Fuer one-time Produkte pruefen:
   - `TenantScanCredit` wurde erzeugt.
   - Deep Scan verbraucht Credit erst bei erfolgreichem Start.
   - Access Window ist gesetzt.
8. Fuer Monitoring pruefen:
   - `TenantProductEntitlement` aktiv.
   - Subscription-Status aktiv.
   - Dashboard zeigt Monitoring-Panels.
   - Wiederholte Scans sind erlaubt.
9. Customer Portal erzeugen und Subscription kuendigen.
10. Webhook nach Kuendigung pruefen.

## Legacy-Regel

- Legacy Free/Premium darf nicht mehr in Kundentexten erscheinen.
- Interner Legacy-Code darf kurzfristig bleiben, wenn er Kompatibilitaet fuer alte Tenants/Webhooks sichert.
- Jede interne Legacy-Stelle muss bei sichtbarer Ausgabe auf aktuelle Produktnamen mappen.

## Go/No-Go

No-Go fuer ersten zahlenden Kunden, bis mindestens ein vollstaendiger Stripe-Testlauf pro Produkttyp dokumentiert ist:

- one-time: Assessment oder Validation Check
- subscription: Monitoring Monthly oder Monitoring Annual

Fuer handgefuehrten Pilot ist Go moeglich, wenn Kauf/Lizenz alternativ manuell ueber Admin vergeben und auditiert wird.

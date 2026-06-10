# Landingpage Smoke Test

Datum: 2026-06-10

Status: STATIC CHECKS PASS / BROWSER AND LIVE ROUTING NOT EXECUTED.

## Gepruefte Seiten

- `landingpage/index.html`
- `landingpage/docs.html`
- `landingpage/security.html`
- `landingpage/privacy.html`
- `landingpage/terms.html`
- `landingpage/contact.html`
- `landingpage/impressum.html`
- `landingpage/loss-examples.html`
- `landingpage/partner-register.html`
- `landingpage/partner-login.html`
- `landingpage/partner-reset-password.html`
- `landingpage/partner-portal.html`
- `landingpage/billing-success.html`
- `landingpage/billing-cancel.html`

Zusatzdateien gefunden, aber nicht Teil der Pflichtliste:

- `landingpage/help.html`
- `landingpage/support.html`

## Ausgefuehrte Checks

| Check | Ergebnis |
|---|---|
| `node --check landingpage/script.js` | PASS |
| `node --check landingpage/js/site-shell.js` | PASS |
| `landingpage/lang/de.json` parse | PASS: 775 Keys, 0 leere Werte |
| `landingpage/lang/en.json` parse | PASS: 775 Keys, 0 leere Werte |
| Suche sichtbare Legacy/Mojibake | PASS fuer sichtbare Werte; alter Key-Name `nav_free_vs_premium` bleibt mit aktuellem Wert |
| Link-Inventar per `rg href=/src=` | PASS inventarisiert, kein automatischer HTTP-Linkcheck |

## Befund

PASS:

- Zentrale Header/Footer-Logik ueber `landingpage/js/site-shell.js` ist eingebunden.
- DE/EN JSON-Dateien sind valide.
- Sichtbare `Start free ERP health scan` CTAs wurden entfernt.
- Billing Success/Cancel enthalten keine bekannten kaputten Texte wie `Unbekoennt`, `perfuermed`, `cloesed`.
- `Free vs Premium` ist als sichtbarer Wert entfernt; der alte Key-Name bleibt aus Kompatibilitaetsgruenden.

WARN:

- Mehrere Unterseiten haben noch eigene Inline-i18n-Bloecke. Das ist funktional tolerierbar, aber nicht ideal fuer zentrale Admin-Translation-Pflege.
- `help.html` und `support.html` sind vorhanden, obwohl die Smoke-Pflichtliste nur `docs.html` und `contact.html` nennt.
- Einige Seiten nutzen Screenshot-/Mockup-Hinweise fuer AppSource-Vorbereitung. Fuer zahlende Kunden sollten finale Screenshots folgen.

NOT EXECUTED:

- Browser-Rendering Desktop/Mobile.
- Mobile Navigation Klicktest.
- Live-HTTPS Linkcheck.
- Theme Toggle visueller Test.
- DE/EN Umschaltung im Browser mit localStorage.

## Akzeptanz fuer Pilot

Go fuer handgefuehrten Pilot, wenn auf DEV live bestaetigt:

1. Alle Pflichtseiten liefern HTTP 200.
2. Header/Footer sehen konsistent aus.
3. Sprachumschalter funktioniert auf jeder Seite.
4. Theme Toggle zeigt keinen Text `Light`/`Dark`, sondern nur Icon/Button.
5. Keine sichtbaren i18n-Keys oder `undefined`.
6. Kein sichtbares Free/Trial/Premium in Landingpage, Dashboard, Admin oder BC Setup.

## Offene Aufgabe vor zahlendem Kunden

Inline-i18n aus alten Unterseiten mittelfristig entfernen oder in die zentrale Admin-Translation-Struktur ueberfuehren.

# LP-GL-11A — Admin Content Publishing Audit

## Ergebnis

Die Landingpage und ihre öffentlichen Unterseiten verwenden nun einen gemeinsamen Bundle-Vertrag über `landingpage/js/content-runtime.js`.

Der Runtime-Layer erwartet optional einen öffentlichen Read-only-Endpunkt und übergibt:

- `locale` (`de` oder `en`)
- `bundle` (zum Beispiel `redesign`, `security`, `partner-portal`)

Ohne Backend-Antwort werden die versionierten JSON-Dateien unter `landingpage/lang/` als vollständiger Fallback verwendet.

## Repository-Prüfung

Gezielte Suchen nach einer bestehenden Landingpage-Publishing-API, Landingpage-Übersetzungsmodellen und eindeutigen Admin-Publish-Funktionen lieferten auf dem Arbeitsbranch keinen verifizierbaren öffentlichen Endpunkt, der den neuen Bundle-Vertrag bereits erfüllt.

Daher wurde bewusst kein mutmaßlicher API-Pfad fest im Frontend eingetragen.

## Benötigter Backend-Vertrag

Empfohlener öffentlicher Read-only-Vertrag:

```http
GET /<verified-public-path>?locale=de&bundle=redesign
Accept: application/json
```

Die Antwort soll dasselbe Schema wie der jeweilige statische Fallback liefern. Teilantworten sind erlaubt, da der Runtime-Layer veröffentlichte Inhalte tief mit dem lokalen Fallback zusammenführt.

## Publishing-Anforderungen

Die Admin-Verwaltung sollte mindestens unterstützen:

1. Entwurf pro Bundle und Sprache
2. Vorschau vor Veröffentlichung
3. Schema- und DE/EN-Paritätsprüfung
4. Veröffentlichung mit Versionsnummer und Zeitstempel
5. Rollback auf die vorherige Version
6. Audit-Informationen zu Autor und Veröffentlichungszeitpunkt
7. Cache-Steuerung über ETag oder Versionskennung
8. serverseitige Beschränkung auf bekannte Bundles und Sprachen

## Sicherheitsanforderungen

- Der öffentliche Endpunkt ist read-only.
- Entwürfe dürfen ohne autorisierte Vorschau nicht öffentlich abrufbar sein.
- Inhalte müssen als Daten geliefert werden; ausführbarer HTML- oder JavaScript-Inhalt ist abzulehnen oder zu sanitizen.
- Unbekannte Bundles und Sprachen sollen mit einer kontrollierten Fehlerantwort abgewiesen werden.
- Veröffentlichung und Rollback gehören ins Admin-Auditlog.

## Noch offen

Die konkrete vorhandene Admin-Implementierung muss anhand ihrer tatsächlichen Router-, Model-, Service- und Template-Dateien Ende-zu-Ende zugeordnet werden. Falls keine passende Implementierung existiert, wird dafür ein eigener Backend-Sprint benötigt.

Bis dahin bleibt die statische Bundle-Struktur die verlässliche Source of Truth und der Backend-Hook optional.
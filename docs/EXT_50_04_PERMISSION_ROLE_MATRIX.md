# EXT-50-04 – Permission-Set- und Rollenmatrix

## Ziel

BCSentinel muss ohne SUPER funktionieren. Jede Rolle erhält nur die für ihren Anwendungsfall notwendigen BCSentinel-Berechtigungen. Positive und negative Tests werden in einer realen Business-Central-Sandbox durchgeführt.

## Bestehende Rollen

| Rolle | Permission Set | Zweck |
|---|---|---|
| Viewer | BCSENTINEL VIEWER | Dashboard, Historie, Findings und Reports lesen |
| Scan User | BCSENTINEL SCAN | Manuelle Scans und Finding-Remediation ausführen |
| Setup Admin | BCSENTINEL SETUP | Registrierung, Setup, Check-Auswahl und Scheduler konfigurieren |
| Scheduler User | BCSENTINEL SCHEDULER | Geplante Scans headless ausführen |
| BCSentinel Admin | BCSENTINEL ADMIN | Vollständige BCSentinel-Administration |
| Normaler BC User | keines | Darf keine BCSentinel-Funktionen nutzen |

## Automatisierte Vertragsprüfungen

- alle fünf BCSentinel Permission Sets existieren und sind assignable
- kein SUPER-Bezug in den BCSentinel Permission Sets
- Viewer besitzt auf BCSentinel-Tabellen ausschließlich Leserechte
- Scan User darf DH Setup nicht verändern
- Setup Admin darf Setup/Check-Auswahl ändern, aber keine Scan-Ergebnis-Tabellen schreiben
- Scheduler ist headless und erhält keine BCSentinel-Seitenberechtigungen
- BCSentinel Admin besitzt RIMD auf den zentralen BCSentinel-Datentabellen

## Manueller Runtime-Test in Business Central

Für jede Testrolle einen separaten Testbenutzer verwenden. SUPER und andere weitreichende kundenspezifische Permission Sets müssen für den jeweiligen Testbenutzer entfernt sein. Normale Business-Central-Basisrechte dürfen vorhanden sein, soweit sie zum Öffnen der zugrunde liegenden Standard-BC-Datensätze erforderlich sind.

| Test | Viewer | Scan User | Setup Admin | Scheduler User | BCSentinel Admin | BC User ohne BCSentinel |
|---|---|---|---|---|---|---|
| BCSentinel Dashboard öffnen | PASS erwartet | PASS erwartet | optional / nicht erforderlich | FAIL erwartet | PASS erwartet | FAIL erwartet |
| Historie/Findings lesen | PASS erwartet | PASS erwartet | nicht erforderlich | nicht erforderlich | PASS erwartet | FAIL erwartet |
| Finding-Drilldown öffnen | PASS erwartet, sofern Standard-BC-Leserecht vorhanden | PASS erwartet | nicht erforderlich | nicht erforderlich | PASS erwartet | FAIL erwartet |
| Exception anlegen | FAIL erwartet | PASS erwartet | FAIL erwartet | FAIL erwartet | PASS erwartet | FAIL erwartet |
| Als korrigiert markieren | FAIL erwartet | PASS erwartet | FAIL erwartet | FAIL erwartet | PASS erwartet | FAIL erwartet |
| Manuellen Scan starten | FAIL erwartet | PASS erwartet | FAIL erwartet | nicht interaktiv | PASS erwartet | FAIL erwartet |
| BCSentinel Setup ändern | FAIL erwartet | FAIL erwartet | PASS erwartet | FAIL erwartet | PASS erwartet | FAIL erwartet |
| Check-Auswahl ändern | FAIL erwartet | nur lesen | PASS erwartet | nur lesen | PASS erwartet | FAIL erwartet |
| Scheduler konfigurieren | FAIL erwartet | keine Konfigurationshoheit | PASS erwartet | FAIL erwartet | PASS erwartet | FAIL erwartet |
| Geplanten Scan ausführen | nicht erforderlich | nicht erforderlich | Konfiguration erlaubt | PASS erwartet | PASS erwartet | FAIL erwartet |

## Zusätzliche Negativtests

1. Viewer versucht eine DH-Ausnahme anzulegen → muss durch Permission Enforcement scheitern.
2. Viewer versucht einen Finding-Status zu verändern → muss scheitern.
3. Scan User versucht BCSentinel Setup zu ändern → muss scheitern.
4. Setup Admin versucht Scan-Historie oder Findings direkt zu verändern → muss scheitern.
5. Scheduler User versucht interaktive BCSentinel-Seiten zu öffnen → nicht vorgesehen / keine Seitenberechtigung.
6. Benutzer ohne BCSentinel Permission Set versucht Dashboard, Setup oder Scan-Aufruf → muss scheitern.
7. Alle positiven Tests erneut ohne SUPER durchführen.

## Akzeptanzkriterien EXT-50-04

EXT-50-04 ist erst PASS, wenn:

- automatisierter Permission-Contract grün ist,
- AL Compile + CodeCop/PTECop grün ist,
- Viewer ohne SUPER lesen, aber nicht verändern kann,
- Scan User ohne SUPER einen manuellen Scan vollständig ausführen kann,
- Setup Admin ohne SUPER registrieren/konfigurieren kann, aber keine Scanergebnisse verändern kann,
- Scheduler User ohne SUPER einen geplanten Scan vollständig ausführen kann,
- BCSentinel Admin ohne SUPER alle vorgesehenen BCSentinel-Funktionen ausführen kann,
- ein normaler BC User ohne BCSentinel Permission Set keinen BCSentinel-Zugriff erhält,
- keine Rolle aufgrund fehlender indirekter Berechtigung auf einen BCSentinel-internen AL-Objektzugriff unerwartet fehlschlägt.

## Stop-Kriterien

Kein Merge als PASS bei:

- notwendiger SUPER-Rolle,
- Viewer mit Schreibzugriff,
- Setup-Rolle mit Schreibzugriff auf Scanresultate,
- Scheduler mit unnötigen interaktiven Rechten,
- erfolgreichem Zugriff eines normalen BC Users ohne BCSentinel Permission Set,
- fehlgeschlagenem Scan/Scheduler ausschließlich wegen fehlender BCSentinel-internen Permission.

## Evidence

Für jeden manuellen Test dokumentieren:

- Sandbox und BC-Version
- Benutzer/Testrolle
- zugewiesene Permission Sets
- explizit: SUPER = nein
- getestete Aktion
- erwartetes Ergebnis
- tatsächliches Ergebnis
- Screenshot bei Fehler oder sicherheitsrelevantem Negativtest

Finaler Status: `AWAITING_MANUAL_BC_RUNTIME_EVIDENCE` bis die Matrix in einer realen Sandbox abgeschlossen ist.

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
- die Runtime-Evidence schreibt einen permanenten SUPER-Admin als Recovery-Anker vor
- die Runtime-Evidence erlaubt genau einen wiederverwendbaren Non-SUPER-Testbenutzer für die sequenziellen Rollenszenarien
- vor jedem Rollenszenario müssen alle BCSentinel-Rollen des Testbenutzers zurückgesetzt und die effektiven Berechtigungen dokumentiert werden

## Sichere Runtime-Teststrategie bei nur einer produktiven Admin-Lizenz

Der bestehende Administrator bleibt während des gesamten Tests unverändert mit SUPER ausgestattet und wird **nicht** als No-SUPER-Evidence verwendet. Er dient ausschließlich als Recovery-Anker, falls eine Testrolle nicht mehr administrierbar ist.

Für die Runtime-Evidence darf ein einzelner zusätzlicher, lizenzierter Testbenutzer nacheinander alle Rollenszenarien durchlaufen. Separate Benutzer pro Rolle sind nicht erforderlich, wenn die Rollen strikt isoliert getestet werden.

Der Testbenutzer darf zu keinem Zeitpunkt SUPER besitzen.

### Rollenwechsel-Protokoll

Vor **jedem** Szenario:

1. Mit dem bestehenden SUPER-Administrator anmelden.
2. Beim Testbenutzer alle BCSentinel Permission Sets entfernen.
3. Die dokumentierten normalen BC-Basisberechtigungen unverändert lassen.
4. Genau das zu prüfende BCSentinel Permission Set zuweisen – oder für den Negativtest keines.
5. Prüfen und dokumentieren: SUPER = nein.
6. Die Seite **Effektive Berechtigungen / Effective Permissions** für den Testbenutzer kontrollieren und Beleg erfassen.
7. Bestehende Sitzung des Testbenutzers beenden; anschließend neu anmelden, damit keine alte Permission-Sitzung weiterverwendet wird.
8. Positiv- und Negativtests der Rolle ausführen.
9. Tatsächliches Ergebnis, Fehlermeldungen und relevante Screenshots dokumentieren.
10. Danach wieder über den SUPER-Administrator zum neutralen Zustand zurücksetzen.

### Konstante BC-Basisberechtigungen

Normale Business-Central-Basisrechte dürfen vorhanden sein, soweit sie zum Öffnen der zugrunde liegenden Standard-BC-Daten und zum Ausführen des jeweiligen Geschäftsprozesses erforderlich sind.

Damit ein Ergebnis aussagekräftig bleibt:

- die normalen BC-Basis-Permission-Sets werden vor dem ersten Test vollständig dokumentiert,
- dieselbe Baseline wird für alle interaktiven Rollenszenarien beibehalten,
- zwischen den Szenarien wird nur das BCSentinel Permission Set gewechselt,
- SUPER und andere globale Vollzugriffsrollen sind beim Testbenutzer verboten,
- falls für eine Aktion zusätzliches Standard-BC-Recht benötigt wird, wird dieses als Standard-BC-Abhängigkeit dokumentiert und nicht stillschweigend dem BCSentinel Permission Set zugeschlagen.

So unterscheiden wir sauber zwischen:
1. fehlender BCSentinel-interner AL-Berechtigung,
2. legitimer Standard-BC-Berechtigung auf Kundendaten,
3. Lizenz-/Entitlement-Grenzen.

## Manueller Runtime-Test in Business Central

Die Matrix wird mit dem dedizierten Non-SUPER-Testbenutzer sequenziell durchlaufen.

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
7. Alle positiven Tests müssen ohne SUPER durchgeführt werden.

## Fehlerklassifikation während Runtime

Jeder unerwartete Fehler wird vor einer Codeänderung klassifiziert:

- **BCSENTINEL_PERMISSION_GAP** – ein interner BCSentinel-AL-Zugriff fehlt.
- **STANDARD_BC_PERMISSION_REQUIRED** – die Aktion benötigt legitimes Standard-BC-Recht auf einen BC-Datensatz oder Prozess.
- **LICENSE_ENTITLEMENT_LIMIT** – der Benutzer darf die Aktion aufgrund seiner BC-Lizenz nicht ausführen.
- **PRODUCT_DEFECT** – die Aktion scheitert unabhängig von der Permission-Matrix.
- **EXPECTED_DENIAL** – ein Negativtest wurde korrekt blockiert.

Nur BCSENTINEL_PERMISSION_GAP rechtfertigt unmittelbar eine Änderung an unseren BCSentinel Permission Sets.

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
- keine Rolle aufgrund fehlender indirekter Berechtigung auf einen BCSentinel-internen AL-Objektzugriff unerwartet fehlschlägt,
- der bestehende SUPER-Administrator während des Tests unverändert als Recovery-Anker erhalten blieb,
- die BC-Basisberechtigungen des Testbenutzers für jede Rolle nachvollziehbar dokumentiert sind.

## Stop-Kriterien

Kein PASS bei:

- notwendiger SUPER-Rolle für eine normale BCSentinel-Funktion,
- Entfernung des letzten sicheren SUPER-Administrators,
- Viewer mit Schreibzugriff,
- Setup-Rolle mit Schreibzugriff auf Scanresultate,
- Scheduler mit unnötigen interaktiven Rechten,
- erfolgreichem Zugriff eines normalen BC Users ohne BCSentinel Permission Set,
- fehlgeschlagenem Scan/Scheduler ausschließlich wegen fehlender BCSentinel-interner Permission,
- nicht dokumentierten zusätzlichen BC-Basisrechten,
- vermischten BCSentinel-Rollen während eines Rollenszenarios.

## Evidence

Für jedes manuelle Rollenszenario dokumentieren:

- Sandbox und BC-Version
- Extension-Version
- anonyme Testidentität / Evidence-ID
- zugewiesene normale BC-Basis-Permission-Sets
- genau zugewiesenes BCSentinel Permission Set
- explizit: SUPER = nein
- Effective-Permissions-Snapshot erfasst
- getestete Aktion
- erwartetes Ergebnis
- tatsächliches Ergebnis
- Fehlerklassifikation bei Abweichung
- Screenshot bei Fehler oder sicherheitsrelevantem Negativtest

Die konkrete Arbeitsreihenfolge steht in `docs/EXT_50_04_RUNTIME_NO_SUPER_CHECKLIST.md`.

Finaler Status: `AWAITING_MANUAL_BC_RUNTIME_EVIDENCE` bis die Matrix in einer realen SaaS-Sandbox abgeschlossen ist.

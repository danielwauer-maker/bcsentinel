# PILOT-E2E-01A – Manuelles Runbook für Daniel

Dieses Runbook beschreibt ausschließlich Schritte, die nicht sicher und vollständig ohne deine Microsoft-/Business-Central-Umgebung ausgeführt werden können. Arbeite die Abschnitte in Reihenfolge ab. Verwende keine Produktionsumgebung und keine echten Kundendaten.

## 0. Sicherheitsregeln

Vor dem Start bestätigen:

- Es handelt sich um eine Business-Central-Sandbox.
- Die Test-Company enthält nur Testdaten.
- Die verwendete Backend-URL zeigt auf DEV oder STAGING, nicht auf PROD.
- Keine Secrets werden in Screenshots, Chatnachrichten oder Repository-Dateien veröffentlicht.
- Für Tests wird ein eigener Benutzer oder eine eigene Entra-App verwendet.
- Vor Upgrade- und Deinstallationstests wird die Sandbox kopiert oder ein Wiederherstellungspunkt dokumentiert.

Evidence-Ordner lokal anlegen:

```text
PILOT-E2E-01A-EVIDENCE/
  01-environment/
  02-installation/
  03-registration-free/
  04-assessment/
  05-exceptions/
  06-validation/
  07-monitoring/
  08-expiry/
  09-upgrade/
  10-uat/
```

In Screenshots dürfen Tenant-IDs und Company-IDs enthalten sein, aber niemals Client Secrets, Passwörter, Tokens oder vollständige Connection Strings.

---

# Phase A – Umgebung bereitstellen

## A1. BC-Sandbox identifizieren

1. Öffne das Business Central Admin Center.
2. Wähle den Tenant aus, der ausschließlich für BCSentinel-Tests verwendet wird.
3. Prüfe, dass der Environment Type `Sandbox` ist.
4. Notiere:
   - Environment Name
   - BC-Version
   - Land/Region
   - Datum und Uhrzeit
5. Erstelle einen Screenshot der Environment-Übersicht.
6. Speichere ihn unter:

```text
01-environment/A1-bc-sandbox.png
```

PASS-Kriterium:

- Environment Type ist eindeutig Sandbox.
- Die BC-Version entspricht der aktuell unterstützten Zielversion oder ist bewusst als Abweichung dokumentiert.

## A2. Test-Company vorbereiten

1. Öffne die Sandbox.
2. Lege eine neue Company an oder verwende eine vorhandene reine Test-Company.
3. Verwende einen eindeutigen Namen, zum Beispiel:

```text
BCSentinel Pilot E2E
```

4. Öffne `Company Information`.
5. Notiere Company Name und Company System ID.
6. Erstelle einen Screenshot ohne sensible Kontaktdaten.
7. Speichere ihn unter:

```text
01-environment/A2-test-company.png
```

PASS-Kriterium:

- Die Company ist eindeutig eine Test-Company.
- Die System ID ist verfügbar und dokumentiert.

## A3. Testbenutzer anlegen

1. Lege einen dedizierten Testbenutzer an oder verwende einen vorhandenen Sandbox-Testbenutzer.
2. Weise zunächst die für Installation und Setup benötigten Administratorrechte zu.
3. Dokumentiere später zusätzlich einen normalen Anwender für Berechtigungstests.
4. Notiere nur Benutzername/E-Mail, niemals Passwort oder MFA-Daten.

PASS-Kriterium:

- Ein Administrator-Testbenutzer existiert.
- Ein normaler Anwender kann für spätere Rechteprüfung verwendet werden.

## A4. Backend-Ziel prüfen

1. Bestimme die DEV-/STAGING-Backend-URL.
2. Öffne den Readiness-Endpunkt im Browser oder per PowerShell.
3. Erwartet wird HTTP 200.
4. PowerShell-Beispiel:

```powershell
Invoke-WebRequest -Uri "https://DEINE-STAGING-URL/health/ready" -UseBasicParsing
```

5. Speichere die Ausgabe als Text unter:

```text
01-environment/A4-backend-ready.txt
```

STOP-Kriterium:

- URL zeigt auf PROD.
- HTTP-Status ist nicht 200.
- Zertifikat ist ungültig.

---

# Phase B – Extension installieren

## B1. Aktuelles APP-Artefakt herunterladen

1. Öffne den grünen `BC AL Compile and Cop Gate`-Run des freigegebenen Staging-Commits.
2. Lade das Artefakt `bc-al-compile-output` herunter.
3. Entpacke es lokal.
4. Notiere:
   - Workflow Run ID
   - Commit SHA
   - Dateiname der `.app`
   - Dateigröße
5. Speichere diese Angaben in:

```text
02-installation/B1-app-source.txt
```

PASS-Kriterium:

- APP stammt vom freigegebenen Staging-Commit.
- Artefakt ist nicht abgelaufen und lässt sich entpacken.

## B2. Extension hochladen

1. Öffne in BC `Extension Management`.
2. Wähle `Manage` → `Upload Extension`.
3. Lade die `.app` hoch.
4. Aktiviere die Option für die aktuelle Version, falls BC danach fragt.
5. Warte bis Installation abgeschlossen ist.
6. Öffne den Eintrag BCSentinel.
7. Erstelle einen Screenshot mit:
   - Name
   - Publisher
   - Version
   - Status installiert
8. Speichere ihn unter:

```text
02-installation/B2-installed-extension.png
```

FAIL dokumentieren bei:

- Dependency Error
- Permission Error
- Schema Synchronization Error
- Signatur-/Runtime-Fehler
- Installation bleibt hängen

Bei Fehlern zusätzlich:

1. Öffne `Deployment Status` beziehungsweise Fehlerdetails.
2. Kopiere den vollständigen Fehlertext ohne Secrets.
3. Speichere ihn unter:

```text
02-installation/B2-install-error.txt
```

---

# Phase C – Setup, Registrierung und Free Scan

## C1. BCSentinel Setup öffnen

1. Suche in BC nach `BCSentinel Setup` oder der aktuellen Setup-Seite.
2. Prüfe, dass die Seite ohne Fehler geöffnet wird.
3. Trage ausschließlich die DEV-/STAGING-Backend-URL ein.
4. Speichere.
5. Verwende die Funktion `Test Connection`.
6. Dokumentiere Ergebnis und Uhrzeit.

PASS-Kriterium:

- Verbindungstest ist erfolgreich.
- Es wird HTTPS verwendet.
- Keine technische Stacktrace-Meldung wird dem Anwender angezeigt.

Evidence:

```text
03-registration-free/C1-setup.png
03-registration-free/C1-connection-result.png
```

## C2. Registrierung durchführen

1. Starte `Register`.
2. Verwende eine eindeutige Test-E-Mail.
3. Warte auf die Rückmeldung.
4. Notiere:
   - Entra Tenant ID
   - Environment Name
   - Environment Type
   - Company System ID
   - Company Name
   - angezeigte Tenant-/Registration-ID
5. Aktualisiere anschließend die Lizenz beziehungsweise den Access Snapshot.
6. Erstelle Screenshots der erfolgreichen Registrierung und des Access-Status.

PASS-Kriterium:

- Registrierung ist erfolgreich.
- Tenant, Environment und Company stimmen exakt mit Phase A überein.
- Keine fremde Company ist sichtbar.

## C3. Idempotenz manuell prüfen

1. Führe `Register` mit identischen Daten erneut aus.
2. Erwartet wird keine zweite unabhängige Tenant-/Company-Zuordnung.
3. Die Aktion darf keine doppelten Benutzer-Mitgliedschaften erzeugen.
4. Notiere das Ergebnis.

PASS-Kriterium:

- Wiederholung ist idempotent oder liefert eine verständliche Erfolgs-/Bereits-registriert-Meldung.
- Keine Dateninkonsistenz entsteht.

## C4. Free Scan starten

1. Stelle sicher, dass keine bezahlte Lizenz aktiv ist.
2. Starte den Free Data Health Score.
3. Notiere sofort:
   - BC Run ID
   - Startzeit
   - Status
4. Aktualisiere die Statusanzeige bis zum Terminalstatus.
5. Notiere:
   - Endzeit
   - Endstatus
   - Health Score
   - Anzahl Findings/Checks, sofern angezeigt
6. Öffne Dashboard, Findings-Zusammenfassung und Free Report.

PASS-Kriterium:

- Run wechselt nachvollziehbar von queued/running zu completed.
- Ergebnis gehört zur richtigen Company.
- Dashboard, Findings-Zusammenfassung und Free Report sind verfügbar.
- Paid Assessment-, Validation- und Monitoring-Rechte sind nicht aktiv.

Evidence:

```text
03-registration-free/C4-run-start.png
03-registration-free/C4-run-completed.png
03-registration-free/C4-free-dashboard.png
03-registration-free/C4-free-report.pdf
```

## C5. Permanenten Free-Zugriff prüfen

1. Schließe BC vollständig oder melde dich ab.
2. Warte mindestens 2 Minuten, damit der 60-Sekunden-Access-Snapshot sicher erneuert wird.
3. Melde dich wieder an.
4. Aktualisiere die Lizenz/den Access Snapshot.
5. Öffne erneut Dashboard, Findings-Zusammenfassung und Free Report.

PASS-Kriterium:

- Gespeichertes Free-Ergebnis bleibt verfügbar.
- Es entstehen keine bezahlten Rechte.

---

# Phase D – Assessment und Credit

## D1. Test-Assessment bereitstellen

Verwende ausschließlich eine vorgesehene Testmethode:

- Stripe Testmode, oder
- dokumentierte Admin-Testfreischaltung, oder
- Testfixture im nichtproduktiven Backend.

Notiere:

- Methode
- Offer `assessment`
- Credit vor Aktivierung
- Credit nach Aktivierung
- Gültigkeitszeitraum

Keine Datenbankwerte manuell verändern, sofern dafür kein dokumentierter Admin-/Fixture-Pfad existiert.

## D2. Lizenz in BC aktualisieren

1. Klicke `Refresh License`.
2. Prüfe, dass Assessment aktiv ist.
3. Prüfe, dass Validation und Monitoring nicht automatisch aktiv wurden.
4. Dokumentiere die Access-Anzeige.

PASS-Kriterium:

- Offer und Rechte entsprechen exakt Assessment.
- Kein Rechte-Upgrade über das gekaufte Offer hinaus.

## D3. Deep Scan starten

1. Notiere Credit-Anzahl vor Start.
2. Starte genau einen Assessment-Scan.
3. Notiere Run ID und Execution Token, sofern sichtbar.
4. Versuche während des aktiven Runs keinen absichtlichen zweiten Start, außer die UI bietet eine sichere Prüfung ohne Verbrauch.
5. Warte auf completed.
6. Aktualisiere Credit-Anzeige.

PASS-Kriterium:

- Genau ein Credit wird verbraucht.
- Run erreicht completed.
- Findings und Executive Report sind verfügbar.
- Erneuter identischer Callback oder Refresh verbraucht keinen zweiten Credit.

Evidence:

```text
04-assessment/D3-credit-before.png
04-assessment/D3-run-start.png
04-assessment/D3-run-completed.png
04-assessment/D3-credit-after.png
04-assessment/D3-executive-report.pdf
```

## D4. Zweiten Start ohne Credit prüfen

1. Prüfe, ob kein Assessment-Credit mehr vorhanden ist.
2. Versuche einen weiteren Assessment-Scan zu starten.
3. Erwartet wird eine verständliche Sperre vor Ausführung.

PASS-Kriterium:

- Kein Run wird gestartet.
- Kein negativer Creditstand entsteht.
- Fehlermeldung ist verständlich.

---

# Phase E – Data-Health-Ausnahmen

## E1. Geeigneten Datensatz auswählen

1. Öffne ein Finding für Debitor, Kreditor oder Artikel.
2. Notiere Datensatzart, Datensatz-ID und Finding/Check.
3. Notiere Score und Finding-Anzahl vor der Ausnahme.

## E2. Ausnahme erstellen

1. Erstelle eine Ausnahme.
2. Lasse den Grund zunächst leer und speichere.
3. Erwartet wird eine Validierung: Grund ist Pflicht.
4. Trage einen eindeutigen Testgrund ein.
5. Speichere erneut.

PASS-Kriterium:

- Leerer Grund wird verhindert.
- Ersteller und Erstellzeit werden gespeichert.
- Ausnahme ist aktiv.

## E3. Dublette verhindern

1. Versuche dieselbe aktive Ausnahme erneut zu erstellen.
2. Erwartet wird eine Sperre oder verständliche Duplikatmeldung.

PASS-Kriterium:

- Keine zweite aktive Dublette entsteht.

## E4. Auswirkung prüfen

1. Starte den dafür vorgesehenen erneuten Scan oder aktualisiere die Berechnung nach Produktspezifikation.
2. Prüfe Score und Findings.
3. Öffne Executive Report.

PASS-Kriterium:

- Ausgenommener Datensatz beeinflusst den Score nicht mehr.
- Report weist auf aktive Ausnahmen hin.
- Anzahl der Ausnahmen ist korrekt.
- Ausnahme wird nicht als behobenes Finding fehlinterpretiert.

## E5. Deaktivieren und reaktivieren

1. Deaktiviere die Ausnahme.
2. Prüfe Historie auf `INCLUDED` beziehungsweise entsprechenden Eintrag.
3. Reaktiviere die Ausnahme.
4. Prüfe Historie auf `EXCLUDED` beziehungsweise entsprechenden Eintrag.

PASS-Kriterium:

- Keine Löschung erforderlich.
- Historie ist vollständig und chronologisch.
- Statusfilter Aktiv/Inaktiv/Alle funktionieren.

Evidence:

```text
05-exceptions/E2-created.png
05-exceptions/E3-duplicate-blocked.png
05-exceptions/E4-report-exception.png
05-exceptions/E5-history.png
```

---

# Phase F – Validation

## F1. Validation bereitstellen

1. Aktiviere ausschließlich Offer `validation` über Testmode/Admin-Fixture.
2. Aktualisiere die Lizenz in BC.
3. Prüfe, dass Validation sichtbar ist.
4. Notiere Credit vor Start.

## F2. Validation ausführen

1. Starte Validation gegen den vorgesehenen Assessment-Ausgangspunkt.
2. Notiere Run ID.
3. Warte auf completed.
4. Prüfe Credit nach Abschluss.
5. Prüfe Vergleich beziehungsweise Ergebnisdarstellung.

PASS-Kriterium:

- Genau ein Validation-Credit wird verbraucht.
- Validation wird nicht als neues Assessment verkauft oder dargestellt.
- Ausgangsbasis und neues Ergebnis sind nachvollziehbar.

---

# Phase G – Monitoring und Scheduler

## G1. Monitoring aktivieren

1. Aktiviere Monitoring ausschließlich im Testmode.
2. Aktualisiere Lizenz in BC.
3. Prüfe:
   - Monitoring aktiv
   - Scheduler-Funktion verfügbar
   - Assessment-/Validation-Rechte nur gemäß Produktmodell

## G2. Zeitplan konfigurieren

1. Aktiviere Scheduled Scans.
2. Verwende den kürzesten sicheren Testzeitraum oder einen kontrollierten Testtrigger.
3. Notiere geplante Ausführungszeit.
4. Öffne BC Job Queue Entries.
5. Dokumentiere den zugehörigen Job.

## G3. Ausführung prüfen

1. Warte bis nach der geplanten Zeit.
2. Aktualisiere Job Queue und Scan-Historie.
3. Notiere Run ID und Status.
4. Prüfe Backend/Dashboard.

PASS-Kriterium:

- Genau ein geplanter Run entsteht.
- Run erreicht Terminalstatus.
- Historie enthält den geplanten Run.
- Keine unkontrollierte Duplikatausführung.

## G4. Fehler und Wiederholung

Nur in Sandbox:

1. Verwende eine kontrolliert ungültige STAGING-URL oder eine dokumentierte Teststörung.
2. Lasse einen geplanten Lauf fehlschlagen.
3. Stelle die korrekte URL wieder her.
4. Prüfe Retry-/Recovery-Verhalten.

PASS-Kriterium:

- Fehler ist sichtbar und verständlich.
- Run bleibt nicht dauerhaft `running`.
- Nach Wiederherstellung kann ein neuer Lauf sicher ausgeführt werden.

---

# Phase H – Ablauf und Downgrade

## H1. Testablauf erzeugen

1. Setze über die vorgesehene Admin-Testfunktion eine kurze Testgültigkeit oder verwende eine abgelaufene Testlizenz.
2. Warte bis zum Ablauf.
3. Aktualisiere den Access Snapshot nach mindestens 60 Sekunden.

PASS-Kriterium:

- Paid Scan, Full Findings, Executive Paid Report und Monitoring werden gesperrt.
- Permanent gespeicherter Free Score bleibt verfügbar.
- UI zeigt verständlichen Status statt technischer Fehlermeldung.

## H2. Company-Isolation prüfen

1. Wechsle in eine andere Test-Company im gleichen Environment.
2. Öffne BCSentinel Setup und Ergebnisse.

PASS-Kriterium:

- Ergebnisse, Runs, Credits und Exceptions der ersten Company sind nicht sichtbar.
- Registrierung erfordert den korrekten Company-Kontext.

---

# Phase I – Upgrade

## I1. Ausgangsversion dokumentieren

1. Notiere installierte Version.
2. Erstelle Screenshots von:
   - Setup
   - letztem Run
   - Scan-Historie
   - einer aktiven Ausnahme
   - aktuellem Access-Status

## I2. Neue APP installieren

1. Verwende eine neuere, grün kompilierte APP-Version.
2. Lade sie über Extension Management hoch.
3. Führe Upgrade aus.
4. Dokumentiere Deployment Status.

## I3. Datenbeibehaltung prüfen

PASS-Kriterium:

- Setup bleibt erhalten.
- Registrierung bleibt korrekt.
- Scan-Historie bleibt vorhanden.
- Exceptions bleiben vorhanden.
- Access Snapshot kann erneuert werden.
- Neuer Free-/Testscan lässt sich starten.

---

# Phase J – Manuelle UX-Abnahme

Bewerte jeden Punkt mit PASS, FAIL oder OBSERVATION:

1. Findet ein neuer Benutzer die Setup-Seite über die BC-Suche?
2. Ist klar, welche Backend-URL einzutragen ist?
3. Ist der Unterschied zwischen Free, Assessment, Validation und Monitoring verständlich?
4. Ist beim Scan jederzeit erkennbar, was gerade passiert?
5. Sind Fehlertexte ohne Entwicklerwissen verständlich?
6. Ist erkennbar, ob ein Credit verbraucht wird?
7. Sind Findings priorisierbar und handlungsorientiert?
8. Ist der Executive Report fachlich verständlich?
9. Ist der Hinweis auf Ausnahmen transparent?
10. Sind DE und EN vollständig und ohne Mischtexte?
11. Kann der Benutzer einen Supportkontakt finden?
12. Kann der Benutzer erkennen, was nach Lizenzablauf weiterhin verfügbar ist?

Speichere Ergebnisse in:

```text
10-uat/J-UAT-Ergebnis.md
```

Empfohlenes Format:

```markdown
| Prüfschritt | Status | Beobachtung | Screenshot |
|---|---|---|---|
| Setup auffindbar | PASS | Suche liefert eindeutigen Treffer | J-01.png |
```

---

# Abschlussprotokoll

Der manuelle Sandbox-Lauf ist nur bestanden, wenn:

- alle P0-Schritte PASS sind;
- kein P0 als ungeprüft markiert ist;
- keine produktive Umgebung verwendet wurde;
- alle Run IDs und Versionen dokumentiert sind;
- Credit vor/nach dem Assessment und der Validation dokumentiert ist;
- Company-Isolation bestanden ist;
- Upgrade bestanden ist;
- Scheduler mindestens einmal real ausgeführt wurde;
- Findings, Report und Exceptions fachlich geprüft wurden.

Bei jedem FAIL erfassen:

```text
Fehler-ID:
Datum/Uhrzeit:
BC Environment:
Company:
Extension-Version:
Run ID:
Schritte zur Reproduktion:
Erwartetes Ergebnis:
Tatsächliches Ergebnis:
Screenshot/Log:
Priorität P0/P1/P2:
```

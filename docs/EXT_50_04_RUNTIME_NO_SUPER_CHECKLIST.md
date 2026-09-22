# EXT-50-04-RUNTIME – No-SUPER SaaS Checkliste

Status: **PREPARED – LICENSED TEST USER REQUIRED FOR RUNTIME**

Diese Checkliste ist die operative Evidence-Vorlage für den realen BC27-SaaS-Test. Sie ändert keine Produktberechtigungen und markiert keinen Runtime-Test als bestanden.

## 0. Sicherheitsvoraussetzungen

- [ ] Test ausschließlich in einer Business-Central-Sandbox.
- [ ] BCSentinel 1.0.2.22 ist installiert.
- [ ] Bestehender SUPER-Admin bleibt unverändert.
- [ ] SUPER-Admin wird nicht als No-SUPER-Evidence verwendet.
- [ ] Dedizierter zweiter Testbenutzer kann sich in BC anmelden.
- [ ] Testbenutzer besitzt **kein SUPER**.
- [ ] Login/E-Mail des Testbenutzers wird nicht ins Repository geschrieben; Evidence-ID: `BCS-NOSUPER-TEST-01`.
- [ ] Normale BC-Basis-Permission-Sets des Testbenutzers vollständig notieren.
- [ ] Sandbox-Name und BC-Version in der Evidence-Datei ergänzen.

## 1. Neutralzustand vor jedem Szenario

Diese Schritte vor **jedem** Rollenwechsel wiederholen:

- [ ] Mit SUPER-Admin anmelden.
- [ ] Alle BCSentinel Permission Sets beim Testbenutzer entfernen.
- [ ] Dokumentierte Standard-BC-Baseline unverändert lassen.
- [ ] Prüfen: kein SUPER und keine globale Vollzugriffsrolle beim Testbenutzer.
- [ ] Für den jeweiligen Test exakt ein BCSentinel Permission Set zuweisen; beim Plain-User-Test keines.
- [ ] Effective Permissions kontrollieren und Screenshot/Evidence erfassen.
- [ ] Testbenutzer vollständig abmelden.
- [ ] Neue Sitzung mit Testbenutzer starten.
- [ ] Erst dann Runtime-Aktionen ausführen.

Wenn eine zusätzliche Berechtigung erforderlich scheint: **nicht sofort vergeben**. Erst Fehler klassifizieren.

## 2. Viewer – BCSENTINEL VIEWER

Erwartung: lesen ja, BCSentinel-Daten verändern nein.

- [ ] Neutralzustand hergestellt.
- [ ] Nur `BCSENTINEL VIEWER` als BCSentinel-Rolle.
- [ ] SUPER = nein.
- [ ] Dashboard öffnet.
- [ ] Historie / Findings lesbar.
- [ ] Finding-Drilldown öffnet, sofern Standard-BC-Leserecht vorhanden.
- [ ] Exception anlegen wird blockiert.
- [ ] Finding als korrigiert markieren wird blockiert.
- [ ] Manueller Scan wird blockiert.
- [ ] Setup-Änderung wird blockiert.
- [ ] Actual Results in Evidence übertragen.

## 3. Scan User – BCSENTINEL SCAN

Erwartung: Scan und Remediation ja, Setup-Hoheit nein.

- [ ] Neutralzustand hergestellt.
- [ ] Nur `BCSENTINEL SCAN` als BCSentinel-Rolle.
- [ ] SUPER = nein.
- [ ] Dashboard / Findings lesbar.
- [ ] Exception kann angelegt werden.
- [ ] Finding kann als korrigiert markiert werden.
- [ ] Manueller Scan startet und wird vollständig abgeschlossen.
- [ ] Setup-Änderung wird blockiert.
- [ ] Bei Zugriff auf Customer/Vendor/Item prüfen, ob ein Fehler BCSentinel-intern oder Standard-BC-bedingt ist.
- [ ] Actual Results in Evidence übertragen.

## 4. Setup Admin – BCSENTINEL SETUP

Erwartung: Registrierung und Konfiguration ja, direkte Scanresultat-Manipulation nein.

- [ ] Neutralzustand hergestellt.
- [ ] Nur `BCSENTINEL SETUP` als BCSentinel-Rolle.
- [ ] SUPER = nein.
- [ ] Setup öffnen und zulässige Einstellung ändern.
- [ ] Check-Auswahl ändern.
- [ ] Scheduler-Konfiguration durchführen.
- [ ] Direkte Änderung an Scan-Historie / Findings wird blockiert.
- [ ] Actual Results in Evidence übertragen.

## 5. Scheduler User – BCSENTINEL SCHEDULER

Erwartung: headless geplanter Scan ja, keine interaktive Konfigurationshoheit.

- [ ] Neutralzustand hergestellt.
- [ ] Nur `BCSENTINEL SCHEDULER` als BCSentinel-Rolle.
- [ ] SUPER = nein.
- [ ] Scheduler-Konfiguration wird nicht mit dieser Rolle vorgenommen.
- [ ] Geplanter Scan läuft unter der vorgesehenen Scheduler-Identität vollständig durch.
- [ ] BCSentinel-Setup kann nicht verändert werden.
- [ ] Interaktive BCSentinel-Seiten sind nicht erforderlich / nicht unnötig freigegeben.
- [ ] Actual Results in Evidence übertragen.

## 6. BCSentinel Admin – BCSENTINEL ADMIN

Erwartung: sämtliche vorgesehenen BCSentinel-Funktionen ohne SUPER.

- [ ] Neutralzustand hergestellt.
- [ ] Nur `BCSENTINEL ADMIN` als BCSentinel-Rolle.
- [ ] SUPER = nein.
- [ ] Dashboard funktioniert.
- [ ] Manueller Scan funktioniert.
- [ ] Setup funktioniert.
- [ ] Remediation funktioniert.
- [ ] Scheduler-Konfiguration / vorgesehene Scheduler-Funktion funktioniert.
- [ ] Copied-Company-Recovery-Permission im finalen integrierten Runtime-Pass mitprüfen.
- [ ] Actual Results in Evidence übertragen.

## 7. Plain BC User – Kein BCSentinel Permission Set

Erwartung: kein BCSentinel-Zugriff.

- [ ] Neutralzustand hergestellt.
- [ ] Kein BCSentinel Permission Set zugewiesen.
- [ ] SUPER = nein.
- [ ] Dashboard-Zugriff wird blockiert.
- [ ] Setup-Zugriff wird blockiert.
- [ ] Scan-Aufruf wird blockiert.
- [ ] Actual Results in Evidence übertragen.

## 8. Fehlerklassifikation

Jede Abweichung genau einer primären Klasse zuordnen:

| Klasse | Bedeutung | Reaktion |
|---|---|---|
| `BCSENTINEL_PERMISSION_GAP` | Interner BCSentinel-AL-Zugriff fehlt | Minimalen BCSentinel-Permission-Patch entwickeln |
| `STANDARD_BC_PERMISSION_REQUIRED` | Legitime BC-Standardberechtigung auf Geschäftsdatensatz/Prozess fehlt | BC-Baseline dokumentiert ergänzen und erneut testen |
| `LICENSE_ENTITLEMENT_LIMIT` | Lizenz blockiert die Aktion unabhängig von Permission Set | Lizenztest korrigieren; kein BCSentinel-Patch |
| `PRODUCT_DEFECT` | Fehler ist kein Permission-Problem | Separaten Defect anlegen |
| `EXPECTED_DENIAL` | Negativtest korrekt blockiert | PASS dokumentieren |

## 9. Abschluss-Gate

EXT-50-04-RUNTIME ist erst PASS, wenn:

- [ ] alle fünf BCSentinel-Rollen ohne SUPER gemäß Matrix funktionieren,
- [ ] der Plain-BC-User keinen BCSentinel-Zugriff hat,
- [ ] alle unerwarteten Fehler klassifiziert und geklärt sind,
- [ ] keine Rolle SUPER benötigt,
- [ ] keine überbreiten BC-Basisrechte als versteckter Workaround verwendet wurden,
- [ ] Copied-Company-Recovery im integrierten No-SUPER-Kontext berücksichtigt wurde,
- [ ] Evidence-Datei vollständig aktualisiert ist,
- [ ] CI nach eventuellen Permission-Patches vollständig grün ist.

Bis dahin bleibt der Status `AWAITING_MANUAL_BC_RUNTIME_EVIDENCE`.

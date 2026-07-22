# DH-Ausnahmen – Benutzer- und Admin-Anleitung

## Zentrale Liste öffnen

Öffnen Sie **BCSentinel Setup > Settings > DH Exceptions** oder suchen Sie in **Tell Me** nach **DH Exceptions / DH-Ausnahmen**. Die Liste zeigt aktive und inaktive Einträge. Über Views können Sie Active, Inactive, All, Customers, Vendors und Items wählen; Issue Code und Created By lassen sich mit den Standardfiltern filtern.

## Ausnahme anlegen

Öffnen Sie einen Customer, Vendor oder Item und wählen Sie **DH Exceptions > Create Exception**. Alternativ verwenden Sie **Exclude from Analysis** in einer unterstützten Findings-Liste. Kontrollieren Sie Datensatz und Issue Code, geben Sie einen fachlichen Grund ein und bestätigen Sie. Eine bereits aktive identische Ausnahme wird nicht dupliziert.

Die Ausnahme gilt unbefristet. Im nächsten Scan wird nur dieser Datensatz aus genau diesem Check entfernt; Finding-Zahl, Penalty, Financial Impact und sichtbarer Score verwenden die bereinigte Menge.

## Deaktivieren und reaktivieren

Wählen Sie den Eintrag in der zentralen Liste und **Deactivate**. Nach Bestätigung werden User und Zeitpunkt protokolliert; der Eintrag bleibt sichtbar und der Datensatz wird im nächsten Scan wieder berücksichtigt. Für **Activate** ist erneut ein Grund zu bestätigen oder zu aktualisieren. Created By/At bleiben unverändert.

## Historie und Report

**Show History** zeigt EXCLUDED (Anlage/Aktivierung), INCLUDED (Deaktivierung) und getrennte CORRECTED-Ereignisse mit User, Zeitpunkt, Check und Kommentar. **Open Record** öffnet den Quelldatensatz, sofern er noch existiert und der Benutzer Zugriff hat.

Der Executive Report zeigt nur dann einen kompakten Hinweis, wenn mindestens eine aktive Ausnahme im konkreten Scan tatsächlich angewandt wurde. Details bleiben ausschließlich in Business Central.

## Berechtigungen und Adminprüfung

- `BCSENTINEL VIEWER`: lesen, nicht ändern.
- `BCSENTINEL SCAN`: lesen, anlegen, aktivieren und deaktivieren; kein Löschen.
- `BCSENTINEL ADMIN`: vollständige operative Verwaltung; die v1-Page bietet weiterhin kein physisches Löschen.

Admins prüfen vor Pilotbetrieb die Rollen ohne `SUPER`, den Zugriff auf Customer/Vendor/Item, Companywechsel sowie das Upgrade mit bestehenden aktiven und inaktiven Ausnahmen.

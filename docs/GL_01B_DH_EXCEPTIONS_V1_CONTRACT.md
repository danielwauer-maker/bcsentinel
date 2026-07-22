# GL-01B DH Exceptions v1 Contract

**Stand:** 22. Juli 2026  
**Status:** verbindlicher Pilotvertrag; ersetzt die offenen Empfehlungen aus GL-01A für v1

## Geltungsbereich und Identität

Eine DH-Ausnahme gehört zu genau einer Business-Central-Company, einer Tabelle, einer `Record SystemId` und einem Issue Code. Unterstützte operative Datensatztypen sind Customer, Vendor und Item. Eine zweite Exception-Autorität im Backend existiert nicht.

## Lifecycle

- Operative BCSentinel-Benutzer dürfen mit Pflichtgrund anlegen, aktivieren und deaktivieren; Viewer lesen nur.
- Eine neue Ausnahme ist sofort aktiv und unbefristet.
- Dieselbe Kombination aus Company, Table ID, Record SystemId und Issue Code wird nicht dupliziert.
- Eine aktive Dublette wird abgewiesen. Ein inaktiver Eintrag wird kontrolliert reaktiviert; Created By/At bleiben erhalten.
- Deaktivieren setzt `Active = false`, Deactivated By und Deactivated At. Es wird nicht physisch gelöscht.
- EXCLUDED bezeichnet Anlage/Aktivierung/Reaktivierung, INCLUDED die Deaktivierung, CORRECTED bleibt eine getrennte fachliche Dokumentation.

## Score- und Finding-Wirkung

Aktive Ausnahmen entfernen den betroffenen Datensatz aus der wirksamen Zählung des exakten Checks. Damit entstehen für ihn kein wirksames Finding, keine Penalty und kein Financial Impact. Der sichtbare Score ist der so bereinigte Score; Raw/Adjusted-Doppelscores sind nicht Teil von v1. Deaktivierte, falsche Table-/SystemId-/Issue-Code- oder fremde Company-Einträge wirken nicht.

Jeder Scan führt `applied_exception_count`: die Zahl unterschiedlicher aktiver Exception-Einträge, die im konkreten Scan tatsächlich mindestens einmal angewandt wurden. Default ist 0.

## Report

Bei Count 0 erscheint kein Hinweis. Bei Count > 0 zeigt der Executive Report einen kompakten deutschen oder englischen Hinweis mit Singular/Plural, Count, Ausschluss aus der Score-Berechnung und Verweis auf Business Central > DH-Ausnahmen. Eine vollständige Ausnahmeliste wird nicht in den Report aufgenommen.

## Berechtigungen

| Rolle | Lesen | Anlegen | Aktivieren/Deaktivieren | Physisch löschen |
|---|---:|---:|---:|---:|
| Viewer | ja | nein | nein | nein |
| Scan/operativer User | ja | ja | ja | nein |
| Admin | ja | ja | ja | nur technisch; nicht über die v1-Page |

Der Ablauf setzt kein `SUPER` voraus. Standardrechte auf Customer/Vendor/Item werden zusätzlich benötigt, um Quelldatensätze zu öffnen.

## Ausdrücklich nicht Teil von v1

Expiry, Review-Datum, Approver, Workflow, Backend-Exception-Persistenz, Snapshot-Synchronisation, Dashboard-Management, Raw/Adjusted-Doppelscore, Enterprise-RBAC und öffentliche Exception-API sind ausgeschlossen.

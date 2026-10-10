# BCSentinel Unterauftragsverarbeiter / Subprocessors – Review Candidate

**Version:** 0.9-review  
**Stand:** 2026-10-10

Diese Liste ist bewusst **kein erfundener Produktionsanbieter-Katalog**. Ein Anbieter darf erst als produktiver Unterauftragsverarbeiter veröffentlicht werden, wenn sein tatsächlicher Einsatz, Vertragsstatus, Verarbeitungszweck, Standort und etwaiger Drittlandtransfer verifiziert wurden.

| Kategorie | Produktiver Anbieter | Zweck | Datenkategorien | Region / Transfer | Status |
|---|---|---|---|---|---|
| Hosting / Datenbank | vor PROD verifizieren | Betrieb von API, Web und Datenbank | SaaS- und technische Metadaten | vor PROD verifizieren | REVIEW REQUIRED |
| Transaktions-E-Mail / SMTP | vor PROD verifizieren | Service-E-Mails | Kontakt- und Zustellmetadaten | vor PROD verifizieren | REVIEW REQUIRED |
| Billing / Payment | Stripe ist technisch vorgesehen; produktive Vertrags-/Account-Konfiguration in E4 verifizieren | Checkout, Subscription, Rechnung, Zahlung | Rechnungs-, Zahlungs- und Kontaktdaten | Provider-Dokumentation vor PROD prüfen | E4 EVIDENCE REQUIRED |
| Monitoring / Error Tracking | vor PROD verifizieren | Betriebsüberwachung | technische Telemetrie | vor PROD verifizieren | REVIEW REQUIRED |
| Support | kein allgemeiner externer Support-Processor im Produktvertrag festgelegt | Supportdiagnostik | tenantbezogene Diagnosedaten | n/a | INTERNAL / REVIEW |

## Änderungsprozess

Vor Aufnahme eines neuen produktiven Unterauftragsverarbeiters werden mindestens Zweck, Datenumfang, Region, Datenschutzvertrag, TOMs, Löschfristen und Drittlandtransfer bewertet. Die öffentliche bzw. vertragliche Subprozessorenliste muss anschließend mit dieser technischen Source of Truth synchronisiert werden.

## PROD-Gate

Eine Produktionsfreigabe ist aus Legal-/Privacy-Sicht nicht vollständig, solange Zeilen mit `vor PROD verifizieren` für tatsächlich eingesetzte Provider offen sind.

# BCSentinel Unterauftragsverarbeiter

Stand: 29. Juli 2026

Verantwortlicher Anbieter: Daniel Wauer, Geschäftsbezeichnung BCSentinel

Diese Liste dokumentiert Dienstleister, die für Betrieb, Zahlungsabwicklung oder Kommunikation eingesetzt werden. Sie ist bei Änderungen der produktiven Architektur vor Einsatz eines neuen Dienstleisters zu aktualisieren.

| Dienstleister | Status | Zweck | Betroffene Datenkategorien | Verarbeitungsort / Drittlandbezug | Vertrags- und Kontrollmaßnahme |
|---|---|---|---|---|---|
| Hetzner Online GmbH | aktiv | Hosting von Website, Backend, Datenbank, Speicher, Backups und technischen Protokollen | Account-, Tenant-, Company-, Scan-, Finding-, Report-, Support- und technische Protokolldaten | Falkenstein, Deutschland / EU | Auftragsverarbeitungsvertrag, Zugriffsbeschränkung, Verschlüsselung, Backup- und Löschkonzept |
| Stripe Payments Europe, Limited | aktiv | Checkout, Zahlungsabwicklung, Abonnement- und Zahlungsstatus | Rechnungs-, Kontakt-, Vertrags-, Zahlungs- und Transaktionsdaten; vollständige Kartendaten werden nicht durch BCSentinel gespeichert | EWR; mögliche konzerninterne oder technische Drittlandverarbeitung nach Stripe-Vertragsunterlagen | Stripe-Datenschutz- und Vertragsunterlagen prüfen, Datenminimierung, Webhook-Signaturen, eingeschränkte Metadaten |
| Brevo / Sendinblue GmbH | aktiv für Kontaktzustellung | Transaktionale Zustellung von Kontaktanfragen über den eigenen BCSentinel-Backend-Endpunkt | Empfängeradresse, Antwortadresse, Betreff, Nachrichteninhalt und technische Zustellinformationen | EU-Konfiguration bevorzugt; mögliche weitere Verarbeitung nach Brevo-Vertragsunterlagen | Auftragsverarbeitungsvertrag, SMTP-Zugang nur serverseitig, Datenminimierung, Rate Limiting, definierte Log- und Löschfristen |

FormSubmit ist seit LP-LEGAL-02 nicht mehr Bestandteil des öffentlichen Kontaktflusses. Verbleibende Zugangsdaten oder Konfigurationen sind aus Deployment und Secret Store zu entfernen.

## Änderungsprozess

1. Datenschutz- und Sicherheitsprüfung vor Aktivierung eines neuen Dienstleisters.
2. Abschluss beziehungsweise Prüfung des erforderlichen Auftragsverarbeitungsvertrags.
3. Prüfung von Unterauftragnehmern, Speicherorten und möglichen Drittlandübermittlungen.
4. Aktualisierung dieser Liste, der Datenschutzerklärung, des AVV und der technischen Dokumentation.
5. Technische Entfernung nicht mehr eingesetzter Integrationen und Geheimnisse.

## Kundeninformation

Wesentliche Änderungen an Unterauftragsverarbeitern werden nach Maßgabe des späteren BCSentinel-AVV und der vertraglichen Informationsfristen mitgeteilt. Diese Datei ist die interne führende Betriebsdokumentation und wird für eine veröffentlichte Kundenfassung des AVV aufbereitet.

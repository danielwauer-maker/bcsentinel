# BCSentinel Unterauftragsverarbeiter

Stand: 29. Juli 2026

Verantwortlicher Anbieter: Daniel Wauer, Geschäftsbezeichnung BCSentinel

Diese Liste dokumentiert Dienstleister, die für Betrieb, Zahlungsabwicklung oder Kommunikation eingesetzt werden beziehungsweise für einen bereits beschlossenen technischen Wechsel vorgesehen sind. Die Liste ist bei Änderungen der produktiven Architektur vor Einsatz des neuen Dienstleisters zu aktualisieren.

| Dienstleister | Status | Zweck | Betroffene Datenkategorien | Verarbeitungsort / Drittlandbezug | Vertrags- und Kontrollmaßnahme |
|---|---|---|---|---|---|
| Hetzner Online GmbH | aktiv | Hosting von Website, Backend, Datenbank, Speicher, Backups und technischen Protokollen | Account-, Tenant-, Company-, Scan-, Finding-, Report-, Support- und technische Protokolldaten | Falkenstein, Deutschland / EU | Auftragsverarbeitungsvertrag, Zugriffsbeschränkung, Verschlüsselung, Backup- und Löschkonzept |
| Stripe Payments Europe, Limited | aktiv | Checkout, Zahlungsabwicklung, Abonnement- und Zahlungsstatus | Rechnungs-, Kontakt-, Vertrags-, Zahlungs- und Transaktionsdaten; vollständige Kartendaten werden nicht durch BCSentinel gespeichert | EWR; mögliche konzerninterne oder technische Drittlandverarbeitung nach Stripe-Vertragsunterlagen | Stripe-Datenschutz- und Vertragsunterlagen prüfen, Datenminimierung, Webhook-Signaturen, eingeschränkte Metadaten |
| FormSubmit | vorübergehend aktiv | Weiterleitung von Anfragen des öffentlichen Kontaktformulars | Name, E-Mail-Adresse, Unternehmen, Thema, Nachricht und technische Übermittlungsdaten | nach Anbieter- und Infrastrukturangaben; Drittlandbezug möglich | Nur bis Abschluss von LP-LEGAL-02; keine vertraulichen Inhalte anfordern; anschließend vollständig entfernen |
| Brevo / Sendinblue GmbH | geplant | Transaktionale Zustellung von Kontaktanfragen und später produktbezogenen E-Mails über das eigene Backend | Empfängeradresse, Absender-/Antwortadresse, Betreff, Nachrichteninhalt und technische Zustellinformationen | EU-Konfiguration bevorzugt; konkrete Vertrags- und Infrastrukturangaben vor Aktivierung verifizieren | Auftragsverarbeitungsvertrag, API-Schlüssel nur serverseitig, Datenminimierung, definierte Log- und Löschfristen |

## Änderungsprozess

1. Datenschutz- und Sicherheitsprüfung vor Aktivierung eines neuen Dienstleisters.
2. Abschluss beziehungsweise Prüfung des erforderlichen Auftragsverarbeitungsvertrags.
3. Prüfung von Unterauftragnehmern, Speicherorten und möglichen Drittlandübermittlungen.
4. Aktualisierung dieser Liste, der Datenschutzerklärung, des AVV und der technischen Dokumentation.
5. Technische Entfernung nicht mehr eingesetzter Integrationen und Geheimnisse.

## Kundeninformation

Wesentliche Änderungen an Unterauftragsverarbeitern werden nach Maßgabe des späteren BCSentinel-AVV und der vertraglichen Informationsfristen mitgeteilt. Diese Datei ist die interne führende Betriebsdokumentation und wird für eine veröffentlichte Kundenfassung des AVV aufbereitet.

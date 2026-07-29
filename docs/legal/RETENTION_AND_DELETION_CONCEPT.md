# BCSentinel Lösch- und Aufbewahrungskonzept

Stand: 29. Juli 2026

Verantwortlicher Anbieter: Daniel Wauer, Geschäftsbezeichnung BCSentinel

## Grundsätze

BCSentinel verarbeitet Daten zweckgebunden, mandantengetrennt und nur so lange, wie dies für Produktbetrieb, Vertrag, Sicherheit oder gesetzliche Pflichten erforderlich ist. Gesetzliche Aufbewahrungspflichten gehen einer operativen Löschfrist vor. Nach Fristende werden Daten gelöscht oder, soweit ausreichend, irreversibel anonymisiert.

## Aufbewahrungsmatrix

| Datenkategorie | Regelmäßige Aufbewahrung | Löschereignis / Maßnahme | Verantwortlich |
|---|---|---|---|
| Öffentliche Webserver-Zugriffslogs | 14 Tage | automatische Rotation und Löschung; längere Sicherung nur bei dokumentiertem Sicherheitsvorfall | Betrieb |
| Fehler- und Security-Logs | 90 Tage | automatische Rotation; sicherheitsrelevante Auszüge nur solange der Vorfall bearbeitet oder nachgewiesen werden muss | Betrieb / Security |
| Kontaktformular-Anfragen | Abschluss der Anfrage plus 6 Monate | Löschung, sofern kein Vertrag, keine Rechtsverteidigung und keine gesetzliche Pflicht entgegensteht | Support |
| Erfolglos beendete Partneranfragen | Abschluss plus 6 Monate | Löschung oder Anonymisierung | Partner Operations |
| Aktive Benutzer-, Partner- und Mitgliedschaftskonten | Dauer des Vertrags oder der aktiven Geschäftsbeziehung | Sperrung bei Ende; Löschung nach Ablauf der Nachfrist und gesetzlicher Pflichten | Operations |
| Deaktivierte Konten ohne offene Verpflichtungen | 90 Tage nach Deaktivierung | Löschung oder Anonymisierung; Security-Auditdaten getrennt nach eigener Frist | Operations |
| Tenant-, Environment- und Company-Zuordnung | Dauer des Produktzugriffs plus 90 Tage | Löschung nach Vertragsende, sofern keine Wiederherstellung, Rechtsverteidigung oder Pflicht entgegensteht | Product Operations |
| Scan-Runs, Findings, Scores und Reportdaten | produktabhängig während des Zugriffs; nach Vertragsende grundsätzlich 90 Tage | Löschung oder Anonymisierung nach Ablauf der Nachfrist; kundenseitiger Export vor Ende ermöglichen | Product Operations |
| Temporäre Embed-, Share-, Execution- und Access-Tokens | bis Ablauf, Widerruf oder Abschluss des Vorgangs | automatische Löschung beziehungsweise kryptografische Unbrauchbarkeit | Backend |
| Abrechnungs-, Vertrags- und Zahlungsbelege | nach den jeweils geltenden handels- und steuerrechtlichen Fristen | fristgerechte Löschung nach Ende der gesetzlichen Aufbewahrung | Finance |
| Stripe-IDs und Zahlungsstatus | Vertragsdauer plus gesetzliche Nachweisfrist | Löschung, soweit nicht für Buchhaltung, Rückabwicklung oder Rechtsverteidigung erforderlich | Finance / Backend |
| Backups | rollierend nach produktiver Backup-Policy, Zielwert maximal 35 Tage | automatisches Überschreiben; Wiederherstellung führt nicht zur dauerhaften Reaktivierung bereits gelöschter Datensätze | Betrieb |
| Supportfälle mit Vertragsbezug | Vertragsdauer plus 3 Jahre, soweit für Nachweis oder Rechtsverteidigung erforderlich | Löschung oder Anonymisierung nach Fristende | Support |

## Löschablauf bei Vertragsende

1. Produktzugriff und aktive Tokens werden beendet.
2. Der Kunde erhält Gelegenheit, verfügbare Reports oder Daten innerhalb der vertraglich vorgesehenen Frist zu exportieren.
3. Produktivdaten werden nach der vorgesehenen 90-Tage-Nachfrist gelöscht oder anonymisiert.
4. Daten in rollierenden Backups laufen über die Backup-Frist aus.
5. Abrechnungs- und Vertragsunterlagen bleiben nur im gesetzlich erforderlichen Umfang erhalten.
6. Die Löschung wird technisch protokolliert, ohne gelöschte Inhaltsdaten erneut zu speichern.

## Betroffenenanfragen und Kundenweisungen

Anfragen auf Auskunft, Berichtigung, Einschränkung oder Löschung werden identitäts- und mandantenbezogen geprüft. Soweit BCSentinel als Auftragsverarbeiter tätig ist, erfolgt die Bearbeitung nach dokumentierter Weisung des Kunden als Verantwortlichem. Gesetzliche Aufbewahrungspflichten oder überwiegende Nachweisinteressen werden transparent dokumentiert.

## Technische Umsetzung und Kontrolle

- Löschjobs müssen wiederholbar, fehlertolerant und auditierbar sein.
- Mandanten- und Company-Grenzen sind bei jeder Löschoperation zu erzwingen.
- Backups werden nicht selektiv verändert; gelöschte Daten werden bei Wiederherstellung erneut anhand eines Löschregisters entfernt.
- Fristen und tatsächliche Backend-Jobs werden vor öffentlichem Go-Live und danach mindestens jährlich abgeglichen.
- Abweichungen werden als Security- oder Compliance-Finding dokumentiert und priorisiert behoben.

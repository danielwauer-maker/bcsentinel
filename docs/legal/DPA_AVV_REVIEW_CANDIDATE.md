# BCSentinel Auftragsverarbeitungsvereinbarung (AVV/DPA) – Review Candidate

**Version:** 0.9-review  
**Stand:** 2026-10-10  
**Status:** Interner Review Candidate; keine Rechtsfreigabe.

## 1. Gegenstand und Dauer

BCSentinel verarbeitet im Rahmen der vereinbarten SaaS-Leistungen Daten aus Microsoft Dynamics 365 Business Central, soweit dies für Scan, Analyse, Monitoring, Berichtserstellung, Support und technische Betriebsführung erforderlich ist. Gegenstand, Produktumfang und Laufzeit richten sich nach dem jeweiligen BCSentinel-Vertrag bzw. der aktiven Subscription. Nach Vertragsende gelten die vereinbarten Aufbewahrungs- und Löschprozesse.

## 2. Art und Zweck der Verarbeitung

Die Verarbeitung dient insbesondere der Erkennung und Darstellung von Datenqualitätsproblemen, der Berechnung von Data-Health- und Business-Impact-Modellen, der Erstellung von Findings, Maßnahmen- und Monitoring-Ansichten sowie Executive Reports. BCSentinel nimmt keine fachlichen Änderungen an Business-Central-Stammdaten über das Web-Dashboard vor; operative Änderungen bleiben beim Kunden bzw. in Business Central.

## 3. Kategorien betroffener Personen und Daten

Je nach kundenseitigem Datenbestand können insbesondere Daten von Kunden, Lieferanten, Beschäftigten, Ansprechpartnern und sonstigen Geschäftspartnern verarbeitet werden. Verarbeitete Kategorien können Identifikations-, Kontakt-, Stamm-, Beleg-, Buchungs-, Nutzungs- und technische Metadaten umfassen. Der Kunde bestimmt durch seine Business-Central-Konfiguration und den gewählten Scan-Scope, welche Daten tatsächlich einbezogen werden.

## 4. Weisungen

BCSentinel verarbeitet personenbezogene Daten ausschließlich auf dokumentierte Weisung des Kunden, soweit keine gesetzliche Verpflichtung entgegensteht. Produktkonfiguration, Scan-Scope und freigegebene Supportvorgänge gelten im Rahmen des vereinbarten Funktionsumfangs als dokumentierte Weisungen.

## 5. Vertraulichkeit

Personen mit Zugriff auf personenbezogene Kundendaten werden auf Vertraulichkeit verpflichtet und erhalten nur die für ihre Aufgaben erforderlichen Berechtigungen. Supportzugriff ist grundsätzlich tenantbezogen, zeitlich begrenzt und auditierbar; der Controlled-Pilot-Stand sieht zunächst Diagnostics-only-Zugriff und keine allgemeine Impersonation vor.

## 6. Technische und organisatorische Maßnahmen

Die jeweils gültigen TOMs sind Bestandteil dieses Review Candidates und werden in `docs/legal/TOMS_REVIEW_CANDIDATE.md` geführt. Änderungen dürfen das vereinbarte Schutzniveau nicht wesentlich unterschreiten.

## 7. Unterauftragsverarbeiter

Unterauftragsverarbeiter werden in `docs/legal/SUBPROCESSORS_REVIEW_CANDIDATE.md` dokumentiert. Vor Produktionsfreigabe müssen dort ausschließlich tatsächlich eingesetzte, verifizierte Anbieter aufgeführt werden. Nicht verifizierte Anbieter dürfen nicht als produktiv genutzt dargestellt werden.

## 8. Unterstützung des Verantwortlichen

BCSentinel unterstützt den Kunden im angemessenen Umfang bei Betroffenenrechten, Datenschutz-Folgenabschätzungen, Sicherheitsvorfällen und behördlichen Anfragen, soweit die jeweilige Anfrage die durch BCSentinel verarbeiteten Daten betrifft.

## 9. Meldung von Datenschutzverletzungen

BCSentinel informiert den Kunden nach Bekanntwerden einer Verletzung des Schutzes personenbezogener Daten ohne unangemessene Verzögerung und stellt die verfügbaren Informationen bereit, die der Kunde für seine gesetzlichen Pflichten benötigt.

## 10. Rückgabe, Export und Löschung

BCSentinel führt Export- und Löschanforderungen als nachvollziehbaren Lifecycle-Prozess. Operative Daten, Reports, Logs, Audit-Evidence und Backups können unterschiedlichen Aufbewahrungsfristen unterliegen. Vor Produktivstart müssen die finalen Fristen in Privacy Policy, TOMs, Operations Policy und diesem AVV konsistent festgelegt sein.

## 11. Nachweise und Audits

BCSentinel stellt angemessene Informationen über die Einhaltung dieser Vereinbarung bereit. Audits sollen risikobasiert, verhältnismäßig und unter Wahrung der Sicherheit anderer Mandanten durchgeführt werden.

## 12. Drittlandtransfers

Drittlandtransfers dürfen nur auf einer geeigneten Rechtsgrundlage und unter den erforderlichen Schutzmaßnahmen erfolgen. Vor Produktivstart ist für jeden tatsächlich eingesetzten Unterauftragsverarbeiter zu prüfen und zu dokumentieren, ob ein Drittlandtransfer stattfindet und welche Transfergrundlage verwendet wird.

---

## Offene juristische Freigabepunkte vor PROD

- tatsächliche Vertragspartei / Rechtsform und Vertretungsangaben,
- konkrete produktive Hosting-, E-Mail-, Billing- und Monitoring-Anbieter,
- finale Lösch- und Backup-Fristen,
- Drittlandtransfer-Bewertung,
- Haftungs-/Auditregelungen und Kostenregelung für Sonderaudits,
- Abgleich mit finalen Terms/EULA und Privacy Policy.

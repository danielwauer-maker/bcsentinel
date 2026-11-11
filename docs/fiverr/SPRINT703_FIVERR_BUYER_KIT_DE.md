# Sprint 7.03 – Fiverr-Verkaufs- und Betreuungspaket (DE)

**Status:** Redaktionell fertig vorbereitet; **NICHT ZUR VERÖFFENTLICHUNG FREIGEGEBEN**.  
**Stand:** 11.11.2026 | Excel-Aufgabe **7.03** im Fiverr-Sprint 8 | Deutsche Referenzfassung der vollständigen EN-Fassung `SPRINT703_FIVERR_BUYER_KIT_EN.md`.

## 1. Verbindliches Zielmodell und Angebotsgrenzen

- **Free Entry:** genau ein initialer autorisierter Deep Scan; dauerhafter Free-Aggregatbericht; **kein kostenpflichtiges Fiverr-Angebot**.
- **Full Assessment:** vorgeschlagene Freischaltung der detaillierten Ergebnisse des existierenden initialen Scans für **14 Tage**. Kein zweiter Scan durch Freischaltung. Keine tatsächliche Datensanierung.
- **Renewal:** vorgeschlagen +14 Tage Detailzugriff ohne neuen Scan; je nach endgültiger Preis-/Produktfreigabe als Fiverr-Custom-Offer bzw. geeigneter Follow-up-Prozess.
- **Renewal + Validation:** vorgeschlagen +14 Tage Full-Zugriff und genau **ein** neu autorisierter Validation Scan Credit. Vergleich darf nur bei nachgewiesener Methodik-/Scope-/Record-Evidence-Kompatibilität als „gelöst“/„verbessert“ etc. dargestellt werden.
- **Monitoring:** separate wiederkehrende Leistung; Frequenz, Preis, Kündigungs- und Lieferregeln erst nach operativer Endabnahme verbindlich.
- **Zielsystem:** Microsoft Dynamics 365 Business Central **Online**. Keine Zusage für On-Premises.
- **Volumenklassen:** ≤250.000 / ≤1 Mio. / ≤5 Mio. / ≤20 Mio. / Custom, auf Basis abgeschlossener autorisierter Scan-Daten. USD-Fiverr-Tarife noch nicht freigegeben.
- **Fiverr:** Zahlungen, Preisvereinbarungen, Bestellungen und vertragsbezogene Kommunikation bleiben auf Fiverr. BCSentinel Extension/Backend erfüllt nur die technische Leistung. Keine Off-Platform-Zahlungsaufforderung.

**Harte Grenze:** Das alte `main`-Launch-Kit nennt Quick Assessment, 7 Tage Full und konkrete historische USD-Preise. Diese Aussagen nicht für den geplanten v2-Launch übernehmen. Die neue Access-v2-Semantik steht noch unter Product-Contract-/Runtime-Gates; Pricing nicht erfinden.

## 2. Drei Fiverr-Gigs: Titel, Leistungsbeschreibung, Abgrenzung

### Gig A – Full Assessment

**Titel-Vorschlag (Englisch für Fiverr):** I will audit your Microsoft Dynamics 365 Business Central data quality.

**Deutsche Arbeitsbeschreibung:**

> Ich prüfe die Datenqualität Ihrer Microsoft Dynamics 365 Business Central Online-Umgebung mit BCSentinel. Sie erhalten einen strukturierten Assessment-Bericht zu erkannten Auffälligkeiten, Schweregraden, betroffenen Datensätzen, relevanten Ursachen und modellierten geschäftlichen Auswirkungen, soweit diese zuverlässig berechnet werden können.
>
> Ein neuer Mandant führt nach autorisierter Einrichtung genau einen initialen Data Health Scan durch. Wenn bereits ein geeigneter erster Scan vorhanden ist, wird dessen Ergebnis für das Full Assessment freigeschaltet – ohne zusätzlichen Scan. Der vorgeschlagene Detailzugriff beträgt 14 Tage ab Aktivierung.
>
> Voraussetzung ist ein berechtigter Business-Central-Administrator, der die Erweiterung installiert und einrichtet. Zugangsdaten, API-Tokens oder Datenexporte sind in Fiverr-Nachrichten nicht erforderlich.
>
> Die Leistung umfasst Analyse und Handlungsempfehlungen, nicht die Durchführung von Datenkorrekturen. Finanzielle Auswirkungen sind modellierte Schätzwerte, keine garantierten Verluste oder Einsparungen. Der Preis richtet sich nach dem analysierten Datenvolumen; die endgültige Preisstaffel wird vor Veröffentlichung verbindlich festgelegt.

**Leistungsumfang:** autorisierter BC-Online-Scan oder bestehende Baseline, geprüfter Detailbericht, priorisierte Findings und nachvollziehbare Empfehlungen; kein unbegrenztes Scannen, kein Writeback, keine garantierte Kosteneinsparung.

### Gig B – Validation

**Titel-Vorschlag:** I will validate Business Central data quality improvements after your fixes.

**Deutsche Arbeitsbeschreibung:**

> Nach einem bezahlten BCSentinel Full Assessment und Ihren Datenkorrekturen prüfen wir die Datenqualität erneut. Die Validation umfasst einen autorisierten Folgescan und einen Vergleich mit dem geeigneten ursprünglichen Assessment.
>
> Der Bericht unterscheidet nur dort zwischen nachweisbar veränderten Befunden, wo Methodik, Umfang und unveränderliche Prüfnachweise einen verlässlichen Vergleich erlauben. Nicht vergleichbare Checks werden ausdrücklich als nicht vergleichbar bezeichnet.
>
> Validation ist keine Erstprüfung und keine Datenbereinigung. Die vorgeschlagene Kombination „Renewal + Validation“ enthält weitere 14 Tage Full-Zugriff und genau einen Validation-Scan-Credit; die endgültigen Angebotsbedingungen bedürfen der Freigabe.
>
> Wurde der BC-Mandant oder der Prüfumfang verändert, muss dies vor Bestellung geklärt werden. Sämtliche Bestellung und Vergütung erfolgen über Fiverr.

**Leistungsumfang:** ein autorisierter neuer Scan und belegbarer Vorher-nachher-Bericht, ohne Zusage, dass sämtliche 199 Prüfungen datensatzweise vergleichbar sind.

### Gig C – Monitoring

**Titel-Vorschlag:** I will monitor Microsoft Dynamics Business Central data quality trends.

**Deutsche Arbeitsbeschreibung (NICHT VERÖFFENTLICHEN):**

> BCSentinel Monitoring soll Business Central Online-Umgebungen über regelmäßige autorisierte Scans bei der Überwachung von Datenqualitätsrisiken unterstützen.
>
> Vorgesehen sind ein nachvollziehbarer Verlauf, geeignete Trenddarstellungen und unterstützte Warnungen. Vergleiche werden nur dort angezeigt, wo die zugrunde liegenden Prüfungen und Nachweise kompatibel sind.
>
> Scanfrequenz, Supportumfang, Zugriff während einer aktiven Laufzeit, Kündigung, Aufbewahrung und Preise werden vor dem Launch verbindlich definiert. Automatische Datenkorrekturen, garantierte Einsparungen und nicht vereinbarte SLA-Zusagen sind nicht Bestandteil.
>
> Monitoring wird erst nach erfolgreicher Subscription-, Runtime- und Kundenabnahme angeboten.

**Leistungsumfang:** ausschließlich die später im Kaufvertrag/Subscription-Modell freigegebenen periodischen Prüfungen und Berichte. Kein aktuelles Verfügbarkeitsversprechen.

## 3. Käuferfragen (Fiverr Requirements)

**Für alle Gigs erforderlich:**
1. Nutzen Sie Microsoft Dynamics 365 Business Central Online? (Ja / Nein / Unsicher)
2. Welche Umgebung und welche Gesellschaft/Company sind Gegenstand des Auftrags? (Nur nicht geheime Namen, keine Zugangsdaten.)
3. Kann ein berechtigter BC-Administrator die Erweiterung installieren und konfigurieren? (Ja / Freigabe fehlt / Unsicher)
4. Welches Datenvolumen schätzen Sie? (≤250k / ≤1 Mio. / ≤5 Mio. / ≤20 Mio. / >20 Mio. / Unsicher)
5. Gewünschte Berichtssprache? (Deutsch / Englisch)
6. Bestätigen Sie, keine Passwörter, MFA-Codes, API-Tokens oder andere Geheimnisse über Fiverr zu senden? (Ja / Rückfrage)

**Nur Validation:** Referenz zur vorangegangenen bezahlten Assessment-Bestellung, Zeitraum der Korrekturen, Hinweise auf geänderte Company/Methodik, ohne Rohdaten.

**Nur Monitoring:** Gewünschter Zeitraum und Umfang – erst nach genehmigtem Monitoring-Vertrag verpflichtend verwenden.

**Datenschutz:** Eine technische E-Mail-Adresse für Bericht/Benachrichtigungen wird ausschließlich innerhalb der Extension eingerichtet und nicht als außerhalb von Fiverr erreichbare Verkaufsadresse im Bestellformular angefordert.

## 4. FAQ für die deutschsprachige Betreuung

1. **Ist BCSentinel für Business Central On-Premises geeignet?** Der geplante Fiverr-Launch unterstützt nur BC Online.
2. **Muss ich mein BC-Passwort weitergeben?** Nein. Installation und Autorisierung erfolgen durch Ihren eigenen BC-Administrator.
3. **Werden unsere Datensätze geändert?** Eine automatische Datenbereinigung ist nicht Vertragsbestandteil; der Dienst analysiert und berichtet.
4. **Löst Full Assessment einen zweiten Scan aus?** Nein, es nutzt den autorisierten initialen Scan. Ein noch nicht registrierter Mandant benötigt diesen einmaligen Erstscan.
5. **Wie lange gilt der Full-Zugriff?** Geplant sind 14 Tage ab Aktivierung; verbindlich gelten die später freigegebenen Bestellbedingungen.
6. **Warum können Sie den Preis nicht pauschal nennen?** Wir staffeln nach autorisiert analysiertem Datensatzvolumen; die gültigen Preise stehen im späteren Fiverr-Angebot.
7. **Ist eine errechnete mögliche Einsparung garantiert?** Nein, es handelt sich um modellierte Entscheiderinformationen, nicht um buchhalterisch bestätigte Realized Savings.
8. **Brauche ich vor Validation ein Assessment?** Ja, eine geeignete bezahlte Full-Baseline ist Voraussetzung.
9. **Zeigt Validation immer gelöste und neue Einzelbefunde?** Nein, nur bei nachweisbar vergleichbaren Checks und belegter Identität; sonst steht „nicht vergleichbar“.
10. **Was bedeutet Monitoring?** Nach Freigabe periodische Scans und belegbare Trends im vereinbarten Umfang; Laufzeit und Konditionen werden explizit geregelt.

## 5. Vorlagen für Fiverr-Nachrichten (Deutsch)

**Vor Bestellung:**
> Vielen Dank für Ihr Interesse an BCSentinel. Nutzen Sie Business Central Online und wie groß ist das geschätzte Datenvolumen? Für die Installation wird ein berechtigter BC-Administrator benötigt. Ich prüfe dann gerne, welches Fiverr-Angebot zum gewünschten Umfang passt. Bitte senden Sie keine Zugangsdaten oder vertraulichen Exporte.

**Bestellung eingegangen:**
> Vielen Dank für Ihre Bestellung. Ich prüfe zunächst den vereinbarten Business-Central-Umfang und Ihre Angaben im Fiverr-Bestellformular. Anschließend stimmen wir die autorisierte Installation bzw. den vorhandenen Erstscan ab. Zugangsdaten oder API-Tokens sind hier nicht erforderlich.

**Einrichtung:**
> Bitte installieren Sie die freigegebene BCSentinel-Erweiterung im vereinbarten Business Central Online-Umfeld. Ein berechtigter Administrator hinterlegt die notwendige Zustimmung, Berichtssprache und Benachrichtigungsadresse innerhalb der Erweiterung. Melden Sie hier im Fiverr-Auftrag, sobald die Einrichtung abgeschlossen ist.

**Warten auf Mitwirkung:**
> Die nächste Prüfung kann beginnen, sobald die technische Einrichtung durch Ihren Administrator abgeschlossen wurde. Falls dadurch der vereinbarte Zeitrahmen betroffen ist, stimmen wir die weiteren Schritte über die Fiverr-Auftragsfunktionen ab.

**Scan abgeschlossen, Bericht in Prüfung:**
> Der autorisierte Scan ist abgeschlossen. Ich prüfe derzeit den technischen Nachweis, die Berechtigung und den Bericht. Erst nach dieser Kontrolle erfolgt die Lieferung des freigegebenen Ergebnisses.

**Full Assessment geliefert (nur nach echtem PASS):**
> Ihr BCSentinel Full Assessment für den vereinbarten Business Central Online-Umfang ist abgeschlossen. Der geprüfte Bericht ist diesem Fiverr-Auftrag beigefügt. Er enthält die priorisierten Befunde und, soweit methodisch gestützt, modellierte geschäftliche Auswirkungen. Die Detailzugriffsdauer richtet sich nach den freigegebenen Bestellbedingungen. Der Bericht ist keine Garantie für tatsächliche finanzielle Verluste oder Einsparungen.

**Validation geliefert (nur bei echtem Vergleich):**
> Ihr BCSentinel Validation-Bericht ist beigefügt. Er vergleicht den autorisierten Folgescan mit der geeigneten bezahlten Ausgangsprüfung – ausschließlich dort, wo die verfügbaren Prüfnachweise einen verlässlichen Vergleich zulassen. Nicht vergleichbare Prüfungen sind ausdrücklich gekennzeichnet. Rückfragen zur Darstellung können Sie über diesen Fiverr-Auftrag stellen.

**Validation blockiert:**
> Für einen Teil des vereinbarten Umfangs fehlen derzeit ausreichende technische Vergleichsnachweise. Deshalb werde ich keine unbestätigten Verbesserungen als gelöst darstellen. Wir klären die zulässigen nächsten Schritte sowie gegebenenfalls eine Anpassung des Auftrags direkt über Fiverr.

**Monitoring-Bericht (nur nach Release-GO):**
> Der vereinbarte Monitoring-Zeitraum ist abgeschlossen. Der freigegebene Periodenbericht ist beigefügt. Er zeigt die unterstützten Trends einschließlich technischer Einschränkungen im Rahmen Ihrer aktiven Vereinbarung.

**Darstellungskorrektur:**
> Vielen Dank für den Hinweis. Ich kann den bestehenden Bericht erläutern und Darstellungsfehler anhand derselben bestätigten Scandaten korrigieren. Ein neuer Scan, zusätzliche Gesellschaften oder die eigentliche Datenbereinigung sind nicht Bestandteil dieser Revision.

**Datenvolumen größer als bestellt:**
> Der abgeschlossene autorisierte Scan ergibt eine höhere Datenvolumenklasse als ursprünglich angegeben. Bevor zusätzliche kostenpflichtige Berichtsinhalte freigegeben werden, klären wir den korrekten Leistungsumfang und mögliche Unterschiede ausschließlich über Fiverr.

**Technischer Fehler:**
> Bei einem technischen Prüfschritt ist ein Problem aufgetreten. Ich untersuche es, ohne dass Sie Zugangsdaten oder vertrauliche Datensätze übermitteln müssen. Falls eine Änderung der Lieferfrist nötig wird, verwenden wir die vorgesehenen Fiverr-Auftragsfunktionen.

**Auftrag abschließen:**
> Vielen Dank für die Prüfung des Berichts. Bei einer Darstellungsfrage innerhalb der vereinbarten Revision antworten Sie bitte direkt über diesen Fiverr-Auftrag. Für weitere Folgescans oder zusätzlichen Umfang ist eine gesonderte Vereinbarung erforderlich.

## 6. Interner Ablauf: Auftrag → Lieferung

1. Fiverr-Bestellung und Zahlung bestätigen, aber **keine** Providerzahlung im BCSentinel-Backend als bewiesen voraussetzen.
2. Order-ID und freigegebene Ziel-Company/Environment im internen Operator-Audit verknüpfen; keine Secrets in Tickettext.
3. Produkt, Datenvolumen, Berechtigungen und Erstscan-/Folgescananspruch gegen den freigegebenen Vertrag prüfen.
4. Tenant registrieren, einmaligen Erstscan kontrollieren bzw. bestehende zulässige Baseline zuordnen.
5. Erst nach Prüfung genau das gekaufte Access-Entitlement und den passenden Credit gewähren.
6. Report auf Aktualität, Datenfreigabe, Tenant-/Company-Isolation, Unveränderlichkeit und Kompatibilität prüfen.
7. Nur geprüfte PDF-/Report-Inhalte über den entsprechenden Fiverr-Auftrag liefern; befristete Reportlinks nicht als dauerhafte Sharelinks darstellen.
8. Eine vereinbarte Revision beschränkt sich auf Darstellung und Erläuterung derselben Scandaten.
9. Bei Zahlungs-/Volumen-/Evidence-/Runtime-Abweichung **BLOCKED**, nicht „erledigt“; Entscheidung und Kommunikation über Fiverr dokumentieren.
10. Auftragsabschluss und eventuellen Follow-up-Prozess dokumentieren; keine ungeprüfte automatische Kündigungs-/Monitoring-Zusage.

## 7. Sperren vor endgültiger Veröffentlichung

- [ ] Genehmigtes Product-System-v2-Modell, insbesondere Renewal, standalone Validation, Monitoring und Full 14 Tage.
- [ ] Konkrete Fiverr-USD-Preise, Lieferfristen, Revisionen, Paketvarianten und Volumengrenzen freigegeben.
- [ ] BC27-Runtime und Non-SUPER/E2E tatsächlich PASS.
- [ ] Full-, Validation- und Monitoring-Berichte entsprechend ihrem jeweiligen Scope wirklich nachgewiesen; kein erfundener Vergleich.
- [ ] Monitoring Subscription, Historie, Laufzeit, Kündigung, Support und Lieferprozesse PASS.
- [ ] Datenschutz-/AVV-/Hosting-/Datenfluss-Aussagen rechtlich und tatsächlich freigegeben.
- [ ] Fiverr-Formular, Kategorien, Galerie, Accountfreigaben und Testbestellung geprüft.
- [ ] Finales PROD-GO und Freigabe zur Aktivierung der Gigs dokumentiert.

**Ergebnis:** Redaktionelles DE/EN-Arbeitspaket vollständig; **Go-Live-Freigabe noch offen**. Alte Quick-/7-Tage-Fiverr-Texte aus dem historischen `main` nicht live übernehmen.


## 6. Ergänzende Käuferreise und Sonderfälle

Die zweisprachigen Vorlagen zu Scanfehlern, abgelaufenen Berichtslinks, strittigen Zahlungen, Erstattungen, Stornierung und eingeschränkter Vergleichbarkeit sowie die detaillierte Acceptance-Matrix stehen in [`SPRINT703_BUYER_JOURNEY_AND_ACCEPTANCE.md`](SPRINT703_BUYER_JOURNEY_AND_ACCEPTANCE.md). **Wichtig:** Auf Core `main` gilt noch das historische Quick-/7-Tage-Modell als dokumentierter Altstand; das hier beschriebene 14-Tage-Zielmodell von PR #154 ist nicht genehmigt oder live abgenommen. Eine Erstattung wird nicht automatisch zugesagt. Bereits verbrauchte Scanrechte und historische Ergebnisse dürfen nicht ohne genehmigte Regeln verändert werden.

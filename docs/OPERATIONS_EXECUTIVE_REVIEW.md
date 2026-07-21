# Operations Executive Review

Stand: 2026-07-21

## Würde ich persönlich den Betrieb dieses Systems verantworten?

Für einen eng begrenzten, aktiv betreuten Pilot: **ja, unter Bedingungen**. Für einen unbeaufsichtigten Enterprisebetrieb: **nein**.

Das System besitzt echte betriebliche Substanz. Startupvalidierung, Migration-Gate, strukturierte Logs, Request-IDs, Healthchecks, Retry-/Recoverymechanismen, ein non-root Container und eine breite Backend-Testbasis zeigen verantwortungsbewusstes Engineering. Diese Bausteine reichen aus, damit ein kleines Kernteam einen Pilot kontrolliert führen kann.

Sie reichen nicht aus, um langfristige Enterprise-Betriebsverantwortung zu übernehmen. Heute könnte ein Deployment ungetesteten Code direkt ausliefern. Ein Produktionsausfall könnte zuerst vom Kunden entdeckt werden. Backup, Restore und Rollback sind beschrieben, aber nicht bewiesen. Bei Hostverlust existiert kein getesteter Wiederanlauf mit RTO/RPO. Security- und Adminzugriffe sind nicht für ein wachsendes Operator-Team organisiert. Lastgrenzen sind unbekannt. Das ist keine Frage von Optimismus, sondern fehlender Beweiskette.

## Welche Betriebsrisiken akzeptiere ich?

Für einen vertraglich begrenzten Pilot akzeptiere ich:

- Single-Host- und Single-Instance-Betrieb bei niedriger, kontrollierter Last;
- einen modularen Monolithen statt vorzeitiger Microservices;
- manuelle tägliche Betriebschecks;
- founder-led Support mit namentlichem Backup;
- manuelle Releasefreigabe und Kundenkommunikation;
- begrenzte Servicezeiten ohne öffentliches 24/7-SLA;
- dokumentierte technische Schulden ohne unmittelbaren Daten-, Tenant- oder Recoveryeffekt.

Ich akzeptiere diese Risiken nur mit Owner, Ablaufdatum, Abbruchkriterium und offener Kommunikation an den Pilotkunden.

## Welche Risiken akzeptiere ich niemals?

- Produktionsdeployment ohne grünen, commitgebundenen Testnachweis.
- Unbekannten oder ungeprüften Cross-Tenant-Zugriff.
- Betrieb ohne verwertbares, überwachtes und erfolgreich wiederhergestelltes Backup.
- Unbemerkten Ausfall ohne Alarm und benannten Incident Owner.
- Gemeinsame privilegierte Zugänge ohne Nachvollziehbarkeit.
- Nicht rotierbare oder unkontrolliert offengelegte Secrets.
- Irreversible Migration ohne Backup, Vorprüfung und Recoveryentscheidung.
- Verschleierung fehlender Evidenz gegenüber Kunden oder Unternehmensführung.
- Enterprise-SLA ohne SLO-, Capacity-, On-call- und DR-Fähigkeit.
- Skalierung auf mehrere Instanzen, solange Jobownership, Rate Limits und Datenbankverhalten ungeklärt sind.

## Welche drei Investitionen erhöhen die Betriebssicherheit am stärksten?

1. **Release Safety:** CI-Testgates, immutable Image-Promotion, Release Manifest, Environment Approval sowie nachgewiesener Migration-/Rollbackpfad. Diese Investition schützt jede zukünftige Änderung.
2. **Observability und Incident Operations:** zentrale Logs, Metriken, Traces, Alerts, SLOs, On-call, Runbooks und Übungen. Diese Investition verkürzt unbekannte Ausfälle und schützt Kundenvertrauen.
3. **Recoverability und Security Operations:** automatisierte Off-host-Backups, Restore-/DR-Drills, RTO/RPO, Admin-RBAC, Secret Lifecycle und Access Reviews. Diese Investition begrenzt existenzielle Unternehmensrisiken.

## Welche Bereiche besitzen bereits Enterprise-Niveau?

- **Request-Korrelation und strukturierte Logging-Grundlage:** technisch klar und testbar.
- **Schema- und Startup-Schutz:** Backend startet nicht still auf falschem Alembicstand oder kritischer Fehlkonfiguration.
- **Transaktionale Scan-Lifecycle-Grundlagen:** Idempotenz, Leases, Retry und Recovery zeigen reife Failure-Denke.
- **Container-Runtime-Grundlage:** gepinnte Pakete, Chromium-Buildprüfung und non-root Runtime.
- **BC-Berechtigungsmodell:** fünf getrennte Permission Sets sind eine gute Least-Privilege-Basis.
- **Evidenzorientierte Dokumentation:** Risiken werden in Runbooks, Checklisten und Product Master Book ungewöhnlich offen benannt.

„Enterprise-Niveau“ bezeichnet die Qualität dieser einzelnen Grundlage, nicht die Freigabe des Gesamtsystems.

## Welche Bereiche verhindern heute einen unbeaufsichtigten Enterprise-Go-Live?

- CI/CD ohne Testgate und kontrollierte Artefaktpromotion.
- fehlendes Produktionsmonitoring, Telemetrie und Alerting.
- nicht operationalisierte Backup-, Restore-, Rollback- und DR-Fähigkeit.
- keine native AL-Regression und keine Performance-/Capacity-Evidenz.
- Single-Host-Topologie ohne HA-/Failoververtrag.
- unzureichende Admin-RBAC-, MFA-/SSO- und Secret-Governance.
- founder-abhängiger Incident- und Supportbetrieb.
- fehlende normative SLO-, RTO/RPO-, On-call- und Operations-Governance.

## Welche organisatorischen Prozesse fehlen?

- Release Owner, approvierter Release Candidate und formales Go/No-Go.
- Change Management mit Vier-Augen-Freigabe für kritische Konfiguration.
- On-call-Rotation, Incident Commander, Severity und Eskalationszeiten.
- Kundenkommunikation, Statuspage und Postmortem-Prozess.
- Backup Owner, Restore-/DR-Kadenz und evidenzbasierte RTO/RPO-Prüfung.
- Access Reviews, Joiner/Mover/Leaver und Break-glass-Governance.
- Secretrotation, Vulnerability Management und Patch-SLA.
- Capacity Planning und regelmäßige Performance-Baselines.
- Support Intake, Ticketownership, Wissensbasis und Problem Management.
- regelmäßige Runbooktests und Betriebsübergabe an eine zweite Person.

## Founder Decision

# NEIN

Wenn BCSentinel mein eigenes Unternehmen wäre, würde ich den **unbeaufsichtigten Enterprise-Betrieb heute nicht verantworten**.

Die Entscheidung ist eindeutig, weil mehrere existenzielle Risiken gleichzeitig unkontrolliert sind: Ein Release kann ohne Testgate live gehen, ein Ausfall muss nicht automatisch alarmieren, ein Restore ist nicht bewiesen, ein Hostverlust hat keinen getesteten DR-Pfad, privilegierte Zugriffe sind nicht enterprise-gerecht delegierbar und die Lastgrenze ist unbekannt. Jedes dieser Themen allein wäre ein ernstes Gate; zusammen schließen sie eine verantwortbare unbeaufsichtigte Freigabe aus.

Die Entscheidung ist keine Abwertung des Produkts. Der technische Kern ist weit genug, um einen bewusst manuellen Pilot unter starker persönlicher Betreuung zu rechtfertigen. Ein Pilot erzeugt jedoch keine automatische Enterprise Operations Readiness. Der Übergang gelingt erst, wenn Betriebssicherheit als eigenes System aus Automatisierung, Observability, Recoverability, Security Operations und organisatorischer Verantwortung aufgebaut und durch Drills bewiesen wurde.

## Maximal zehn Maßnahmen mit höchstem Unternehmenswert

1. **P0 — CI vor CD erzwingen:** Backend-, PostgreSQL-/Migrations-, Contract- und Securitytests müssen jeden Deploy blockieren können.
2. **P0 — Immutable Releases einführen:** Ein Image einmal bauen, scannen, signieren und per Digest mit Release Manifest promoten.
3. **P0 — Monitoring und Alerting etablieren:** Availability, 5xx, Latenz, Ressourcen, DB, Jobs und Backups mit Owner und Runbook überwachen.
4. **P0 — Backup/Restore beweisen:** automatisiertes verschlüsseltes Off-host-Backup und wiederholten gemessenen Restore-Drill einführen.
5. **P0 — Incident Operations aufbauen:** On-call, Severity, Incident Commander, Kundenkommunikation, Postmortem und Übungen.
6. **P0 — Admin- und Secret-Governance schließen:** benannte Least-Privilege-Identitäten, MFA/SSO-Ziel, Access Reviews, Break-glass und Rotation.
7. **P1 — AL-Regression operationalisieren:** native AL-Test-App und automatisierte BC-Sandbox-Pipeline für Install, Upgrade, Permissions und Scheduler.
8. **P1 — Performance und Capacity belegen:** realistische Last-/Soaktests, SLOs, Datenwachstum und Ressourcenbudgets messen.
9. **P1 — Skalierungsarchitektur entscheiden:** Single-Instance-Grenze, Jobownership, verteilte Rate Limits, DB-HA und Failure Domains normativ festlegen.
10. **P1 — Operations Governance im Product System verankern:** SLO, RTO/RPO, Release, Incident, Support, Security Operations und Runbook-Review als verbindliche Verträge definieren.

Die P0/P1-Angaben sind Empfehlungen für die nächste Planungsentscheidung, keine bestehende Roadmap. Im formalen Product-Intelligence-Assessment bleiben `priority=null` und `target_release=unassigned`.

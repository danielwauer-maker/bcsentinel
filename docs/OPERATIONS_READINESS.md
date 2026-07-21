# Operations Readiness

Stand: 2026-07-21

Grundlage: [Operations Assessment](OPERATIONS_ASSESSMENT.md), Repository-HEAD `c3fa58734086e2f44fe29f6413ed0433be5c460e`.

## Readiness-Vertrag

Readiness ist eine regelbasierte Sicht und weder Prozentwert noch Durchschnitt. Zustände:

- **Ready:** notwendige Gates sind mit aktueller, reproduzierbarer Evidenz erfüllt.
- **Ready with Conditions:** ein eng definierter Betriebsmodus ist möglich, wenn benannte Bedingungen vor Start geschlossen und während des Betriebs kontrolliert werden.
- **Blocked:** mindestens ein notwendiges Gate ist verletzt oder nicht belegt.
- **Evidence Missing:** die Aussage kann ohne fehlenden Nachweis nicht positiv getroffen werden.

## Operational Readiness — Blocked

**Zweck:** Beurteilt, ob ein Betriebsteam die Plattform zuverlässig überwachen, steuern, diagnostizieren und wiederherstellen kann.

**Einflussgrößen:** Deployment, Scheduler, Background Jobs, Monitoring, Logging, Telemetry, Health Checks, Alerting, Backup, Restore, Incident Response und Administration.

**Interpretation:** Strukturierte Logs, Request-IDs, Healthchecks und Runbooks sind brauchbare Grundlagen. Ein Team kann den Betrieb jedoch nicht zuverlässig übernehmen, weil zentrale Monitoring-/Alerting-/Telemetry-Fähigkeiten, nachgewiesene Recovery und formale On-call-/Incident-Prozesse fehlen.

**Blocker:** zentrale Betriebsüberwachung; Alarmierung mit Owner/Runbook; Backup-/Restore-Drill; Incident-RACI und On-call; Runbooktest; benannte Betriebsgrenzen.

## Deployment Readiness — Blocked

**Zweck:** Beurteilt, ob ein freigegebener Stand reproduzierbar, kontrolliert und sicher ausgeliefert sowie zurückgenommen werden kann.

**Einflussgrößen:** Release Management, CI/CD, Build Pipeline, Migrationen, Environment-, Configuration- und Secrets Management.

**Interpretation:** Der technische Deploypfad funktioniert konzeptionell. Er baut jedoch auf dem Zielhost aus dem Branch, führt keine Tests vor Deployment aus, besitzt kein Environment Approval, kein immutable Artefakt und keinen bewiesenen Rollback. Ein grüner Healthcheck ersetzt keine Release Safety.

**Blocker:** Required CI Gates; Release Manifest; Image-Digest/Provenance; kontrollierte Promotion; Migrations-/Rollback-Drill; Environment- und Secret-Governance.

## Support Readiness — Ready with Conditions

**Zweck:** Beurteilt, ob Incidents und Kundenprobleme eines eng begrenzten Piloten diagnostiziert, kommuniziert und gelöst werden können.

**Einflussgrößen:** Logging, Health, Supportfähigkeit, Incident Response, RBAC, Administration und Operational Documentation.

**Interpretation:** Für 1–3 handgeführte Kunden kann das Kernteam mit Tenant-, Run- und Request-IDs sowie Adminfunktionen Support leisten. Dies ist founder-led Support, kein skalierbarer Enterprise-Support.

**Bedingungen:** namentlicher Primary/Backup Owner; definierter Supportkanal; Severity und Eskalation; sichere Diagnoseanleitung; tägliche Betriebschecks; kein unbeaufsichtigter 24/7-SLA; dokumentierte Kundenkommunikation.

## Security Operations Readiness — Blocked

**Zweck:** Beurteilt, ob betriebliche Zugriffe, Secrets, Security-Signale, Schwachstellen und Incidents professionell gesteuert werden.

**Einflussgrößen:** Secrets Management, RBAC, Operational Security, Logging, Telemetry, Alerting, Incident Response und Administration.

**Interpretation:** Mehrere technische Controls sind solide. Die operative Sicherheitsorganisation fehlt: keine benannten Operatoridentitäten im Backend-Admin, keine MFA-/SSO-Evidenz, keine Secretrotation, keine Detection-/SIEM-Kette, kein Vulnerability-/Patchprozess und kein Security-Incident-Drill.

**Blocker:** benannte Least-Privilege-Identitäten; Secret Lifecycle; Access Review; Vulnerability/Patch Governance; Security Detection; Security-Incident-Playbooks und Übung.

## Pilot Operations Readiness — Ready with Conditions

**Zweck:** Beurteilt, ob ein begrenzter Enterprise-Pilot im bewusst manuellen Single-Instance-Betriebsmodell verantwortbar ist.

**Einflussgrößen:** alle Operations-Capabilities, jedoch mit explizit begrenztem Kundenzahl-, Last-, SLA- und Supportkontext.

**Interpretation:** Ein handgeführter Pilot kann verantwortet werden, wenn er als kontrollierte Lernphase und nicht als unbeaufsichtigter Enterprisebetrieb geführt wird. Der aktuelle Code und die Runbooks liefern genug Substanz; die fehlende Betriebsautomation muss durch konkrete menschliche Kontrollen ersetzt werden.

**Bedingungen vor Start:**

- ein fixierter Commit, getestetes Image und dokumentierte Konfiguration;
- grüner Backend-/PostgreSQL-Release-Candidate-Lauf und aktuelle BC-Sandbox-Abnahme;
- manuell ausgeführtes Deployment- und Rollbackprotokoll;
- erfolgreicher, gemessener Backup-/Restore-Drill;
- benannter 24/7 erreichbarer Incident Owner während kritischer Pilotphasen;
- tägliche Health-/Log-/Job-/Backup-Kontrolle und dokumentierte Eskalation;
- streng begrenzte Adminrechte und rotierbare Secrets;
- keine zugesagte horizontale Skalierung oder Enterprise-SLA;
- klare Abbruchkriterien bei Daten-, Tenant-, Zahlungs- oder Recoveryrisiko.

## Enterprise Go-Live Readiness — Blocked

**Zweck:** Beurteilt, ob BCSentinel ohne Sonderbetreuung für mehrere Enterprise-Kunden langfristig sicher, stabil und professionell betrieben werden kann.

**Einflussgrößen:** sämtliche 29 bewerteten Capabilities.

**Interpretation:** Nicht freigabefähig. Die Blockade folgt nicht aus einer einzelnen fehlenden Funktion, sondern aus einer ungeschlossenen Betriebskette: ungegatetes Deployment, fehlende Observability/Alerts, unbewiesene Recovery, fehlende AL-/Performance-Evidenz, Single-Host-Topologie, schwache Admin-RBAC- und Secret-Governance sowie founder-abhängiger Support.

**Blocker:**

- CI/CD mit releaseblockierenden Tests und immutable Promotion;
- Monitoring, Telemetry, Alerting und SLOs;
- automatisiertes Backup plus wiederholte Restore-/DR-Drills mit RTO/RPO;
- professionelle Incident-, On-call- und Supportorganisation;
- Admin-RBAC, MFA/SSO-Ziel und Secret Lifecycle;
- native AL-Regression und produktionsnahe Performance-/Mehrinstanztests;
- dokumentierte Capacity-, HA- und Scaling-Entscheidung;
- nachgewiesene Release-, Migration- und Rollback-Sicherheit.

## Nicht abgeleitete Aussagen

Diese Readiness bewertet keine Produktfunktion, Customer Experience, Landingpage, Dashboard UX, Scan Engine, Executive Reports, Pricing, Branding oder Marketing. `Blocked` bedeutet nicht, dass die Anwendung nicht läuft; es bedeutet, dass unbeaufsichtigte Enterprise-Betriebsverantwortung nicht evidenzbasiert übernommen werden kann.

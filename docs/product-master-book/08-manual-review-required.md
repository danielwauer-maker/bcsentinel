# Manuell zu prüfen

| Komponente | Grund | Benötigte Umgebung | Vorbereitung / Nachweisform |
|---|---|---|---|
| BC Extension | Installation, UI-Ablauf, TaskScheduler und API-Kommunikation nicht statisch ausführbar | BC 27 Sandbox, Extensionpaket, Testtenant | Acceptance-Protokoll, Telemetrie, Screenshots |
| Berechtigungen | Verhalten ohne `SUPER` und mit fünf Permission Sets | BC Sandbox, Rollenmatrix | Negativ-/Positivprotokoll |
| Upgrade | Install-/Upgrade-Codeunits existieren; veröffentlichter Versionssprung nicht ausgeführt | BC Sandbox mit Vorversion | Upgradeprotokoll und Datenvergleich |
| Stripe | echte Checkout-, Webhook-, Portal-, Refund-/Fehlerabläufe | Stripe Testmode, Webhookziel | Provider-Events und DB-Diff |
| E-Mail | SMTP-Zustellung und Darstellung in Clients | Test-SMTP, Outlook/Gmail/mobile Clients | Zustelllogs und Screenshots |
| Dashboard/Landingpage | visuelle Qualität, mobile Darstellung, Browser- und Tastaturverhalten | unterstützte Browser/Geräte | Browser-Matrix, Accessibility-Review |
| Kanonische Website | `landingpage/` ist paketiert, aber seine öffentliche Produktionsauslieferung ist nicht abschließend belegt; `landingpage_neu/` hat keine Deploymenteinbindung | Produktionsrouting, Hosting-/DNS-Konfiguration, Produktentscheidung | dokumentierte kanonische Quelle und Deploymentpfad |
| PDF | Seitenumbrüche, Fonts und große reale Datensätze | gebautes Backendimage mit Chromium | visuelle PDF-Freigabe und Extraktionscheck |
| Tenant Isolation | statische Guards und Tests existieren; reale parallele Tenantnutzung | PostgreSQL-Staging, mehrere Tenants | Request-/DB-Audit |
| Performance | keine Lastsuite | produktionsnahe Daten/Topologie | Lastprofil, Latenz-/Ressourcenmessung |
| Backup/Restore | nur Betriebsdokumentation nachgewiesen | isolierte PostgreSQL-Umgebung | Restore-Drill und Konsistenzcheck |
| Deployment | SSH/Docker-Ablauf und Healthchecks vorhanden, Rollbackwirkung extern | Stagingserver | Deployment-/Rollbackprotokoll |
| Datenschutz/Legal | technische Dokumente und Rechtstext-Platzhalter ersetzen keine fachliche Prüfung | juristische/fachliche Review | freigegebene Fassungen |

Keine Reihenfolge oder Priorität ist mit der Tabellenposition verbunden.

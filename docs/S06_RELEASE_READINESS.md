# S06 Release Readiness

Stand: 04.10.2026

## Ziel

S06 konsolidiert die bereits vorhandene Installations-, Upgrade-, Backup-/Restore- und Betriebs-Evidenz in einen aktuellen Release-Readiness-Vertrag. Der Sprint darf keinen finalen Release Candidate behaupten, solange Commit, Buildartefakt, Hash und reale Recovery-/Pilot-Gates nicht abgeschlossen sind.

## Bereits verifizierte Evidenz

- Fresh Installation in einer Business-Central-SaaS-Sandbox: `VERIFIED_WITH_KNOWN_DEFECTS`
- Upgrade 1.0.2.16 → 1.0.2.20 inklusive Daten-, Historien- und Scheduler-Erhalt: `PASS_WITH_KNOWN_DEFECTS`
- PostgreSQL-16 Backup/Restore mit Revisions-, Tabellen- und Datenintegritätsvergleich: `VERIFIED_IN_CI`
- Operator Alerting / Incident-Basis: `VERIFIED_IN_CI`

Diese Nachweise werden referenziert und nicht dupliziert.

## Aktuelle Extension-Baseline

Die aktuelle Source-of-Truth-Version in `bc-extension/app.json` und `bc-extension/app.cloud.json` ist 1.0.2.22. Die ältere EXT-50-01-Release-Baseline für 1.0.2.20 bleibt historische Evidenz und darf nicht als aktueller Release Candidate interpretiert werden.

## Rollback- und Recovery-Policy

BCSentinel bevorzugt nach einem ausgeführten Schema-/Extension-Upgrade einen kontrollierten Roll-forward. Backend und Extension werden als kompatibles Paar behandelt. Vor destruktiven Recovery-Schritten muss ein verwertbarer Datenbank-Restore-Punkt existieren. Automatisches Löschen von Tenant-, Scan-, Finding- oder Extensiondaten ist kein zulässiger Rollbackmechanismus.

## Noch offene manuelle Gates

- finalen Release-Candidate-Commit einfrieren
- finalen APP-Artefaktnamen und SHA-256 aus dem grünen Build binden
- Restore auf realer Pilot-Infrastruktur mit gemessenem RPO/RTO
- ungefährlichen BC-Sandbox-Rollback-/Roll-forward-Drill durchführen
- Pilotfreigabe dokumentieren
- Signing/AppSource nur dann schließen, wenn diese Distribution im Releaseumfang liegt

## Definition of Done dieses automatisierten Vorziehens

Der automatisierbare S06-Anteil ist erfüllt, wenn:

1. aktuelle AL-Manifeste identisch sind,
2. Release-Metadaten mit der aktuellen Source of Truth übereinstimmen,
3. historische Evidenzpfade vorhanden und maschinenlesbar referenziert sind,
4. die Recovery-Policy nicht-destruktiv und fail-safe bleibt,
5. kein finaler RC-SHA oder Artefakthash erfunden wird,
6. CI eine eigenständige S06-Evidenz erzeugt.

Damit wird S06 technisch bis an die echten manuellen Release-/Recovery-Gates vorgezogen, ohne deren PASS vorzutäuschen.

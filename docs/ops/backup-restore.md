# Backup and Restore

Status: E5 automation prepared; real off-host restore evidence still required before official E5 completion.

## Automated recovery evidence

BCSentinel now provides reusable PostgreSQL backup/restore scripts plus the `E5 Recovery Automation Quality Gate`.

The CI drill:

1. Starts PostgreSQL 16.
2. Migrates a fresh source database to the current Alembic head.
3. Writes a deterministic recovery probe.
4. Creates a PostgreSQL custom-format dump.
5. Generates SHA-256 checksum and JSON manifest containing the schema revision.
6. Restores the dump into a separate isolated database.
7. Verifies the restored recovery probe and Alembic revision.
8. Uploads the non-production CI recovery evidence for seven days.

Reusable scripts:

```bash
bash scripts/backup_postgres.sh artifacts/recovery
bash scripts/restore_postgres.sh artifacts/recovery/<backup>.dump
```

The scripts receive credentials exclusively through standard PostgreSQL environment variables. They do not package `.env` files or application secrets into the backup artifact.

## Pilot backup minimum

- Run a database backup at least daily during pilot operation.
- Store production backups encrypted and outside the application host.
- Keep at least 7 daily backups for pilot operation unless the customer agreement says otherwise.
- Protect deployment configuration/secrets separately; database backups alone are not enough to restore service.
- Record checksum, timestamp, database/schema revision and retention evidence.

## Real restore acceptance still required

CI proves that the backup format and restore mechanics are technically recoverable, but it is not production disaster-recovery evidence. Before the first paid/controlled production pilot, perform one real restore from an encrypted off-host backup into an isolated environment and document:

- Backup timestamp and storage location/class.
- Encryption and checksum verification result.
- Restore start/end time and measured duration.
- Restored Alembic revision.
- `/health/ready` result against the restored database.
- Known tenant/sample data verification.
- Operator and evidence date.
- Accepted RTO/RPO target and whether the drill met it.

## Reverse proxy and HTTPS

- Terminate TLS in the approved reverse proxy/load-balancer path.
- Expose the backend only through HTTPS.
- Keep compose backend ports bound to loopback where the reverse proxy runs on the same host.
- Forward the required proxy headers/request IDs according to the deployment contract.
- HSTS must only be emitted for HTTPS production traffic.

## Sprint boundary

Automated CI recovery evidence is **preparation**, not official E5 completion. E5 becomes acceptance-ready only when the real off-host restore, measured RTO/RPO and restored application/tenant checks have been recorded.

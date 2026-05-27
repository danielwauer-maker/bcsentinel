# Scan Stability Layer

Phase 1 adds a persistent scan status layer so users can always distinguish queued, active, completed, failed, stalled, and cancelled scans.

## Status Model

Supported statuses:

- `queued`
- `preparing`
- `running`
- `finalizing`
- `completed`
- `failed`
- `stalled`
- `cancelled`

Backend status is stored in `scan_run_statuses` with `run_id`, `tenant_id`, optional company/environment, `scan_mode`, progress, current module/step, heartbeat timestamps, completion/failure timestamps, warnings, errors, ETA, and module counters.

Module progress is stored in `scan_run_modules`. Short non-sensitive progress messages are stored in `scan_run_events`.

## Polling Flow

Business Central starts a scan with a queued status and opens the Deep Scan Monitor. The monitor refreshes on open and through the visible Refresh action. Where supported by the BC client, background refresh remains non-blocking and avoids long synchronous loops.

The monitor calls:

- `GET /scan/status/{run_id}`
- `GET /scan/status/latest`

Status responses include the current status, progress percentage, current module/step, heartbeat timestamp, ETA, module progress, recent events, and error/warning text.

## Heartbeat

The backend helper `update_scan_progress(...)` updates:

- `status`
- `progress_percent`
- `current_module`
- `current_step`
- `updated_at`
- `heartbeat_at`
- optional scan event

The BC deep scan runner sends progress at scan start, module start, module completion, finalizing, completion, and failure. If the backend cannot be reached, the local scan continues and the monitor shows a warning on refresh.

## Watchdog

`mark_stalled_scans()` marks active scans as `stalled` when `heartbeat_at` is older than `SCAN_STALLED_AFTER_SECONDS`.

Default:

- `SCAN_STALLED_AFTER_SECONDS=180`
- `SCAN_MAX_RUNTIME_SECONDS` is reserved for a future hard runtime guard.

The watchdog runs during status polling and can also be used from a maintenance job.

## Failure States

Failed scans set:

- `status=failed`
- `failed_at`
- `error_code`
- `error_message`
- error-level event

This prevents long-running scans from remaining indefinitely in `running`.

## UI Behavior

The BC Deep Scan Monitor shows:

- Run ID
- Status
- Progress %
- Current Module
- Current Step
- Last Heartbeat
- Estimated Remaining Time
- Module Progress
- Recent Events
- Warning and Error panels

Status labels are English source text in AL and translated through XLIFF.

## Event Privacy Rules

Events must not contain customer names, vendor names, item names, email addresses, document numbers, or other personal/business-sensitive record identifiers.

Allowed event content:

- module name
- check name
- aggregate counts
- technical status messages

The backend redacts email-like values before storing event messages.

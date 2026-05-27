# Scan Monitor Debug Audit

## Build Marker

The scan monitor page shows this temporary marker:

`ScanMonitorFix v2`

If this marker is not visible in Business Central, the running sandbox does not contain the fixed app package.

## Root Cause Found

The monitor still had automatic page lifecycle refresh logic:

- `OnAfterGetCurrRecord` queued a background task.
- The background task completion called `ReloadMonitor()`.
- `ReloadMonitor()` called `ApiClient.RefreshScanStatus(...)`.
- `RefreshScanStatus(...)` modified the same scan run record.
- The page then called `CurrPage.Update(false)`.

That means the page could still update and modify its source record while it was being opened or refreshed by the client.

The scan start flow also opened `DH Deep Scan Monitor` immediately after task creation, while the background scan and backend status updates could still modify the same run.

## Current Safe Flow

Deep scan start now does this:

1. Create the run record.
2. `Commit()`.
3. Send the queued status to the backend.
4. Create the background task.
5. Store the task id.
6. `Commit()`.
7. Show a message with the run id.
8. Do not open the monitor automatically.

The monitor can be opened from scan history or an existing monitor action.

## Monitor Page Lifecycle

`DH Deep Scan Monitor` now follows these rules:

- `OnOpenPage` only calculates display variables.
- `OnAfterGetRecord` only calculates display variables.
- `OnAfterGetCurrRecord` only calculates display variables.
- No automatic backend refresh is started while opening the page.
- No background auto-refresh is queued.
- `Refresh Status` is the only action that calls the backend and updates the local run.

## Status Fields

Persisted raw fields:

- `Status`: local Business Central option status.
- `Backend Status`: backend status text.
- `Progress %`: latest stored progress.
- `Current Module`: latest stored module.
- `Current Step`: latest stored step.
- `Warning Message`: latest stored warning.
- `Error Message`: latest stored error.

Visible display fields:

- `Scan Status`
- `Overall Progress`
- `Current Module`
- `Current Step`
- `Warning`
- `Error`

Display priority:

1. `Backend Status`, if present.
2. Local `Status`, only as fallback.
3. `completed` always displays:
   - `Completed`
   - `100%`
   - `All modules completed`
   - `Scan completed`
   - no stale warning or error

## Risk Review

- `DH Deep Scan Monitor.OnOpenPage`: uncritical, display variables only.
- `DH Deep Scan Monitor.OnAfterGetRecord`: uncritical, display variables only.
- `DH Deep Scan Monitor.OnAfterGetCurrRecord`: uncritical, display variables only.
- `DH Deep Scan Monitor.Refresh Status`: intentionally modifies the run after an explicit user action.
- `DH API Client.RefreshScanStatus`: intentionally modifies the supplied run record; now only called by explicit refresh in the monitor.
- `DH Deep Scan Mgt.QueueDeepScan`: intentionally inserts/modifies the run before the monitor is opened manually.
- `DH Deep Scan Runner`: intentionally modifies scan progress from the background task.

## Manual Validation

1. Publish a clean app package with version `1.0.2.3`.
2. Start a deep scan.
3. Confirm that no monitor page opens automatically.
4. Confirm the message: `Scan started. Open the monitor to view progress. Run ID: ...`
5. Open the monitor from scan history.
6. Confirm the marker `ScanMonitorFix v2` is visible.
7. Confirm no page-refresh dialog appears on first open.
8. Click `Refresh Status`.
9. Check diagnostics:
   - `Local Status Raw`
   - `Backend Status Raw`
   - `Display Status`
   - `Display Progress`
   - `Last Refresh Source`
   - `Last Refresh Error Count`
10. For completed scans, confirm:
   - `Display Status = Completed`
   - `Display Progress = 100`
   - `Current Module = All modules completed`
   - `Current Step = Scan completed`
   - stale backend refresh warnings are empty

If the marker is missing, unpublish the old app package from the sandbox and publish the newly built `.app` again.

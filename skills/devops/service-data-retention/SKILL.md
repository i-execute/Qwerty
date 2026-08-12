---
name: service-data-retention
description: Safely reduce disk use for a live local service while retaining specified data and preserving a recoverable/restartable service state.
version: 1.0.0
author: Hermes Agent
created_by: agent
---

# Service Data Retention

Use for requests such as "delete everything except logs/statistics/venv" in a directory that may also be a running service checkout.

## Core rule

Interpret retention requests literally, but **discover runtime dependencies before deletion**. A service directory often contains indispensable but untracked state: environment files, service credentials, sessions, databases, virtual environments, and systemd unit dependencies.

## Procedure

1. **Inspect before deleting**
   - Measure directory size and largest subdirectories/files.
   - Check whether a related process or systemd service is active.
   - Read the service unit to identify `WorkingDirectory`, `EnvironmentFile`, and `ExecStart`.
   - Inspect the selected retained report and verify it parses successfully before any cleanup.

2. **State the retention boundary**
   - Identify requested keep paths explicitly.
   - Separately list runtime-critical paths that would be removed but are required for a later restart (commonly `.env`, session/database files, source checkout, and `venv`).
   - If the user explicitly wants only the selected artifacts, preserve exactly those artifacts—but state that the service will be non-runnable afterward unless the deleted configuration/state is recreated.

3. **Stop writers first**
   - Stop the service before selecting a "latest" report or deleting generated output, so temporary files and the selected snapshot are stable.

4. **Preserve one validated data artifact**
   - Select the newest completed JSON report (never `.tmp`).
   - Validate JSON and an expected schema/required fields.
   - Copy it to a stable, clearly named location (for example `telemetry_latest.json`) outside any directory slated for deletion.

5. **Delete with an allowlist**
   - Use an allowlist of exact retained paths, not a pattern that can accidentally retain/delete unexpected material.
   - Do not delete while a process remains active.

6. **Verify and report**
   - Confirm the exact remaining top-level entries, parse the retained report again, compare disk usage/free space before and after, and report service state.

7. **If asked to restore/update/restart after a destructive cleanup**
   - Re-clone or restore tracked source from Git first, then run `git pull --ff-only`.
   - Check that the `EnvironmentFile`, interpreter path, dependencies, and service-state files exist before attempting `systemctl start`.
   - Do not claim the service restarted if its secrets/configuration/session state was intentionally removed. Report the specific prerequisite category that must be restored without exposing secrets.

## Uploading retained reports

- Validate the file before upload.
- Use the target host's accepted upload form/method; if an initial upload fails, inspect the HTTP method requirement and retry with the documented/form-compatible form upload.
- Verify the returned URL is reachable before sharing it.

## Pitfalls

- A Git checkout cannot restore untracked `.env`, Telegram/other service sessions, local databases, or a virtualenv.
- `git pull` requires a valid checkout; after deleting `.git`, restore/clone before pulling.
- A systemd service can enter an auto-restart loop after its `EnvironmentFile` or `ExecStart` interpreter disappears. Stop and reset its failed state after a destructive cleanup.
- “Latest” reports can be partial `.tmp` files. Never retain those as the only statistics artifact.

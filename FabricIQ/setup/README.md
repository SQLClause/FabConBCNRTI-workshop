# Fabric IQ setup

This folder provisions the plumbing for the Fabric IQ workshop: a `Fabric IQ`
workspace, pinned to a non-trial capacity, containing a Lakehouse, an
Eventhouse/KQL database, an Eventstream, and a reference-data notebook.

## Quick start

Pick whichever launcher matches your OS, or call the Python script directly.

**macOS / Linux:**
```bash
cd setup
pip install -r requirements.txt
./run-setup.sh
```

**Windows (PowerShell):**
```powershell
cd setup
pip install -r requirements.txt
.\run-setup.ps1
```

**Direct (any OS):**
```bash
cd setup
pip install -r requirements.txt
python3 provision_fabric_iq.py
```

The script is interactive by default: it will list your eligible Fabric
capacities and ask you to pick one, then create (or reuse) the `Fabric IQ`
workspace and import the four items.

## What this script does

1. Preflight-checks Python (3.10+) and the Fabric CLI (`fab --version`).
2. Confirms you're signed in to Fabric, or runs `fab auth login` for you.
3. Lists your eligible capacities and has you pick one. **Trial capacities
   are hard-blocked** unless you explicitly override the warning (or pass
   `--force`) — Fabric IQ's Ontology/Graph preview features don't work on
   trial (FT1) capacities.
4. Creates a workspace named `Fabric IQ` (or reuses one if it already exists).
5. Locates the `artifacts/` folder (using the local checkout this script
   lives in, or cloning the repo fresh if run standalone).
6. Imports, in order: `ColdChainLakehouse` (Lakehouse) → `ColdChainEventhouse`
   (Eventhouse) → `FreezerTelemetryEventstream` (Eventstream) →
   `00_LoadReferenceData` (Notebook).
7. Verifies all four items landed in the workspace.
8. Prints a summary with a workspace deep link and a pointer to
   `modules/module-00-welcome-and-setup/lab-00-environment-setup-and-verify.md`.

## What this script explicitly does NOT do

- **It does not create the Ontology, Data Agent, or Operations Agent items.**
  These are still-preview item types without confirmed `fab` support for
  scripted creation, and — more importantly — building them live is the
  entire point of Modules 03 and 04. You build these by hand, in the lab.
- **It does not run the `00_LoadReferenceData` notebook for you.** Importing
  a notebook doesn't execute it. Running it — and watching the `Customers`,
  `Stores`, `Freezers` Delta tables appear — is a deliberate, visible step in
  the early lab guides.
- **It does not configure the Eventstream's connection string** into
  `artifacts/generator/freezer_telemetry_generator.py`. That connection
  string is only obtainable from the Fabric portal after the Eventstream
  item exists in *your* workspace, so it's a one-time manual copy/paste step
  covered in `lab-02`, not something this script can do for you.

## Flags

| Flag | Description |
|---|---|
| `--dry-run` | Print every command that would run, without creating or importing anything. Read-only checks (version, auth, capacity listing) still actually run so you see real state. |
| `--non-interactive` | Never prompt. **Requires** `--capacity`. Intended for presenter testing/CI, not for attendees. |
| `--capacity <name>` | Exact capacity name to use, skipping the interactive picker. |
| `--workspace-name <name>` | Name of the workspace to create/reuse (default: `Fabric IQ`). |
| `--force` | Reuse an existing workspace without prompting, override the trial-capacity warning, and force-overwrite items on import. Use with care. |

Every step is designed to be safe to re-run: creating an already-existing
workspace is handled by reuse (not a crash), and re-importing an item that
already exists is handled via `fab import ... -f` when `--force` is passed.

## Troubleshooting

Each of these maps to a numbered section in
[`../prerequisites/PREREQUISITES.md`](../prerequisites/PREREQUISITES.md) —
check there first for the underlying fix.

| Symptom | Likely cause | Fix |
|---|---|---|
| `Command not found: fab` | Fabric CLI isn't installed. | `pip install ms-fabric-cli`, confirm with `fab --version`. See PREREQUISITES.md §3. |
| Script hangs or fails at "Authentication" | Not signed in, or `fab auth login`'s browser/device-code flow is blocked by a corporate VPN/proxy. | Run `fab auth login` manually and watch for errors. See PREREQUISITES.md §4. |
| "No capacities were returned by the Fabric CLI" | Your account has no visible/eligible Fabric capacity, or lacks Contributor+ role on one. | Confirm capacity access with your tenant admin. See PREREQUISITES.md §2. |
| "Capacity looks like a trial capacity" warning | You selected (or only have) an FT1/trial capacity. | Use a non-trial F2+/P1+ capacity — trial capacities don't support Ontology/Graph/Data Agent features at all, and later modules will fail. See PREREQUISITES.md §1. Do not use `--force` to bypass this unless you fully understand later modules won't work. |
| An import fails with an error mentioning "preview" or "not enabled" | A tenant-level preview setting (Ontology/Data Agent) hasn't been enabled by your Fabric admin. | This can't be fixed live — it needs your tenant admin to enable the setting 2+ weeks ahead of the event. See PREREQUISITES.md §1. |
| "Workspace already exists" prompt / `--force` needed | A previous run (or another attendee) already created a workspace with this name. | Reuse it (default prompt), pick a different `--workspace-name`, or pass `--force` to reuse without prompting. |
| An item import reports a name collision | An item with that name already exists in the target workspace (e.g. from a partial previous run). | Re-run with `--force` to overwrite, or delete the conflicting item manually first. |
| Post-import verification shows a MISSING item | The import step failed silently or the item type isn't yet covered by `fab import` in your CLI version. | Check the printed error for that item, and try the manual `fab import` command the summary prints for you. |

## For maintainers: judgment calls made while writing this script

- **Auth check command**: `fab` was not confirmed (during this authoring
  pass, without a live tenant) to expose a dedicated `whoami`/`auth status`
  subcommand. The script uses a harmless `fab -c "ls ."` call as an auth
  probe instead. Validate against `fab --help` during the pre-event dry run
  and swap in a dedicated status command if one exists.
- **Capacity listing parsing**: the exact column layout of
  `fab -c "ls .capacities -l"` output wasn't verified against a live tenant.
  The script takes the first whitespace-separated token as the capacity name
  and scans the full line for trial-SKU keywords (`trial`, `ft1`, `free`).
  Validate and tighten this parsing during the pre-event dry run.
- **`fab import` vs `fab deploy`**: per `BUILD_PLAN.md`, `fab deploy`
  (manifest-driven, wraps `fabric-cicd`) is the preferred long-term path if a
  pre-event dry run confirms it covers all four item types used here. This
  script deliberately uses the more verbose but individually verifiable
  per-item `fab import` loop until that's confirmed — see the comment above
  `import_items()` in `provision_fabric_iq.py`.
- **Notebook execution**: the script does not attempt `fab job run` (or
  similar) to auto-run `00_LoadReferenceData` after import — this was a
  deliberate pedagogical choice (see "What this script explicitly does NOT
  do" above), not a technical limitation.

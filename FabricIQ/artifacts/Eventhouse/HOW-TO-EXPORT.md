# The Eventhouse and its KQL database: how provisioning actually works

## No dev-tenant export needed for the Eventhouse itself

Earlier versions of this workshop planned to hand-build the Eventhouse once in a
dev tenant and `fab export` it, the same way the Eventstream is handled. That was
tried and abandoned — confirmed live against a real tenant:

- `fab export`/`fab get` do not work against a live KQL database item at all;
  both fail with a generic, unhelpful `"UnexpectedError"`. There's no way to
  obtain a real, tenant-verified export of a KQL database's item definition
  right now.
- Creating an Eventhouse via `fab mkdir` auto-provisions exactly one default
  KQL database, and that database's name always matches the Eventhouse's own
  name (e.g. an Eventhouse named `ColdChainEventhouse` gets a database also
  named `ColdChainEventhouse`, not `ColdChainKQLDB`).
- There is no `fab` command to rename it afterward — `fab mv`/`fab cp`
  explicitly exclude `eventhouse`/`kql_database` from their supported item
  types (see the installed `fabric_cli` package's own
  `core/fab_config/command_support.yaml`).

So `setup/provision_fabric_iq.py` doesn't import a pre-captured Eventhouse
definition at all anymore. Instead (see `create_via_mkdir_item()` and
`create_kql_database_item()` in that script):

1. The Eventhouse is created bare via `fab mkdir` (`mode: create` in
   `manifest.yaml`, same pattern as the Lakehouse) — no definition folder
   needed, and this auto-provisions a default database named after the
   Eventhouse.
2. A second, correctly-named KQL database (`ColdChainKQLDB`) is created via
   `fab import` from the minimal, hand-built definition in
   [`ColdChainKQLDB.KQLDatabase/`](ColdChainKQLDB.KQLDatabase/) — just a
   `.platform` file and a `DatabaseProperties.json` with a
   `__EVENTHOUSE_ID__` placeholder, substituted with the real Eventhouse's
   item ID at import time. This is NOT a `fab export`-captured definition
   (that's not obtainable — see above); it was hand-built and confirmed live
   to import cleanly.
3. The auto-created default database (named after the Eventhouse) is then
   deleted via `fab rm` (which, unlike `mv`/`cp`, IS supported for
   `kql_database`), leaving exactly one, correctly-named database.

If you ever need to regenerate `ColdChainKQLDB.KQLDatabase/`: create any
KQL database in any workspace, keep its `.platform` (adjusting
`displayName`) and `DatabaseProperties.json` (replacing whatever
`parentEventhouseItemId` value it has with the literal string
`__EVENTHOUSE_ID__`) — you do not need a successful `fab export` for this,
since the shape of these two files is simple enough to hand-edit once
understood.

## The KQL schema IS applied automatically

The KQL schema (table/column definitions, ingestion mapping, dimension
tables, and the enriched materialized view) is written out for real in this
folder, at [`ColdChainKQLDB.kql`](ColdChainKQLDB.kql). `provision_fabric_iq.py`
runs this whole script against the live `ColdChainKQLDB` database right after
creating it, via `run_kql_schema()` — which imports a small throwaway
notebook that executes the script **server-side**, via Kusto's `.execute
database script` control command (which runs a multi-statement script —
including the multi-line `.create-or-alter materialized-view` block — in one
call), runs it with `fab job run`, then deletes the notebook again.

This was previously believed impossible via `fab`: its `-A/--audience` flag
only offers 4 fixed token scopes (`fabric`, `storage`, `azure`, `powerbi`),
none of which speak Kusto's own protocol correctly, and raw `fab api` calls
against the cluster's own REST endpoint hit ARM-gateway routing mismatches.
An earlier version of this called Kusto directly from the presenter's/
attendee's own laptop via the `azure-kusto-data` Python SDK — that worked,
but needed its own **separate interactive device-code sign-in**, independent
of (and confusing alongside) `fab auth login`. Running the same logic from
inside a Fabric notebook instead avoids that entirely: confirmed live that
`notebookutils.credentials.getToken("kusto")` gives the notebook a
trusted-execution Kusto-audience token for free, no interactive prompt,
because it runs server-side under `fab job run`'s already-established `fab
auth login` session. Also confirmed live that `azure-kusto-data` itself is
**not usable inside a Fabric notebook** as of this writing — Fabric's
runtime has already imported an older, incompatible `azure-core` by the time
user code runs, and `pip install -U` inside the same kernel session doesn't
help (Python's module cache keeps serving the already-imported old version).
The notebook instead calls Kusto's REST endpoint directly via `requests` —
confirmed live end-to-end, including the full script: created
`FreezerTelemetryRaw` (with its docstring), `StoresDim`/`FreezersDim`
(seeded), and the `FreezerTelemetryEnriched` materialized view.

This step needs **no extra sign-in** beyond the one `fab auth login` already
does in step 2 — confirmed live with a fully `--non-interactive` run. Skip
it explicitly with `--skip-kql-schema`; see `run_kql_schema()`'s docstring.

Every `.create` statement in `ColdChainKQLDB.kql` uses an idempotent-safe
form (`ifnotexists` / `create-or-alter`), so re-running `provision_fabric_iq.py`
(e.g. with `--force`) re-applies the script harmlessly rather than erroring
on already-existing tables/view — confirmed live on a second run.

**Note for Module 10's lab:** `FreezerTelemetryEnriched` already exists by
the time attendees reach Lab 10 — that lab's Part E was rewritten to explain
and confirm the view (reading the KQL, running `.show materialized-view`)
rather than having attendees create it themselves, since it's no longer a
"first time this exists" moment. See `lab-10-join-streaming-and-reference-data.md`.

## Validate before the event

Re-run `setup/provision_fabric_iq.py --dry-run`, then a real run against a
throwaway workspace, to confirm:
- `ColdChainEventhouse` and `ColdChainKQLDB` both land correctly, with no
  leftover default-named database.
- The KQL schema step completes and shows `[OK] ... (schema applied)` in the
  summary, and `FreezerTelemetryEnriched` is queryable (returns 0 rows before
  telemetry flows, per `ColdChainKQLDB.kql`'s own comments).

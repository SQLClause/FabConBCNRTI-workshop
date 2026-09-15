# Session Memory — Fabric IQ Workshop Planning & Build

This file captures the decisions, rationale, research findings, and open items from the Claude Code
session that planned and built this `FabricIQ/` folder, so a future session can pick up context without
re-deriving it. It complements [`BUILD_PLAN.md`](BUILD_PLAN.md) (the design/folder-structure plan) and
[`README.md`](README.md) (what's built) — this file is the "why" and "what's still open."

## Project context

- Repo: `FabConBCNRTI-workshop` — labs for an 8-hour workshop, "Building Intelligent, Event-Driven
  Architectures with Fabric Real-Time Intelligence," co-presented by **Johan** (Real-Time Intelligence
  half) and **Brian** (Fabric IQ half, this folder). Likely tied to FabCon Barcelona (the sample data
  scenario was localized to Barcelona-area stores for that reason — see below).
- Brian's section is the **second 4 hours**, running **after** Johan's RTI half — Module 00/01 give only
  a light RTI recap, not a from-scratch RTI intro. If the running order ever changes, flag this as
  needing real content added.
- Audience: data/AI practitioners already comfortable with Fabric basics (workspaces, lakehouses, KQL),
  new to ontologies/Fabric IQ specifically.
- `plan.md` in this folder is the original one-paragraph brief this whole build was derived from —
  left unchanged as the historical source document.

## Key decisions & rulings (with rationale)

1. **CLI provisioning script provisions plumbing only** — workspace, Lakehouse, Eventhouse, Eventstream,
   notebook. It deliberately does **not** create the Ontology, Data Agent, or Operations Agent items.
   Reason: Fabric CLI (`fab`) has no confirmed support for those (still-preview) item types, and building
   them live is the actual pedagogical point of Modules 03–04.
2. **Attendees use their own org's Fabric capacity**, not a trial capacity — Fabric IQ's Ontology/Graph
   preview features are confirmed unsupported on trial (FT1) capacities, so the setup script hard-blocks
   trial-SKU selection (override requires `--force` + explicit acknowledgement).
3. **Single connecting scenario for the whole 4 hours: retail cold-chain monitoring**, reusing Microsoft's
   own official retail ontology tutorial pattern (Customer/Store/Freezer entities) extended with live
   freezer-temperature telemetry, mirroring the official Digital Twin Builder bus/bus-stop tutorial's
   static-context + live-Eventhouse-binding pattern. Chosen to maximize reuse of tested Microsoft content
   over an invented scenario, directly serving the "fool proof" goal in `plan.md`.
4. **PowerPoint slides are a separate, condensed layer on top of the markdown**, not a replacement for
   it. The `theory-XX-*.md` / `lab-XX-*.md` files remain the source of truth and the durable
   attendee-facing reference for later rerun/reference (explicit instruction) — `slides/*.md` decks are
   written *from* that content, more bulleted/condensed, and are what's actually presented from.
5. **Slide pipeline switched mid-session**: originally built with stock Marp CLI (`@marp-team/marp-cli
   --pptx`), which rasterizes each slide as an image (not editable). Once the user supplied the real
   conference PowerPoint template (`slides/template/*.pptx`), the whole pipeline was rebuilt on
   [MarpToPptx](https://github.com/jongalloway/MarpToPptx) instead, which renders real editable OOXML
   shapes styled from that template's own masters/layouts. See "MarpToPptx / template findings" below —
   this took real empirical verification, not just reading MarpToPptx's docs.

## Fixed naming contract (used consistently across every artifact, lab, slide, and script)

Keep any future edits consistent with this — it's referenced by name across ~20 files.

- Fabric workspace: **`Fabric IQ`**
- Lakehouse: **`ColdChainLakehouse`** — tables `Customers`, `Stores`, `Freezers`
- Eventhouse: **`ColdChainEventhouse`** — KQL database **`ColdChainKQLDB`**
  - Raw table: `FreezerTelemetryRaw` (`FreezerId`:string, `StoreId`:string, `Timestamp`:datetime,
    `TemperatureC`:real, `DoorOpen`:bool)
  - Enriched materialized view: `FreezerTelemetryEnriched` (`arg_max(Timestamp, *)` per `FreezerId`,
    `lookup`-joined to `StoresDim`/`FreezersDim`)
- Eventstream: **`FreezerTelemetryEventstream`** (custom-endpoint source, Event Hubs/AMQP protocol)
- Notebook: **`00_LoadReferenceData`**
- Ontology (built live in Module 03, not scripted): **`ColdChainOntology`** — entity types `Customer`,
  `Store`, `Freezer`; relationships `Store`—`has`—>`Freezer`, `Customer`—`ShopsAt`—>`Store` (field value
  is the single token `ShopsAt`; spoken/prose form is "Customer shops at Store" — entity/relationship
  names can't contain spaces)
- Data Agent (built live, Module 04): **`ColdChainDataAgent`**
- Operations Agent (built live, Module 04): **`ColdChainOperationsAgent`**, paired with Activator
  Ontology Rule **`Freezer running warm`** (fires when `TemperatureC` > ~-12°C, sustained ~5 min)
- Sample data / scenario dressing: **Fabrikam Fresh**, a 6-store retail chain across Barcelona (×2),
  Madrid, Valencia, Bilbao, Seville (`artifacts/SampleData/*.csv`) — this localization was a judgment
  call by the setup-script-authoring agent (FabCon Barcelona fit), not an explicit user instruction;
  easy to rename if a US-generic setting is preferred later.
- Anomaly threshold used everywhere alerting/agent labs reference it: **-12°C**. Setpoint: **-18°C**.

## Research findings that shaped the plan (as of Sept 2026 — re-verify if much time has passed)

- **Fabric IQ's Ontology, Graph, and Planning items are (preview)**; Data Agent and Operations Agent are
  GA. Ontology/Graph require a tenant admin to enable "Ontology item (preview)" + Data Agent/Azure OpenAI
  tenant settings, and a non-trial F2+/P1+ capacity — none of this can be fixed live during the workshop.
- **Fabric CLI (`fab`)** reliably automates workspace creation, capacity listing/assignment, and item
  import (`fab import`) for Lakehouse/Eventhouse/Eventstream/Notebook from local exported definitions.
  No confirmed support for Ontology/Graph/Data Agent item types. No native interactive capacity picker or
  "import from GitHub URL" — both had to be hand-built in `provision_fabric_iq.py`.
- **Microsoft's own Digital Twin Builder RTI tutorial** (bus/bus-stop scenario) is the direct template
  for the RTI→Ontology bridge lab (Module 02→03): static contextual data → Lakehouse → ontology →
  projected into Eventhouse. Microsoft's own **retail ontology tutorial** (Customer/Store/Freezer) is the
  direct template for Module 03's ontology build. Full URL list is in `docs/agenda.md`.
- **The ontology graph does NOT auto-refresh** when new rows land in a bound source — this was discovered
  during Module 03 lab authoring (via live Microsoft Learn doc research) and is a real, non-obvious
  product behavior: the lab has attendees explicitly trigger the auto-created Graph item's "Refresh now"
  rather than waiting for live updates that will never come. Getting this backwards live would be a
  visible failure mode — flagged as high-value, keep this step in any future edits.
- **Fabric Eventstream's "custom endpoint" source is Event Hubs-compatible SAS/AMQP, not plain HTTPS** —
  the telemetry generator script uses `azure-eventhub` (lazily imported) for this reason, not `requests`.
  This dependency is documented in `setup/requirements.txt`, `prerequisites/PREREQUISITES.md`, and as an
  explicit `pip install` step inside `lab-02`.

## MarpToPptx / template findings (empirically verified, not just read from docs)

The conference template (`slides/template/EMFCC26_SpeakerPPT_TemplateA_...pptx`) has **12 slide layouts**;
MarpToPptx's own diagnostics tool couldn't statically tell them apart (all reported "0 distinct shapes"),
so every finding below came from an actual test render + inspecting the generated OOXML — not from
reading layout names.

- **Title slide**: use `<!-- _layout: Template[3] -->` (clones the template's own authored branded title
  slide — the fancy treatment is hand-authored on slide 3 of the template file, not exposed as a normal
  reusable layout). `Template[1]` is the wrong choice (that's a generic "Splash Screen" example with
  placeholder text "Slide 1"). Confirmed MarpToPptx fills the real `title`-type placeholder with markdown
  content and **clears** (doesn't leave stale) the template's non-placeholder "YOUR NAME" / "TITLE,
  COMPANY NAME, COUNTRY" text boxes — but since those are plain text boxes, not placeholders, markdown
  can't populate them either. **Every generated deck needs a one-time manual fill-in of those two boxes
  in PowerPoint after building** — this is documented in `slides/README.md` and
  `docs/facilitator-guide.md`, not something the build script can automate.
- **Default content layout**: `Main Content : Title + Text Box` (real title+body placeholders).
- **Section dividers**: `Section Break Slide` (only one `body` placeholder — keep these slides short).
- **Visual/diagram slides**: `Main Content : Title + Visual Data` — note this only changes the slide's
  background framing, not code-block/table placement (those render as standalone shapes on any layout).
- **Deliberately NOT used**: `Dark Content (White Background)` and both `Dark BKG` variants (zero
  declared placeholders — MarpToPptx falls back to unstyled freeform text boxes); the "Dual Text Box" /
  "Dual Visual Data" layouts (confirmed MarpToPptx does **not** actually split content across two
  placeholders — everything still lands in one, so these offer no real two-column benefit over the
  default); `Splash Screen` (zero placeholders at all); `1_Main Content : Title + Text Box` (untested
  duplicate-looking variant).
- Both `--template` and `--theme-css` are passed together in `build-slides.sh` — the template governs
  placeholder-backed slides' styling regardless of the CSS; the CSS covers freeform elements the template
  doesn't own (code blocks, etc.).
- Tooling: `.NET 10 SDK` + `dotnet tool install --global MarpToPptx` (installed globally on this machine
  at time of writing, v1.2.0). `dnx MarpToPptx` works as a no-install fallback (slower, resolves fresh
  each run) — `build-slides.sh` already handles both paths.

## Open items / needs validation before the live event

These are called out inline in the relevant files too, but collected here for visibility:

- **RESOLVED (live-validated in a later session, fab 0.1.10, against a real tenant/capacity)**:
  - `fab auth status` and the `fab -c "ls .capacities -l"` column layout — both confirmed; the capacity
    parsing had a real bug (multi-word capacity names got truncated to their first word by a plain
    `.split()`), now fixed. See `setup/README.md`'s "For maintainers" section for specifics.
  - **Lakehouse provisioning**: `fab export`/`fab import` do NOT support the Lakehouse item type at all
    (confirmed via `ms-fabric-cli`'s own `command_support.yaml`, not just guessed). `provision_fabric_iq.py`
    now provisions it via `fab mkdir` + `fab cp` instead (see `create_lakehouse_item()`) — no
    `artifacts/Lakehouse/` export folder is needed or expected anymore; `artifacts/Lakehouse/HOW-TO-EXPORT.md`
    was deleted since there's nothing left to export.
  - **Notebook provisioning**: a Notebook's git-source `.py` format is public/documented and plain-text,
    so `00_LoadReferenceData` is now `fab import`'d directly from `artifacts/Notebooks/00_LoadReferenceData.py`
    (rewritten into that real format), with its default-Lakehouse binding filled in at import time via a
    placeholder substitution (`__LAKEHOUSE_ID__`/`__WORKSPACE_ID__`) — see `create_notebook_item()`. No
    dev-tenant hand-build/export is needed for this item either; `artifacts/Notebooks/HOW-TO-EXPORT.md` was
    deleted. Ran the imported notebook end-to-end in a throwaway workspace: all three Delta tables
    (`Stores`, `Freezers`, `Customers`) landed correctly with real reference data.
  - So `artifacts/{Eventhouse,Eventstream}/HOW-TO-EXPORT.md` are the only two of the original four
    HOW-TO-EXPORT.md files still needed — those two item types' definition JSON shape genuinely isn't
    public, so they still require a real `fab export` from a hand-built dev-tenant item. **Neither has
    actually been captured yet** (same gap as before, just narrower) — the KQL script and Eventstream
    topology instructions are real and correct, but the importable `.Eventhouse/`/`.Eventstream/` folders
    under `artifacts/` don't exist yet.
- **NEW gap found while live-testing (not resolved, and intentionally not addressed this pass — see
  `setup/README.md`'s "What this script explicitly does NOT do", which a later session was explicitly
  told to keep as-is)**: `lab-00`'s checkpoint and `lab-01`/`lab-02`'s prerequisites all assume
  `ColdChainLakehouse`'s `Customers`/`Stores`/`Freezers` tables are **already populated** by the time
  `lab-00` finishes — but nothing in the current design (script or labs) actually runs
  `00_LoadReferenceData` before then; running it is only ever framed as a troubleshooting fallback in
  `lab-00`, never a golden-path step anywhere in Modules 00-02. Either a lab needs an explicit "run this
  notebook" step added, or the provisioning script needs to run it (which would mean dropping that bullet
  from "does NOT do") — a real product decision, not something to silently resolve either way.
- **`fab import` vs `fab deploy`**: the script uses the more verbose but individually-verifiable
  `fab import` loop for Eventhouse/Eventstream; `fab deploy` (manifest-driven) is the preferred long-term
  path *if* a pre-event dry run confirms it covers those two item types. Doesn't apply to the Lakehouse or
  Notebook either way (see above).
- **Eventhouse KQL schema on import**: still open — no `fab` command or Fabric-audience `fab api` call was
  found that can execute a `.kql` script against a KQL database directly (Kusto's own query/management
  endpoint needs a token audience `fab api` doesn't expose). If the imported Eventhouse doesn't carry the
  Queryset-created tables/view, re-running `ColdChainKQLDB.kql` stays a manual step — see
  `artifacts/Eventhouse/HOW-TO-EXPORT.md`.
- **`fab job run --timeout` crashes client-side** in fab 0.1.10 (`'<' not supported between instances of
  'int' and 'str'`) even though the job itself starts fine server-side (confirmed by polling
  `fab job run-status` separately). Doesn't affect `provision_fabric_iq.py` (which never calls `job run`),
  but worth knowing if you manually run the notebook from a terminal.
- **Module 03's exact click-paths** (ontology UI) were grounded against live Microsoft Learn docs at
  authoring time but not a live tenant walkthrough — this is the single highest-risk lab in the section
  (preview UI). See `docs/risk-fallback-plan.md`.
- **Screenshots** (`assets/screenshots/**/step-NN.png`) are placeholders only — none have been captured
  yet. **Fallback recordings** (`assets/fallback-recordings/LINKS.md`) likewise need to actually be
  recorded and linked.
- **Mandatory presenter dry run** of the full script + every lab, within ~72 hours of the event (preview
  features move fast) — not something any session can do without live access.
- **MarpToPptx layout table** is only valid for the exact template file used — if the conference issues
  an updated template, re-run the empirical verification (test render + OOXML inspection) before trusting
  the existing layout assignments; see `slides/README.md`'s "If you edit the template."

## Where everything lives

See `BUILD_PLAN.md`'s "Folder Structure to Create" for the full map, and each subfolder's own README
(`setup/README.md`, `slides/README.md`) for details specific to that piece. Nothing in this repo has
been committed to git as of this writing — all work is in the working tree only.

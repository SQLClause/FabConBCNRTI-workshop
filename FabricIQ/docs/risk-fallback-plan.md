# Risk / Fallback Plan

## Per-module risk table

| Module | Risk | Likelihood | Impact | Mitigation | Fallback asset |
|---|---|---|---|---|---|
| 00 – Setup | Most of the room now runs installs + `fab auth login` + provisioning live, simultaneously, for the first time (no longer just a few pre-run stragglers) — individual auth/permissions/network failures are more likely in aggregate, and the room-wide venue network/auth load is higher during this specific 40-minute window | Medium-High | Medium (a cluster of simultaneous failures can eat into the fixed 40-minute block, not just one attendee's time) | Pair anyone who fails with a neighbor who succeeded rather than troubleshooting solo; keep one pre-provisioned "instructor" workspace as a screen-share fallback; the trial-capacity hard-block in `provision_fabric_iq.py` and the matching Lab 00 troubleshooting block exist specifically to stop that one failure mode from eating the room's time — don't let anyone bypass it hoping to fix it later | Instructor's own already-provisioned workspace, screen-shared |
| 01 – Architecture & Context | Low — mostly discussion/exploration of already-provisioned items | Low | Low | — | — |
| 02 – Telemetry & Grounding | Eventstream custom-endpoint connection or synthetic generator fails to stream live data | Medium | Medium (lab depends on seeing live data land) | Test the generator against a real tenant within 72 hours of the event; have a pre-recorded short clip of data flowing as backup | `assets/fallback-recordings/LINKS.md` |
| 03 – Ontology Design | **Highest risk** — Ontology item is (preview), UI can change or misbehave without notice | High | High (core lab of the whole section) | Mandatory presenter dry run within 72 hours; static screenshot fallback sequence prepared in advance | `assets/screenshots/fallback/lab-03/` + narration below |
| 04 – Agent Patterns | Data Agent/Operations Agent + Activator ontology rules is a newly composed, live-data path even though items are individually GA | Medium-High | High | Mandatory presenter dry run; static screenshot fallback sequence prepared in advance | `assets/screenshots/fallback/lab-04/` + narration below |
| 05 – Prompting, Trust & Traceability | Low — mostly inspection/discussion of agents already built in Module 04 | Low | Low (this module is the designated time-box buffer anyway) | Compress to discussion-only if running behind | — |
| 06 – Wrap-up | None | — | — | — | — |

## Fallback assets

- **Pre-recorded screen captures** for Module 02 (data streaming), Module 03 (ontology creation), and
  Module 04 (agent + Activator rule creation) are linked externally from
  [`assets/fallback-recordings/LINKS.md`](../assets/fallback-recordings/LINKS.md) (unlisted
  YouTube/OneDrive/Stream). **Video files are not committed to this git repository** — if that changes,
  Git LFS becomes a hard requirement and the resulting repo-size trade-off should be reconsidered.
- **Static screenshot fallback sequences** at `assets/screenshots/fallback/lab-03/` and
  `assets/screenshots/fallback/lab-04/`, each frame paired with narration text below, so the presenter
  can "drive" the lab from screenshots + narration if the live preview UI misbehaves mid-session.

### Narration: Module 03 fallback sequence

1. *(Ontology canvas, empty)* "This is the Ontology (preview) item after creation — a blank canvas."
2. *(Entity type added)* "I'm adding the Freezer entity type with properties FreezerId, Model, InstallDate."
3. *(Binding dialog)* "Binding Freezer to the Lakehouse Freezers table — no data copy happens here."
4. *(Graph view)* "The bound entities now form a queryable graph."

### Narration: Module 04 fallback sequence

1. *(Data agent creation)* "Creating a Fabric Data Agent grounded in the ColdChainOntology."
2. *(Test query)* "Asking the agent 'which freezers in Store 12 are above threshold' — it resolves this
   through the ontology, not raw table names."
3. *(Operations agent + Activator rule)* "The Operations Agent is set up to watch the Freezer entity;
   the Activator rule fires in business terms — 'Freezer running warm' — not a raw KQL threshold."

## Pre-event checklist for the presenter

- [ ] Run the full provisioning script + every lab end-to-end in a representative tenant within
      **~72 hours** of the event — preview features change fast, so anything older is unreliable.
- [ ] Confirm venue network connectivity; Fabric has no offline fallback, so have a mobile-hotspot
      backup plan for the room (out of this repo's scope, but worth confirming ahead of time). This
      matters more than it used to: Module 00 now has most of the room hitting `fab auth login` and
      `pip install` simultaneously for ~15-20 minutes, not a handful of stragglers.
- [ ] Confirm Module 05 can be compressed to discussion-only on short notice, in case Module 03/04 ran
      long.

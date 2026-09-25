# Risk / Fallback Plan — RTI half

## Per-module risk table

| Module | Risk | Likelihood | Impact | Mitigation | Fallback asset |
|---|---|---|---|---|---|
| 01 – Workspace & hub | Attendee can't create a workspace (no capacity assigned) | Low (Microsoft provides accounts) | High for that attendee | Pair with a neighbour; flag facilitator; same failure mode the IQ half hard-blocks | Instructor workspace, screen-shared |
| 02 – Eventstream | **Feed down** (TMB API limit hit, Function crashed, Event Hubs throttled) | Medium | **High** (everything downstream needs data) | Function caches + `IsStale`; Function runs only in the window; dry-run recording | `infra/replay_events.py` from the presenter laptop, same hubs, zero attendee change |
| 02–05 – all | **Capacity throttled → eventstreams paused** (observed in the dry run on an **F16 shared with another workspace**: the eventstream stopped, the processed table went stale, and a manual **Resume** was needed; one build's own footprint is still unmeasured) | Medium–High, depends on SKU | **High** (silently breaks every later lab for that attendee) | Dry run one full attendee build on the real SKU with the Capacity Metrics app open; keep raw tables on queued ingestion (C3a); metro stream is optional; pause streams at lunch (Module 07). Recovery: Live view → **Resume** paused nodes | Presenter demo on the instructor workspace while capacity recovers |
| 02 – Eventstream | Attendee uses wrong consumer group / `$Default` → partitions stolen from another attendee | Medium | Medium | Assignment sheet; the lab says in bold not to use `$Default` | Reassign a spare group (`attendee-9x`) |
| 02 – Eventstream | Group-by operator preview shows nothing for a minute (tumbling window not yet closed) | High (expected) | Low | Lab step says to wait 60–90 s | — |
| 02 – Eventstream | Manage fields picker doesn't show nested `payload → data → ibus` (no schema yet), or Expand won't take a nested path | Medium | Medium (blocks the flattening branch) | Refresh data preview first; troubleshooting block in step 17; presenter demo shows the picker working | Screenshot fallback `assets/screenshots/fallback/lab-02/` |
| 02 – Eventstream | Get data wizard splits `payload` into many columns instead of one `dynamic` | Medium | Medium (Lab 03's `mv-expand` expects `payload`) | Step 13 says to set nesting level so `payload` stays one column; if it happened anyway, delete the table and reconfigure | — |
| 02 – Eventstream | **SQL operator (preview)** missing in the tenant, rejects the query, or the input alias differs | Medium | Medium (Lab 05's `MinutesToArrival` comes from it) | Dry-run the exact query; step 26 says to copy the alias from the Inputs pane; documented no-code fallback (Filter → Group by → Stream with `MIN_ArrivalMs`) and Lab 05's KQL-queryset-alert fallback | Presenter workspace with the SQL node built |
| 02 – Eventstream | Expand won't take a nested array path (`Stops → linies_trajectes`) | Medium | Medium | Step 19 troubleshooting: promote the array with a Manage fields first, then Expand | — |
| 03 – Eventhouse | Update policy created before `StopsDim` loaded → `lookup` fails, policy errors | Medium | Medium | Lab orders Part B (load CSVs) before Part C; troubleshooting block shows `.show table … policy update` and the failed-ingestion query | — |
| 03 – Eventhouse | Attaching the policy fails: "Referencing additional tables … not allowed when streaming ingestion is enabled" (Eventstream turned streaming on for `BusArrivalsRaw`) | Certain unless C3a is run | Medium | Step 13 (C3a) disables streaming ingestion on the raw table and sets a 10-second batching window before the policy is attached; troubleshooting block names the error verbatim | — |
| 03 – Eventhouse | Raw `key` column typed `long` in Lab 02 → ingests null | Medium | Low (queries use `codi_parada`) | Lab 02 step 13 says string; Lab 03 troubleshooting explains the symptom | — |
| 03 – Eventhouse | Get data → Local file infers `StopCode` as string on one machine and long on another | Low | Medium (join type mismatch) | Lab tells attendees to set the type explicitly in **Edit columns**; KQL uses `tolong()` on the fact side defensively | — |
| 04 – Dashboard | Map visual doesn't render (missing lat/lon for a stop) | Low | Low | Query filters `isnotnull(Lat)` | Time chart + table only |
| 05 – Activator | Rule never fires in the session window (all buses on time) | Medium | Medium | Rule 1 threshold tuned from dry run; **Send me a test alert** works off history; rule 2 (heartbeat) can be *forced* by the presenter pausing the Function for 10 minutes during the break | Presenter's already-fired alert on screen |
| 05 – Activator | Teams action unavailable on event accounts | Medium | Low | Email is the default in every step | — |
| 06 – Fabric events | OneLake event → notebook takes 1–3 min (Spark cold start) and people think it failed | High (expected) | Low | Lab sets expectations, Monitor hub on the projector | — |
| 06 – Fabric events | Tenant has Fabric events disabled | Low | Medium | Check in prerequisites; presenter demo instead | Recording of Part C |
| 07 – Wrap-up | Attendees forget to pause streams → afternoon capacity throttled | Medium | Medium for the IQ half | Explicit numbered steps; Brian re-checks in IQ Lab 00 Part B | — |

## Fallback assets

- **Replay**: `infra/replay_events.py <recording.jsonl>` re-publishes a dry-run recording with timestamps
  shifted to now. Keep the recording on the presenter laptop *and* in cloud storage.
- **Instructor workspace**: fully built through Lab 06 before the day, for screen-share.
- **Screenshot fallback sequences**: `assets/screenshots/fallback/lab-02/` (eventstream operators) and
  `assets/screenshots/fallback/lab-06/` (OneLake alert wizard). Not yet captured.
- **Recordings**: link list in `assets/fallback-recordings/LINKS.md` (not yet recorded). Priority order:
  Lab 02 Part C (operators), Lab 06 Part B–C (alert wizard + notebook run).

## Pre-event checklist for the presenter

- [ ] Full dry run of Labs 01–06 in a fresh workspace within ~72 hours of the event.
- [ ] Recording captured; `replay_events.py` tested against the real hubs.
- [ ] TMB plan limits confirmed against the polling budget in `data-feed-contract.md` §1.
- [ ] Consumer-group sheet printed; 10 spare groups exist.
- [ ] Threshold sanity: during the dry run between 11:00 and 13:00 local, `Long wait at the Fòrum` fired at
      least three times; if not, lower the threshold in Lab 05 to 10 minutes.
- [ ] Confirm with Brian that IQ Lab 00 Part B includes the "pause your morning eventstreams" check.

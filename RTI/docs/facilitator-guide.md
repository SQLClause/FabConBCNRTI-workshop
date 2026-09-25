# Facilitator Guide — RTI half

Presenter-only notes. Not part of the attendee handout.

## Format decisions worth knowing

- **Portal-only for attendees, by design.** The IQ half installs Git/Python/`fab` live in its Module 00 and
  budgets 40 minutes for it. Doing any local install in the morning would either duplicate that or force a
  re-plan of Brian's agenda. Everything here happens in the Fabric portal; the only "local" thing is the
  presenter's Azure Function and Event Hubs.
- **Shared feed, private consumer groups, two hubs per feed.** Every attendee reads the same feed; consumer
  groups isolate their eventstreams from each other (two eventstreams on one consumer group fight over
  partitions). A hub allows 100 consumer groups, so for 120 people the Function publishes each envelope to
  `tmb-ibus-1-65` and `tmb-ibus-66-130` (and the metro pair); users 1–65 have consumer groups `user-001`…`user-065`
  on the first pair, users 66–130 have `user-066`…`user-130` on the second. Hand out the seat sheet at the start
  of Module 02, not before; people lose paper.
- **The feed is raw on purpose.** The Function publishes TMB's JSON unchanged inside an envelope: three nested
  arrays and two epoch clocks, no "minutes". Flattening it, in Eventstream (Lab 02, Expand ×3 and the SQL
  operator) and in KQL (Lab 03, `mv-expand` ×3), is a learning objective, not a chore. Don't "help" by
  pre-flattening or pre-computing in the Function.
- **Teach → show → do.** Each theory file ends with a "Live demo before the lab" script on the instructor
  workspace. With 120 people the demo is what keeps the helpers from drowning; don't skip it to buy lab time.
- **Theory lives in `XX-theory-*.md`, delivered live.** Same convention as the IQ half. Slides are not built
  yet for this half; if you build them, follow `FabricIQ/slides/README.md` (MarpToPptx onto the conference
  template) so the day looks like one deck.
- **Facilitator asides live inside the lab files** as `<!-- facilitator: ... -->` comments (invisible on
  GitHub) or visible `> 🎤 Facilitator note:` blockquotes.

## Before the day

- [ ] Run `RTIBCN/setup_event_hubs.sh` (namespace, four hubs, 130 consumer groups, Function role), then
      [`../infra/prepare-room.sh`](../infra/prepare-room.sh) (listen-only key, seat sheet). Print the seat sheet;
      project the namespace and listen key.
- [ ] Set the Function's `TMB_IBUS_STOPS` / `TMB_METRO_STATIONS` from the committed
      `artifacts/SampleData/stops.csv` and `metro_stations.csv` (the values are printed in
      [`../infra/README.md`](../infra/README.md) §1). During the dry run, confirm iTransit returns predictions for
      all 18 stops, in particular the venue stop 2689; if one stop comes back empty all morning, swap it for a
      neighbour from the same landmark and regenerate with `infra/build_stops_from_osm.py`.
- [ ] During the dry run, confirm: the Eventstream field picker shows `payload → parades` (Lab 02 step 17); Expand
      accepts the nested `Stops → linies_trajectes` path (step 19) or note the Manage-fields workaround; the Get
      data wizard lands `payload` as `dynamic` (step 13); and the SQL operator accepts the step 26 query with the
      input alias `[BusArrivalsEventstream-stream]`. These are the steps most likely to look different in a newer
      portal build, and the SQL operator is preview.
- [ ] Dry run **every lab** against a fresh workspace within 72 hours of the event. Record 60+ minutes of
      live events to JSONL for the replay fallback.
- [ ] Confirm whether the Microsoft-provided accounts have Teams. If not, say so in Module 05's theory so nobody
      spends five minutes hunting for the Teams action.
- [ ] Pre-provision your own `RTI Transit` workspace fully (through Lab 06) to screen-share as a fallback.
- [ ] Check TMB's service-status page the morning of the event. A metro strike or line closure is *great*
      live content but changes what "normal" looks like on the dashboard.

## Timing cues

See [`agenda.md`](agenda.md). Flex points, in the order you'd use them:

1. Module 04 (dashboard) compresses from 17 to 8 minutes: map tile + time chart only.
2. Module 06 Part D (workspace item events) becomes a presenter demo (it's marked that way already).
3. Module 03 Part F (OneLake availability + interchange query) is skippable.
4. Module 02 Part D (metro stream) can move to the start of Module 05 or be dropped; only three later steps
   reference metro and each says what to do without it.

Never compress: Module 02 Parts A–C (the feed must be flowing into `BusArrivalsRaw` before the first break),
Module 03 Parts B–D (update policy + materialized view are the morning's core), Module 05 rules 1–2, Module 07's
"park your workspace".

## If something breaks live

See [`risk-fallback-plan.md`](risk-fallback-plan.md). Short version:

- **No events in data preview for the whole room** → your feed is down. Start `replay_events.py` from the
  presenter laptop; attendees change nothing.
- **An eventstream shows paused or its destinations stop filling, and the capacity is busy** → capacity
  throttling. Fabric pauses eventstream processing when the capacity is over its limit and **does not resume it by itself**
  (dry run on a shared F16: manual Resume was needed). Recovery: open the eventstream in Live view, check each source/destination node's status,
  and **Resume** whatever is paused (pick **Now** when asked where to resume from). Then reduce load: pause the
  metro eventstream for anyone who built it, stop unneeded Activator rules, and close dashboard tabs. If half the
  room is affected, too many attendees share one P1 and it can't be resized on the day: pause the metro
  eventstreams room-wide and turn off dashboard live refresh; see `prerequisites/PREREQUISITES.md` §2.
- **No events for one attendee** → wrong consumer group, wrong hub name, or wrong key. 90% of cases are a
  trailing space in the shared access key, the other user range's hub (their consumer group only exists on their
  own hubs), or someone typing `$Default` (which works for exactly one person per hub and then kicks others off).
- **Manage fields can't see inside `payload`** → the stream had no schema yet when the pane opened. Refresh the
  data preview on the stream node first, then re-open the operator.
- **Lab 03 lookups return empty names for everyone** → someone typed the raw `key` column as `long` in Lab 02
  step 13 (it ingests as null). The lab's queries use `codi_parada` from the payload, so this only bites people
  who improvise their own `tolong(key)`; point them at the payload field.
- **SQL operator Test query returns 0 rows for everyone** → the Function isn't polling the venue stops. Check
  the `key` values in any attendee's data preview against `TMB_IBUS_STOPS` (should include 2689, 3347, 1090).
  This bit during authoring: the Function's example settings polled 108 and 1265 only.
- **Eventhouse table not filling although the eventstream shows data** → they published before configuring
  the destination table, or picked *Event processing before ingestion* and left "Activate ingestion" unchecked.
  Live view → destination node → check status.
- **Activator rule never fires** → check the rule is grouped by `LineCode` (not `StopCode`), the field is the
  `MinutesToArrival` column of the `ForumNextBus` stream, and that the rule is *started*. Then use **Send me
  a test alert**, which works off history.
- **OneLake event doesn't trigger the notebook** → the event filter on `subject` is case-sensitive and the
  folder path must match `Files/reference/` exactly; also the alert must be *started*.

## Room logistics

- Attendees need nothing but a browser. Venue Wi-Fi only carries portal traffic; Event Hubs → Fabric is
  cloud-to-cloud.
- Keep the Fabric **Monitor** hub open on the projector during Module 06 so the room sees notebook runs
  appear.
- Keep TMB's own iBus page for one venue stop open in a tab. Comparing "what TMB says" with "what our
  dashboard says" is the most convincing two seconds of the morning.

## Handoff to the afternoon

Module 07's wrap-up (10 min) has attendees pause both eventstreams and stop `TransitAlerts` rules so the
shared P1 capacities have their CU free for Ontology/Data Agent. Tell Brian how many attendees were in the room and
whether anyone is on a shared capacity. See [`alignment-with-fabric-iq.md`](alignment-with-fabric-iq.md) §D for
the wording edits the IQ half should make so its "this morning you built…" lines are accurate.

# Facilitator Guide — RTI half

Presenter-only notes. Not part of the attendee handout.

## Format decisions worth knowing

- **Portal-only for attendees, by design.** The IQ half installs Git/Python/`fab` live in its Module 00 and
  budgets 40 minutes for it. Doing any local install in the morning would either duplicate that or force a
  re-plan of Brian's agenda. Everything here happens in the Fabric portal; the only "local" thing is the
  presenter's Azure Function and Event Hubs.
- **Shared feed, private consumer groups, two hubs per feed.** Every attendee reads the same feed; consumer
  groups isolate their eventstreams from each other (two eventstreams on one consumer group fight over
  partitions). A hub allows 100 consumer groups, so for 120 people the Function publishes each event to
  `tmb-ibus-a` and `tmb-ibus-b` (and the metro pair) and the seat sheet assigns half the room to each letter.
  Hand out the seat sheet at the start of Module 02, not before; people lose paper.
- **Teach → show → do.** Each theory file ends with a "Live demo before the lab" script on the instructor
  workspace. With 120 people the demo is what keeps the helpers from drowning; don't skip it to buy lab time.
- **Theory lives in `XX-theory-*.md`, delivered live.** Same convention as the IQ half. Slides are not built
  yet for this half; if you build them, follow `FabricIQ/slides/README.md` (MarpToPptx onto the conference
  template) so the day looks like one deck.
- **Facilitator asides live inside the lab files** as `<!-- facilitator: ... -->` comments (invisible on
  GitHub) or visible `> 🎤 Facilitator note:` blockquotes.

## Before the day

- [ ] Run [`../infra/create-eventhubs.sh`](../infra/create-eventhubs.sh) with `--attendees 120` (10 spare groups
      are added; two hubs per feed result). Print the seat sheet; project the namespace and listen key.
- [ ] Run [`../infra/resolve_stops.py`](../infra/resolve_stops.py) once, review `artifacts/SampleData/stops.csv`
      and `metro_stations.csv`, commit them, and set the Function's `TMB_IBUS_STOPS` / `TMB_METRO_STATIONS` from them.
- [ ] Apply [`../infra/function-changes/`](../infra/function-changes/README.md) to `RTIBCN/` so the Function publishes
      flat per-prediction events (the labs' field names), and pin `flatten_metro()` to a real iTransit response.
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
- **No events for one attendee** → wrong consumer group, wrong hub letter, or wrong key. 90% of cases are a
  trailing space in the shared access key, the other hub letter (their consumer group only exists on their own
  hub), or someone typing `$Default` (which works for exactly one person per hub and then kicks others off).
- **Eventhouse table not filling although the eventstream shows data** → they published before configuring
  the destination table, or picked *Event processing before ingestion* and left "Activate ingestion" unchecked.
  Live view → destination node → check status.
- **Activator rule never fires** → check the rule is grouped by `LineCode` (not `StopCode`), the property filter
  is `Rank == 1`, and that the rule is *started*. Then use **Send me a test alert**, which works off history.
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
per-attendee capacity is free for Ontology/Data Agent. Tell Brian how many attendees were in the room and
whether anyone is on a shared capacity. See [`alignment-with-fabric-iq.md`](alignment-with-fabric-iq.md) §D for
the wording edits the IQ half should make so its "this morning you built…" lines are accurate.

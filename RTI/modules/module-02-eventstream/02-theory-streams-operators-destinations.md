# Module 02 Theory: Eventstream — Sources, Streams, Operators, Destinations

**Duration:** 15 minutes (10 concepts + 5 live demo)
**Prerequisites:** Module 01 complete (`RTI Transit`, `TransitEventhouse`, `TransitLakehouse` exist).

**Learning objectives**
- Describe an eventstream as *sources → default stream → (operators →) destinations*, and know what a derived stream is.
- Pick the right Eventhouse ingestion mode (direct vs processed) for a given need.
- Know the operator catalogue and the one window type we use today (tumbling).
- Understand why every attendee needs their own consumer group on the shared Event Hubs feed.

## The mental model

```
 [source] ──► default stream ──► [destination: Eventhouse, direct ingestion]   (raw, as-is)
                   │
                   ├─► [Filter] ─► [Group by 1-min tumbling] ─► [destination: Eventhouse, processed]  (aggregated)
                   │
                   └─► [Filter: venue stop] ─► derived stream "ForumArrivals" ─► (Module 05: Activator)
```

- **Source**: where events come from. Today: **Azure Event Hubs** (GA, the workhorse connector). The gallery has
  ~30 others: IoT Hub, Service Bus, Kafka, Pub/Sub, Kinesis, MQTT (preview), database CDC feeds, an **HTTP**
  poller (preview), sample data, and every Fabric/Azure event type.
- **Default stream**: the raw feed inside the eventstream, exactly as received.
- **Operators**: no-code transformations placed *between* the stream and a destination: **Filter**, **Manage
  fields** (rename, remove, change type, add computed fields with built-in string/date/math functions such as
  `Left`, `Substring`, `Replace`, `RegExMatch`; no concatenation), **Aggregate**, **Group by**
  (aggregations over a time window, grouped by fields), **Union**, **Expand** (flatten arrays), **Join**
  (stream-to-stream), and a **SQL operator** (preview) when the no-code shapes aren't enough.
- **Derived stream**: the output of an operator chain published as a *named stream* of its own. It shows up in
  Real-Time hub, can be paused/resumed, and can be consumed by other destinations or other teams without them
  knowing how it was produced. Think "curated topic".
- **Destinations**: **Eventhouse**, **Lakehouse**, **Activator**, **Custom endpoint** (let external apps read
  the stream, i.e. fan-out to consumers outside Fabric), **Derived stream**, **Spark notebook** (preview).

## Two ways into an Eventhouse

| Mode | What happens | Use when |
|---|---|---|
| **Direct ingestion** | Events are handed to the KQL database's own ingestion; you configure the table + mapping in the Eventhouse **Get data** wizard after publishing | You want the raw stream, unchanged, with Kusto doing any shaping later (update policies, materialized views). **Default choice for raw tables.** |
| **Event processing before ingestion** | Operators run in the eventstream; the result is written to a table you name in the destination dialog | You want to *reduce* before storing (aggregates, filters) or *reshape* (flatten) and don't need the raw rows |

Today's raw table (`BusArrivalsRaw`) uses direct ingestion; the per-minute aggregate (`BusWaitByStopMinute`) uses
processed ingestion. Storing both is a common pattern: raw for forensics and replay, aggregate for cheap dashboards.

## Windows, briefly

**Group by** needs a window. **Tumbling** windows are fixed, non-overlapping (00:00–00:59, 01:00–01:59…): one
row per stop/line per minute. **Hopping** overlap, **sliding** advance per event, **session** close after a
gap, **snapshot** groups events with identical timestamps. Tumbling is the right default for "per minute"
summaries and it's what we use. A window only emits when it *closes*, so the preview shows nothing for the first
60–90 seconds. That's expected.

## Why consumer groups (and hub letters) matter today

Everyone reads the *same* feed. Event Hubs delivers each partition to **one** reader per consumer group. If two
eventstreams share `$Default`, they steal partitions from each other and both see gaps. Your personal
`attendee-NNN` group gives your eventstream its own cursor over the whole hub. A hub holds at most 100 consumer
groups, so with 120 of us the feed is duplicated into two hubs per feed (`tmb-ibus-a` / `tmb-ibus-b`); your seat
sheet says which letter is yours. The key you're given is **listen-only**; nobody in the room can write to the feed.

## What this morning's stream looks like

```json
{ "EventType":"BusArrival", "PolledAtUtc":"2026-09-30T07:15:02Z", "StopCode":1497, "LineCode":"H16",
  "RouteId":"1601", "Destination":"Forum Campus Besos", "Rank":1, "MinutesToArrival":4,
  "SecondsToArrival":230, "ArrivalText":"4 min", "IsStale":false, "Source":"TMB iBus" }
```

Notice what is **not** there: no stop name, no coordinates, no line origin/destination. The feed is codes and
numbers. Module 03 adds the meaning. This afternoon Brian makes the same point about a `FreezerId` and a
temperature; keep the parallel in mind.

## Live demo before the lab (5 minutes, instructor workspace)

Click through the lab path once, narrating the UI, before anyone touches their own workspace:

1. Open the pre-built `BusArrivalsEventstream` in **Edit** mode. Point at the source node: "this is the Event
   Hubs connection; you'll type a namespace, a hub name from your sheet, the listen key, and *your* consumer group".
2. **Data preview** on the stream node: read one event aloud, field by field. "No stop name. No coordinates."
3. Hover the stream node → **+** → show the operator menu (Filter, Manage fields, Group by, …) without adding one.
4. Click the existing **Group by** node: show aggregations, group-by fields, the tumbling window. "Nothing
   appears for a minute; that's the window closing, not a bug."
5. Click the two Eventhouse destinations: one **Direct ingestion**, one **Event processing before ingestion**.
   Point at the table names.
6. Switch to **Live** view: **Data insights** on a destination, and the **ForumArrivals** derived stream.
   "That's what you build in the next 35 minutes."

> 🎤 Facilitator note: the one thing to protect in this theory slot is the direct-vs-processed table. Attendees
> who pick the wrong mode in the lab lose ten minutes. The demo is not optional: with 120 people, five minutes of
> "you'll see this screen" saves twenty minutes of helpers walking the room.

*Sources: [Eventstream overview](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/overview),
[Add and manage sources](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-manage-eventstream-sources),
[Event processing editor](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/process-events-using-event-processor-editor),
[Eventhouse destination](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database),
[Derived streams](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-derived-stream)*

Continue to [Lab 02: Build the transit eventstream](lab-02-build-the-transit-eventstream.md).

# Lab 02: Build the Transit Eventstream

**Duration:** 35 minutes
**Prerequisites:** Module 01 complete. `RTI Transit` contains `TransitEventhouse` (with its default KQL
database) and `TransitLakehouse`. You have the four values from the facilitator's seat sheet: Event Hubs
**namespace name**, **your two hub names** (`tmb-ibus-1-65` + `tmb-metro-1-65`, or `tmb-ibus-66-130` +
`tmb-metro-66-130`), the **`attendee-listen`** shared access key: `hmUG6ik4kG63LStmc4uKY6EX/DoCsTQ1e+AEhAypPIg=`, and **your** consumer group `user-NNN`.

**Learning objectives**
- Connect an eventstream to an Azure Event Hubs source with a shared-access key and a dedicated consumer group.
- Read a raw API envelope in the data preview and understand why it isn't yet usable as events.
- Route the raw stream to an Eventhouse table with **direct ingestion**, keeping the nested payload as `dynamic`.
- **Flatten** the payload in the stream with **Manage fields** and **Expand**, then **Filter** and **Group by**
  (1-minute tumbling window) into a second table with **event processing before ingestion**.
- Publish a **derived stream** with the next bus per line at the venue stop, for Module 05.
- **[metro]** Create a second eventstream from Real-Time hub's **Connect to data source** entry point.

## Before you begin

Confirm your environment matches this state before starting:
- [ ] `RTI Transit` workspace open; `TransitEventhouse` and `TransitLakehouse` present.
- [ ] Namespace name, your two hub names, the `attendee-listen` key, and your `user-NNN` written down.
      **Do not use `$Default`**, and don't use the other user range's hubs: your consumer group only exists on yours.
- [ ] You know the **venue stop code** (first row of
      [`artifacts/SampleData/stops.csv`](../../artifacts/SampleData/stops.csv), `Zone = Venue`, `IsPrimary = true`;
      the facilitator also has it on screen). It's referred to below as `<VENUE_STOP_CODE>`.

## Steps

### Part A — Create the eventstream and add the Event Hubs source

1. In the **RTI Transit** workspace, **click** **+ New item**, **type** `Eventstream`, **select** **Eventstream**,
   **type** `BusArrivalsEventstream` as the name, and **click** **Create**.

   ![Step 1](../../assets/screenshots/lab-02/step-01.png)

   > ✅ Expected result: an empty eventstream canvas opens in **Edit** mode with a **Connect data sources** tile.

2. **Click** **Connect data sources**. In the **Select a data source** page, **type** `Event Hubs` in the search box
   and **click** **Connect** on the **Azure Event Hubs** tile.

3. On **Configure connection settings**, **confirm** the feature level is **Basic**, then **click** **New connection**.

4. Under **Connection settings**, **type** the **Event Hubs namespace** name and **type** your bus hub from the
   seat sheet as the **Event hub**: `tmb-ibus-1-65` or `tmb-ibus-66-130`.

5. Under **Connection credentials**:
   - **Connection name**: `tmb-ibus-listen`
   - **Authentication kind**: **Shared Access Key**
   - **Shared Access Key Name**: `attendee-listen`
   - **Shared Access Key**: **paste** the key from the facilitator's slide
   - **Click** **Connect**.

   ![Step 5](../../assets/screenshots/lab-02/step-02.png)

   <details>
   <summary>Troubleshooting — "Unable to connect" / 401</summary>

   Nine times out of ten this is a trailing space or a truncated paste in the key. Re-copy the key, paste it into
   a plain-text editor first, and check it ends with `=`. Also confirm the key *name* is exactly `attendee-listen`.
   </details>

6. For **Consumer group**, **type** your personal `user-NNN`. For **Data format**, **select** **JSON**.

   > ⚠️ Sixty-five attendees read each hub. If you type `$Default` (or someone else's group) your eventstream
   > will compete for partitions with theirs and the connection will throw an error. If the connection fails with a
   > "consumer group not found" style error, you've typed the other user range's hub.

7. In the **Source details** pane on the right, **click** the pencil next to the source name and **type**
   `TMBBusArrivals`. **Click** **Next**, review the summary, and **click** **Add**.

   > ✅ Expected result: the canvas shows **TMBBusArrivals → BusArrivalsEventstream-stream**.

8. **Click** the **BusArrivalsEventstream-stream** node, then in the bottom pane **click** **Data preview** and
   **Refresh** if it's empty.

   ![Step 8](../../assets/screenshots/lab-02/step-03.png)

   > ✅ Expected result: within ~30 seconds rows appear with four top-level fields: `source` (`tmb.ibus`), `key`
   > (a stop code, as text), `fetchedAt`, and `payload`. **Expand** a `payload` cell: inside is TMB's response as
   > it came off the wire, `status` plus a `data.ibus` **array** with one element per upcoming bus: `line`,
   > `routeId`, `destination`, `t-in-min`, `t-in-s`, `text-ca`. One event on the hub is one *stop*, not one bus,
   > and the numbers you care about are two levels down in an array. That's the shape most real APIs give you;
   > Part C is where you turn it into events.

   <details>
   <summary>Troubleshooting — preview stays empty</summary>

   1. Wait a full minute; the first poll after connecting can take that long.
   2. Check your neighbour. If nobody sees data, the feed itself is down; the facilitator switches to the
      replay and you change nothing.
   3. If only you see nothing, re-open the source (click **TMBBusArrivals** → **Edit**) and check the consumer
      group and the event hub name against your seat sheet.
   </details>

<!-- facilitator: this is where wrong consumer groups surface. Walk the room. Anyone with $Default gets a spare group (user-121..130) now, not later. -->

### Part B — Raw envelopes → Eventhouse (direct ingestion)

9. **Click** **Add destination** on the ribbon and **select** **Eventhouse**.

10. In the **Eventhouse** pane:
    - **Select** **Direct ingestion**
    - **Destination name**: `BusArrivalsRaw`
    - **Workspace**: `RTI Transit`
    - **Eventhouse**: `TransitEventhouse`
    - **KQL Database**: `TransitEventhouse`
    - **Click** **Save**.

    > ✅ Expected result: an **Eventhouse** destination node appears, connected to the stream. If it isn't
    > connected, **drag** from the stream node's right edge to the destination.

11. **Click** **Publish** on the ribbon.

    > ✅ Expected result: the canvas switches to **Live** view. The Eventhouse node shows a **Configure** button
    > with a warning that the destination isn't configured yet. That's expected for direct ingestion.

12. **Click** **Configure** on the Eventhouse node. The Eventhouse's **Get data** wizard opens.
    - **Confirm** the database is **TransitEventhouse**
    - **Click** **+ New table**, **type** `BusArrivalsRaw`, and **confirm**
    - **Keep** the proposed **Data connection name** and **click** **Next**

13. On **Inspect the data**, **wait** for the sample to load, **confirm** **Format** is **JSON**, then **click**
    **Edit columns**. You want exactly four columns; fix any that differ, then **Apply**:

    | Column | Type |
    |---|---|
    | `source` | `string` |
    | `key` | `long` |
    | `fetchedAt` | `datetime` |
    | `payload` | `dynamic` |

    ![Step 13](../../assets/screenshots/lab-02/step-04.png)

    > ✅ Expected result: `payload` is `dynamic`, which is Kusto's JSON type. If the wizard instead proposes a
    > flattened list of columns (`payload_status`, `payload_data_ibus`…), set **Nested levels** to `1` (or
    > switch the JSON nesting level back to the top level) so the payload stays as one JSON column: Lab 03
    > flattens it in KQL on purpose.

15. **Click** **Finish**, wait for the three green checks, then **click** **Close**.

    > ✅ Expected result: back in Live view the Eventhouse node reads **BusArrivalsRaw** with a green status.

    *Adapted from: [Add an Eventhouse destination — Direct ingestion](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database#direct-ingestion-mode)*

### Part C — Operators: flatten, filter, aggregate, and a derived stream

15. **Click** **Edit** on the ribbon to return to Edit mode.

16. We want a *second* branch off the stream (the raw destination stays as it is), so **hover** over the
    **BusArrivalsEventstream-stream** node itself, **click** its **+**, and **select** **Manage fields**.

17. In the **Manage fields** pane, **Operation name** `PickPredictions`. **Click** **Add field** three times:
    - `key` — keep the name
    - `fetchedAt` — keep the name
    - **expand** `payload` → `data` → **select** `ibus` (the array), and **rename** it to `Predictions`
    - **Click** **Save**

    > ✅ Expected result: the **Test result** tab (bottom pane, **Refresh**) shows three columns: `key`,
    > `fetchedAt`, `Predictions`, the last one an array of 2–8 objects per row. Everything else from the envelope
    > is gone.

    <details>
    <summary>Troubleshooting — I can't see inside <code>payload</code> in the field picker</summary>

    The picker only shows nested fields once the stream has a schema from real data. Make sure the data preview
    on the stream node showed rows (step 8), then re-open the Manage fields pane. If `payload` still shows as a
    single opaque field, add it as-is here, add an **Expand** on `payload.data.ibus` in the next step by typing
    the path, and continue.
    </details>

18. **Hover** over **PickPredictions**, **click** **+**, **select** **Expand**. **Operation name** `OnePerBus`,
    **Array field** `Predictions`, **click** **Save**.

    ![Step 18](../../assets/screenshots/lab-02/step-05.png)

    > ✅ Expected result: Test result now has **one row per upcoming bus**: the same `key` and `fetchedAt`
    > repeated, and `Predictions` is now a single object (`line`, `routeId`, `destination`, `t-in-min`, …) instead
    > of an array. Five predictions in an envelope became five events. This is the "Expand" operator's only job,
    > and it is the single most useful thing to know when an API hands you arrays.

    *Adapted from: [Process event data by using the event processing editor](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/process-events-using-event-processor-editor)*

19. **Hover** over **OnePerBus**, **click** **+**, **select** **Manage fields**. **Operation name**
    `ShapeBusArrivals`. **Add** these fields (expand `Predictions` to reach the nested ones), **renaming** and
    **changing type** where shown:

    | Add | Rename to | Change type |
    |---|---|---|
    | `key` | `StopCode` | **Int64** |
    | `fetchedAt` | `PolledAtUtc` | **DateTime** (if not already) |
    | `Predictions` → `line` | `LineCode` | |
    | `Predictions` → `routeId` | `RouteId` | |
    | `Predictions` → `destination` | `Destination` | |
    | `Predictions` → `t-in-min` | `MinutesToArrival` | **Int64** |
    | `Predictions` → `t-in-s` | `SecondsToArrival` | **Int64** |

    Then **Add field** → **Built-in Function** → **String** → **Left**, input `Predictions` → `line`, length `1`,
    name `LineFamily`. **Click** **Save**.

    > ✅ Expected result: Test result shows flat, typed events: `StopCode 1497, PolledAtUtc …, LineCode H16,
    > RouteId 1601, Destination Forum Campus Besos, MinutesToArrival 4, SecondsToArrival 230, LineFamily H`. Compare
    > with step 8: same information, now something a rule or a chart can use. `LineFamily` is `H`/`V`/`D` for the
    > orthogonal network and a digit for trunk lines like 7 and 59.

    <details>
    <summary>What else Manage fields can do</summary>

    Rename, remove, reorder, change type, and add computed fields with the built-in functions: string (`Left`,
    `Right`, `Upper`, `Lower`, `Len`, `Trim`, `Replace`, `Substring`, `RegExMatch`, `Json_Parse`, `Json_Stringify`, …),
    date/time and math. There is no concatenation function, which is why Module 05 uses `LineCode` alone as the
    Activator object and filters on the stop instead of building a combined key.
    </details>

20. **Hover** over **ShapeBusArrivals**, **click** **+**, **select** **Group by**. Configure:
    - **Operation name**: `WaitByStopMinute`
    - **Aggregations**: **Minimum** of `MinutesToArrival`, **Average** of `MinutesToArrival`, **Count** of
      `MinutesToArrival` (use **Add aggregation** for each)
    - **Group aggregations by**: `StopCode`, `LineCode`, `LineFamily`
    - **Time window**: **Tumbling**, **Duration** `1` **minute**
    - **Click** **Save**

    > ✅ Expected result: after **60–90 seconds** the Test result shows one row per stop/line per minute with
    > `MIN_MinutesToArrival` (the next bus), `AVG_MinutesToArrival`, `COUNT_MinutesToArrival`, `LineFamily` and a
    > window end timestamp. Nothing appears until the first window closes; that's how tumbling windows work.
    > The minimum is how we get "the next bus" without a rank column: with two predictions per line, the smaller
    > one is the one arriving first.

21. **Hover** over **WaitByStopMinute**, **click** **+**, **select** **Eventhouse**. The pane is pre-set to
    **Event processing before ingestion**. Configure:
    - **Destination name**: `BusWaitByStopMinute`
    - **Workspace** `RTI Transit`, **Eventhouse** `TransitEventhouse`, **KQL database** `TransitEventhouse`
    - **Destination table**: **Create new** → `BusWaitByStopMinute`
    - **Input data format**: **JSON**
    - **Leave** **Activate ingestion after adding the data source** checked
    - **Click** **Save**

    *Adapted from: [Add an Eventhouse destination — Event processing before ingestion](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database#event-processing-before-ingestion)*

22. Now the venue branch for Module 05. **Hover** over **ShapeBusArrivals** again, **click** **+**, **select**
    **Filter**. **Name** it `VenueStopOnly`, **condition** **`StopCode` equals `<VENUE_STOP_CODE>`**, **Save**.

23. **Hover** over **VenueStopOnly**, **click** **+**, **select** **Group by**. **Operation name** `NextBusByLine`,
    **Aggregation** **Minimum** of `MinutesToArrival`, **Group aggregations by** `LineCode`, `StopCode`,
    **Tumbling** `1` **minute**, **Save**.

24. **Hover** over **NextBusByLine**, **click** **+**, **select** **Stream**. **Name** it `ForumNextBus`,
    **Data format** **JSON**, **click** **Save**.

    > ✅ Expected result: the canvas now has three branches off the stream: direct → `BusArrivalsRaw`;
    > `PickPredictions → OnePerBus → ShapeBusArrivals → WaitByStopMinute → BusWaitByStopMinute`; and
    > `ShapeBusArrivals → VenueStopOnly → NextBusByLine → ForumNextBus`. Check the **Authoring errors** tab is empty.

    *Adapted from: [Add a derived stream destination](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-derived-stream)*

25. **Click** **Publish**.

    > ✅ Expected result: Live view. All destination nodes show a healthy status within a minute or two. **Click**
    > **ForumNextBus** → **Data preview**: one row per line at your venue stop per minute, with
    > `MIN_MinutesToArrival`. **Click** `BusWaitByStopMinute` → **Data insights**: incoming events climb once a minute.

<!-- facilitator: leave your own Live view on the projector. The three-branch canvas is the picture of the module; point at each branch and say raw / flattened+aggregated / curated. -->

> 🎤 Facilitator note: ask the room why we kept the raw envelopes *and* built the flat aggregate. The answer
> (raw for replay, forensics and Module 03's in-database flattening; aggregate for cheap dashboards and alerts)
> sets up Module 03.

### Part D — [metro] A second stream, from Real-Time hub

26. **Click** **Real-Time** in the left navigation, then **+ Connect to data source**. **Search** `Event Hubs`,
    **click** **Connect** on **Azure Event Hubs**.

27. **Click** **New connection** and configure it like step 4–5 but with **Event hub** = your metro hub from the
    seat sheet (`tmb-metro-1-65` or `tmb-metro-66-130`, same user range as your bus hub) and **Connection name**
    `tmb-metro-listen`. **Click** **Connect**. **Consumer group**: your same `user-NNN`. **Data format**: **JSON**.

    > ✅ Expected result: the same key and consumer group work for both hubs: consumer groups are per event hub,
    > so `user-NNN` on the metro hub is a different cursor from `user-NNN` on the bus hub.

28. In **Stream details** on the right, **select** workspace **RTI Transit**, **click** the pencil next to
    **Eventstream name** and **type** `MetroArrivalsEventstream`. **Click** **Next**, then **Connect**.

    > ✅ Expected result: Real-Time hub confirms the stream was created and offers **Open eventstream**. This is
    > the point of Part D: the hub is a front door, the result is an ordinary Eventstream item in your workspace.

29. **Click** **Open eventstream**, **click** **Edit**, **add** an **Eventhouse** destination with **Direct
    ingestion** named `MetroArrivalsRaw` into `TransitEventhouse`, **Publish**, **Configure** the destination
    into a **new table** `MetroArrivalsRaw` exactly as in steps 12–14: `source`, `key` string; `fetchedAt`
    datetime; `payload` dynamic.

    > ✅ Expected result: one envelope per poll, `key` = `"120,122,321"`-style list of every station, and a
    > `payload` with **four** nested arrays (`linies → estacions → linies_trajectes → propers_trens`). Too deep
    > for the no-code editor to be fun; Lab 03 Part F flattens it in four lines of KQL.

    *Adapted from: [Real-Time hub — connect to data source](https://learn.microsoft.com/fabric/real-time-hub/real-time-hub-overview)*

## Checkpoint

At the end of this lab, your **RTI Transit** workspace should contain:
- `BusArrivalsEventstream` (published, Live view healthy) with source `TMBBusArrivals` and three branches:
  - default stream → Eventhouse **direct ingestion** → table `BusArrivalsRaw` (raw envelopes, `payload` dynamic)
  - `PickPredictions` → `OnePerBus` → `ShapeBusArrivals` → `WaitByStopMinute` → Eventhouse **processed** → table `BusWaitByStopMinute` (flat, one row per stop/line/minute)
  - `ShapeBusArrivals` → `VenueStopOnly` → `NextBusByLine` → derived stream **`ForumNextBus`**
- **[metro]** `MetroArrivalsEventstream` → `MetroArrivalsRaw` (raw envelopes)
- In `TransitEventhouse`: tables `BusArrivalsRaw`, `BusWaitByStopMinute`, `MetroArrivalsRaw` with rows arriving

Real API responses from the streets outside are now landing in your database, and you have already turned one of
them into flat events once. Continue to
[Module 03: Eventhouse & KQL](../module-03-eventhouse-kql/lab-03-enrich-and-analyze-in-eventhouse.md), where the
same flattening happens inside the database.

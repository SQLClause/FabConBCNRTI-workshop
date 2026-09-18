# Lab 02: Build the Transit Eventstream

**Duration:** 35 minutes
**Prerequisites:** Module 01 complete. `RTI Transit` contains `TransitEventhouse` (with its default KQL
database) and `TransitLakehouse`. You have the four values from the facilitator's seat sheet: Event Hubs
**namespace name**, **your hub letter** (`a` or `b`), the **`attendee-listen`** shared access key, and **your**
consumer group `attendee-NNN`.

**Learning objectives**
- Connect an eventstream to an Azure Event Hubs source with a shared-access key and a dedicated consumer group.
- Read the live data preview and publish.
- Route the raw stream to an Eventhouse table with **direct ingestion**, configuring the table in the Get data wizard.
- Add **Manage fields**, **Filter** and **Group by** (1-minute tumbling window) operators and write the result to a second table with **event processing before ingestion**.
- Publish a **derived stream** scoped to the venue stop, for Module 05.
- **[metro]** Create a second eventstream from Real-Time hub's **Connect to data source** entry point.

## Before you begin

Confirm your environment matches this state before starting:
- [ ] `RTI Transit` workspace open; `TransitEventhouse` and `TransitLakehouse` present.
- [ ] Namespace name, your hub letter, the `attendee-listen` key, and your `attendee-NNN` written down.
      **Do not use `$Default`**, and don't use the other hub letter: only your own hub has your consumer group.
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
   seat sheet as the **Event hub**: `tmb-ibus-a` or `tmb-ibus-b`.

5. Under **Connection credentials**:
   - **Connection name**: `tmb-ibus-listen`
   - **Authentication kind**: **Shared Access Key**
   - **Shared Access Key Name**: `attendee-listen`
   - **Shared Access Key**: **paste** the key from the facilitator's sheet
   - **Click** **Connect**.

   ![Step 5](../../assets/screenshots/lab-02/step-02.png)

   <details>
   <summary>Troubleshooting — "Unable to connect" / 401</summary>

   Nine times out of ten this is a trailing space or a truncated paste in the key. Re-copy the key, paste it into
   a plain-text editor first, and check it ends with `=`. Also confirm the key *name* is exactly `attendee-listen`.
   </details>

6. For **Consumer group**, **type** your personal `attendee-NNN`. For **Data format**, **select** **JSON**.

   > ⚠️ Sixty-odd attendees read each hub. If you type `$Default` (or someone else's group) your eventstream
   > will compete for partitions with theirs and both of you will see gaps. If the connection fails with a
   > "consumer group not found" style error, you've typed the other hub letter.

7. In the **Source details** pane on the right, **click** the pencil next to the source name and **type**
   `TMBBusArrivals`. **Click** **Next**, review the summary, and **click** **Add**.

   > ✅ Expected result: the canvas shows **TMBBusArrivals → BusArrivalsEventstream-stream**.

   *Adapted from: [Add an Azure Event Hubs source to an eventstream](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-azure-event-hubs)*

8. **Click** the **BusArrivalsEventstream-stream** node, then in the bottom pane **click** **Data preview** and
   **Refresh** if it's empty.

   ![Step 8](../../assets/screenshots/lab-02/step-03.png)

   > ✅ Expected result: within ~30 seconds rows appear with `EventType`, `PolledAtUtc`, `StopCode`, `LineCode`,
   > `RouteId`, `Destination`, `Rank`, `MinutesToArrival`, `SecondsToArrival`, `ArrivalText`, `IsStale`,
   > `Source`. Look at `MinutesToArrival` on a couple of rows: that's the number TMB's own app shows at the stop
   > right now.

   <details>
   <summary>Troubleshooting — preview stays empty</summary>

   1. Wait a full minute; the first poll after connecting can take that long.
   2. Check your neighbour. If nobody sees data, the feed itself is down; the facilitator switches to the
      replay and you change nothing.
   3. If only you see nothing, re-open the source (click **TMBBusArrivals** → **Edit**) and check the consumer
      group and the event hub name (`tmb-ibus-a` or `tmb-ibus-b`, matching your seat sheet).
   </details>

<!-- facilitator: this is where wrong consumer groups surface. Walk the room. Anyone with $Default gets a spare group now, not later. -->

### Part B — Raw stream → Eventhouse (direct ingestion)

9. **Click** **Add destination** on the ribbon and **select** **Eventhouse**.

10. In the **Eventhouse** pane:
    - **Select** **Direct ingestion**
    - **Destination name**: `BusArrivalsRaw`
    - **Workspace**: `RTI Transit`
    - **Eventhouse**: `TransitEventhouse`
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

13. On **Inspect the data**, **wait** for the sample to load (it can take a minute), **confirm** **Format** is
    **JSON**, then **click** **Edit columns** and **check** the inferred types. Fix any that differ from this list,
    then **click** **Apply**:

    | Column | Type |
    |---|---|
    | `EventType`, `LineCode`, `RouteId`, `Destination`, `ArrivalText`, `Source` | `string` |
    | `PolledAtUtc` | `datetime` |
    | `StopCode`, `Rank`, `MinutesToArrival`, `SecondsToArrival` | `long` (or `int`) |
    | `IsStale` | `bool` |

    ![Step 13](../../assets/screenshots/lab-02/step-04.png)

14. **Click** **Finish**, wait for the three green checks, then **click** **Close**.

    > ✅ Expected result: back in Live view the Eventhouse node reads **BusArrivalsRaw** with a green status. In
    > Module 03 you query this table; if you're curious now, open `TransitEventhouse` → **TransitEventhouse**
    > database → **Tables** and you'll see `BusArrivalsRaw` (it may take 1–2 minutes for the first rows).

    *Adapted from: [Add an Eventhouse destination — Direct ingestion](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database#direct-ingestion-mode)*

### Part C — Operators: shape, filter, aggregate, and a derived stream

15. **Click** **Edit** on the ribbon to return to Edit mode.

16. We want a *second* branch off the stream (the raw destination stays as it is), so **hover** over the
    **BusArrivalsEventstream-stream** node itself, **click** its **+**, and **select** **Manage fields**.

17. In the **Manage fields** pane:
    - **Operation name**: `ShapeBusArrivals`
    - **Click** **Add all fields**
    - **Remove** `Source` and `ArrivalText` (we don't need text we can derive)
    - **Click** **Add field** → **Built-in Function** → **String** → **Left**. **Choose** `LineCode` as the
      input, **type** `1` for the length, and **name** the result `LineFamily`
    - **Click** **Save**

    > ✅ Expected result: the **Test result** tab (bottom pane, click **Refresh**) shows the same rows minus the
    > two removed fields, plus `LineFamily`: `H` for horizontal lines (H16), `V` for vertical (V15), `D` for
    > diagonal (D20), and a digit for the classic trunk lines (7, 47, 59). TMB's network is literally encoded in
    > the first character of the line name; now it's a field you can group and alert on.

    <details>
    <summary>What else Manage fields can do</summary>

    Rename and reorder fields, change a field's type (for example `StopCode` to string), and add computed fields
    with the built-in functions: string (`Left`, `Right`, `Upper`, `Lower`, `Len`, `Trim`, `Replace`, `Substring`,
    `RegExMatch`, `Json_Parse`, `Json_Stringify`, …), date/time and math. There is no concatenation function, which
    is why Module 05 uses `LineCode` alone as the Activator object and filters on the stop instead of building a
    combined key here.
    </details>

    *Adapted from: [Process event data by using the event processing editor](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/process-events-using-event-processor-editor)*

18. **Hover** over the **ShapeBusArrivals** node, **click** **+**, **select** **Filter**. **Name** it
    `NextBusOnly`, **set** the condition to **`Rank` equals `1`**, and **click** **Save**.

    > ✅ Expected result: Test result shows only `Rank = 1` rows (the next bus per stop and line).

19. **Hover** over **NextBusOnly**, **click** **+**, **select** **Group by**. Configure:
    - **Operation name**: `WaitByStopMinute`
    - **Aggregations**: **Average** of `MinutesToArrival`, **Minimum** of `MinutesToArrival`, **Count** of
      `MinutesToArrival` (use **Add aggregation** for each)
    - **Group aggregations by**: `StopCode`, `LineCode`, `LineFamily`
    - **Time window**: **Tumbling**, **Duration** `1` **minute**
    - **Click** **Save**

    ![Step 19](../../assets/screenshots/lab-02/step-05.png)

    > ✅ Expected result: after **60–90 seconds** the Test result shows one row per stop/line per minute with
    > `AVG_MinutesToArrival`, `MIN_MinutesToArrival`, `COUNT_MinutesToArrival`, `LineFamily` and a window end
    > timestamp.
    > Nothing appears until the first window closes; that's how tumbling windows work.

20. **Hover** over **WaitByStopMinute**, **click** **+**, **select** **Eventhouse**. This time the pane is
    pre-set to **Event processing before ingestion**. Configure:
    - **Destination name**: `BusWaitByStopMinute`
    - **Workspace** `RTI Transit`, **Eventhouse** `TransitEventhouse`, **KQL database** `TransitEventhouse`
    - **Destination table**: **Create new** → `BusWaitByStopMinute`
    - **Input data format**: **JSON**
    - **Leave** **Activate ingestion after adding the data source** checked
    - **Click** **Save**

    *Adapted from: [Add an Eventhouse destination — Event processing before ingestion](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database#event-processing-before-ingestion)*

21. Now the derived stream for Module 05. **Hover** over the **ShapeBusArrivals** node again, **click** **+**,
    **select** **Filter**. **Name** it `VenueStopOnly`, **set** the condition to **`StopCode` equals
    `<VENUE_STOP_CODE>`**, and **click** **Save**.

22. **Hover** over **VenueStopOnly**, **click** **+**, **select** **Stream**. **Name** it `ForumArrivals`,
    **Data format** **JSON**, **click** **Save**.

    > ✅ Expected result: the canvas now has three branches off the stream: direct → `BusArrivalsRaw`;
    > `ShapeBusArrivals → NextBusOnly → WaitByStopMinute → BusWaitByStopMinute`; and
    > `ShapeBusArrivals → VenueStopOnly → ForumArrivals`. Check the **Authoring errors** tab is empty.

    *Adapted from: [Add a derived stream destination](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-derived-stream)*

23. **Click** **Publish**.

    > ✅ Expected result: Live view. All destination nodes show a healthy status within a minute. **Click**
    > **ForumArrivals** → **Data preview**: only your venue stop's events. **Click** the
    > `BusWaitByStopMinute` node → **Data insights**: incoming events climb once a minute.

<!-- facilitator: leave your own Live view on the projector. The three-branch canvas is the picture of the module; point at each branch and say raw / aggregate / curated. -->

> 🎤 Facilitator note: ask the room why we stored *both* the raw table and the per-minute aggregate. The answer
> (raw for replay/forensics and the update policy in Module 03; aggregate for cheap dashboards) sets up Module 03.

### Part D — [metro] A second stream, from Real-Time hub

24. **Click** **Real-Time** in the left navigation, then **+ Connect to data source**. **Search** `Event Hubs`,
    **click** **Connect** on **Azure Event Hubs**.

25. **Click** **New connection** and configure it like step 4–5 but with **Event hub** = your metro hub from the
    seat sheet (`tmb-metro-a` or `tmb-metro-b`, same letter as your bus hub) and **Connection name**
    `tmb-metro-listen`. **Click** **Connect**. **Consumer group**: your same `attendee-NNN`. **Data format**: **JSON**.

    > ✅ Expected result: the same key and consumer group work for both hubs: consumer groups are per event hub,
    > so `attendee-NNN` on the metro hub is a different cursor from `attendee-NNN` on the bus hub.

26. In **Stream details** on the right, **select** workspace **RTI Transit**, **click** the pencil next to
    **Eventstream name** and **type** `MetroArrivalsEventstream`. **Click** **Next**, then **Connect**.

    > ✅ Expected result: Real-Time hub confirms the stream was created and offers **Open eventstream**. This is
    > the point of Part D: the hub is a front door, the result is an ordinary Eventstream item in your workspace.

27. **Click** **Open eventstream**, **click** **Edit**, **add** an **Eventhouse** destination with **Direct
    ingestion** named `MetroArrivalsRaw` into `TransitEventhouse`, **Publish**, **Configure** the destination
    into a **new table** `MetroArrivalsRaw` exactly as in steps 12–14 (types: `StationCode`, `Track`,
    `DirectionId`, `Rank`, `SecondsToArrival` → `long`; `PolledAtUtc`, `PredictedArrivalUtc` → `datetime`;
    `IsStale` → `bool`; the rest `string`).

    > ✅ Expected result: rows like `StationCode 435, LineCode L4, Direction Trinitat Nova, Rank 1,
    > SecondsToArrival 95`. Unlike iBus, TMB's metro feed gives an absolute arrival instant, so the Function
    > also passes `PredictedArrivalUtc` through as-is.

    *Adapted from: [Real-Time hub — connect to data source](https://learn.microsoft.com/fabric/real-time-hub/real-time-hub-overview)*

## Checkpoint

At the end of this lab, your **RTI Transit** workspace should contain:
- `BusArrivalsEventstream` (published, Live view healthy) with source `TMBBusArrivals` and three branches:
  - default stream → Eventhouse **direct ingestion** → table `BusArrivalsRaw` (filling)
  - `ShapeBusArrivals` → `NextBusOnly` → `WaitByStopMinute` → Eventhouse **processed** → table `BusWaitByStopMinute` (one row per stop/line/minute)
  - `ShapeBusArrivals` → `VenueStopOnly` → derived stream **`ForumArrivals`**
- **[metro]** `MetroArrivalsEventstream` → `MetroArrivalsRaw`
- In `TransitEventhouse`: tables `BusArrivalsRaw`, `BusWaitByStopMinute`, `MetroArrivalsRaw` with rows arriving

Real events from the streets outside are now landing in your own database. Continue to
[Module 03: Eventhouse & KQL](../module-03-eventhouse-kql/lab-03-enrich-and-analyze-in-eventhouse.md).

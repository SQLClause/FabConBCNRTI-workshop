# Lab 01: Ingest a Live Stream

**Duration:** 15 minutes
**Prerequisites:** a Fabric workspace on a capacity where you can create items (see the [README](../README.md#prerequisites)).

**Learning objectives**
- Create an **Eventhouse** and know what it auto-creates (KQL database, queryset).
- Create an **Eventstream** with a built-in **sample data** source.
- Add a **Manage fields** operator that stamps every event with its processing time.
- Route the stream into an Eventhouse table with **Event processing before ingestion**.

## Before you begin

- [ ] You can open your workspace and see **+ New item** at the top.
- [ ] Nobody else is using the item names in this lab inside your workspace.

## Steps

### Part A — Eventhouse (3 min)

1. In your workspace, **click** **+ New item**, **search** for and **select** **Eventhouse**, **type**
   `BikeEventhouse`, and **click** **Create**.

   > ✅ Expected result: the Eventhouse opens. Under **KQL databases** there is a database also named
   > `BikeEventhouse`, and your workspace now lists a queryset `BikeEventhouse_queryset` as well. You use both in
   > Lab 02.

   *Adapted from: [Create an eventhouse](https://learn.microsoft.com/fabric/real-time-intelligence/create-eventhouse)*

### Part B — Eventstream with the Bicycles sample (4 min)

2. **Go back** to the workspace, **click** **+ New item**, **select** **Eventstream**, **type**
   `BikeEventstream`, and **click** **Create**.

3. On the eventstream's get-started page, **click** **Use sample data**. In the **Sample data** pane:
   - **Source name**: `BicycleSample`
   - **Sample data**: **Bicycles**
   - **Click** **Add**.

   > ✅ Expected result: the canvas shows `BicycleSample` → `BikeEventstream-stream` → a tile labelled
   > **Transform events or add destination**. **Select** the stream node and open **Data preview** at the bottom:
   > rows with `BikepointID`, `Street`, `Neighbourhood`, `Latitude`, `Longitude`, `No_Bikes` and
   > `No_Empty_Docks` arrive within seconds.

   <details>
   <summary>Troubleshooting — I closed the get-started page</summary>

   In **Edit** mode, **click** **Add source** on the ribbon → **Sample data**, and fill the same pane.
   </details>

   *Adapted from: [Add a sample data source to an eventstream](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-sample-data)*

> 💡 There's no timestamp in the sample. Each event says *what* a station looks like, not *when*. The next part
> fixes that, because every time chart, window and "for 5 minutes" rule later depends on it.

### Part C — Stamp each event with a time (3 min)

4. **Click** the down arrow on the **Transform events or add destination** tile and **select** **Manage fields**.
   **Click** the pencil icon on the new tile. In the **Manage fields** pane:
   - **Operation name**: `AddTimestamp`
   - **Click** **Add all fields** (keeps every sample column)
   - **Click** **+ Add Field** → **Field** dropdown → **Built-in Date Time Function** → **SYSTEM.Timestamp()**;
     **Name** `Timestamp`; **click** **Add**
   - **Click** **Save**.

   > ✅ Expected result: the `AddTimestamp` tile no longer shows a warning, and its **Data preview** (select the
   > tile, bottom pane) shows the sample columns plus `Timestamp`.

   *Adapted from: [Tutorial: Get real-time events](https://learn.microsoft.com/fabric/real-time-intelligence/tutorial-2-get-real-time-events)*

### Part D — Land it in the Eventhouse (4 min)

5. **Point** at the right edge of the `AddTimestamp` tile, **click** the green **+**, then **Destinations** →
   **Eventhouse**. **Click** the pencil on the new **Eventhouse** tile and fill the pane:
   - **Data ingestion mode**: **Event processing before ingestion**
   - **Destination name**: `BikesRawDest`
   - **Workspace**: your workspace
   - **Eventhouse**: `BikeEventhouse`; **KQL Database**: `BikeEventhouse`
   - **Destination table**: **Create new** → `BikesRaw`
   - **Input data format**: **Json**
   - Keep **Activate ingestion after adding the data** checked
   - **Click** **Save**.

6. **Click** **Publish** on the ribbon.

   > ✅ Expected result: the eventstream switches to **Live** view. The canvas reads
   > `BicycleSample → BikeEventstream-stream → AddTimestamp → BikesRawDest`, all nodes green or *Active*.

   <details>
   <summary>Troubleshooting</summary>

   - **Publish is greyed out**: a tile still has a warning icon. Open it and click **Save** again.
   - **Destination shows an error after publish**: the table name already existed with another schema. Edit,
     open `BikesRawDest`, choose **Create new** with `BikesRaw2`, and use that name in Lab 02.
   </details>

### Part E — Prove it landed (1 min)

7. **Open** `BikeEventhouse` → database `BikeEventhouse` → **Tables** → `BikesRaw`. **Wait** up to a minute and
   **refresh**.

   > ✅ Expected result: the table's overview shows a row count that grows on every refresh, and the data preview
   > shows a `Timestamp` column next to the sample columns.

## Checkpoint

At the end of this lab, your workspace contains:
- Eventhouse **`BikeEventhouse`** with KQL database `BikeEventhouse` and table **`BikesRaw`** (rows arriving)
- Queryset `BikeEventhouse_queryset`
- Eventstream **`BikeEventstream`**, published: `BicycleSample` → `AddTimestamp` → `BikesRawDest`

Continue to [Lab 02: Shape, enrich and query in Eventhouse](lab-02-shape-and-query-in-eventhouse.md).

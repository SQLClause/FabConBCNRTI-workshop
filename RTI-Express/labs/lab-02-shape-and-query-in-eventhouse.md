# Lab 02: Shape, Enrich and Query in Eventhouse

**Duration:** 28 minutes
**Prerequisites:** Lab 01 complete; `BikesRaw` is receiving rows. Open
[`artifacts/BikeEventhouse.kql`](../artifacts/BikeEventhouse.kql) in another tab: every query below is in it,
labelled A1, A2, and so on.

**Learning objectives**
- Explore a live table with KQL: `take`, `getschema`, `summarize`, `bin`, `render`, `arg_max`.
- Build a small **dimension table** and enrich streaming rows with **`lookup`**.
- Shape and enrich data **on ingest** with a stored function and an **update policy**, and know why a lookup
  in an update policy needs **queued** rather than **streaming** ingestion.
- Keep "latest state per entity" cheap with a **materialized view**.
- Package a reusable answer as a **stored function** for dashboards and people.

## Before you begin

- [ ] `BikesRaw` row count grows when you refresh it.
- [ ] You know how the editor runs code: it executes **only the block your cursor is in**, where blocks are
      separated by blank lines. Paste one block, run it, then paste the next. Two statements in one block give
      *"A recognition error occurred"*.

## Steps

**Open** `BikeEventhouse_queryset` from your workspace (or **Query with code** from the database). **Confirm**
the database selector at the top says `BikeEventhouse`.

### Part A — Explore the raw stream (6 min)

1. **Run** **A1** and **A2**.

   ```kql
   BikesRaw
   | take 10
   ```

   ```kql
   BikesRaw
   | getschema
   | project ColumnName, ColumnType
   ```

   > ✅ Expected result: eight columns. Note the spelling of `Neighbourhood`. If your table says `Neighborhood`,
   > use that spelling in every query from here on (search-and-replace in the artifact file).

2. **Run** **A3** (volume and freshness).

   ```kql
   BikesRaw
   | extend Timestamp = todatetime(Timestamp)
   | summarize Events = count(), Stations = dcount(BikepointID), Oldest = min(Timestamp), Newest = max(Timestamp)
   | extend LagSeconds = datetime_diff('second', now(), Newest)
   ```

   > ✅ Expected result: `Stations` is the number of docking stations the sample has reported so far, and
   > `LagSeconds` is seconds, not minutes. Remember this number: Part C changes it.

3. **Run** **A5**: the latest reading per station, rolled up by neighbourhood. (**A4**, an event-rate chart, is
   in the artifact file if you have a spare minute.)

   ```kql
   BikesRaw
   | extend Timestamp = todatetime(Timestamp), No_Bikes = tolong(No_Bikes)
   | summarize arg_max(Timestamp, *) by BikepointID
   | summarize Stations = count(), EmptyStations = countif(No_Bikes == 0), Bikes = sum(No_Bikes) by Neighbourhood
   | top 10 by EmptyStations desc
   ```

   > 💡 `arg_max(Timestamp, *) by BikepointID` keeps the newest row per station. It is the most useful pattern in
   > streaming KQL, and Part D turns it into something you never have to recompute.

### Part B — Reference data: which crew covers which neighbourhood (4 min)

The stream tells you a station is empty; it doesn't tell you **who** should go and fix it. Ops keeps that in a
reference table: every neighbourhood is assigned to one of six rebalancing crews. Reference data like this
changes rarely and is small, which makes it a **dimension table**.

4. **Run** **B1**. It takes the neighbourhood names from your own stream, spreads them over the six crews with a
   stable `hash()`, and looks up each crew's details from an inline `datatable`. That's your first `lookup`.

   ```kql
   .set-or-append NeighbourhoodCrew <|
       BikesRaw
       | summarize by Neighbourhood = tostring(Neighbourhood)
       | where isnotempty(Neighbourhood)
       | extend CrewId = strcat("C0", tostring(hash(Neighbourhood, 6) + 1))
       | lookup kind = leftouter (
           datatable(CrewId: string, CrewName: string, Shift: string, HomeDepot: string) [
               "C01", "North Loop", "Morning", "Kings Cross",
               "C02", "River Run", "Morning", "Southwark",
               "C03", "City Sweep", "Morning", "Liverpool Street",
               "C04", "West Wheels", "Afternoon", "Paddington",
               "C05", "East Docks", "Afternoon", "Canary Wharf",
               "C06", "Night Owls", "Night", "Waterloo"
           ]) on CrewId
   ```

5. **Run** **B2**.

   ```kql
   NeighbourhoodCrew
   | summarize Neighbourhoods = count() by CrewId, CrewName, HomeDepot
   | order by CrewId asc
   ```

   > ✅ Expected result: six rows, one per crew, each covering a share of the neighbourhoods. Same crews as the
   > CSV you'll load in Lab 05.

   > 💡 `lookup` is a `join` tuned for this exact shape: a big **fact** side on the left, a small **dimension**
   > on the right that fits in memory. `kind = leftouter` keeps fact rows that find no match.

   *Adapted from: [lookup operator](https://learn.microsoft.com/kusto/query/lookup-operator?view=microsoft-fabric)*

### Part C — Shape and enrich on ingest with an update policy (10 min)

You'll now put that lookup **in the ingest flow**: every batch arriving in `BikesRaw` is typed, classified and
tagged with its crew before it lands in `BikesClean`. There's one rule to respect first.

6. **Run** **C1**, then **C2** (two blocks).

   ```kql
   .alter-merge table BikesRaw policy streamingingestion '{"IsEnabled": false}'
   ```

   ```kql
   .alter table BikesRaw policy ingestionbatching '{"MaximumBatchingTimeSpan": "00:00:10", "MaximumNumberOfItems": 1000, "MaximumRawDataSizeMB": 1024}'
   ```

   > 💡 **Why:** Eventhouse refuses an update policy that reads *another* table (our `lookup` on
   > `NeighbourhoodCrew`) while the source table uses **streaming ingestion**. C1 moves `BikesRaw` to **queued
   > ingestion**; C2 caps the batching wait at 10 seconds so the data stays fresh. Without C1 you get *"Referencing
   > additional tables from update policy is not allowed when streaming ingestion is enabled on the source
   > table"* at C6. The cost is a few seconds of latency: compare A3's `LagSeconds` before and after.

7. **Run** **C3** to create the transformation as a stored function.

   ```kql
   .create-or-alter function with (folder = "Silver", docstring = "Typed, enriched bike station readings with the responsible crew") CleanBikes() {
       BikesRaw
       | extend No_Bikes = tolong(No_Bikes), No_Empty_Docks = tolong(No_Empty_Docks),
                Latitude = toreal(Latitude), Longitude = toreal(Longitude), Timestamp = todatetime(Timestamp)
       | extend Capacity = No_Bikes + No_Empty_Docks
       | extend OccupancyPct = iff(Capacity > 0, round(100.0 * No_Bikes / Capacity, 1), real(null))
       | extend Status = case(No_Bikes == 0, "Empty",
                              No_Empty_Docks == 0, "Full",
                              OccupancyPct < 20.0, "Low",
                              "OK")
       | project Timestamp, BikepointID = tostring(BikepointID), Street = tostring(Street),
                 Neighbourhood = tostring(Neighbourhood), Latitude, Longitude,
                 No_Bikes, No_Empty_Docks, Capacity, OccupancyPct, Status
       | lookup kind = leftouter (NeighbourhoodCrew | project Neighbourhood, CrewId, CrewName) on Neighbourhood
       | extend CrewId = coalesce(CrewId, "-"), CrewName = coalesce(CrewName, "Unassigned")
   }
   ```

8. **Run** **C4** to test the function before anything depends on it.

   ```kql
   CleanBikes()
   | summarize Rows = count() by CrewName
   | order by Rows desc
   ```

   > ✅ Expected result: six crews, and no `Unassigned` row (or a tiny one, see the note after step 10).

9. **Run** **C5** (create `BikesClean` and backfill), then **C6** (the update policy).

   ```kql
   .set-or-append BikesClean <| CleanBikes()
   ```

   ```kql
   .alter table BikesClean policy update @'[{"IsEnabled": true, "Source": "BikesRaw", "Query": "CleanBikes()", "IsTransactional": false, "PropagateIngestionProperties": false}]'
   ```

   > ✅ Expected result: C6 returns a row showing the policy JSON. The few seconds between C5 and C6 are a small
   > gap in `BikesClean`; in production you'd create the policy first and backfill with a time filter.

10. **Run** **C7** twice, about a minute apart.

    ```kql
    BikesClean
    | summarize Rows = count(), Newest = max(Timestamp) by Status
    ```

    > ✅ Expected result: four statuses (`OK`, `Low`, `Empty`, `Full`), with `Rows` growing and `Newest` moving
    > forward between runs.

> 💡 **Ingest-time lookup is a snapshot.** Each row keeps the crew that was assigned *when it was ingested*.
> Reassign a neighbourhood tomorrow and old rows still show the old crew, which is right for history ("who was
> responsible then?") and wrong for "who is responsible now?". A neighbourhood that first appears *after* B1
> lands as `Unassigned` until someone adds it to `NeighbourhoodCrew`. For "now" questions, do the lookup at
> query time instead; the dimension is small, so it's cheap.

<details>
<summary>Troubleshooting</summary>

- **C6 fails with "Referencing additional tables ... streaming ingestion"**: C1 didn't run, or ran against a
  different table name. Run C1 again, then C6.
- **C3 fails with "Failed to resolve ... Neighbourhood"**: your column is spelled `Neighborhood`. Fix the spelling
  in B1 and C3, and run both again.
- **C4 shows only `Unassigned`**: the lookup key doesn't match. Run `NeighbourhoodCrew | take 5` and compare with
  `BikesRaw | take 5`: look for different spelling or stray spaces.
- **C7's `Newest` doesn't move**: check C6 ran (`.show table BikesClean policy update`), and that the eventstream
  is still **Active** (a throttled capacity can pause it; open it and resume).
</details>

*Adapted from: [Update policy overview](https://learn.microsoft.com/kusto/management/update-policy?view=microsoft-fabric)*

### Part D — Latest state per station with a materialized view (4 min)

11. **Run** **D1**, then **D2** and **D3**.

    ```kql
    .create materialized-view with (backfill = true) StationLatest on table BikesClean {
        BikesClean
        | summarize arg_max(Timestamp, *) by BikepointID
    }
    ```

    ```kql
    StationLatest
    | count
    ```

    ```kql
    .show materialized-view StationLatest
    | project Name, IsHealthy, IsEnabled, MaterializedTo
    ```

    > ✅ Expected result: the count roughly equals A3's `Stations`; `IsHealthy` is `true`; `MaterializedTo` is a
    > few seconds ago. Because `BikesClean` already carries the crew, so does every row of the view.

    *Adapted from: [Materialized views](https://learn.microsoft.com/kusto/management/materialized-views/materialized-view-overview?view=microsoft-fabric)*

### Part E — A reusable "right now" function (4 min)

12. **Run** **E1**, then **E2**.

    ```kql
    .create-or-alter function with (folder = "Gold", docstring = "Current station state rolled up per neighbourhood and crew") NeighbourhoodNow() {
        StationLatest
        | summarize Stations = count(),
                    Empty = countif(Status == "Empty"), Low = countif(Status == "Low"), Full = countif(Status == "Full"),
                    Bikes = sum(No_Bikes), Docks = sum(Capacity)
                    by Neighbourhood, CrewName
        | extend PctEmpty = round(100.0 * Empty / Stations, 1)
        | order by Empty desc, PctEmpty desc
    }
    ```

    ```kql
    NeighbourhoodNow()
    | take 10
    ```

13. **Pick your neighbourhood** for Lab 04: choose one from E2's top ten that has a few `Empty` and several `Low`
    stations. **Copy** its name exactly, including capitals and spaces, and keep it somewhere handy. Note its
    crew too.

    > ✅ Expected result: you have one neighbourhood name (and its crew) written down. Lab 04's alerts only watch
    > that neighbourhood, so your inbox gets a handful of messages, not hundreds.

### *(stretch)*

14. **Run** **S1** (bikes needed per crew right now: which van leaves first?) and **S2** (how long has each empty
    station been empty?) from the artifact file.

## Checkpoint

At the end of this lab, database `BikeEventhouse` contains:
- Dimension table **`NeighbourhoodCrew`** (neighbourhood → crew)
- `BikesRaw` on **queued ingestion** with 10-second batching
- Function **`CleanBikes()`** and table **`BikesClean`** (with `CrewId`, `CrewName`), filled continuously by an
  update policy on `BikesRaw`
- Materialized view **`StationLatest`**, healthy, one row per station
- Function **`NeighbourhoodNow()`**
- And you have **one neighbourhood name** written down for Lab 04.

Continue to [Lab 03: Real-Time Dashboard](lab-03-real-time-dashboard.md).

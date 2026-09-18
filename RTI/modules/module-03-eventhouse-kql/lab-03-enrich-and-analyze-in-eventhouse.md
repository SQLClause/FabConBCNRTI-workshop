# Lab 03: Enrich and Analyse in the Eventhouse

**Duration:** 35 minutes
**Prerequisites:** Module 02 complete. `TransitEventhouse`'s default database contains `BusArrivalsRaw` and
`BusWaitByStopMinute` with rows arriving (and `MetroArrivalsRaw` if you did Part D). You have this repo's
[`artifacts/SampleData/`](../../artifacts/SampleData/) CSVs and
[`artifacts/Eventhouse/TransitEventhouse.kql`](../../artifacts/Eventhouse/TransitEventhouse.kql) open in a browser tab
to copy from.

**Learning objectives**
- Query a raw event table with KQL: `top`, `summarize … by bin()`, `render`, time-zone conversion.
- Load reference CSVs into KQL tables through the portal and fix an inferred type.
- Author an **update policy** (target table + function + policy) that enriches events at ingestion time.
- Author a **materialized view** that keeps the newest prediction per stop and line.
- Save analysis queries in a **KQL Queryset** for the dashboard module.
- Stretch: join bus and metro at the venue; turn on **OneLake availability**.

## Before you begin

Confirm your environment matches this state before starting:
- [ ] `BusArrivalsRaw | count` returns a growing number (run it twice, a minute apart).
- [ ] `BusWaitByStopMinute` exists (it may still have few rows; that's fine).
- [ ] You have `stops.csv` and `lines.csv` downloaded locally from `artifacts/SampleData/` (and
      `metro_stations.csv` if you did the metro part).

## Steps

### Part A — Explore the raw stream

1. **Open** `TransitEventhouse`, **click** the **TransitEventhouse** database, then **click** **Query with code**
   (or **New KQL Queryset** on the ribbon). **Name** the queryset `TransitQueries` when prompted.

   ![Step 1](../../assets/screenshots/lab-03/step-01.png)

   > ✅ Expected result: a query editor opens attached to the `TransitEventhouse` database, tables listed on the left.

2. **Paste** and **run** query **A1** from the KQL script (latest 20 predictions), then **A2** (events per minute,
   rendered as a time chart).

   > ✅ Expected result: A1 shows rows from the last minute; A2 draws a line hovering around a steady number of
   > events per minute, with a visible step every 30 seconds where the venue stops poll faster.

3. **Run** **A3** (predictions by line) and **A4** (local time and predicted arrival instant).

   > ✅ Expected result: A3 lists line codes like `H16`, `7`, `V15` with stop counts, and nothing else about them:
   > no names, no origins. A4 shows `PolledAtLocal` two hours ahead of UTC and a `PredictedArrivalUtc` column
   > computed from `SecondsToArrival`.

<!-- facilitator: A3 is the "codes only" cliffhanger. Ask "which of these is the bus to the airport?" Nobody can tell. Part B fixes that. -->

### Part B — Load the reference data

4. **Go back** to the **TransitEventhouse** database page (breadcrumb), **click** **Get data** on the ribbon, and
   **select** **Local file**.

5. **Click** **+ New table**, **type** `StopsDim`, then **drag** `stops.csv` into the window (or **Browse for
   files**). **Click** **Next**.

   ![Step 5](../../assets/screenshots/lab-03/step-02.png)

6. On **Inspect**, **confirm** **Format** is **CSV** and **First row is column header** is **on**. **Click**
   **Edit columns** and **check** the types: `StopCode` must be **long**, `Lat` and `Lon` **real**, `IsPrimary`
   **bool**, everything else **string**. Fix any that differ, **Apply**, then **Finish**. **Close** when the
   three steps are green.

   <details>
   <summary>Troubleshooting — <code>StopCode</code> was inferred as string and I already finished</summary>

   Run **B3** from the script (it rebuilds the table with `tolong(StopCode)`). A string/long mismatch makes
   every `lookup` in Part C return nulls, so don't skip this check.
   </details>

   *Adapted from: [Get data from file](https://learn.microsoft.com/fabric/real-time-intelligence/get-data-local-file)*

7. **Repeat** steps 4–6 for `lines.csv` → new table `LinesDim` (all columns string). **[metro]** Repeat for
   `metro_stations.csv` → `MetroStationsDim` (`StationCode` long, `Lat`/`Lon` real, rest string).

8. **Back in `TransitQueries`**, **run** **B1** and **B2**.

   > ✅ Expected result: `StopsDim` shows ~16 rows with `StopName`, `Zone`, `Lat`, `Lon`; `LinesDim` shows
   > the lines with `LineName`, `LineOrigin`, `LineDestination`. B2 reports `StopCode` as `long` in **both**
   > tables.

9. **Run** **B4**.

   > ✅ Expected result: the same predictions as A4, now with `StopName`, `Zone`, `LineName`, `Lat`, `Lon`.
   > Find your venue stop by name. This query is what we're about to automate.

### Part C — Author the update policy

10. **Paste** and **run** **C1** (create `BusArrivalsEnriched`).

    > ✅ Expected result: the table appears under **Tables** in the left pane (refresh it if needed). Empty.

11. **Paste** and **run** **C2** (create the `EnrichBusArrivals()` function).

    > ✅ Expected result: `EnrichBusArrivals` appears under **Functions** (folder `Enrichment`). **Run**
    > `EnrichBusArrivals() | take 5` to prove it behaves like a table.

12. **Paste** and **run** **C3** (attach the update policy), then **immediately** **C4** (backfill).

    > ✅ Expected result: C3 returns one row describing the policy. C4 returns an ingestion summary. From this
    > moment, every batch that lands in `BusArrivalsRaw` is enriched into `BusArrivalsEnriched` by the engine,
    > with no eventstream change and no schedule. (A handful of rows ingested in the seconds between C3 and C4
    > may appear twice; harmless for everything downstream.)

    *Adapted from: [Update policy](https://learn.microsoft.com/kusto/management/update-policy)*

13. **Wait** about a minute, then **run** **C5** twice, 30 seconds apart.

    ![Step 13](../../assets/screenshots/lab-03/step-03.png)

    > ✅ Expected result: `BusArrivalsEnriched` has fresh rows each time, each carrying `StopName`, `Zone`,
    > `LineName` and `PredictedArrivalUtc` next to the raw values. You didn't write a pipeline; the database is
    > doing it per ingestion batch.

    <details>
    <summary>Troubleshooting — <code>BusArrivalsEnriched</code> stays empty</summary>

    Run **C6**. If `.show ingestion failures` lists rows for this table, the message tells you why; the common
    ones are a `StopCode` type mismatch (Part B step 6) or a function/table schema mismatch (re-run C1 and C2,
    which are idempotent). If there are no failures, wait one more minute; ingestion batches every ~30–60 s.
    </details>

### Part D — Author the materialized view

14. **Paste** and **run** the `.create-or-alter materialized-view` statement in **Part D**.

    > ✅ Expected result: `BusNextArrivalLatest` appears under **Materialized views**. With `backfill = true` it
    > is populated from existing rows within a minute or so.

    *Adapted from: [Create materialized view](https://learn.microsoft.com/kusto/management/materialized-views/materialized-view-create)*

15. **Run** **D1**, then **D2**.

    > ✅ Expected result: D1 shows exactly one row per stop/line combination (no duplicates, unlike the raw
    > table), ordered by wait. D2 shows the venue's next buses with an `AgeSeconds` column under ~60. That's
    > "what's the wait right now?" as a table you can point a dashboard or an alert at.

16. **Run** **D3**.

    > ✅ Expected result: `IsHealthy = true`, `Status = Active`, and a recent `LastRun`.

> 🎤 Facilitator note: stop here and connect the dots. Raw → enriched (policy) → latest (view). This exact chain
> is what Brian's provisioning script builds for freezers this afternoon; attendees will see
> `FreezerTelemetryRaw` and `FreezerTelemetryEnriched` and know what they're looking at.

### Part E — Save the analysis queries

17. **Paste** each of **E1**–**E5** into its own tab in `TransitQueries` (the **+** next to the tab strip) and
    **run** them. **Rename** the tabs (right-click → **Rename**): `Avg wait by line`, `Wait from aggregate`,
    `Bunching`, `Longest wait map`, `Freshness`.

    > ✅ Expected result:
    > - **E1** renders a time chart, one line per bus line.
    > - **E2** draws nearly the same chart from `BusWaitByStopMinute` with far fewer rows. If its column names
    >   differ from the script's guesses, run `BusWaitByStopMinute | getschema` and adjust; the eventstream
    >   Group-by names outputs `AVG_<field>` style.
    > - **E3** lists stop/line pairs where the next two buses are ≤ 2 minutes apart (bunching). At quiet times
    >   it may be empty; that's real.
    > - **E4** has `Lat`/`Lon` for every row: the map tile's input.
    > - **E5** shows every stop with `SilentForMin` near 0 or 1.

18. **Click** **Save** on the queryset.

    *Adapted from: [KQL Queryset](https://learn.microsoft.com/fabric/real-time-intelligence/kusto-query-set)*

### Part F — Stretch: the interchange question and OneLake availability

19. **[metro]** **Run** **F1** then **F2**.

    > ✅ Expected result: F2 returns one short table for the venue: bus lines and metro directions mixed,
    > sorted by wait. Skip both if you didn't do Lab 02 Part D.

20. **Go back** to the **TransitEventhouse** database page, **click** the **OneLake availability** toggle in
    the database details (or **…** on `BusArrivalsEnriched` → **Data policies** → **OneLake availability**) and
    **turn it on**. **Click** **Done**.

    > ✅ Expected result: within a few minutes the table's OneLake folder path is shown, and the data is
    > readable as Delta from `TransitLakehouse` via a shortcut, from a notebook, or from Direct Lake. Nothing
    > was copied by you; the Eventhouse writes Parquet/Delta alongside its own storage.

    *Adapted from: [Eventhouse OneLake availability](https://learn.microsoft.com/fabric/real-time-intelligence/event-house-onelake-availability)*

<!-- facilitator: if the room is behind, skip Part F entirely; nothing later depends on it. If ahead, add a OneLake shortcut in TransitLakehouse pointing at the enriched table and open it in the SQL endpoint -- it's the "one copy, many engines" moment. -->

## Checkpoint

At the end of this lab, the `TransitEventhouse` database should contain:
- Tables: `BusArrivalsRaw`, `BusWaitByStopMinute`, `StopsDim`, `LinesDim`, `BusArrivalsEnriched` (filling
  automatically via the update policy), **[metro]** `MetroArrivalsRaw`, `MetroStationsDim`
- Function: `EnrichBusArrivals()`
- Materialized view: `BusNextArrivalLatest`, healthy
- Queryset `TransitQueries` with five saved analysis tabs (E1–E5)

Raw codes have become named stops on a map with a current wait. Take the break, then continue to
[Module 04: Real-Time Dashboard](../module-04-real-time-dashboard/lab-04-build-transit-ops-dashboard.md).

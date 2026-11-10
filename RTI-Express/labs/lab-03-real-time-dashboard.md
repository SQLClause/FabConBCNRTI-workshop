# Lab 03: Real-Time Dashboard

**Duration:** 20 minutes
**Prerequisites:** Lab 02 complete: `BikesClean` is filling and `StationLatest` is healthy. Tile queries are in
[`artifacts/dashboard-tiles.kql`](../artifacts/dashboard-tiles.kql).

**Learning objectives**
- Create a Real-Time Dashboard and connect it to a KQL database.
- Add a **query-driven parameter** and use it in every tile.
- Build a **map**, a **time chart** and a **table** tile.
- Turn on **live refresh** and watch tiles update without touching them.

## Before you begin

- [ ] `StationLatest | where isnotnull(Latitude) | count` returns roughly the same number as `StationLatest | count`.

## Steps

### Part A — Dashboard and data source (3 min)

1. In your workspace, **click** **+ New item**, **select** **Real-Time Dashboard**, **type** `BikeOpsDashboard`,
   **click** **Create**.

2. **Click** **+ Add data source** → **KQL Database** (or **Eventhouse / KQL Database**). In the **OneLake
   catalog** window **select** `BikeEventhouse`, then **Connect**.

   > ✅ Expected result: `BikeEventhouse` is listed under the dashboard's data sources, and the toolbar's tile and
   > parameter buttons are enabled.

   *Adapted from: [Create a Real-Time Dashboard](https://learn.microsoft.com/fabric/real-time-intelligence/dashboard-real-time-create)*

### Part B — Neighbourhood parameter (4 min)

3. **Click** **Manage** → **Parameters** → **+ New parameter** (or **+ Add parameter** on the toolbar). Fill in:
   - **Label**: `Neighbourhood`
   - **Parameter type**: **Multiple selection**
   - **Variable name**: `_hood`
   - **Data type**: **String**
   - **Source**: **Query** → **Edit query**, paste the query below, **Run**, **Done**
   - **Value**: `Neighbourhood`; **Display name**: `Neighbourhood`
   - **Default value**: **Select all** (turn on **Add a Select all value** if it isn't offered)
   - **Click** **Done**.

   ```kql
   StationLatest
   | distinct Neighbourhood
   | order by Neighbourhood asc
   ```

   > ✅ Expected result: a **Neighbourhood** dropdown appears at the top of the dashboard. Every tile you build
   > next filters on it with `isempty(_hood) or Neighbourhood in (_hood)`: *Select all* sends an empty list, which
   > means "no filter".

   *Adapted from: [Use parameters in Real-Time Dashboards](https://learn.microsoft.com/fabric/real-time-intelligence/dashboard-parameters)*

### Part C — Map: every station, sized by missing bikes (5 min)

4. **Click** **New tile** (or **+ Add tile**). **Paste** **T1** and **click** **Run**.

   ```kql
   StationLatest
   | where isnotnull(Latitude) and isnotnull(Longitude)
   | where isempty(_hood) or Neighbourhood in (_hood)
   | project Street, Neighbourhood, CrewName, Status, No_Bikes, Capacity, MissingBikes = Capacity - No_Bikes, Latitude, Longitude
   ```

5. On the **Visual setup** tab, **set** **Visual type** to **Map**. Under **Data**, **set** **Define location by**
   to **Latitude and longitude**, then **Latitude column** `Latitude` and **Longitude column** `Longitude`.
   **Label column** `Street` if offered. Under **Size**, **select** **Show** and **Size column** `MissingBikes`.
   Under **General**, **Tile name** `Stations: missing bikes`. **Click** **Apply changes** (or **Done**).

   > ✅ Expected result: a map of central London covered in dots; the biggest dots are stations missing the most
   > bikes. Hover a dot to see street, crew, status and counts.

   *Adapted from: [Customize Real-Time Dashboard visuals](https://learn.microsoft.com/fabric/real-time-intelligence/dashboard-visuals-customize)*

### Part D — Time chart: empty and full stations per minute (4 min)

6. **New tile**, **paste** **T2**, **Run**.

   ```kql
   BikesClean
   | where Timestamp > ago(1h)
   | where isempty(_hood) or Neighbourhood in (_hood)
   | summarize Empty = dcountif(BikepointID, Status == "Empty"), Full = dcountif(BikepointID, Status == "Full") by bin(Timestamp, 1m)
   ```

   On the **Visual setup** tab, **set** **Visual type** to **Time chart**. Under **Data**, in the order the pane
   shows them: **Y columns** `Empty` and `Full`, **X column** `Timestamp`. **Tile name** `Empty and full stations
   per minute`. **Apply changes**.

   > ✅ Expected result: two lines over the last hour (or since Lab 01, whichever is shorter). **Pick** a single
   > neighbourhood in the dropdown: both the map and this chart re-query for just that area.

### Part E — Refill list per crew (2 min)

7. **New tile**, **paste** **T3**, **Run**, **Visual type** **Table**, **Tile name** `Refill list`, **Apply
   changes**. The `Crew` column comes from the lookup you put in the ingest flow in Lab 02: the dashboard does
   no join at all.

   ```kql
   StationLatest
   | where Status in ("Empty", "Low")
   | where isempty(_hood) or Neighbourhood in (_hood)
   | project Crew = CrewName, Street, Neighbourhood, Status, Bikes = No_Bikes, Capacity, OccupancyPct, AsOf = Timestamp
   | top 25 by OccupancyPct asc
   | order by Crew asc, OccupancyPct asc
   ```

### Part F — Live refresh and save (2 min)

8. **Click** **Manage** → **Refresh settings**. **Select** **Live refresh (Recommended)** if it isn't already
   selected (it is the default for new dashboards). Under **Settings**, **set** **Refresh rate limit** to
   `30 seconds`. **Close** the pane.

9. **Click** **Save**, then **switch** from **Editing** to **Viewing**. **Arrange** the tiles by dragging if you
   like: map large on the left, time chart and table on the right.

   > ✅ Expected result: within a minute the **Refill list**'s `AsOf` values move forward and rows change order
   > without you clicking anything. That's the stream, through the update policy and the materialized view, onto
   > the screen.

   *Adapted from: [Live refresh in Real-Time Dashboards](https://learn.microsoft.com/fabric/real-time-intelligence/dashboard-live-refresh)*

<details>
<summary>Troubleshooting</summary>

- **"Failed to resolve scalar expression named '_hood'"**: the parameter's **Variable name** isn't exactly `_hood`.
- **Map shows nothing**: **Define location by** is still **Infer**; set it to **Latitude and longitude**.
- **Tiles show "No results" after picking a neighbourhood**: the parameter's **Value** column isn't
  `Neighbourhood`, so the dropdown sends display text that doesn't match.
</details>

## Checkpoint

At the end of this lab, your workspace contains **`BikeOpsDashboard`** with:
- Data source `BikeEventhouse` and parameter **Neighbourhood** (`_hood`, multiple selection)
- Tiles `Stations: missing bikes` (map), `Empty and full stations per minute` (time chart), `Refill list` (table)
- Live refresh on

Continue to [Lab 04: Activator rules](lab-04-activator-rules.md).

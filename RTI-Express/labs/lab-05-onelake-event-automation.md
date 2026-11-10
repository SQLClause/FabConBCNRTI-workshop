# Lab 05: Event-Driven Automation with OneLake Events

**Duration:** 15 minutes
**Prerequisites:** none from the other labs. You need
[`artifacts/LoadLanding.py`](../artifacts/LoadLanding.py) open to copy from and
[`artifacts/rebalancing_crews.csv`](../artifacts/rebalancing_crews.csv) downloaded.

**Learning objectives**
- See that "events" are not only telemetry: Fabric itself emits events when files land in OneLake.
- Subscribe to **OneLake events** from Real-Time hub with a path filter.
- Make Activator **run a notebook** when a file lands, and watch the run start by itself.

## Before you begin

- [ ] Real-Time hub → **Fabric events** lists **OneLake events**. If it doesn't, Fabric events are disabled in this
      tenant; read through Parts B–C as a demo.

## Steps

### Part A — The notebook that will be triggered (6 min)

1. In your workspace, **click** **+ New item** → **Lakehouse**, **name** it `BikeLakehouse`, **Create**.

2. In the Lakehouse explorer, **hover** over **Files**, **click** **…** → **New subfolder**, **name** it `landing`.

3. **Go back** to the workspace, **click** **+ New item** → **Notebook**, and **rename** it (click the title) to
   `LoadLanding`.

4. In the notebook's **Explorer** pane, **click** **Add data items** → **Existing data sources**, **select**
   `BikeLakehouse`, **Connect**.

5. **Replace** the first cell's content with the whole of `LoadLanding.py`, and **click** **Run all**.

   > ✅ Expected result: after a Spark start-up of 1–3 minutes the cell prints
   > `No CSV files in Files/landing yet; nothing to load.` and finishes green. That proves the notebook runs; the
   > event will provide the file.

   <details>
   <summary>Troubleshooting</summary>

   `Could not list Files/landing`: the lakehouse isn't attached (step 4) or the folder isn't named exactly
   `landing` (step 2). `Session timed out`: run again; a cold capacity sometimes times out once.
   </details>

### Part B — The rule: file lands → run the notebook (5 min)

6. **Click** **Real-Time** in the left navigation, then **Fabric events**. **Hover** over **OneLake events** and
   **click** **Set alert**.

7. In the **Add rule** pane, **Details** → **Rule name**: `Landing file arrived`.

8. **Monitor** → **Source** → **Select source events**. The **Connect data source** wizard opens:
   - **Select event type(s)**: **select only** `Microsoft.Fabric.OneLake.FileCreated`
   - **Select data source for events**: **Add a OneLake source** → **My data** → **select** `BikeLakehouse` →
     **Next** → **select all** (or the **Files** entry) → **Add**
   - **Set filters** → **+ Filter**: **Field** `subject`, **Operator** **String contains**, **Value**: **type**
     `Files/landing/` and **click** **Add new value**
   - **Next** → **Review + connect** → **Save**

   > ✅ Expected result: back in **Add rule**, **Monitor** reads **Source: OneLake events**, with one event type
   > and one filter.

   *Adapted from: [Set alerts on OneLake events in Real-Time hub](https://learn.microsoft.com/fabric/real-time-hub/set-alerts-fabric-onelake-events)*

9. **Condition** → **Check**: **On each event**.

   <details>
   <summary>If the Check dropdown only offers "On each event when"</summary>

   **Grouping field**: leave empty; **When**: `subject`; **Condition**: **Contains**; **Value**: `Files/landing/`.
   It repeats the filter from step 8, which is harmless.
   </details>

10. **Action** → **Select action** (it defaults to **Message to individuals**; change it) → under **Run Fabric
    activities** **select** **Notebook** → **Select Fabric item to run** → `LoadLanding`.

11. **Save location** → **Workspace**: your workspace; **Item**: open the dropdown (it defaults to **My
    activator**) → **Create a new item** → `BikeAutomation`. **Click** **Create**, then **Open** on **Alert
    created**. **Confirm** the rule shows **Running**; if not, **click** **Start**.

    *Adapted from: [Trigger Fabric items](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-trigger-fabric-items)*

### Part C — Fire it (4 min)

12. **Open** `BikeLakehouse` → **Files** → **landing**. **Click** **Upload** → **Upload files**, **select**
    `rebalancing_crews.csv`, **Upload**.

13. **Click** **Monitor** in the left navigation. **Wait** 30–90 seconds and **refresh**.

    > ✅ Expected result: a run of **LoadLanding** appears with status **In progress**, started without anyone
    > clicking Run. Give it 1–3 minutes for Spark to start.

14. When the run shows **Succeeded**, **open** `BikeLakehouse` → **Tables** → **refresh**.

    > ✅ Expected result: a table `rebalancing_crews` with six rows: the same six crews Lab 02's
    > `NeighbourhoodCrew` assigns to neighbourhoods. The file landing *was* the trigger: no schedule, no polling.

<details>
<summary>Troubleshooting — no run appeared</summary>

1. The rule isn't running (step 11).
2. Filter typo: `subject` looks like `/<workspaceId>/<lakehouseId>/Files/landing/rebalancing_crews.csv`, and the
   filter is case-sensitive.
3. The file went to `Files` instead of `Files/landing`.
4. Give it two full minutes, then upload the file again (a replace also raises `FileCreated`).
</details>

> 💡 Swap the action target and nothing else changes: a pipeline, a Dataflow, a Spark job or a User Data
> Function. Swap the event source (Azure Blob Storage, a Fabric job finishing, a workspace item being created)
> and the rule pattern stays the same.

## Checkpoint

At the end of this lab, your workspace contains:
- Lakehouse **`BikeLakehouse`** with `Files/landing/rebalancing_crews.csv` and table `rebalancing_crews`
- Notebook **`LoadLanding`**, attached to `BikeLakehouse`
- Activator item **`BikeAutomation`** with rule `Landing file arrived` (OneLake `FileCreated`, filter
  `Files/landing/`, action **Run notebook**), **Running**, with one activation

You've built the whole loop: ingest, shape, see, act, automate. Before you leave, [clean up](../README.md#clean-up-after-the-session).

# RTI Express: Real-Time Intelligence in 100 minutes

A self-contained, hands-on lab set for **Microsoft Fabric Real-Time Intelligence (RTI)** only: no Fabric IQ, no
ontologies, no presenter-hosted infrastructure. Every attendee generates their own live stream from Eventstream's
built-in **Bicycles** sample, so the labs run the same in any tenant, on any day, with no Azure Function, Event
Hubs namespace or shared key.

The full-day workshop material stays in [`../RTI/`](../RTI/README.md). This folder is the short version for
participants who want the whole RTI loop (ingest → store and shape → visualize → act → automate) in one sitting.

## Scenario: bike-share rebalancing control room

A city bike-share scheme streams the state of every docking station: bikes available, empty docks, street,
neighbourhood and coordinates. The operations team needs to see which stations are running empty, get told when a
station in *their* neighbourhood has been empty for a while, and have new reference files (crew rosters) loaded
automatically the moment someone drops them in the lake.

## Agenda

| Lab | Minutes | You build |
|---|---|---|
| [01 Ingest a live stream](labs/lab-01-ingest-a-live-stream.md) | 15 | Eventhouse, Eventstream with the Bicycles sample, a Manage fields operator, Eventhouse destination `BikesRaw` |
| [02 Shape, enrich and query in Eventhouse](labs/lab-02-shape-and-query-in-eventhouse.md) | 28 | KQL exploration, dimension table `NeighbourhoodCrew`, update policy with a `lookup` into `BikesClean`, materialized view `StationLatest`, function `NeighbourhoodNow()` |
| [03 Real-Time Dashboard](labs/lab-03-real-time-dashboard.md) | 20 | `BikeOpsDashboard` with a parameter, map, time chart, refill table per crew, live refresh |
| [04 Activator rules](labs/lab-04-activator-rules.md) | 20 | `BikeAlerts`: object per station, a change rule and a sustained 5-minute rule, filtered to your neighbourhood |
| [05 Event-driven automation](labs/lab-05-onelake-event-automation.md) | 15 | OneLake `FileCreated` event → Activator → runs notebook `LoadLanding` |
| **Total** | **98** | 2 minutes of slack inside the 100-minute limit |

Each lab ends with a **Checkpoint**. Labs 01 → 02 → 03 are strictly sequential. Lab 04 needs Labs 01–02.
Lab 05 is independent of the others and can be run first by anyone whose stream is slow to start.

Stretch steps are marked *(stretch)* and are not counted in the timings.

## Prerequisites

- A Fabric workspace on a capacity (F SKU, P SKU or Fabric trial) where you can create items. One workspace per
  attendee; the labs never share items between people.
- Tenant settings allow Eventstream, Eventhouse, Real-Time Dashboard and Activator (default on in most tenants).
- An email address (or Teams) that Activator can send to: your own work account.
- A modern browser. Nothing to install.
- [`artifacts/`](artifacts/) downloaded or open in another tab: you paste from `BikeEventhouse.kql`,
  `dashboard-tiles.kql`, `LoadLanding.py`, and upload `rebalancing_crews.csv`.

## Fixed names

Used consistently in every lab and artifact. If you rename something, rename it everywhere.

| Item | Name |
|---|---|
| Eventhouse and its KQL database | `BikeEventhouse` |
| Queryset (auto-created with the Eventhouse) | `BikeEventhouse_queryset` |
| Eventstream | `BikeEventstream` (source `BicycleSample`, operator `AddTimestamp`, destinations `BikesRawDest`, `BikeAlertsDest`) |
| Tables | `BikesRaw` (as ingested; queued ingestion, 10 s batching), `NeighbourhoodCrew` (dimension), `BikesClean` (update-policy target, with `CrewId`, `CrewName`) |
| Functions | `CleanBikes()` (update policy, includes the `lookup`), `NeighbourhoodNow()` |
| Materialized view | `StationLatest` (`arg_max(Timestamp, *)` by `BikepointID`) |
| Real-Time Dashboard | `BikeOpsDashboard` (parameter `_hood`) |
| Activator items | `BikeAlerts` (station rules), `BikeAutomation` (OneLake rule) |
| Lakehouse, folder, notebook | `BikeLakehouse`, `Files/landing`, `LoadLanding` |

Status rules used in KQL, dashboard and alerts: **Empty** = 0 bikes; **Full** = 0 empty docks; **Low** = under 20 %
occupancy; otherwise **OK**. Alert threshold: **empty for 5 minutes** (the shortest duration Activator's
occurrence picker offers).

## Facilitator notes

- **Lessons carried over from the full-day dry run.** The KQL editor runs one blank-line-separated block at a
  time, so every statement in `BikeEventhouse.kql` is its own block. In Activator, create the **object** first
  and the rule second. The dashboard's **Visual setup** pane lists **Y columns** before **X column**. The OneLake
  events wizard uses **Set filters**, not "Configure connection settings". The update policy's `lookup` reads
  another table, which Eventhouse refuses while the source table uses streaming ingestion. Lab 02 step 6 switches
  `BikesRaw` to queued ingestion with 10-second batching first, and explains why; make sure nobody skips it.
- **Capacity.** Every attendee runs one sample source, one Eventstream, one Eventhouse and one dashboard on live
  refresh. On a shared capacity, watch the Capacity Metrics app during Labs 02–03. If an Eventstream shows as
  paused after throttling, the attendee opens it and resumes it; nothing is lost but the gap.
- **Alert volume.** Rules in Lab 04 are filtered to one neighbourhood per attendee. Without the filter, the
  change rule fires for every station in London that runs empty: hundreds of emails. Check filters before
  anyone clicks **Start**.
- **No-data fallback.** There is none to prepare: the sample source is generated inside Fabric. If one
  attendee's stream won't start, pair them with a neighbour for Labs 02–04 and have them do Lab 05 meanwhile.

## Clean up after the session

The sample source keeps producing events, and the Eventhouse keeps consuming capacity, until you stop them.

1. `BikeAlerts` and `BikeAutomation`: select each rule, **Stop**.
2. `BikeEventstream`: in **Live** view, switch the `BicycleSample` source off (toggle on the source node).
3. Optional: delete the workspace items, or the workspace.

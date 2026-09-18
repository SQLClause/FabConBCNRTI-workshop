# Real-Time Intelligence Workshop Section

This folder contains the presenter materials for the **Real-Time Intelligence (RTI)** half (first 4 hours) of
*Building Intelligent, Event-Driven Architectures with Fabric Real-Time Intelligence* (FabCon Europe 2026,
Barcelona). The **Fabric IQ** half that follows lives in [`../FabricIQ/`](../FabricIQ/README.md) and assumes
everything taught here.

## Scenario

Everything in this section runs on one connecting narrative: **live Barcelona transit around the venue**.
An Azure Function (presenter-hosted) polls Transports Metropolitans de Barcelona (TMB) for real-time bus
arrival predictions (iBus) and metro arrivals at a curated set of stops and stations around the CCIB and the
city's main interchanges, and publishes one event per prediction to Azure Event Hubs. Attendees ingest that
stream with Eventstream, land and enrich it in an Eventhouse, visualize it on a Real-Time Dashboard, detect
conditions with Activator, and then broaden the picture to *non-telemetry* events (OneLake, Fabric job and
workspace events) to see the same event-driven pattern applied to data-platform automation.

The scenario is deliberately different from the afternoon's retail cold-chain scenario. Attendees learn the
RTI building blocks on transit data in the morning; in the afternoon they see the same blocks re-used
(`FreezerTelemetryRaw` → `FreezerTelemetryEnriched` → Activator) underneath Fabric IQ's ontology and agents.
See [`docs/alignment-with-fabric-iq.md`](docs/alignment-with-fabric-iq.md) for the explicit overlap check.

## Folder guide

| Folder | Contents |
|---|---|
| `prerequisites/` | Short pre-event checklist. Attendees need only a browser and the Microsoft-provided account; the presenter needs the Azure Function + Event Hubs running (see `infra/`). |
| `docs/` | Agenda, facilitator guide, risk/fallback plan, the data-feed contract for the Azure Function, and the alignment check against `FabricIQ/`. |
| `modules/` | Theory + hands-on lab content, one pair per module, in delivery order. Same template as `FabricIQ/docs/lab-guide-template.md`. |
| `artifacts/` | KQL scripts, reference CSVs, notebook code, dashboard tile queries, and sample event payloads that the labs paste from. |
| `infra/` | Presenter-only: Event Hubs provisioning script, TMB stop-code resolver, and a replay script for the no-live-data fallback. |
| `assets/` | Screenshot placeholders (`assets/screenshots/lab-XX/step-NN.png`), same convention as the Fabric IQ half. |

## Fixed naming contract

Used consistently across every lab, script and doc in this folder. Keep future edits consistent with it.

- Fabric workspace: **`RTI Transit`** (distinct from the afternoon's `Fabric IQ` workspace, which is provisioned separately by `FabricIQ/setup/provision_fabric_iq.py`)
- Eventhouse: **`TransitEventhouse`**, with its auto-created default KQL database (also named `TransitEventhouse`)
  - Raw tables: `BusArrivalsRaw`, `MetroArrivalsRaw`
  - Dimension tables: `StopsDim`, `LinesDim`, `MetroStationsDim`
  - Update-policy target: `BusArrivalsEnriched` (function `EnrichBusArrivals()`)
  - Materialized view: `BusNextArrivalLatest` (`arg_max(PolledAtUtc, *)` by `StopCode`, `LineCode`)
  - Aggregated table fed by Eventstream: `BusWaitByStopMinute`
- Eventstreams: **`BusArrivalsEventstream`** (Azure Event Hubs source `tmb-ibus-a` or `-b`), **`MetroArrivalsEventstream`** (Azure Event Hubs source `tmb-metro-a` or `-b`); the letter comes from the attendee's seat sheet
  - Derived stream: `ForumArrivals` (filtered to the venue-zone stops)
- Lakehouse: **`TransitLakehouse`** (folder `Files/reference/`, table `Stops`)
- KQL Queryset: **`TransitQueries`**
- Real-Time Dashboard: **`TransitOpsDashboard`**
- Activator items: **`TransitAlerts`** (rules on the live stream), **`TransitAutomation`** (rules on OneLake events)
- Notebook: **`LoadStopsReference`**
- Azure side (presenter): Azure Function in [`../RTIBCN/`](../RTIBCN/README.md) publishing flat per-prediction events to every hub of a feed; Event Hubs namespace `<prefix>-fabcon-ehns` (Premium), event hubs `tmb-ibus-a`, `tmb-ibus-b`, `tmb-metro-a`, `tmb-metro-b` (100 consumer groups per hub; 120 attendees + spare → two hubs per feed), listen-only SAS policy `attendee-listen`, consumer groups `attendee-001` … `attendee-130`
- Alert thresholds used everywhere: **long wait = next bus > 12 minutes sustained 3 minutes**; **silent stop = no events for 10 minutes**

## Quick start (attendees)

1. Read [`prerequisites/PREREQUISITES.md`](prerequisites/PREREQUISITES.md). It is short.
2. Start at [`modules/module-01-workspace-and-real-time-hub/lab-01-create-workspace-and-explore-real-time-hub.md`](modules/module-01-workspace-and-real-time-hub/lab-01-create-workspace-and-explore-real-time-hub.md).
3. Work through Modules 01–06 in order. Each lab's **Checkpoint** tells you what must exist before you move on.

## Quick start (facilitator)

See [`docs/facilitator-guide.md`](docs/facilitator-guide.md), [`docs/agenda.md`](docs/agenda.md) and, before anything
else, [`docs/data-feed-contract.md`](docs/data-feed-contract.md) plus [`infra/README.md`](infra/README.md), which
describe what the Azure Function must publish and how the shared Event Hubs namespace is set up for the room.

# Agenda — Real-Time Intelligence Section (240 minutes)

Runs **first**, before the Fabric IQ half. Single connecting scenario throughout: **live Barcelona transit
around the venue** (TMB bus arrival predictions + metro arrivals, polled by a presenter-hosted Azure Function
and published to Event Hubs). Attendees work entirely in the Fabric portal. Room size: **120**.

## How each module teaches

The audience is level 200 and many will not have touched RTI before, so every module runs **teach → show → do**:

1. **Theory** (the `XX-theory-*.md` file, presented): what the component is, its vocabulary, when to use it.
2. **Live demo** (last 3–5 minutes of the theory slot, on the instructor workspace): the presenter clicks through
   the exact lab path once, narrating the UI. Each theory file ends with a "Live demo before the lab" script.
3. **Lab**: attendees repeat it on their own workspace, with ✅ expected-result checks after every step.

Theory + demo time is **73 minutes** of the 240; labs are **136**; breaks and wrap-up the rest. Every lab has a
compressible tail so the theory slots are never the thing that gets cut.

| Time | Duration | Segment | Theory+demo / Lab | Topics covered | Primary Microsoft doc(s) adapted |
|---|---|---|---|---|---|
| 0:00–0:10 | 10 min | **Module 00 – Kickoff** | Theory 10 | Event-driven architectures in one slide; the day's two halves; the transit scenario; the four values to write down | [RTI overview](https://learn.microsoft.com/fabric/real-time-intelligence/overview) |
| 0:10–0:25 | 15 min | **Module 01 – Workspace & Real-Time hub** | Theory 5 / Lab 10 | Where RTI items live; Eventhouse vs KQL database; create `RTI Transit`, `TransitEventhouse`, `TransitLakehouse`; quick hub tour | [Create an eventhouse](https://learn.microsoft.com/fabric/real-time-intelligence/create-eventhouse), [Real-Time hub overview](https://learn.microsoft.com/fabric/real-time-hub/real-time-hub-overview) |
| 0:25–1:15 | 50 min | **Module 02 – Eventstream** | Theory+demo 15 / Lab 35 | Sources, default vs derived streams, operators, windows, destinations, direct vs processed ingestion, consumer groups; **flatten the raw API envelope** (Manage fields + Expand); build the bus stream end to end; metro stream via the hub | [Add Event Hubs source](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-azure-event-hubs), [Event processor editor](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/process-events-using-event-processor-editor), [Eventhouse destination](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database), [Derived stream](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-derived-stream) |
| 1:15–2:05 | 50 min | **Module 03 – Eventhouse & KQL** | Theory+demo 15 / Lab 35 | What Kusto is good at; KQL in five operators; `dynamic` columns and **`mv-expand`**; tables, functions, **update policies**, **materialized views**; `lookup`. Lab: explore envelopes, flatten, load CSVs, author policy + view, save queries; stretch: four-level metro flatten | [Get data from file](https://learn.microsoft.com/fabric/real-time-intelligence/get-data-local-file), [Update policy](https://learn.microsoft.com/kusto/management/update-policy), [Materialized views](https://learn.microsoft.com/kusto/management/materialized-views/materialized-view-overview) |
| 2:05–2:20 | 15 min | **Break** | — | — | — |
| 2:20–2:40 | 20 min | **Module 04 – Real-Time Dashboard** | Theory+demo 5 / Lab 15 | Tiles, visuals (map, KPI), parameters, live refresh; vs Power BI | [Create a Real-Time Dashboard](https://learn.microsoft.com/fabric/real-time-intelligence/dashboard-real-time-create) |
| 2:40–3:15 | 35 min | **Module 05 – Activator** | Theory+demo 12 / Lab 23 | Objects, properties, rules, actions; stateless vs stateful vs heartbeat; sustained occurrence; where rules are authored; Fabric-item actions. Lab: two rules on the venue stream | [Activator intro](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-introduction), [Detection conditions](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-detection-conditions) |
| 3:15–3:25 | 10 min | **Break** | — | — | — |
| 3:25–3:53 | 28 min | **Module 06 – Event-driven beyond telemetry** | Theory+demo 10 / Lab 18 | Fabric/Azure events, five patterns, Business events (preview); OneLake event → run notebook; workspace item events audit (presenter demo) | [Set alerts on OneLake events](https://learn.microsoft.com/fabric/real-time-hub/set-alerts-fabric-onelake-events), [Trigger Fabric items](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-trigger-fabric-items) |
| 3:53–4:00 | 7 min | **Module 07 – Wrap-up & handoff** | Theory 7 | **Park the workspace first** (3 min), then recap and what Fabric IQ builds on top | — |

**Total: 240 minutes.**

## Facilitator timing notes

- **Module 02 is the anchor.** Everything downstream needs `BusArrivalsRaw` filling. If the room is behind at
  1:15, cut Part D (metro) and step 21–22 (derived stream); both can be added back in Module 05's first minutes.
- **Module 03 Part F** (OneLake availability + interchange query) is the stretch; skip if behind.
- **Module 04 is the compressible buffer**: map + time chart only is a pass (8 minutes).
- **Module 06 Part D** (workspace item events) is presenter-demo by default.
- **Never cut theory to buy lab time.** With 120 people, a room that half-understood the component costs more
  minutes in troubleshooting than the five you'd save. Cut the lab tails listed above instead.
- **Do not skip Module 07's parking step.** The afternoon's Ontology/Data Agent labs run on the same per-attendee
  capacity.
- With 120 attendees, budget two helpers walking the room during Labs 02 and 05; the consumer-group sheet and the
  nested field picker in the Manage fields operator are the two things they'll fix most.

---
marp: true
theme: fabric-iq
layout: Main Content : Title + Text Box
paginate: true
footer: 'Fabric IQ Workshop · Module 02 — Telemetry & Grounding'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Template[3] -->

# Module 02
## Telemetry & grounding

**Topics 3–4**

<!-- notes: 40 min total — 15 min theory, 25 min lab. This module prepares the data both sides (static + live) need before we can build the ontology in Module 03. -->

---

## Learning objectives

By the end of this module you can:

- Explain how static contextual data and live telemetry are prepared to meet in Fabric IQ
- Describe the update-policy vs. materialized-view distinction at a conceptual level
- Identify the keys that let a freezer's live signal and static record be linked later

---

## Topic 3 — Combining real-time telemetry with semantic context

- RTI already gives us a live stream: `FreezerTelemetryEventstream` → `ColdChainEventhouse`
- Fabric IQ's job is to make that stream **meaningful**, not just fast
- Two ingredients have to come together:
  - **Live signal** — temperature, door state, arriving every few seconds
  - **Semantic context** — which freezer, which store, which customer base it serves
- Neither ingredient alone is enough — this module gets both into the right shape

---

## The Digital Twin Builder pattern

Microsoft's official RTI tutorial establishes the template we're following:

1. **Static contextual data** (customers, stores, freezers) is uploaded as CSVs
2. Landed into a **Lakehouse** (`ColdChainLakehouse`) as governed tables
3. Later **projected into the Eventhouse** so it can be joined against live telemetry
4. The **ontology** (Module 03) is what actually binds the two together for querying

<p class="small">Adapted from: Digital Twin Builder RTI tutorial, parts 1–2.</p>

---

<!-- _layout: Main Content : Title + Visual Data -->

## Where our reference data lives

**`ColdChainLakehouse`**

| Table | Contents |
|---|---|
| `Customers` | Customer records |
| `Stores` | Store master data |
| `Freezers` | Model, Capacity, InstallDate — nameplate specs, rarely change |

- This is **static context** — it changes rarely, if ever, during the day
- It's the "what should be true" half of grounding

---

<!-- _layout: Main Content : Title + Visual Data -->

## Where our live signal lives

**`ColdChainEventhouse`** → KQL database **`ColdChainKQLDB`**

| Table | Contents |
|---|---|
| `FreezerTelemetryRaw` | Every event exactly as ingested |
| `FreezerTelemetryEnriched` | Cleaned/derived — `TemperatureC`, `DoorOpen` |

- This is **live signal** — it changes every few seconds
- It's the "what is actually happening" half of grounding

---

## Topic 4 — Grounding signals with enterprise meaning

- "Grounding" = attaching a live signal to the business entity it's actually about
- Before an ontology can bind anything, both sides need **consistent keys**
  - A `FreezerID` in `FreezerTelemetryEnriched` must match a `FreezerID` in the Lakehouse `Freezers` table
- Get the keys wrong here, and no amount of ontology design later will fix it
- This module's real deliverable: **clean, joinable data on both sides**

---

## KQL: update policy vs. materialized view (conceptual)

<div class="columns">
<div>

**Update policy**

- Runs on **ingest**, per event
- Transforms `Raw` → `Enriched` automatically as data arrives
- Good for: cleaning, reshaping, deriving fields continuously

</div>
<div>

**Materialized view**

- Maintains a **pre-aggregated, always-fresh summary**
- Good for: "current state per freezer," rollups, dashboards
- Avoids re-scanning the whole raw table every query

</div>
</div>

<p class="small">Adapted from: Kusto update-policy docs, materialized-view use cases.</p>

---

## Applying that to our pipeline

- `FreezerTelemetryRaw` → **update policy** → `FreezerTelemetryEnriched`
  - Normalizes units, filters bad readings, computes `DoorOpen` from raw sensor codes
- A **materialized view** could maintain "latest reading per Freezer" for fast dashboard/agent queries
- Neither of these requires touching the raw stream — both are additive, non-destructive transforms

<div class="callout">
This is the plumbing. The ontology in Module 03 is what gives it business meaning.
</div>

---

<!-- _layout: Main Content : Title + Visual Data -->

## Example: raw event to enriched record

```text
FreezerTelemetryRaw
{ "sensorId": "FZ-118-T1", "ts": "...", "rawC": -9.2, "doorCode": 1 }

        │  update policy
        ▼

FreezerTelemetryEnriched
{ "FreezerID": "FZ-118", "TemperatureC": -9.2, "DoorOpen": true, "ts": "..." }
```

- Same event, now keyed by `FreezerID` — ready to be bound to a Freezer entity in Module 03

---

## Where this leaves us

- ✅ Static context landed in `ColdChainLakehouse` (`Customers`, `Stores`, `Freezers`)
- ✅ Live telemetry cleaned and keyed in `ColdChainEventhouse` (`FreezerTelemetryEnriched`)
- ✅ Both sides share consistent `FreezerID` / `StoreID` / `CustomerID` keys
- ⏭ Next: bind them together in a queryable ontology graph

---

<!-- _class: lab -->
<!-- _layout: Section Break Slide -->

## Hands-on lab

**Lab 02 — Telemetry & grounding**

- Land reference CSVs into `ColdChainLakehouse`
- Wire the freezer telemetry generator into `FreezerTelemetryEventstream`
- Inspect the update policy that produces `FreezerTelemetryEnriched`

📄 `modules/module-02-telemetry-and-grounding/lab-02-join-streaming-and-reference-data.md`

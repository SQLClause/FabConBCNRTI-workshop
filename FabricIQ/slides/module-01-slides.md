---
marp: true
theme: fabric-iq
layout: Main Content : Title + Text Box
paginate: true
footer: 'Fabric IQ Workshop · Module 01 — Architecture & Context'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Template[3] -->

# Module 01
## Fabric IQ architecture & why context matters

**Topics 1–2**

<!-- notes: 25 min total — 10 min theory, 15 min lab. Keep this tight; the real depth comes in Modules 02-04. -->

---

## Learning objectives

By the end of this module you can:

- Describe where Fabric IQ sits relative to Lakehouse, Eventhouse, and Power BI
- Explain, in one sentence, why raw events need business context to be actionable
- Recognize the three architectural layers we'll build through today

---

## Topic 1 — What is Fabric IQ?

- Fabric IQ is Microsoft's **ontology / semantic / agent layer** on top of Fabric
- It doesn't store a second copy of your data — it **overlays meaning** on data that already lives in OneLake
- Built for one purpose: make operational data **understandable and actionable** by both people and AI agents

<div class="callout">
Think of it as the layer that turns "a table of numbers" into "a Freezer that belongs to a Store."
</div>

---

## The architecture, three layers

1. **Data layer** — Lakehouse (`ColdChainLakehouse`), Eventhouse (`ColdChainEventhouse`) — this is what RTI already built
2. **Semantic layer** — the **ontology** (`ColdChainOntology`, built in Module 03) — entities, properties, relationships, bound to the data layer with *no copying*
3. **Agent layer** — Data Agent, Operations Agent, Activator Ontology Rules (Module 04) — reason and act over the semantic layer

---

## How the layers connect

- **Static context** (customer records, store master data, freezer specs) → **Lakehouse**
- **Live signals** (freezer temperature, door state) → **Eventstream → Eventhouse**
- **Ontology** binds both, without moving either
- **Agents** query and act through the ontology — never against raw tables directly

<p class="small">This is the same layering pattern as Microsoft's Digital Twin Builder tutorials — we're following a tested template, not inventing one.</p>

---

## Topic 2 — Why context matters for event interpretation

- A telemetry event is just **a number with a timestamp**
- The same number can mean *nothing* or *everything*, depending on what it's attached to
- Without context, every downstream system — dashboards, alerts, agents — has to *guess* at meaning
- With context, the same event becomes a **traceable, explainable business fact**

---

## Case study: what does -9°C mean?

<div class="columns">
<div>

**Without context**

- Reading: `-9°C`
- Source: `sensor-4471`
- ...is that bad?

</div>
<div>

**With context**

- Reading: `-9°C`
- Entity: **Freezer FZ-118**
- Normal range: **-18°C to -22°C**
- Store: **Copenhagen Nørrebro**
- ⚠️ **9°C above spec — door open or compressor fault**

</div>
</div>

<div class="callout">
Same number. One version tells you nothing. The other tells you exactly what to do and where to go.
</div>

<!-- notes: This is the single idea to hammer home before lunch — everything else today builds on it. If a room only remembers one slide, make it this one. -->

---

## The same reading, a different entity

- `-9°C` at a **freezer** → alarming, act now
- `-9°C` at a **loading dock cold room** (spec: -5°C to -10°C) → perfectly normal
- The raw event is identical — **only the entity context changes the required action**
- This is exactly what an ontology encodes: which entity, what's normal for it, what it relates to

---

## Where we're headed

- **Module 02** — get the static and live data ready for grounding
- **Module 03** — build `ColdChainOntology` so "-9°C" always resolves to the right entity and meaning
- **Module 04** — put agents on top that reason in business terms, not raw thresholds

---

<!-- _class: lab -->
<!-- _layout: Section Break Slide -->

## Hands-on lab

**Lab 01 — Architecture & context walkthrough**

- Tour the `Fabric IQ` workspace and identify each architectural layer
- Inspect the raw telemetry stream and discuss what context is missing

📄 `modules/module-01-architecture-and-context/lab-01-explore-workspace-and-data-landscape.md`

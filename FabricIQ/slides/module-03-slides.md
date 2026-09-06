---
marp: true
theme: fabric-iq
layout: Main Content : Title + Text Box
paginate: true
footer: 'Fabric IQ Workshop · Module 03 — Ontology Design'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Template[3] -->

# Module 03
## Ontology design essentials for operational AI

**Topic 5 — the core of this workshop**

<!-- notes:
45 min total — 15 min theory, 30 min lab. This is the highest-risk module (preview UI) and the
core learning objective of the whole afternoon. Do not let this get compressed — if anything runs
long, it's Module 05 that flexes, not this one. Have the screenshot fallback sequence open in a
browser tab before you start, per risk-fallback-plan.md.
-->

---

## Learning objectives

By the end of this module you can:

- Define entity type, property, and relationship in Fabric IQ's ontology model
- Explain how ontology binding works **without copying data**
- Describe why the ontology graph is queryable, not just descriptive
- Walk through the design of `ColdChainOntology` end to end

---

## What is an ontology, here?

- A **business-language model** of the things that matter: Customers, Stores, Freezers
- It sits *above* the Lakehouse and Eventhouse tables from Module 02 — it doesn't replace them
- Three building blocks:
  - **Entity type** — a kind of thing (`Freezer`)
  - **Property** — a fact about that thing (`TemperatureC`, `Model`)
  - **Relationship** — how entity types connect (`Store —has→ Freezer`)

---

## Entity type

- A named category of real-world thing your business cares about
- Examples in our scenario: `Customer`, `Store`, `Freezer`
- Each entity type has **properties** and can participate in **relationships**
- An entity type is *not* a table — it's a business concept that may be **bound** to one or more tables

---

## Property

- A single fact attached to an entity type
- Two flavors, both valid on the same entity type:
  - **Static** — rarely changes (`Freezer.Model`, `Freezer.Capacity`, `Freezer.InstallDate`)
  - **Live** — changes continuously (`Freezer.TemperatureC`, `Freezer.DoorOpen`)
- Properties are bound to source columns — the ontology stores the *mapping*, not the *value*

---

## Relationship

- A named, directional connection between two entity types
- In our scenario:
  - `Store` **—has→** `Freezer`
  - `Customer` **—shops at→** `Store`
- Relationships make the graph **traversable**: "show me every Freezer at every Store this Customer shops at"

---

## No-code binding, without copying data

- Binding an entity type's property to a table column is done **declaratively, in the ontology designer**
- No pipeline, no notebook, no data movement
- The ontology stores a **pointer**: "`Freezer.Model` comes from `ColdChainLakehouse.Freezers.Model`"
- Change the underlying data, and the ontology reflects it immediately — nothing to resync

<div class="callout">
This is the payoff of Module 02's work: because both sides already share clean keys, binding is just a few clicks.
</div>

---

## The queryable ontology graph

- Once entities, properties, and relationships are defined, the ontology is a **live graph** — not documentation
- You can query it directly: traverse relationships, filter on properties, mix static and live facts in one query
- This graph is what **agents** query in Module 04 — they never touch raw tables directly
- Same graph also powers Copilot-style natural-language question answering

---

## Worked example: ColdChainOntology

We build one ontology today: **`ColdChainOntology`**

**Entity types:** `Customer` · `Store` · `Freezer`

**Relationships:**
- `Store` **—has→** `Freezer`
- `Customer` **—shops at→** `Store`

---

<!-- _layout: Main Content : Title + Visual Data -->

## Freezer: a dual-bound entity type

`Freezer` is bound to **two different data sources at once**:

| Source | Binding | Properties |
|---|---|---|
| Lakehouse `ColdChainLakehouse.Freezers` | static | `Model`, `Capacity`, `InstallDate` |
| Eventhouse `ColdChainEventhouse.FreezerTelemetryEnriched` | live | `TemperatureC`, `DoorOpen` |

<div class="callout">
One entity, two speeds of truth. This is the architectural payoff of the whole morning: nameplate specs and live telemetry, on the same node in the graph.
</div>

---

<!-- _layout: Main Content : Title + Visual Data -->

## The full picture

```text
Customer ──shops at──▶ Store ──has──▶ Freezer
                                        │
                          ┌─────────────┴─────────────┐
                     static (Lakehouse)          live (Eventhouse)
                Model, Capacity, InstallDate   TemperatureC, DoorOpen
```

- This is the graph our agents will reason over in Module 04
- Every node is traceable back to a real table — nothing here is duplicated data

---

## Design principles worth internalizing

- Model **entity types around business concepts**, not around whatever tables happen to exist
- Keep relationships **directional and named** — "has" and "shops at" read like a sentence, not a foreign key
- Bind properties **as narrowly as needed** — don't drag in every column just because it's there
- A good ontology answers a plain-English question by construction: *"which freezers does this customer's usual store have?"*

---

<!-- _class: lab -->
<!-- _layout: Section Break Slide -->

## Hands-on lab

**Lab 03 — Build ColdChainOntology**

- Create entity types: `Customer`, `Store`, `Freezer`
- Bind `Freezer` to both `ColdChainLakehouse.Freezers` and `ColdChainEventhouse.FreezerTelemetryEnriched`
- Define relationships and run your first graph query

📄 `modules/module-03-ontology-design/lab-03-build-retail-coldchain-ontology.md`

<!-- notes: If the ontology designer misbehaves live, switch to the fallback screenshot sequence — see risk-fallback-plan.md. Don't skip the graph query at the end; it's what makes the payoff concrete before Module 04. -->

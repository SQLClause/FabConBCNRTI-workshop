---
marp: true
theme: fabric-iq
layout: Main Content : Title + Text Box
paginate: true
footer: 'Fabric IQ Workshop · Module 04 — Agent Patterns'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Template[3] -->

# Module 04
## Agent patterns over real-time and semantic layers

**Topic 6**

<!-- notes:
35 min total — 15 min theory, 20 min lab. Second highest-risk module (preview UI: Data Agent,
Operations Agent, Activator ontology rules). Fallback screenshot sequence should be ready.
-->

---

## Learning objectives

By the end of this module you can:

- Name four distinct ways to ground an agent in an ontology, and when to reach for each
- Explain what `ColdChainDataAgent` and `ColdChainOperationsAgent` each do
- Describe how an Activator Ontology Rule differs from a raw-threshold Activator rule

---

## Why agents need grounding

- An LLM with no context will guess, hallucinate units, or invent entities that don't exist
- `ColdChainOntology` gives an agent a **fixed vocabulary**: real entity types, real properties, real relationships
- Every question an agent answers, and every action it takes, can be traced back to a graph node
- This module is about **where** an agent plugs into that graph

---

<!-- _layout: Main Content : Title + Visual Data -->

## Four ways to ground an agent

| Pattern | Grounding style | Best for |
|---|---|---|
| **Fabric Data Agent** | Q&A over the ontology graph | Ask-a-question, exploratory analysis |
| **Operations Agent** | Event-triggered, paired with rules | React to conditions as they happen |
| **Foundry IQ** | Ontology as a tool for custom AI apps | Building bespoke agentic apps in Azure AI Foundry |
| **Copilot Studio MCP connector** | Ontology exposed via MCP | Grounding agents built outside Fabric entirely |

---

## Pattern 1 — Fabric Data Agent: `ColdChainDataAgent`

- Grounded directly in **`ColdChainOntology`**
- Answers natural-language questions by traversing the graph
- *"Which freezers at the Nørrebro store are older than 5 years?"* → traverses `Store —has→ Freezer`, filters `InstallDate`
- Question-and-answer pattern — a person (or another system) initiates

---

## Pattern 2 — Operations Agent: `ColdChainOperationsAgent`

- Also grounded in `ColdChainOntology`, but **event-triggered rather than question-driven**
- Paired with an **Activator Ontology Rule**: **"Freezer running warm"**
- Fires when `TemperatureC` rises above roughly **-12°C** for a sustained period
- Simulates a real operational fault: **door left open, or compressor failure**

---

## Activator Ontology Rules vs. classic Activator rules

<div class="columns">
<div>

**Classic Activator (RTI half)**

- Threshold on a raw column
- *"Alert if `TemperatureC` > -12"*
- No idea what entity, store, or customer is involved

</div>
<div>

**Activator Ontology Rule**

- Threshold on an **entity's property**
- *"Alert if this **Freezer** is running warm"*
- Carries the whole graph context: which Store, which Customer base

</div>
</div>

<div class="callout">
Same math, radically different output — one gives you a number, the other gives you a business incident.
</div>

---

## Case study: "Freezer running warm" end to end

1. `FreezerTelemetryEnriched.TemperatureC` climbs above ≈ **-12°C** and stays there
2. The **Activator Ontology Rule** evaluates this against the `Freezer` entity, not a raw column
3. Rule fires → **`ColdChainOperationsAgent`** is notified
4. Agent has full graph context: *this* Freezer, *its* Store, *its* Model/Capacity/InstallDate
5. Agent can act or notify **in business language**: *"Freezer FZ-118 at Nørrebro is running warm — check the door or compressor"*

<!-- notes: This is the payoff slide for the whole day — walk it slowly. It ties together Module 01's -9°C example, Module 02's grounding work, and Module 03's ontology. -->

---

## Pattern 3 — Foundry IQ

- Exposes the ontology as a grounding source for custom agentic applications built in **Azure AI Foundry**
- Use when you need an agent experience **beyond** what Fabric's built-in Data/Operations Agents offer
- Same underlying graph, same trust guarantees — different build surface

---

## Pattern 4 — Copilot Studio MCP connector

- Fabric IQ exposes the ontology via **MCP (Model Context Protocol)**
- Lets an agent built entirely **outside Fabric** — e.g. in Copilot Studio — ground its answers in `ColdChainOntology`
- The ontology becomes a reusable grounding source across your whole agent estate, not just Fabric-native agents

---

## Choosing a pattern

- Need ad-hoc Q&A over the graph? → **Data Agent**
- Need to react automatically when something changes? → **Operations Agent** + **Ontology Rule**
- Building a custom AI app in Foundry? → **Foundry IQ**
- Grounding an agent that lives outside Fabric? → **Copilot Studio MCP connector**
- All four read from the **same ontology** — no duplicated modeling effort

---

<!-- _class: lab -->
<!-- _layout: Section Break Slide -->

## Hands-on lab

**Lab 04 — Agent patterns**

- Build `ColdChainDataAgent`, grounded in `ColdChainOntology`
- Create the **"Freezer running warm"** Activator Ontology Rule
- Build `ColdChainOperationsAgent` and trigger it with live telemetry

📄 `modules/module-04-agent-patterns/lab-04-build-data-agent-and-operations-agent.md`

<!-- notes: If the generator hasn't produced a warm reading naturally, use the manual override step in the lab to force one — don't burn lab time waiting on randomness. -->

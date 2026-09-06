---
marp: true
theme: fabric-iq
layout: Main Content : Title + Text Box
paginate: true
footer: 'Fabric IQ Workshop · Module 06 — Wrap-up'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Template[3] -->

# Module 06
## Wrap-up

**Recap · resources · next steps**

<!-- notes: 10 min, theory only, no lab. Keep this brisk — energy is low at the end of a 4-hour session. -->

---

<!-- _layout: Main Content : Title + Visual Data -->

## What you built today

```text
Fabric IQ (workspace)
  │
  ├── ColdChainLakehouse ─── Customers · Stores · Freezers
  ├── ColdChainEventhouse ── ColdChainKQLDB
  │      FreezerTelemetryRaw ──▶ FreezerTelemetryEnriched
  ├── FreezerTelemetryEventstream
  │
  ├── ColdChainOntology ──── Customer ─shops at→ Store ─has→ Freezer
  │                                                    (static + live bound)
  │
  ├── ColdChainDataAgent ─────── grounded in ColdChainOntology
  └── ColdChainOperationsAgent ─ + "Freezer running warm" rule
```

---

## The arc of the day

1. **Module 01** — a raw reading means nothing without context
2. **Module 02** — prepared static context and live telemetry to be groundable
3. **Module 03** — built the ontology that gives every reading a business meaning
4. **Module 04** — put agents on top that reason and act in business language
5. **Module 05** — saw how grounding makes those agents trustworthy and auditable

<div class="callout">
Same idea, four different layers: workspace → data → ontology → agents.
</div>

---

## Official Microsoft tutorials this workshop adapted

- [Get started with Fabric IQ](https://learn.microsoft.com/fabric/iq/get-started-with-fabric-iq)
- [Fabric IQ overview](https://learn.microsoft.com/fabric/iq/overview)
- [Ontology tutorial 0 — Introduction](https://learn.microsoft.com/fabric/iq/ontology/tutorial-0-introduction)
- [Ontology tutorial 1 — Create an ontology](https://learn.microsoft.com/fabric/iq/ontology/tutorial-1-create-ontology)
- [Ontology tutorial 4 — Create a data agent](https://learn.microsoft.com/fabric/iq/ontology/tutorial-4-create-data-agent)

---

## Official Microsoft tutorials, continued

- [Digital Twin Builder RTI tutorial — upload contextual data](https://learn.microsoft.com/fabric/real-time-intelligence/digital-twin-builder/tutorial-rti-1-upload-contextual-data)
- [Kusto update policies](https://learn.microsoft.com/kusto/management/update-policy)
- [Kusto materialized views — use cases](https://learn.microsoft.com/kusto/management/materialized-views/materialized-view-use-cases)
- [Create an operations agent](https://learn.microsoft.com/fabric/iq/ontology/how-to-create-operations-agent)
- [Ontology rules](https://learn.microsoft.com/fabric/iq/ontology/how-to-use-rules)
- [Agent integration concepts](https://learn.microsoft.com/fabric/iq/ontology/concepts-agent-integration)
- [Fabric IQ Ontology MCP connector](https://learn.microsoft.com/microsoft-copilot-studio/mcp-fabric-iq-ontology)
- [mslearn-fabric hands-on labs](https://microsoftlearning.github.io/mslearn-fabric/)

---

## Keep learning after today

- Rerun today's labs in your own tenant — the `modules/` folder is yours to keep
- Extend `ColdChainOntology` with a new entity type (e.g. `MaintenanceTicket`) as a self-study exercise
- Try grounding an external agent via the **Copilot Studio MCP connector** against your ontology
- Explore **Foundry IQ** if you're already building custom agentic apps in Azure AI Foundry

---

## Before you go

- If you provisioned a trial/temporary capacity just for today, remember to **clean up** the `Fabric IQ` workspace to avoid ongoing charges
- Slides, lab guides, and setup scripts all live in this repo — clone it, don't just screenshot it
- Feedback helps us improve the next run of this workshop — please fill in the session survey

---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Section Break Slide -->

# Thank you

**Questions, feedback, and freezer-alert war stories always welcome.**

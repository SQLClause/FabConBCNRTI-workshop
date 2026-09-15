---
marp: true
theme: fabric-iq
layout: Main Content : Title + Text Box
paginate: true
footer: 'Fabric IQ Workshop · Module 05 — Prompting, Trust & Traceability'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Template[3] -->

# Module 05
## Prompting, trust & traceability

**Topics 7–8**

<!-- notes:
15 min total — 10 min theory, 5 min lab (cut from 35/15/20 to fund Module 00's expanded live setup —
see docs/agenda.md). This is still the designated timing buffer on top of that: if Modules 03/04 ran
long, compress this module's already-short lab into a facilitator-led walkthrough rather than cutting
content from 03/04. Do not skip this module's ideas, though — trust/traceability is the responsible-AI
payoff of the whole day.
-->

---

## Learning objectives

By the end of this module you can:

- Explain how ontology grounding constrains and validates an agent's responses
- Contrast a grounded agent's answer with a free-form LLM answer on the same question
- Describe what an audit trail looks like for an ontology-triggered agent action

---

## Topic 7 — Prompting, grounding, and response validation

- A prompt to `ColdChainDataAgent` isn't answered by the raw LLM alone
- The agent's response is **constrained to what the ontology graph actually contains**
- If a fact isn't a node, property, or relationship in `ColdChainOntology`, the agent can't fabricate it into an answer
- This is validation **by construction**, not a post-hoc check bolted on afterward

---

## Grounded agent vs. free-form LLM

<div class="columns">
<div>

**Free-form LLM**

- Answers from general training knowledge
- No guaranteed link to *your* data
- Can sound confident and still be wrong
- No way to verify which record it "used"

</div>
<div>

**Ontology-grounded agent**

- Answers by traversing real entities and properties
- Every fact traces to a bound column
- Wrong data → wrong answer, but never a *fabricated* entity
- Response can cite the entity/property it used

</div>
</div>

---

## Response validation strategies

- **Schema-constrained answers** — the agent can only reference entity types/properties that exist in the ontology
- **Cite the source** — a good response names the entity instance behind the answer (*"based on Freezer FZ-118..."*)
- **Confidence framing** — distinguish "the graph says X" from "I'm inferring X"
- **Fail closed** — if the graph doesn't have the answer, the agent should say so, not guess

---

## Topic 8 — Trust, transparency, and traceability

- An agent that can *act* (like `ColdChainOperationsAgent`) needs more than a good answer — it needs an **audit trail**
- Three questions every stakeholder will ask after an incident:
  1. **What** triggered this action?
  2. **Which entity** was it about?
  3. **What data** was the decision based on?
- Ontology grounding makes all three answerable by design

---

<!-- _layout: Main Content : Title + Visual Data -->

## Case study: tracing "Freezer running warm"

```text
FreezerTelemetryEnriched.TemperatureC crosses ~-12°C, sustained
        │
        ▼
Activator Ontology Rule "Freezer running warm" fires
        │  (bound to entity: Freezer FZ-118, via ColdChainOntology)
        ▼
ColdChainOperationsAgent notified / acts
        │
        ▼
Audit trail: rule name, entity instance, triggering readings,
             Store + Customer context — all traceable, end to end
```

<div class="callout">
Compare this to a raw-threshold alert: "value exceeded -12" — no entity, no store, no traceable business meaning.
</div>

---

## Why this matters operationally

- A manager asking *"why did this fire?"* gets a real answer, not a log line with a sensor ID
- Compliance/audit reviews can replay **which entity, which rule, which underlying reading** caused an action
- Trust compounds: once one traced incident checks out, the room trusts the next ten
- This is the difference between an agent you **monitor** and one you **rely on**

---

## Bringing it together

- Grounding (Topic 7) prevents the agent from saying something false
- Traceability (Topic 8) lets you prove *why* it said or did something true
- Both come from the same source: the ontology graph built in Module 03
- Everything downstream — Data Agent answers, Operations Agent actions — inherits this for free

---

<!-- _class: lab -->
<!-- _layout: Section Break Slide -->

## Hands-on lab

**Lab 05 — Prompting, trust & traceability**

- Ask `ColdChainDataAgent` a question and inspect which entities/properties it cited
- Trace a fired "Freezer running warm" event back to its source reading

📄 `modules/module-05-prompting-trust-traceability/lab-05-validate-and-audit-agent-responses.md`

<!-- notes: If time is short (per the buffer note), run this as a facilitator-led walkthrough on the instructor workspace rather than fully hands-on — the ideas matter more than everyone clicking through it individually. -->

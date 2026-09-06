---
marp: true
theme: fabric-iq
layout: Main Content : Title + Text Box
paginate: true
footer: 'Fabric IQ Workshop · Module 00'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _layout: Template[3] -->

# Fabric IQ
## Grounding real-time intelligence in enterprise context

**Retail cold-chain monitoring, end to end**

<!-- notes:
Kickoff (5 min). Welcome the room, introduce yourself, and set expectations: this is the
second half of the day, built directly on top of what Johan just covered.
-->

---

## Today's scenario, in one line

A retail chain with **stores**, **customers**, and **freezers** full of frozen goods.

- Freezers stream live temperature telemetry, second by second
- A raw reading like **-9°C** is meaningless on its own
- Fabric IQ adds the business context that turns a number into a decision

> We spend the next four hours building this — live, in your own workspace.

---

## Where this fits in the day

- **Morning / first half (Johan):** Real-Time Intelligence — Eventstream, Eventhouse, Activator
- **This half (Brian):** **Fabric IQ** — the semantic and agent layer *on top of* RTI
- Same retail cold-chain data, same workspace — we're extending, not restarting

<!-- notes: Reassure the room this isn't a context switch — it's the next layer on the same stack they just built. -->

---

## The four-hour build, top to bottom

1. **Module 01** — Fabric IQ architecture & why context matters
2. **Module 02** — Telemetry + semantic context, grounding signals
3. **Module 03** — Build `ColdChainOntology` (highest-value module)
4. **Module 04** — Agents on top: `ColdChainDataAgent`, `ColdChainOperationsAgent`
5. **Module 05** — Prompting, trust, traceability
6. **Module 06** — Wrap-up & resources

---

## Light RTI recap

You already built (or will verify) these in the `Fabric IQ` workspace:

- **Eventstream** — `FreezerTelemetryEventstream`, streaming simulated freezer readings
- **Eventhouse** — `ColdChainEventhouse`, KQL database `ColdChainKQLDB`
  - `FreezerTelemetryRaw` — raw ingested events
  - `FreezerTelemetryEnriched` — cleaned/derived table
- **Activator** — rule-based alerting on raw thresholds (Johan's half)

<div class="callout">
Fabric IQ doesn't replace any of this — it sits on top of it.
</div>

---

## Environment verification: what should already exist

- [ ] Workspace named **`Fabric IQ`** on a non-trial capacity
- [ ] Lakehouse **`ColdChainLakehouse`** with `Customers`, `Stores`, `Freezers` tables
- [ ] Eventhouse **`ColdChainEventhouse`** / KQL DB **`ColdChainKQLDB`**
- [ ] Eventstream **`FreezerTelemetryEventstream`** created
- [ ] You can sign in to the Fabric portal and see this workspace

<p class="small">If any of these are missing, flag it now — Module 00's lab time is built for exactly this.</p>

---

## Housekeeping

- Two breaks: after Module 02, and after Module 04
- **Module 05 is a built-in buffer** — if Modules 03/04 run long, we compress 05, not 03/04
- Modules 03 and 04 touch **preview UI** — if something misbehaves live, we have a fallback walkthrough ready
- Ask questions as we go — this is hands-on, not a lecture

---

<!-- _class: lab -->
<!-- _layout: Section Break Slide -->

## Hands-on lab

**Lab 00 — Setup verification**

- Confirm your `Fabric IQ` workspace and items match the checklist above
- Troubleshoot with the facilitator if anything is missing or greyed out

📄 `modules/module-00-welcome-and-setup/lab-00-environment-setup-and-verify.md`

<!-- notes: Walk the room during this lab — most first-time issues are tenant preview settings not enabled, covered in PREREQUISITES.md. -->

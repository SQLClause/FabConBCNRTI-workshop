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

## What you'll have when this module ends

- [ ] Workspace named **`Fabric IQ`** on a non-trial capacity
- [ ] Lakehouse **`ColdChainLakehouse`** with `Customers`, `Stores`, `Freezers` tables
- [ ] Eventhouse **`ColdChainEventhouse`** / KQL DB **`ColdChainKQLDB`**
- [ ] Eventstream **`FreezerTelemetryEventstream`** created

<p class="small">Didn't pre-run the setup script? No problem — that's the default, not the exception. We build all of this live in the next 35 minutes.</p>

---

## Housekeeping

- Two breaks: after Module 02, and after Module 04
- **Module 05 is a built-in buffer** — if Modules 03/04 run long, we compress 05, not 03/04
- Modules 03 and 04 touch **preview UI** — if something misbehaves live, we have a fallback walkthrough ready
- Ask questions as we go — this is hands-on, not a lecture

---

<!-- _class: lab -->
<!-- _layout: Section Break Slide -->

## Hands-on lab (35 min)

**Lab 00 — Set up & verify**

- **Part A:** install the Fabric CLI, sign in, and run `provision_fabric_iq.py` live — skip straight to Part B if you already did this before today
- **Part B:** everyone confirms the `Fabric IQ` workspace and items match the checklist above

📄 `modules/module-00-welcome-and-setup/lab-00-environment-setup-and-verify.md`

<!-- notes: Walk the room during Part A — most first-time issues are either a blocked VPN/proxy or a
trial capacity slipping through. A trial capacity is a hard stop: pair that attendee with a neighbor
immediately rather than let them try to troubleshoot it, since it traces back to a tenant-admin setting
in PREREQUISITES.md that can't be fixed live. Attendees who pre-ran setup finish Part B early — point
them ahead to Module 01 or have them help a neighbor instead of waiting idle. -->

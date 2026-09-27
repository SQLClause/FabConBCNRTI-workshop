# Agenda — Fabric IQ Section (240 minutes)

Runs **after** the Real-Time Intelligence (RTI) half of the day, so Module 08/09 give a light recap of
Eventstream/Eventhouse/Activator rather than teaching them from scratch. Single connecting scenario
throughout: **retail cold-chain monitoring** (Customer / Store / Freezer entities + live freezer
temperature telemetry).

| Time | Duration | Segment | Theory / Lab | Topics covered | Primary Microsoft tutorial(s) adapted |
|---|---|---|---|---|---|
| 0:00–0:05 | 5 min | Kickoff & scenario framing | Theory only | — | — |
| 0:05–0:45 | 40 min | **Module 08 – Set up & verify** | Theory 5 / Lab 35 | Live environment provisioning (software install + `provision_fabric_iq.py`), verification, light RTI recap | [Get started with Fabric IQ](https://learn.microsoft.com/fabric/iq/get-started-with-fabric-iq) |
| 0:45–1:10 | 25 min | **Module 09 – Architecture & Context** | Theory 10 / Lab 15 | 1. Fabric IQ architecture · 2. Why context matters for event interpretation | [Fabric IQ overview](https://learn.microsoft.com/fabric/iq/overview), [Ontology tutorial 0](https://learn.microsoft.com/fabric/iq/ontology/tutorial-0-introduction) |
| 1:10–1:50 | 40 min | **Module 10 – Telemetry & Grounding** | Theory 15 / Lab 25 | 3. Combining real-time telemetry with semantic context · 4. Grounding signals with enterprise meaning | [Digital Twin Builder RTI tutorial parts 1–2](https://learn.microsoft.com/fabric/real-time-intelligence/digital-twin-builder/tutorial-rti-1-upload-contextual-data), [Kusto update policies](https://learn.microsoft.com/kusto/management/update-policy), [materialized views](https://learn.microsoft.com/kusto/management/materialized-views/materialized-view-use-cases) |
| 1:50–2:05 | 15 min | **Break** | — | — | — |
| 2:05–2:50 | 45 min | **Module 11 – Ontology Design** (highest-risk: preview UI) | Theory 15 / Lab 30 | 5. Ontology design essentials for operational AI | [Tutorial 1 – Create an ontology](https://learn.microsoft.com/fabric/iq/ontology/tutorial-1-create-ontology), [mslearn labs 23/24/27](https://microsoftlearning.github.io/mslearn-fabric/), [Digital Twin Builder parts 3–4](https://learn.microsoft.com/fabric/real-time-intelligence/digital-twin-builder/tutorial-rti-1-upload-contextual-data) |
| 2:50–3:25 | 35 min | **Module 12 – Agent Patterns** | Theory 15 / Lab 20 | 6. Agent patterns over real-time and semantic layers | [Tutorial 4 – Create a data agent](https://learn.microsoft.com/fabric/iq/ontology/tutorial-4-create-data-agent), [mslearn lab 28](https://microsoftlearning.github.io/mslearn-fabric/), [Create an operations agent](https://learn.microsoft.com/fabric/iq/ontology/how-to-create-operations-agent), [Ontology rules](https://learn.microsoft.com/fabric/iq/ontology/how-to-use-rules) |
| 3:25–3:35 | 10 min | **Break** | — | — | — |
| 3:35–3:50 | 15 min | **Module 13 – Prompting, Trust & Traceability** (built-in time buffer — compressible to discussion-only if Modules 11/12 ran long) | Theory 10 / Lab 5 | 7. Prompting, grounding, and response validation strategies · 8. Trust, transparency, and traceability in agent outputs | [Agent integration concepts](https://learn.microsoft.com/fabric/iq/ontology/concepts-agent-integration), [Fabric IQ Ontology MCP](https://learn.microsoft.com/microsoft-copilot-studio/mcp-fabric-iq-ontology) |
| 3:50–4:00 | 10 min | **Module 14 – Wrap-up** | Theory only | Recap, resources, cleanup, feedback | — |

**Total: 240 minutes.**

## Facilitator timing notes

- **Module 08 is now 40 minutes and assumes most of the room is provisioning live for the first time**,
  not just verifying pre-done work — attendees are no longer expected to have run
  `setup/provision_fabric_iq.py` before arriving (see `prerequisites/PREREQUISITES.md`, which now covers
  only the admin-only, can't-be-done-live items). Attendees who *did* pre-run it skip straight to Part B
  of the lab and will have spare time — point them ahead to Module 09's reading or let them help a
  neighbor.
- This 20-minute increase was taken entirely from Module 13 (35 min → 15 min), which was already the
  designated compressible buffer — see below. Modules 09–12's durations are unchanged; only their clock
  times shifted later by 20 minutes.
- Module 13 remains the buffer for the *rest* of the section too: if Module 11 or 12 overruns (most
  likely, since both touch preview UI), compress Module 13's lab further into a facilitator-led
  discussion rather than cutting Module 11/12 short — ontology design and agent patterns are the core
  learning objectives of this section. At only 15 minutes to start with, there's less slack here than
  before, so protecting Module 08's new 40-minute block (not letting it run over) matters more than it
  used to.
- See [`risk-fallback-plan.md`](risk-fallback-plan.md) for what to do if live preview features misbehave
  during Module 11 or 12, and for Module 08's updated risk profile now that most of the room sets up
  live simultaneously.

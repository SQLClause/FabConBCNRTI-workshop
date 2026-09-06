# Agenda — Fabric IQ Section (240 minutes)

Runs **after** the Real-Time Intelligence (RTI) half of the day, so Module 00/01 give a light recap of
Eventstream/Eventhouse/Activator rather than teaching them from scratch. Single connecting scenario
throughout: **retail cold-chain monitoring** (Customer / Store / Freezer entities + live freezer
temperature telemetry).

| Time | Duration | Segment | Theory / Lab | Topics covered | Primary Microsoft tutorial(s) adapted |
|---|---|---|---|---|---|
| 0:00–0:05 | 5 min | Kickoff & scenario framing | Theory only | — | — |
| 0:05–0:25 | 20 min | **Module 00 – Setup verification** | Theory 5 / Lab 15 | Environment verification, light RTI recap | [Get started with Fabric IQ](https://learn.microsoft.com/fabric/iq/get-started-with-fabric-iq) |
| 0:25–0:50 | 25 min | **Module 01 – Architecture & Context** | Theory 10 / Lab 15 | 1. Fabric IQ architecture · 2. Why context matters for event interpretation | [Fabric IQ overview](https://learn.microsoft.com/fabric/iq/overview), [Ontology tutorial 0](https://learn.microsoft.com/fabric/iq/ontology/tutorial-0-introduction) |
| 0:50–1:30 | 40 min | **Module 02 – Telemetry & Grounding** | Theory 15 / Lab 25 | 3. Combining real-time telemetry with semantic context · 4. Grounding signals with enterprise meaning | [Digital Twin Builder RTI tutorial parts 1–2](https://learn.microsoft.com/fabric/real-time-intelligence/digital-twin-builder/tutorial-rti-1-upload-contextual-data), [Kusto update policies](https://learn.microsoft.com/kusto/management/update-policy), [materialized views](https://learn.microsoft.com/kusto/management/materialized-views/materialized-view-use-cases) |
| 1:30–1:45 | 15 min | **Break** | — | — | — |
| 1:45–2:30 | 45 min | **Module 03 – Ontology Design** (highest-risk: preview UI) | Theory 15 / Lab 30 | 5. Ontology design essentials for operational AI | [Tutorial 1 – Create an ontology](https://learn.microsoft.com/fabric/iq/ontology/tutorial-1-create-ontology), [mslearn labs 23/24/27](https://microsoftlearning.github.io/mslearn-fabric/), [Digital Twin Builder parts 3–4](https://learn.microsoft.com/fabric/real-time-intelligence/digital-twin-builder/tutorial-rti-1-upload-contextual-data) |
| 2:30–3:05 | 35 min | **Module 04 – Agent Patterns** | Theory 15 / Lab 20 | 6. Agent patterns over real-time and semantic layers | [Tutorial 4 – Create a data agent](https://learn.microsoft.com/fabric/iq/ontology/tutorial-4-create-data-agent), [mslearn lab 28](https://microsoftlearning.github.io/mslearn-fabric/), [Create an operations agent](https://learn.microsoft.com/fabric/iq/ontology/how-to-create-operations-agent), [Ontology rules](https://learn.microsoft.com/fabric/iq/ontology/how-to-use-rules) |
| 3:05–3:15 | 10 min | **Break** | — | — | — |
| 3:15–3:50 | 35 min | **Module 05 – Prompting, Trust & Traceability** (built-in time buffer — compressible to discussion-only if Modules 03/04 ran long) | Theory 15 / Lab 20 | 7. Prompting, grounding, and response validation strategies · 8. Trust, transparency, and traceability in agent outputs | [Agent integration concepts](https://learn.microsoft.com/fabric/iq/ontology/concepts-agent-integration), [Fabric IQ Ontology MCP](https://learn.microsoft.com/microsoft-copilot-studio/mcp-fabric-iq-ontology) |
| 3:50–4:00 | 10 min | **Module 06 – Wrap-up** | Theory only | Recap, resources, cleanup, feedback | — |

**Total: 240 minutes.**

## Facilitator timing notes

- Module 00's 20 minutes assumes most attendees pre-ran `setup/provision_fabric_iq.py` per
  `prerequisites/PREREQUISITES.md` before arriving — this slot is verification and troubleshooting
  for stragglers, not first-time provisioning for the whole room.
- Module 05 is the designated buffer: if Module 03 or 04 overruns (most likely, since both touch
  preview UI), compress Module 05's lab into a facilitator-led walkthrough rather than cutting Module
  03/04 short — ontology design and agent patterns are the core learning objectives of this section.
- See [`risk-fallback-plan.md`](risk-fallback-plan.md) for what to do if live preview features misbehave
  during Module 03 or 04.

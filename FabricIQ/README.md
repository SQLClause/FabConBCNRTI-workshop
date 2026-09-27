# Fabric IQ Workshop Section

This folder contains the presenter materials for the **Fabric IQ** half (4 hours) of
*Building Intelligent, Event-Driven Architectures with Fabric Real-Time Intelligence*.
It picks up where the Real-Time Intelligence (RTI) half leaves off and adds the semantic/ontology
and agent layer on top of it.

See [`BUILD_PLAN.md`](BUILD_PLAN.md) for the full design rationale and [`plan.md`](plan.md) for the
original brief this was built from.

## Scenario

Everything in this section — labs, sample data, the provisioning script — runs on a single connecting
narrative: **retail cold-chain monitoring**. Live freezer temperature telemetry (Eventstream/Eventhouse)
is grounded with business context (Customer/Store/Freezer entities in a Fabric IQ Ontology), and agents
are built on top to reason over both. This directly extends Microsoft's own official retail ontology
tutorial and Digital Twin Builder bus-tutorial pattern rather than inventing a new scenario from scratch.

## Folder guide

| Folder | Contents |
|---|---|
| `prerequisites/` | **Read this first if you are hosting this session, or forward it to your tenant admin if you're attending.** The only things that must happen before the event — tenant-admin settings and capacity access that can't be fixed live. Attendee software install + provisioning happens live in Module 08 now, not as homework. |
| `setup/` | The provisioning script (`provision_fabric_iq.py`) that creates the "Fabric IQ" workspace and its RTI plumbing (Lakehouse, Eventhouse, Eventstream, notebook) via the Fabric CLI (`fab`). |
| `artifacts/` | Fabric item definitions and sample data the provisioning script imports. |
| `modules/` | Theory + hands-on lab content, one pair per module, in delivery order. |
| `slides/` | Marp-format PowerPoint decks (source `.md` + generated `.pptx`) for presenting the theory portions. |
| `docs/` | Agenda, the shared lab-guide template, the facilitator guide, and the risk/fallback plan. |
| `assets/` | Screenshots and links to fallback screen recordings, used if live preview features misbehave. |

## Quick start (attendees)

1. If you're not your own tenant admin, forward [`prerequisites/PREREQUISITES.md`](prerequisites/PREREQUISITES.md)
   to whoever is, **at least two weeks before the event** — it's short on purpose and only covers the
   handful of tenant-level settings that genuinely can't be fixed live.
2. Nothing else to do ahead of time. Bring a laptop with admin rights to install software, and start at
   [`modules/module-08-welcome-and-setup/lab-08-environment-setup-and-verify.md`](modules/module-08-welcome-and-setup/lab-08-environment-setup-and-verify.md)
   on the day — Part A walks you through cloning this repo, installing dependencies, and running the
   provisioning script live, in the room.
3. Already ran the setup yourself ahead of time? Great — skip straight to Part B of that same lab.

## Quick start (facilitator)

See [`docs/facilitator-guide.md`](docs/facilitator-guide.md) and [`docs/agenda.md`](docs/agenda.md).

# Alignment check against `FabricIQ/` (the afternoon half)

Reviewed against `FabricIQ/` at commit `a52018d` (18 Sep 2026): `README.md`, `SESSION_MEMORY.md`,
`docs/agenda.md`, all seven module theory/lab files, the KQL schema, the Eventstream definition, the generator
and `slides/module-08-slides.md`. This file records (a) what the RTI half deliberately covers because the IQ
half assumes it, (b) what it deliberately avoids because the IQ half owns it, and (c) small edits the IQ half
should make so the two halves tell one story.

## A. What the IQ half assumes attendees already know (RTI must teach these)

| IQ reference | Assumption | Where RTI covers it |
|---|---|---|
| `08-theory-kickoff-and-scenario.md`: "You've just spent the morning in Johan's RTI session, working with Eventstream, Eventhouse, and Activator … We won't re-teach RTI fundamentals" | All three items at a working level | Modules 02, 03, 05 |
| `slides/module-08-slides.md` "Light RTI recap": Eventstream, Eventhouse raw/enriched tables, "Activator — rule-based alerting on raw thresholds (Johan's half)" | Raw → enriched table pattern; Activator threshold rules | Lab 03 (update policy → `BusArrivalsEnriched`), Lab 05 |
| `lab-10` Part A–C: attendees copy an Eventstream **custom endpoint** connection string, use **Live view** and **Data preview**, read a `.create-or-alter materialized-view … arg_max` | Eventstream UI fluency; understanding an `arg_max` materialized view | Lab 02 (edit vs live view, data preview, operators, publish), Lab 03 Part D (attendees *author* an `arg_max` MV) |
| IQ's generator emits **flat** JSON (`FreezerId`, `TemperatureC`, …) straight into a typed table | Attendees know that real feeds rarely arrive that tidy | RTI's feed is the **raw TMB envelope**; Labs 02–03 teach flattening (Expand, `mv-expand`), so the afternoon's tidy events read as a convenience, not the norm |
| `10-theory`: update policies vs materialized views (in depth) | Attendees can follow the comparison | Module 03 theory covers the mechanics; Lab 03 has them build **one of each**, so Brian's comparison lands on things they've touched |
| `12-theory`: "Activator Ontology Rules … the same no-code event-detection engine from Johan's RTI session … emphasize the word *sustained*" | Attendees know Activator objects, conditions, actions, and why a sustained-duration condition matters | Lab 05 rule 1 uses **"When it has been true for 5 minutes"** explicitly so the afternoon's identical "sustained 5 minutes" on the ontology rule is a callback, not a new idea |
| `lab-12` step 13: Teams *or* email action | Attendees have sent an Activator notification before | Lab 05 uses email by default, Teams optional |

## B. What RTI deliberately does **not** cover (IQ owns it)

- Ontology, Graph, GQL, entity/relationship modelling, data binding (IQ Module 11).
- Data Agent, Operations Agent, ontology rules (IQ Module 12). RTI mentions Operations Agent in one theory
  bullet as "this afternoon" and nothing more.
- Prompting/trust/traceability (IQ Module 13).
- The cold-chain scenario, `ColdChain*`/`Freezer*` names, the `Fabric IQ` workspace, the `fab` CLI, Python
  venvs, the telemetry generator. RTI is portal-only and uses the `RTI Transit` workspace, so nothing RTI
  creates is touched by `provision_fabric_iq.py` and vice versa.
- Lakehouse reference tables loaded by a notebook as the golden path (IQ Lab 08 step 9 owns that). RTI's
  notebook (`LoadStopsReference`) exists only as the *target* of an OneLake-event-triggered run.
- Eventstream **custom endpoint** source (IQ Lab 10 Part A). RTI uses the **Azure Event Hubs** source so
  attendees see both connector shapes across the day.
- Digital Twin Builder. IQ's SESSION_MEMORY cites Microsoft's DTB bus tutorial as a *pattern reference*; RTI
  stays away from the DTB item entirely to avoid "which twin/ontology thing is this?" confusion.

## C. Deliberate overlaps (same technique, different data, on purpose)

| Technique | RTI (morning) | IQ (afternoon) | Why it's fine |
|---|---|---|---|
| `arg_max(...) by <key>` materialized view | `BusNextArrivalLatest` — attendees author it | `FreezerTelemetryEnriched` — pre-provisioned, attendees read it | Learn by building, then recognise it |
| `lookup` enrichment against dimension tables | Update policy `EnrichBusArrivals()` (attendees author) | Inside the MV definition (read) | Same |
| Activator threshold + sustained duration | On a derived eventstream, plain fields | On an ontology entity property | Afternoon shows the "business language" upgrade of the same rule |
| Reference data as CSV → dimension table | Get data → Local file into KQL | `.set-or-replace … datatable` in script + notebook → Lakehouse | Different mechanisms, both worth seeing |

## D. Suggested edits to `FabricIQ/` (small, all wording)

1. **`slides/module-08-slides.md`, "Where this fits in the day"** says *"Same retail cold-chain data, same
   workspace — we're extending, not restarting."* This is not true: the morning uses Barcelona transit data in
   an `RTI Transit` workspace, and IQ provisions its own `Fabric IQ` workspace. Suggested: *"Same building
   blocks you used on live bus data this morning, now applied to freezer telemetry in a fresh workspace."*
   Same fix for the "Light RTI recap" slide, whose bullets describe `FreezerTelemetryEventstream` etc. as
   things attendees "already built" — they haven't; the script provisions them.
2. **`10-theory-telemetry-plus-semantic-context.md`, "Microsoft's own template for this pattern"** contrasts
   buses/bus stops (Microsoft's DTB tutorial) with freezers/stores. Since attendees will have *just* built a
   real bus/bus-stop pipeline, add one line: *"This is exactly the shape you built this morning: `BusArrivalsRaw`
   plus `StopsDim` → `BusArrivalsEnriched`."* It turns a borrowed example into a callback.
3. **`11-theory-ontology-design-essentials.md`, "Where we are in the story"** says Module 10 produced
   `FreezerTelemetryEnriched` via *"an update policy and a materialized view"*. IQ Lab 10 only has a
   materialized view. Either drop "an update policy and", or (better) say *"the update-policy / materialized-view
   pattern you built by hand this morning."*
4. **`08-theory-kickoff-and-scenario.md`, facilitator comment** suggests asking "who attended Johan's session
   live vs. is picking up mid-day". Keep it; RTI Module 07's wrap-up tells attendees to keep the `RTI Transit`
   workspace but **pause** its eventstreams so the IQ labs aren't starved of capacity. Brian may want to
   re-check that in his Module 08 Part B ("if your two morning eventstreams are still running, pause them").
5. **`prerequisites/PREREQUISITES.md` §1 (capacity)**: attendees are on shared **P1** capacities (F64-equivalent,
   not pausable) that carry both halves. Brian's text says "F2 SKU or higher (or P1+)", which P1 satisfies, but the
   real question is how many attendees share one P1 with two eventstreams each running in the morning and
   Ontology/Data Agent in the afternoon. Worth one sentence there, pointing at RTI Module 07's parking step.
6. **`12-theory-agent-patterns.md`** describes Operations Agent as *"the direct bridge from RTI to IQ … takes the
   live telemetry Eventstream/Eventhouse pattern you already know from Johan's session"*. Accurate; no change.
   RTI Module 07 seeds this with one sentence so the phrase lands.
7. **`.github/workflows/publish-attendee-labs.yml`** only publishes `FabricIQ/`. If the RTI half should also
   ship to an attendee repo, add a second job (or a second `safe_rsync` set) mirroring `RTI/` with the same
   `--exclude="*theory*"` filter. Not done here; it's a repo-owner decision (separate repo vs. same one).

## E. Things that are shared and must stay in sync

- **Capacity is the shared risk.** During the RTI dry run an attendee build on an **F16 shared with another workspace** hit throttling
  and Fabric paused the eventstream until it was resumed by hand. The shared P1 capacities carry Brian's Ontology and Data Agent in the afternoon,
  so one P1 needs a dry run with one full RTI build *and* the IQ provisioning on it, scaled by the number of
  attendees per capacity, and Module 07's parking step is not optional. Whoever talks to Microsoft about capacity should bring both halves'
  numbers.
- **Room size is 120.** The IQ half's Module 08 has everyone run `pip install` and `fab auth login` at once; with
  120 laptops on venue Wi-Fi that 40-minute block is the day's biggest network risk. Worth Brian knowing the count
  and considering a "pre-install over lunch" nudge; RTI's prerequisites already point attendees at his §1 for that.

- **Accounts and tenant**: both halves use the Microsoft-provided per-attendee account. RTI's prerequisites
  link to IQ's rather than duplicating them.
- **Break placement**: IQ has breaks at 1:50 and 3:25 into its half. RTI has breaks at 2:00 and 3:10. Lunch sits
  between the halves.
- **Lab template and conventions**: RTI labs follow `FabricIQ/docs/lab-guide-template.md` (bold verb + exact UI
  label, ✅ expected result, collapsible troubleshooting, *Adapted from* attribution, `<!-- facilitator -->`
  comments, checkpoint + next link) so an attendee sees one consistent handout all day.
- **Screenshot path convention**: `assets/screenshots/lab-XX/step-NN.png`, placeholders until captured.

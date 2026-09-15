# Facilitator Guide

Presenter-only notes: room setup, timing cues, and what to say if something breaks. Not part of the
attendee-facing handout.

## Format decisions worth knowing

- **No separate slide-deck source of truth.** Theory content lives as structured markdown outlines
  (talking points + case studies + discussion prompts) in each module's `theory-XX-*.md` — that's the
  durable, attendee-facing reference they keep for later. The `slides/module-XX-slides.md` decks are a
  **condensed** presentation layer built from that same content, not a duplicate of its full prose;
  present from the slides, but the markdown is what you'd point an attendee back to afterward.
- **Facilitator asides live inside the lab files themselves**, marked with HTML comments
  (`<!-- facilitator: ... -->`, invisible on GitHub) or a visible `> 🎤 Facilitator note:` blockquote —
  not a separate synced document. If you add a tip mid-workshop, put it directly in the lab file so it
  doesn't drift out of sync.

## Slides

The 7 decks under `slides/` are built onto the conference's own branded PowerPoint template
(`slides/template/*.pptx`) via MarpToPptx, producing real editable `.pptx` files, not slide images —
see [`../slides/README.md`](../slides/README.md) for the build command and the layout cheat-sheet.
Two things worth knowing before presenting: layout differences between the template's 12 slide
layouts were verified empirically by inspecting rendered output rather than by reading a spec (the
template gives no static guarantee two layouts look different), so if the template file is ever
replaced, re-verify before trusting the existing layout assignments; and **each deck's title slide
needs a one-time manual fill-in** in PowerPoint (your name/title/company) after running
`build-slides.sh` — the build can't populate those boxes from markdown, see the slides README's "After
generating" section.

## Session order assumption

This section runs **after** Johan's Real-Time Intelligence half. Module 00/01 assume attendees already
know Eventstream/Eventhouse/Activator at a basic level and give only a light recap. If the running order
ever changes, Module 01's theory needs real RTI-fundamentals content added — flag this to whoever edits
the agenda if the day's order shifts.

## Timing cues

See [`agenda.md`](agenda.md) for the full table. Two built-in flex points:

- **Module 00 (40 min)** now assumes most of the room is provisioning live for the first time, not
  verifying pre-done work — attendees are no longer expected to have run the setup script before
  arriving. Budget it as real hands-on setup time, and protect it from running over: it took 20 minutes
  from Module 05's buffer to make room in the agenda, so there's less slack downstream than there used to
  be. Anyone who *did* pre-run the script skips to Part B of the lab and finishes early — point them
  ahead to Module 01's reading, or have them help a neighbor, rather than let the room wait idle.
- **Module 05 is the buffer** — now only 15 minutes to start with. If Module 03 or 04 (both touch preview
  UI) run long, compress Module 05's lab to a facilitator-led walkthrough with less hands-on time — do
  not cut Module 03/04 short, since ontology design and agent patterns are this section's core learning
  objectives.

## If something breaks live

See [`risk-fallback-plan.md`](risk-fallback-plan.md) for the per-module risk table and fallback
narration scripts. In short: Module 03 (Ontology) and Module 04 (Data Agent/Operations Agent) are the
highest-risk, preview-UI-dependent labs — have the screenshot fallback sequences open in a browser tab
before the session starts, just in case.

## Room logistics

- Confirm venue wifi can handle the room streaming to Fabric simultaneously; there's no offline mode.
- Keep one already-provisioned "instructor" workspace ready to screen-share as a fallback for any
  attendee whose own setup script failed and can't be fixed in the room.

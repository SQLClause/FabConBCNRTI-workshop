# Lab Guide Template

Every `lab-XX-*.md` in `modules/` follows this skeleton. Copy it as a starting point for new labs, and
keep existing labs consistent with it when editing.

---

```markdown
# Lab XX: <Title>

**Duration:** <NN> minutes
**Prerequisites:** <which prior labs/modules must be complete, and what must exist in the workspace>

**Learning objectives**
- <objective 1>
- <objective 2>

## Before you begin

Confirm your environment matches this state before starting:
- [ ] <expected item 1, e.g. "Fabric IQ" workspace exists>
- [ ] <expected item 2, e.g. ColdChainLakehouse contains Customers/Stores/Freezers tables>

## Steps

1. **Click** the **+ New item** button in the top-left of the workspace.

   ![Step 1](../../assets/screenshots/lab-XX/step-01.png)

   > ✅ Expected result: the "New item" panel opens.

2. **Type** `<exact value>` in the Name field, then **click** **Create**.

   <details>
   <summary>Troubleshooting</summary>

   If the item type is greyed out, the tenant setting enabling it may not be turned on for your
   tenant — see `prerequisites/PREREQUISITES.md`.
   </details>

   *Adapted from: [Tutorial name, Steps N–M](https://learn.microsoft.com/...)*

<!-- facilitator: mention that this step is where attendees most often get stuck; walk the room -->

> 🎤 Facilitator note: pause here and ask who's seeing something different before moving on.

## Checkpoint

At the end of this lab, your workspace should contain:
- <item 1>
- <item 2>

Continue to [Module XX+1](../module-XX-next/theory-XX-next.md).
```

---

## Conventions

- **Numbered steps** written as bold action verb + exact UI label in backticks/quotes:
  `**Click** the **+ New item** button`, `**Type** \`ColdChainOntology\` in the Name field`.
- **Screenshot placeholders** always follow the path convention
  `../../assets/screenshots/lab-XX/step-NN.png` with descriptive alt text. Image capture happens
  separately from writing the lab text — leave the placeholder even if the image doesn't exist yet.
- **Expected-result callouts** after key steps: `> ✅ Expected result: ...`
- **Troubleshooting notes** as collapsible blocks tied to a known failure point, most often "preview
  feature greyed out → tenant setting not enabled" or "item import failed → re-run setup script."
- **Source attribution** after every step group that adapts an official Microsoft tutorial:
  `*Adapted from: [Tutorial title, Steps N–M](url)*`. Every lab must trace back to which official
  tutorial(s) it's adapting — this is what keeps the workshop "fool proof" instead of running on
  untested, presenter-invented click paths.
- **Facilitator-only asides** use HTML comments (`<!-- facilitator: ... -->`) so they're invisible when
  the file renders as a plain attendee handout on GitHub. Optional talking points worth showing
  attendees too use a visible `> 🎤 Facilitator note:` blockquote instead.
- **End-of-lab checkpoint**: a short summary of what now exists in the workspace, and an explicit link
  to the next module — this is what lets an attendee (or the facilitator, mid-session) confirm they're
  in the right state before moving on.

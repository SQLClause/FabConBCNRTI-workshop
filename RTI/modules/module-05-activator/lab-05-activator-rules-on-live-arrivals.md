# Lab 05: Activator Rules on Live Arrivals

**Duration:** 23 minutes
**Prerequisites:** Module 02 complete: `BusArrivalsEventstream` is published with the derived stream
`ForumArrivals` (your venue stop only). You know your own email address on the event account (and whether
Teams is available; the facilitator says so).

**Learning objectives**
- Add an Activator destination to a derived stream and create the `TransitAlerts` item.
- Create a **sustained threshold** rule per object (`LineCode`) with a property filter.
- Create a **heartbeat** rule that fires when a stop goes silent.
- Test a rule against history, start it, and read its **Analytics**.
- Optional: create a **stateful** (change) rule and compare its firing behaviour.

## Before you begin

- [ ] `BusArrivalsEventstream` → Live view → `ForumArrivals` → **Data preview** shows events (all with your
      venue `StopCode`, several `LineCode` values, `Rank` 1 and 2).
- [ ] If the derived stream doesn't exist (you skipped Lab 02 step 21–22), add it now: Edit → `+` on
      `ShapeBusArrivals` → Filter `StopCode equals <VENUE_STOP_CODE>` → `+` → Stream `ForumArrivals` → Publish.

## Steps

### Part A — Attach Activator to the derived stream

1. **Open** `BusArrivalsEventstream` and **click** **Edit**.

2. **Hover** over the **ForumArrivals** derived-stream node, **click** **+**, **select** **Activator**.

3. In the **Activator** pane: **Destination name** `TransitAlertsDest`, **Workspace** `RTI Transit`,
   **Activator** → **Create new** → `TransitAlerts`. **Click** **Save**, then **Publish**.

   ![Step 3](../../assets/screenshots/lab-05/step-01.png)

   > ✅ Expected result: Live view shows `ForumArrivals → TransitAlertsDest`. The node carries a bell/alert icon.

   *Adapted from: [Add a Fabric Activator destination to an eventstream](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-activator)*

### Part B — Rule 1: `Long wait at the Fòrum` (sustained threshold, per line)

4. **Click** the alert icon on **TransitAlertsDest**. The **Rules** pane opens (empty). **Click** **…** →
   **Open in Activator** so you get the full editor (the in-pane form is fine for simple rules, but we want a
   property filter and an occurrence).

5. In the Activator editor's **Explorer**, **select** the **ForumArrivals** stream and **click** **New rule** (ribbon).

6. In the **Definition** pane:
   - **Rule name**: `Long wait at the Fòrum`
   - **Monitor**: **Check** → **On each event grouped by a field**; **Group by** `LineCode`; **field to check**
     `MinutesToArrival`
   - **Condition**: **Is greater than** → `12`
   - **Occurrence**: **When it has been true for** → `3` **minutes**
   - **Property filter** → **+ Add filter**: **Attribute** `Rank`, **Operation** **Is equal to**, **Value** `1`

   ![Step 6](../../assets/screenshots/lab-05/step-02.png)

   > ✅ Expected result: the **Definition** tab's preview chart shows `MinutesToArrival` per line over the last
   > while, with the 12-minute threshold drawn. You can already see whether any line has been above it.

   <details>
   <summary>Troubleshooting — I don't see "grouped by a field" / the object choice</summary>

   Older Activator editors ask you to create an **object** first: select the stream → **New object** → **Object
   ID** `LineCode`, **Properties** `MinutesToArrival`, `Rank`, `Destination`, `StopCode` → **Create**. Then create
   the rule on the `MinutesToArrival` property of that object. Same result: one state per line.
   </details>

   *Adapted from: [Detection settings in Activator](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-detection-conditions)*

7. **Action**: **Select action** → **Email** (or **Teams → Message to individuals** if the facilitator
   confirmed Teams works).
   - **To**: your event-account email
   - **Subject**: `Long wait for line @LineCode at the Fòrum`
   - **Headline**: `@LineCode to @Destination: next bus in @MinutesToArrival min`
   - **Context**: add `StopCode`, `Destination`, `PolledAtUtc`

   > ✅ Expected result: typing `@` offers the event's fields; the preview under **Edit action** renders the
   > message with real values.

8. **Click** **Save**, then **Send me a test alert**.

   > ✅ Expected result: an email arrives within a minute, built from a *past* event that satisfied the rule.
   > If the button is disabled, no line has been over 12 minutes for 3 minutes yet; carry on, start the rule,
   > and check back after the break.

9. **Click** **Start**.

   > ✅ Expected result: the rule card shows **Running**. From now on, each *line* at the venue stop is tracked
   > independently; a line whose next bus stays more than 12 minutes away for three minutes triggers one
   > message, and won't message again until it recovers and re-enters the state.

   *Adapted from: [Create Activator rules](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-create-activators)*

<!-- facilitator: this is the "sustained" moment. Ask: what would happen with "Every time the condition is met" instead? Answer: one email every 30 s for every late line. -->

### Part C — Rule 2: `Stop went silent` (heartbeat)

10. **Select** the **ForumArrivals** stream again, **click** **New rule**.
    - **Rule name**: `Stop went silent`
    - **Monitor**: grouped by `LineCode`
    - **Condition**: category **Heartbeat** → **No presence of data**; **duration** `10` **minutes**
    - **Action**: **Email**, **Subject** `No arrival data for line @LineCode at the Fòrum for 10 minutes`,
      **Headline** `Check the feed (Function / Event Hubs) before blaming TMB.`
    - **Save**, **Start**.

    > ✅ Expected result: **Running**. This rule fires when the *feed* stops for a line at the venue stop for ten
    > minutes: the Function is down, Event Hubs is unreachable, or TMB has been failing for that stop on every
    > poll. Ten minutes is far longer than any real headway on these lines, so silence means the pipeline broke,
    > not the buses. (If the facilitator pauses the feed during the break, everyone's inbox proves it.)

### Part D — Optional: Rule 3 `Bus arriving now` (stateful change)

11. **New rule** on **ForumArrivals**: name `Bus arriving now`; grouped by `LineCode`; condition category
    **Numeric change** → **Decreases below** → `2`; property filter `Rank` **Is equal to** `1`; action Teams
    or email, headline `@LineCode is arriving at the Fòrum now`. **Save**, **Start**.

    > ✅ Expected result: this one fires once per line each time the prediction *crosses* below 2 minutes, not
    > on every event under 2 minutes. Compare with rule 1's model: **change** conditions are inherently
    > stateful; **state** conditions need an occurrence to avoid repeats.

### Part E — Read the analytics

12. **Select** `Long wait at the Fòrum` and **click** the **Analytics** tab.

    ![Step 12](../../assets/screenshots/lab-05/step-03.png)

    > ✅ Expected result: two charts: total activations over time, and activations by the top object IDs
    > (lines). Even before anything fired live, the **Definition** chart shows how often the rule *would have*
    > fired on the history the stream has already delivered.

13. **Go back** to `BusArrivalsEventstream` (Live view) and **click** the alert icon on `TransitAlertsDest`.

    > ✅ Expected result: the **Rules** pane lists all your rules with start/stop toggles. This is where Module
    > 07 stops them before lunch.

> 🎤 Facilitator note: keep your own `Long wait` email from the dry run ready to show. Real data may be
> perfectly punctual for the 25 minutes this lab runs, and that's a fine teaching point too.

<!-- facilitator: check three things for anyone whose rule "does nothing": object/group-by is LineCode, the Rank filter exists, and the rule is started. Then Send me a test alert. -->

## Checkpoint

At the end of this lab, your workspace contains Activator item **`TransitAlerts`**, fed by the `ForumArrivals`
derived stream, with:
- `Long wait at the Fòrum` — **Is greater than 12**, **true for 3 minutes**, filter `Rank == 1`, grouped by `LineCode`, **Running**
- `Stop went silent` — **No presence of data** for 10 minutes, grouped by `LineCode`, **Running**
- optionally `Bus arriving now` — **Decreases below 2**, **Running**

You've turned a stream into a per-line state machine with actions. Take the break, then continue to
[Module 06: Event-driven beyond telemetry](../module-06-fabric-events/lab-06-onelake-events-trigger-automation.md).

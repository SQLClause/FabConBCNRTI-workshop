# Lab 04: Activator Rules

**Duration:** 20 minutes
**Prerequisites:** Lab 01 complete (`BikeEventstream` published), and the **neighbourhood name** you picked at the
end of Lab 02. Your email address (or Teams) on this account.

**Learning objectives**
- Send a stream to **Activator** as an Eventstream destination.
- Model the stream as **objects** (one per station) with **properties**.
- Build a **change** rule (fires on the crossing) and a **sustained state** rule (fires after 5 minutes).
- Narrow rules with a **filter** so alerts stay relevant and few.
- Test, start and read a rule's history.

## Before you begin

- [ ] You have your neighbourhood name copied exactly (capitals and spaces matter).
- [ ] You understand why the filter matters: the sample covers a whole city. A rule without a filter emails you
      every time *any* station anywhere runs empty.

## Steps

### Part A — Send the stream to Activator (4 min)

1. **Open** `BikeEventstream` and **click** **Edit**.

2. **Point** at the right edge of the `AddTimestamp` tile, **click** the green **+**, then **Destinations** →
   **Activator**. **Click** the pencil on the new tile:
   - **Destination name**: `BikeAlertsDest`
   - **Workspace**: your workspace
   - **Activator**: **Create new** → `BikeAlerts`
   - **Input data format**: **Json** (if asked)
   - **Click** **Save**, then **Publish**.

   > ✅ Expected result: Live view shows `AddTimestamp` with two destinations, `BikesRawDest` and
   > `BikeAlertsDest`. The same events now feed storage and detection in parallel.

   <details>
   <summary>Troubleshooting — the + on AddTimestamp doesn't offer Activator</summary>

   Add it from the `BikeEventstream-stream` node instead (hover, **+**, **Activator**). You lose the `Timestamp`
   column in Activator, which doesn't affect these rules: Activator stamps events on arrival.
   </details>

   *Adapted from: [Add an Activator destination to an eventstream](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-activator)*

### Part B — One object per station (3 min)

3. **Open** `BikeAlerts` from your workspace. In the **Explorer** on the left, **select** the stream event
   (named after your eventstream). **Wait** until its preview shows rows.

4. **Click** **New object** on the ribbon. In the pane:
   - **Object name**: `Station`
   - **Object ID** (the field that identifies one instance): `BikepointID`
   - **Properties**: `No_Bikes`, `No_Empty_Docks`, `Street`, `Neighbourhood`
   - **Click** **Create**.

   > ✅ Expected result: `Station` appears in the Explorer with four properties underneath. From now on every
   > rule on this object is evaluated **separately per station**: one station recovering doesn't hide another
   > that's still empty.

   *Adapted from: [Assign data to objects in Activator](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-assign-data-objects)*

### Part C — Rule 1: `Station ran out of bikes` (change rule) (6 min)

5. **Select** the **`No_Bikes`** property under `Station` and **click** **New rule** (ribbon). In the
   **Definition** pane:
   - **Rule name**: `Station ran out of bikes`
   - **Monitor**: already `No_Bikes` of `Station`
   - **Condition**: category **Numeric change** → **Decreases below** → `1`
   - **Filter** (add one): **Attribute** `Neighbourhood`, **Operation** **Is equal to**, **Value** *your
     neighbourhood*

   > ✅ Expected result: the preview chart above the definition shows `No_Bikes` for a sample of stations, with
   > markers where the rule *would have* fired. With the filter set, only your neighbourhood's stations count.

6. **Action** → **Select action** → **Email** (or **Teams** → **Message to individuals**):
   - **To**: your own address
   - **Subject**: `@Street ran out of bikes`
   - **Headline**: `@Street in @Neighbourhood has no bikes`
   - **Context**: add `No_Empty_Docks`

   > 💡 Typing `@` offers the object's properties. The message is built per station, from that station's values.

7. **Click** **Save**, then **Send me a test alert**, then **Start**.

   > ✅ Expected result: a test message arrives within a minute, and the rule card shows **Running**. A **change**
   > rule fires once when a station *crosses* from 1+ bikes to 0, not on every event while it stays at 0.

   *Adapted from: [Detection settings in Activator](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-detection-conditions)*

### Part D — Rule 2: `Empty for 5 minutes` (sustained state) (4 min)

8. **Select** `No_Bikes` under `Station` again, **click** **New rule**:
   - **Rule name**: `Empty for 5 minutes`
   - **Condition**: category **Numeric state** → **Is less than** → `1`
   - **Occurrence**: **When it has been true for** → `5` **minutes**
   - **Filter**: same as rule 1 (`Neighbourhood` **Is equal to** *your neighbourhood*)
   - **Action**: **Email** to yourself, **Subject** `@Street has been empty for 5 minutes`, **Headline**
     `Send a crew to @Street (@Neighbourhood)`
   - **Save**, **Start**.

   > ✅ Expected result: **Running**. Compare the two rules out loud with your neighbour: rule 1 tells you the
   > moment something happens; rule 2 ignores stations that are refilled within 5 minutes and only escalates
   > the ones that stay empty. Most real alerting wants rule 2.

### Part E — Read the history (3 min)

9. **Select** `Station ran out of bikes` and **open** the **Analytics** tab.

   > ✅ Expected result: activations over time and the top stations (object IDs) that triggered it. If nothing
   > has fired yet, the **Definition** chart still shows where it *would have* fired on recent data.

10. *(stretch)* **New rule** on `Station`: `Station went quiet`, condition **Heartbeat** → **No presence of data**,
    `10` minutes, same filter, email action. It fires if a station stops reporting at all: a broken sensor, or a
    broken pipeline.

<details>
<summary>Troubleshooting — the rule "does nothing"</summary>

1. The rule isn't started: the card must say **Running**.
2. The filter value doesn't match exactly. Copy it again from `NeighbourhoodNow()` output.
3. The object ID is `BikepointID`, not `Neighbourhood`: with the wrong ID, the whole neighbourhood is one object.
4. Your eventstream is paused (throttled capacity). Open it and resume.
</details>

## Checkpoint

At the end of this lab, your workspace contains Activator item **`BikeAlerts`**, fed by `BikeAlertsDest`, with
object **`Station`** (ID `BikepointID`) and:
- `Station ran out of bikes`: **Decreases below 1**, filtered to your neighbourhood, **Running**
- `Empty for 5 minutes`: **Is less than 1**, **true for 5 minutes**, same filter, **Running**

Rules keep running after the session. Stop them when you're done (see [Clean up](../README.md#clean-up-after-the-session)).

Continue to [Lab 05: Event-driven automation](lab-05-onelake-event-automation.md).

# Lab 01: Create the Workspace and Explore Real-Time Hub

**Duration:** 10 minutes (Parts A–C are the work; Part D is a two-minute look around)
**Prerequisites:** You are signed in to [app.fabric.microsoft.com](https://app.fabric.microsoft.com) with the
Microsoft-provided account for this event, and that account can create workspaces on a Fabric capacity (see
[`prerequisites/PREREQUISITES.md`](../../prerequisites/PREREQUISITES.md)).

**Learning objectives**
- Create the `RTI Transit` workspace on a Fabric capacity.
- Create the two containers every later lab uses: `TransitEventhouse` and `TransitLakehouse`.
- Find your way around Real-Time hub: data streams, Fabric events, and the connector gallery.

## Before you begin

- [ ] You can open [app.fabric.microsoft.com](https://app.fabric.microsoft.com) and see the Fabric home page.
- [ ] If the bottom-left of the navigation shows **Power BI**, click it and switch to **Fabric**.

## Steps

### Part A — Create the workspace

1. **Click** **Workspaces** in the left navigation, then **click** **+ New workspace**.

   ![Step 1](../../assets/screenshots/lab-01/step-01.png)

2. **Type** `RTI Transit` in the **Name** field.

3. **Expand** **Advanced**, and under **License mode** **confirm** a **Fabric capacity** (or **Trial**) is
   selected, not **Pro**. If a **Capacity** dropdown appears, **select** the capacity assigned to you.

   > ✅ Expected result: the license mode shows a Fabric or Trial capacity. Every item in this workshop needs
   > one; Pro workspaces can't hold Eventstreams or Eventhouses.

   <details>
   <summary>Troubleshooting — no Fabric or Trial option</summary>

   Your account hasn't been given a capacity. This can't be fixed in the room. Flag a facilitator and pair
   with a neighbour for now; you'll follow along on their screen and sort out access at the break.
   </details>

4. **Click** **Apply**.

   > ✅ Expected result: an empty workspace named **RTI Transit** opens.

   *Adapted from: [Create a workspace](https://learn.microsoft.com/fabric/fundamentals/create-workspaces)*

### Part B — Create the Eventhouse

5. **Click** **+ New item**, **type** `Eventhouse` in the search box, and **select** **Eventhouse**.

6. **Type** `TransitEventhouse` as the name and **click** **Create**.

   ![Step 6](../../assets/screenshots/lab-01/step-02.png)

   > ✅ Expected result: the Eventhouse opens on its **System overview** page. In the left **Explorer** pane you
   > see one KQL database, also named **TransitEventhouse**. Fabric always creates one default database with
   > the Eventhouse's own name; that's the database we use all morning.

7. **Click** the **TransitEventhouse** database in the Explorer pane.

   > ✅ Expected result: the database page opens with a **Get data** button on the ribbon and an empty
   > **Tables** node. Nothing to do here yet; Module 02 fills it.

   *Adapted from: [Create an eventhouse](https://learn.microsoft.com/fabric/real-time-intelligence/create-eventhouse)*

### Part C — Create the Lakehouse

8. **Go back** to the **RTI Transit** workspace (click its name in the breadcrumb or left navigation).

9. **Click** **+ New item**, **type** `Lakehouse`, **select** **Lakehouse**, **type** `TransitLakehouse`, and
   **click** **Create**. Leave any "Lakehouse schemas" option at its default.

   > ✅ Expected result: an empty Lakehouse opens showing **Tables** and **Files** nodes.

10. **Click** the **…** next to **Files**, **select** **New subfolder**, **type** `reference`, and **click**
    **Create**.

    > ✅ Expected result: `Files/reference` exists and is empty. Module 06 drops a file here to trigger
    > automation; leave it empty until then.

### Part D — Tour Real-Time hub

11. **Click** **Real-Time** in the left navigation.

    ![Step 11](../../assets/screenshots/lab-01/step-03.png)

    > ✅ Expected result: Real-Time hub opens. The left rail shows **All data streams**, **My data streams**,
    > **Fabric events**, **Azure events**, and the **Connect to data source** entry point.

12. **Click** **All data streams**.

    > ✅ Expected result: probably empty for you right now (no eventstream exists yet). By Module 03 it lists
    > your eventstream outputs *and* your KQL tables. This page is tenant-wide, filtered to what you can access.

13. **Click** **Fabric events**.

    > ✅ Expected result: a list including **OneLake events**, **Job events**, **Workspace item events** and
    > capacity events. **Hover** over **OneLake events** and notice the **Set alert** button. Module 06 uses it.

14. **Click** **+ Connect to data source** (top right) and **scroll** the gallery. **Find** **Azure Event Hubs**,
    **Sample data**, **HTTP**, **Fabric OneLake events**. **Close** the dialog without connecting anything.

    > ✅ Expected result: you've seen where every source connector lives. In Module 02 we use **Azure Event
    > Hubs** from inside an eventstream, and in Part D of that lab we use this same hub entry point instead, to
    > see that both roads lead to an Eventstream item.

    *Adapted from: [Real-Time hub overview](https://learn.microsoft.com/fabric/real-time-hub/real-time-hub-overview)*

> 🎤 Facilitator note: while people finish, hand out the consumer-group sheet and put the namespace + key on the
> screen. Module 02 starts by typing them.

<!-- facilitator: the most common failure here is the workspace ending up in Pro license mode because Advanced was collapsed. Check the workspace settings of anyone whose "+ New item" gallery lacks Eventhouse. -->

## Checkpoint

At the end of this lab, your **RTI Transit** workspace should contain:
- `TransitEventhouse` (Eventhouse) with its default KQL database `TransitEventhouse`, no tables yet
- `TransitLakehouse` (Lakehouse) with an empty `Files/reference` folder
- (auto-created alongside the Lakehouse: a SQL analytics endpoint and a default semantic model; ignore them)

You have also seen Real-Time hub's three lists (data streams, Fabric events, Azure events) and the connector
gallery. Continue to [Module 02: Eventstream](../module-02-eventstream/lab-02-build-the-transit-eventstream.md).

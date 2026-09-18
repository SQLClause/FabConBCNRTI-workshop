# Pre-Event Prerequisites — RTI half

**Microsoft is providing the Fabric tenant/capacity and a dedicated user account for every attendee at this
event** (the same account is used for the Fabric IQ half in the afternoon; see
[`../../FabricIQ/prerequisites/PREREQUISITES.md`](../../FabricIQ/prerequisites/PREREQUISITES.md)). Nothing in the RTI half
needs a tenant-admin action beyond what that checklist already covers.

## 1. Attendees

- [ ] A laptop with a current browser (Edge or Chrome). **Nothing to install** for the morning. The afternoon's
      Fabric IQ half installs Git and Python live in its Module 00; if you want to get ahead, follow
      [`../../FabricIQ/prerequisites/PREREQUISITES.md`](../../FabricIQ/prerequisites/PREREQUISITES.md) §4 during the lunch break.
- [ ] Your Microsoft-provided sign-in for this event.
- [ ] Optional: the Microsoft Teams app signed in with the same account, if the event accounts have Teams
      licences (the facilitator confirms this on the day). Every Activator lab step offers **email** as the
      default action so Teams is never required.

## 2. Confirm with Microsoft ahead of time (presenter action, 2+ weeks lead time)

- [ ] Each attendee has **Contributor or higher on a workspace they can create**, on a Fabric capacity
      (F2 or higher, or trial). All RTI items used here (Eventstream, Eventhouse, Activator, Real-Time
      Dashboard, Lakehouse, Notebook, Data pipeline) work on trial and F2 capacities. Only the *afternoon's*
      Ontology/Data Agent items need a non-trial capacity, so the same F2+ capacity the IQ half requires is
      fine for both halves.
- [ ] Tenant settings: **Users can create Fabric items** (on), **Fabric Activator** (on), **Real-Time Hub**
      visible, **OneLake events** / **Fabric events** allowed (these are on by default in most tenants but a
      locked-down event tenant may have them off).
- [ ] Capacity headroom: each attendee runs two Eventstreams, one Eventhouse, one Activator and one Real-Time
      Dashboard with live refresh for ~3 hours, on the **same** per-attendee capacity the afternoon needs for
      Ontology + Data Agent. Module 07's "park your workspace" step pauses the streams before lunch precisely
      so the afternoon isn't throttled. If Microsoft assigns one *shared* capacity for the room instead of one
      per attendee, ask for at least an F64 for the day.

## 3. Presenter-owned infrastructure (must be running before the session)

- [ ] Azure Function (`RTIBCN/`) polling TMB and publishing raw envelopes to Event Hubs per
      [`../docs/data-feed-contract.md`](../docs/data-feed-contract.md), scheduled to run from ~07:30 to ~14:00
      local time on the day (plus the dry run).
- [ ] Event Hubs namespace (Premium) with `tmb-ibus-1-65`, `tmb-ibus-66-130`, `tmb-metro-1-65`, `tmb-metro-66-130`
      and consumer groups `user-001`…`user-130` (`RTIBCN/setup_event_hubs.sh`), plus the listen-only SAS policy
      and seat sheet from [`../infra/prepare-room.sh`](../infra/prepare-room.sh).
- [ ] A printed seat sheet (`infra/out/seat-sheet.csv`) and a projected slide with the namespace name and the
      listen-only key name + key. Each attendee needs their row: consumer group and the two hub names.
- [ ] Two helpers for a room of 120, briefed on the two most common fixes (consumer group / hub name in Lab 02,
      the nested field picker in Lab 02 step 17).
- [ ] TMB developer account with an application registered (app_id/app_key) and its **plan rate limits
      confirmed** against the polling schedule in the data-feed contract.
- [ ] A recorded JSONL sample of at least 60 minutes of real events (from the dry run) for
      [`../infra/replay_events.py`](../infra/replay_events.py), so the labs run identically if TMB or the Function
      is unavailable on the day.

## 4. Network caveat

Attendees only talk to `app.fabric.microsoft.com`. Event Hubs traffic is cloud-to-cloud (Fabric ↔ Azure), so venue
network restrictions don't affect ingestion. If the venue blocks Teams, use the email action in Module 05.

## Support contact

Questions on any of the above: contact Johan ahead of the event.

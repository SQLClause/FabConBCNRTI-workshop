# Pre-Workshop Prerequisites

**Several items below cannot be fixed live during the workshop.** Please complete this checklist at
least two weeks before the event, and send it to your Fabric tenant admin if you are not one yourself.

## 1. Tenant admin actions (2+ weeks lead time)

Fabric IQ's Ontology and Graph items are still **(preview)** as of this writing and require explicit
tenant-level enablement — they will simply not appear as an option in the UI otherwise.

- [ ] Enable the **"Ontology item (preview)"** tenant setting.
      See [Ontology required tenant settings](https://learn.microsoft.com/fabric/iq/ontology/overview-tenant-settings).
- [ ] Enable the Azure OpenAI / Copilot tenant settings required for **Fabric Data Agent**.
- [ ] Confirm the capacity attendees will use is **F2 SKU or higher** (or **P1+** for Premium-based
      capacities) — see [capacity consumption for ontology (preview)](https://learn.microsoft.com/fabric/iq/ontology/resources-capacity-usage).
- [ ] **Confirm the capacity is NOT a Fabric trial capacity.** Ontology, Graph, and Data Agent features
      are not supported on trial (FT1) capacities — attendees who default to a personal trial capacity
      will hit a wall mid-workshop with no live fix available. This is the single most common failure
      mode for this session; call it out explicitly to attendees ahead of time.

## 2. Attendee capacity/workspace permissions

- [ ] Contributor (or higher) role on an eligible, non-trial Fabric capacity.
- [ ] Workspace-creation rights in your tenant (the provisioning script creates a new workspace named
      "Fabric IQ").

## 3. Attendee software installs

- [ ] **Python 3.10–3.13** (`python3 --version`)
- [ ] **Fabric CLI**: `pip install ms-fabric-cli`, then confirm with `fab --version`
- [ ] **git**
- [ ] `pip install -r setup/requirements.txt` (installs `ms-fabric-cli`, `pyyaml`, and `azure-eventhub` —
      the last one is needed for Module 02's telemetry generator script, not for the setup script itself)
- [ ] A modern browser, signed in with the account that has the permissions above

## 4. Network caveats

- [ ] If you're on a corporate VPN or proxy, test that `fab auth login`'s browser/device-code flow and
      `git clone` both succeed **before** the day — some corporate networks block one or both.

## 5. Run this before you arrive

1. Clone this repository: `git clone <repo-url>`
2. Follow [`setup/README.md`](../setup/README.md) to run `provision_fabric_iq.py`.
3. Confirm the script reports a "Fabric IQ" workspace containing:
   - `ColdChainLakehouse` (Lakehouse)
   - `ColdChainEventhouse` (Eventhouse, with the `ColdChainKQLDB` KQL database)
   - `FreezerTelemetryEventstream` (Eventstream)
   - `00_LoadReferenceData` (Notebook)

   If any item is missing or the script errors out, see the troubleshooting section in
   [`setup/README.md`](../setup/README.md) — and if you're still stuck, reach out **before** the
   workshop day using the contact below, not during the session.

## Support contact

Questions or issues with any of the above: contact Brian ahead of the event — problems caught a week
out are a five-minute fix; problems discovered live in the room are not.

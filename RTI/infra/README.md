# Presenter infrastructure (RTI half)

Attendees never touch any of this. It exists so **120 people** can each build their own eventstream over one live feed.

```
 TMB iBus / iTransit metro ──► Azure Function RTIBCN/ (timers, 30 s / 60 s)
                                     │ publishes every event to BOTH hubs of a feed (two output bindings)
                                     ▼
                     Event Hubs namespace <prefix>-fabcon-ehns (Premium, 1 PU)
                       ├─ tmb-ibus-a   (4 partitions, consumer groups attendee-001..065)
                       ├─ tmb-ibus-b   (4 partitions, consumer groups attendee-066..130)
                       ├─ tmb-metro-a  (2 partitions, attendee-001..065)
                       └─ tmb-metro-b  (2 partitions, attendee-066..130)
                                     │  listen-only SAS "attendee-listen"
                                     ▼
                     each attendee's BusArrivalsEventstream / MetroArrivalsEventstream
```

## Why two hubs per feed

Every attendee eventstream needs its **own consumer group** (two readers on one group fight over partitions). A
hub allows a fixed number of consumer groups, so the room size decides the hub count:

| Tier | Consumer groups / hub | Hubs per feed for 120 + 10 spare | Notes |
|---|---|---|---|
| Standard | 20 | 7 | Seven output bindings per function, seven-way seat sheet. No. |
| **Premium (1 PU)** | 100 | **2** | **Used.** One namespace, `-a`/`-b` per feed, two output bindings in the Function. 1 PU handles thousands of connections; 130 readers × 4 partitions is far below it. Pay for the day; delete after. |
| Dedicated (1 CU) | 1,000 | 1 | Simplest topology, but ~10× the cost and a provisioning lead time. Not worth it for one morning. |

Each attendee is assigned a **letter**; their consumer group exists only on that letter's hubs. Attendees 1–65 → `a`,
66–130 → `b` (`infra/out/consumer-groups.csv`). Both halves see identical data because the Function publishes each
flat event to both hubs.

## 1. Resolve stop and station codes (once, before the dry run)

```bash
pip install requests
export TMB_APP_ID=... TMB_APP_KEY=...          # from https://developer.tmb.cat/
python3 infra/resolve_stops.py                 # writes artifacts/SampleData/{stops,lines,metro_stations}.csv
```

The script prints the property names it found in TMB's GeoJSON so you can sanity-check the mapping. Review the
CSVs, commit them; step 2 turns their first columns into `TMB_IBUS_STOPS` / `TMB_METRO_STATIONS`. The metro
station codes must be the `codi_estacio` values iTransit expects (`120,122,321` in the Function's example); the
resolver prefers `CODI_ESTACIO`. See `artifacts/SampleData/README.md`.

## 2. Create the Event Hubs namespace

```bash
az login
./infra/create-eventhubs.sh --prefix fabcon26 --location westeurope --attendees 120 --tier Premium \
    --function-principal-id <objectId of the Function App's managed identity>
```

Creates the resource group, namespace, the four hubs (24 h retention), SAS policies `function-send` (Send, used
only by the replay script) and `attendee-listen` (Listen, handed to the room), 130 consumer groups spread over
the two hub pairs, the Data Sender role for the Function, and writes `infra/out/consumer-groups.csv` (seat sheet
to print) plus `infra/out/function-settings.env` (paste into the Function App's application settings).

## 3. Make the Function publish flat events to both hubs

Follow [`function-changes/README.md`](function-changes/README.md): copy `flatten.py` next to `function_app.py`,
replace the two functions with the two-binding versions shown there, run the tests, deploy with the settings from
step 2. `flatten_metro()` is pinned to a real iTransit response (`artifacts/EventSamples/itransit-metro-response.json`).
Field-level contract: [`../docs/data-feed-contract.md`](../docs/data-feed-contract.md).

Run the Function **only in the workshop window** (07:30–14:00 Europe/Madrid on the day, plus the dry run) so the TMB
plan's daily budget survives and Lab 05's heartbeat rule means "feed down".

## 4. Fallback: replay a recording

During the dry run, once `BusArrivalsRaw` has an hour of data, export it from the KQL editor:

```kql
BusArrivalsRaw | where PolledAtUtc > ago(1h) | order by PolledAtUtc asc
```

Save as `infra/out/recording-bus.csv` (same for `MetroArrivalsRaw` → `recording-metro.csv`). On the day, if the live
feed fails, run one replay per hub (four processes):

```bash
pip install azure-eventhub
set -a; source infra/out/function-settings.env; set +a      # exports EVENTHUB_SEND_CONNECTION_STRING
for h in tmb-ibus-a tmb-ibus-b;  do python3 infra/replay_events.py infra/out/recording-bus.csv   --hub $h --loop & done
for h in tmb-metro-a tmb-metro-b; do python3 infra/replay_events.py infra/out/recording-metro.csv --hub $h --loop & done
```

Timestamps are shifted so the first event is "now" and relative spacing is kept; `--speed 2` halves the waits.
Attendees change nothing.

## 5. Alternative delivery (not used in the labs): Eventstream HTTP source

If Event Hubs were unavailable, each attendee could poll an HTTP trigger on the Function with Eventstream's **HTTP**
source (preview): a `GET /api/arrivals` returning the latest flat predictions as a JSON array, 30 s interval, API-key
auth. It scales to any room with no consumer-group maths (120 pollers every 30 s is 4 requests/s, trivial for a
Function), but it's preview, polling rather than streaming, and the Function needs a cached read endpoint.
Documented plan B; the labs are written for Event Hubs.

## 6. Tear down

```bash
az group delete --name fabcon26-fabcon-rg --yes --no-wait
```

The evening after the workshop. Attendees who want to keep experimenting are told (Module 07) to switch their source
to the built-in **Sample data → Buses** feed.

# Presenter infrastructure (RTI half)

Attendees never touch any of this. It exists so **120 people** can each build their own eventstream over one live feed.

```
 TMB iBus / iTransit metro ──► Azure Function RTIBCN/ (timers, 30 s / 60 s), raw envelope per response,
                                     │ copied to both hubs of each feed (two output bindings)
                                     ▼
                     Event Hubs namespace evhns-rtibcn-premium-1976 (Premium, 1 PU)
                       ├─ tmb-ibus-1-65      consumer groups user-001..user-065
                       ├─ tmb-ibus-66-130    consumer groups user-066..user-130
                       ├─ tmb-metro-1-65     consumer groups user-001..user-065
                       └─ tmb-metro-66-130   consumer groups user-066..user-130
                                     │  listen-only SAS "attendee-listen"
                                     ▼
                     each attendee's BusArrivalsEventstream / MetroArrivalsEventstream
```

Why two hubs per feed: every attendee eventstream needs its own consumer group (two readers on one group fight
over partitions), and a Premium hub allows 100. Attendees 1–65 use the `-1-65` hubs, 66–130 the `-66-130` hubs;
their consumer group exists only on their own pair. Both halves see identical data.

## 1. Resolve stop and station codes (once, before the dry run)

```bash
pip install requests
export TMB_APP_ID=... TMB_APP_KEY=...          # from https://developer.tmb.cat/
python3 infra/resolve_stops.py                 # writes artifacts/SampleData/{stops,lines,metro_stations}.csv
```

Review the CSVs, commit them, and set the Function's `TMB_IBUS_STOPS` / `TMB_METRO_STATIONS` from their first
columns (`StationCode` = TMB's `codi_estacio`, the codes iTransit expects). See `artifacts/SampleData/README.md`.

## 2. Provision Event Hubs and the Function

```bash
../RTIBCN/setup_event_hubs.sh        # namespace, four hubs, 130 consumer groups, Data Sender role, app settings
./infra/prepare-room.sh              # listen-only SAS policy, replay send policy, seat sheet, projected values
```

`prepare-room.sh` writes `infra/out/seat-sheet.csv` (print it; one row per attendee) and `infra/out/replay.env`.
Both scripts default to the same subscription / resource group / namespace; override with the env vars they list.

Set the schedules per the [contract](../docs/data-feed-contract.md) §1 (`IBUS_SCHEDULE` every 30 s, `METRO_SCHEDULE`
every 60 s) and run the Function **only in the workshop window** (07:30–14:00 Europe/Madrid on the day, plus the
dry run) so the TMB plan's daily budget survives and Lab 05's heartbeat rule means "feed down".

## 3. Fallback: replay a recording

During the dry run, once `BusArrivalsRaw` has an hour of data, export it from the KQL editor:

```kql
BusArrivalsRaw | where fetchedAt > ago(1h) | order by fetchedAt asc
```

Save as `infra/out/recording-bus.csv` (same for `MetroArrivalsRaw` → `recording-metro.csv`). On the day, if the live
feed fails, run one replay per hub:

```bash
pip install azure-eventhub
set -a; source infra/out/replay.env; set +a
for h in tmb-ibus-1-65 tmb-ibus-66-130;   do python3 infra/replay_events.py infra/out/recording-bus.csv   --hub $h --loop & done
for h in tmb-metro-1-65 tmb-metro-66-130; do python3 infra/replay_events.py infra/out/recording-metro.csv --hub $h --loop & done
```

`fetchedAt` is shifted so the first envelope is "now" and relative spacing is kept; `--speed 2` halves the waits.
Attendees change nothing.

## 4. Alternative delivery (not used in the labs): Eventstream HTTP source

If Event Hubs were unavailable, each attendee could poll an HTTP trigger on the Function with Eventstream's **HTTP**
source (preview): a `GET /api/arrivals` returning the latest envelopes as a JSON array, 30 s interval, API-key auth.
120 pollers every 30 s is 4 requests/s. It's preview and polling rather than streaming, and the Function would need
a cached read endpoint. Documented plan B; the labs are written for Event Hubs.

## 5. Tear down

Delete the resource group the evening after the workshop (see `RTIBCN/setup_event_hubs.sh` for its name). Attendees
who want to keep experimenting are told (Module 07) to switch their source to the built-in **Sample data → Buses** feed.

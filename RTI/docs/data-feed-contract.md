# Data-feed contract — what the Azure Function must publish

This is the contract between the presenter-hosted Azure Function in [`../../RTIBCN/`](../../RTIBCN/README.md)
(which polls TMB) and every lab in this folder. The labs' KQL, Eventstream field names, Activator object IDs
and dashboard queries all assume exactly the field names and types in §3. Change the Function to match this
(a drop-in module is provided, see §4), or change this document *and* every lab.

**Status of the Function today (commit `776a416`)**: it polls `ibus/stops/{stop}` per configured stop and
`itransit/metro/estacions?estacions=…` once for all stations, and publishes **one envelope per API response**
(`{"source","key","fetchedAt","payload"}`, the payload being TMB's raw JSON) to one hub per feed.
The labs need **one flat event per prediction**. §4 describes the change; §6 describes what to do in the labs if you
decide to keep the envelope instead.

## 1. Which stops and which data — the decision

### Selection criteria

1. **Venue first.** Attendees should recognise the stops they used to get to the CCIB, and the alerts should be
   about *their* bus home. The CCIB is served by metro **L4 El Maresme | Fòrum**, bus lines **H16** and **7** (both
   terminate at the Fòrum / Diagonal Mar end) plus **136**, and tram T4/T5 (tram is not in TMB's iBus feed, so out
   of scope). Source: [ccib.es/how-to-get-here](https://ccib.es/en/how-to-get-here/).
2. **High frequency, so the stream never looks dead.** Only lines that run every ~6–10 minutes in daytime: the H
   (horizontal) and V (vertical) orthogonal-network lines, D20, and the trunk lines 7, 47, 59.
3. **Spread across the city for the map tile**: the Fòrum, the Poblenou/Diagonal Mar corridor between venue and
   centre, the four interchanges everyone knows (Plaça Catalunya, Passeig de Gràcia / Diagonal, Sagrada Família,
   Sants Estació), plus Glòries and Barceloneta.
4. **Small enough to respect TMB's API plan.** Target **≤ 16 bus stops** and **≤ 10 metro stations**. iBus
   refreshes predictions every 20–40 s ([TMB iBus](https://www.tmb.cat/en/barcelona/tmb-ibus)); TMB's own docs say
   iMetro refreshes at least every 10–15 s (per `RTIBCN/README.md`). Polling faster than 30 s buys nothing.

### Bus stops (`GET /v1/ibus/stops/{stopCode}`; one call returns every line at that stop)

TMB stop codes are only obtainable from the authenticated developer API, so this table lists *landmarks* and
preferred lines; [`../infra/resolve_stops.py`](../infra/resolve_stops.py) turns it into exact `StopCode`s by querying
`/v1/transit/linies/bus/{line}/parades` and picking, per landmark and line, the nearest stop in each direction. Its
output, `artifacts/SampleData/stops.csv`, is **both** the Function's `TMB_IBUS_STOPS` list **and** the `StopsDim`
table attendees load in Lab 03. Run it once during the dry run, commit the result, don't regenerate on the day.

| Zone | Landmark (approx. lat, lon) | Preferred lines | Why |
|---|---|---|---|
| Venue | CCIB / Rambla de Prim – Av. Diagonal (41.4108, 2.2180) | H16, 7, 136 | The stops attendees used; both directions |
| Venue | El Maresme \| Fòrum metro entrance (41.4098, 2.2166) | H16, 7 | Second venue cluster, ties bus to metro |
| Corridor | Diagonal Mar / Selva de Mar (41.4066, 2.2110) | 7, H16 | First stop out of the venue |
| Corridor | Poblenou – Rambla del Poblenou / Diagonal (41.4029, 2.2043) | 7, H16, V27 | Mid-corridor |
| Corridor | Glòries (41.4033, 2.1868) | 7, H12, V21 | Corridor meets the L1 interchange |
| Corridor | Vila Olímpica / Marina (41.3880, 2.1962) | V21, D20, 59 | Coastal route to the centre |
| Interchange | Plaça Catalunya (41.3870, 2.1700) | V15, H16, 59, 47 | Highest-frequency stop set |
| Interchange | Passeig de Gràcia – Diagonal (41.3955, 2.1613) | 7, V15, H8 | Where line 7 crosses the centre |
| Interchange | Sagrada Família (41.4036, 2.1744) | V19, H10, 19, 33 | Tourist hotspot; visible bunching at peak |
| Interchange | Sants Estació (41.3792, 2.1401) | H10, V7, D40 | Rail interchange; far west for the map |
| Interchange | Barceloneta – Pla de Palau (41.3809, 2.1899) | V15, V17, 59, D20 | South anchor for the map |

Resolver rules: for each landmark row and preferred line, take the nearest stop of that line within **250 m**,
one per direction, cap the total at **16**, prefer stops serving several preferred lines. The line list comes from
public maps, not the API; if a line doesn't pass a landmark the resolver simply finds nothing for that pair. The
table is a wish list; **`stops.csv` is the contract**.

### Metro stations (`GET /v1/itransit/metro/estacions?estacions=<codes>`, one call for all)

| Station | Lines | Why |
|---|---|---|
| El Maresme \| Fòrum | L4 | Venue |
| Besòs Mar | L4 | Next stop out, headway comparison |
| Selva de Mar | L4 | Corridor |
| Barceloneta | L4 | Corridor towards the centre |
| Passeig de Gràcia | L2, L3, L4 | Interchange |
| Catalunya | L1, L3 | Interchange |
| Sagrada Família | L2, L5 | Interchange |
| Diagonal | L3, L5 | Interchange |
| Glòries | L1 | Corridor meets L1 |
| Sants Estació | L3, L5 | Rail interchange |

The resolver writes `artifacts/SampleData/metro_stations.csv` from `/v1/transit/linies/metro/{line}/estacions`;
use its `StationCode` column for `TMB_METRO_STATIONS`. Confirm during the dry run that the codes the iTransit
endpoint expects are the same station codes the Transit API returns (the Function's example uses `120,122,321`).

### Polling schedule and API budget

The Function has one NCRONTAB schedule per feed. Recommended values:

| Setting | Value | Calls / hour | Notes |
|---|---|---|---|
| `IBUS_SCHEDULE` | `*/30 * * * * *` (every 30 s) | 16 stops × 120 = **1,920** | One iBus call per stop returns all lines |
| `METRO_SCHEDULE` | `0 */1 * * * *` (every 60 s) | **60** | One iTransit call for all stations |
| **Total** | | **≈ 2,000 / hour**, ≈ 13,000 for a 07:30–14:00 window | **Confirm against your TMB plan's per-second and per-day limits before the dry run.** If the daily cap is lower, use `0 */1 * * * *` for iBus (960/h). |

Keep `TMB_MAX_CONCURRENCY` at 5 or lower so a 30-second cycle never bursts above the plan's per-second limit.
Run the Function **only inside the workshop window** (and the dry run): scale the Function App to zero or disable
the timer functions outside 07:30–14:00 Europe/Madrid on the day, so the plan's daily budget isn't burnt overnight
and Lab 05's heartbeat rule means "the feed is down".

## 2. Transport: Azure Event Hubs

- Namespace `<prefix>-fabcon-ehns`, **Premium (1 PU)**, 24 h retention. Each attendee eventstream needs its own
  consumer group and Premium allows **100 per event hub**, so **120 attendees + spare = two hubs per feed**:
  **`tmb-ibus-a`, `tmb-ibus-b`** (4 partitions each) and **`tmb-metro-a`, `tmb-metro-b`** (2 partitions each).
  Attendees 1–65 read the `-a` hubs, 66–130 the `-b` hubs (the seat sheet says which). The Function publishes
  **every event to both hubs of a feed** (two output bindings per function, see §4).
- Function → hubs: **managed identity** with *Azure Event Hubs Data Sender* on the namespace (already how the Function
  is written: `EVENT_HUB_CONNECTION__fullyQualifiedNamespace`). A SAS policy `function-send` also exists, used only by
  the replay script.
- Attendees → hub: listen-only SAS policy **`attendee-listen`** plus a personal consumer group **`attendee-NNN`**
  on their assigned hub letter. Never hand the room a key that can send.
- One Event Hubs **event per prediction**, body = UTF-8 JSON object. The output binding can't set partition keys
  per event; ordering per stop isn't required by any lab.
- Volume: 16 stops × ~4 lines × 2 predictions ≈ 130 events per 30-second cycle. Trivial.

## 3. Event schemas

Field names are **PascalCase** and used verbatim in KQL, Eventstream and Activator. Times are ISO-8601 **UTC**
with a `Z` suffix; labs convert to Europe/Madrid for display.

### 3.1 `BusArrival` (hubs `tmb-ibus-a` and `tmb-ibus-b`)

```json
{
  "EventType": "BusArrival",
  "PolledAtUtc": "2026-09-30T07:15:02Z",
  "StopCode": 1497,
  "LineCode": "H16",
  "RouteId": "1601",
  "Destination": "Forum Campus Besos",
  "Rank": 1,
  "MinutesToArrival": 4,
  "SecondsToArrival": 230,
  "ArrivalText": "4 min",
  "IsStale": false,
  "Source": "TMB iBus"
}
```

| Field | Type | From (Function envelope → iBus payload) | Notes |
|---|---|---|---|
| `EventType` | string | constant | `BusArrival` |
| `PolledAtUtc` | datetime | envelope `fetchedAt`, normalised to `…Z` | Event time used everywhere downstream |
| `StopCode` | int | envelope `key` | Join key to `StopsDim.StopCode` |
| `LineCode` | string | `payload.data.ibus[].line` | Join key to `LinesDim.LineCode`, e.g. `H16` |
| `RouteId` | string | `payload.data.ibus[].routeId` | Direction identifier |
| `Destination` | string | `payload.data.ibus[].destination` | Human-readable direction |
| `Rank` | int | position within the same `line` in the array, 1-based, ordered by `t-in-s` | `1` = next bus |
| `MinutesToArrival` | int | `payload.data.ibus[].t-in-min` | The number the alerts use |
| `SecondsToArrival` | int | `payload.data.ibus[].t-in-s` | |
| `ArrivalText` | string | `payload.data.ibus[].text-ca` | e.g. `4 min` |
| `IsStale` | bool, **optional** | constant `false` unless you add caching | Labs tolerate its absence; the KQL tables define it |
| `Source` | string | constant | `TMB iBus` |

Deliberately **not** in the event: stop name, coordinates, line origin/destination. Attendees add those in Lab 03
from `StopsDim`/`LinesDim`; the raw stream being "codes only" is the teaching point (and mirrors the afternoon's
"a FreezerId and a number tells you nothing").

iBus payload shape this maps from (per [TMB API samples](https://github.com/TMB-Barcelona/TMB-API-samples) and
the [tmb Python library](https://github.com/alemuro/tmb)):
`{"status":"success","data":{"ibus":[{"line":"V23","routeId":"2230","destination":"Can Marcet","t-in-min":5,"t-in-s":323,"text-ca":"5 min"}]}}`

### 3.2 `MetroArrival` (hubs `tmb-metro-a` and `tmb-metro-b`)

```json
{
  "EventType": "MetroArrival",
  "PolledAtUtc": "2026-09-17T21:30:01Z",
  "StationCode": 321,
  "LineCode": "L3",
  "RouteId": "0031",
  "Direction": "Trinitat Nova",
  "DirectionId": 1,
  "Track": 1,
  "ServiceId": "303",
  "Rank": 1,
  "PredictedArrivalUtc": "2026-09-17T21:31:50Z",
  "SecondsToArrival": 108,
  "IsStale": false,
  "Source": "TMB metro"
}
```

Mapped from the iTransit `metro/estacions?estacions=…` response (real sample:
[`../artifacts/EventSamples/itransit-metro-response.json`](../artifacts/EventSamples/itransit-metro-response.json)),
one event per `linies[] → estacions[] → linies_trajectes[] → propers_trens[]`:

| Field | Type | From | Notes |
|---|---|---|---|
| `PolledAtUtc` | datetime | Function clock | |
| `StationCode` | int | `estacions[].codi_estacio` | Join key to `MetroStationsDim.StationCode`; same codes as `TMB_METRO_STATIONS` (`120,122,321` in the example) |
| `LineCode` | string | `linies_trajectes[].nom_linia` | `L1` … `L11` |
| `RouteId` | string | `linies_trajectes[].codi_trajecte` | e.g. `0031` |
| `Direction` | string | `linies_trajectes[].desti_trajecte` | Terminus name |
| `DirectionId` | int | `estacions[].id_sentit` | 1 / 2 |
| `Track` | int | `estacions[].codi_via` | Platform/track |
| `ServiceId` | string | `propers_trens[].codi_servei` | Train run id |
| `Rank` | int | position by `temps_arribada` within the station/trajecte | `1` = next train |
| `PredictedArrivalUtc` | datetime | `propers_trens[].temps_arribada` (epoch ms → ISO) | Absolute instant, unlike iBus |
| `SecondsToArrival` | int | `(temps_arribada − payload.timestamp) / 1000`, floored at 0 | Computed against TMB's own clock, not the Function's |
| `IsStale`, `Source` | | constants | `false`, `TMB metro` |

Implemented and unit-tested in `flatten_metro()` (§4) against the saved sample.

## 4. The Function change (drop-in)

[`../infra/function-changes/`](../infra/function-changes/) contains `flatten.py` (pure functions
`flatten_ibus()` / `flatten_metro()`, tested against the real iTransit sample), `test_flatten.py`, and a README
with the edit to `function_app.py`: replace `_envelope(...)` with the flatteners, and add a **second Event Hubs
output binding per function** so each event lands in both the `-a` and `-b` hub. No schedule or auth change.

## 5. Behaviour the labs rely on

- **Continuous flow**: at least one `BusArrival` per stop every 30–60 s during the session (Lab 02 preview, Lab 04
  live refresh, Lab 05 heartbeat = 10 minutes of silence).
- **Two ranks per stop/line**: Lab 03's bunching query uses `Rank == 1` vs `Rank == 2`.
- **Occasional long waits**: real data produces `MinutesToArrival > 12` several times an hour on the less frequent
  lines; Lab 05's `Long wait at the Fòrum` is tuned to that. If the dry run between 11:00 and 13:00 never fires it,
  lower the threshold in Lab 05 to 10 rather than touching the Function.
- **Stable field set**: add fields freely (they flow through), never rename or remove one.

## 6. If you keep the envelope instead

Everything still works, with two lab changes and one KQL change:

- **Lab 02** gains an **Expand** operator on `payload.data.ibus` right after the source, followed by **Manage
  fields** that promotes `key → StopCode`, `fetchedAt → PolledAtUtc`, `payload.data.ibus.line → LineCode`,
  `…t-in-min → MinutesToArrival`, etc. `Rank` doesn't exist; drop the `NextBusOnly` filter and change the
  **Group by** aggregate to **Minimum** of `MinutesToArrival` (min = next bus).
- **Lab 05** rule 1 uses **Summarization: Minimum, window 1 minute** on `MinutesToArrival` instead of the `Rank == 1`
  filter.
- **Lab 03** ingests the envelope as-is (`source`, `key`, `fetchedAt`, `payload : dynamic`) and the update policy
  flattens with `mv-expand` and computes `Rank` with `row_number()`; the ready-made variant is the commented
  **Part C-alt** at the end of [`../artifacts/Eventhouse/TransitEventhouse.kql`](../artifacts/Eventhouse/TransitEventhouse.kql).

The flat contract is recommended: it keeps Lab 02 inside its 35 minutes and makes the Activator semantics exact.

## 7. Fallback: replay

Record 60+ minutes of real events during the dry run (`BusArrivalsRaw | where PolledAtUtc > ago(1h)` → export)
and keep the file with the presenter laptop. If TMB or the Function is down on the day,
[`../infra/replay_events.py`](../infra/replay_events.py) re-publishes the recording to the same hubs (via the
`function-send` SAS policy) with `PolledAtUtc` shifted to "now", so every lab step runs unchanged.

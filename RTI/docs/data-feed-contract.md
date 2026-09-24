# Data-feed contract — what the Azure Function publishes and what the labs derive from it

The presenter-hosted Azure Function in [`../../RTIBCN/`](../../RTIBCN/README.md) polls TMB and publishes **one
envelope per API response**, with TMB's raw JSON as the payload, to four Event Hubs. **The labs flatten that
envelope themselves**: in Eventstream (Expand + Manage fields, Lab 02) and in KQL (`mv-expand`, Lab 03). Learning
to turn a nested API payload into flat, typed events is part of the course, so the Function is deliberately kept
"dumb". This document pins both ends: §3 what arrives, §4 the flat field names every lab, query and rule uses.

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
   refreshes predictions every 20–40 s ([TMB iBus](https://www.tmb.cat/en/barcelona/tmb-ibus)); iMetro at least every
   10–15 s. Polling faster than 30 s buys nothing.

### Bus stops (`GET /v1/itransit/bus/parades/{stopCode}`; one call returns every line at that stop)

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
its `StationCode` column (TMB's `codi_estacio`, the same codes iTransit returns, e.g. `120,122,321`) is the
Function's `TMB_METRO_STATIONS`.

### Polling schedule and API budget

| Setting | Value | Calls / hour | Notes |
|---|---|---|---|
| `IBUS_SCHEDULE` | `*/30 * * * * *` (every 30 s) | 16 stops × 120 = **1,920** | One iBus call per stop returns all lines |
| `METRO_SCHEDULE` | `0 */1 * * * *` (every 60 s) | **60** | One iTransit call for all stations |
| **Total** | | **≈ 2,000 / hour**, ≈ 13,000 for a 07:30–14:00 window | **Confirm against your TMB plan's per-second and per-day limits before the dry run.** If the daily cap is lower, use `0 */1 * * * *` for iBus (960/h). |

Keep `TMB_MAX_CONCURRENCY` at 5 or lower so a 30-second cycle never bursts above the plan's per-second limit.
Run the Function **only inside the workshop window** (and the dry run): disable the timers outside 07:30–14:00
Europe/Madrid on the day, so the plan's daily budget isn't burnt overnight and Lab 05's heartbeat rule means
"the feed is down".

## 2. Transport: Azure Event Hubs (as provisioned by `RTIBCN/setup_event_hubs.sh`)

| | Users 1–65 | Users 66–130 |
|---|---|---|
| Bus hub | **`tmb-ibus-1-65`** | **`tmb-ibus-66-130`** |
| Metro hub | **`tmb-metro-1-65`** | **`tmb-metro-66-130`** |
| Consumer groups on those hubs | `user-001` … `user-065` | `user-066` … `user-130` |

- Namespace: Premium (1 PU), default name `evhns-rtibcn-premium-1976`; all four hubs have 2 partitions and 24 h
  retention. Premium allows 100 consumer groups per hub, so 120 attendees + spare need two hubs per feed; the
  Function copies every event to both hubs of a feed.
- Function → hubs: **managed identity**, *Azure Event Hubs Data Sender* on the namespace (done by the setup script).
- Attendees → hubs: listen-only SAS policy **`attendee-listen`** (created by [`../infra/prepare-room.sh`](../infra/prepare-room.sh),
  which also prints the seat sheet) plus their personal consumer group **on their own user-range hubs only**.
  Never hand the room a key that can send.
- One Event Hubs **event per API response** (one per bus stop per poll; one per poll for all metro stations),
  body = UTF-8 JSON envelope.

## 3. What arrives: the envelope

```json
{
  "source": "tmb.ibus",
  "key": "1497",
  "fetchedAt": "2026-09-30T07:15:02.123456+00:00",
  "payload": { ...TMB's response, unchanged... }
}
```

| Field | Type | Meaning |
|---|---|---|
| `source` | string | `tmb.ibus` or `tmb.imetro` |
| `key` | string | Bus: the stop code polled. Metro: the comma-separated station list (`"120,122,321"`) |
| `fetchedAt` | datetime | Function clock, UTC, ISO-8601 |
| `payload` | object | The raw TMB JSON |

### 3.1 iTransit bus payload (`source = tmb.ibus`, hubs `tmb-ibus-*`, from `GET /v1/itransit/bus/parades/{stop}`)

```
{"timestamp": <epoch ms>,
 "parades": [ {"codi_parada": "1265", "nom_parada": "Pg de Sant Joan - Còrsega",
               "linies_trajectes": [ {"codi_linia": 208, "nom_linia": "H8", "id_sentit": 2, "codi_trajecte": "2081",
                                      "desti_trajecte": "Ernest Lluch", "id_operador": 2, "transit_namespace": "bus",
                                      "propers_busos": [ {"temps_arribada": <epoch ms>, "id_bus": 6405,
                                                          "info_bus": {"accessibilitat": {"estat_rampa": "SENSE_INCIDENCIA"}}} ] } ] } ] }
```

Three nested arrays: the stop (one element, since the Function asks for one stop per call), the lines and
directions serving it, and the next buses per line (usually two). There is **no relative time**: `temps_arribada`
is an absolute arrival instant, so the wait is `temps_arribada − timestamp` (TMB's clock on both sides). The stop
**name** is included; coordinates, zone and line origin/destination are not. Real sample:
[`../artifacts/EventSamples/ibus-envelope.json`](../artifacts/EventSamples/ibus-envelope.json). (The old
`ibus/stops/{stop}` endpoint with its `status/data/ibus` shape is deprecated and no longer used.)

### 3.2 iTransit metro payload (`source = tmb.imetro`, hubs `tmb-metro-*`)

```
{"timestamp": <epoch ms>,
 "linies": [ {"codi_linia", "nom_linia", "nom_familia", "color_linia",
              "estacions": [ {"codi_via", "id_sentit", "codi_estacio",
                              "linies_trajectes": [ {"nom_linia", "codi_trajecte", "desti_trajecte",
                                                     "propers_trens": [ {"codi_servei", "temps_arribada": <epoch ms>} ] } ] } ] } ] }
```

Four nested arrays; `temps_arribada` is an **absolute** arrival instant. Real sample:
[`../artifacts/EventSamples/itransit-metro-response.json`](../artifacts/EventSamples/itransit-metro-response.json)
(wrapped in the envelope: [`imetro-envelope.json`](../artifacts/EventSamples/imetro-envelope.json)).

## 4. What the labs derive: the flat field names

These names are used verbatim in every lab, KQL statement, dashboard query and Activator rule. Change one, change all.

### 4.1 Bus (derived in Lab 02's Eventstream operators and SQL operator, and Lab 03's `EnrichBusArrivals()` update policy)

| Flat field | Type | From | Where |
|---|---|---|---|
| `PolledAtUtc` | datetime | `fetchedAt` | all |
| `TmbTimestamp` | datetime | `payload.timestamp` (epoch ms) | KQL (`PolledMs` as raw epoch in the no-code stream) |
| `StopCode` | long | `tolong(key)` | all; join key to `StopsDim` |
| `StopName` | string | `parades[].nom_parada` (KQL prefers `StopsDim.StopName`, falls back to it) | all |
| `LineCode` | string | `linies_trajectes[].nom_linia` | all; join key to `LinesDim`; `H8`, `47`, `V19` |
| `LineFamily` | string | `Left(LineCode, 1)` | no-code stream only; `H`/`V`/`D` orthogonal network, digit = trunk |
| `RouteId`, `DirectionId` | string, long | `linies_trajectes[].codi_trajecte`, `.id_sentit` | KQL and no-code stream |
| `Destination` | string | `linies_trajectes[].desti_trajecte` | all |
| `BusId` | long | `propers_busos[].id_bus` | KQL and no-code stream |
| `ArrivalMs` | long | `propers_busos[].temps_arribada` (raw epoch) | no-code stream; `MIN_ArrivalMs` after the Group by |
| `PredictedArrivalUtc` | datetime | `temps_arribada` → datetime | KQL |
| `SecondsToArrival` | long | `PredictedArrivalUtc − TmbTimestamp` | KQL |
| `MinutesToArrival` | real | `SecondsToArrival / 60` (KQL); `MIN((temps_arribada − timestamp) / 60000.0)` per line per minute (SQL operator → `ForumNextBus`) | KQL and the SQL-operator derived stream; **the number the alerts and dashboards use** |
| `Rank` | long | `row_number()` per stop/line/poll ordered by `PredictedArrivalUtc` | KQL only; `1` = next bus. The no-code stream uses **Minimum** aggregates instead |

Plus, after enrichment: `Zone`, `Lat`, `Lon` (from `StopsDim`) and `LineName`, `LineOrigin`, `LineDestination`
(from `LinesDim`).

Why three places: the no-code Manage fields operator has no arithmetic between two fields, so the stream branch
that needs minutes (Activator, Lab 05) is built with the **SQL operator** (preview; `CROSS APPLY GetArrayElements`
for the three arrays, subtraction for the minutes), and the branch that only needs a per-minute aggregate keeps the
raw epoch (`MIN_ArrivalMs`) and lets KQL subtract at query time.

### 4.2 Metro (derived in Lab 03 Part F's `MetroArrivalsFlat()` function)

| Flat field | From |
|---|---|
| `PolledAtUtc` | `fetchedAt` |
| `TmbTimestamp` | `payload.timestamp` (epoch ms → datetime) |
| `StationCode`, `Track`, `DirectionId` | `estacions[].codi_estacio`, `.codi_via`, `.id_sentit` |
| `LineCode`, `RouteId`, `Direction` | `linies_trajectes[].nom_linia`, `.codi_trajecte`, `.desti_trajecte` |
| `ServiceId`, `PredictedArrivalUtc` | `propers_trens[].codi_servei`, `.temps_arribada` (epoch ms → datetime) |
| `SecondsToArrival` | `PredictedArrivalUtc − TmbTimestamp`, in seconds |
| `Rank` | `row_number()` per poll/station/route ordered by `PredictedArrivalUtc` |

## 5. Behaviour the labs rely on

- **Continuous flow**: one bus envelope per stop every 30 s during the session (Lab 02 preview, Lab 04 live
  refresh, Lab 05 heartbeat = 10 minutes of silence). A stop can legitimately have an empty `propers_busos` for a
  line when TMB has no active prediction; the labs tolerate that.
- **Two predictions per line** in most responses: Lab 03's bunching query compares `Rank 1` and `Rank 2`.
- **Eventstream name without underscores or dots** (`BusArrivalsEventstream`): the SQL operator refuses others.
- **Occasional long waits**: real data produces next-bus predictions above 12 minutes several times an hour on
  the less frequent lines; Lab 05's `Long wait at the Fòrum` is tuned to that. If the dry run between 11:00 and
  13:00 never fires it, lower the threshold in Lab 05 to 10.
- **Stable envelope**: `source`, `key`, `fetchedAt`, `payload` never change; TMB's own payload is passed through.

## 6. Fallback: replay

Record 60+ minutes of real envelopes during the dry run (`BusArrivalsRaw | where fetchedAt > ago(1h)` → export)
and keep the file with the presenter laptop. If TMB or the Function is down on the day,
[`../infra/replay_events.py`](../infra/replay_events.py) re-publishes the recording to the same hubs (via the
`function-send` SAS policy) with `fetchedAt` shifted to "now", so every lab step runs unchanged.

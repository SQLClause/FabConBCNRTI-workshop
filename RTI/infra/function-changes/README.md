# Function change: flat per-prediction events, published to two hubs per feed

The poller in [`../../../RTIBCN/`](../../../RTIBCN/README.md) publishes one envelope per TMB response to one hub
per feed. The labs need (a) one flat event per prediction ([`../../docs/data-feed-contract.md`](../../docs/data-feed-contract.md)
§3) and (b) with 120 attendees, **two hubs per feed** (Premium allows 100 consumer groups per hub). This folder
holds the change as a drop-in so `RTIBCN/` isn't edited from here.

## 1. Copy the module

```bash
cp RTI/infra/function-changes/flatten.py RTIBCN/flatten.py
cp RTI/infra/function-changes/test_flatten.py RTIBCN/tests/test_flatten.py
```

(`test_flatten.py` reads `RTI/artifacts/EventSamples/itransit-metro-response.json` when it finds it and falls back
to an embedded excerpt otherwise, so it runs from either folder.)

## 2. Edit `RTIBCN/function_app.py`

Add the import:

```python
from flatten import flatten_ibus, flatten_metro
```

Replace the two functions' decorators and bodies with a **second output binding** each and the flatteners
(Python v2 model supports several output bindings; each needs its own `arg_name`):

```python
@app.function_name(name="poll_ibus")
@app.timer_trigger(schedule="%IBUS_SCHEDULE%", arg_name="timer", run_on_startup=False)
@app.event_hub_output(arg_name="events_a", event_hub_name="%EVENT_HUB_NAME_IBUS_A%", connection="EVENT_HUB_CONNECTION")
@app.event_hub_output(arg_name="events_b", event_hub_name="%EVENT_HUB_NAME_IBUS_B%", connection="EVENT_HUB_CONNECTION")
async def poll_ibus(timer: func.TimerRequest, events_a: func.Out[List[str]], events_b: func.Out[List[str]]) -> None:
    stops = _csv_setting("TMB_IBUS_STOPS")
    if not stops:
        logging.warning("TMB_IBUS_STOPS is empty; nothing to poll.")
        return
    template = os.environ.get("TMB_IBUS_PATH_TEMPLATE", DEFAULT_IBUS_PATH_TEMPLATE)
    requests = [(stop, template.format(stop=stop), None) for stop in stops]
    async with _client() as client:
        results = await client.gather(requests)
    fetched_at = datetime.now(timezone.utc)
    flat = [json.dumps(e, ensure_ascii=False, separators=(",", ":"))
            for stop, payload in results
            for e in flatten_ibus(stop, fetched_at, payload)]
    if not flat:
        logging.error("iBus poll produced no predictions for %d stops.", len(stops))
        return
    events_a.set(flat)
    events_b.set(flat)
    logging.info("Published %d iBus predictions for %d/%d stops.", len(flat), len(results), len(stops))


@app.function_name(name="poll_metro")
@app.timer_trigger(schedule="%METRO_SCHEDULE%", arg_name="timer", run_on_startup=False)
@app.event_hub_output(arg_name="events_a", event_hub_name="%EVENT_HUB_NAME_METRO_A%", connection="EVENT_HUB_CONNECTION")
@app.event_hub_output(arg_name="events_b", event_hub_name="%EVENT_HUB_NAME_METRO_B%", connection="EVENT_HUB_CONNECTION")
async def poll_metro(timer: func.TimerRequest, events_a: func.Out[List[str]], events_b: func.Out[List[str]]) -> None:
    request = _metro_request()
    if request is None:
        logging.warning("TMB_METRO_STATIONS is empty; nothing to poll.")
        return
    async with _client() as client:
        results = await client.gather([request])
    fetched_at = datetime.now(timezone.utc)
    flat = [json.dumps(e, ensure_ascii=False, separators=(",", ":"))
            for _key, payload in results
            for e in flatten_metro(fetched_at, payload)]
    if not flat:
        logging.error("iMetro poll produced no predictions.")
        return
    events_a.set(flat)
    events_b.set(flat)
    logging.info("Published %d metro predictions for stations %s.", len(flat), request[0])
```

`_envelope()` can stay for debugging or be deleted. For a room under 90 people, point `*_A` and `*_B` at the same
hub name (the binding then double-publishes to one hub; drop the `_b` binding instead if you prefer).

## 3. Settings

`RTI/infra/out/function-settings.env` (written by `create-eventhubs.sh`) contains everything below with real values:

| Setting | Value |
|---|---|
| `TMB_IBUS_STOPS` | `StopCode` column of `RTI/artifacts/SampleData/stops.csv`, comma-separated |
| `TMB_METRO_STATIONS` | `StationCode` column of `metro_stations.csv` (these are the `codi_estacio` values iTransit expects, e.g. `120,122,321`) |
| `IBUS_SCHEDULE` | `*/30 * * * * *` |
| `METRO_SCHEDULE` | `0 */1 * * * *` |
| `EVENT_HUB_NAME_IBUS_A` / `EVENT_HUB_NAME_IBUS_B` | `tmb-ibus-a` / `tmb-ibus-b` |
| `EVENT_HUB_NAME_METRO_A` / `EVENT_HUB_NAME_METRO_B` | `tmb-metro-a` / `tmb-metro-b` |
| `EVENT_HUB_CONNECTION__fullyQualifiedNamespace` | `<prefix>-fabcon-ehns.servicebus.windows.net` |

Grant the Function App's managed identity **Azure Event Hubs Data Sender** on the namespace
(`create-eventhubs.sh --function-principal-id <objectId>` does it).

## 4. Test

```bash
cd RTIBCN && python -m unittest discover -s tests -v
```

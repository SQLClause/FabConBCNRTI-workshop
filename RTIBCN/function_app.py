"""Poll TMB real-time APIs and publish the responses to Azure Event Hubs.

Two timer-triggered functions:
  * poll_ibus  - real-time bus arrivals for configured stops
  * poll_metro - real-time train arrivals for configured metro stations
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import azure.functions as func

from tmb_client import TmbClient

# Binding annotations must use typing.List, not list[...]: the Azure Python
# worker silently fails to index the whole module on PEP 585 generics.
app = func.FunctionApp()

DEFAULT_API_BASE = "https://api.tmb.cat/v1"
DEFAULT_IBUS_PATH_TEMPLATE = "ibus/stops/{stop}"
DEFAULT_METRO_PATH = "itransit/metro/estacions"


def _csv_setting(name: str, default: str = "") -> List[str]:
    return [part.strip() for part in os.environ.get(name, default).split(",") if part.strip()]


def _client() -> TmbClient:
    return TmbClient(
        base_url=os.environ.get("TMB_API_BASE", DEFAULT_API_BASE),
        app_id=os.environ.get("TMB_APP_ID", ""),
        app_key=os.environ.get("TMB_APP_KEY", ""),
        concurrency=int(os.environ.get("TMB_MAX_CONCURRENCY", "5")),
        timeout_seconds=int(os.environ.get("TMB_TIMEOUT_SECONDS", "10")),
    )


def _metro_request() -> Optional[Tuple[str, str, Dict[str, str]]]:
    stations = _csv_setting("TMB_METRO_STATIONS")
    if not stations:
        return None

    station_key = ",".join(stations)
    path = os.environ.get("TMB_METRO_PATH", DEFAULT_METRO_PATH)
    return station_key, path, {"estacions": station_key}


def _envelope(source: str, key: str, payload: Dict[str, Any]) -> str:
    return json.dumps(
        {
            "source": source,
            "key": key,
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


@app.function_name(name="poll_ibus")
@app.timer_trigger(schedule="%IBUS_SCHEDULE%", arg_name="timer", run_on_startup=False)
@app.event_hub_output(
    arg_name="events",
    event_hub_name="%EVENT_HUB_NAME_IBUS%",
    connection="EVENT_HUB_CONNECTION",
)
async def poll_ibus(timer: func.TimerRequest, events: func.Out[List[str]]) -> None:
    stops = _csv_setting("TMB_IBUS_STOPS")
    if not stops:
        logging.warning("TMB_IBUS_STOPS is empty; nothing to poll.")
        return

    template = os.environ.get("TMB_IBUS_PATH_TEMPLATE", DEFAULT_IBUS_PATH_TEMPLATE)
    requests = [(stop, template.format(stop=stop), None) for stop in stops]

    async with _client() as client:
        results = await client.gather(requests)

    if not results:
        logging.error("iBus poll returned no successful responses for %d stops.", len(stops))
        return

    events.set([_envelope("tmb.ibus", stop, payload) for stop, payload in results])
    logging.info("Published iBus arrivals for %d/%d stops.", len(results), len(stops))


@app.function_name(name="poll_metro")
@app.timer_trigger(schedule="%METRO_SCHEDULE%", arg_name="timer", run_on_startup=False)
@app.event_hub_output(
    arg_name="events",
    event_hub_name="%EVENT_HUB_NAME_METRO%",
    connection="EVENT_HUB_CONNECTION",
)
async def poll_metro(timer: func.TimerRequest, events: func.Out[List[str]]) -> None:
    request = _metro_request()
    if request is None:
        logging.warning("TMB_METRO_STATIONS is empty; nothing to poll.")
        return

    async with _client() as client:
        results = await client.gather([request])

    if not results:
        logging.error("iMetro poll returned no successful response.")
        return

    events.set([_envelope("tmb.imetro", key, payload) for key, payload in results])
    logging.info("Published iMetro arrivals for stations %s.", request[0])
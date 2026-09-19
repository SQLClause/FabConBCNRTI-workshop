# RTIBCN TMB real-time poller

Python v2 Azure Functions app that polls the TMB developer APIs and publishes live arrivals to Azure Event Hubs.

| Function | Source | Users 1-65 | Users 66-130 |
|---|---|---|---|
| `poll_ibus` | `itransit/bus/parades/{stop}` for each configured bus stop | `tmb-ibus-1-65` | `tmb-ibus-66-130` |
| `poll_metro` | iMetro predictions for configured metro stations | `tmb-metro-1-65` | `tmb-metro-66-130` |

Each function copies the same events to both destination hubs. Every hub has 65 consumer groups named
`user-001` through `user-065` or `user-066` through `user-130`. This requires an Event Hubs Premium
namespace because Standard supports at most 20 consumer groups per hub. Azure also creates the reserved
`$Default` consumer group, so each hub contains 65 workshop groups plus `$Default`.

Events use this envelope:

```json
{"source":"tmb.imetro","key":"120,122,321","fetchedAt":"2026-09-18T10:00:00+00:00","payload":{}}
```

## Configuration

Copy `local.settings.json.example` to `local.settings.json` for local development. Never commit TMB credentials. In Azure, use Key Vault references for `TMB_APP_ID` and `TMB_APP_KEY`, and managed identity for Event Hubs.

Important settings:

| Setting | Purpose |
|---|---|
| `TMB_IBUS_STOPS` | Comma-separated bus stop codes. No bus events are emitted when empty. |
| `TMB_METRO_STATIONS` | Comma-separated metro station codes used by iMetro. |
| `IBUS_SCHEDULE` | NCRONTAB schedule for bus polling. |
| `METRO_SCHEDULE` | NCRONTAB schedule for metro polling. |
| `EVENT_HUB_NAME_IBUS_1_65` / `EVENT_HUB_NAME_IBUS_66_130` | Bus Event Hubs for each user range. |
| `EVENT_HUB_NAME_METRO_1_65` / `EVENT_HUB_NAME_METRO_66_130` | Metro Event Hubs for each user range. |

The current iBus API returns `timestamp`, `parades`, `linies_trajectes`, and `propers_busos`. A stop can
legitimately have an empty `propers_busos` list when TMB has no active prediction, but events must never
use the deprecated `status/data/ibus` response shape.

TMB documents iMetro predictions as based on each train's last known position and refreshed at least every 10-15 seconds.

## Run locally

Prerequisites: Python 3.11, Azure Functions Core Tools, and Azurite or another valid `AzureWebJobsStorage` connection.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp local.settings.json.example local.settings.json
func start
```

## Test

```bash
python -m unittest discover -s tests -v
python -m compileall -q function_app.py tmb_client.py tests
```

## Deploy

Provision the Premium namespace, four hubs, consumer groups, managed-identity role, and Function settings:

```bash
./setup_event_hubs.sh
```

The script defaults to the workshop's `MVP Demo` subscription resources. Override
`AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_LOCATION`, `EVENT_HUB_NAMESPACE`, or
`FUNCTION_APP_NAME` when targeting another environment.

Publish the Function App:

```bash
func azure functionapp publish <function-app-name> --python --build remote
```
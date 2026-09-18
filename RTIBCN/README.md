# RTIBCN TMB real-time poller

Python v2 Azure Functions app that polls the TMB developer APIs and publishes live arrivals to Azure Event Hubs.

| Function | Source | Destination |
|---|---|---|
| `poll_ibus` | `ibus/stops/{stop}` for each configured bus stop | `tmb-ibus` |
| `poll_metro` | iMetro predictions for configured metro stations | `tmb-metro` |

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
| `EVENT_HUB_NAME_IBUS` | Bus Event Hub name. |
| `EVENT_HUB_NAME_METRO` | Metro Event Hub name. |

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

Set the application settings shown in `local.settings.json.example`, assign the Function App managed identity the `Azure Event Hubs Data Sender` role on the namespace, and publish:

```bash
func azure functionapp publish <function-app-name> --python --build remote
```
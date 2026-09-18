# Sample / reference data

| File | Status | Used by |
|---|---|---|
| `stops_landmarks.csv` | **Input**, hand-authored. Landmarks, preferred lines, search radius, polling interval. | `infra/resolve_stops.py` |
| `metro_stations_wanted.csv` | **Input**, hand-authored. Station names and lines. | `infra/resolve_stops.py` |
| `stops.csv` | **Generated** by the resolver from the live TMB Transit API. Columns: `StopCode,StopName,Address,Zone,Lat,Lon,Lines,IsPrimary,PollIntervalSeconds`. | The Azure Function (polling list) **and** Lab 03 (`StopsDim`), Lab 06 (uploaded to `Files/reference/`) |
| `lines.csv` | **Generated**. Columns: `LineCode,LineName,LineOrigin,LineDestination,TmbLineId`. | Lab 03 (`LinesDim`), Lab 04 parameter |
| `metro_stations.csv` | **Generated**. Columns: `StationCode,StationName,Lines,Zone,Lat,Lon`. | The Function (metro polling list) and Lab 03 (`MetroStationsDim`) |

TMB stop and station codes are only available through the authenticated developer API, so the generated files
are **not** checked in until the presenter has run the resolver once with real credentials:

```bash
export TMB_APP_ID=... TMB_APP_KEY=...
python3 infra/resolve_stops.py
```

Commit the three generated files afterwards and **do not regenerate them on the day**: the labs' expected
results quote stop names, and the Function must poll exactly the codes attendees have in `StopsDim`.

The first row of `stops.csv` (`Zone = Venue`, `IsPrimary = true`) is the `<VENUE_STOP_CODE>` referenced by
Labs 02 and 05.

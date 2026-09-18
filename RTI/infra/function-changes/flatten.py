"""flatten.py -- turn TMB API responses into the flat per-prediction events the RTI labs expect.

Drop this file next to `function_app.py` in RTIBCN/ and see README.md in this folder for the
change to the two timer functions. Pure functions, no I/O, unit-tested in test_flatten.py.

Contract: RTI/docs/data-feed-contract.md §3.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_z(value: str | datetime | int | float | None = None) -> str:
    """Normalise ISO strings, datetimes or epoch milliseconds to ISO-8601 UTC with a 'Z', second precision."""
    if value is None:
        dt = datetime.now(timezone.utc)
    elif isinstance(value, datetime):
        dt = value
    elif isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
    else:
        s = value.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc).replace(microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")


def _to_int(value: Any, default: int | None = None) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def flatten_ibus(stop_code: str | int, fetched_at: str | datetime, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One BusArrival event per prediction in an iBus `ibus/stops/{stop}` response.

    Rank is 1-based per line, ordered by seconds-to-arrival (1 = next bus of that line).
    Returns [] for an empty or malformed payload (the caller simply publishes nothing for that stop).
    """
    predictions = ((payload or {}).get("data") or {}).get("ibus") or []
    polled = _utc_z(fetched_at)
    stop = _to_int(stop_code)
    if stop is None or not isinstance(predictions, list):
        return []

    by_line: Dict[str, List[Dict[str, Any]]] = {}
    for p in predictions:
        if not isinstance(p, dict) or not p.get("line"):
            continue
        by_line.setdefault(str(p["line"]), []).append(p)

    events: List[Dict[str, Any]] = []
    for line, preds in by_line.items():
        preds.sort(key=lambda p: _to_int(p.get("t-in-s"), _to_int(p.get("t-in-min"), 0) * 60))
        for rank, p in enumerate(preds, start=1):
            seconds = _to_int(p.get("t-in-s"))
            minutes = _to_int(p.get("t-in-min"))
            if minutes is None and seconds is not None:
                minutes = seconds // 60
            if seconds is None and minutes is not None:
                seconds = minutes * 60
            events.append({
                "EventType": "BusArrival",
                "PolledAtUtc": polled,
                "StopCode": stop,
                "LineCode": line,
                "RouteId": str(p.get("routeId", "")),
                "Destination": str(p.get("destination", "")),
                "Rank": rank,
                "MinutesToArrival": minutes if minutes is not None else 0,
                "SecondsToArrival": seconds if seconds is not None else 0,
                "ArrivalText": str(p.get("text-ca") or p.get("text-en") or p.get("text-es") or ""),
                "IsStale": False,
                "Source": "TMB iBus",
            })
    return events


def flatten_metro(fetched_at: str | datetime, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One MetroArrival event per station x track x route (trajecte) x predicted train.

    iTransit `metro/estacions?estacions=...` response shape (confirmed from a real response):
        {"timestamp": <epoch ms>,
         "linies": [{"codi_linia", "nom_linia", ...,
                     "estacions": [{"codi_via", "id_sentit", "codi_estacio",
                                    "linies_trajectes": [{"nom_linia", "codi_trajecte", "desti_trajecte",
                                                          "propers_trens": [{"codi_servei", "temps_arribada": <epoch ms>}]}]}]}]}

    `temps_arribada` is an absolute arrival instant, so SecondsToArrival is computed against the
    payload's own `timestamp` (falling back to fetched_at). Rank is 1-based per station/trajecte.
    """
    ts_ms = _to_int((payload or {}).get("timestamp"))
    polled = _utc_z(fetched_at)
    base_ms = ts_ms if ts_ms is not None else int(datetime.fromisoformat(polled.replace("Z", "+00:00")).timestamp() * 1000)

    events: List[Dict[str, Any]] = []
    for line in (payload or {}).get("linies") or []:
        if not isinstance(line, dict):
            continue
        for st in line.get("estacions") or []:
            if not isinstance(st, dict):
                continue
            station = _to_int(st.get("codi_estacio"))
            if station is None:
                continue
            track = _to_int(st.get("codi_via"))
            direction_id = _to_int(st.get("id_sentit"))
            for tr in st.get("linies_trajectes") or []:
                if not isinstance(tr, dict):
                    continue
                trains = [t for t in (tr.get("propers_trens") or []) if isinstance(t, dict) and _to_int(t.get("temps_arribada")) is not None]
                trains.sort(key=lambda t: _to_int(t["temps_arribada"]))
                for rank, t in enumerate(trains, start=1):
                    arr_ms = _to_int(t["temps_arribada"])
                    events.append({
                        "EventType": "MetroArrival",
                        "PolledAtUtc": polled,
                        "StationCode": station,
                        "LineCode": str(tr.get("nom_linia") or line.get("nom_linia") or ""),
                        "RouteId": str(tr.get("codi_trajecte") or ""),
                        "Direction": str(tr.get("desti_trajecte") or ""),
                        "DirectionId": direction_id,
                        "Track": track,
                        "ServiceId": str(t.get("codi_servei") or ""),
                        "Rank": rank,
                        "PredictedArrivalUtc": _utc_z(arr_ms),
                        "SecondsToArrival": max(0, (arr_ms - base_ms) // 1000),
                        "IsStale": False,
                        "Source": "TMB metro",
                    })
    return events

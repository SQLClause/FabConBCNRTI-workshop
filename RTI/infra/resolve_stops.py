#!/usr/bin/env python3
"""
resolve_stops.py -- turn the hand-authored landmark/station wish lists into the exact TMB stop
and station codes the Azure Function polls and the labs load as dimension tables.

Inputs  (hand-authored, committed):
    artifacts/SampleData/stops_landmarks.csv
    artifacts/SampleData/metro_stations_wanted.csv
Outputs (generated, commit after review):
    artifacts/SampleData/stops.csv
    artifacts/SampleData/lines.csv
    artifacts/SampleData/metro_stations.csv

TMB endpoints used (base https://api.tmb.cat/v1, auth via app_id/app_key query params):
    /transit/linies/bus                          -> all bus lines (GeoJSON FeatureCollection)
    /transit/linies/bus/{tmbLineId}/parades      -> stops of one bus line (GeoJSON, Point geometry)
    /transit/linies/metro                        -> all metro lines
    /transit/linies/metro/{tmbLineId}/estacions  -> stations of one metro line

TMB's Transit API property names aren't documented outside the authenticated developer portal. The
names below (CODI_LINIA, NOM_LINIA, ORIGEN_LINIA, DESTI_LINIA, CODI_PARADA, NOM_PARADA, ADRECA) are the
ones used by the open-source `tmb` Python library; station properties are guessed with the same pattern
(CODI_ESTACIO, NOM_ESTACIO). The script prints the property keys it actually sees on the first feature
of every response so you can correct the KEY_* constants below if TMB renamed anything.

Usage:
    export TMB_APP_ID=... TMB_APP_KEY=...
    python3 infra/resolve_stops.py [--max-stops 16] [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

BASE = "https://api.tmb.cat/v1"
ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "artifacts" / "SampleData"

# --- property-name guesses (verify against the printed keys) -------------------------------------
KEY_LINE_ID = ("CODI_LINIA",)
KEY_LINE_NAME = ("NOM_LINIA",)
KEY_LINE_ORIGIN = ("ORIGEN_LINIA",)
KEY_LINE_DEST = ("DESTI_LINIA",)
KEY_STOP_ID = ("CODI_PARADA",)
KEY_STOP_NAME = ("NOM_PARADA",)
KEY_STOP_ADDR = ("ADRECA",)
KEY_STOP_DIRECTION = ("DESTI_SENTIT", "SENTIT", "DESTI_TRAJECTE", "ID_SENTIT")
KEY_STATION_ID = ("CODI_ESTACIO", "CODI_GRUP_ESTACIO", "CODI_PARADA")
KEY_STATION_NAME = ("NOM_ESTACIO", "NOM_PARADA")


def pick(props: dict, candidates: tuple[str, ...], default=None):
    for k in candidates:
        if k in props and props[k] not in (None, ""):
            return props[k]
    # case-insensitive fallback
    lower = {k.lower(): v for k, v in props.items()}
    for k in candidates:
        if k.lower() in lower and lower[k.lower()] not in (None, ""):
            return lower[k.lower()]
    return default


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def norm(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().replace("|", " ").replace("-", " ").split())


class Tmb:
    def __init__(self, app_id: str, app_key: str):
        self.auth = {"app_id": app_id, "app_key": app_key}
        self.session = requests.Session()
        self._printed: set[str] = set()

    def get(self, path: str) -> dict:
        r = self.session.get(f"{BASE}{path}", params=self.auth, timeout=30)
        if r.status_code == 429:
            sys.exit("TMB returned 429 Too Many Requests -- your plan's rate limit. Wait and re-run.")
        r.raise_for_status()
        data = r.json()
        feats = data.get("features") or []
        tag = path.split("/")[2] if path.count("/") >= 2 else path
        if feats and tag not in self._printed:
            self._printed.add(tag)
            print(f"[keys] {path}: {sorted(feats[0].get('properties', {}).keys())}")
        return data


def load_landmarks() -> list[dict]:
    with (SAMPLE / "stops_landmarks.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["Lat"] = float(r["Lat"]); r["Lon"] = float(r["Lon"])
        r["RadiusMeters"] = float(r.get("RadiusMeters") or 250)
        r["PreferredLines"] = [x.strip() for x in r["PreferredLines"].split(";") if x.strip()]
        r["IsPrimary"] = str(r.get("IsPrimary", "")).lower() == "true"
        r["PollIntervalSeconds"] = int(r.get("PollIntervalSeconds") or 60)
    return rows


def load_wanted_stations() -> list[dict]:
    with (SAMPLE / "metro_stations_wanted.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["Lines"] = [x.strip() for x in r["Lines"].split(";") if x.strip()]
    return rows


def resolve_bus(tmb: Tmb, landmarks: list[dict], max_stops: int):
    lines_fc = tmb.get("/transit/linies/bus")
    line_by_code: dict[str, dict] = {}
    for f in lines_fc.get("features", []):
        p = f.get("properties", {})
        code = str(pick(p, KEY_LINE_NAME, "")).strip()
        if code:
            line_by_code[code] = {
                "LineCode": code,
                "TmbLineId": str(pick(p, KEY_LINE_ID, "")),
                "LineOrigin": str(pick(p, KEY_LINE_ORIGIN, "")),
                "LineDestination": str(pick(p, KEY_LINE_DEST, "")),
            }
    wanted_lines = sorted({ln for lm in landmarks for ln in lm["PreferredLines"]})
    missing = [ln for ln in wanted_lines if ln not in line_by_code]
    if missing:
        print(f"[warn] lines not found in TMB's bus line list, skipped: {missing}")

    # stops per line (cached), with direction if the API exposes it
    stops_of_line: dict[str, list[dict]] = {}
    for ln in wanted_lines:
        if ln not in line_by_code:
            continue
        fc = tmb.get(f"/transit/linies/bus/{line_by_code[ln]['TmbLineId']}/parades")
        out = []
        for f in fc.get("features", []):
            p = f.get("properties", {})
            geom = f.get("geometry") or {}
            coords = geom.get("coordinates") or [None, None]
            if coords[0] is None:
                continue
            out.append({
                "StopCode": int(pick(p, KEY_STOP_ID)),
                "StopName": str(pick(p, KEY_STOP_NAME, "")),
                "Address": str(pick(p, KEY_STOP_ADDR, "")),
                "Direction": str(pick(p, KEY_STOP_DIRECTION, "")),
                "Lon": float(coords[0]), "Lat": float(coords[1]),
            })
        stops_of_line[ln] = out

    # candidate selection
    chosen: dict[int, dict] = {}
    for lm in landmarks:
        for ln in lm["PreferredLines"]:
            cands = []
            for s in stops_of_line.get(ln, []):
                d = haversine_m(lm["Lat"], lm["Lon"], s["Lat"], s["Lon"])
                if d <= lm["RadiusMeters"]:
                    cands.append((d, s))
            cands.sort(key=lambda t: t[0])
            # nearest per direction (or nearest two distinct stops when direction unknown)
            seen_dir: set[str] = set()
            picked = 0
            for d, s in cands:
                key = s["Direction"] or f"_{picked}"
                if key in seen_dir:
                    continue
                seen_dir.add(key)
                picked += 1
                entry = chosen.setdefault(s["StopCode"], {
                    "StopCode": s["StopCode"], "StopName": s["StopName"], "Address": s["Address"],
                    "Zone": lm["Zone"], "Lat": s["Lat"], "Lon": s["Lon"], "Lines": set(),
                    "IsPrimary": False, "PollIntervalSeconds": lm["PollIntervalSeconds"],
                    "_landmark": lm["Landmark"], "_dist": d, "_primary_landmark": lm["IsPrimary"],
                })
                entry["Lines"].add(ln)
                entry["PollIntervalSeconds"] = min(entry["PollIntervalSeconds"], lm["PollIntervalSeconds"])
                if lm["Zone"] == "Venue":
                    entry["Zone"] = "Venue"
                if picked >= 2:
                    break
            if not cands:
                print(f"[info] no stop of line {ln} within {int(lm['RadiusMeters'])} m of '{lm['Landmark']}'")

    # rank: venue first, then multi-line, then distance; cap
    ranked = sorted(chosen.values(), key=lambda e: (e["Zone"] != "Venue", -len(e["Lines"]), e["_dist"]))
    ranked = ranked[:max_stops]
    # primary = nearest stop to the primary landmark among the venue stops
    venue = [e for e in ranked if e["_primary_landmark"]]
    if venue:
        min(venue, key=lambda e: e["_dist"])["IsPrimary"] = True
    ranked.sort(key=lambda e: (not e["IsPrimary"], e["Zone"] != "Venue", e["StopName"]))

    used_lines = sorted({ln for e in ranked for ln in e["Lines"]})
    lines_rows = [dict(line_by_code[ln], LineName=f"{ln} {line_by_code[ln]['LineOrigin']} - {line_by_code[ln]['LineDestination']}".strip()) for ln in used_lines]
    return ranked, lines_rows


def resolve_metro(tmb: Tmb, wanted: list[dict]):
    lines_fc = tmb.get("/transit/linies/metro")
    metro_lines: dict[str, str] = {}
    for f in lines_fc.get("features", []):
        p = f.get("properties", {})
        metro_lines[str(pick(p, KEY_LINE_NAME, "")).strip()] = str(pick(p, KEY_LINE_ID, ""))
    stations: dict[str, dict] = {}
    for w in wanted:
        target = norm(w["StationName"])
        for ln in w["Lines"]:
            if ln not in metro_lines:
                print(f"[warn] metro line {ln} not found"); continue
            fc = tmb.get(f"/transit/linies/metro/{metro_lines[ln]}/estacions")
            best = None
            for f in fc.get("features", []):
                p = f.get("properties", {})
                name = str(pick(p, KEY_STATION_NAME, ""))
                n = norm(name)
                score = 2 if n == target else (1 if target in n or n in target else 0)
                if score and (best is None or score > best[0]):
                    coords = (f.get("geometry") or {}).get("coordinates") or [None, None]
                    best = (score, {"StationCode": int(pick(p, KEY_STATION_ID)), "StationName": name,
                                    "Lon": coords[0], "Lat": coords[1]})
            if best is None:
                print(f"[info] station '{w['StationName']}' not found on {ln}"); continue
            st = stations.setdefault(best[1]["StationCode"], dict(best[1], Lines=set(), Zone=w["Zone"]))
            st["Lines"].add(ln)
    return sorted(stations.values(), key=lambda s: (s["Zone"] != "Venue", s["StationName"]))


def write_csv(path: Path, rows: list[dict], columns: list[str], dry_run: bool):
    print(f"\n== {path.relative_to(ROOT)} ({len(rows)} rows)")
    for r in rows:
        print("   ", {c: r.get(c) for c in columns})
    if dry_run:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c) for c in columns})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-stops", type=int, default=16)
    ap.add_argument("--dry-run", action="store_true", help="print, don't write")
    args = ap.parse_args()

    app_id, app_key = os.environ.get("TMB_APP_ID"), os.environ.get("TMB_APP_KEY")
    if not app_id or not app_key:
        sys.exit("Set TMB_APP_ID and TMB_APP_KEY (create an application at https://developer.tmb.cat/).")
    tmb = Tmb(app_id, app_key)

    stops, lines = resolve_bus(tmb, load_landmarks(), args.max_stops)
    for s in stops:
        s["Lines"] = ";".join(sorted(s["Lines"]))
        s["IsPrimary"] = "true" if s["IsPrimary"] else "false"
        s["Lat"] = round(s["Lat"], 6); s["Lon"] = round(s["Lon"], 6)
    write_csv(SAMPLE / "stops.csv", stops,
              ["StopCode", "StopName", "Address", "Zone", "Lat", "Lon", "Lines", "IsPrimary", "PollIntervalSeconds"], args.dry_run)
    write_csv(SAMPLE / "lines.csv", lines,
              ["LineCode", "LineName", "LineOrigin", "LineDestination", "TmbLineId"], args.dry_run)

    metro = resolve_metro(tmb, load_wanted_stations())
    for m in metro:
        m["Lines"] = ";".join(sorted(m["Lines"]))
    write_csv(SAMPLE / "metro_stations.csv", metro,
              ["StationCode", "StationName", "Lines", "Zone", "Lat", "Lon"], args.dry_run)

    if not stops or not any(s["IsPrimary"] == "true" for s in stops):
        print("\n[warn] no primary venue stop resolved -- check the Venue landmarks' lines/radius before using stops.csv")
    print("\nReview the CSVs, then commit them. The first row of stops.csv is <VENUE_STOP_CODE> for Labs 02/05.")


if __name__ == "__main__":
    main()

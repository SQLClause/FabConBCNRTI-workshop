#!/usr/bin/env python3
"""
build_stops_from_osm.py -- build artifacts/SampleData/stops.csv and lines.csv from OpenStreetMap, no TMB key needed.

OSM bus stops in Barcelona carry TMB's stop code in the `ref` tag (spot-checked against tmb.cat: 2689
"Diagonal Mar", 2265 "Pg Taulat - Diagonal Mar", 2683 "Rambla de Prim - Metro La Pau", 1265 "Pg de Sant
Joan - Còrsega"), plus coordinates and, for most stops, the lines serving them in `route_ref`. That's
everything StopsDim needs and everything the Function needs for TMB_IBUS_STOPS.

Inputs  : artifacts/SampleData/stops_landmarks.csv  (Zone, Landmark, Lat, Lon, PreferredLines, RadiusMeters, IsPrimary, PollIntervalSeconds)
Outputs : artifacts/SampleData/stops.csv, artifacts/SampleData/lines.csv
Cache   : infra/out/osm_bus_stops.json (re-used if younger than --max-cache-age hours)

Usage:
    python3 infra/build_stops_from_osm.py [--max-stops 16] [--dry-run] [--refresh]

The API-based resolver (resolve_stops.py) remains the alternative if you'd rather use TMB's own Transit API;
either way, commit the generated CSVs and don't regenerate them on the day.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "artifacts" / "SampleData"
CACHE = ROOT / "infra" / "out" / "osm_bus_stops.json"

# Barcelona bounding box (south, west, north, east) -- covers every landmark with margin
BBOX = "41.35,2.10,41.47,2.25"
OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]
QUERY = f'[out:json][timeout:90];node["highway"="bus_stop"]["ref"]({BBOX});out;'

# Line origins/destinations as shown on tmb.cat's line pages (checked 2026-09-24); only used for LinesDim's
# display columns. Lines not listed here get empty origin/destination.
LINE_INFO = {
    "H16": ("Pg. Zona Franca", "Fòrum Campus Besòs"),
    "7":   ("Fòrum", "Zona Universitària"),
    "136": ("Pg. Marítim", "Verneda"),
    "V31": ("Fòrum", "Trinitat Vella"),
    "V27": ("Pg. Marítim", "Canyelles"),
    "V21": ("Pg. Marítim", "Montbau"),
    "V19": ("Barceloneta", "Pl. Alfonso Comín"),
    "V15": ("Barceloneta", "Av. Tibidabo"),
    "H10": ("Pl. Sants", "Olímpic de Badalona"),
    "H12": ("Gornal", "Besòs Verneda"),
    "D20": ("Pg. Marítim", "Ernest Lluch"),
    "47":  ("Pg. Marítim", "Canyelles"),
    "59":  ("Poblenou", "Pl. Reina Maria Cristina"),
    "19":  ("Pl. Catalunya", "Sant Genís"),
    "33":  ("Zona Universitària", "Verneda"),
}


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def fetch_osm(refresh: bool, max_age_h: float) -> list[dict]:
    if CACHE.exists() and not refresh and (time.time() - CACHE.stat().st_mtime) < max_age_h * 3600:
        print(f"[cache] using {CACHE.relative_to(ROOT)}")
        return json.loads(CACHE.read_text(encoding="utf-8"))["elements"]
    body = urllib.parse.urlencode({"data": QUERY}).encode()
    last = None
    for url in OVERPASS_ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=body, headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "FabConBCNRTI-workshop stops builder (contact: workshop presenter)",
            })
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(data), encoding="utf-8")
            print(f"[osm] {len(data.get('elements', []))} bus stops with a ref from {url}")
            return data["elements"]
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"[warn] {url}: {exc}")
    sys.exit(f"Overpass failed on every endpoint: {last}")


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


def stop_lines(tags: dict) -> set[str]:
    raw = tags.get("route_ref") or ""
    return {x.strip() for x in raw.replace(",", ";").replace(" ", ";").split(";") if x.strip()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-stops", type=int, default=16)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="ignore the cached Overpass result")
    ap.add_argument("--max-cache-age", type=float, default=24 * 7, help="hours")
    args = ap.parse_args()

    elements = fetch_osm(args.refresh, args.max_cache_age)
    stops = []
    for el in elements:
        t = el.get("tags", {})
        ref = t.get("ref", "")
        if not ref.isdigit() or len(ref) > 5:  # TMB codes are 1-5 digits; AMB/others use other formats
            continue
        stops.append({"StopCode": int(ref), "StopName": t.get("name", "").strip(), "Lat": el["lat"], "Lon": el["lon"],
                      "lines": stop_lines(t), "operator": t.get("operator", "")})

    # Stops operated by AMB / interurban operators share names with TMB stops near the venue but aren't
    # served by TMB's iTransit bus endpoint; keep TMB-operated or unattributed stops only.
    stops = [s for s in stops if not any(x in s["operator"] for x in ("Àrea Metropolitana", "ATM", "AMB"))]

    landmarks = load_landmarks()
    chosen: dict[int, dict] = {}
    for lm in landmarks:
        pref = set(lm["PreferredLines"])
        cands = []
        for s in stops:
            served = s["lines"] & pref
            if not served:
                continue
            d = haversine_m(lm["Lat"], lm["Lon"], s["Lat"], s["Lon"])
            if d <= lm["RadiusMeters"]:
                cands.append((-len(served), d, s))
        cands.sort(key=lambda c: (c[0], c[1]))
        # Venue landmarks may contribute up to 4 stops (both directions of both lines); others up to 2
        per_landmark = 4 if lm["Zone"] == "Venue" else 2
        matched_lines: set[str] = set()
        for _neg, d, s in cands[:per_landmark]:
            e = chosen.setdefault(s["StopCode"], {
                **{k: s[k] for k in ("StopCode", "StopName", "Lat", "Lon")},
                "Address": "", "Zone": lm["Zone"], "Lines": set(), "IsPrimary": False,
                "PollIntervalSeconds": lm["PollIntervalSeconds"], "_dist": d, "_primary_lm": lm["IsPrimary"],
                "_landmark": lm["Landmark"],
            })
            e["Lines"] |= s["lines"]
            e["_dist"] = min(e["_dist"], d)
            e["PollIntervalSeconds"] = min(e["PollIntervalSeconds"], lm["PollIntervalSeconds"])
            if lm["Zone"] == "Venue":
                e["Zone"] = "Venue"
            matched_lines |= s["lines"] & pref
        missing = pref - matched_lines
        if not cands:
            print(f"[warn] '{lm['Landmark']}': no TMB stop of {sorted(pref)} within {int(lm['RadiusMeters'])} m -- widen the radius or change the lines")
        elif missing:
            print(f"[info] '{lm['Landmark']}': lines {sorted(missing)} not found nearby (OSM route_ref may be incomplete); kept {len(cands[:per_landmark])} stop(s)")

    # Global cap: every venue stop first, then one stop per remaining landmark (round-robin), then the rest by line count
    venue_stops = [e for e in chosen.values() if e["Zone"] == "Venue"]
    others = [e for e in chosen.values() if e["Zone"] != "Venue"]
    by_lm: dict[str, list[dict]] = {}
    for e in sorted(others, key=lambda e: (-len(e["Lines"]), e["_dist"])):
        by_lm.setdefault(e["_landmark"], []).append(e)
    ranked = list(venue_stops)
    rounds = max((len(v) for v in by_lm.values()), default=0)
    for i in range(rounds):
        for lm_name in by_lm:
            if i < len(by_lm[lm_name]) and len(ranked) < args.max_stops:
                ranked.append(by_lm[lm_name][i])
    ranked = ranked[: args.max_stops]
    venue = [e for e in ranked if e["Zone"] == "Venue" and e["_primary_lm"]]
    if venue:
        min(venue, key=lambda e: e["_dist"])["IsPrimary"] = True
    ranked.sort(key=lambda e: (not e["IsPrimary"], e["Zone"] != "Venue", e["Zone"], e["StopName"]))

    wanted_lines = sorted({ln for lm in landmarks for ln in lm["PreferredLines"]})
    used_lines = sorted({ln for e in ranked for ln in e["Lines"] if ln in wanted_lines})

    print(f"\n== stops.csv ({len(ranked)} stops)")
    for e in ranked:
        print(f"   {e['StopCode']:>5}  {e['Zone']:<11} {'*' if e['IsPrimary'] else ' '} {e['StopName']:<40} {e['Lat']:.5f},{e['Lon']:.5f}  {';'.join(sorted(l for l in e['Lines'] if l in wanted_lines))}")
    print(f"\n== lines.csv ({len(used_lines)} lines): {', '.join(used_lines)}")
    print(f"\nTMB_IBUS_STOPS={','.join(str(e['StopCode']) for e in ranked)}")

    if args.dry_run:
        return
    with (SAMPLE / "stops.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["StopCode", "StopName", "Address", "Zone", "Lat", "Lon", "Lines", "IsPrimary", "PollIntervalSeconds"])
        for e in ranked:
            w.writerow([e["StopCode"], e["StopName"], e["Address"], e["Zone"], f"{e['Lat']:.6f}", f"{e['Lon']:.6f}",
                        ";".join(sorted(l for l in e["Lines"] if l in wanted_lines)), "true" if e["IsPrimary"] else "false",
                        e["PollIntervalSeconds"]])
    with (SAMPLE / "lines.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["LineCode", "LineName", "LineOrigin", "LineDestination", "TmbLineId"])
        for ln in used_lines:
            o, d = LINE_INFO.get(ln, ("", ""))
            w.writerow([ln, f"{ln} {o} - {d}".strip(), o, d, ""])
    print(f"\nWrote {SAMPLE / 'stops.csv'} and {SAMPLE / 'lines.csv'}. Review, commit, and set TMB_IBUS_STOPS as printed above.")


if __name__ == "__main__":
    main()

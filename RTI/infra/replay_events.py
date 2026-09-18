#!/usr/bin/env python3
"""
replay_events.py -- re-publish a recording of real TMB events to Event Hubs when the live feed is down.

The recording is an export of BusArrivalsRaw (or MetroArrivalsRaw) from the dry run: CSV (as the Fabric
KQL editor exports it) or JSON lines, one event per row. Timestamps are shifted so the first event is
"now" and the original spacing is preserved; the event body otherwise matches the data-feed contract
exactly, so every lab step runs unchanged.

    pip install azure-eventhub
    export EVENTHUB_SEND_CONNECTION_STRING="Endpoint=sb://...;SharedAccessKeyName=function-send;..."
    python3 infra/replay_events.py infra/out/recording-bus.csv --hub tmb-ibus-a --loop
    python3 infra/replay_events.py infra/out/recording-metro.csv --hub tmb-metro-a --loop --speed 1
    (run one process per hub: -a and -b for each feed)

Stop with Ctrl+C.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

INT_FIELDS = {"StopCode", "StationCode", "Rank", "MinutesToArrival", "SecondsToArrival"}
BOOL_FIELDS = {"IsStale"}
DROP_FIELDS = {"$IngestionTime", "IngestionTime"}  # Fabric export extras


def parse_ts(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def coerce(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if k in DROP_FIELDS or k is None:
            continue
        if v is None or v == "":
            out[k] = None
        elif k in INT_FIELDS:
            out[k] = int(float(v))
        elif k in BOOL_FIELDS:
            out[k] = str(v).strip().lower() in ("true", "1", "yes")
        else:
            out[k] = v
    return out


def load(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    rows: list[dict] = []
    if path.suffix.lower() in (".jsonl", ".ndjson") or text.lstrip().startswith("{"):
        for line in text.splitlines():
            line = line.strip()
            if line:
                rows.append(coerce(json.loads(line)))
    elif text.lstrip().startswith("["):
        rows = [coerce(r) for r in json.loads(text)]
    else:
        rows = [coerce(r) for r in csv.DictReader(text.splitlines())]
    rows = [r for r in rows if r.get("PolledAtUtc")]
    rows.sort(key=lambda r: parse_ts(r["PolledAtUtc"]))
    if not rows:
        sys.exit("No rows with PolledAtUtc found in the recording.")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recording", type=Path)
    ap.add_argument("--hub", required=True, help="tmb-ibus-a, tmb-ibus-b, tmb-metro-a or tmb-metro-b")
    ap.add_argument("--speed", type=float, default=1.0, help="2 = twice as fast as recorded")
    ap.add_argument("--loop", action="store_true", help="start over when the recording ends")
    ap.add_argument("--dry-run", action="store_true", help="print instead of sending")
    args = ap.parse_args()

    rows = load(args.recording)
    span = parse_ts(rows[-1]["PolledAtUtc"]) - parse_ts(rows[0]["PolledAtUtc"])
    print(f"Loaded {len(rows)} events spanning {span}; replaying to '{args.hub}' at {args.speed}x"
          f"{' (loop)' if args.loop else ''}.")

    producer = None
    if not args.dry_run:
        try:
            from azure.eventhub import EventData, EventHubProducerClient
        except ImportError:
            sys.exit("pip install azure-eventhub")
        cs = os.environ.get("EVENTHUB_SEND_CONNECTION_STRING")
        if not cs:
            sys.exit("Set EVENTHUB_SEND_CONNECTION_STRING (the function-send policy from create-eventhubs.sh).")
        producer = EventHubProducerClient.from_connection_string(cs, eventhub_name=args.hub)

    key_field = "StationCode" if "metro" in args.hub else "StopCode"

    try:
        while True:
            t0_rec = parse_ts(rows[0]["PolledAtUtc"])
            t0_now = datetime.now(timezone.utc)
            # group rows by original poll timestamp so each poll cycle is one batch
            i = 0
            sent = 0
            while i < len(rows):
                ts = parse_ts(rows[i]["PolledAtUtc"])
                batch_rows = []
                while i < len(rows) and parse_ts(rows[i]["PolledAtUtc"]) == ts:
                    batch_rows.append(rows[i]); i += 1
                target = t0_now + (ts - t0_rec) / args.speed
                delay = (target - datetime.now(timezone.utc)).total_seconds()
                if delay > 0:
                    time.sleep(delay)
                shifted = datetime.now(timezone.utc).replace(microsecond=0)
                for r in batch_rows:
                    r = dict(r)
                    r["PolledAtUtc"] = shifted.isoformat().replace("+00:00", "Z")
                    if args.dry_run:
                        print(json.dumps(r))
                    else:
                        from azure.eventhub import EventData  # noqa: F811
                        batch = producer.create_batch(partition_key=str(r.get(key_field, "")))
                        batch.add(EventData(json.dumps(r)))
                        producer.send_batch(batch)
                sent += len(batch_rows)
                print(f"{shifted.isoformat()}  sent {len(batch_rows):3d} events  (total {sent})")
            if not args.loop:
                break
            print("Recording finished; looping.")
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        if producer:
            producer.close()


if __name__ == "__main__":
    main()

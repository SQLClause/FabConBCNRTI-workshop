#!/usr/bin/env python3
"""
replay_events.py -- re-publish a recording of real TMB envelopes to Event Hubs when the live feed is down.

The recording is an export of BusArrivalsRaw (or MetroArrivalsRaw) from the dry run: CSV (as the Fabric KQL
editor exports it, with `payload` as a JSON string) or JSON lines, one envelope per row. `fetchedAt` is
shifted so the first envelope is "now" and the original spacing is preserved; `source`, `key` and `payload`
are sent unchanged, so every lab step runs as with the live Function.

    pip install azure-eventhub
    set -a; source infra/out/replay.env; set +a      # EVENTHUB_SEND_CONNECTION_STRING
    python3 infra/replay_events.py infra/out/recording-bus.csv   --hub tmb-ibus-1-65 --loop
    python3 infra/replay_events.py infra/out/recording-metro.csv --hub tmb-metro-1-65 --loop
    (one process per hub: both -1-65 and -66-130 for each feed)

Stop with Ctrl+C.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TIME_FIELD = "fetchedAt"
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
        if k == "payload" and isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                pass
        out[k] = v
    return out


def load(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    rows: list[dict] = []
    stripped = text.lstrip()
    if stripped.startswith(("{", "[")):
        try:  # one JSON document: a single envelope or an array of them
            doc = json.loads(text)
            rows = [coerce(r) for r in (doc if isinstance(doc, list) else [doc])]
        except json.JSONDecodeError:  # JSON lines: one envelope per line
            for line in text.splitlines():
                line = line.strip()
                if line:
                    rows.append(coerce(json.loads(line)))
    else:
        rows = [coerce(r) for r in csv.DictReader(text.splitlines())]
    rows = [r for r in rows if r.get(TIME_FIELD)]
    rows.sort(key=lambda r: parse_ts(r[TIME_FIELD]))
    if not rows:
        sys.exit(f"No rows with {TIME_FIELD} found in the recording.")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recording", type=Path)
    ap.add_argument("--hub", required=True, help="tmb-ibus-1-65, tmb-ibus-66-130, tmb-metro-1-65 or tmb-metro-66-130")
    ap.add_argument("--speed", type=float, default=1.0, help="2 = twice as fast as recorded")
    ap.add_argument("--loop", action="store_true", help="start over when the recording ends")
    ap.add_argument("--dry-run", action="store_true", help="print instead of sending")
    args = ap.parse_args()

    rows = load(args.recording)
    span = parse_ts(rows[-1][TIME_FIELD]) - parse_ts(rows[0][TIME_FIELD])
    print(f"Loaded {len(rows)} envelopes spanning {span}; replaying to '{args.hub}' at {args.speed}x"
          f"{' (loop)' if args.loop else ''}.")

    producer = None
    if not args.dry_run:
        try:
            from azure.eventhub import EventData, EventHubProducerClient
        except ImportError:
            sys.exit("pip install azure-eventhub")
        cs = os.environ.get("EVENTHUB_SEND_CONNECTION_STRING")
        if not cs:
            sys.exit("Set EVENTHUB_SEND_CONNECTION_STRING (infra/out/replay.env from prepare-room.sh).")
        producer = EventHubProducerClient.from_connection_string(cs, eventhub_name=args.hub)

    try:
        while True:
            t0_rec = parse_ts(rows[0][TIME_FIELD])
            t0_now = datetime.now(timezone.utc)
            i = 0
            sent = 0
            while i < len(rows):
                ts = parse_ts(rows[i][TIME_FIELD])
                batch_rows = []
                while i < len(rows) and parse_ts(rows[i][TIME_FIELD]) == ts:
                    batch_rows.append(rows[i]); i += 1
                target = t0_now + (ts - t0_rec) / args.speed
                delay = (target - datetime.now(timezone.utc)).total_seconds()
                if delay > 0:
                    time.sleep(delay)
                shifted = datetime.now(timezone.utc).isoformat()
                if not args.dry_run:
                    from azure.eventhub import EventData  # noqa: F811
                    batch = producer.create_batch()
                for r in batch_rows:
                    r = dict(r)
                    r[TIME_FIELD] = shifted
                    body = json.dumps(r, ensure_ascii=False, separators=(",", ":"))
                    if args.dry_run:
                        print(body[:200])
                    else:
                        try:
                            batch.add(EventData(body))
                        except ValueError:
                            producer.send_batch(batch)
                            batch = producer.create_batch()
                            batch.add(EventData(body))
                if not args.dry_run and len(batch) > 0:
                    producer.send_batch(batch)
                sent += len(batch_rows)
                print(f"{shifted}  sent {len(batch_rows):3d} envelopes  (total {sent})")
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

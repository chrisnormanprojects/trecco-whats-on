"""Validate both downloaded feeds before replacing the published snapshot."""
import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path


def validate(path, start, days):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("status") != "OK":
        raise ValueError(f"{path.name}: feed status is not OK")
    groups = data.get("results")
    if not isinstance(groups, list) or len(groups) != days:
        raise ValueError(f"{path.name}: expected {days} day groups")
    occurrences, ids = set(), set()
    count = 0
    for offset, group in enumerate(groups):
        if not isinstance(group, list):
            raise ValueError(f"{path.name}: invalid day group {offset}")
        expected = (start + timedelta(days=offset)).isoformat()
        for event in group:
            if not isinstance(event, dict) or not str(event.get("name", "")).strip():
                raise ValueError(f"{path.name}: event is missing its name")
            if event.get("datetime") != expected + " 00:00":
                raise ValueError(f"{path.name}: event is in the wrong date group")
            time = event.get("time", "")
            if not isinstance(time, str) or len(time) != 5:
                raise ValueError(f"{path.name}: invalid event time")
            datetime.strptime(time, "%H:%M")
            key = (expected, time, event["name"], event.get("location", ""))
            booking = str(event.get("booking_id", ""))
            if key in occurrences or (booking and booking in ids):
                raise ValueError(f"{path.name}: duplicate event")
            occurrences.add(key)
            if booking:
                ids.add(booking)
            count += 1
    if not count:
        raise ValueError(f"{path.name}: empty feed; retaining the previous snapshot for review")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("start", type=date.fromisoformat)
    parser.add_argument("days", type=int)
    args = parser.parse_args()
    for venue in ("showdome", "pavilion"):
        count = validate(args.directory / f"{venue}.json", args.start, args.days)
        print(f"{venue}: validated {count} events across {args.days} day groups")

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
    occurrences, ids = {}, {}
    count = 0
    for offset, group in enumerate(groups):
        if not isinstance(group, list):
            raise ValueError(f"{path.name}: invalid day group {offset}")
        expected = (start + timedelta(days=offset)).isoformat()
        for event in group:
            if not isinstance(event, dict) or not str(event.get("name", "")).strip():
                raise ValueError(f"{path.name}: event is missing its name")
            actual_datetime = event.get("datetime")
            try:
                actual_date = datetime.strptime(actual_datetime, "%Y-%m-%d %H:%M").date().isoformat()
            except (TypeError, ValueError):
                raise ValueError(
                    f"{path.name}: invalid event datetime "
                    f"(group_index={offset}, expected_date={expected!r}, "
                    f"actual_datetime={actual_datetime!r}, event_name={event['name']!r}, "
                    f"booking_id={event.get('booking_id')!r}, "
                    f"event_time={event.get('time')!r}, location={event.get('location')!r})"
                ) from None
            if actual_date != expected:
                raise ValueError(
                    f"{path.name}: event is in the wrong date group "
                    f"(group_index={offset}, expected_date={expected!r}, "
                    f"actual_datetime={actual_datetime!r}, "
                    f"event_name={event['name']!r}, booking_id={event.get('booking_id')!r}, "
                    f"event_time={event.get('time')!r}, location={event.get('location')!r})"
                )
            time = event.get("time", "")
            if not isinstance(time, str) or len(time) != 5:
                raise ValueError(f"{path.name}: invalid event time")
            datetime.strptime(time, "%H:%M")
            key = (expected, time, event["name"], event.get("location", ""))
            booking = str(event.get("booking_id", ""))
            previous = occurrences.get(key)
            reason = "same date, time, name and location"
            if previous is None and booking:
                previous = ids.get(booking)
                reason = "same booking ID"
            if previous is not None:
                raise ValueError(
                    f"{path.name}: duplicate event ({reason}; "
                    f"first_group_index={previous['group_index']}, "
                    f"first_event={json.dumps(previous['event'], ensure_ascii=False, sort_keys=True)}, "
                    f"duplicate_group_index={offset}, "
                    f"duplicate_event={json.dumps(event, ensure_ascii=False, sort_keys=True)})"
                )
            record = {"group_index": offset, "event": event}
            occurrences[key] = record
            if booking:
                ids[booking] = record
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

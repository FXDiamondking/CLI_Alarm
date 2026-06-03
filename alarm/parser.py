from __future__ import annotations

import shlex
from datetime import datetime, timedelta

# Supported strptime formats — tried in order
_TIME_FORMATS = [
    "%H:%M",        # 14:05
    "%I:%M %p",     # 02:05 PM
    "%I:%M%p",      # 02:05PM
    "%H:%M:%S",     # 14:05:00 (convenience)
]


def parse_time(raw: str) -> datetime:
    """
    Parse a user-supplied time string into a tz-aware local datetime.

    If the resolved time has already passed today, the alarm is scheduled
    for the same time tomorrow.

    Raises ValueError with a human-readable message on bad input.
    """
    raw = raw.strip()
    parsed: datetime | None = None

    for fmt in _TIME_FORMATS:
        try:
            parsed = datetime.strptime(raw, fmt)
            break
        except ValueError:
            continue

    if parsed is None:
        raise ValueError(
            f"Unrecognised time format: '{raw}'. "
            "Use HH:MM (24-hour) or HH:MM AM/PM (12-hour)."
        )

    # Build a tz-aware datetime for today at the parsed hour/minute
    local_now = datetime.now().astimezone()
    local_tz = local_now.tzinfo

    scheduled = local_now.replace(
        hour=parsed.hour,
        minute=parsed.minute,
        second=0,
        microsecond=0,
        tzinfo=local_tz,
    )

    # Advance to tomorrow if the time has already passed
    if scheduled <= local_now:
        scheduled += timedelta(days=1)

    return scheduled


def tokenise(raw_input: str) -> tuple[str, list[str]]:
    """
    Split a raw input line into (command, args).

    Handles quoted strings so labels with spaces work, e.g.:
        add 07:30 "Morning standup"  ->  ("add", ["07:30", "Morning standup"])
    """
    try:
        tokens = shlex.split(raw_input)
    except ValueError:
        # Unmatched quote — treat the whole input as one token so the REPL
        # can report an "unknown command" rather than crashing.
        tokens = raw_input.split()

    if not tokens:
        return ("", [])

    command = tokens[0].lower()
    args = tokens[1:]
    return (command, args)

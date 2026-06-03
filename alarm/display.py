from __future__ import annotations

import sys
import threading
from datetime import datetime

from .models import Alarm, AlarmStatus

# Single lock so scheduler notifications never interleave with REPL output
_print_lock = threading.Lock()


def _print(*args, **kwargs) -> None:
    with _print_lock:
        print(*args, **kwargs)
        sys.stdout.flush()


# ------------------------------------------------------------------
# Startup
# ------------------------------------------------------------------

def print_banner() -> None:
    tz_name = datetime.now().astimezone().strftime("%Z")
    _print("\n  CLI Alarm Clock")
    _print(f"  Timezone: {tz_name}")
    _print("  Commands: add <HH:MM> [label]  |  list  |  update <id> <HH:MM> [label]  |  delete <id>  |  exit")
    _print("  " + "─" * 72 + "\n")


# ------------------------------------------------------------------
# CRUD confirmations
# ------------------------------------------------------------------

def print_alarm_added(alarm: Alarm) -> None:
    label_part = f" — {alarm.label}" if alarm.label else ""
    _print(f"  [+] Alarm #{alarm.id} set for {alarm.formatted_time()}{label_part}")


def print_alarm_updated(alarm: Alarm) -> None:
    label_part = f" — {alarm.label}" if alarm.label else ""
    _print(f"  [~] Alarm #{alarm.id} updated to {alarm.formatted_time()}{label_part}")


def print_alarm_deleted(alarm_id: int) -> None:
    _print(f"  [-] Alarm #{alarm_id} deleted.")


# ------------------------------------------------------------------
# List
# ------------------------------------------------------------------

def print_alarm_list(alarms: list[Alarm]) -> None:
    if not alarms:
        _print("  No alarms scheduled.")
        return

    col_id    = 4
    col_time  = 12
    col_label = 22
    col_status = 9

    header = (
        f"  {'ID':<{col_id}}  {'Time':<{col_time}}  {'Label':<{col_label}}  {'Status':<{col_status}}"
    )
    divider = "  " + "─" * (col_id + col_time + col_label + col_status + 6)

    with _print_lock:
        print(header)
        print(divider)
        for alarm in alarms:
            label = alarm.label if alarm.label else "—"
            status_tag = alarm.status.value
            print(
                f"  {alarm.id:<{col_id}}  {alarm.formatted_time():<{col_time}}  "
                f"{label:<{col_label}}  {status_tag:<{col_status}}"
            )
        sys.stdout.flush()


# ------------------------------------------------------------------
# Notification (called from scheduler thread)
# ------------------------------------------------------------------

def fire_notification(alarm: Alarm) -> None:
    label_part = alarm.label if alarm.label else f"Alarm #{alarm.id}"
    title = f"  ALARM #{alarm.id} — {label_part}  "
    width = len(title)
    border = "  ╔" + "═" * (width - 2) + "╗"
    middle = "  ║" + title[2:]  + "║"
    footer = "  ╚" + "═" * (width - 2) + "╝"

    with _print_lock:
        print()
        print(border)
        print(middle)
        print(footer)
        print()
        sys.stdout.write("\a")   # audible bell
        sys.stdout.flush()


# ------------------------------------------------------------------
# Errors
# ------------------------------------------------------------------

def print_error(message: str) -> None:
    _print(f"  [!] {message}")

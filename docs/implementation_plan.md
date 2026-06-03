# CLI Alarm Clock — Implementation Plan

## Project Layout

```
CLI_Alarm/
├── alarm/
│   ├── __init__.py
│   ├── models.py          # Alarm dataclass and AlarmStatus enum
│   ├── store.py           # In-memory alarm store (CRUD operations)
│   ├── scheduler.py       # Background daemon thread (polling loop)
│   ├── parser.py          # Command-line input tokeniser and time parser
│   ├── display.py         # All terminal output / formatting helpers
│   └── repl.py            # Interactive REPL loop (command dispatcher)
├── main.py                # Entry point — wires everything and starts REPL
├── docs/
│   ├── specs.md
│   └── implementation_plan.md
└── README.md
```

---

## Phase 1 — Data Layer (`models.py`, `store.py`)

### Step 1.1 — `models.py`
Define the core data types.

```
AlarmStatus  (Enum)
    ACTIVE      = "active"
    TRIGGERED   = "triggered"

Alarm  (dataclass)
    id       : int
    time     : datetime          # tz-aware, local timezone
    label    : str = ""
    status   : AlarmStatus = AlarmStatus.ACTIVE
```

- Use `@dataclass` with `slots=True` for clean attribute access.
- Keep `datetime` tz-aware so comparisons never mix naive and aware objects.

### Step 1.2 — `store.py`
Centralised in-memory store; all mutations go through this module.

```
AlarmStore
    _alarms    : list[Alarm]     # ordered by insertion
    _next_id   : int             # starts at 1, increments on every add

    add(time, label) -> Alarm
    get(alarm_id)    -> Alarm | None
    list_all()       -> list[Alarm]            # copy, never the internal list
    update(alarm_id, time=None, label=None) -> Alarm | AlarmStoreError
    delete(alarm_id) -> bool
    mark_triggered(alarm_id) -> None
```

- `AlarmStore` is instantiated once in `main.py` and passed to every other module that needs it (dependency injection, no global state).
- All public methods are thread-safe: protected by a single `threading.Lock` because the scheduler thread will call `mark_triggered` concurrently.

**Errors:** define a thin `AlarmStoreError` exception (subclass of `ValueError`) with a `message` field — avoids leaking internal types to the REPL.

---

## Phase 2 — Input Parsing (`parser.py`)

### Step 2.1 — Time parser
Accepts both 24-hour and 12-hour formats and returns a tz-aware `datetime` for today (or tomorrow if the time has already passed today).

Supported formats:
- `HH:MM` — 24-hour
- `H:MM` — 24-hour, single-digit hour
- `HH:MM AM` / `HH:MM PM` — 12-hour (case-insensitive)

```
parse_time(raw: str) -> datetime          # raises ValueError on bad input
```

Implementation notes:
- Use `datetime.strptime` with a try/except chain over the format list.
- After parsing, attach local timezone via `datetime.now().astimezone().tzinfo`.
- If the resolved time is in the past (already passed for today), advance by one day.

### Step 2.2 — Command tokeniser
```
tokenise(raw_input: str) -> tuple[str, list[str]]
    # returns (command_name, arg_tokens)
    # strips outer quotes from label tokens
```

- Split on whitespace but respect quoted strings (use `shlex.split`).
- First token is the command; the rest are positional arguments.

---

## Phase 3 — Background Scheduler (`scheduler.py`)

### Step 3.1 — Daemon thread
```
AlarmScheduler
    _store     : AlarmStore
    _thread    : threading.Thread   (daemon=True)
    _stop_event: threading.Event

    start() -> None
    stop()  -> None
    _run()  -> None    # private polling loop
```

### Step 3.2 — Polling loop (`_run`)
```
while not _stop_event.is_set():
    now = datetime.now().astimezone()
    for alarm in store.list_all():
        if alarm.status == ACTIVE and now >= alarm.time:
            store.mark_triggered(alarm.id)
            display.fire_notification(alarm)   # prints to terminal
    sleep(1)
```

- Uses `_stop_event.wait(1)` instead of `time.sleep(1)` so `stop()` can unblock it immediately on exit.
- Calls `display.fire_notification` to keep all terminal formatting in one module.

---

## Phase 4 — Display Layer (`display.py`)

All terminal output is routed through this module. No other module calls `print` directly.

```
print_banner()                          # shown on startup
print_alarm_added(alarm: Alarm)
print_alarm_list(alarms: list[Alarm])   # table format
print_alarm_updated(alarm: Alarm)
print_alarm_deleted(alarm_id: int)
print_error(message: str)
fire_notification(alarm: Alarm)         # prominent alert + \a bell
```

### Output format for `list`

```
ID   Time         Label               Status
──   ──────────   ──────────────────  ──────────
1    07:30 IST    Morning standup     active
2    14:00 IST                        triggered
```

### Notification format (fired by scheduler)

```
╔══════════════════════════════╗
║  ALARM #1 — Morning standup  ║
╚══════════════════════════════╝
```
Followed by `\a` (system bell).

---

## Phase 5 — REPL (`repl.py`)

### Step 5.1 — Command dispatcher

```
AlarmRepl
    _store    : AlarmStore
    _parser   : module (parser.py functions)
    _display  : module (display.py functions)

    run() -> None     # blocking loop; exits on "exit" or "quit" or Ctrl-C
    _handle_add(args)
    _handle_list(args)
    _handle_update(args)
    _handle_delete(args)
```

### Step 5.2 — REPL loop

```
display.print_banner()
while True:
    try:
        raw = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        break                         # clean exit on Ctrl-C / Ctrl-D

    if not raw:
        continue
    cmd, args = parser.tokenise(raw)

    match cmd:
        case "add":    _handle_add(args)
        case "list":   _handle_list(args)
        case "update": _handle_update(args)
        case "delete": _handle_delete(args)
        case "exit" | "quit": break
        case _:        display.print_error(f"Unknown command: {cmd}")
```

### Step 5.3 — Handler argument validation

| Handler        | Required args        | Optional args | Validation                         |
|----------------|----------------------|---------------|------------------------------------|
| `_handle_add`  | `time`               | `label`       | valid time format                  |
| `_handle_list` | —                    | —             | none                               |
| `_handle_update`| `id`, `time`        | `label`       | id is int, valid time format       |
| `_handle_delete`| `id`               | —             | id is int                          |

Each handler catches `ValueError` / `AlarmStoreError` and delegates to `display.print_error`.

---

## Phase 6 — Entry Point (`main.py`)

```python
def main():
    store     = AlarmStore()
    scheduler = AlarmScheduler(store)
    repl      = AlarmRepl(store)

    scheduler.start()
    try:
        repl.run()
    finally:
        scheduler.stop()
        print("\nGoodbye.")

if __name__ == "__main__":
    main()
```

- `scheduler.stop()` in `finally` ensures the daemon thread's `_stop_event` is set before the process exits — prevents any stray `print` after the terminal closes.

---

## Implementation Order

| # | File            | Depends on           | Notes                                      |
|---|-----------------|----------------------|--------------------------------------------|
| 1 | `models.py`     | nothing              | Pure data; no imports from this project    |
| 2 | `store.py`      | `models.py`          | Add `threading.Lock` from the start        |
| 3 | `parser.py`     | stdlib only          | Test time parsing with edge cases          |
| 4 | `display.py`    | `models.py`          | Stub all functions first, refine later     |
| 5 | `scheduler.py`  | `store.py`, `display.py` | Manually verify with a 1-min alarm     |
| 6 | `repl.py`       | all above            | Wire command dispatch and error paths      |
| 7 | `main.py`       | all above            | Final integration and clean exit           |

---

## Threading Considerations

| Resource             | Accessed by              | Protection          |
|----------------------|--------------------------|---------------------|
| `AlarmStore._alarms` | REPL thread + scheduler  | `threading.Lock`    |
| `AlarmStore._next_id`| REPL thread only         | same lock (simpler) |
| Terminal output      | REPL thread + scheduler  | `threading.Lock` in `display.py` to prevent interleaved text |

The notification from the scheduler can print mid-prompt. To handle this cleanly, the display lock ensures the full notification block is written atomically before the REPL resumes.

---

## Error Handling Strategy

- `parser.parse_time` raises `ValueError` with a human-readable message.
- `AlarmStore` raises `AlarmStoreError` (subclass of `ValueError`) for business-rule violations.
- REPL handlers catch both, pass the message to `display.print_error`, and return — the loop continues.
- Unexpected exceptions propagate to `main.py` where the `finally` block still runs `scheduler.stop()`.

---

## Standard Library Only

No third-party dependencies. All features rely on:

| Module           | Usage                                      |
|------------------|--------------------------------------------|
| `datetime`       | Time representation and comparison         |
| `threading`      | Daemon thread, Lock, Event                 |
| `time` / `Event` | `wait(1)` in scheduler loop                |
| `shlex`          | Quoted-string-aware tokenisation           |
| `dataclasses`    | `Alarm` model                              |
| `enum`           | `AlarmStatus`                              |
| `zoneinfo`       | Local timezone (Python 3.9+)               |

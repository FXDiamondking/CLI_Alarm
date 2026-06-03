# CLI Alarm Clock

A terminal-only alarm clock written in Python. No web UI, no database, no third-party dependencies — just the standard library.

---

## Features

- **Create** one or many alarms with an optional label
- **List** all alarms with their status in a formatted table
- **Update** an alarm's time or label by its ID
- **Delete** an alarm by its ID
- **Terminal notification** — a boxed alert prints directly in the terminal the moment an alarm fires, along with an audible bell
- **Local timezone aware** — all times use the system's local clock and timezone
- **In-memory** — no files or databases; state lives for the duration of the process

---

## Requirements

- Python 3.10 or later (uses `match/case` and `slots=True` on dataclasses)
- No pip packages required

---

## Quick Start

```bash
git clone <repo-url>
cd CLI_Alarm
python3 main.py
```

---

## Usage

The app runs as an interactive prompt. Type a command and press Enter.

```
> add <HH:MM> [label]
> list
> update <id> <HH:MM> [label]
> delete <id>
> exit
```

### Commands

| Command | Description |
|---|---|
| `add <HH:MM> [label]` | Create a new alarm. Label is optional. |
| `list` | Print all alarms with ID, time, label, and status. |
| `update <id> <HH:MM> [label]` | Change the time and/or label of an active alarm. |
| `delete <id>` | Remove an alarm permanently (for this session). |
| `exit` / `quit` | Shut down the app cleanly. `Ctrl-C` also works. |

### Time formats accepted

| Format | Example |
|---|---|
| 24-hour | `14:30` |
| 12-hour with space | `02:30 PM` |
| 12-hour no space | `02:30pm` |

If the specified time has already passed today, the alarm is automatically scheduled for the same time tomorrow.

---

## Example Session

```
$ python3 main.py

  CLI Alarm Clock
  Timezone: IST
  Commands: add <HH:MM> [label]  |  list  |  update <id> <HH:MM> [label]  |  delete <id>  |  exit
  ────────────────────────────────────────────────────────────────────────────────

> add 07:30 "Morning standup"
  [+] Alarm #1 set for 07:30 IST — Morning standup

> add 13:00 Lunch
  [+] Alarm #2 set for 13:00 IST — Lunch

> list
  ID    Time          Label                   Status
  ─────────────────────────────────────────────────────
  1     07:30 IST     Morning standup         active
  2     13:00 IST     Lunch                   active

> update 1 08:00 "Updated standup"
  [~] Alarm #1 updated to 08:00 IST — Updated standup

> delete 2
  [-] Alarm #2 deleted.

> list
  ID    Time          Label                   Status
  ─────────────────────────────────────────────────────
  1     08:00 IST     Updated standup         active

> exit

Goodbye.
```

### When an alarm fires

```
  ╔══════════════════════════════════╗
  ║  ALARM #1 — Updated standup      ║
  ╚══════════════════════════════════╝
```

The prompt returns immediately after the notification so you can continue using the app.

---

## Project Structure

```
CLI_Alarm/
├── main.py                 # Entry point — wires everything and starts REPL
├── alarm/
│   ├── models.py           # Alarm dataclass and AlarmStatus enum
│   ├── store.py            # In-memory alarm store (thread-safe CRUD)
│   ├── scheduler.py        # Background daemon thread (polls every second)
│   ├── parser.py           # Time parser and command tokeniser
│   ├── display.py          # All terminal output and formatting
│   └── repl.py             # Interactive REPL loop and command dispatcher
├── tests/
│   └── manual/
│       ├── scenarios.md    # 25 structured manual test cases
│       └── quick_commands.txt  # Copy-paste command blocks for quick smoke testing
└── docs/
    ├── specs.md            # Full feature specification
    └── implementation_plan.md  # Phase-by-phase implementation plan
```

---

## Architecture Notes

- **Thread safety** — a `threading.Lock` in `AlarmStore` and `display.py` ensures the scheduler thread (which fires alarms) never races with the REPL thread (which handles user input).
- **Daemon thread** — the scheduler runs as a daemon so it exits automatically when the main process ends. `_stop_event.wait(1)` is used instead of `time.sleep(1)` so `stop()` can unblock it immediately.
- **No globals** — `AlarmStore` is instantiated once in `main.py` and injected into both the scheduler and the REPL.

---

## Limitations

- State is lost when the process exits (by design — no persistence).
- No recurring or repeating alarms.
- No snooze.
- Sound is limited to the terminal bell character (`\a`); no audio file playback.

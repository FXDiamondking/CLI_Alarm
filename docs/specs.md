# CLI Alarm Clock — Specification

## Overview

A terminal-only alarm clock application written in Python. No web UI, no database. All alarm state is held in memory for the duration of the process.

---

## User Functionalities

### 1. Create Alarm
- The user can create a new alarm by specifying a time and an optional label.
- Multiple alarms can be created and all are active simultaneously.
- Each alarm is assigned a unique ID upon creation.

**Input:**
- Time: `HH:MM` (24-hour) or `HH:MM AM/PM` (12-hour)
- Label (optional): a short description string

**Output:**
- Confirmation message with the assigned alarm ID and scheduled time.

---

### 2. List Alarms
- The user can view all currently scheduled alarms.
- Display includes: ID, label, scheduled time, and status (active / triggered).

---

### 3. Update Alarm
- The user can modify an existing alarm identified by its ID.
- Fields that can be updated: time, label.
- Only active (not yet triggered) alarms can be updated.

---

### 4. Delete Alarm
- The user can remove an alarm by its ID.
- Deletion is immediate and permanent for the session.

---

### 5. Terminal Notification
- When the scheduled time is reached, the application prints a prominent alert directly in the terminal.
- The alert includes the alarm ID and label.
- A system bell character (`\a`) is emitted to produce an audible beep where supported.

---

## System Functionalities

### 1. Local Time and Timezone
- All times are resolved against the system's local clock and timezone.
- `datetime.now()` with `tzinfo` from the local system is used — no UTC conversion is forced on the user.
- The active timezone is displayed in all time-related output for clarity.

### 2. In-Memory Storage
- All alarm data lives in a Python data structure (list of dicts or dataclass instances) for the lifetime of the process.
- No files, databases, or external services are used.
- Data is lost when the process exits — this is intentional.

---

## Data Model

Each alarm is represented as:

| Field      | Type      | Description                              |
|------------|-----------|------------------------------------------|
| `id`       | `int`     | Auto-incrementing unique identifier      |
| `label`    | `str`     | Optional user-provided description       |
| `time`     | `datetime`| Scheduled fire time (local tz-aware)     |
| `status`   | `str`     | `"active"` or `"triggered"`             |

---

## CLI Interface

The application runs as an interactive REPL loop. The user types commands at a prompt.

```
> add 07:30 "Morning standup"
> add 14:00
> list
> update 1 08:00 "Updated standup"
> delete 2
> exit
```

### Commands

| Command                              | Description                        |
|--------------------------------------|------------------------------------|
| `add <HH:MM> [label]`               | Create a new alarm                 |
| `list`                               | List all alarms                    |
| `update <id> <HH:MM> [label]`       | Update an existing alarm           |
| `delete <id>`                        | Delete an alarm by ID              |
| `exit` / `quit`                      | Exit the application               |

---

## Background Alarm Checker

- A background thread runs a polling loop (every second) that compares the current local time against all active alarms.
- When a match is found (current time >= alarm time and alarm is active), the thread prints the notification and marks the alarm as `"triggered"`.
- The thread is a daemon thread so it exits automatically when the main process ends.

---

## Error Handling

| Scenario                        | Behaviour                                    |
|---------------------------------|----------------------------------------------|
| Invalid time format             | Print error, prompt user to retry            |
| ID not found (update/delete)    | Print error message                          |
| Updating a triggered alarm      | Print error, inform alarm already fired      |
| Empty alarm list on `list`      | Print "No alarms scheduled"                  |

---

## Non-Goals

- No persistence between sessions.
- No recurring / repeating alarms.
- No snooze functionality.
- No web UI or REST API.
- No sound file playback (only system bell).

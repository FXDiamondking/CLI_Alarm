# Manual Test Scenarios — CLI Alarm Clock

Start the app before each scenario:
```
python3 main.py
```

---

## TC-01 — Startup banner

**Steps:**
1. Run `python3 main.py`

**Expected:**
- Banner prints with app name, current timezone (e.g. `IST`), and command reference.
- Prompt `> ` appears.

---

## TC-02 — Add a single alarm (24-hour format)

**Steps:**
```
> add 23:59
```

**Expected:**
```
  [+] Alarm #1 set for 23:59 IST
```

---

## TC-03 — Add alarm with a label

**Steps:**
```
> add 07:30 "Morning standup"
```

**Expected:**
```
  [+] Alarm #1 set for 07:30 IST — Morning standup
```

---

## TC-04 — Add alarm using 12-hour AM/PM format

**Steps:**
```
> add 07:30 AM Breakfast
> add 02:00 PM Lunch
```

**Expected:**
- Alarm 1 set for 07:30.
- Alarm 2 set for 14:00 (displayed as 14:00).

---

## TC-05 — Add multiple alarms

**Steps:**
```
> add 06:00 "Wake up"
> add 08:00 "Gym"
> add 13:00 "Lunch"
```

**Expected:**
- Three alarms created with IDs 1, 2, 3.

---

## TC-06 — List all alarms

**Steps (after TC-05):**
```
> list
```

**Expected:**
```
  ID    Time          Label                   Status
  ─────────────────────────────────────────────────────
  1     06:00 IST     Wake up                 active
  2     08:00 IST     Gym                     active
  3     13:00 IST     Lunch                   active
```

---

## TC-07 — List with no alarms

**Steps (fresh session):**
```
> list
```

**Expected:**
```
  No alarms scheduled.
```

---

## TC-08 — Update alarm time

**Steps:**
```
> add 09:00 "Meeting"
> update 1 10:00
```

**Expected:**
```
  [~] Alarm #1 updated to 10:00 IST — Meeting
```
- Label is preserved when not supplied.

---

## TC-09 — Update alarm time and label

**Steps:**
```
> add 09:00 "Meeting"
> update 1 10:30 "Team sync"
```

**Expected:**
```
  [~] Alarm #1 updated to 10:30 IST — Team sync
```

---

## TC-10 — Delete an alarm

**Steps:**
```
> add 07:00 "Wake"
> add 08:00 "Gym"
> delete 1
> list
```

**Expected:**
- Only alarm #2 remains in the list.
```
  [-] Alarm #1 deleted.
```

---

## TC-11 — Alarm fires in terminal (notification test)

**Steps:**
1. Check the current time (e.g. 14:32).
2. Set an alarm 1–2 minutes ahead:
   ```
   > add 14:34
   ```
3. Wait at the prompt without typing.

**Expected (when time is reached):**
```
  ╔══════════════════════════════╗
  ║  ALARM #2 — Alarm #2         ║
  ╚══════════════════════════════╝
```
- Terminal bell sounds (if terminal supports it).
- Prompt `> ` returns immediately after.

---

## TC-12 — Triggered alarm shows in list

**Steps (after TC-11 fires):**
```
> list
```

**Expected:**
- The fired alarm shows `triggered` in the Status column.

---

## TC-13 — Cannot update a triggered alarm

**Steps (after TC-11 fires):**
```
> update 1 15:00
```

**Expected:**
```
  [!] Alarm #1 has already triggered and cannot be updated.
```

---

## TC-14 — Past time auto-advances to tomorrow

**Steps:**
```
> add 00:01
```

**Expected:**
- Alarm is set for 00:01 **tomorrow** (since 00:01 today has passed).
- Confirm via `list` — the date shown should be tomorrow if your terminal shows dates.

---

## TC-15 — Invalid time format

**Steps:**
```
> add 25:00
> add abc
> add 7:99
```

**Expected for each:**
```
  [!] Unrecognised time format: '...'. Use HH:MM (24-hour) or HH:MM AM/PM (12-hour).
```
- App does not crash; prompt returns.

---

## TC-16 — Update/delete non-existent alarm

**Steps:**
```
> update 99 08:00
> delete 99
```

**Expected:**
```
  [!] Alarm #99 not found.
```

---

## TC-17 — Invalid ID (non-integer)

**Steps:**
```
> delete abc
> update xyz 08:00
```

**Expected:**
```
  [!] Invalid ID 'abc' — must be a whole number.
```

---

## TC-18 — Unknown command

**Steps:**
```
> foo
> help
```

**Expected:**
```
  [!] Unknown command: 'foo'. Type 'exit' to quit.
```

---

## TC-19 — Empty input (blank line)

**Steps:**
- Press Enter several times at the prompt.

**Expected:**
- Prompt `> ` re-appears silently. No error.

---

## TC-20 — Exit with `exit` and `quit`

**Steps:**
```
> exit
```
Then restart and try:
```
> quit
```

**Expected:**
```
Goodbye.
```
- Process terminates cleanly.

---

## TC-21 — Exit with Ctrl-C

**Steps:**
- Press `Ctrl+C` at the prompt.

**Expected:**
```
Goodbye.
```
- Process terminates; no traceback printed.

---

## TC-22 — Missing required arguments

**Steps:**
```
> add
> update
> update 1
> delete
```

**Expected per command:**
```
  [!] Usage: add <HH:MM> [label]
  [!] Usage: update <id> <HH:MM> [label]
  [!] Usage: update <id> <HH:MM> [label]
  [!] Usage: delete <id>
```

---

## TC-23 — Label with spaces (quoted and unquoted)

**Steps:**
```
> add 09:00 "Team daily standup"
> add 10:00 Quick coffee break
```

**Expected:**
- Alarm 1 label: `Team daily standup`
- Alarm 2 label: `Quick coffee break`

---

## TC-24 — Multiple alarms fire close together

**Steps:**
1. Note current time (e.g. 15:10).
2. Set two alarms 1 minute apart:
   ```
   > add 15:11 "First"
   > add 15:11 "Second"
   ```
3. Wait.

**Expected:**
- Both notification boxes print without overlapping or garbling each other.

---

## TC-25 — Alarm ID increments correctly after delete

**Steps:**
```
> add 07:00 A
> add 08:00 B
> delete 1
> add 09:00 C
> list
```

**Expected:**
- IDs in list: `2` (B) and `3` (C). ID `1` is gone; `3` is not reused as `1`.

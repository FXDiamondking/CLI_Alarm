from __future__ import annotations

from . import display, parser
from .store import AlarmStore, AlarmStoreError


class AlarmRepl:
    def __init__(self, store: AlarmStore) -> None:
        self._store = store

    def run(self) -> None:
        display.print_banner()
        while True:
            try:
                raw = input("> ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw:
                continue

            cmd, args = parser.tokenise(raw)

            match cmd:
                case "add":
                    self._handle_add(args)
                case "list":
                    self._handle_list()
                case "update":
                    self._handle_update(args)
                case "delete":
                    self._handle_delete(args)
                case "exit" | "quit":
                    break
                case "":
                    continue
                case _:
                    display.print_error(f"Unknown command: '{cmd}'. Type 'exit' to quit.")

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_add(self, args: list[str]) -> None:
        if not args:
            display.print_error("Usage: add <HH:MM> [label]")
            return
        try:
            alarm_time = parser.parse_time(args[0])
        except ValueError as e:
            display.print_error(str(e))
            return

        label = " ".join(args[1:]) if len(args) > 1 else ""
        alarm = self._store.add(alarm_time, label)
        display.print_alarm_added(alarm)

    def _handle_list(self) -> None:
        display.print_alarm_list(self._store.list_all())

    def _handle_update(self, args: list[str]) -> None:
        if len(args) < 2:
            display.print_error("Usage: update <id> <HH:MM> [label]")
            return

        alarm_id = self._parse_id(args[0])
        if alarm_id is None:
            return

        try:
            alarm_time = parser.parse_time(args[1])
        except ValueError as e:
            display.print_error(str(e))
            return

        label = " ".join(args[2:]) if len(args) > 2 else None

        try:
            alarm = self._store.update(alarm_id, time=alarm_time, label=label)
            display.print_alarm_updated(alarm)
        except AlarmStoreError as e:
            display.print_error(str(e))

    def _handle_delete(self, args: list[str]) -> None:
        if not args:
            display.print_error("Usage: delete <id>")
            return

        alarm_id = self._parse_id(args[0])
        if alarm_id is None:
            return

        try:
            self._store.delete(alarm_id)
            display.print_alarm_deleted(alarm_id)
        except AlarmStoreError as e:
            display.print_error(str(e))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_id(self, raw: str) -> int | None:
        try:
            return int(raw)
        except ValueError:
            display.print_error(f"Invalid ID '{raw}' — must be a whole number.")
            return None

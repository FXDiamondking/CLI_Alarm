from __future__ import annotations

import threading
from datetime import datetime

from .models import Alarm, AlarmStatus


class AlarmStoreError(ValueError):
    pass


class AlarmStore:
    def __init__(self) -> None:
        self._alarms: list[Alarm] = []
        self._next_id: int = 1
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add(self, time: datetime, label: str = "") -> Alarm:
        with self._lock:
            alarm = Alarm(id=self._next_id, time=time, label=label)
            self._alarms.append(alarm)
            self._next_id += 1
            return alarm

    def update(self, alarm_id: int, time: datetime | None = None, label: str | None = None) -> Alarm:
        with self._lock:
            alarm = self._find(alarm_id)
            if alarm is None:
                raise AlarmStoreError(f"Alarm #{alarm_id} not found.")
            if not alarm.is_active():
                raise AlarmStoreError(f"Alarm #{alarm_id} has already triggered and cannot be updated.")
            if time is not None:
                alarm.time = time
            if label is not None:
                alarm.label = label
            return alarm

    def delete(self, alarm_id: int) -> bool:
        with self._lock:
            alarm = self._find(alarm_id)
            if alarm is None:
                raise AlarmStoreError(f"Alarm #{alarm_id} not found.")
            self._alarms.remove(alarm)
            return True

    def mark_triggered(self, alarm_id: int) -> None:
        with self._lock:
            alarm = self._find(alarm_id)
            if alarm is not None:
                alarm.status = AlarmStatus.TRIGGERED

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, alarm_id: int) -> Alarm | None:
        with self._lock:
            return self._find(alarm_id)

    def list_all(self) -> list[Alarm]:
        with self._lock:
            return list(self._alarms)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find(self, alarm_id: int) -> Alarm | None:
        # caller must hold the lock
        for alarm in self._alarms:
            if alarm.id == alarm_id:
                return alarm
        return None

from __future__ import annotations

import threading
from datetime import datetime

from . import display
from .models import AlarmStatus
from .store import AlarmStore


class AlarmScheduler:
    def __init__(self, store: AlarmStore) -> None:
        self._store = store
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True, name="alarm-scheduler")

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop_event.wait(1):
            now = datetime.now().astimezone()
            for alarm in self._store.list_all():
                if alarm.status == AlarmStatus.ACTIVE and now >= alarm.time:
                    self._store.mark_triggered(alarm.id)
                    display.fire_notification(alarm)

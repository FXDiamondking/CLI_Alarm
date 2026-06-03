from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AlarmStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"


@dataclass(slots=True)
class Alarm:
    id: int
    time: datetime          # tz-aware, local timezone
    label: str = ""
    status: AlarmStatus = field(default=AlarmStatus.ACTIVE)

    def is_active(self) -> bool:
        return self.status == AlarmStatus.ACTIVE

    def formatted_time(self) -> str:
        tz_name = self.time.strftime("%Z")
        return self.time.strftime(f"%H:%M {tz_name}")

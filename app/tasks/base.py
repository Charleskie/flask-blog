from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence


TaskRunner = Callable[["Flask"], int | None]


@dataclass(frozen=True)
class ScheduledTask:
    task_id: str
    description: str
    trigger_args: Mapping[str, str | int]
    runner: TaskRunner
    source: str = "project"
    enabled: bool = True
    disabled_reason: str | None = None
    command_preview: Sequence[str] = field(default_factory=tuple)
    working_directory: str | None = None

    def cron_summary(self) -> str:
        parts = []
        for key in ("minute", "hour", "day", "month", "day_of_week"):
            value = self.trigger_args.get(key)
            if value is not None:
                parts.append(f"{key}={value}")
        return ", ".join(parts)


__all__ = ["ScheduledTask", "TaskRunner"]


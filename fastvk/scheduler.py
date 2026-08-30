from __future__ import annotations

import asyncio
import inspect
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger("fastvk.scheduler")


def _parse_interval(value: float | str) -> float:
    """Accept seconds as a number, or a short string like ``"5m"``, ``"2h"``, ``"1d"``."""
    if isinstance(value, (int, float)):
        return float(value)
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    text = value.strip().lower()
    if text[-1] in units:
        return float(text[:-1]) * units[text[-1]]
    return float(text)


@dataclass
class _Job:
    func: Callable[..., Any]
    interval: float
    next_run: float
    name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

    async def run(self) -> None:
        try:
            result = self.func(*self.args, **self.kwargs)
            if inspect.isawaitable(result):
                await result
        except Exception:
            logger.exception("Scheduled job %r failed", self.name)


class Scheduler:
    """
    Minimal in-process interval scheduler.

    ```python
    scheduler = Scheduler()

    @scheduler.every("30m")
    async def refresh() -> None:
        ...

    @scheduler.at("09:00")
    async def morning_digest() -> None:
        ...

    # start alongside the bot
    async def on_start(bot: FastVK) -> None:
        scheduler.bind(bot)
        await scheduler.start()
    ```
    """

    def __init__(self) -> None:
        self._jobs: list[_Job] = []
        self._task: asyncio.Task | None = None
        self._ctx: dict[type, Any] = {}

    def bind(self, *objects: Any) -> None:
        """Make *objects* injectable into jobs by their type (e.g. the bot)."""
        for obj in objects:
            self._ctx[type(obj)] = obj

    def every(
        self, interval: float | str, *, name: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Run the decorated coroutine every *interval* (seconds or ``"5m"`` / ``"2h"``)."""
        seconds = _parse_interval(interval)

        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._jobs.append(
                _Job(
                    func=fn,
                    interval=seconds,
                    next_run=time.time() + seconds,
                    name=name or fn.__name__,
                )
            )
            return fn

        return deco

    def at(
        self, hhmm: str, *, name: str | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Run the decorated coroutine once per day at ``"HH:MM"`` (local time)."""
        hour, minute = (int(x) for x in hhmm.split(":"))

        def _next_after(now: datetime) -> float:
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            return target.timestamp()

        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._jobs.append(
                _Job(
                    func=fn,
                    interval=86400,
                    next_run=_next_after(datetime.now()),
                    name=name or fn.__name__,
                )
            )
            return fn

        return deco

    def add_job(
        self,
        func: Callable[..., Any],
        interval: float | str,
        *args: Any,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        seconds = _parse_interval(interval)
        self._jobs.append(
            _Job(
                func=func,
                interval=seconds,
                next_run=time.time() + seconds,
                name=name or getattr(func, "__name__", "job"),
                args=args,
                kwargs=kwargs,
            )
        )

    def _inject(self, job: _Job) -> None:
        if job.args or job.kwargs:
            return
        try:
            hints = {
                p.name: p.annotation
                for p in inspect.signature(job.func).parameters.values()
                if p.annotation is not inspect.Parameter.empty
            }
        except (TypeError, ValueError):
            hints = {}
        job.kwargs = {
            name: self._ctx[ann] for name, ann in hints.items() if ann in self._ctx
        }

    async def _loop(self) -> None:
        for job in self._jobs:
            self._inject(job)
        while True:
            now = time.time()
            due = [j for j in self._jobs if j.next_run <= now]
            for job in due:
                asyncio.create_task(job.run())
                job.next_run = now + job.interval
            await asyncio.sleep(1.0)

    async def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop())
            logger.info("Scheduler started with %d job(s)", len(self._jobs))

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            self._task = None


__all__ = ["Scheduler"]

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import FastVK


def render_prometheus(app: FastVK) -> str:
    """Render :class:`~fastvk.FastVK` runtime stats in Prometheus text format."""
    stats = app._stats
    started = stats.get("started_at")
    uptime = time.monotonic() - started if started else 0.0
    lines: list[str] = [
        "# HELP fastvk_updates_total Total updates received.",
        "# TYPE fastvk_updates_total counter",
        f"fastvk_updates_total {stats.get('total', 0)}",
        "# HELP fastvk_updates_handled_total Updates matched by a handler.",
        "# TYPE fastvk_updates_handled_total counter",
        f"fastvk_updates_handled_total {stats.get('handled', 0)}",
        "# HELP fastvk_errors_total Updates that raised during processing.",
        "# TYPE fastvk_errors_total counter",
        f"fastvk_errors_total {stats.get('errors', 0)}",
        "# HELP fastvk_uptime_seconds Seconds since the bot started.",
        "# TYPE fastvk_uptime_seconds gauge",
        f"fastvk_uptime_seconds {uptime:.1f}",
        "# HELP fastvk_inflight_updates Updates currently being processed.",
        "# TYPE fastvk_inflight_updates gauge",
        f"fastvk_inflight_updates {len(getattr(app, '_tasks', ()))}",
        "# HELP fastvk_updates_by_type_total Updates received, by event type.",
        "# TYPE fastvk_updates_by_type_total counter",
    ]
    for event_type, count in stats.get("by_type", {}).items():
        safe = str(event_type).replace('"', '\\"')
        lines.append(f'fastvk_updates_by_type_total{{type="{safe}"}} {count}')
    return "\n".join(lines) + "\n"


__all__ = ["render_prometheus"]

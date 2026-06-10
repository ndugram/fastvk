from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DashboardConfig:
    dashboard: bool = True
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8080


class BaseDashboard:
    config: DashboardConfig = DashboardConfig()

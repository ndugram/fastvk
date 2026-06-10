from __future__ import annotations

import pytest

from fastvk.dashboard.config import BaseDashboard, DashboardConfig


class TestDashboardConfig:
    def test_defaults(self) -> None:
        cfg = DashboardConfig()
        assert cfg.dashboard is True
        assert cfg.dashboard_host == "127.0.0.1"
        assert cfg.dashboard_port == 8080

    def test_custom_values(self) -> None:
        cfg = DashboardConfig(dashboard=False, dashboard_host="0.0.0.0", dashboard_port=9000)
        assert cfg.dashboard is False
        assert cfg.dashboard_host == "0.0.0.0"
        assert cfg.dashboard_port == 9000

    def test_partial_override(self) -> None:
        cfg = DashboardConfig(dashboard_port=3000)
        assert cfg.dashboard is True
        assert cfg.dashboard_host == "127.0.0.1"
        assert cfg.dashboard_port == 3000

    def test_equality(self) -> None:
        assert DashboardConfig() == DashboardConfig()
        assert DashboardConfig(dashboard_port=1234) != DashboardConfig(dashboard_port=5678)


class TestBaseDashboard:
    def test_default_config(self) -> None:
        db = BaseDashboard()
        assert isinstance(db.config, DashboardConfig)
        assert db.config.dashboard is True

    def test_subclass_override(self) -> None:
        class MyDash(BaseDashboard):
            config = DashboardConfig(dashboard_host="0.0.0.0", dashboard_port=9999)

        db = MyDash()
        assert db.config.dashboard_host == "0.0.0.0"
        assert db.config.dashboard_port == 9999

    def test_disabled_via_subclass(self) -> None:
        class DisabledDash(BaseDashboard):
            config = DashboardConfig(dashboard=False)

        assert DisabledDash().config.dashboard is False

    def test_multiple_subclasses_independent(self) -> None:
        class DashA(BaseDashboard):
            config = DashboardConfig(dashboard_port=8001)

        class DashB(BaseDashboard):
            config = DashboardConfig(dashboard_port=8002)

        assert DashA().config.dashboard_port == 8001
        assert DashB().config.dashboard_port == 8002


class TestFastVKDashboardIntegration:
    def test_dashboard_none_by_default(self) -> None:
        from fastvk import FastVK

        app = FastVK(token="fake", group_id=1)
        assert app._dashboard is None

    def test_dashboard_accepts_base_dashboard(self) -> None:
        from fastvk import FastVK

        db = BaseDashboard()
        app = FastVK(token="fake", group_id=1, dashboard=db)
        assert app._dashboard is db

    def test_dashboard_config_accessible(self) -> None:
        from fastvk import FastVK

        class MyDash(BaseDashboard):
            config = DashboardConfig(dashboard_host="0.0.0.0", dashboard_port=7070)

        db = MyDash()
        app = FastVK(token="fake", group_id=1, dashboard=db)
        assert app._dashboard.config.dashboard_host == "0.0.0.0"
        assert app._dashboard.config.dashboard_port == 7070

    def test_dashboard_disabled_flag(self) -> None:
        from fastvk import FastVK

        class OffDash(BaseDashboard):
            config = DashboardConfig(dashboard=False)

        app = FastVK(token="fake", group_id=1, dashboard=OffDash())
        assert app._dashboard.config.dashboard is False

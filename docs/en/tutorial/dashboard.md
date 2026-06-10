# Dashboard

FastVK ships with a built-in web dashboard that shows live bot statistics: uptime, total updates handled, errors, and a rolling event log.

## Setup

Define a `BaseDashboard` subclass with a `DashboardConfig` and pass an instance to `FastVK`:

```python
from fastvk import FastVK
from fastvk.dashboard import BaseDashboard, DashboardConfig

class MyDashboard(BaseDashboard):
    config = DashboardConfig(
        dashboard_host="127.0.0.1",
        dashboard_port=8080,
    )

bot = FastVK(
    token=TOKEN,
    group_id=GROUP_ID,
    dashboard=MyDashboard(),
)
```

Open `http://127.0.0.1:8080` while the bot is running.

## Separate settings file

Keep dashboard config in its own file (e.g. `settings.py`):

```python title="settings.py"
from fastvk.dashboard import BaseDashboard, DashboardConfig

class Dashboard(BaseDashboard):
    config = DashboardConfig(
        dashboard_host="127.0.0.1",
        dashboard_port=8000,
    )

dashboard = Dashboard()
```

```python title="bot.py"
from fastvk import FastVK
from settings import dashboard

bot = FastVK(token=TOKEN, group_id=GROUP_ID, dashboard=dashboard)
```

## Disabling the dashboard

Pass `dashboard=None` (the default) or set `dashboard=False` in `DashboardConfig`:

```python
# completely disabled (default)
bot = FastVK(token=TOKEN, group_id=GROUP_ID)

# object present but server won't start
class OffDash(BaseDashboard):
    config = DashboardConfig(dashboard=False)

bot = FastVK(token=TOKEN, group_id=GROUP_ID, dashboard=OffDash())
```

## DashboardConfig reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dashboard` | `bool` | `True` | Start the dashboard server |
| `dashboard_host` | `str` | `"127.0.0.1"` | Bind host |
| `dashboard_port` | `int` | `8080` | Bind port |

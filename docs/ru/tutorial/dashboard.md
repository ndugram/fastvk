# Дашборд

FastVK включает встроенный веб-дашборд с живой статистикой бота: аптайм, всего апдейтов, ошибки и лог событий.

## Настройка

Создай подкласс `BaseDashboard` с `DashboardConfig` и передай экземпляр в `FastVK`:

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

Открой `http://127.0.0.1:8080` пока бот работает.

## Отдельный файл настроек

Выноси конфиг дашборда в отдельный файл (например `settings.py`):

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

## Отключение дашборда

Передай `dashboard=None` (по умолчанию) или выставь `dashboard=False` в `DashboardConfig`:

```python
# полностью отключён (по умолчанию)
bot = FastVK(token=TOKEN, group_id=GROUP_ID)

# объект есть, но сервер не запустится
class OffDash(BaseDashboard):
    config = DashboardConfig(dashboard=False)

bot = FastVK(token=TOKEN, group_id=GROUP_ID, dashboard=OffDash())
```

## Справка по DashboardConfig

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `dashboard` | `bool` | `True` | Запустить сервер дашборда |
| `dashboard_host` | `str` | `"127.0.0.1"` | Хост |
| `dashboard_port` | `int` | `8080` | Порт |

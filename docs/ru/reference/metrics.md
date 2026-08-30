# Метрики и health

## Эндпоинты

| Где | Путь | Ответ |
|---|---|---|
| Webhook-сервер | `GET /health` | `{"status": "ok"}` |
| Webhook-сервер и дашборд | `GET /metrics` | Текстовая экспозиция Prometheus |

## render_prometheus

```python
from fastvk.metrics import render_prometheus

text = render_prometheus(bot)   # bot: FastVK
```

## Экспортируемые серии

| Метрика | Тип | Значение |
|---|---|---|
| `fastvk_updates_total` | counter | Получено апдейтов |
| `fastvk_updates_handled_total` | counter | Апдейтов обработано хэндлером |
| `fastvk_errors_total` | counter | Апдейтов с исключением при обработке |
| `fastvk_uptime_seconds` | gauge | Секунд с момента старта |
| `fastvk_inflight_updates` | gauge | Апдейтов обрабатывается прямо сейчас |
| `fastvk_updates_by_type_total{type="…"}` | counter | Апдейтов по типу события |

## Конфиг скрейпа Prometheus

```yaml
scrape_configs:
  - job_name: fastvk
    static_configs:
      - targets: ["bot-host:8080"]   # порт webhook или порт дашборда
```

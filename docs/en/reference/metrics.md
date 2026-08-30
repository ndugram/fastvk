# Metrics & health

## Endpoints

| Where | Path | Response |
|---|---|---|
| Webhook server | `GET /health` | `{"status": "ok"}` |
| Webhook server & dashboard | `GET /metrics` | Prometheus text exposition |

## render_prometheus

```python
from fastvk.metrics import render_prometheus

text = render_prometheus(bot)   # bot: FastVK
```

## Exposed series

| Metric | Type | Meaning |
|---|---|---|
| `fastvk_updates_total` | counter | Updates received |
| `fastvk_updates_handled_total` | counter | Updates matched by a handler |
| `fastvk_errors_total` | counter | Updates that raised during processing |
| `fastvk_uptime_seconds` | gauge | Seconds since start |
| `fastvk_inflight_updates` | gauge | Updates currently being processed |
| `fastvk_updates_by_type_total{type="…"}` | counter | Updates per event type |

## Prometheus scrape config

```yaml
scrape_configs:
  - job_name: fastvk
    static_configs:
      - targets: ["bot-host:8080"]   # webhook port, or the dashboard port
```

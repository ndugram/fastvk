# Webhook

FastVK поддерживает два способа получения событий от VK:

| Режим | Как работает | Лучше для |
|---|---|---|
| **Long Polling** | Бот опрашивает серверы VK каждые ~25 с | Разработка, простые боты |
| **Webhook** | VK пушит события на твой сервер | Продакшн, низкая задержка |

## Как работает VK Callback API

1. Ты регистрируешь публичный HTTPS URL в настройках группы (API → Callback API).
2. VK отправляет одноразовый **confirmation**-запрос — сервер должен ответить строкой подтверждения.
3. После подтверждения VK отправляет каждое событие `POST`-запросом на твой URL.
4. Сервер отвечает `"ok"` на каждое событие.

## Что нужно заранее

- Публичный HTTPS URL. Для локальной разработки подойдут [ngrok](https://ngrok.com/) или [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
- **Строка подтверждения** из настроек группы → API → Callback API.

## Базовое использование

```python
import os
from fastvk import FastVK, Command
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Привет через webhook!")


bot.run_webhook(
    confirmation_token=os.environ["VK_CONFIRMATION"],
    host="0.0.0.0",
    port=8080,
    path="/vk",
)
```

## Параметры

```python
bot.run_webhook(
    confirmation_token="abc123",  # обязательно — из настроек группы VK
    host="0.0.0.0",              # интерфейс (по умолчанию: "0.0.0.0")
    port=8080,                   # порт (по умолчанию: 8080)
    path="/vk",                  # путь URL (по умолчанию: "/")
    secret="my_secret",          # опционально — секретный ключ VK
)
```

## Секретный ключ

VK может включать секретную строку в каждый webhook-запрос. Задай её в настройках группы и передай то же значение в `run_webhook`. Запросы с неверным или отсутствующим секретом отклоняются с HTTP 403.

```python
bot.run_webhook(
    confirmation_token="abc123",
    secret="my_secret",
)
```

## Локальная разработка через ngrok

```bash
ngrok http 8080
```

Скопируй `https://`-URL, который выдаст ngrok (например, `https://abc123.ngrok-free.app`), и вставь в настройки группы как URL для Callback API. Используй `/vk` как путь:

```
https://abc123.ngrok-free.app/vk
```

Затем запусти бота:

```bash
VK_TOKEN=... VK_GROUP_ID=... VK_CONFIRMATION=... python bot.py
```

## Совместимость с lifespan и dashboard

Webhook-режим поддерживает контекстный менеджер `lifespan` и встроенный дашборд так же, как и long polling:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    print("Бот запускается")
    yield
    print("Бот останавливается")

bot = FastVK(
    token="...",
    group_id=123,
    lifespan=lifespan,
    dashboard=True,
    dashboard_port=8090,
)

bot.run_webhook(confirmation_token="abc123", port=8080)
```

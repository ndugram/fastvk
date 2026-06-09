# Webhook

FastVK supports two ways to receive events from VK:

| Mode | How it works | Best for |
|---|---|---|
| **Long Polling** | Bot polls VK servers every ~25 s | Development, simple bots |
| **Webhook** | VK pushes events to your server | Production, low latency |

## How VK Callback API works

1. You register a public HTTPS URL in your group settings (API → Callback API).
2. VK sends a one-time **confirmation** request — your server must respond with the confirmation code.
3. After confirmation, VK sends every event as a `POST` request to your URL.
4. Your server responds with `"ok"` for each event.

## Prerequisites

- A public HTTPS URL. For local development you can use [ngrok](https://ngrok.com/) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
- The **confirmation code** from VK group settings → API → Callback API.

## Basic usage

```python
import os
from fastvk import FastVK, Command
from fastvk.types import Message

bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))


@bot.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Hello from webhook!")


bot.run_webhook(
    confirmation_token=os.environ["VK_CONFIRMATION"],
    host="0.0.0.0",
    port=8080,
    path="/vk",
)
```

## Parameters

```python
bot.run_webhook(
    confirmation_token="abc123",  # required — from VK group settings
    host="0.0.0.0",              # interface to bind (default: "0.0.0.0")
    port=8080,                   # port to listen on (default: 8080)
    path="/vk",                  # URL path (default: "/")
    secret="my_secret",          # optional — VK secret key for verification
)
```

## Secret key

VK can include a secret string in every webhook request. Set it in your group settings and pass the same value to `run_webhook`. Requests with a wrong or missing secret are rejected with HTTP 403.

```python
bot.run_webhook(
    confirmation_token="abc123",
    secret="my_secret",
)
```

## Local development with ngrok

```bash
ngrok http 8080
```

Copy the `https://` URL ngrok gives you (e.g. `https://abc123.ngrok-free.app`) and paste it into VK group settings as the callback URL. Use `/vk` as the path:

```
https://abc123.ngrok-free.app/vk
```

Then start your bot:

```bash
VK_TOKEN=... VK_GROUP_ID=... VK_CONFIRMATION=... python bot.py
```

## Combining with lifespan and dashboard

Webhook mode supports both the `lifespan` context manager and the built-in dashboard exactly like long polling:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    print("Bot starting")
    yield
    print("Bot stopping")

bot = FastVK(
    token="...",
    group_id=123,
    lifespan=lifespan,
    dashboard=True,
    dashboard_port=8090,
)

bot.run_webhook(confirmation_token="abc123", port=8080)
```

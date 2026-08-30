# Changelog

All notable changes to FastVK are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Changed (behaviour)

- **The sender is no longer fetched on every update.** Previously every
  `message_new` / `message_event` / `group_join` / `group_leave` /
  `wall_post_new` triggered a `users.get` call. Now the `User` is resolved
  **lazily** — only when a handler declares a `user: User` parameter (or calls
  `await message.get_user()`). `message.from_user` is `None` until resolved.
  This roughly halves the API calls for a typical echo bot.

### Fixed

- Filters are now evaluated with **short-circuit** semantics — the first
  failing filter stops evaluation instead of running all of them.
- Middleware can now pass data into handlers: values placed in the middleware
  `data` dict are injected by type (`data[MyType] = obj` → `handler(obj: MyType)`).
- All HTTP requests now use a **timeout** (`FastVK(timeout=30.0)`); the Long
  Poll request gets its own longer timeout derived from `wait`.
- Update processing tasks are **tracked and drained** on shutdown instead of
  being fire-and-forget; optional `FastVK(max_concurrency=N)` bounds parallelism.
- `SIGTERM` / `SIGINT` now trigger a graceful shutdown (Docker/systemd-friendly).
- Retry now also covers VK error codes **6** (too-many-requests) and **29**
  (rate limit) in addition to 1, 9, 10.
- Webhook and Long Poll updates are **de-duplicated by `event_id`** (VK retries
  Callback API deliveries).
- Handler exceptions in `_process_update` are logged instead of bubbling into
  an unretrieved task.

### Added

- **Captcha handling** — `FastVK(...).bot.set_captcha_handler(async (sid, img) -> answer)`
  or `Bot(captcha_handler=...)`; the failed call is retried with the answer.
- **`bot.execute(code)`** and **`bot.execute_batch([(method, params), ...])`**
  for batching up to 25 API calls into one request.
- **`bot.download(url, dest=None)`** helper.
- **Typed attachments** (`fastvk.types`): `Photo`, `Video`, `Audio`, `Document`,
  `AudioMessage`, `Sticker`, `Graffiti`, `Link`, `Poll`, `WallPost`, plus
  `Message.typed_attachments`, `.photos`, `.docs`, `.videos`, `.audio_messages`,
  `.sticker`, `.content_type`, `.content_types`, `.has_attachment(...)`.
  `Photo.largest` / `Photo.url` give the best size.
- **New filters**: `Regexp` (injects `match: re.Match`), `ContentType`,
  `HasAttachment`; `Command(..., ignore_case=True)`.
- **`Message.answer_media_group([...])`** and **`Message.answer_carousel(...)`**.
- **`Carousel`** template builder and **`Button.vkapps(...)`** (open VK Mini App).
- **`CallbackQuery.edit_message(...)`** and `CallbackQuery.answer(app_hash=...)`.
- **`Router.middleware()`** — per-router middleware, plus `Router.startup` /
  `Router.shutdown` lifecycle decorators.
- **`fastvk.Scheduler`** — in-process interval / daily scheduler
  (`@scheduler.every("30m")`, `@scheduler.at("09:00")`).
- **`fastvk.middleware.i18n`** — `I18n` (JSON catalogs) + `I18nMiddleware`.
- **User Long Poll** — `FastVK(token=USER_TOKEN, polling="user")`.
- **`fastvk.test`** — `MockedBot`, `message_update()`, `callback_update()`,
  `dispatch()` for unit-testing handlers without a token.
- **CLI** — `fastvk new <name>` scaffolds a project, `fastvk run <module>` runs it.
- **`/metrics`** (Prometheus text) and **`/health`** endpoints in webhook mode;
  `/metrics` is also served by the dashboard.

### Tooling

- `mypy` is now part of `[dev]` and runs in CI along with `ruff` on
  `fastvk/` and `tests/`.

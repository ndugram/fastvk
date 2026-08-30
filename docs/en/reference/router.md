# Router

`Router` registers handlers and composes sub-routers. `Bot` / `FastVK` inherits from it.

## Handler decorators

### @router.message

```python
@router.message(*filters)
async def handler(message: Message, ...) -> None: ...
```

Registers a handler for `message_new` events.

### @router.callback

```python
@router.callback(*filters)
async def handler(callback: CallbackQuery, ...) -> None: ...
```

Registers a handler for `message_event` (callback button press) events.

### @router.error

```python
@router.error()
async def handler(error: Exception, ...) -> None: ...
```

Registers a global error handler. Called when any other handler raises.

## Router-level filters

```python
router = Router()
router.message.filter(IsAdmin())
router.callback.filter(IsAdmin())
```

All handlers on this router will only receive events where `IsAdmin()` returns `True`.

## Event decorators

Besides `@router.message` / `@router.callback`:

```python
@router.message_reply()     @router.message_allow()   @router.message_edit()
@router.group_join()        @router.group_leave()     @router.wall_post_new()
@router.on("photo_new")     # any raw event type by name
```

## Middleware

```python
router.middleware(mw) -> mw
```

Registers a middleware that wraps this router's handlers (and its
sub-routers'). `mw(call_next, event, data)` — same contract as
`BaseMiddleware`. Values placed in `data` are injected into handlers by type.

## Lifecycle hooks

```python
@router.startup
async def on_start(bot: FastVK) -> None: ...

@router.shutdown
async def on_stop() -> None: ...
```

Run once on start / stop, with DI by type. `FastVK` invokes the hooks of
itself and every included router.

## include_router

```python
router.include_router(other_router: Router) -> None
```

Merge all handlers from `other_router` into this router (handlers resolved in registration order).

## Dependency injection

Handler parameters are resolved by type:

```python
async def handler(
    message: Message,      # the event object
    user: User,            # fetched automatically for message_new
    state: FSMContext,     # FSM context for this user+chat
    bot: Bot,              # the bot instance
) -> None: ...
```

Custom types can be injected via middleware by adding them to `data` dict.

## Handler resolution order

1. Handlers registered first take priority.
2. If a handler's filters pass, it handles the event and stops processing.
3. Router-level filters are checked before handler-level filters.
4. Sub-router handlers are checked after parent-router handlers.

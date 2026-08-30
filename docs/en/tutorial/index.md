# Tutorial

This tutorial covers all major FastVK features step by step.

- [First steps](first-steps.md) — install, first bot, run.
- [Handlers](handlers.md) — `@bot.message()`, `@bot.callback()`, group events, user long poll, startup/shutdown.
- [Filters](filters.md) — `Command`, `Text`, `F`, `StateFilter`, `Regexp`, `ContentType`.
- [Message](message.md) — `answer()`, media shortcuts, edit, pin, typing.
- [Attachments](attachments.md) — typed photo/doc/video accessors, content-type filters.
- [Keyboard](keyboard.md) — `Button`, `Keyboard`, `Carousel`, inline and regular.
- [FSM](fsm.md) — states, `FSMContext`, storages.
- [Routers](routers.md) — splitting handlers across files.
- [Middleware](middleware.md) — intercepting events, injecting data.
- [Scheduler](scheduler.md) — periodic and daily jobs.
- [i18n](i18n.md) — JSON catalogs and per-user locale.
- [Lifespan](lifespan.md) — startup and shutdown hooks.
- [Exception handling](exceptions.md) — `@bot.exception_handler()`.
- [Testing](testing.md) — `MockedBot`, update factories, `dispatch()`.
- [Command line](cli.md) — `fastvk new`, `fastvk run`.

from __future__ import annotations

import asyncio

import pytest

from fastvk import FastVK
from fastvk.test import MockedBot, message_update
from fastvk.types import Message


@pytest.mark.parametrize("throttle_rate", [0, 1])
async def test_failed_update_can_be_retried(throttle_rate: int) -> None:
    app = FastVK(token="t", throttle_rate=throttle_rate)
    app.bot = MockedBot()
    attempts = 0

    @app.message()
    async def handler(message: Message) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary failure")

    update = message_update("hello", event_id="retry")
    with pytest.raises(RuntimeError, match="temporary failure"):
        await app._process_update(update)
    await app._process_update(update)
    await app._process_update(update)
    assert attempts == 2
    assert app._stats["errors"] == 1
    assert app._stats["handled"] == 1


@pytest.mark.parametrize("failure", [False, True])
async def test_inflight_duplicates_share_the_result(failure: bool) -> None:
    app = FastVK(token="t", throttle_rate=0)
    app.bot = MockedBot()
    started = asyncio.Event()
    release = asyncio.Event()
    attempts = 0

    @app.message()
    async def handler(message: Message) -> None:
        nonlocal attempts
        attempts += 1
        started.set()
        await release.wait()
        if failure:
            raise RuntimeError("temporary failure")

    update = message_update("hello", event_id="shared")
    original = asyncio.create_task(app._process_update(update))
    await asyncio.wait_for(started.wait(), 2)
    duplicate = asyncio.create_task(app._process_update(update))
    await asyncio.sleep(0)
    assert not duplicate.done()
    release.set()
    results = await asyncio.gather(original, duplicate, return_exceptions=True)
    assert attempts == 1
    if failure:
        assert all(isinstance(result, RuntimeError) for result in results)
    else:
        assert results == [None, None]


async def test_cancelling_duplicate_does_not_cancel_original() -> None:
    app = FastVK(token="t", throttle_rate=0)
    app.bot = MockedBot()
    started = asyncio.Event()
    release = asyncio.Event()

    @app.message()
    async def handler(message: Message) -> None:
        started.set()
        await release.wait()

    update = message_update("hello", event_id="shared")
    original = asyncio.create_task(app._process_update(update))
    await asyncio.wait_for(started.wait(), 2)
    duplicate = asyncio.create_task(app._process_update(update))
    await asyncio.sleep(0)
    duplicate.cancel()
    with pytest.raises(asyncio.CancelledError):
        await duplicate
    assert not original.done()
    release.set()
    await original


async def test_drain_cancels_and_awaits_handlers_then_allows_redelivery() -> None:
    app = FastVK(token="t", throttle_rate=0)
    app.bot = MockedBot()
    started = asyncio.Event()
    cleanup = asyncio.Event()
    attempts = 0

    @app.message()
    async def handler(message: Message) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                await asyncio.sleep(0)
                cleanup.set()

    update = message_update("hello", event_id="cancelled")
    task = app._spawn(update)
    await asyncio.wait_for(started.wait(), 2)
    await app._drain(timeout=0)
    assert task.cancelled()
    assert cleanup.is_set()
    await app._process_update(update)
    assert attempts == 2


async def test_event_ids_are_scoped_to_the_group() -> None:
    app = FastVK(token="t", throttle_rate=0)
    app.bot = MockedBot()
    attempts = 0

    @app.message()
    async def handler(message: Message) -> None:
        nonlocal attempts
        attempts += 1

    first = message_update("hello", event_id="same")
    second = first.model_copy(update={"group_id": first.group_id + 1})
    await app._process_update(first)
    await app._process_update(second)
    assert attempts == 2

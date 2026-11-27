from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Callable
from contextlib import ExitStack, asynccontextmanager
from typing import BinaryIO, TypeVar

import aiohttp

_T = TypeVar("_T")
CHUNK_SIZE = 64 * 1024


def remaining_size(stream: BinaryIO) -> int | None:
    if not stream.seekable():
        return None
    position = stream.tell()
    end = stream.seek(0, os.SEEK_END)
    stream.seek(position)
    return max(0, end - position)


async def run_io(operation: Callable[[], _T]) -> _T:
    task = asyncio.create_task(asyncio.to_thread(operation))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        try:
            await task
        finally:
            raise


@asynccontextmanager
async def open_file(opener: Callable[[], BinaryIO]) -> AsyncIterator[BinaryIO]:
    stack = ExitStack()
    try:
        stream = await run_io(lambda: stack.enter_context(opener()))
        yield stream
    finally:
        await run_io(stack.close)


async def read_chunks(stream: BinaryIO) -> AsyncIterator[bytes]:
    while chunk := await run_io(lambda: stream.read(CHUNK_SIZE)):
        yield chunk


class StreamingFilePayload(aiohttp.payload.AsyncIterablePayload):
    def __init__(self, stream: BinaryIO, size: int | None) -> None:
        super().__init__(read_chunks(stream))
        self._size = size

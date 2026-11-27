from __future__ import annotations

import io
import threading
from pathlib import Path
from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from typing_extensions import Self

from fastvk import Bot, Uploader


@pytest.mark.parametrize("use_string_path", [False, True])
async def test_upload_reads_file_outside_event_loop_and_closes_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, use_string_path: bool,
) -> None:
    path = tmp_path / "photo.jpg"
    content = b"test image"
    path.write_bytes(content)
    event_loop_thread = threading.get_ident()
    original_open = io.open
    opened = []

    class CheckedFile:
        def __init__(self, stream: Any) -> None:
            self.stream = stream

        def read(self, size: int = -1) -> bytes:
            assert threading.get_ident() != event_loop_thread
            return self.stream.read(size)

        def __getattr__(self, name: str) -> Any:
            return getattr(self.stream, name)

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            self.stream.close()

    def checked_open(file: Any, *args: Any, **kwargs: Any) -> Any:
        stream = original_open(file, *args, **kwargs)
        if file == path or file == str(path):
            opened.append(stream)
            return CheckedFile(stream)
        return stream

    async def upload(request: web.Request) -> web.Response:
        reader = await request.multipart()
        part = await reader.next()
        assert part is not None
        assert part.filename == "photo.jpg"
        assert part.headers["Content-Type"] == "image/jpeg"
        assert await part.read() == content
        return web.json_response({"file": "uploaded"})

    application = web.Application()
    application.router.add_post("/", upload)
    bot = Bot(token="test-token")
    try:
        async with TestServer(application) as server:
            with monkeypatch.context() as patch:
                patch.setattr("builtins.open", checked_open)
                patch.setattr(io, "open", checked_open)
                result = await Uploader(bot)._upload_file(
                    str(server.make_url("/")),
                    str(path) if use_string_path else path,
                    None,
                    "file",
                )
        assert result == {"file": "uploaded"}
        assert opened
        assert all(stream.closed for stream in opened)
    finally:
        await bot.close()

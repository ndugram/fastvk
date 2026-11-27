from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from fastvk import Uploader
from fastvk.api.client import Bot


class BoundedStream(BytesIO):
    def read(self, size: int = -1) -> bytes:
        assert 0 < size <= 64 * 1024
        return super().read(size)


@pytest.mark.parametrize("source", ["path", "string", "stream"])
@pytest.mark.parametrize("status", [200, 500])
async def test_upload_streams_and_respects_file_ownership(
    source: str, status: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = b"media" * 100_000
    stream = BoundedStream(b"skip" + content)
    stream.seek(4)
    path = tmp_path / "photo.jpg"
    monkeypatch.setattr(Path, "open", lambda *_args, **_kwargs: stream)

    async def upload(request: web.Request) -> web.Response:
        assert request.content_length is not None
        reader = await request.multipart()
        part = await reader.next()
        assert part is not None
        assert part.name == "photo"
        assert part.filename == "custom.jpg"
        received = bytearray()
        while chunk := await part.read_chunk():
            received.extend(chunk)
        assert received == content
        return web.json_response({"photo": "uploaded"}, status=status)

    app = web.Application()
    app.router.add_post("/", upload)
    bot = Bot(token="test-token")
    file = stream if source == "stream" else str(path) if source == "string" else path
    try:
        async with TestServer(app) as server:
            operation = Uploader(bot)._upload_file(str(server.make_url("/")), file, "custom.jpg", "photo")
            if status == 200:
                assert await operation == {"photo": "uploaded"}
            else:
                with pytest.raises(RuntimeError, match="500"):
                    await operation
        assert stream.closed is (source != "stream")
    finally:
        stream.close()
        await bot.close()

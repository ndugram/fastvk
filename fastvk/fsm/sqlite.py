from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

from .storage import BaseStorage, _Key

if TYPE_CHECKING:
    import aiosqlite as _aiosqlite


class SQLiteStorage(BaseStorage):
    """
    FSM storage backed by SQLite. State survives bot restarts.
    No external services required — just a file path.

    Requires ``aiosqlite``: ``pip install aiosqlite``.

    ```python
    from fastvk.fsm.sqlite import SQLiteStorage

    storage = SQLiteStorage("bot.db")
    bot = FastVK(token="...", group_id=123, storage=storage)
    ```
    """

    def __init__(self, path: str = "fastvk_fsm.db", *, table: str = "fastvk_fsm") -> None:
        try:
            import aiosqlite as _  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "SQLiteStorage requires the 'aiosqlite' package. "
                "Install it: pip install aiosqlite"
            ) from e
        self._path = path
        self._table = table
        self._db: _aiosqlite.Connection | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def _conn(self) -> _aiosqlite.Connection:
        async with self._lock:
            if self._db is None:
                import aiosqlite
                self._db = await aiosqlite.connect(self._path)
                self._db.row_factory = aiosqlite.Row
                await self._db.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._table} (
                        peer_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        state  TEXT,
                        data   TEXT NOT NULL DEFAULT '{{}}',
                        PRIMARY KEY (peer_id, user_id)
                    )
                    """
                )
                await self._db.commit()
        return self._db  # type: ignore[return-value]

    async def get_state(self, key: _Key) -> str | None:
        db = await self._conn()
        async with db.execute(
            f"SELECT state FROM {self._table} WHERE peer_id=? AND user_id=?",
            key,
        ) as cur:
            row = await cur.fetchone()
        return row["state"] if row else None

    async def set_state(self, key: _Key, state: str | None) -> None:
        db = await self._conn()
        await db.execute(
            f"""
            INSERT INTO {self._table} (peer_id, user_id, state)
            VALUES (?, ?, ?)
            ON CONFLICT(peer_id, user_id) DO UPDATE SET state=excluded.state
            """,
            (*key, state),
        )
        await db.commit()

    async def get_data(self, key: _Key) -> dict[str, Any]:
        db = await self._conn()
        async with db.execute(
            f"SELECT data FROM {self._table} WHERE peer_id=? AND user_id=?",
            key,
        ) as cur:
            row = await cur.fetchone()
        return json.loads(row["data"]) if row else {}

    async def set_data(self, key: _Key, data: dict[str, Any]) -> None:
        db = await self._conn()
        await db.execute(
            f"""
            INSERT INTO {self._table} (peer_id, user_id, data)
            VALUES (?, ?, ?)
            ON CONFLICT(peer_id, user_id) DO UPDATE SET data=excluded.data
            """,
            (*key, json.dumps(data, ensure_ascii=False)),
        )
        await db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

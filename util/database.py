from asyncio import AbstractEventLoop
from datetime import datetime
from typing import List, Optional, TypedDict

from aiomysql import DictCursor, Pool, create_pool


class PartialMedia(TypedDict):
    dir: str
    created_at: datetime
    uploader: int


class Media(PartialMedia):
    id: int


class User(TypedDict):
    id: int
    permission: int


class MoahNodeDB:
    _instance: Optional[MoahNodeDB] = None

    def __init__(self, pool: Pool):
        self.pool: Pool = pool

    @classmethod
    async def acquire(
        cls,
        host: str,
        port: int,
        user: str,
        password: str,
        db: str,
        loop: Optional[AbstractEventLoop] = None,
        **kwargs,
    ):
        if cls._instance is None:
            pool = await create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                db=db,
                loop=loop,
                autocommit=True,
                cursorclass=DictCursor,
                **kwargs,
            )
            cls._instance = MoahNodeDB(pool=pool)
        return cls._instance

    async def close(self, force: bool = False) -> None:
        self.pool.close()
        self._instance = None
        if not force:
            await self.pool.wait_closed()

    async def get_media(self, media_id: int) -> Optional[Media]:
        query = "SELECT * FROM media WHERE id = %s"
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, media_id)
                return await cursor.fetchone()

    async def insert_media(self, media: PartialMedia) -> None:
        query = "INSERT INTO media (dir, uploader, created_at) VALUES (%s, %s, %s)"
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    query, (media["dir"], media["uploader"], media["created_at"])
                )

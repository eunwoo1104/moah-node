from asyncio import AbstractEventLoop
from datetime import datetime
from typing import Optional, TypedDict

from aiomysql import DictCursor, Pool, create_pool


class PartialMedia(TypedDict):
    dir: str
    uploaded_from: int


class Media(PartialMedia):
    id: int
    created_at: datetime


class CoreData(TypedDict):
    id: int
    auth: str


class MoAhNodeDB:
    def __init__(self, pool: Pool):
        self.__pool: Pool = pool

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
        return cls(pool)

    async def close(self, force: bool = False) -> None:
        self.__pool.close()
        if not force:
            await self.__pool.wait_closed()

    async def get_media(self, media_id: int) -> Optional[Media]:
        query = "SELECT * FROM media WHERE id = %s"
        async with self.__pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, media_id)
                return await cursor.fetchone()

    async def insert_media(self, media: PartialMedia) -> int:
        query = "INSERT INTO media (dir, uploaded_from) VALUES (%s, %s)"
        async with self.__pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (media["dir"], media["uploaded_from"]))
                return cursor.lastrowid

    async def get_core_id(self, key: str) -> Optional[int]:
        query = "SELECT id FROM core WHERE auth = %s"
        async with self.__pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, key)
                data: CoreData = await cursor.fetchone()
                return (bool(data) or None) and data["id"]

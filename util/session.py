from hashlib import sha256
from secrets import token_urlsafe
from typing import Optional

import redis.asyncio as redis


class MediaUploadSessionManager:
    def __init__(self):
        self.__redis = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
            max_connections=10,
        )

    async def close(self) -> None:
        await self.__redis.aclose()

    async def create_session(self, core_id: int) -> str:
        key = token_urlsafe(32)
        await self.__redis.set(
            self.hash_key(key), str(core_id), nx=True, ex=60 * 5  # 5 min
        )
        return key

    async def get_session(self, key: str) -> Optional[str]:
        # TODO: should use context manager so session could be retained on upload fail
        return await self.__redis.getdel(self.hash_key(key))

    @staticmethod
    def hash_key(key: str) -> str:
        return sha256(key.encode()).hexdigest()

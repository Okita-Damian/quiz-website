from arq import create_pool
from arq.connections import RedisSettings

from config.settings import settings

async def get_redis_pool():
    return await create_pool(
        RedisSettings.from_dsn(
            settings.redis_url
        )
    )
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

import config
from database.db_config import create_db_pool, init_db
from handlers import start, bunker_logic

logging.basicConfig(level=logging.INFO)

async def main():
    redis = Redis.from_url(config.REDIS_URL)
    storage = RedisStorage(redis)

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    db_pool = await create_db_pool()
    await init_db(db_pool)

    dp.include_routers(start.router, bunker_logic.router)
    dp["db_pool"] = db_pool

    logging.info("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from aiohttp import web  # Render tekinga o'chirib qo'ymasligi uchun veb-server

import config
from database.db_config import create_db_pool, init_db
from handlers import start, bunker_logic

logging.basicConfig(level=logging.INFO)

# Render uchun soxta veb-sahifa (Sog'lomlik testi uchun)
async def handle_root(request):
    return web.Response(text="Bunker Bot ishlamoqda... 🔒")

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
    
    # Render port talab qilgani uchun aiohttp serverni ham birga ishga tushiramiz
    app = web.Application()
    app.router.add_get('/', handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)  # Render 10000 portni ko'radi
    
    # Ikkala vazifani ham parallel yuritamiz
    await asyncio.gather(
        dp.start_polling(bot),
        site.start()
    )

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Redis o'rniga MemoryStorage
from aiohttp import web

import config
from database.db_config import create_db_pool, init_db
from handlers import start, bunker_logic

logging.basicConfig(level=logging.INFO)

async def handle_root(request):
    return web.Response(text="Bunker Bot ishlamoqda... 🔒")

async def main():
    # Render tekin tarifi uchun xavfsiz va tezkor xotira ombori
    storage = MemoryStorage()

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    db_pool = await create_db_pool()
    await init_db(db_pool)

    dp.include_routers(start.router, bunker_logic.router)
    dp["db_pool"] = db_pool

    logging.info("Bot ishga tushdi!")
    
    app = web.Application()
    app.router.add_get('/', handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    
    await asyncio.gather(
        dp.start_polling(bot),
        site.start()
    )

if __name__ == "__main__":
    asyncio.run(main())

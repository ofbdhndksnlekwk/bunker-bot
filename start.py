import secrets
from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, db_pool):
    user_id = message.from_user.id
    username = message.from_user.username

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if not user:
            bunker_id = secrets.token_hex(4)
            await conn.execute(
                "INSERT INTO users (user_id, username, bunker_id) VALUES ($1, $2, $3)",
                user_id, username, bunker_id
            )
        else:
            bunker_id = user['bunker_id']

    bot_info = await message.bot.get_me()
    anonim_link = f"https://t.me/{bot_info.username}?start={bunker_id}"
    await message.answer(f"🔒 Bunkeringiz tayyor!\n\nHavola: {anonim_link}")
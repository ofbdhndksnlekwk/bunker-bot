from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

class BunkerState(StatesGroup):
    waiting_for_anon_message = State()

@router.message(lambda msg: msg.text and msg.text.startswith("/start "))
async def handle_anon_link(message: types.Message, state: FSMContext, db_pool):
    bunker_id = message.text.split(" ")[1]
    async with db_pool.acquire() as conn:
        target_user = await conn.fetchrow("SELECT user_id FROM users WHERE bunker_id = $1", bunker_id)

    if target_user:
        if target_user['user_id'] == message.from_user.id:
            await message.answer("O'zingizga xabar yubora olmaysiz!")
            return
        await state.update_data(target_user_id=target_user['user_id'])
        await state.set_state(BunkerState.waiting_for_anon_message)
        await message.answer("🔒 Anonim xabaringizni yozing:")
    else:
        await message.answer("Xato havola!")

@router.message(BunkerState.waiting_for_anon_message)
async def send_anon_message(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_id = data.get("target_user_id")
    try:
        await bot.send_message(chat_id=target_id, text=f"📩 Yangi anonim xabar:\n\n{message.text}")
        await message.answer("Yuborildi! ✅")
    except Exception:
        await message.answer("Xatolik bo'ldi.")
    await state.clear()
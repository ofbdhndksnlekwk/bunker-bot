import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, html
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiohttp import web

import config
from database.db_config import create_db_pool, init_db

logging.basicConfig(level=logging.INFO)

# O'YIN MA'LUMOTLARI EMBEDDED (O'yin qiziqarli chiqishi uchun unikal variantlar)
KASBLAR = ["Shifokor", "Muhandis", "Oshpaz", "Harbiy", "Olim", "Dehqon", "Psixolog", "Dasturchi", "Kimyogar", "Uchuvchi"]
SOGLIK = ["Mutlaqo sog'lom", "Yengil allergiya", "Ko'zi ojizroq (ko'zoynakda)", "Yuragi biroz zaif", "Chap oyog'i oqsoqlanadi"]
XOBBI = ["Yulduzlarni kuzatish", "Ovchilik", "Yashirin qurol yasash", "Tibbiy o'tlar yig'ish", "Kitob mutolaasi", "Sport"]
BUYUMLAR = ["Pistolet (3 ta o'q bilan)", "Tibbiy aptechka", "1 yillik konserva", "Filtrli suv idishi", "Arqon va bolta", "Radio"]
FAKTLAR = ["Bunkerni buzib kirish kodini biladi", "Yashirincha o'g'rilik qila oladi", "Aslida u josus", "Stressga juda chidamli"]

KATASTROFALAR = [
    "Yadro urushi boshlandi! Dunyo radiatsiya ostida. Bunker 50 yilga mo'ljallangan.",
    "Zombi apokalipsisi! Shaharlarni zombilar egalladi. Bunker eng xavfsiz joy.",
    "Yerga ulkan meteorit urildi! Havo harorati -40 darajaga tushib ketdi.",
    "Global toshqin! Dunyoni suv bosdi, bunker tog' cho'qqisida joylashgan."
]

# Aktiv o'yinlar bazasi (Xotirada saqlanadi)
GAMES = {}

async def handle_root(request):
    return web.Response(text="🔒 Bunker O'yin Boti Aktiv va 24/7 ishlamoqda!")

async def main():
    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    db_pool = await create_db_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool

    # 1. Guruhda o'yinni boshlash buyrug'i
    @dp.message(Command("bunker_start"))
    async def cmd_bunker_start(message: types.Message):
        if message.chat.type in ["private"]:
            await message.answer("❌ Bu o'yinni faqat guruhlarda o'ynash mumkin!")
            return

        chat_id = message.chat.id
        if chat_id in GAMES and GAMES[chat_id]["status"] == "started":
            await message.answer("⚠️ Guruhda allaqachon aktiv o'yin ketmoqda!")
            return

        GAMES[chat_id] = {
            "status": "registration",
            "players": {},
            "katastrofa": random.choice(KATASTROFALAR),
            "bunker_limit": 0
        }

        await message.answer(
            f"🎮 <b>BUNKER O'YINI BOSHLANDI!</b>\n\n"
            f"🚨 <b>Vaziyat:</b> {GAMES[chat_id]['katastrofa']}\n\n"
            f"O'yinda qatnashish uchun hamma tezda quyidagi tugmani bossin va botga <code>/start</code> bosganiga ishonch hosil qilsin!",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[
                    types.InlineKeyboardButton(text="🙋‍♂️ O'yinga qo'shilish", callback_data=f"join_{chat_id}")
                ]]
            )
        )

    # 2. O'yinga qo'shilish tugmasi bosilganda
    @dp.callback_query(lambda c: c.data.startswith("join_"))
    async def inline_join(callback: types.CallbackQuery):
        chat_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        name = callback.from_user.full_name

        if chat_id not in GAMES:
            await callback.answer("Bu o'yin allaqachon eskirgan.", show_alert=True)
            return

        if GAMES[chat_id]["status"] != "registration":
            await callback.answer("Ro'yxatdan o'tish tugagan!", show_alert=True)
            return

        if user_id in GAMES[chat_id]["players"]:
            await callback.answer("Siz allaqachon ro'yxatdan o'tgansiz!", show_alert=True)
            return

        # Xarakteristika generatsiyasi
        xarakter = {
            "kasb": random.choice(KASBLAR),
            "soglik": random.choice(SOGLIK),
            "xobbi": random.choice(XOBBI),
            "buyum": random.choice(BUYUMLAR),
            "fakt": random.choice(FAKTLAR)
        }

        try:
            # Xarakterni shaxsiyga yuborish
            await callback.bot.send_message(
                chat_id=user_id,
                text=f"🔒 <b>Sizning Bunker O'yinidagi Xarakteringiz:</b>\n\n"
                     f"💼 <b>Kasb:</b> {xarakter['kasb']}\n"
                     f"❤️ <b>Sog'liq:</b> {xarakter['soglik']}\n"
                     f"🎨 <b>Xobbi:</b> {xarakter['xobbi']}\n"
                     f"🎒 <b>Yoningizdagi buyum:</b> {xarakter['buyum']}\n"
                     f"🤫 <b>Maxfiy fakt:</b> {xarakter['fakt']}\n\n"
                     f"<i>Guruhda o'zingizni himoya qiling va bunkerdan haydalib ketmaslikka harakat qiling!</i>",
                parse_mode="HTML"
            )
            
            GAMES[chat_id]["players"][user_id] = {"name": name, "xarakter": xarakter, "votes": 0}
            await callback.answer("Siz o'yinga qo'shildingiz! Xarakteringiz shaxsiy xabaringizga yuborildi.", show_alert=True)
            
            # Guruhga xabar berish
            player_count = len(GAMES[chat_id]["players"])
            await callback.message.edit_text(
                f"{callback.message.text}\n\n✅ <b>Qo'shildi:</b> {html.quote(name)} (Jami: {player_count} kishi)",
                parse_mode="HTML",
                reply_markup=callback.message.reply_markup
            )
        except Exception:
            await callback.answer("❌ Botga shaxsiy xabarda /start bosing, aks holda xarakteringizni yubora olmayman!", show_alert=True)

    # 3. O'yinni rasman start qilish (Tugallash) buyrug'i
    @dp.message(Command("bunker_go"))
    async def cmd_bunker_go(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in GAMES or GAMES[chat_id]["status"] != "registration":
            await message.answer("❌ Guruhda ro'yxatdan o'tish jarayoni faol emas.")
            return

        players = GAMES[chat_id]["players"]
        if len(players) < 2:
            await message.answer("❌ O'yinni boshlash uchun kamida 2 ta o'yinchi kerak!")
            return

        GAMES[chat_id]["status"] = "started"
        bunker_limit = max(1, len(players) - 1)
        GAMES[chat_id]["bunker_limit"] = bunker_limit

        text = f"🚨 <b>O'YIN BOSHLANDI! RO'YXATDAN O'TISH YOPILDI!</b>\n\n" \
               f"Bunker atigi <b>{bunker_limit} kishi</b> uchun mo'ljallangan! Demak, 1 kishi bunkerdan tashqarida qolib o'lishi kerak.\n\n" \
               f"🗣 Har bir o'yinchi o'z kasbi va xarakterini guruhga aytib, nega aynan u bunkerga kirishi kerakligini isbotlasin!\n\n" \
               f"🎙 Tartib bilan gapiring. Muhokamadan so'ng ovoz berish uchun <code>/bunker_vote</code> buyrug'ini bering!"
        
        await message.answer(text, parse_mode="HTML")

    # 4. Ovoz berish bosqichini boshlash
    @dp.message(Command("bunker_vote"))
    async def cmd_bunker_vote(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in GAMES or GAMES[chat_id]["status"] != "started":
            await message.answer("❌ Aktiv o'yin mavjud emas yoki hali boshlanmagan.")
            return

        buttons = []
        for u_id, p_info in GAMES[chat_id]["players"].items():
            buttons.append([types.InlineKeyboardButton(text=f"❌ {p_info['name']}", callback_data=f"v_{chat_id}_{u_id}")])

        await message.answer(
            "🗳 <b>KIMNI BUNKERDAN HAYDAYMIZ?</b>\n"
            "Pastdagi ro'yxatdan eng foydasiz deb hisoblagan o'yinchigizga ovoz bering:",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    # 5. Ovozni qabul qilish
    @dp.callback_query(lambda c: c.data.startswith("v_"))
    async def handle_vote(callback: types.CallbackQuery):
        parts = callback.data.split("_")
        chat_id = int(parts[1])
        target_id = int(parts[2])
        voter_id = callback.from_user.id

        if chat_id not in GAMES or GAMES[chat_id]["status"] != "started":
            await callback.answer("O'yin tugagan.", show_alert=True)
            return

        if voter_id not in GAMES[chat_id]["players"]:
            await callback.answer("Siz bu o'yinda qatnashmayapsiz!", show_alert=True)
            return

        GAMES[chat_id]["players"][target_id]["votes"] += 1
        await callback.answer("Ovozingiz qabul qilindi!")
        
        # Eng ko'p ovoz olganni aniqlash va o'yinni tugatish
        players = GAMES[chat_id]["players"]
        kicked_user = max(players, key=lambda k: players[k]["votes"])
        kicked_name = players[kicked_user]["name"]
        kicked_kasb = players[kicked_user]["xarakter"]["kasb"]

        await callback.message.edit_text(
            f"💀 <b>OVOZ BERISH YAKUNLANDI!</b>\n\n"
            f"Ko'pchilikning qaroriga ko'ra, <b>{kicked_name}</b> ({kicked_kasb}) bunkerdan shafqatsizlarcha haydaldi va tashqarida halok bo'ldi!\n\n"
            f"🎉 <b>Qolganlar bunkerga muvaffaqiyatli joylashishdi va tirik qolishdi!</b> O'yin tugadi.",
            parse_mode="HTML"
        )
        del GAMES[chat_id]

    # Standart xabarlarni middleware yoki oddiy tekshirish (Bot guruhga qo'shilganda salomlashish)
    @dp.message(lambda msg: msg.new_chat_members)
    async def welcome_bot(message: types.Message):
        for member in message.new_chat_members:
            if member.id == (await message.bot.get_me()).id:
                await message.answer(
                    "👋 <b>Salom guruh a'zolari!</b> Men professional 'Bunker' o'yin botiman.\n\n"
                    "O'yinni boshlash uchun guruhga <code>/bunker_start</code> buyrug'ini yuboring! 🎭",
                    parse_mode="HTML"
                )

    # Web server integratsiyasi (Render o'chirib qo'ymasligi uchun)
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

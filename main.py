import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, html
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

import config
from database.db_config import create_db_pool, init_db

logging.basicConfig(level=logging.INFO)

# ==========================================
# 🎭 ULKAN O'YIN MA'LUMOTLARI BAZASI
# ==========================================

KASBLAR = [
    "Shifokor-jarroh", "Harbiy muhandis", "Professional oshpaz", "Yadro fizik-olimi", 
    "Uchuvchi", "Dehqon/Agronom", "Klinik psixolog", "Senior dasturchi", "Sanoat kimyogari", 
    "Mexanik/Santexnik", "Gidrolog (Suv mutaxassisi)", "Geolog", "Elektrik", 
    "Botanik/O'tshunos", "Arxeolog", "Astronom", "Tarixchi", "Ekolog", "Veterinar",
    "Advokat", "Iqtisodchi", "Arhitetkor/Quruvchi", "Professional mergan (Snayper)",
    "Kiber-xavfsizlik mutaxassisi", "Bio-muhandis", "Yong'in o'chiruvchi", "Shaxtyor",
    "Jurnalist", "Kriminolog", "Kartograf (Xarita chizuvchi)", "Meteorolog",
    "Professional mexanik", "Tikuvchi/Dizayner", "Siyosatchi/Natijali ritorik", 
    "Geodezist", "Slesar/Temirchi", "Gidrotexnik muhandis", "Hayvonlar o'rgatuvchisi",
    "Farmatsevt/Dorishunos", "Loyiha boshqaruvchisi (PM)"
]

SOGLIK = [
    "25 yosh, erkak, mutlaqo sog'lom, sportchi", "40 yosh, ayol, a'lo darajada, yuqori immunitet",
    "19 yosh, ayol, yengil allergiya (gullarga)", "35 yosh, erkak, ko'zi ojizroq (ko'zoynak taqadi)", 
    "52 yosh, erkak, yuragi biroz zaif (shoshilish mumkin emas)", "28 yosh, ayol, chap oyog'i biroz oqsoqlanadi",
    "31 yosh, erkak, surunkali astma (ba'zan doriga muhtoj)", "45 yosh, erkak, juda baquvvat, og'ir yuk ko'tara oladi",
    "22 yosh, ayol, qon bosimi bor", "38 yosh, erkak, tishlari mukammal holatda, jismonan sog'lom",
    "60 yosh, erkak, tajribali, lekin tez charchaydi", "26 yosh, ayol, eshitish qobiliyati juda o'tkir",
    "21 yosh, erkak, professional yuguruvchi, o'pka hajmi juda katta", "47 yosh, ayol, mutlaqo sog'lom, yoga ustasi",
    "33 yosh, erkak, surunkali uyqusizlikdan aziyat chekadi", "29 yosh, ayol, bitta buyragi yo'q (lekin parhezda sog'lom)",
    "55 yosh, erkak, qandli diabet (yengil bosqichda)", "24 yosh, ayol, jismoniy kuchi juda yuqori",
    "42 yosh, erkak, umurtqa pog'onasida yengil churra (gryja) bor", "30 yosh, ayol, barcha virusli kasalliklarga qarshi emlangan",
    "18 yosh, erkak, yosh, g'ayratli, hech qanday kasalligi yo'q", "36 yosh, ayol, o'ta o'tkir ko'rish qobiliyatiga ega"
]

XOBBI = [
    "Yulduzlarni kuzatish va astronomiya", "Yashirincha qurol va qopqonlar yasash", 
    "Tibbiy va shifobaxsh o'tlar yig'ish", "Kitob mutolaasi va falsafa", "Yoga va meditatsiya", 
    "Pichoq otish va pichoqbozlik", "Qo'l jangi (Karate/Dzyudo)", "Radio-havaskorlik (antennalar yasash)",
    "Kimyoviy tajribalar o'tkazish", "Bog'dorchilik va urug' yetishtirish", "Shaxmat va strategik o'yinlar",
    "Yovvoyi tabiatda omon qolish sirlari", "Chizmachilik va xaritalash", "Eski texnikani ta'mirlash",
    "Qurilish va duradgorlik", "Tog'ga chiqish (Alpinizm)", "Baliqchilik va suv ostida suzish",
    "Chorvachilik va hayvon boqish", "She'riyat va ssenariy yozish", "Kartbozlik va illyuzionizm",
    "Qulflarni kalitsiz ochish (Lockpicking)", "Metal qidirish va qazishmalarni yaxshi ko'radi",
    "Ob-havoni aniq prognoz qilish", "Yashirin xabarlar yozish (Kriptografiya)"
]

BUYUMLAR = [
    "Makarov pistoleti (5 ta o'q bilan)", "To'liq jihozlangan jarrohlik aptechkasi", 
    "6 oylik quruq konserva zaxirasi", "Portativ suv filtri (1000 litr uchun)", 
    "Mustahkam arqon va o'tkir bolta", "Quyosh batareyasida ishlaydigan Radio", 
    "Tunni yorituvchi durbin (NVD)", "Kimyoviy himoya kiyumi (Protivogaz)",
    "Professional asboblar qutisi (otvyortka, kalitlar)", "Urug'lar solingan germetik quti",
    "Dala sharoitida olov yoquvchi maxsus moslama", "10 litr toza spirt (tibbiyot uchun)",
    "Dunyoning to'liq geologik xaritasi", "Qalin harbiy chodir", "Kuchli elektroshoker",
    "20 ta turli xil batareyalar qutisi", "Doimiy ishlaydigan cho'ntak kompassi",
    "10 ta sham va gugurtlar to'plami", "Kimyoviy elementlarni o'lchaydigan datchik",
    "Kichik benzinli motor va 5 litr yoqilg'i", "Ulkan pichoq (Machete)",
    "Suv o'tkazmaydigan germetik sumka", "Dala durbini (20x yaqinlashtiradi)",
    "Issiqlikni saqlaydigan 3 ta maxsus adyol", "1 kg tuz va ziravorlar qutisi"
]

FAKTLAR = [
    "Bunkerni buzib kirish maxfiy kodini biladi", "Yashirincha o'g'rilik qila oladi (qo'li chaqqon)", 
    "Aslida u dushman tomonning josusi", "Har qanday og'ir stressga juda chidamli",
    "Zulmatdan (qorong'ulikdan) dahshatli darajada qo'rqadi", "Klaustrofobiya (yopiq joydan qo'rqish) bor",
    "Yashirincha psixotrop dorilarga qaramligi bor", "O'tmishda qamoqda o'tirib chiqqan",
    "Bunkerdagi radiatsiyani o'lchovchi yagona datchik unda", "Odam psixologiyasini ko'rib turib o'qiydi",
    "Oilasini qutqarish uchun hamma narsaga tayyor (sotqinlik qilishi mumkin)",
    "Bunker qurgan muhandisning yaqin qarindoshi", "Uzoq vaqt ovqatsiz yashashga o'rgangan",
    "Mizofobiya (mikroblardan o'ta qo'rqish) kasalligi bor", "Aslida uning diplomi soxta (hech narsani bilmaydi)",
    "Gipnoz qilish qobiliyatiga ega", "Uxlashda judayam baland ovozda xurrak otadi",
    "Bunker tashqarisida yashirin oziq-ovqat ombori borligini biladi", "Tez-tez tajovuzkor bo'lib qoladi (psixik buzilish)",
    "O'ta aqlli (IQ darajasi 160 dan yuqori)", "Har qanday texnikani 5 daqiqada buza oladi",
    "Sudralib yuruvchilardan (ilon, suvarak) dahshatli qo'rqadi", "Hamma sirni sota oladigan xarakterga ega"
]

KATASTROFALAR = [
    "Yadro urushi boshlandi! Dunyo radiatsiya ostida. Bunker 50 yilga mo'ljallangan.",
    "Zombi apokalipsisi! Shaharlarni zombilar egalladi. Bunker eng xavfsiz joy.",
    "Yerga ulkan meteorit urildi! Havo harorati -40 darajaga tushib ketdi.",
    "Global toshqin! Dunyoni suv bosdi, bunker tog' cho'qqisida joylashgan."
]

# Aktiv guruh o'yinlarini xotirada saqlash obyekti
GAMES = {}

# ==========================================
# 🤖 BOT LOGIKASI VA DIZAYNI
# ==========================================

async def main():
    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    # Ma'lumotlar bazasini asinxron ulash (PostgreSQL)
    db_pool = await create_db_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool

    # 1. Guruhda o'yinni boshlash
    @dp.message(Command("bunker_start"))
    async def cmd_bunker_start(message: types.Message):
        if message.chat.type in ["private"]:
            await message.answer("❌ Ushbu strategik o'yinni faqat guruhlarda o'ynash mumkin!")
            return

        chat_id = message.chat.id
        if chat_id in GAMES and GAMES[chat_id]["status"] == "started":
            await message.answer("⚠️ Guruhda allaqachon aktiv o'yin davom etmoqda!")
            return

        GAMES[chat_id] = {
            "status": "registration",
            "players": {},
            "katastrofa": random.choice(KATASTROFALAR),
            "bunker_limit": 0
        }

        await message.answer(
            f"🎮 <b>BUNKER O'YINI BOSHLANDI!</b>\n\n"
            f"🚨 <b>Katastrofa (Ofat):</b> {GAMES[chat_id]['katastrofa']}\n\n"
            f"O'yinda qatnashmoqchi bo'lganlar pastdagi tugmani bossin va botga shaxsiy xabarda <code>/start</code> berganiga ishonch hosil qilsin!",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[
                    types.InlineKeyboardButton(text="🙋‍♂️ O'yinga qo'shilish", callback_data=f"join_{chat_id}")
                ]]
            )
        )

    # 2. O'yinga a'zo bo'lish tugmasi (Callback)
    @dp.callback_query(lambda c: c.data.startswith("join_"))
    async def inline_join(callback: types.CallbackQuery):
        chat_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        name = callback.from_user.full_name

        if chat_id not in GAMES:
            await callback.answer("Bu o'yin allaqachon eskirgan yoki tugagan.", show_alert=True)
            return

        if GAMES[chat_id]["status"] != "registration":
            await callback.answer("Ro'yxatdan o'tish bosqichi tugagan!", show_alert=True)
            return

        if user_id in GAMES[chat_id]["players"]:
            await callback.answer("Siz allaqachon o'yindasiz!", show_alert=True)
            return

        # Tasodifiy unikal xarakter yaratish
        xarakter = {
            "kasb": random.choice(KASBLAR),
            "soglik": random.choice(SOGLIK),
            "xobbi": random.choice(XOBBI),
            "buyum": random.choice(BUYUMLAR),
            "fakt": random.choice(FAKTLAR)
        }

        try:
            # Xarakteristikani shaxsiy chatga (LCh) yuborish
            await callback.bot.send_message(
                chat_id=user_id,
                text=f"🔒 <b>Sizning Bunker O'yinidagi Xarakteringiz:</b>\n\n"
                     f"💼 <b>Kasb:</b> {xarakter['kasb']}\n"
                     f"❤️ <b>Biologiya/Sog'liq:</b> {xarakter['soglik']}\n"
                     f"🎨 <b>Xobbi:</b> {xarakter['xobbi']}\n"
                     f"🎒 <b>Yoningizdagi buyum:</b> {xarakter['buyum']}\n"
                     f"🤫 <b>Maxfiy fakt:</b> {xarakter['fakt']}\n\n"
                     f"<i>Guruhda o'z xarakteringizni himoya qiling va bunkerdan haydalib ketmaslikka harakat qiling! Omnon qoling!</i>",
                parse_mode="HTML"
            )
            
            GAMES[chat_id]["players"][user_id] = {"name": name, "xarakter": xarakter, "votes": 0}
            await callback.answer("Siz o'yinga qo'shildingiz! Xarakteringiz shaxsiy xabaringizga yuborildi.", show_alert=True)
            
            player_count = len(GAMES[chat_id]["players"])
            await callback.message.edit_text(
                f"{callback.message.text}\n\n✅ <b>Qo'shildi:</b> {html.quote(name)} (Jami o'yinchilar: {player_count} kishi)",
                parse_mode="HTML",
                reply_markup=callback.message.reply_markup
            )
        except Exception:
            await callback.answer("❌ Bot sizga xabar yubora olmadi! Avval botning o'ziga kirib /start bosing, keyin guruhga qaytib ushbu tugmani qayta bosing!", show_alert=True)

    # 3. Ro'yxatdan o'tishni yopish va o'yinni rasman boshlash
    @dp.message(Command("bunker_go"))
    async def cmd_bunker_go(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in GAMES or GAMES[chat_id]["status"] != "registration":
            await message.answer("❌ Guruhda ro'yxatdan o'tish jarayoni faol emas.")
            return

        players = GAMES[chat_id]["players"]
        if len(players) < 2:
            await message.answer("❌ O'yinni boshlash uchun guruhda kamida 2 ta o'yinchi yig'ilishi kerak!")
            return

        GAMES[chat_id]["status"] = "started"
        bunker_limit = max(1, len(players) - 1)
        GAMES[chat_id]["bunker_limit"] = bunker_limit

        text = f"🚨 <b>O'YIN RASMAN BOSHLANDI! RO'YXATDAN O'TISH YOPILDI!</b>\n\n" \
               f"Bunker atigi <b>{bunker_limit} kishi</b> uchun mo'ljallangan! Demak, ovoz berish yo'li bilan 1 kishi bunkerdan tashqarida qolib o'lishi kerak.\n\n" \
               f"🗣 <b>Vazifa:</b> Har bir o'yinchi navbat bilan o'z kasbi va xarakterini guruhga tushuntirib, nega aynan u bunkerga loyiqligini isbotlasin!\n\n" \
               f"🎙 Muhokama yakunlangach, eng foydasiz o'yinchini haydash (ovoz berish) uchun guruhga <code>/bunker_vote</code> buyrug'ini yuboring!"
        
        await message.answer(text, parse_mode="HTML")

    # 4. Ovoz berish tizimini yoqish
    @dp.message(Command("bunker_vote"))
    async def cmd_bunker_vote(message: types.Message):
        chat_id = message.chat.id
        if chat_id not in GAMES or GAMES[chat_id]["status"] != "started":
            await message.answer("❌ Aktiv o'yin mavjud emas yoki hali muhokama bosqichiga o'tilmagan.")
            return

        buttons = []
        for u_id, p_info in GAMES[chat_id]["players"].items():
            buttons.append([types.InlineKeyboardButton(text=f"❌ {p_info['name']}", callback_data=f"v_{chat_id}_{u_id}")])

        await message.answer(
            "🗳 <b>KIMNI BUNKERDAN HAYDAYMIZ? (OVOZ BERISH VAKTI)</b>\n\n"
            "Pastdagi ro'yxatdan o'yin davomida eng foydasiz deb hisoblagan ishtirokchingizga ovoz bering:",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    # 5. Ovozlar natijasini hisoblash va haydalgan o'yinchini e'lon qilish
    @dp.callback_query(lambda c: c.data.startswith("v_"))
    async def handle_vote(callback: types.CallbackQuery):
        parts = callback.data.split("_")
        chat_id = int(parts[1])
        target_id = int(parts[2])
        voter_id = callback.from_user.id

        if chat_id not in GAMES or GAMES[chat_id]["status"] != "started":
            await callback.answer("O'yin yakunlangan.", show_alert=True)
            return

        if voter_id not in GAMES[chat_id]["players"]:
            await callback.answer("Siz ushbu o'yinda qatnashmayapsiz!", show_alert=True)
            return

        GAMES[chat_id]["players"][target_id]["votes"] += 1
        await callback.answer("Ovozingiz muvaffaqiyatli qabul qilindi!")
        
        players = GAMES[chat_id]["players"]
        
        # Eng ko'p ovoz to'plagan foydalanuvchini aniqlash
        kicked_user = max(players, key=lambda k: players[k]["votes"])
        kicked_name = players[kicked_user]["name"]
        kicked_kasb = players[kicked_user]["xarakter"]["kasb"]

        await callback.message.edit_text(
            f"💀 <b>OVOZ BERISH SHAFQATSIZLARCHA YAKUNLANDI!</b>\n\n"
            f"Ko'pchilik o'yinchilarning qaroriga ko'ra, <b>{kicked_name}</b> (Kasbi: {kicked_kasb}) bunkerdan tashqariga haydaldi va ofat sababli halok bo'ldi!\n\n"
            f"🎉 <b>Qolgan o'yinchilar bunkerga xavfsiz joylashib, insoniyat sivilizatsiyasini saqlab qolishdi!</b> O'yin yakunlandi.",
            parse_mode="HTML"
        )
        # Guruh xotirasini tozalash (yangi o'yin uchun joy ochish)
        del GAMES[chat_id]

    # 6. Bot guruhga qo'shilganda avtomatik salomlashish va qo'llanma berish
    @dp.message(lambda msg: msg.new_chat_members)
    async def welcome_bot(message: types.Message):
        for member in message.new_chat_members:
            if member.id == (await message.bot.get_me()).id:
                await message.answer(
                    "👋 <b>Salom guruh a'zolari!</b> Men professional va mukammal 'Bunker' psixologik o'yin boti hisoblanaman.\n\n"
                    "Guruhda yangi o'yin sarguzashtini boshlash uchun <code>/bunker_start</code> buyrug'ini yuboring! 🎭",
                    parse_mode="HTML"
                )

    logging.info("Bot Railway tizimida muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

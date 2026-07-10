import asyncio
import json
import os
import re
import time
import httpx
from bs4 import BeautifulSoup
from pyrogram import Client, filters, errors
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from pyrogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Event Loop xavfsizligini ta'minlash
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# 🔐 ASOSIY PARAMETRLAR
BOT_TOKEN = "8099815200:AAH05Qa5PiHbhdC54UdZiLMf0dNeRt4ETwQ"
API_ID = 33118317
API_HASH = "53aae636122c27a99a6c211ecc5d0c68"
REQUIRED_CHANNEL = "oqivaqotaril"

app = Client(
    "iqro_premium_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)
scheduler = AsyncIOScheduler()

# 🗄️ MA'LUMOTLAR OMBORI FAYLLARI
SETTINGS_FILE = "user_settings.json"
PASSED_USERS_FILE = "passed_users.json"
STATES_FILE = "user_states.json"
FEEDBACK_FILE = "feedback.json"

click_timers = {}

PREDEFINED_TOPICS = [
    "Oyat", "Hadis", "Sher", "Hikoya", "Hikmat", 
    "Salovat", "Fiqh", "Tarix", "Ruhiyat", "Motivatsiya",
    "Duolar", "Ilm", "Axloq", "Tafsir", "Hammasi"
]

PREDEFINED_CHANNELS = [
    "@oqivaqotaril", "@annuvr", "@ihruz", "@hikmatlar_hazinasi", "@ilm_nuri",
    "@soliham", "@islomuz", "@quran_uz", "@hadis_uz", "@ziyouz",
    "@siyrat_uz", "@tarix_uz", "@ruhiyat_uz", "@salovatchilar", "@duolar_uz"
]

AVAILABLE_TIMES = [
    "05:00", "05:30", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
    "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00",
    "20:00", "21:00", "22:00", "23:00", "00:00"
]

# 🌐 KO'P TILLI MUKAMMAL MATNLAR TIZIMI
TEXTS = {
    "uz_lot": {
        "about": "✨ **'Iqro Pro Ultra' Premium Avto-Post Tizimi**\n\n📜 **Tizim imkoniyatlari:**\n» Manba kanallaridan eng sara postlarni saralaydi.\n» Belgilangan mavzular bo'yicha filtrlaydi.\n» Kanalingizga avtomatik ravishda tayyorlangan postlarni joylaydi.\n\n⚙️ *Sozlashni boshlash uchun quyidagi tugmani bosing:*",
        "sub_req": "👋 Botdan to'liq foydalanish va sozlash uchun avval rasmiy kanalimizga a'zo bo'ling:",
        "sub_btn": "📢 Kanalga Obuna Bo'lish",
        "verify_btn": "✅ Obunani Tasdiqlash",
        "too_fast": "⚠️ Sokinroq! Tasdiqlash uchun kamida 2 soniya kuting.",
        "verified": "🎉 Obuna muvaffaqiyatli tasdiqlandi!",
        "main_menu_btn": "⚙️ Avto-postni Sozlash",
        "step1": "🚀 **1-Bosqich:** Matn manbasini (Kanalni) tanlang yoki izlang:",
        "step2": "📂 **2-Bosqich:** Qaysi mavzudagi postlar sizga kerak?",
        "step3": "📢 **3-Bosqich:** Postlar yuboriladigan kanal yoki guruh `@username`ini yuboring:",
        "step4": "⏳ **4-Bosqich:** Post yuborish vaqtlarini belgilang:\n\n*(Tugmalardan tanlang yoki qo'lda kiriting)*",
        "back_btn": "⬅️ Orqaga",
        "home_btn": "🏠 Bosh Menyu",
        "save_btn": "💾 Saqlash va Aktivlashtirish",
        "custom_btn": "🔍 Qo'lda kanal izlash",
        "custom_time_btn": "✍️ O'zim vaqt kiritaman",
        "success": "🎉 **Barcha sozlamalar muvaffaqiyatli saqlandi va tizim ishga tushirildi!**\n\n*Belgilangan vaqtlarda bot kontent tarqatishni boshlaydi.*",
        "menu_setup": "⚙️ Sozlash",
        "menu_question": "💬 Savol yuborish",
        "menu_suggestion": "💡 Taklif kiritish",
        "menu_help": "🆘 Yordam xizmati",
        "menu_about": "📢 Bot Haqida",
        "menu_privacy": "🔒 Maxfiylik",
        "menu_lang": "🌐 Til (Language)",
        "privacy_text": "🔒 **Maxfiylik Siyosati:**\n\n1. Sizning sozlamalaringiz xavfsiz va maxfiy saqlanadi.\n2. Bot faqat siz ruxsat bergan kanallarda xizmat ko'rsatadi.\n3. Shaxsiy ma'lumotlar uchinchi shaxslarga berilmaydi.",
        "about_text": "🤖 **Iqro Pro Ultra Bot:**\n\nKanallarni eng sifatli va saralangan islomiy hamda ma'rifiy kontentlar bilan avtomatik to'ldirib boruvchi yordamchi.\n\n📢 Kanal: @oqivaqotaril",
        "help_text": "🆘 **Tezkor Yordam:**\n\n❓ **Bot kanalga post tashlamayapti?**\n- Botni o'zingizning kanalingizga **Admin** qilib qo'shganingizga va post joylash huquqini berganingizga ishonch hosil qiling.\n\n❓ **Qo'lda vaqt kiritish qanday?**\n- '✍️ O'zim vaqt kiritaman' tugmasini bosib, `07:15, 14:30` ko'rinishida yozing.",
        "ask_question": "💬 **Savolingizni matn shaklida yuboring:**\n*Mutaxassislarimiz tez orada javob berishadi.*",
        "ask_suggestion": "💡 **Loyiha sifatini oshirish uchun taklifingizni yozing:**",
        "thanks_feedback": "✅ Rahmat! Murojaatingiz muvaffaqiyatli qabul qilindi.",
        "enter_custom_time_prompt": "✍️ **Vaqtlarni HH:MM formatida vergul bilan ajratib yuboring.**\n\nMasalan: `08:00, 13:15, 21:45`",
        "invalid_time": "❌ Vaqt formati xato. Iltimos, na'munadagidek kiriting: `09:30` yoki `12:00, 18:45`"
    },
    "uz_kir": {
        "about": "✨ **'Iqro Pro Ultra' Премиум Авто-Пост Тизими**\n\n📜 **Тизим имкониятлари:**\n» Манба каналларидан энг сара постларни саралайди.\n» Белгиланган мавзулар бўйича филтрлайди.\n» Каналингизга автоматик равишda тайёрланган постларни жойлайди.\n\n⚙️ *Созлашни бошлаш учун қуйидаги тугмани босинг:*",
        "sub_req": "👋 Ботдан тўлиқ фойдаланиш ва созлаш учун аввал расмий каналимизга аъзо бўлинг:",
        "sub_btn": "📢 Каналга Обуна Бўлиш",
        "verify_btn": "✅ Обунани Тасдиқлаш",
        "too_fast": "⚠️ Сокинроқ! Тасдиқлаш учун камида 2 сония кутинг.",
        "verified": "🎉 Обуна муваффақиятли тасдиқланди!",
        "main_menu_btn": "⚙️ Авто-постни Созлаш",
        "step1": "🚀 **1-Босқич:** Матн манбасини (Канални) танланг ёки изланг:",
        "step2": "📂 **2-Босқич:** Қайси мавзудаги постлар сизга керак?",
        "step3": "📢 **3-Босқич:** Постлар юбориладиган канал ёки гуруҳ `@username`ини юборинг:",
        "step4": "⏳ **4-Босқич:** Пост юбориш вақтларини белгиланг:\n\n*(Тугмалардан танланг ёки қўлда киритинг)*",
        "back_btn": "⬅️ Орқага",
        "home_btn": "🏠 Бош Меню",
        "save_btn": "💾 Сақлаш ва Активлаштириш",
        "custom_btn": "🔍 Қўлда канал излаш",
        "custom_time_btn": "✍️ Ўзим вақт киритаман",
        "success": "🎉 **Барча созламалар муваффақиятли сақланди ва тизим ишга туширилди!**\n\n*Белгиланган вақтларда бот контент тарқатишни бошлайди.*",
        "menu_setup": "⚙️ Созлаш",
        "menu_question": "💬 Савол юбориш",
        "menu_suggestion": "💡 Таклиф киритиш",
        "menu_help": "🆘 Ёрдам хизмати",
        "menu_about": "📢 Бот Ҳақида",
        "menu_privacy": "🔒 Махфийлик",
        "menu_lang": "🌐 Тил (Language)",
        "privacy_text": "🔒 **Махфийлик Сиёсати:**\n\n1. Сизнинг созламаларингиз хавфсиз ва махфий сақланади.\n2. Бот фақат сиз рухсат берган каналларда хизмат кўрсатади.\n3. Шахсий маълумотлар учинчи шахсларга берилмайди.",
        "about_text": "🤖 **Iqro Pro Ultra Бот:**\n\nКаналларни энг сифатли ва сараланган исломий ҳамда маърифий контентлар билан автоматик тўлдириб борувчи ёрдамчи.\n\n📢 Канал: @oqivaqotaril",
        "help_text": "🆘 **Тезкор Ёрдам:**\n\n❓ **Бот каналга пост ташламаяпти?**\n- Ботни ўзингизнинг каналингизга **Админ** қилиб қўшганингизга ва пост жойлаш ҳуқуқини берганингизга ишонч ҳосил қилинг.\n\n❓ **Қўлда вақт киритиш қандай?**\n- '✍️ Ўзим ваqt киритаман' тугмасини босиб, `07:15, 14:30` кўринишида ёзинг.",
        "ask_question": "💬 **Саволингизни матн шаклида юборинг:**\n*Мутахассисларимиз тез орада жавоб беришади.*",
        "ask_suggestion": "💡 **Лойиҳа сифатини ошириш учун таклифингизни ёзинг:**",
        "thanks_feedback": "✅ Раҳмат! Мурожаатингиз муваффақиятли қабул қилинди.",
        "enter_custom_time_prompt": "✍️ **Вақтларни ХХ:ММ форматида вергул билан ажратиб юборинг.**\n\nМасалан: `08:00, 13:15, 21:45`",
        "invalid_time": "❌ Вақт формати хато. Илтимос, наъмунадагидек киритинг: `09:30` ёки `12:00, 18:45`"
    },
    "ru": {
        "about": "✨ **Premium Система Авто-Постинга 'Iqro Pro Ultra'**\n\n📜 **Возможности системы:**\n» Фильтрация лучших постов из каналов-источников.\n» Сортировка контента по выбранным темам.\n» Автоматическая публикация готовых постов в ваш канал.\n\n⚙️ *Для начала настройки нажмите кнопку ниже:*",
        "sub_req": "👋 Для полноценного использования бота сначала подпишитесь на наш канал:",
        "sub_btn": "📢 Подписаться на Канал",
        "verify_btn": "✅ Проверить Подписку",
        "too_fast": "⚠️ Не спешите! Подождите минимум 2 секунды перед проверкой.",
        "verified": "🎉 Подписка успешно подтверждена!",
        "main_menu_btn": "⚙️ Настроить Авто-постинг",
        "step1": "🚀 **Шаг 1:** Выберите или найдите канал-источник контента:",
        "step2": "📂 **Шаг 2:** Посты на какие темы вам необходимы?",
        "step3": "📢 **Шаг 3:** Отправьте `@username` канала или группы, куда отправлять посты:",
        "step4": "⏳ **Шаг 4:** Укажите время для публикаций:\n\n*(Выберите на кнопках или введите вручную)*",
        "back_btn": "⬅️ Назад",
        "home_btn": "🏠 Главное Меню",
        "save_btn": "💾 Сохранить и Активировать",
        "custom_btn": "🔍 Ручной поиск канала",
        "custom_time_btn": "✍️ Введу время вручную",
        "success": "🎉 **Все настройки успешно сохранены, система запущена!**\n\n*Бот начнет публикацию контента в указанное время.*",
        "menu_setup": "⚙️ Настройка",
        "menu_question": "💬 Задать вопрос",
        "menu_suggestion": "💡 Предложение",
        "menu_help": "🆘 Помощь",
        "menu_about": "📢 О Боте",
        "menu_privacy": "🔒 Конфиденциальность",
        "menu_lang": "🌐 Язык (Language)",
        "privacy_text": "🔒 **Политика Конфиденциальности:**\n\n1. Ваши настройки хранятся в безопасности и конфиденциальности.\n2. Бот работает только в тех каналах, где вы предоставили доступ.\n3. Личные данные не передаются третьим лицам.",
        "about_text": "🤖 **Бот Iqro Pro Ultra:**\n\nВаш персональный помощник для автоматического наполнения каналов качественным исламским и просветительским контентом.\n\n📢 Наш канал: @oqivaqotaril",
        "help_text": "🆘 **Быстрая Помощь:**\n\n❓ **Бот не публикует посты в канал?**\n- Убедитесь, что вы добавили бота в свой канал в качестве **Администратора** с правом публикации постов.\n\n❓ **Как ввести время вручную?**\n- Нажмите кнопку '✍️ Введу время вручную' и отправьте в формате: `07:15, 14:30`.",
        "ask_question": "💬 **Отправьте ваш вопрос в текстовом виде:**\n*Наши специалисты ответят вам в ближайшее время.*",
        "ask_suggestion": "💡 **Напишите свое предложение для улучшения проекта:**",
        "thanks_feedback": "✅ Спасибо! Ваше обращение успешно принято.",
        "enter_custom_time_prompt": "✍️ **Отправьте время в формате ЧЧ:ММ через запятую.**\n\nПример: `08:00, 13:15, 21:45`",
        "invalid_time": "❌ Неверный формат времени. Пожалуйста, введите по шаблону: `09:30` или `12:00, 18:45`"
    },
    "en": {
        "about": "✨ **'Iqro Pro Ultra' Premium Auto-Post System**\n\n📜 **System Features:**\n» Filters the best posts from source channels.\n» Categorizes content based on selected topics.\n» Automatically publishes compiled posts to your channel.\n\n⚙️ *Click the button below to start configuration:*",
        "sub_req": "👋 To fully use and configure the bot, please subscribe to our official channel first:",
        "sub_btn": "📢 Subscribe to Channel",
        "verify_btn": "✅ Verify Subscription",
        "too_fast": "⚠️ Slow down! Please wait at least 2 seconds before verifying.",
        "verified": "🎉 Subscription successfully verified!",
        "main_menu_btn": "⚙️ Configure Auto-Post",
        "step1": "🚀 **Step 1:** Select or search for the content source channel:",
        "step2": "📂 **Step 2:** Which topics of posts do you need?",
        "step3": "📢 **Step 3:** Send the `@username` of the target channel or group:",
        "step4": "⏳ **Step 4:** Set publication schedules:\n\n*(Choose from buttons or enter manually)*",
        "back_btn": "⬅️ Back",
        "home_btn": "🏠 Main Menu",
        "save_btn": "💾 Save & Activate",
        "custom_btn": "🔍 Search Channel Manually",
        "custom_time_btn": "✍️ Enter Custom Time",
        "success": "🎉 **All configurations saved successfully and system activated!**\n\n*The bot will start publishing content at the scheduled times.*",
        "menu_setup": "⚙️ Settings",
        "menu_question": "💬 Ask Question",
        "menu_suggestion": "💡 Suggestion",
        "menu_help": "🆘 Help & Support",
        "menu_about": "📢 About Bot",
        "menu_privacy": "🔒 Privacy",
        "menu_lang": "🌐 Language",
        "privacy_text": "🔒 **Privacy Policy:**\n\n1. Your configurations and data are kept secure and strictly confidential.\n2. The bot only acts within channels where you granted admin rights.\n3. Personal information is never shared with third parties.",
        "about_text": "🤖 **Iqro Pro Ultra Bot:**\n\nAn automated assistant designed to populate your Telegram channels with refined educational and Islamic content.\n\n📢 Channel: @oqivaqotaril",
        "help_text": "🆘 **Quick Help:**\n\n❓ **The bot isn't posting to my channel?**\n- Ensure you have added the bot as an **Admin** to your channel with permission to post messages.\n\n❓ **How to add custom times?**\n- Click '✍️ Enter Custom Time' and type like: `07:15, 14:30`.",
        "ask_question": "💬 **Send your question in text format:**\n*Our support team will respond shortly.*",
        "ask_suggestion": "💡 **Write your suggestions to improve this project:**",
        "thanks_feedback": "✅ Thank you! Your feedback has been successfully recorded.",
        "enter_custom_time_prompt": "✍️ **Send times in HH:MM format separated by commas.**\n\nExample: `08:00, 13:15, 21:45`",
        "invalid_time": "❌ Invalid time format. Please enter according to the template: `09:30` or `12:00, 18:45`"
    }
}

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user_state(user_id):
    states = load_json(STATES_FILE)
    return states.get(str(user_id), {"lang": "uz_lot"})

def update_user_state(user_id, key, value):
    states = load_json(STATES_FILE)
    u_id = str(user_id)
    if u_id not in states:
        states[u_id] = {"lang": "uz_lot"}
    states[u_id][key] = value
    save_json(STATES_FILE, states)

def get_reply_keyboard(lang):
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(txt["menu_setup"]), KeyboardButton(txt["menu_lang"])],
            [KeyboardButton(txt["menu_question"]), KeyboardButton(txt["menu_suggestion"])],
            [KeyboardButton(txt["menu_help"]), KeyboardButton(txt["menu_about"])],
            [KeyboardButton(txt["menu_privacy"])]
        ],
        resize_keyboard=True
    )

STOP_WORDS = ["http://", "https://", "t.me/", "tg.me", "reklama", "aksiya", "chegirma", "tanlov", "homiy", "click", "payme"]

def is_ad(text):
    return any(word in text.lower() for word in STOP_WORDS)

async def get_post_by_topics_async(channel, keywords):
    chan_username = channel.replace("@", "").strip()
    url = f"https://t.me/s/{chan_username}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                msgs = soup.find_all('div', class_='tgme_widget_message_text')
                for msg in reversed(msgs):
                    for br in msg.find_all('br'):
                        br.replace_with('\n')
                    text = msg.get_text().strip()
                    if len(text) > 15 and not is_ad(text):
                        if keywords:
                            if any(word.lower() in text.lower() for word in keywords):
                                return text
                        else:
                            return text
    except Exception as e:
        print(f"🌐 Skraping xatoligi ({channel}): {e}")
    return None

async def cron_checker():
    now = datetime.now().strftime("%H:%M")
    settings = load_json(SETTINGS_FILE)
    
    for user_id, config in settings.items():
        user_times = config.get("times", [])
        if now in user_times:
            target_chat = config.get("target_chat")
            source_channel = config.get("source_channel")
            keywords = config.get("keywords", [])
            
            if not target_chat or not source_channel:
                continue
                
            content = await get_post_by_topics_async(source_channel, keywords)
            if content:
                # 🕊️ TELEGRAM UCHUN ENGO'ZAL VA GO'ZAL DIZAYNDAGI XABAR SHABLONI
                formatted_text = (
                    f"📖 **Ma'rifat Ulashuvchi Kontent**\n"
                    f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n\n"
                    f"{content}\n\n"
                    f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
                    f"✍️ **Manba:** {source_channel}\n"
                    f"📚 **Iqro Avto-Post Tizimi** 🕊️"
                )
                try:
                    await app.send_message(target_chat, formatted_text, parse_mode=ParseMode.MARKDOWN)
                except errors.TelegramAPIError as e:
                    print(f"❌ Kanalga post yuborishda xato ({target_chat}): {e}")

@app.on_message(filters.command(["start", "help", "savol", "taklif", "privacy"]) & filters.private)
async def commands_handler(client, message):
    user_id = str(message.from_user.id)
    cmd = message.command[0] if message.command else "start"
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])

    if cmd == "start":
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇺🇿 O'zbekcha (Lotin)", callback_data="lang_uz_lot")],
            [InlineKeyboardButton("🇺🇿 Ўзбекча (Кирил)", callback_data="lang_uz_kir")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ])
        await message.reply(
            "🌐 **Muloqot tilini tanlang / Выберите язык / Choose language:**",
            reply_markup=btn
        )
    elif cmd == "help":
        await message.reply(txt["help_text"], reply_markup=get_reply_keyboard(lang))
    elif cmd == "savol":
        update_user_state(user_id, "expecting", "user_question")
        await message.reply(txt["ask_question"], reply_markup=get_reply_keyboard(lang))
    elif cmd == "taklif":
        update_user_state(user_id, "expecting", "user_suggestion")
        await message.reply(txt["ask_suggestion"], reply_markup=get_reply_keyboard(lang))
    elif cmd == "privacy":
        await message.reply(txt["privacy_text"], reply_markup=get_reply_keyboard(lang))

@app.on_callback_query(filters.regex(r"^lang_"))
async def handle_lang_choice(client, callback):
    lang = callback.data.replace("lang_", "")
    user_id = str(callback.from_user.id)
    
    update_user_state(user_id, "lang", lang)
    passed_users = load_json(PASSED_USERS_FILE)
    
    if user_id in passed_users:
        try: await callback.message.delete()
        except: pass
        await show_main_menu(callback.message, lang, edit=False)
    else:
        click_timers[user_id] = time.time()
        txt = TEXTS.get(lang, TEXTS["uz_lot"])
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton(txt["sub_btn"], url=f"https://t.me/{REQUIRED_CHANNEL}")],
            [InlineKeyboardButton(txt["verify_btn"], callback_data="check_subscription")]
        ])
        await callback.message.edit_text(
            f"{txt['about']}\n\n{txt['sub_req']} @{REQUIRED_CHANNEL}",
            reply_markup=btn
        )

@app.on_callback_query(filters.regex("check_subscription"))
async def check_sub_callback(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    
    current_time = time.time()
    start_time = click_timers.get(user_id, current_time)
    
    if (current_time - start_time) < 2.0:
        await callback.answer(txt["too_fast"], show_alert=True)
        return

    passed_users = load_json(PASSED_USERS_FILE)
    passed_users[user_id] = True
    save_json(PASSED_USERS_FILE, passed_users)
    
    await callback.answer(txt["verified"], show_alert=False)
    try: await callback.message.delete()
    except: pass
    
    await show_main_menu(callback.message, lang, edit=False)

async def show_main_menu(message, lang="uz_lot", edit=True):
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(txt["main_menu_btn"], callback_data="step_1_source")]
    ])
    if edit:
        await message.edit_text(txt["about"], reply_markup=btn)
    else:
        await app.send_message(
            chat_id=message.chat.id,
            text=txt["about"],
            reply_markup=get_reply_keyboard(lang)
        )
        await app.send_message(chat_id=message.chat.id, text=txt["about"], reply_markup=btn)

@app.on_callback_query(filters.regex("step_1_source"))
async def step_1_source(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    
    buttons = []
    for i in range(0, len(PREDEFINED_CHANNELS), 2):
        row = [InlineKeyboardButton(PREDEFINED_CHANNELS[i], callback_data=f"src_{PREDEFINED_CHANNELS[i]}")]
        if i + 1 < len(PREDEFINED_CHANNELS):
            row.append(InlineKeyboardButton(PREDEFINED_CHANNELS[i+1], callback_data=f"src_{PREDEFINED_CHANNELS[i+1]}"))
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(txt["custom_btn"], callback_data="src_custom")])
    buttons.append([InlineKeyboardButton(txt["home_btn"], callback_data="go_home")])
    
    await callback.message.edit_text(txt["step1"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^src_"))
async def handle_source_choice(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    src = callback.data.replace("src_", "")
    
    if src == "custom":
        update_user_state(user_id, "expecting", "source")
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton(txt["back_btn"], callback_data="step_1_source")],
            [InlineKeyboardButton(txt["home_btn"], callback_data="go_home")]
        ])
        await callback.message.edit_text("📝 Kanal username-ini yozib kiriting (Masalan: `@annuvr`):", reply_markup=btn)
    else:
        update_user_state(user_id, "source_channel", src)
        await show_step_2_topics(callback.message, lang)

async def show_step_2_topics(message, lang="uz_lot"):
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    buttons = []
    for i in range(0, len(PREDEFINED_TOPICS), 3):
        row = []
        for top in PREDEFINED_TOPICS[i:i+3]:
            row.append(InlineKeyboardButton(f"📌 {top}", callback_data=f"top_{top}"))
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(txt["back_btn"], callback_data="step_1_source"), InlineKeyboardButton(txt["home_btn"], callback_data="go_home")])
    await message.edit_text(txt["step2"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^top_"))
async def handle_topic_choice(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    top = callback.data.replace("top_", "")
    
    if top == "Hammasi":
        update_user_state(user_id, "keywords", [])
    else:
        update_user_state(user_id, "keywords", [top.lower()])
        
    update_user_state(user_id, "expecting", "target_chat")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(txt["back_btn"], callback_data="step_2_back"), InlineKeyboardButton(txt["home_btn"], callback_data="go_home")]
    ])
    await callback.message.edit_text(txt["step3"], reply_markup=btn)

@app.on_callback_query(filters.regex("step_2_back"))
async def step_2_back(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    await show_step_2_topics(callback.message, lang)

@app.on_callback_query(filters.regex("go_home"))
async def go_home_callback(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    await show_main_menu(callback.message, lang, edit=True)

async def show_step_4_times(message, user_id, lang="uz_lot", edit=True):
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    state = get_user_state(user_id)
    selected = state.get("selected_times", [])
    
    buttons = []
    for i in range(0, len(AVAILABLE_TIMES), 4):
        row = []
        for t in AVAILABLE_TIMES[i:i+4]:
            mark = "✅ " if t in selected else "▫️ "
            row.append(InlineKeyboardButton(f"{mark}{t}", callback_data=f"tm_{t}"))
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(txt["custom_time_btn"], callback_data="custom_time_input")])
    buttons.append([InlineKeyboardButton(txt["save_btn"], callback_data="save_all")])
    buttons.append([InlineKeyboardButton(txt["back_btn"], callback_data="step_2_back"), InlineKeyboardButton(txt["home_btn"], callback_data="go_home")])
    
    if edit:
        await message.edit_text(txt["step4"], reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await app.send_message(chat_id=message.chat.id, text=txt["step4"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("custom_time_input"))
async def custom_time_input_cb(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    
    update_user_state(user_id, "expecting", "custom_time")
    await callback.message.edit_text(txt["enter_custom_time_prompt"])

@app.on_callback_query(filters.regex(r"^tm_"))
async def toggle_time(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    t = callback.data.replace("tm_", "")
    
    selected = state.get("selected_times", [])
    if t in selected:
        selected.remove(t)
    else:
        selected.append(t)
        
    update_user_state(user_id, "selected_times", selected)
    await show_step_4_times(callback.message, user_id, lang, edit=True)

@app.on_callback_query(filters.regex("save_all"))
async def save_all_settings(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    
    settings = load_json(SETTINGS_FILE)
    settings[user_id] = {
        "source_channel": state.get("source_channel"),
        "keywords": state.get("keywords", []),
        "target_chat": state.get("target_chat"),
        "times": state.get("selected_times", [])
    }
    save_json(SETTINGS_FILE, settings)
    await callback.message.edit_text(txt["success"])

@app.on_message(filters.private & ~filters.command(["start", "help", "savol", "taklif", "privacy"]))
async def handle_text_inputs(client, message):
    user_id = str(message.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    text = message.text.strip()
    
    if text == txt["menu_setup"]:
        await show_main_menu(message, lang, edit=False)
        return
    elif text == txt["menu_question"]:
        update_user_state(user_id, "expecting", "user_question")
        await message.reply(txt["ask_question"])
        return
    elif text == txt["menu_suggestion"]:
        update_user_state(user_id, "expecting", "user_suggestion")
        await message.reply(txt["ask_suggestion"])
        return
    elif text == txt["menu_help"]:
        await message.reply(txt["help_text"])
        return
    elif text == txt["menu_about"]:
        await message.reply(txt["about_text"])
        return
    elif text == txt["menu_privacy"]:
        await message.reply(txt["privacy_text"])
        return
    elif text == txt["menu_lang"]:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇺🇿 O'zbekcha (Lotin)", callback_data="lang_uz_lot")],
            [InlineKeyboardButton("🇺🇿 Ўзбекча (Кирил)", callback_data="lang_uz_kir")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ])
        await message.reply("🌐 **Muloqot tilini tanlang:**", reply_markup=btn)
        return

    exp = state.get("expecting")
    
    if exp == "source":
        update_user_state(user_id, "source_channel", text)
        update_user_state(user_id, "expecting", None)
        msg = await message.reply("⚙️...")
        await show_step_2_topics(msg, lang)
        
    elif exp == "target_chat":
        update_user_state(user_id, "target_chat", text)
        update_user_state(user_id, "expecting", None)
        update_user_state(user_id, "selected_times", [])
        await show_step_4_times(message, user_id, lang, edit=False)
        
    elif exp == "custom_time":
        times_found = re.findall(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", text)
        if times_found:
            selected = state.get("selected_times", [])
            for t in times_found:
                if len(t) == 4 and t[1] == ':':
                    t = '0' + t
                if t not in selected:
                    selected.append(t)
            update_user_state(user_id, "selected_times", selected)
            update_user_state(user_id, "expecting", None)
            await message.reply("✅ Vaqtlar muvaffaqiyatli qo'shildi!")
            await show_step_4_times(message, user_id, lang, edit=False)
        else:
            await message.reply(txt["invalid_time"])

    elif exp in ["user_question", "user_suggestion"]:
        feedbacks = load_json(FEEDBACK_FILE)
        if user_id not in feedbacks: feedbacks[user_id] = []
        feedbacks[user_id].append({"type": exp, "text": text, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        save_json(FEEDBACK_FILE, feedbacks)
        
        update_user_state(user_id, "expecting", None)
        await message.reply(txt["thanks_feedback"])

# 📡 Internal Web Server Render uchun portni ushlab turadi
async def handle_render_port(reader, writer):
    response = b"HTTP/1.1 200 OK\r\nContent-Length: 14\r\n\r\nPremium Active"
    writer.write(response)
    await writer.drain()
    writer.close()

async def main():
    port = int(os.environ.get("PORT", 10000))
    server = await asyncio.start_server(handle_render_port, '0.0.0.0', port)
    print(f"📡 Premium Server Portda ochiq: {port}")

    async with app:
        scheduler.add_job(cron_checker, "interval", minutes=1)
        scheduler.start()
        print("🚀 IQRO PRO ULTRA PREMIUM bot ishga tushdi!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(main())


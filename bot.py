#!/usr/bin/env python3
"""
📢 AUTO-POST BOT - FLOOD WAIT FIXED
Flood Wait Aane Par Auto-Retry With Delay
"""

import asyncio, json, os, re, time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions, types
from pyrogram.errors import FloodWait

# ═══════════════ CONFIG ═══════════════
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8771905727:AAEJq2QVVSe8OxZOqLkatVK1wGysO9UyzCQ"
OWNER_ID = 1987818347

# ═══════════════ DATABASE ═══════════════
CHANNEL_DB = "channels.json"

# ═══════════════ BOT ═══════════════
app = Client("auto_post_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ═══════════════ HELPERS ═══════════════
def jload(f, d=None):
    try:
        if os.path.exists(f):
            with open(f) as fl:
                return json.load(fl)
    except:
        pass
    return d if d is not None else {}

def jsave(f, d):
    with open(f, 'w') as fl:
        json.dump(d, fl, indent=2)

def get_channels():
    return jload(CHANNEL_DB, {"channels": []})

def add_channel(channel_id, channel_name):
    data = get_channels()
    for ch in data["channels"]:
        if ch["id"] == channel_id:
            return False
    data["channels"].append({"id": channel_id, "name": channel_name})
    jsave(CHANNEL_DB, data)
    return True

def remove_channel(channel_id):
    data = get_channels()
    data["channels"] = [ch for ch in data["channels"] if ch["id"] != channel_id]
    jsave(CHANNEL_DB, data)
    return True

def get_all_channels():
    return get_channels()["channels"]

# ═══════════════ CHECK ADMIN ═══════════════
async def check_admin(client, chat_id):
    try:
        bot_member = await client.get_chat_member(chat_id, "me")
        status = bot_member.status
        
        if isinstance(status, ChatMemberStatus):
            status_str = status.value if hasattr(status, 'value') else str(status)
        else:
            status_str = str(status)
        
        if "administrator" in status_str.lower() or "creator" in status_str.lower():
            return True, "Admin ✅"
        else:
            return False, f"Bot is {status_str}"
            
    except Exception as e:
        error = str(e)
        if "USER_NOT_PARTICIPANT" in error:
            return False, "❌ Bot is not a member of the channel!"
        elif "CHAT_ADMIN_REQUIRED" in error:
            return False, "❌ Bot is not admin!"
        elif "CHAT_ID_INVALID" in error:
            return False, "❌ Invalid channel ID!"
        elif "Forbidden" in error:
            return False, "❌ Bot cannot access this channel!"
        else:
            return False, f"⚠️ Error: {error[:100]}"

# ═══════════════ SEND MESSAGE WITH FLOOD WAIT HANDLER ═══════════════
async def send_with_retry(client, send_func, *args, **kwargs):
    """FloodWait aane par auto-retry with delay"""
    try:
        return await send_func(*args, **kwargs)
    except FloodWait as e:
        wait_time = e.value if hasattr(e, 'value') else 60
        print(f"⚠️ FloodWait: Waiting {wait_time} seconds...")
        await asyncio.sleep(wait_time + 5)
        return await send_func(*args, **kwargs)

async def send_to_channel(client, msg, channel_id):
    """Message ko channel mein send karega - FloodWait handle karega"""
    try:
        # Agar message forward hai toh original content copy karo
        if msg.forward_from or msg.forward_from_chat:
            # Pehle text copy karo agar hai
            if msg.text:
                await send_with_retry(client, client.send_message, channel_id, msg.text)
                await asyncio.sleep(0.5)
            
            # Phir media copy karo agar hai
            if msg.photo:
                await send_with_retry(client, client.send_photo, channel_id, msg.photo.file_id, caption=msg.caption)
                await asyncio.sleep(0.5)
            elif msg.video:
                await send_with_retry(client, client.send_video, channel_id, msg.video.file_id, caption=msg.caption)
                await asyncio.sleep(0.5)
            elif msg.sticker:
                await send_with_retry(client, client.send_sticker, channel_id, msg.sticker.file_id)
                await asyncio.sleep(0.5)
            elif msg.document:
                await send_with_retry(client, client.send_document, channel_id, msg.document.file_id, caption=msg.caption)
                await asyncio.sleep(0.5)
            elif msg.animation:
                await send_with_retry(client, client.send_animation, channel_id, msg.animation.file_id, caption=msg.caption)
                await asyncio.sleep(0.5)
            elif msg.voice:
                await send_with_retry(client, client.send_voice, channel_id, msg.voice.file_id, caption=msg.caption)
                await asyncio.sleep(0.5)
            elif msg.audio:
                await send_with_retry(client, client.send_audio, channel_id, msg.audio.file_id, caption=msg.caption)
                await asyncio.sleep(0.5)
            
            return True
        else:
            # Normal message - copy using raw API
            try:
                await send_with_retry(client, client.invoke,
                    functions.messages.CopyMessages(
                        from_peer=await client.resolve_peer(msg.chat.id),
                        id=[msg.id],
                        to_peer=await client.resolve_peer(channel_id),
                        silent=False
                    )
                )
                await asyncio.sleep(0.5)
                return True
            except:
                # Fallback: send manually
                if msg.text:
                    await send_with_retry(client, client.send_message, channel_id, msg.text)
                    await asyncio.sleep(0.5)
                if msg.photo:
                    await send_with_retry(client, client.send_photo, channel_id, msg.photo.file_id, caption=msg.caption)
                    await asyncio.sleep(0.5)
                elif msg.video:
                    await send_with_retry(client, client.send_video, channel_id, msg.video.file_id, caption=msg.caption)
                    await asyncio.sleep(0.5)
                elif msg.sticker:
                    await send_with_retry(client, client.send_sticker, channel_id, msg.sticker.file_id)
                    await asyncio.sleep(0.5)
                elif msg.document:
                    await send_with_retry(client, client.send_document, channel_id, msg.document.file_id, caption=msg.caption)
                    await asyncio.sleep(0.5)
                elif msg.animation:
                    await send_with_retry(client, client.send_animation, channel_id, msg.animation.file_id, caption=msg.caption)
                    await asyncio.sleep(0.5)
                elif msg.voice:
                    await send_with_retry(client, client.send_voice, channel_id, msg.voice.file_id, caption=msg.caption)
                    await asyncio.sleep(0.5)
                elif msg.audio:
                    await send_with_retry(client, client.send_audio, channel_id, msg.audio.file_id, caption=msg.caption)
                    await asyncio.sleep(0.5)
                return True
    except FloodWait as e:
        wait_time = e.value if hasattr(e, 'value') else 60
        print(f"⚠️ FloodWait: Waiting {wait_time} seconds...")
        await asyncio.sleep(wait_time + 5)
        return await send_to_channel(client, msg, channel_id)
    except Exception as e:
        print(f"Error sending to {channel_id}: {e}")
        return False

async def send_to_channels(client, msg, channels):
    """Message ko sab channels mein send karega - FloodWait handle karega"""
    sent_count = 0
    
    for channel in channels:
        channel_id = channel.get("id")
        if await send_to_channel(client, msg, channel_id):
            sent_count += 1
        await asyncio.sleep(0.5)  # Har channel ke baad 0.5 sec delay
    
    return sent_count

# ═══════════════ COMMANDS ═══════════════
@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    await msg.reply_text(
        "📢 **AUTO-POST BOT**\n\n"
        "Mujhe channel admin banao aur main jo bhi msg bhejo ge woh channel par **exactly waisa hi** post kar dunga!\n\n"
        "✅ Forward message bina 'Forwarded From' tag ke post hoga!\n"
        "✅ Photo + Text + Premium Emoji sab saath mein post hoga!\n\n"
        "**Commands:**\n"
        "/start - Show this message\n"
        "/help - Help menu\n"
        "/addchannel CHANNEL_ID - Add channel by ID\n"
        "/removechannel CHANNEL_ID - Remove channel\n"
        "/listchannels - List all channels\n"
        "/check CHANNEL_ID - Check admin status"
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, msg):
    await msg.reply_text(
        "📖 **HELP MENU**\n\n"
        "**Commands:**\n"
        "/addchannel CHANNEL_ID - Add channel by ID\n"
        "/removechannel CHANNEL_ID - Remove channel\n"
        "/listchannels - List all channels\n"
        "/check CHANNEL_ID - Check admin status\n\n"
        "**How to get channel ID:**\n"
        "1️⃣ Channel mein @getidsbot bhejo\n"
        "2️⃣ Channel ID copy karo (negative number)\n"
        "3️⃣ /addchannel -123456789 bhejo\n\n"
        "**Features:**\n"
        "✅ Photo + Text + Premium Emoji sab saath mein post hoga\n"
        "✅ Forward message bina 'Forwarded From' tag ke\n"
        "✅ FloodWait handle karega - auto retry"
    )

@app.on_message(filters.command("check"))
async def check_cmd(client, msg):
    parts = msg.text.split(maxsplit=1)
    
    if len(parts) != 2:
        await msg.reply_text("❌ **Usage:** `/check CHANNEL_ID`")
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await msg.reply_text("❌ Invalid channel ID!")
        return
    
    status_msg = await msg.reply_text(f"🔍 Checking admin status...")
    is_admin, status = await check_admin(client, channel_id)
    
    if is_admin:
        await status_msg.edit_text(
            f"✅ **Bot is Admin!** 🎉\n\n"
            f"📢 **Channel ID:** `{channel_id}`\n"
            f"🔹 **Status:** {status}\n\n"
            "You can now add this channel using:\n"
            f"`/addchannel {channel_id}`"
        )
    else:
        await status_msg.edit_text(
            f"❌ **Bot is NOT Admin!**\n\n"
            f"📢 **Channel ID:** `{channel_id}`\n"
            f"🚫 **Reason:** {status}"
        )

@app.on_message(filters.command("addchannel"))
async def add_channel_cmd(client, msg):
    parts = msg.text.split(maxsplit=1)
    
    if len(parts) != 2:
        await msg.reply_text("❌ **Usage:** `/addchannel CHANNEL_ID`")
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await msg.reply_text("❌ Invalid channel ID!")
        return
    
    status_msg = await msg.reply_text(f"🔍 Checking admin status...")
    is_admin, status = await check_admin(client, channel_id)
    
    if not is_admin:
        await status_msg.edit_text(
            f"❌ **I'm not an admin!**\n\n"
            f"📢 **Channel ID:** `{channel_id}`\n"
            f"🚫 **Reason:** {status}"
        )
        return
    
    try:
        chat = await client.get_chat(channel_id)
        channel_name = chat.title or "Unknown"
    except:
        channel_name = "Unknown"
    
    if add_channel(channel_id, channel_name):
        await status_msg.edit_text(
            f"✅ **Channel Added!** 🎉\n\n"
            f"📢 **Name:** {channel_name}\n"
            f"🆔 **ID:** `{channel_id}`\n\n"
            "Now I will auto-post **exactly** whatever you send me!\n"
            "✅ Photo + Text + Premium Emoji sab saath mein post hoga!"
        )
    else:
        await status_msg.edit_text(
            f"⚠️ **Channel already added!**\n\n"
            f"📢 **Name:** {channel_name}\n"
            f"🆔 **ID:** `{channel_id}`"
        )

@app.on_message(filters.command("removechannel"))
async def remove_channel_cmd(client, msg):
    parts = msg.text.split(maxsplit=1)
    
    if len(parts) != 2:
        await msg.reply_text("❌ **Usage:** `/removechannel CHANNEL_ID`")
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await msg.reply_text("❌ Invalid channel ID!")
        return
    
    if remove_channel(channel_id):
        await msg.reply_text(f"✅ **Channel Removed!**\n\n🆔 **ID:** `{channel_id}`")
    else:
        await msg.reply_text(f"❌ **Channel not found!**\n\n🆔 **ID:** `{channel_id}`")

@app.on_message(filters.command("listchannels"))
async def list_channels_cmd(client, msg):
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text("📭 **No channels added yet!**")
        return
    
    text = "📋 **CHANNEL LIST**\n\n"
    for i, channel in enumerate(channels, 1):
        name = channel.get("name", "Unknown")
        channel_id = channel.get("id")
        text += f"**{i}.** {name}\n`{channel_id}`\n\n"
    
    await msg.reply_text(text)

# ═══════════════ AUTO-POST - ALL MESSAGES ═══════════════
@app.on_message(filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_all(client, msg):
    """Har type ke message ko catch karega aur channels mein send karega"""
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text("⚠️ No channels added! Use `/addchannel CHANNEL_ID` first.")
        return
    
    # Check if message has any content
    if not msg.text and not msg.photo and not msg.video and not msg.sticker and not msg.document and not msg.animation and not msg.voice and not msg.audio:
        await msg.reply_text("⚠️ Unsupported message type!")
        return
    
    sent_count = await send_to_channels(client, msg, channels)
    
    if sent_count > 0:
        # Detect message type for reply
        if msg.forward_from or msg.forward_from_chat:
            msg_type = "Forwarded message"
        elif msg.text:
            msg_type = "Text"
        elif msg.photo:
            msg_type = "Photo"
        elif msg.video:
            msg_type = "Video"
        elif msg.sticker:
            msg_type = "Sticker"
        elif msg.document:
            msg_type = "Document"
        elif msg.animation:
            msg_type = "Animation"
        elif msg.voice:
            msg_type = "Voice"
        elif msg.audio:
            msg_type = "Audio"
        else:
            msg_type = "Message"
        
        await msg.reply_text(f"✅ **{msg_type} posted to {sent_count} channel(s)!**")
    else:
        await msg.reply_text("❌ Failed to post to any channel!")

# ═══════════════ GET ID ═══════════════
@app.on_message(filters.command("getid"))
async def get_id_cmd(client, msg):
    chat = msg.chat
    await msg.reply_text(
        f"📋 **Chat Info**\n\n"
        f"📢 **Name:** {chat.title or chat.first_name or 'Unknown'}\n"
        f"🆔 **ID:** `{chat.id}`\n"
        f"📂 **Type:** {chat.type}"
    )

# ═══════════════ RUN WITH FLOOD WAIT HANDLER ═══════════════
async def main():
    """Bot start with flood wait handling"""
    try:
        print("""
╔══════════════════════════════════════╗
║  📢 AUTO-POST BOT - FLOOD WAIT FIX  ║
║  Photo + Text + Premium Emoji       ║
║  Sab Saath Mein Post Hoga           ║
║  FloodWait Handle Karega            ║
╚══════════════════════════════════════╝
        """)
        await app.start()
        print("✅ Bot Started Successfully!")
        await asyncio.Event().wait()
    except FloodWait as e:
        wait_time = e.value if hasattr(e, 'value') else 60
        print(f"⚠️ FloodWait: Waiting {wait_time} seconds before retry...")
        await asyncio.sleep(wait_time + 5)
        await main()
    except Exception as e:
        print(f"❌ Error: {e}")
        await asyncio.sleep(10)
        await main()

if __name__ == "__main__":
    try:
        app.run()
    except FloodWait as e:
        wait_time = e.value if hasattr(e, 'value') else 60
        print(f"⚠️ FloodWait: Waiting {wait_time} seconds...")
        time.sleep(wait_time + 5)
        app.run()

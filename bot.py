#!/usr/bin/env python3
"""
📢 AUTO-POST BOT - FINAL FIXED
Forward Message Waisa Hi Post Hoga, Sirf "Forwarded From" Tag Hatega
"""

import asyncio, json, os, re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions, types

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

# ═══════════════ COPY MESSAGE - EXACTLY WAISA HI ═══════════════
async def copy_message_exact(client, from_chat, msg_id, to_chat):
    """
    Message ko copy karega EXACTLY waisa hi, bina "Forwarded From" tag ke
    Premium emoji, formatting, sab same rahega
    """
    try:
        # Raw API call - copy message without forward tag
        result = await client.invoke(
            functions.messages.CopyMessages(
                from_peer=await client.resolve_peer(from_chat),
                id=[msg_id],
                to_peer=await client.resolve_peer(to_chat),
                silent=False,
                send_as=None,
                schedule_date=None
            )
        )
        return True
    except Exception as e:
        print(f"Copy error: {e}")
        return False

async def copy_to_channels(client, msg, channels):
    """Message ko channels mein copy karega EXACTLY waisa hi"""
    sent_count = 0
    
    for channel in channels:
        channel_id = channel.get("id")
        try:
            # Copy message (not forward) - no "Forwarded From" tag
            result = await client.invoke(
                functions.messages.CopyMessages(
                    from_peer=await client.resolve_peer(msg.chat.id),
                    id=[msg.id],
                    to_peer=await client.resolve_peer(channel_id),
                    silent=False
                )
            )
            if result:
                sent_count += 1
        except Exception as e:
            print(f"Error copying to {channel_id}: {e}")
    
    return sent_count

# ═══════════════ COMMANDS ═══════════════
@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    await msg.reply_text(
        "📢 **AUTO-POST BOT**\n\n"
        "Mujhe channel admin banao aur main jo bhi msg bhejo ge woh channel par **exactly waisa hi** post kar dunga!\n\n"
        "✅ Forward message bina 'Forwarded From' tag ke post hoga!\n"
        "✅ Premium emoji, text, media sab exactly waisa hi rahega!\n\n"
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
        "✅ Premium emoji exactly waisa hi post hoga\n"
        "✅ Forward message bina 'Forwarded From' tag ke\n"
        "✅ Text, photo, video, sticker sab exactly waisa hi"
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
            "✅ Forward messages bina tag ke post honge!\n"
            "✅ Premium emoji exactly waisa hi rahega!"
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

# ═══════════════ AUTO-POST - EXACT COPY ═══════════════
@app.on_message(filters.text & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_text(client, msg):
    channels = get_all_channels()
    if not channels:
        await msg.reply_text("⚠️ No channels added!")
        return
    
    sent_count = await copy_to_channels(client, msg, channels)
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Posted to {sent_count} channel(s)!**")

@app.on_message(filters.photo & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_photo(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    sent_count = await copy_to_channels(client, msg, channels)
    if sent_count > 0:
        await msg.reply_text(f"✅ **Photo posted to {sent_count} channel(s)!**")

@app.on_message(filters.video & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_video(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    sent_count = await copy_to_channels(client, msg, channels)
    if sent_count > 0:
        await msg.reply_text(f"✅ **Video posted to {sent_count} channel(s)!**")

@app.on_message(filters.sticker & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_sticker(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    sent_count = await copy_to_channels(client, msg, channels)
    if sent_count > 0:
        await msg.reply_text(f"✅ **Sticker posted to {sent_count} channel(s)!**")

@app.on_message(filters.document & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_document(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    sent_count = await copy_to_channels(client, msg, channels)
    if sent_count > 0:
        await msg.reply_text(f"✅ **Document posted to {sent_count} channel(s)!**")

@app.on_message(filters.animation & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_animation(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    sent_count = await copy_to_channels(client, msg, channels)
    if sent_count > 0:
        await msg.reply_text(f"✅ **Animation posted to {sent_count} channel(s)!**")

@app.on_message(filters.voice & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_voice(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    sent_count = await copy_to_channels(client, msg, channels)
    if sent_count > 0:
        await msg.reply_text(f"✅ **Voice posted to {sent_count} channel(s)!**")

@app.on_message(filters.audio & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "check"]))
async def auto_post_audio(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    sent_count = await copy_to_channels(client, msg, channels)
    if sent_count > 0:
        await msg.reply_text(f"✅ **Audio posted to {sent_count} channel(s)!**")

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

# ═══════════════ RUN ═══════════════
if not os.path.exists(CHANNEL_DB):
    jsave(CHANNEL_DB, {"channels": []})

print("""
╔══════════════════════════════════════╗
║  📢 AUTO-POST BOT - FINAL           ║
║  Copy Message Without Forward Tag   ║
║  Premium Emoji + Text + Media      ║
║  Sab Exactly Waisa Hi Rahega       ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

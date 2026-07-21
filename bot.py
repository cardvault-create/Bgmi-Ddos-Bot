#!/usr/bin/env python3
"""
📢 AUTO-POST BOT - FINAL FIXED
Admin Check Properly Working
"""

import asyncio, json, os, re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus

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

# ═══════════════ CHECK ADMIN - FINAL FIXED ═══════════════
async def check_admin(client, chat_id):
    """Check if bot is admin in channel - FINAL FIXED"""
    try:
        # Try to get bot member info
        bot_member = await client.get_chat_member(chat_id, "me")
        
        # LOGIC FIX: Check status properly
        # ChatMemberStatus.ADMINISTRATOR is an enum, compare with string or enum
        status = bot_member.status
        
        # Convert to string for comparison if needed
        if isinstance(status, ChatMemberStatus):
            status_str = status.value if hasattr(status, 'value') else str(status)
        else:
            status_str = str(status)
        
        print(f"Bot status: {status_str}")
        
        # Check if admin or creator
        if "administrator" in status_str.lower() or "creator" in status_str.lower():
            return True, "Admin ✅"
        else:
            return False, f"Bot is {status_str}"
            
    except Exception as e:
        error = str(e)
        print(f"Error checking admin: {error}")
        
        if "USER_NOT_PARTICIPANT" in error:
            return False, "❌ Bot is not a member of the channel!"
        elif "CHAT_ADMIN_REQUIRED" in error:
            return False, "❌ Bot is not admin!"
        elif "CHAT_ID_INVALID" in error:
            return False, "❌ Invalid channel ID!"
        elif "Forbidden" in error:
            return False, "❌ Bot cannot access this channel! Is bot added?"
        else:
            return False, f"⚠️ Error: {error[:100]}"

# ═══════════════ COMMANDS ═══════════════
@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    await msg.reply_text(
        "📢 **AUTO-POST BOT**\n\n"
        "Mujhe channel admin banao aur main jo bhi msg bhejo ge woh channel par post kar dunga!\n\n"
        "**Commands:**\n"
        "/start - Show this message\n"
        "/help - Help menu\n"
        "/addchannel CHANNEL_ID - Add channel by ID\n"
        "/removechannel CHANNEL_ID - Remove channel\n"
        "/listchannels - List all channels\n"
        "/check CHANNEL_ID - Check admin status\n"
        "/post - Post message to channel\n\n"
        "**How to use:**\n"
        "1️⃣ Bot ko channel admin banao\n"
        "2️⃣ /addchannel -123456789 bhejo\n"
        "3️⃣ Ab jo bhi message bhejo ge channel par post ho jayega!"
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, msg):
    await msg.reply_text(
        "📖 **HELP MENU**\n\n"
        "**Commands:**\n"
        "/addchannel CHANNEL_ID - Add channel by ID\n"
        "/removechannel CHANNEL_ID - Remove channel\n"
        "/listchannels - List all channels\n"
        "/check CHANNEL_ID - Check admin status\n"
        "/post - Post message to channel\n\n"
        "**How to get channel ID:**\n"
        "1️⃣ Channel mein @getidsbot bhejo\n"
        "2️⃣ Channel ID copy karo (negative number)\n"
        "3️⃣ /addchannel -123456789 bhejo"
    )

@app.on_message(filters.command("check"))
async def check_cmd(client, msg):
    parts = msg.text.split(maxsplit=1)
    
    if len(parts) != 2:
        await msg.reply_text(
            "❌ **Usage:** `/check CHANNEL_ID`\n\n"
            "Example: `/check -100123456789`"
        )
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await msg.reply_text("❌ Invalid channel ID!")
        return
    
    # Send status message
    status_msg = await msg.reply_text(f"🔍 Checking admin status for `{channel_id}`...")
    
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
            f"🚫 **Reason:** {status}\n\n"
            "**Please follow these steps:**\n"
            "1️⃣ Add bot to the channel\n"
            "2️⃣ Make bot admin with **Post Messages** permission\n"
            "3️⃣ Wait 5 seconds and try `/check` again\n\n"
            "**Make sure:**\n"
            "✅ Bot is in the channel\n"
            "✅ Bot has admin permissions\n"
            "✅ Bot can post messages"
        )

@app.on_message(filters.command("addchannel"))
async def add_channel_cmd(client, msg):
    parts = msg.text.split(maxsplit=1)
    
    if len(parts) != 2:
        await msg.reply_text(
            "❌ **Usage:** `/addchannel CHANNEL_ID`\n\n"
            "Example: `/addchannel -100123456789`"
        )
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await msg.reply_text("❌ Invalid channel ID!")
        return
    
    status_msg = await msg.reply_text(f"🔍 Checking admin status for `{channel_id}`...")
    is_admin, status = await check_admin(client, channel_id)
    
    if not is_admin:
        await status_msg.edit_text(
            f"❌ **I'm not an admin!**\n\n"
            f"📢 **Channel ID:** `{channel_id}`\n"
            f"🚫 **Reason:** {status}\n\n"
            "Use `/check CHANNEL_ID` to verify first."
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
            "Now I will auto-post all messages to this channel!\n"
            "Send any message to me privately."
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
        await msg.reply_text(
            "❌ **Usage:** `/removechannel CHANNEL_ID`\n\n"
            "Example: `/removechannel -100123456789`"
        )
        return
    
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await msg.reply_text("❌ Invalid channel ID!")
        return
    
    if remove_channel(channel_id):
        await msg.reply_text(
            f"✅ **Channel Removed!**\n\n"
            f"🆔 **ID:** `{channel_id}`"
        )
    else:
        await msg.reply_text(
            f"❌ **Channel not found!**\n\n"
            f"🆔 **ID:** `{channel_id}`"
        )

@app.on_message(filters.command("listchannels"))
async def list_channels_cmd(client, msg):
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text("📭 **No channels added yet!**\n\nUse `/addchannel CHANNEL_ID` to add.")
        return
    
    text = "📋 **CHANNEL LIST**\n\n"
    for i, channel in enumerate(channels, 1):
        name = channel.get("name", "Unknown")
        channel_id = channel.get("id")
        text += f"**{i}.** {name}\n`{channel_id}`\n\n"
    
    await msg.reply_text(text)

# ═══════════════ AUTO-POST ═══════════════
@app.on_message(filters.text & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post", "check"]))
async def auto_post_text(client, msg):
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text(
            "⚠️ **No channels added!**\n\n"
            "Add a channel first using `/addchannel CHANNEL_ID`"
        )
        return
    
    sent_count = 0
    for channel in channels:
        channel_id = channel.get("id")
        try:
            await client.send_message(channel_id, msg.text)
            sent_count += 1
        except Exception as e:
            print(f"Error posting to {channel_id}: {e}")
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Message posted to {sent_count} channel(s)!**")
    else:
        await msg.reply_text("❌ Failed to post to any channel!")

@app.on_message(filters.command("post"))
async def post_cmd(client, msg):
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text("⚠️ No channels added! Use `/addchannel CHANNEL_ID` first.")
        return
    
    if msg.reply_to_message:
        reply_msg = msg.reply_to_message
        sent_count = 0
        
        for channel in channels:
            channel_id = channel.get("id")
            try:
                if reply_msg.text:
                    await client.send_message(channel_id, reply_msg.text)
                elif reply_msg.photo:
                    await client.send_photo(channel_id, reply_msg.photo.file_id, caption=reply_msg.caption)
                elif reply_msg.video:
                    await client.send_video(channel_id, reply_msg.video.file_id, caption=reply_msg.caption)
                elif reply_msg.sticker:
                    await client.send_sticker(channel_id, reply_msg.sticker.file_id)
                elif reply_msg.document:
                    await client.send_document(channel_id, reply_msg.document.file_id, caption=reply_msg.caption)
                sent_count += 1
            except Exception as e:
                print(f"Error: {e}")
        
        await msg.reply_text(f"✅ **Posted to {sent_count} channel(s)!**")
    else:
        parts = msg.text.split(maxsplit=1)
        if len(parts) < 2:
            await msg.reply_text("❌ **Usage:** `/post Hello World!`\nOr reply to a message and `/post`")
            return
        
        text = parts[1]
        sent_count = 0
        
        for channel in channels:
            channel_id = channel.get("id")
            try:
                await client.send_message(channel_id, text)
                sent_count += 1
            except Exception as e:
                print(f"Error: {e}")
        
        await msg.reply_text(f"✅ **Posted to {sent_count} channel(s)!**")

# ═══════════════ MEDIA AUTO-POST ═══════════════
@app.on_message(filters.photo & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post", "check"]))
async def auto_post_photo(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    
    sent_count = 0
    for channel in channels:
        channel_id = channel.get("id")
        try:
            await client.send_photo(channel_id, msg.photo.file_id, caption=msg.caption)
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Photo posted to {sent_count} channel(s)!**")

@app.on_message(filters.video & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post", "check"]))
async def auto_post_video(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    
    sent_count = 0
    for channel in channels:
        channel_id = channel.get("id")
        try:
            await client.send_video(channel_id, msg.video.file_id, caption=msg.caption)
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Video posted to {sent_count} channel(s)!**")

@app.on_message(filters.sticker & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post", "check"]))
async def auto_post_sticker(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    
    sent_count = 0
    for channel in channels:
        channel_id = channel.get("id")
        try:
            await client.send_sticker(channel_id, msg.sticker.file_id)
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Sticker posted to {sent_count} channel(s)!**")

@app.on_message(filters.document & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post", "check"]))
async def auto_post_document(client, msg):
    channels = get_all_channels()
    if not channels:
        return
    
    sent_count = 0
    for channel in channels:
        channel_id = channel.get("id")
        try:
            await client.send_document(channel_id, msg.document.file_id, caption=msg.caption)
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Document posted to {sent_count} channel(s)!**")

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
║  📢 AUTO-POST BOT - FINAL FIXED     ║
║  Admin Check Properly Working       ║
║  Token: 8771905727:AAEJ...          ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

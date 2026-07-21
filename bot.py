#!/usr/bin/env python3
"""
📢 AUTO-POST BOT
Channel Admin Banne Ke Baad Jo Bhi Message Bhejo Channel Par Upload Kar De
"""

import asyncio, json, os, re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

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
    if channel_id not in data["channels"]:
        data["channels"].append(channel_id)
        jsave(CHANNEL_DB, data)
        return True
    return False

def remove_channel(channel_id):
    data = get_channels()
    if channel_id in data["channels"]:
        data["channels"].remove(channel_id)
        jsave(CHANNEL_DB, data)
        return True
    return False

def get_all_channels():
    return get_channels()["channels"]

# ═══════════════ START COMMAND ═══════════════
@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    await msg.reply_text(
        "📢 **AUTO-POST BOT**\n\n"
        "Mujhe channel admin banao aur main jo bhi msg bhejo ge woh channel par post kar dunga!\n\n"
        "**Commands:**\n"
        "/start - Show this message\n"
        "/help - Help menu\n"
        "/addchannel - Add current channel\n"
        "/removechannel - Remove channel\n"
        "/listchannels - List all channels\n"
        "/post - Post message to channel\n\n"
        "**How to use:**\n"
        "1️⃣ Bot ko channel admin banao\n"
        "2️⃣ Channel mein /addchannel command bhejo\n"
        "3️⃣ Ab jo bhi message bhejo ge channel par post ho jayega!"
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, msg):
    await msg.reply_text(
        "📖 **HELP MENU**\n\n"
        "**Commands:**\n"
        "/addchannel - Add current channel\n"
        "/removechannel - Remove channel\n"
        "/listchannels - List all channels\n"
        "/post - Post message to channel\n\n"
        "**How to add channel:**\n"
        "1️⃣ Bot ko channel admin banao (post permission)\n"
        "2️⃣ Channel mein /addchannel bhejo\n"
        "3️⃣ Done! Ab jo bhi msg bhejo ge channel par post hoga!\n\n"
        "**How to post manually:**\n"
        "/post Hello World!\n"
        "Reply to a message and /post"
    )

# ═══════════════ CHANNEL MANAGEMENT ═══════════════
@app.on_message(filters.command("addchannel"))
async def add_channel_cmd(client, msg):
    chat = msg.chat
    
    # Check if it's a channel
    if chat.type not in ["channel", "supergroup"]:
        await msg.reply_text("❌ This command only works in channels or supergroups!")
        return
    
    channel_id = chat.id
    channel_name = chat.title or "Unknown"
    
    # Check if bot is admin
    try:
        bot_member = await client.get_chat_member(channel_id, "me")
        if bot_member.status not in ["administrator", "creator"]:
            await msg.reply_text(
                f"❌ **I'm not an admin!**\n\n"
                f"Please add me as admin in:\n"
                f"**{channel_name}**\n\n"
                f"Then try again!"
            )
            return
    except:
        await msg.reply_text(
            f"❌ **Error checking admin status!**\n\n"
            f"Please make sure I'm an admin in:\n"
            f"**{channel_name}**"
        )
        return
    
    # Add channel
    if add_channel(channel_id, channel_name):
        await msg.reply_text(
            f"✅ **Channel Added!**\n\n"
            f"📢 **Name:** {channel_name}\n"
            f"🆔 **ID:** `{channel_id}`\n\n"
            "Now I will auto-post all messages to this channel!"
        )
    else:
        await msg.reply_text(
            f"⚠️ **Channel already added!**\n\n"
            f"📢 **Name:** {channel_name}\n"
            f"🆔 **ID:** `{channel_id}`"
        )

@app.on_message(filters.command("removechannel"))
async def remove_channel_cmd(client, msg):
    chat = msg.chat
    
    if chat.type not in ["channel", "supergroup"]:
        await msg.reply_text("❌ This command only works in channels or supergroups!")
        return
    
    channel_id = chat.id
    channel_name = chat.title or "Unknown"
    
    if remove_channel(channel_id):
        await msg.reply_text(
            f"✅ **Channel Removed!**\n\n"
            f"📢 **Name:** {channel_name}\n"
            f"🆔 **ID:** `{channel_id}`\n\n"
            "I will no longer auto-post to this channel."
        )
    else:
        await msg.reply_text(
            f"❌ **Channel not found!**\n\n"
            f"📢 **Name:** {channel_name}\n\n"
            "This channel is not in my list."
        )

@app.on_message(filters.command("listchannels"))
async def list_channels_cmd(client, msg):
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text("📭 **No channels added yet!**\n\nUse /addchannel to add a channel.")
        return
    
    text = "📋 **CHANNEL LIST**\n\n"
    for i, channel_id in enumerate(channels, 1):
        try:
            chat = await client.get_chat(channel_id)
            name = chat.title or "Unknown"
            text += f"**{i}.** {name}\n`{channel_id}`\n\n"
        except:
            text += f"**{i}.** Unknown Channel\n`{channel_id}`\n\n"
    
    await msg.reply_text(text)

# ═══════════════ AUTO-POST SYSTEM ═══════════════
@app.on_message(filters.text & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post"]))
async def auto_post_text(client, msg):
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text(
            "⚠️ **No channels added!**\n\n"
            "Add a channel first using /addchannel command in the channel."
        )
        return
    
    # Send to all channels
    sent_count = 0
    failed_channels = []
    
    for channel_id in channels:
        try:
            # Get original message content
            text = msg.text
            
            # Check if message has reply
            if msg.reply_to_message:
                reply_msg = msg.reply_to_message
                if reply_msg.text:
                    text = reply_msg.text + "\n\n" + text
                elif reply_msg.photo:
                    await client.send_photo(
                        channel_id,
                        reply_msg.photo.file_id,
                        caption=text
                    )
                    continue
                elif reply_msg.video:
                    await client.send_video(
                        channel_id,
                        reply_msg.video.file_id,
                        caption=text
                    )
                    continue
                elif reply_msg.sticker:
                    await client.send_sticker(
                        channel_id,
                        reply_msg.sticker.file_id
                    )
                    continue
            
            # Send text
            await client.send_message(channel_id, text)
            sent_count += 1
            
        except Exception as e:
            failed_channels.append(channel_id)
            print(f"Error posting to {channel_id}: {e}")
    
    # Send confirmation
    if sent_count > 0:
        await msg.reply_text(
            f"✅ **Message posted to {sent_count} channels!**"
        )
    else:
        await msg.reply_text(
            f"❌ **Failed to post to any channel!**\n\n"
            "Make sure I'm still admin in the channels."
        )

# ═══════════════ POST COMMAND ═══════════════
@app.on_message(filters.command("post"))
async def post_cmd(client, msg):
    channels = get_all_channels()
    
    if not channels:
        await msg.reply_text("⚠️ No channels added! Use /addchannel first.")
        return
    
    # Check if replying to a message
    if msg.reply_to_message:
        reply_msg = msg.reply_to_message
        
        sent_count = 0
        for channel_id in channels:
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
        
        await msg.reply_text(f"✅ **Posted to {sent_count} channels!**")
        
    else:
        # Get text after /post
        parts = msg.text.split(maxsplit=1)
        if len(parts) < 2:
            await msg.reply_text(
                "❌ **Usage:**\n"
                "/post Hello World!\n"
                "Or reply to a message and /post"
            )
            return
        
        text = parts[1]
        
        sent_count = 0
        for channel_id in channels:
            try:
                await client.send_message(channel_id, text)
                sent_count += 1
            except Exception as e:
                print(f"Error: {e}")
        
        await msg.reply_text(f"✅ **Posted to {sent_count} channels!**")

# ═══════════════ PHOTO/VIDEO/STICKER AUTO-POST ═══════════════
@app.on_message(filters.photo & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post"]))
async def auto_post_photo(client, msg):
    channels = get_all_channels()
    
    if not channels:
        return
    
    sent_count = 0
    for channel_id in channels:
        try:
            await client.send_photo(
                channel_id,
                msg.photo.file_id,
                caption=msg.caption
            )
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Photo posted to {sent_count} channels!**")

@app.on_message(filters.video & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post"]))
async def auto_post_video(client, msg):
    channels = get_all_channels()
    
    if not channels:
        return
    
    sent_count = 0
    for channel_id in channels:
        try:
            await client.send_video(
                channel_id,
                msg.video.file_id,
                caption=msg.caption
            )
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Video posted to {sent_count} channels!**")

@app.on_message(filters.sticker & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post"]))
async def auto_post_sticker(client, msg):
    channels = get_all_channels()
    
    if not channels:
        return
    
    sent_count = 0
    for channel_id in channels:
        try:
            await client.send_sticker(channel_id, msg.sticker.file_id)
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Sticker posted to {sent_count} channels!**")

@app.on_message(filters.document & filters.private & ~filters.command(["start", "help", "addchannel", "removechannel", "listchannels", "post"]))
async def auto_post_document(client, msg):
    channels = get_all_channels()
    
    if not channels:
        return
    
    sent_count = 0
    for channel_id in channels:
        try:
            await client.send_document(
                channel_id,
                msg.document.file_id,
                caption=msg.caption
            )
            sent_count += 1
        except:
            pass
    
    if sent_count > 0:
        await msg.reply_text(f"✅ **Document posted to {sent_count} channels!**")

# ═══════════════ RUN ═══════════════
if not os.path.exists(CHANNEL_DB):
    jsave(CHANNEL_DB, {"channels": []})

print("""
╔══════════════════════════════════════╗
║  📢 AUTO-POST BOT                   ║
║  Channel Admin Banne Ke Baad        ║
║  Jo Bhi Bhejo Channel Par Post      ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

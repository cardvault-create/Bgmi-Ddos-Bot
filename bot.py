#!/usr/bin/env python3
"""
🎯 EMOJI PACK EXTRACTOR BOT
Emoji Pack Link Se Saare Emoji 1-1 Karke Bhejta Hai
"""

import asyncio, json, re, os, requests
from pyrogram import Client, filters
from pyrogram.types import Message

# ═══════════════ CONFIG ═══════════════
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8771905727:AAEJq2QVVSe8OxZOqLkatVK1wGysO9UyzCQ"
OWNER_ID = 1987818347

# ═══════════════ BOT ═══════════════
app = Client("emoji_extractor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ═══════════════ HELPERS ═══════════════
def extract_pack_name(link):
    """Emoji pack link se pack name extract karein"""
    # Example: t.me/addemoji/MyCoolPack
    # or: https://t.me/addemoji/MyCoolPack
    
    patterns = [
        r"t\.me/addemoji/([^\s/]+)",
        r"https?://t\.me/addemoji/([^\s/]+)",
        r"addemoji/([^\s/]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return None

def get_emoji_pack_data(pack_name):
    """
    @Stickers bot se pack data fetch karein
    Note: Yeh official API nahi hai, alternative method hai
    """
    try:
        # Telegram Sticker Pack API
        url = f"https://api.telegram.org/bot{STICKER_BOT_TOKEN}/getStickerSet"
        params = {"name": pack_name}
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                stickers = data.get("result", {}).get("stickers", [])
                return [s.get("file_id") for s in stickers]
    except:
        pass
    return []

# ═══════════════ STICKER BOT TOKEN ═══════════════
# @Stickers bot ka token (yeh public nahi hai, isliye alternative method)
# Actual method: @Stickers bot se interact karna
STICKER_BOT_TOKEN = "YOUR_STICKER_BOT_TOKEN"  # Ye nahi milega public

# ═══════════════ ALTERNATIVE METHOD ═══════════════
async def get_emoji_ids_from_pack(pack_name):
    """
    Alternative method - Pyrogram se pack fetch karein
    """
    try:
        # Pyrogram ka get_sticker_set method
        sticker_set = await app.get_sticker_set(pack_name)
        if sticker_set:
            return [sticker.file_id for sticker in sticker_set.stickers]
    except Exception as e:
        print(f"Error: {e}")
    return []

# ═══════════════ COMMAND: /start ═══════════════
@app.on_message(filters.command("start"))
async def start_cmd(client, msg):
    await msg.reply_text(
        "🎯 **EMOJI PACK EXTRACTOR BOT**\n\n"
        "Mujhe emoji pack ka link bhejo aur main saare emoji 1-1 karke bhej dunga!\n\n"
        "**Example:**\n"
        "`t.me/addemoji/MyCoolPack`\n"
        "`https://t.me/addemoji/MyCoolPack`\n\n"
        "**Commands:**\n"
        "/start - Show this message\n"
        "/help - Help menu"
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, msg):
    await msg.reply_text(
        "📖 **HELP MENU**\n\n"
        "**Kaise Use Karein:**\n"
        "1️⃣ Emoji pack ka link copy karein\n"
        "2️⃣ Bot ko link bhejein\n"
        "3️⃣ Bot saare emoji 1-1 karke bhejega\n\n"
        "**Supported Links:**\n"
        "• `t.me/addemoji/PackName`\n"
        "• `https://t.me/addemoji/PackName`\n\n"
        "**Note:** Telegram premium na ho toh bhi chalega!"
    )

# ═══════════════ EMOJI PACK PROCESS ═══════════════
@app.on_message(filters.text & filters.private)
async def handle_emoji_pack(client, msg):
    text = msg.text.strip()
    
    # Check if it's an emoji pack link
    pack_name = extract_pack_name(text)
    
    if not pack_name:
        await msg.reply_text(
            "❌ **Invalid emoji pack link!**\n\n"
            "Please send a valid link like:\n"
            "`t.me/addemoji/MyCoolPack`"
        )
        return
    
    # Step 1: Acknowledge
    status_msg = await msg.reply_text(
        f"⏳ **Fetching emojis from pack:** `{pack_name}`\n\n"
        "Please wait..."
    )
    
    # Step 2: Get emoji IDs
    try:
        # Try Pyrogram method
        sticker_set = await client.get_sticker_set(pack_name)
        
        if not sticker_set or not sticker_set.stickers:
            await status_msg.edit_text(
                f"❌ **No emojis found in pack:** `{pack_name}`\n\n"
                "Make sure the pack name is correct."
            )
            return
        
        emoji_list = sticker_set.stickers
        total = len(emoji_list)
        
        # Step 3: Update status
        await status_msg.edit_text(
            f"✅ **Found {total} emojis in pack:** `{pack_name}`\n\n"
            "🔄 Sending emojis one by one..."
        )
        
        # Step 4: Send each emoji
        sent_count = 0
        for i, sticker in enumerate(emoji_list, 1):
            try:
                await client.send_sticker(msg.chat.id, sticker.file_id)
                sent_count += 1
                await asyncio.sleep(0.5)  # Rate limit
            except Exception as e:
                print(f"Error sending emoji {i}: {e}")
        
        # Step 5: Final message
        await status_msg.edit_text(
            f"✅ **All {sent_count} emojis sent successfully!** 🎉\n\n"
            f"📦 Pack: `{pack_name}`\n"
            f"📤 Total: {sent_count} emojis\n\n"
            "Send another pack link to extract more emojis!"
        )
        
    except Exception as e:
        await status_msg.edit_text(
            f"❌ **Error fetching pack:** `{pack_name}`\n\n"
            f"Error: {str(e)[:100]}\n\n"
            "Make sure:\n"
            "1. Pack name is correct\n"
            "2. Pack is public\n"
            "3. Try again"
        )

# ═══════════════ VOICE COMMAND ═══════════════
@app.on_message(filters.command("extract"))
async def extract_cmd(client, msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) != 2:
        await msg.reply_text(
            "❌ **Usage:** `/extract pack_name`\n\n"
            "Example: `/extract MyCoolPack`"
        )
        return
    
    pack_name = parts[1].strip()
    
    # Same as above, process pack
    status_msg = await msg.reply_text(f"⏳ Fetching emojis from pack: `{pack_name}`...")
    
    try:
        sticker_set = await client.get_sticker_set(pack_name)
        
        if not sticker_set or not sticker_set.stickers:
            await status_msg.edit_text(f"❌ No emojis found in pack: `{pack_name}`")
            return
        
        emoji_list = sticker_set.stickers
        total = len(emoji_list)
        
        await status_msg.edit_text(f"✅ Found {total} emojis in pack: `{pack_name}`\n\n🔄 Sending...")
        
        sent_count = 0
        for i, sticker in enumerate(emoji_list, 1):
            try:
                await client.send_sticker(msg.chat.id, sticker.file_id)
                sent_count += 1
                await asyncio.sleep(0.5)
            except:
                pass
        
        await status_msg.edit_text(
            f"✅ **All {sent_count} emojis sent!** 🎉\n\n"
            f"📦 Pack: `{pack_name}`"
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")

# ═══════════════ RUN ═══════════════
print("""
╔══════════════════════════════════════╗
║  🎯 EMOJI PACK EXTRACTOR BOT        ║
║  Saare Emoji 1-1 Karke Bhejega      ║
║  Premium Ki Zaroorat Nahi           ║
╚══════════════════════════════════════╝
✅ Bot Ready!
""")

if __name__ == "__main__":
    app.run()

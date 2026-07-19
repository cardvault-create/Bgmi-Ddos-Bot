# ═══════════════ APNA DATA BHARO ═══════════════

# 1. my.telegram.org se API_ID aur API_HASH lo
API_ID = 35140329  # ← CHANGE
API_HASH = "011f638e4acadee178c59afffc80193d"  # ← CHANGE

# 2. @BotFather se 11 BOTS BANAO (1 master + 10 nodes)
MASTER_BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"  # ← Master Bot Token

# 3. 10 Nodes ke liye 10 alag bots
NODE_TOKENS = [
    "bot1_token",   # Node 1 ka bot token
    "bot2_token",   # Node 2 ka bot token
    "bot3_token",   # Node 3 ka bot token
    "bot4_token",   # Node 4 ka bot token
    "bot5_token",   # Node 5 ka bot token
    "bot6_token",   # Node 6 ka bot token
    "bot7_token",   # Node 7 ka bot token
    "bot8_token",   # Node 8 ka bot token
    "bot9_token",   # Node 9 ka bot token
    "bot10_token",  # Node 10 ka bot token
]

# 4. @userinfobot se apna Telegram User ID lo
ADMIN_ID = 1987818347  # ← CHANGE

# Attack Settings (change mat karo)
MAX_THREADS = 3000
MAX_DURATION = 300
BGMI_PORTS = list(range(7000, 15000)) + [17500, 20000, 27000]

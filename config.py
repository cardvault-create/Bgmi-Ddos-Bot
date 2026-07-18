# config.py
import os

# Bot Configuration
API_ID = 35140329  # Apna API ID dalo (my.telegram.org se)
API_HASH = "011f638e4acadee178c59afffc80193d"  # Apna API Hash dalo
BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"  # Apna Bot Token dalo (@BotFather se)

# Session directory
SESSION_DIR = 'sessions'
os.makedirs(SESSION_DIR, exist_ok=True)

# Authorized Users
AUTHORIZED_USERS = [1987818347]  # Apna Telegram User ID dalo

# Target Configuration
TARGET_IP = "127.0.0.1"
TARGET_PORT = 8080

# Attack Configuration
MAX_THREADS = 1000
MAX_DURATION = 600
DEFAULT_DURATION = 60

import os

# ============================================
# 🔐 TELEGRAM API CONFIGURATION
# ============================================
API_ID = 35140329                # my.telegram.org se lein
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8881462630:AAEQX_BDAkR9wRehuE2fO2RoCoNUybBwVWs"  # @BotFather se

# ============================================
# 👤 AUTHORIZED USERS
# ============================================
AUTHORIZED_USERS = [1987818347]  # Apna Telegram ID

# ============================================
# 🎯 DEFAULT TARGET (Apna test server daalein)
# ============================================
TARGET_IP = "127.0.0.1"         # Localhost (apna server)
TARGET_PORT = 8080              # Default port

# ============================================
# ⚙️ MAX SETTINGS (600 seconds = 10 minutes)
# ============================================
MAX_THREADS = 1000              # Max threads
DEFAULT_DURATION = 60           # Default duration seconds
MAX_DURATION = 600              # Max 600 seconds (10 minutes)

# ============================================
# 🎨 BOT SETTINGS
# ============================================
BOT_NAME = "BGMI Stress Tester Pro v3.0"
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

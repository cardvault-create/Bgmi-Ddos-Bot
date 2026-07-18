import os

# ============================================
# 🔐 TELEGRAM API CONFIGURATION
# ============================================
API_ID = 1234567                # my.telegram.org se lein
API_HASH = "your_api_hash_here"
BOT_TOKEN = "your_bot_token_here"  # @BotFather se

# ============================================
# 👤 AUTHORIZED USERS
# ============================================
AUTHORIZED_USERS = [123456789]  # Apna Telegram ID

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

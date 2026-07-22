# ═══════════════ CONFIG ═══════════════
import os

# 🔥 Railway par environment variables use karo
TOKEN = os.environ.get("BOT_TOKEN", "8771905727:AAEJq2QVVSe8OxZOqLkatVK1wGysO9UyzCQ")
OWNER_ID = int(os.environ.get("OWNER_ID", 1987818347))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "FathersOfCreater")

# 🔥 MongoDB URI - Environment variable se lo
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://bgmipower9999_db_user:bgmi123@cluster0.qgej2dh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Attack Settings
MAX_THREADS = 1500
MAX_TIME = 600

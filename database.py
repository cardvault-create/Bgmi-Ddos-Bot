import json
import os
from datetime import datetime
from config import MONGO_URI

# ═══════════════ JSON FALLBACK ═══════════════
DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "orders": [], "logs": [], "keys": []}
    return {"users": {}, "orders": [], "logs": [], "keys": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4, default=str)

# ═══════════════ TRY MONGODB ═══════════════
try:
    from pymongo import MongoClient
    import certifi
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['bgmi_ddos']
    users_col = db['users']
    logs_col = db['logs']
    keys_col = db['keys']
    print("✅ MongoDB Connected Successfully!")
    USE_MONGO = True
except Exception as e:
    print(f"⚠️ MongoDB Error: {e}")
    print("✅ Using JSON Database")
    USE_MONGO = False

# ═══════════════ DATABASE FUNCTIONS ═══════════════
def get_user(user_id):
    user_id = str(user_id)
    if USE_MONGO:
        try:
            user = users_col.find_one({'_id': user_id})
            if not user:
                user = {
                    '_id': user_id,
                    'name': '',
                    'username': '',
                    'joined': datetime.now().isoformat(),
                    'plan': 'free',
                    'expiry': None,
                    'threads': 1000,
                    'max_time': 60,
                    'orders': [],
                    'total_attacks': 0,
                    'banned': False
                }
                users_col.insert_one(user)
            return user
        except:
            pass
    
    # JSON Fallback
    db_data = load_db()
    if user_id not in db_data["users"]:
        db_data["users"][user_id] = {
            "name": "",
            "username": "",
            "joined": datetime.now().isoformat(),
            "plan": "free",
            "expiry": None,
            "threads": 1000,
            "max_time": 60,
            "orders": [],
            "total_attacks": 0,
            "banned": False
        }
        save_db(db_data)
    return db_data["users"][user_id]

def update_user(user_id, data):
    user_id = str(user_id)
    if USE_MONGO:
        try:
            update_data = {}
            for key, value in data.items():
                if key == '$inc':
                    for k, v in value.items():
                        update_data[k] = v
                else:
                    update_data[key] = value
            users_col.update_one({'_id': user_id}, {'$set': update_data}, upsert=True)
            return
        except:
            pass
    
    # JSON Fallback
    db_data = load_db()
    if user_id not in db_data["users"]:
        get_user(user_id)
        db_data = load_db()
    for key, value in data.items():
        if key == '$inc':
            for k, v in value.items():
                db_data["users"][user_id][k] = db_data["users"][user_id].get(k, 0) + v
        else:
            db_data["users"][user_id][key] = value
    save_db(db_data)

def save_log(user_id, ip, port, duration, packets, method):
    if USE_MONGO:
        try:
            logs_col.insert_one({
                'user_id': str(user_id),
                'ip': ip,
                'port': port,
                'duration': duration,
                'packets': packets,
                'method': method,
                'time': datetime.now().isoformat()
            })
            return
        except:
            pass
    
    db_data = load_db()
    db_data["logs"].append({
        "user_id": str(user_id),
        "ip": ip,
        "port": port,
        "duration": duration,
        "packets": packets,
        "method": method,
        "time": datetime.now().isoformat()
    })
    save_db(db_data)

def create_key(plan, duration):
    import random, string
    key_code = f"BGMI-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    
    if USE_MONGO:
        try:
            keys_col.insert_one({
                'key': key_code,
                'plan': plan,
                'duration': duration,
                'used': False,
                'created_at': datetime.now().isoformat()
            })
            return key_code
        except:
            pass
    
    db_data = load_db()
    db_data["keys"].append({
        "key": key_code,
        "plan": plan,
        "duration": duration,
        "used": False
    })
    save_db(db_data)
    return key_code

def redeem_key(key_code, user_id):
    user_id = str(user_id)
    
    if USE_MONGO:
        try:
            key = keys_col.find_one({'key': key_code, 'used': False})
            if key:
                keys_col.update_one({'_id': key['_id']}, {'$set': {'used': True, 'used_by': user_id}})
                from datetime import timedelta
                expiry = datetime.now() + timedelta(days=key['duration'])
                users_col.update_one(
                    {'_id': user_id},
                    {'$set': {
                        'plan': key['plan'],
                        'expiry': expiry.isoformat(),
                        'threads': 5000,
                        'max_time': 600
                    }}
                )
                return True, key['plan'], key['duration']
            return False, None, None
        except:
            pass
    
    # JSON Fallback
    db_data = load_db()
    for key in db_data["keys"]:
        if key["key"] == key_code and not key["used"]:
            key["used"] = True
            from datetime import timedelta
            expiry = datetime.now() + timedelta(days=key["duration"])
            db_data["users"][user_id]["plan"] = key["plan"]
            db_data["users"][user_id]["expiry"] = expiry.isoformat()
            db_data["users"][user_id]["threads"] = 5000
            db_data["users"][user_id]["max_time"] = 600
            save_db(db_data)
            return True, key["plan"], key["duration"]
    return False, None, None

def load_db():
    if os.path.exists("database.json"):
        try:
            with open("database.json", 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "orders": [], "logs": [], "keys": []}
    return {"users": {}, "orders": [], "logs": [], "keys": []}

def save_db(data):
    with open("database.json", 'w') as f:
        json.dump(data, f, indent=4, default=str)

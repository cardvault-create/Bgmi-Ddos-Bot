#!/usr/bin/env python3
"""
BGMI Test Server Simulator - Apne local network mein chalayein
Yeh server simulate karega BGMI jaisa game server
"""

import socket
import threading
import time
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

# Configuration
TCP_PORT = 8080
UDP_PORT = 9000
HTTP_PORT = 8081

# Server stats
tcp_connections = 0
udp_packets = 0
http_requests = 0
server_running = True

class BGMIHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global http_requests
        http_requests += 1
        
        # Simulate BGMI API endpoints
        if "/login" in self.path:
            response = {"status": "success", "token": "bgmi_test_token", "player_id": random.randint(1000,9999)}
        elif "/match" in self.path:
            response = {"status": "success", "match_id": f"match_{random.randint(10000,99999)}", "server_ip": "192.168.1.100"}
        elif "/heartbeat" in self.path:
            response = {"status": "alive", "timestamp": time.time()}
        else:
            response = {"status": "ok", "message": "BGMI Test Server", "connections": tcp_connections}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
        
        # Simulate processing delay
        time.sleep(0.01)
    
    def log_message(self, format, *args):
        # Silence logging
        pass

def tcp_server():
    global tcp_connections, server_running
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", TCP_PORT))
    s.listen(500)
    print(f"[+] TCP Server listening on port {TCP_PORT}")
    
    while server_running:
        try:
            s.settimeout(1)
            conn, addr = s.accept()
            tcp_connections += 1
            conn.settimeout(0.5)
            try:
                data = conn.recv(4096)
                conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
            except:
                pass
            conn.close()
        except socket.timeout:
            continue
        except:
            break
    
    s.close()

def udp_server():
    global udp_packets, server_running
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", UDP_PORT))
    print(f"[+] UDP Server listening on port {UDP_PORT}")
    
    while server_running:
        try:
            s.settimeout(1)
            data, addr = s.recvfrom(2048)
            udp_packets += 1
            # Send response back (like game server)
            response = b"ACK"
            s.sendto(response, addr)
        except socket.timeout:
            continue
        except:
            break
    
    s.close()

def stats_display():
    global tcp_connections, udp_packets, http_requests, server_running
    start_time = time.time()
    
    while server_running:
        time.sleep(5)
        elapsed = time.time() - start_time
        print(f"\n{'='*50}")
        print(f"📊 BGMI TEST SERVER STATS (Running: {elapsed:.0f}s)")
        print(f"{'='*50}")
        print(f"🔗 TCP Connections: {tcp_connections}")
        print(f"📦 UDP Packets: {udp_packets}")
        print(f"🌐 HTTP Requests: {http_requests}")
        print(f"⚡ Load: {'🟢 Low' if tcp_connections < 100 else '🟡 Medium' if tcp_connections < 500 else '🔴 High'}")
        print(f"{'='*50}")

def print_help():
    print(f"""
╔══════════════════════════════════════════════════════╗
║            BGMI TEST SERVER v1.0                     ║
╚══════════════════════════════════════════════════════╝

📋 Server Endpoints:
   TCP: 0.0.0.0:{TCP_PORT}
   UDP: 0.0.0.0:{UDP_PORT}
   HTTP: 0.0.0.0:{HTTP_PORT}

📌 Apne bot mein yeh target use karein:
   IP: 127.0.0.1 (ya apna local IP)
   Port: 8080 (TCP), 9000 (UDP), 8081 (HTTP)

▶️ Server start ho raha hai...
   Ctrl+C se server rok sakte hain
""")

if __name__ == "__main__":
    print_help()
    
    # Start servers
    t1 = threading.Thread(target=tcp_server, daemon=True)
    t2 = threading.Thread(target=udp_server, daemon=True)
    t3 = threading.Thread(target=stats_display, daemon=True)
    
    t1.start()
    t2.start()
    t3.start()
    
    # Start HTTP server
    httpd = HTTPServer(("0.0.0.0", HTTP_PORT), BGMIHTTPHandler)
    http_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    http_thread.start()
    
    print(f"\n[✅] Server ready! Bot se attack kar sakte hain.")
    print(f"    Target: 127.0.0.1 (TCP:{TCP_PORT}, UDP:{UDP_PORT}, HTTP:{HTTP_PORT})")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Server stopping...")
        server_running = False
        httpd.shutdown()
        print("[✓] Server stopped.")
        sys.exit(0)

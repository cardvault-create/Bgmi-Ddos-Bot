import time
import threading
from colorama import Fore, Style, init

init(autoreset=True)

class AttackUtils:
    @staticmethod
    def get_banner():
        return f"""
{Fore.CYAN}╔══════════════════════════════════════╗
{Fore.CYAN}║    {Fore.RED}🔥 BGMI STRESS TESTER PRO{Fore.CYAN}      ║
{Fore.CYAN}║    {Fore.YELLOW}Authorized Testing Only{Fore.CYAN}       ║
{Fore.CYAN}║    {Fore.GREEN}Max Duration: 600 seconds{Fore.CYAN}      ║
{Fore.CYAN}╚══════════════════════════════════════╝{Style.RESET_ALL}
"""

    @staticmethod
    def format_time(seconds):
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            m = seconds // 60
            s = seconds % 60
            return f"{m:.0f}m {s:.0f}s"
        else:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            return f"{h:.0f}h {m:.0f}m"

    @staticmethod
    def format_bytes(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

class Statistics:
    def __init__(self):
        self.packets_sent = 0
        self.bytes_sent = 0
        self.connections_made = 0
        self.errors = 0
        self.start_time = None
        self.lock = threading.Lock()
    
    def start(self):
        self.start_time = time.time()
    
    def add_packet(self, size=1024):
        with self.lock:
            self.packets_sent += 1
            self.bytes_sent += size
    
    def add_connection(self):
        with self.lock:
            self.connections_made += 1
    
    def add_error(self):
        with self.lock:
            self.errors += 1
    
    def get_report(self):
        elapsed = time.time() - self.start_time if self.start_time else 0
        with self.lock:
            return {
                'packets': self.packets_sent,
                'bytes': self.bytes_sent,
                'connections': self.connections_made,
                'errors': self.errors,
                'elapsed': elapsed,
                'packet_rate': self.packets_sent / elapsed if elapsed > 0 else 0,
                'mbps': (self.bytes_sent * 8) / (elapsed * 1024 * 1024) if elapsed > 0 else 0,
                'conn_rate': self.connections_made / elapsed if elapsed > 0 else 0
            }

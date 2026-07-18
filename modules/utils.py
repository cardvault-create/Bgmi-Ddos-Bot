# modules/utils.py

class AttackUtils:
    @staticmethod
    def get_banner():
        return """
╔══════════════════════════════════════╗
║     BGMI STRESS TESTER PRO v4.0     ║
║     UDP Flood Attack System         ║
╚══════════════════════════════════════╝
"""
    
    @staticmethod
    def format_time(seconds):
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def format_bytes(bytes_count):
        if bytes_count < 1024:
            return f"{bytes_count} B"
        elif bytes_count < 1024 * 1024:
            return f"{bytes_count / 1024:.2f} KB"
        elif bytes_count < 1024 * 1024 * 1024:
            return f"{bytes_count / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_count / (1024 * 1024 * 1024):.2f} GB"

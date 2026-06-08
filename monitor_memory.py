"""
Memory Monitor - Real-time system and process memory tracking
Shows top 5 processes by memory usage (like Task Manager)
"""

import psutil
import time
import sys
from datetime import datetime

def get_size_str(bytes_value):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def get_top_processes(n=5):
    """Get top N processes by memory usage"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            info = proc.info
            mem_mb = info['memory_info'].rss / (1024 * 1024)
            processes.append({
                'pid': info['pid'],
                'name': info['name'],
                'memory_mb': mem_mb
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by memory usage (descending)
    processes.sort(key=lambda x: x['memory_mb'], reverse=True)
    return processes[:n]

def monitor_memory(interval=2, target_process_name=None):
    """
    Monitor system memory and show top processes
    
    Args:
        interval: Update interval in seconds
        target_process_name: Optional process name to highlight (e.g., 'python.exe')
    """
    print("=" * 80)
    print("MEMORY MONITOR - Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    try:
        while True:
            # Clear screen (Windows)
            print("\033[2J\033[H", end="")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"📊 Memory Monitor - {timestamp}")
            print("=" * 80)
            
            # System memory
            mem = psutil.virtual_memory()
            print(f"\n🖥️  SYSTEM MEMORY:")
            print(f"   Total:     {get_size_str(mem.total)}")
            print(f"   Available: {get_size_str(mem.available)}")
            print(f"   Used:      {get_size_str(mem.used)} ({mem.percent:.1f}%)")
            print(f"   Free:      {get_size_str(mem.free)}")
            
            # Memory bar
            bar_length = 50
            used_bars = int(mem.percent / 100 * bar_length)
            bar = "█" * used_bars + "░" * (bar_length - used_bars)
            print(f"   [{bar}] {mem.percent:.1f}%")
            
            # Top 5 processes
            print(f"\n🔝 TOP 5 PROCESSES BY MEMORY:")
            print(f"   {'PID':<8} {'Memory':<12} {'Process Name':<40}")
            print(f"   {'-'*8} {'-'*12} {'-'*40}")
            
            top_procs = get_top_processes(5)
            for proc in top_procs:
                pid_str = str(proc['pid'])
                mem_str = f"{proc['memory_mb']:.1f} MB"
                name = proc['name']
                
                # Highlight target process
                if target_process_name and target_process_name.lower() in name.lower():
                    print(f"   {pid_str:<8} {mem_str:<12} {name:<40} ⭐")
                else:
                    print(f"   {pid_str:<8} {mem_str:<12} {name:<40}")
            
            # Find target process if specified
            if target_process_name:
                print(f"\n🎯 TARGET PROCESS: {target_process_name}")
                found = False
                for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                    try:
                        if target_process_name.lower() in proc.info['name'].lower():
                            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
                            cpu = proc.info['cpu_percent']
                            print(f"   PID {proc.info['pid']}: {mem_mb:.1f} MB, CPU: {cpu:.1f}%")
                            found = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if not found:
                    print(f"   ⚠️  Process not found")
            
            print(f"\n{'='*80}")
            print(f"Updating every {interval}s... (Press Ctrl+C to stop)")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        sys.exit(0)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor system memory and top processes")
    parser.add_argument(
        "--interval", 
        type=int, 
        default=2,
        help="Update interval in seconds (default: 2)"
    )
    parser.add_argument(
        "--process",
        type=str,
        default=None,
        help="Target process name to highlight (e.g., 'python.exe')"
    )
    
    args = parser.parse_args()
    
    monitor_memory(interval=args.interval, target_process_name=args.process)

# Made with Bob

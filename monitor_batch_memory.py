"""
Monitor RAM memory usage during batch processing.
Run this in a separate terminal while batch_processor.py is running.
"""

import psutil
import time
import sys
from datetime import datetime

def format_bytes(bytes_val):
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"

def monitor_memory(interval=2):
    """Monitor system and Python process memory usage."""
    print("="*80)
    print("GROOVE.AI Batch Processor - Memory Monitor")
    print("="*80)
    print(f"Monitoring interval: {interval}s")
    print(f"Press Ctrl+C to stop")
    print("="*80)
    print()
    
    # Find Python processes
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and 'batch_processor' in ' '.join(cmdline):
                    python_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if not python_processes:
        print("⚠️  No batch_processor.py processes found!")
        print("Start batch_processor.py first, then run this monitor.")
        return
    
    print(f"Found {len(python_processes)} batch processor process(es)")
    print()
    
    # Header
    print(f"{'Time':<12} {'Total RAM':<15} {'Available':<15} {'Used %':<10} {'Process RAM':<15} {'Peak':<15}")
    print("-"*90)
    
    max_process_mem = 0
    
    try:
        while True:
            # System memory
            mem = psutil.virtual_memory()
            total_ram = format_bytes(mem.total)
            available = format_bytes(mem.available)
            used_percent = f"{mem.percent:.1f}%"
            
            # Process memory (sum of all workers)
            total_process_mem = 0
            for proc in python_processes:
                try:
                    proc_mem = proc.memory_info().rss
                    total_process_mem += proc_mem
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            process_ram = format_bytes(total_process_mem)
            
            # Track peak
            if total_process_mem > max_process_mem:
                max_process_mem = total_process_mem
            peak = format_bytes(max_process_mem)
            
            # Current time
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Print status
            print(f"{current_time:<12} {total_ram:<15} {available:<15} {used_percent:<10} {process_ram:<15} {peak:<15}", end='\r')
            sys.stdout.flush()
            
            # Warning if memory is high
            if mem.percent > 90:
                print()
                print(f"⚠️  WARNING: System RAM usage is {mem.percent:.1f}% - Risk of crash!")
                print()
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print()
        print()
        print("="*80)
        print("Monitoring stopped")
        print(f"Peak process memory: {format_bytes(max_process_mem)}")
        print("="*80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor batch processor memory usage')
    parser.add_argument('--interval', type=int, default=2, help='Monitoring interval in seconds (default: 2)')
    
    args = parser.parse_args()
    
    try:
        monitor_memory(interval=args.interval)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Made with Bob

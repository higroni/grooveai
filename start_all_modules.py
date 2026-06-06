"""
Start all modules in separate processes
"""

import subprocess
import sys
import time
from pathlib import Path

# Module configurations
MODULES = [
    {"name": "file-reader", "port": 8101, "path": "modules/file_reader/main.py"},
    {"name": "text-normalizer", "port": 8102, "path": "modules/text_normalizer/main.py"},
    {"name": "latinizer", "port": 8103, "path": "modules/latinizer/main.py"},
    {"name": "legal-parser", "port": 8104, "path": "modules/legal_parser/main.py"},
]

def start_module(module):
    """Start a module in a new process"""
    print(f"Starting {module['name']} on port {module['port']}...")
    
    # Start process
    process = subprocess.Popen(
        [sys.executable, module['path']],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    return process

def main():
    print("=" * 80)
    print("STARTING ALL MODULES")
    print("=" * 80)
    print()
    
    processes = []
    
    for module in MODULES:
        try:
            process = start_module(module)
            processes.append({
                "name": module['name'],
                "port": module['port'],
                "process": process
            })
            time.sleep(2)  # Wait for module to start
        except Exception as e:
            print(f"[ERROR] Failed to start {module['name']}: {e}")
    
    print()
    print("=" * 80)
    print(f"Started {len(processes)} modules")
    print("=" * 80)
    print()
    print("Modules running:")
    for p in processes:
        print(f"  - {p['name']:20s} on port {p['port']}")
    print()
    print("Press Ctrl+C to stop all modules")
    print()
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
            
            # Check if any process died
            for p in processes:
                if p['process'].poll() is not None:
                    print(f"[WARNING] {p['name']} stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n\nStopping all modules...")
        for p in processes:
            p['process'].terminate()
        print("All modules stopped")

if __name__ == "__main__":
    main()

# Made with Bob

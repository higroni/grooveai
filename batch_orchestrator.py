"""
GROOVE.AI Batch Orchestrator
=============================

Lightweight orchestrator that spawns separate Python process for each document.
Each process is completely isolated and releases ALL memory when finished.

NO imports of heavy modules - only subprocess and file operations.
"""

import subprocess
import sys
import os
import signal
from pathlib import Path
from datetime import datetime
import time

# Try to import psutil for better process management
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  psutil not installed - timeout handling may be less reliable")
    print("   Install with: pip install psutil")


def process_batch(input_dir: str, output_dir: str, enable_semantic: bool = True, skip_existing: bool = True):
    """
    Process all documents by spawning separate process for each.
    
    Args:
        input_dir: Directory containing documents
        output_dir: Directory for output JSONs
        enable_semantic: Enable semantic extraction
        skip_existing: Skip files that already have output JSON
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all document files
    doc_files = sorted([
        f for f in input_path.glob("*")
        if f.suffix.lower() in ['.docx', '.pdf', '.txt']
    ])
    
    if not doc_files:
        print(f"❌ No documents found in {input_dir}")
        return
    
    # Filter out files that already have output (if skip_existing is True)
    if skip_existing:
        files_to_process = []
        skipped = 0
        for doc_file in doc_files:
            output_file = output_path / f"{doc_file.stem}_processed.json"
            if output_file.exists():
                skipped += 1
            else:
                files_to_process.append(doc_file)
        doc_files = files_to_process
        
        if skipped > 0:
            print(f"ℹ️  Skipping {skipped} files that already have output")
    
    if not doc_files:
        print(f"✓ All documents already processed!")
        return
    
    total = len(doc_files)
    print(f"\n{'='*80}")
    print(f"BATCH ORCHESTRATOR - SUBPROCESS MODE")
    print(f"{'='*80}")
    print(f"Documents to process: {total}")
    print(f"Semantic extraction: {'ENABLED' if enable_semantic else 'DISABLED'}")
    print(f"Skip existing: {'ENABLED' if skip_existing else 'DISABLED'}")
    print(f"{'='*80}\n")
    
    processed = 0
    failed = 0
    skipped_count = 0
    start_time = time.time()
    
    for idx, doc_file in enumerate(doc_files, 1):
        print(f"[{idx}/{total}] {doc_file.name}")
        
        # Build command
        cmd = [
            sys.executable,  # Current Python interpreter
            "process_single_document.py",
            "--input-file", str(doc_file),
            "--output-dir", str(output_path)
        ]
        
        if not enable_semantic:
            cmd.append("--disable-semantic")
        
        # Run in separate process - COMPLETE ISOLATION
        try:
            if HAS_PSUTIL:
                # Use psutil for better process management
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                try:
                    # Wait with timeout
                    stdout, stderr = process.communicate(timeout=180)
                    
                    # Print output
                    if stdout:
                        print(stdout, end='')
                    
                    if process.returncode == 0:
                        processed += 1
                    else:
                        failed += 1
                        if stderr:
                            print(f"  Error: {stderr}")
                            
                except subprocess.TimeoutExpired:
                    print(f"  ⏱️  TIMEOUT (3 minutes) - force killing process...")
                    
                    # Force kill the process and all its children
                    try:
                        parent = psutil.Process(process.pid)
                        children = parent.children(recursive=True)
                        
                        # Kill children first
                        for child in children:
                            try:
                                child.kill()
                            except:
                                pass
                        
                        # Kill parent
                        parent.kill()
                        
                        # Wait for process to die
                        parent.wait(timeout=5)
                        print(f"  ✓ Process killed successfully")
                        
                    except Exception as e:
                        print(f"  ⚠️  Error killing process: {e}")
                    
                    failed += 1
                    
            else:
                # Fallback to standard subprocess.run
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180  # 3 minute timeout per document
                )
                
                # Print output from subprocess
                if result.stdout:
                    print(result.stdout, end='')
                
                if result.returncode == 0:
                    processed += 1
                else:
                    failed += 1
                    if result.stderr:
                        print(f"  Error: {result.stderr}")
                        
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  TIMEOUT (3 minutes) - skipping to next file")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"Total processed: {processed}/{total}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(processed/total*100):.1f}%")
    print(f"Total time: {elapsed/60:.1f} minutes")
    print(f"Avg time per doc: {elapsed/total:.1f}s")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch Orchestrator - Subprocess Mode")
    parser.add_argument("--input-dir", required=True, help="Input directory")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--disable-semantic", action="store_true", help="Disable semantic extraction")
    
    args = parser.parse_args()
    
    process_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        enable_semantic=not args.disable_semantic
    )

# Made with Bob

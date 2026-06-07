"""
Check GPU availability for CLASSLA acceleration.
"""
import sys

def check_gpu():
    """Check if GPU is available."""
    print("=" * 60)
    print("GPU Availability Check")
    print("=" * 60)
    
    # Check PyTorch CUDA
    try:
        import torch
        print(f"\n[OK] PyTorch installed: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  Device count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  Device {i}: {torch.cuda.get_device_name(i)}")
                print(f"    Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
        else:
            print("  [X] No CUDA devices found")
    except ImportError:
        print("\n[X] PyTorch not installed")
    except Exception as e:
        print(f"\n[X] Error checking PyTorch: {e}")
    
    # Check CLASSLA
    try:
        import classla
        print(f"\n[OK] CLASSLA installed: {classla.__version__}")
    except ImportError:
        print("\n[X] CLASSLA not installed")
    except Exception as e:
        print(f"\n[X] Error checking CLASSLA: {e}")
    
    print("\n" + "=" * 60)
    print("Recommendation:")
    print("=" * 60)
    
    try:
        import torch
        if torch.cuda.is_available():
            print("[OK] GPU acceleration is available!")
            print("  You can enable GPU for CLASSLA NER processing.")
            print("  Expected speedup: 2-5x faster than CPU")
        else:
            print("[X] No GPU detected.")
            print("  CLASSLA will use CPU (current configuration).")
            print("  Consider using a GPU for better performance.")
    except:
        print("[X] Cannot determine GPU status.")
        print("  Install PyTorch with CUDA support for GPU acceleration.")
    
    print("=" * 60)

if __name__ == "__main__":
    check_gpu()

# Made with Bob

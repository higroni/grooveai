"""
Test script for File Reader module
Tests reading the sample PDF file
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.file_reader.service import FileReaderService
from shared.config_loader import config


def test_file_reader():
    """Test the file reader service with sample file"""
    
    print("=" * 80)
    print("FILE READER MODULE TEST")
    print("=" * 80)
    
    # Get sample file from config
    sample_file = config.get_sample_file()
    print(f"\nSample file: {sample_file}")
    
    # Check if file exists
    if not os.path.exists(sample_file):
        print(f"\nERROR: Sample file not found: {sample_file}")
        return False
    
    print(f"File exists: YES")
    print(f"File size: {os.path.getsize(sample_file)} bytes")
    
    # Initialize service
    print("\nInitializing File Reader Service...")
    service = FileReaderService()
    
    # Read file
    print("\nReading file...")
    try:
        result = service.read_file(sample_file, "pdf")
        
        print("\nRESULTS:")
        print("-" * 80)
        print(f"Encoding: {result['encoding']}")
        print(f"Character count: {result['char_count']}")
        print(f"Page count: {result['page_count']}")
        print(f"Processing time: {result['processing_time_ms']} ms")
        
        print("\nFirst 500 characters of extracted text:")
        print("-" * 80)
        print(result['text'][:500])
        print("-" * 80)
        
        print("\nLast 500 characters of extracted text:")
        print("-" * 80)
        print(result['text'][-500:])
        print("-" * 80)
        
        print("\nTEST PASSED")
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_file_reader()
    sys.exit(0 if success else 1)

# Made with Bob

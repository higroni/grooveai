import os
from pathlib import Path

# Get all PDF files
files = sorted([f for f in Path('test_data/documents2').glob('*.pdf')])

if len(files) > 39:
    file_40 = files[39]  # Index 39 = file 40
    print(f"File 40 (index 39): {file_40.name}")
    
    # Check file size
    size_mb = file_40.stat().st_size / (1024 * 1024)
    print(f"Size: {size_mb:.2f} MB")
    
    if size_mb > 2:
        print("⚠️  File exceeds 2MB limit!")
    
    # Try to read it
    try:
        from modules.file_reader.service import read_file
        content = read_file(str(file_40))
        if content and content.get('content'):
            text_len = len(content['content'])
            print(f"Text length: {text_len:,} characters")
            if text_len > 500000:
                print("⚠️  Text exceeds 500K character limit!")
        else:
            print("⚠️  Empty or no content")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        import traceback
        traceback.print_exc()
else:
    print("File 40 not found")

# Made with Bob

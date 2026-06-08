"""
Check document size and complexity to identify problematic files.
"""

import os
from pathlib import Path
import PyPDF2

def check_document(pdf_path):
    """Check PDF document size and page count."""
    file_size = os.path.getsize(pdf_path)
    file_size_mb = file_size / (1024 * 1024)
    
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            page_count = len(pdf_reader.pages)
            
            # Estimate text length from first page
            if page_count > 0:
                first_page_text = pdf_reader.pages[0].extract_text()
                avg_chars_per_page = len(first_page_text)
                estimated_total_chars = avg_chars_per_page * page_count
            else:
                estimated_total_chars = 0
    except Exception as e:
        page_count = 0
        estimated_total_chars = 0
        print(f"Error reading PDF: {e}")
    
    return {
        'file_size_mb': file_size_mb,
        'page_count': page_count,
        'estimated_chars': estimated_total_chars
    }

if __name__ == "__main__":
    # Check the problematic document
    doc_path = "test_data/documents/radni_odnosi_0026_000026.pdf"
    
    if not os.path.exists(doc_path):
        print(f"Document not found: {doc_path}")
        print("\nChecking all documents in test_data/documents...")
        
        docs_dir = Path("test_data/documents")
        if docs_dir.exists():
            pdf_files = sorted(docs_dir.glob("*.pdf"))
            
            print(f"\nFound {len(pdf_files)} PDF files\n")
            print(f"{'Filename':<40} {'Size (MB)':<12} {'Pages':<8} {'Est. Chars':<15}")
            print("=" * 80)
            
            for pdf_file in pdf_files:
                info = check_document(pdf_file)
                print(f"{pdf_file.name:<40} {info['file_size_mb']:>10.2f}  {info['page_count']:>6}  {info['estimated_chars']:>13,}")
                
                # Highlight large documents
                if info['file_size_mb'] > 5 or info['page_count'] > 100:
                    print(f"  ⚠️  LARGE DOCUMENT - May cause memory issues")
    else:
        print(f"Checking: {doc_path}\n")
        info = check_document(doc_path)
        print(f"File size: {info['file_size_mb']:.2f} MB")
        print(f"Page count: {info['page_count']}")
        print(f"Estimated characters: {info['estimated_chars']:,}")
        
        if info['file_size_mb'] > 5:
            print("\n⚠️  WARNING: Large file (>5MB) - may cause memory issues")
        if info['page_count'] > 100:
            print("\n⚠️  WARNING: Many pages (>100) - may cause memory issues")

# Made with Bob

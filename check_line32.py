"""Check line 32 in latinized output"""
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('pipeline_output_latinized.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
print(f"Line 32 (index 31):")
print(f"  Length: {len(lines[31])}")
print(f"  Starts with space: {lines[31].startswith(' ')}")
print(f"  First 10 chars: {lines[31][:10]}")
print(f"  Contains 'član': {'član' in lines[31].lower()}")
print(f"  Starts with 'Član' (after strip): {lines[31].strip().startswith('Član')}")

# Made with Bob

import sys
sys.stdout.reconfigure(encoding='utf-8')

from modules.file_reader.service import read_file

content = read_file('test_data/documents2/radni_odnosi_0040_000040.pdf')
text = content['content']

print(f"File: radni_odnosi_0040_000040.pdf")
print(f"Text length: {len(text):,} characters")
print(f"\nFirst 500 characters:")
print(text[:500])
print(f"\n\nLast 500 characters:")
print(text[-500:])

# Check for problematic patterns
import re
lines = text.split('\n')
print(f"\n\nTotal lines: {len(lines)}")
print(f"Average line length: {len(text) / len(lines):.1f} chars")

# Check for very long lines
long_lines = [i for i, line in enumerate(lines) if len(line) > 1000]
if long_lines:
    print(f"\n⚠️  Found {len(long_lines)} lines longer than 1000 chars")
    print(f"Line numbers: {long_lines[:10]}")

# Made with Bob

"""
Download Stanza models for Serbian language
"""
import stanza

print("Downloading Stanza Serbian models...")
print("This may take a few minutes...")

try:
    stanza.download('sr')
    print("\n✅ Serbian models downloaded successfully!")
    print("Models are ready for use in Module 10 (Knowledge Enrichment)")
except Exception as e:
    print(f"\n❌ Error downloading models: {e}")
    print("You can try downloading manually later with: stanza.download('sr')")

# Made with Bob

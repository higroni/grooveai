"""Quick test for Module 4 Legal Parser with timeout."""

import requests
import sys

def test_module4():
    """Test Module 4 health and basic parsing."""
    
    try:
        # Test 1: Health check
        print("Testing Module 4 health endpoint...")
        response = requests.get("http://localhost:8104/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check OK: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Simple parse test
        print("\nTesting parse endpoint with sample text...")
        test_text = """
1. Predmet
Član 1.
Mišljenja, modeli i literaturaSudska praksa
Prava, obaveze i odgovornosti iz radnog odnosa, odnosno po osnovu rada, uređuju se ovim
zakonom i posebnim zakonom, u skladu sa ratifikovanim međunarodnim konvencijama.

Član 2.
Odredbe ovog zakona primenjuju se na zaposlene koji rade na teritoriji Republike Srbije.
"""
        
        response = requests.post(
            "http://localhost:8104/api/parse",
            json={
                "text": test_text,
                "source_uri": "test://quick_test",
                "filename": "quick_test.txt"
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Parse OK: Job ID {data['job_id']}")
            
            # Check structure
            output = data.get('output', {})
            legal_units = output.get('legal_units', [])
            
            print(f"\n📊 Results:")
            print(f"   Total units: {len(legal_units)}")
            
            if legal_units:
                unit1 = legal_units[0]
                print(f"\n   First unit:")
                print(f"   - Number: {unit1.get('number')}")
                print(f"   - Heading: {unit1.get('heading')}")
                print(f"   - Content: {unit1.get('content_text', '')[:100]}...")
                
                # Check if heading and content are properly extracted
                if unit1.get('heading'):
                    print(f"   ✅ Heading extracted")
                else:
                    print(f"   ⚠️  No heading")
                    
                if unit1.get('content_text'):
                    print(f"   ✅ Content extracted ({len(unit1.get('content_text', ''))} chars)")
                else:
                    print(f"   ⚠️  No content")
            
            return True
        else:
            print(f"❌ Parse failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server not responding")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server not running on port 8104")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_module4()
    sys.exit(0 if success else 1)

# Made with Bob

"""Simple test for Module 4 without emoji characters."""

import requests
import sys
import json

def test_module4():
    """Test Module 4 health and basic parsing."""
    
    try:
        # Test 1: Health check
        print("Testing Module 4 health endpoint...")
        response = requests.get("http://localhost:8104/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] Health check: {response.json()}")
        else:
            print(f"[ERROR] Health check failed: {response.status_code}")
            return False
        
        # Test 2: Simple parse test
        print("\nTesting parse endpoint with sample text...")
        test_text = """
1. Predmet
Clan 1.
Misljenja, modeli i literaturaSudska praksa
Prava, obaveze i odgovornosti iz radnog odnosa, odnosno po osnovu rada, uredjuju se ovim
zakonom i posebnim zakonom, u skladu sa ratifikovanim medjunarodnim konvencijama.

Clan 2.
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
            print(f"[OK] Parse successful: Job ID {data['job_id']}")
            
            # Check structure
            output = data.get('output', {})
            legal_units = output.get('legal_units', [])
            
            print(f"\n[RESULTS]")
            print(f"  Total units: {len(legal_units)}")
            
            if legal_units:
                unit1 = legal_units[0]
                print(f"\n  First unit:")
                print(f"  - Number: {unit1.get('number')}")
                print(f"  - Heading: {unit1.get('heading')}")
                content = unit1.get('content_text', '')
                print(f"  - Content: {content[:100]}..." if len(content) > 100 else f"  - Content: {content}")
                
                # Check if heading and content are properly extracted
                if unit1.get('heading'):
                    print(f"  [OK] Heading extracted")
                else:
                    print(f"  [WARNING] No heading")
                    
                if unit1.get('content_text'):
                    print(f"  [OK] Content extracted ({len(unit1.get('content_text', ''))} chars)")
                else:
                    print(f"  [WARNING] No content")
                    
                # Save full response for inspection
                with open("m4_test_response.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n[OK] Full response saved to m4_test_response.json")
            
            return True
        else:
            print(f"[ERROR] Parse failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout - server not responding")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error - server not running on port 8104")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_module4()
    sys.exit(0 if success else 1)

# Made with Bob

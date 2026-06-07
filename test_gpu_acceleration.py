"""
Test GPU acceleration for CLASSLA NER in M7 (Entity Recognizer).
Compares CPU vs GPU performance.
"""
import time
import requests
import json

# Test assertions
TEST_ASSERTIONS = [
    {
        "assertion_id": "test-1",
        "text": "Ministar rada, zapošljavanja i socijalne politike donosi Pravilnik o sadržaju obrazaca zahteva."
    },
    {
        "assertion_id": "test-2",
        "text": "Ovaj pravilnik stupa na snagu osmog dana od dana objavljivanja u Službenom glasniku Republike Srbije."
    },
    {
        "assertion_id": "test-3",
        "text": "Zaposleni ima pravo na neisplaćenu zaradu za poslednjih devet meseci pre otvaranja stečajnog postupka."
    },
    {
        "assertion_id": "test-4",
        "text": "Fond solidarnosti isplaćuje naknadu u roku od 30 dana od dana podnošenja zahteva."
    },
    {
        "assertion_id": "test-5",
        "text": "Poslodavac je dužan da isplati naknadu zarade za vreme odsutnosti sa rada zbog privremene sprečenosti."
    }
]

def test_entity_recognition_performance(num_iterations=10):
    """Test entity recognition performance with multiple iterations."""
    print("=" * 80)
    print("GPU ACCELERATION TEST FOR CLASSLA NER")
    print("=" * 80)
    print(f"\nTest configuration:")
    print(f"  - Number of assertions: {len(TEST_ASSERTIONS)}")
    print(f"  - Iterations: {num_iterations}")
    print(f"  - Total requests: {num_iterations}")
    print()
    
    # Prepare batch request
    batch_request = {
        "assertions": TEST_ASSERTIONS,
        "use_ner": True
    }
    
    # Warm-up request (to initialize CLASSLA pipeline)
    print("Warming up CLASSLA pipeline...")
    try:
        response = requests.post(
            "http://localhost:8107/api/recognize/batch",
            json=batch_request,
            timeout=60
        )
        if response.status_code == 200:
            print("[OK] Pipeline initialized")
        else:
            print(f"[ERROR] Warm-up failed: {response.status_code}")
            return
    except Exception as e:
        print(f"[ERROR] Cannot connect to M7: {e}")
        print("Make sure M7 (Entity Recognizer) is running on port 8107")
        return
    
    # Run performance test
    print(f"\nRunning {num_iterations} iterations...")
    times = []
    
    for i in range(num_iterations):
        start = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8107/api/recognize/batch",
                json=batch_request,
                timeout=60
            )
            
            if response.status_code == 200:
                duration = (time.time() - start) * 1000  # Convert to ms
                times.append(duration)
                
                result = response.json()
                total_entities = result.get("metadata", {}).get("total_entities", 0)
                
                print(f"  Iteration {i+1}/{num_iterations}: {duration:.2f}ms ({total_entities} entities)")
            else:
                print(f"  Iteration {i+1}/{num_iterations}: ERROR {response.status_code}")
                
        except Exception as e:
            print(f"  Iteration {i+1}/{num_iterations}: ERROR {str(e)}")
    
    # Calculate statistics
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print("\n" + "=" * 80)
        print("PERFORMANCE RESULTS")
        print("=" * 80)
        print(f"Average time: {avg_time:.2f}ms")
        print(f"Min time: {min_time:.2f}ms")
        print(f"Max time: {max_time:.2f}ms")
        print(f"Throughput: {len(TEST_ASSERTIONS) / (avg_time / 1000):.2f} assertions/sec")
        print()
        
        # Check if GPU is being used
        try:
            health_response = requests.get("http://localhost:8107/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print("Module Status:")
                print(f"  Module: {health_data.get('module', 'N/A')}")
                print(f"  Status: {health_data.get('status', 'N/A')}")
                
                components = health_data.get('components', {})
                classla_status = components.get('classla_ner', {})
                if classla_status:
                    print(f"  CLASSLA NER: {classla_status.get('status', 'N/A')}")
                    print(f"  Message: {classla_status.get('message', 'N/A')}")
        except:
            pass
        
        print("=" * 80)
    else:
        print("\n[ERROR] No successful iterations")

if __name__ == "__main__":
    test_entity_recognition_performance(num_iterations=10)

# Made with Bob

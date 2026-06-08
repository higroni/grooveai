"""
Test script for Procedural Extractor module.
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.procedural_extractor import extract_procedural

# Test cases
test_cases = [
    {
        "name": "Postupak za izdavanje dozvole",
        "text": """
Član 1.

Postupak za izdavanje dozvole:

1) Podnosilac podnosi zahtev nadležnom organu u roku od 30 dana.
2) Organ vrši proveru dokumentacije u roku od 15 dana.
3) Nakon provere, organ donosi rešenje u roku od 8 dana.
"""
    },
    {
        "name": "Obaveze poslodavca",
        "text": """
Član 2.

Poslodavac je dužan da:

1) Obaveštava zaposlenog o promenama u roku od 5 dana.
2) Dostavlja izveštaj inspektoru najkasnije 10 dana pre roka.
3) Sastavlja evidenciju o radnom vremenu.
"""
    },
    {
        "name": "Postupak žalbe",
        "text": """
Član 3.

Zaposleni podnosi žalbu direktoru u roku od 15 dana.

Direktor razmatra žalbu i donosi odluku u roku od 30 dana.

Pre nego što donese odluku, direktor saslušava zaposlenog.
"""
    },
    {
        "name": "Inspekcijski nadzor",
        "text": """
Član 4.

Inspektor vrši nadzor nad primenom propisa.

Poslodavac dostavlja traženu dokumentaciju inspektoru.

Nakon izvršenog nadzora, inspektor sastavlja zapisnik.
"""
    },
    {
        "name": "Sekvencijalni postupak",
        "text": """
Član 5.

Prvo, komisija prikuplja potrebne podatke.

Zatim, komisija analizira prikupljene podatke.

Potom, komisija sastavlja izveštaj.

Na kraju, komisija dostavlja izveštaj ministru.
"""
    }
]

def main():
    print("=" * 80)
    print("PROCEDURAL EXTRACTOR TEST")
    print("=" * 80)
    
    results = []
    total_steps = 0
    total_actors = 0
    total_sequences = 0
    total_dependencies = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {test_case['name']}")
        print("-" * 80)
        
        result = extract_procedural(test_case['text'])
        results.append({
            "test_name": test_case['name'],
            "result": result
        })
        
        content = result['content']
        
        # Steps
        if content['steps']:
            print(f"\nSteps ({len(content['steps'])}):")
            for step in content['steps'][:5]:  # Show first 5
                step_info = f"  - "
                if step['step_number']:
                    step_info += f"Step {step['step_number']}: "
                step_info += step['action'][:50]
                if step['actor']:
                    step_info += f" (Actor: {step['actor']})"
                if step['deadline']:
                    step_info += f" [Deadline: {step['deadline']}]"
                print(step_info)
        
        # Actors
        if content['actors']:
            print(f"\nActors ({len(content['actors'])}):")
            for actor in content['actors']:
                print(f"  - {actor['name']}: {len(actor['responsibilities'])} responsibilities")
        
        # Sequences
        if content['sequences']:
            print(f"\nSequences ({len(content['sequences'])}):")
            for seq in content['sequences']:
                print(f"  - {seq['sequence_type']}: {len(seq['steps'])} steps")
        
        # Dependencies
        if content['dependencies']:
            print(f"\nDependencies ({len(content['dependencies'])}):")
            for dep in content['dependencies']:
                print(f"  - {dep['dependency_type']}: {dep['context'][:60]}...")
        
        print(f"\nProcessing Time: {result['processing_time']:.4f}s")
        print(f"Total Elements: {result['total_elements']}")
        
        # Update totals
        total_steps += len(content['steps'])
        total_actors += len(content['actors'])
        total_sequences += len(content['sequences'])
        total_dependencies += len(content['dependencies'])
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_time = sum(r['result']['processing_time'] for r in results)
    total_elements = sum(r['result']['total_elements'] for r in results)
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Total Processing Time: {total_time:.4f}s")
    print(f"Average Time per Test: {total_time/len(results):.4f}s")
    
    print(f"\nTotal Elements Extracted: {total_elements}")
    print(f"  - Steps: {total_steps}")
    print(f"  - Actors: {total_actors}")
    print(f"  - Sequences: {total_sequences}")
    print(f"  - Dependencies: {total_dependencies}")
    
    # Actor breakdown
    print("\nMost Common Actors:")
    actor_counts = {}
    for item in results:
        for actor in item['result']['content']['actors']:
            name = actor['name']
            actor_counts[name] = actor_counts.get(name, 0) + 1
    
    for actor, count in sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {actor}: {count}")
    
    # Steps with deadlines
    steps_with_deadlines = sum(
        1 for item in results 
        for step in item['result']['content']['steps'] 
        if step['deadline']
    )
    print(f"\nSteps with Deadlines: {steps_with_deadlines}/{total_steps}")
    
    # Save results
    output_file = "procedural_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()

# Made with Bob

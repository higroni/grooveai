"""
Test script for Conditional Logic Extractor module.
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.conditional_logic_extractor import extract_conditional_logic

# Test cases
test_cases = [
    {
        "name": "Jednostavni uslovi",
        "text": """
Član 1.

Ako zaposleni ima više od 5 godina staža, tada ima pravo na dodatak.

Ukoliko poslodavac ne ispuni obavezu, mora platiti kaznu.
"""
    },
    {
        "name": "Uslovi sa izuzecima",
        "text": """
Član 2.

Zaposleni može koristiti godišnji odmor, osim ako postoje vanredne okolnosti.

Poslodavac je dužan da isplati naknadu, izuzev u slučaju više sile.

Radnik ima pravo na bonus, sem ako je prekršio radnu disciplinu.
"""
    },
    {
        "name": "Složeni uslovi",
        "text": """
Član 3.

Ako zaposleni ima više od 10 godina staža, tada može zahtevati povećanje plate.

U slučaju da poslodavac ne odgovori u roku, onda zaposleni može podneti žalbu.

Pod uslovom da su ispunjeni svi kriterijumi, zaposleni dobija ugovor na neodređeno.
"""
    },
    {
        "name": "Kada uslovi",
        "text": """
Član 4.

Kada zaposleni dostavi zahtev, poslodavac mora odgovoriti u roku od 15 dana.

Kada istekne rok, zaposleni ima pravo na naknadu.
"""
    },
    {
        "name": "Kombinovani uslovi",
        "text": """
Član 5.

Ako zaposleni ima više od 3 godine staža, a ako je ispunio sve obaveze, tada ima pravo na bonus.

Ukoliko poslodavac ne isplati platu na vreme, mora platiti zateznu kamatu, osim ako postoje opravdani razlozi.
"""
    }
]

def main():
    print("=" * 80)
    print("CONDITIONAL LOGIC EXTRACTOR TEST")
    print("=" * 80)
    
    results = []
    total_conditions = 0
    total_consequences = 0
    total_exceptions = 0
    total_rules = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {test_case['name']}")
        print("-" * 80)
        
        result = extract_conditional_logic(test_case['text'])
        results.append({
            "test_name": test_case['name'],
            "result": result
        })
        
        content = result['content']
        
        # Conditions
        if content['conditions']:
            print(f"\nConditions ({len(content['conditions'])}):")
            for cond in content['conditions'][:5]:  # Show first 5
                print(f"  - [{cond['condition_type']}] {cond['condition_text'][:60]}...")
        
        # Consequences
        if content['consequences']:
            print(f"\nConsequences ({len(content['consequences'])}):")
            for cons in content['consequences'][:5]:  # Show first 5
                print(f"  - [{cons['consequence_type']}] {cons['consequence_text'][:60]}...")
        
        # Exceptions
        if content['exceptions']:
            print(f"\nExceptions ({len(content['exceptions'])}):")
            for exc in content['exceptions']:
                print(f"  - [{exc['exception_type']}] {exc['exception_text'][:60]}...")
        
        # Rules
        if content['rules']:
            print(f"\nRules ({len(content['rules'])}):")
            for rule in content['rules']:
                print(f"  - [{rule['rule_type']}] {len(rule['conditions'])} conditions, {len(rule['consequences'])} consequences")
                print(f"    Text: {rule['rule_text'][:70]}...")
        
        print(f"\nProcessing Time: {result['processing_time']:.4f}s")
        print(f"Total Elements: {result['total_elements']}")
        
        # Update totals
        total_conditions += len(content['conditions'])
        total_consequences += len(content['consequences'])
        total_exceptions += len(content['exceptions'])
        total_rules += len(content['rules'])
    
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
    print(f"  - Conditions: {total_conditions}")
    print(f"  - Consequences: {total_consequences}")
    print(f"  - Exceptions: {total_exceptions}")
    print(f"  - Rules: {total_rules}")
    
    # Condition type breakdown
    print("\nCondition Types:")
    type_counts = {}
    for item in results:
        for cond in item['result']['content']['conditions']:
            cond_type = cond['condition_type']
            type_counts[cond_type] = type_counts.get(cond_type, 0) + 1
    
    for cond_type, count in sorted(type_counts.items()):
        print(f"  - {cond_type}: {count}")
    
    # Consequence type breakdown
    print("\nConsequence Types:")
    cons_counts = {}
    for item in results:
        for cons in item['result']['content']['consequences']:
            cons_type = cons['consequence_type']
            cons_counts[cons_type] = cons_counts.get(cons_type, 0) + 1
    
    for cons_type, count in sorted(cons_counts.items()):
        print(f"  - {cons_type}: {count}")
    
    # Rule type breakdown
    print("\nRule Types:")
    rule_counts = {}
    for item in results:
        for rule in item['result']['content']['rules']:
            rule_type = rule['rule_type']
            rule_counts[rule_type] = rule_counts.get(rule_type, 0) + 1
    
    for rule_type, count in sorted(rule_counts.items()):
        print(f"  - {rule_type}: {count}")
    
    # Save results
    output_file = "conditional_logic_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()

# Made with Bob

"""
Test script for Quantitative Extractor module.
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.quantitative_extractor import extract_quantitative

# Test cases
test_cases = [
    {
        "name": "Godišnji odmor i radno vreme",
        "text": """
Član 1.

Zaposleni ima pravo na najmanje 20 dana godišnjeg odmora.

Maksimalno radno vreme ne može biti duže od 40 sati nedeljno.

Minimalno radno vreme iznosi 20 sati nedeljno.
"""
    },
    {
        "name": "Naknade i procenti",
        "text": """
Član 2.

Naknada za prekovremeni rad iznosi 26% osnovne zarade.

Zaposleni ima pravo na naknadu od 60% prosečne zarade.

Minimalna naknada ne može biti manja od 50% osnovne zarade.
"""
    },
    {
        "name": "Novčane kazne",
        "text": """
Član 3.

Kazna za prekršaj može biti od 50.000 do 100.000 dinara.

Novčana kazna iznosi 200.000 dinara.

Maksimalna kazna ne prelazi 500.000 dinara.
"""
    },
    {
        "name": "Pragovi i granice",
        "text": """
Član 4.

Prag od 10 zaposlenih primenjuje se za mala preduzeća.

Gornja granica 100 zaposlenih određuje srednja preduzeća.

Donja granica 5 zaposlenih je minimum za registraciju.
"""
    },
    {
        "name": "Opsezi i tačne vrednosti",
        "text": """
Član 5.

Staž između 5 i 10 godina daje pravo na dodatak.

Tačno 15 dana godišnjeg odmora za prvu godinu rada.

Od 1 do 3 meseca je probni rad.
"""
    }
]

def main():
    print("=" * 80)
    print("QUANTITATIVE EXTRACTOR TEST")
    print("=" * 80)
    
    results = []
    total_standards = 0
    total_thresholds = 0
    total_percentages = 0
    total_monetary = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {test_case['name']}")
        print("-" * 80)
        
        result = extract_quantitative(test_case['text'])
        results.append({
            "test_name": test_case['name'],
            "result": result
        })
        
        content = result['content']
        
        # Standards
        if content['standards']:
            print(f"\nStandards ({len(content['standards'])}):")
            for std in content['standards']:
                print(f"  - {std['type']}: {std['value']} {std['unit'] or ''}")
                print(f"    Context: {std['context'][:60]}...")
        
        # Thresholds
        if content['thresholds']:
            print(f"\nThresholds ({len(content['thresholds'])}):")
            for thr in content['thresholds']:
                print(f"  - {thr['type']}: {thr['value']} {thr['unit'] or ''}")
                print(f"    Context: {thr['context'][:60]}...")
        
        # Percentages
        if content['percentages']:
            print(f"\nPercentages ({len(content['percentages'])}):")
            for pct in content['percentages']:
                print(f"  - {pct['value']}%")
                print(f"    Context: {pct['context'][:60]}...")
        
        # Monetary amounts
        if content['monetary_amounts']:
            print(f"\nMonetary Amounts ({len(content['monetary_amounts'])}):")
            for amt in content['monetary_amounts']:
                print(f"  - {amt['amount']} {amt['currency']}")
                print(f"    Context: {amt['context'][:60]}...")
        
        print(f"\nProcessing Time: {result['processing_time']:.4f}s")
        print(f"Total Elements: {result['total_elements']}")
        
        # Update totals
        total_standards += len(content['standards'])
        total_thresholds += len(content['thresholds'])
        total_percentages += len(content['percentages'])
        total_monetary += len(content['monetary_amounts'])
    
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
    print(f"  - Standards: {total_standards}")
    print(f"  - Thresholds: {total_thresholds}")
    print(f"  - Percentages: {total_percentages}")
    print(f"  - Monetary Amounts: {total_monetary}")
    
    # Type breakdown
    print("\nStandard Types:")
    type_counts = {}
    for item in results:
        for std in item['result']['content']['standards']:
            std_type = std['type']
            type_counts[std_type] = type_counts.get(std_type, 0) + 1
    
    for std_type, count in sorted(type_counts.items()):
        print(f"  - {std_type}: {count}")
    
    # Save results
    output_file = "quantitative_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()

# Made with Bob

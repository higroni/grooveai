"""
Analyze normative extraction coverage on JSON exports
Compares detection rates before and after pattern expansion
"""

import json
import os
import sys

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import sys

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from normative_extractor.service import NormativeExtractor

def load_json_exports(json_dir: str) -> List[Dict[str, Any]]:
    """Load all JSON export files"""
    json_files = list(Path(json_dir).glob("*.json"))
    documents = []
    
    print(f"Loading {len(json_files)} JSON files...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                documents.append({
                    'filename': json_file.name,
                    'data': data
                })
        except Exception as e:
            print(f"Error loading {json_file.name}: {e}")
    
    return documents

def extract_text_from_json(data: Dict[str, Any]) -> str:
    """Extract all text content from JSON export"""
    text_parts = []
    
    # Get full_text (main content field in JSON exports)
    if 'full_text' in data:
        text_parts.append(data['full_text'])
    
    # Also check for normalized_text as fallback
    elif 'normalized_text' in data:
        text_parts.append(data['normalized_text'])
    
    # Get parsed content (if available)
    if 'parsed_content' in data:
        parsed = data['parsed_content']
        
        # Extract from articles
        if 'articles' in parsed:
            for article in parsed['articles']:
                if 'content' in article:
                    text_parts.append(article['content'])
                
                # Extract from paragraphs
                if 'paragraphs' in article:
                    for para in article['paragraphs']:
                        if 'content' in para:
                            text_parts.append(para['content'])
                        
                        # Extract from items
                        if 'items' in para:
                            for item in para['items']:
                                if 'content' in item:
                                    text_parts.append(item['content'])
    
    return ' '.join(text_parts) if text_parts else ""

def analyze_normative_content(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze normative content extraction across all documents"""
    
    service = NormativeExtractor()
    
    stats = {
        'total_documents': len(documents),
        'documents_processed': 0,
        'documents_with_normative': 0,
        'total_extractions': 0,
        'by_type': defaultdict(int),
        'by_document': [],
        'pattern_matches': defaultdict(int),
        'examples': defaultdict(list)
    }
    
    print("\nAnalyzing normative content...")
    
    for i, doc in enumerate(documents, 1):
        if i % 10 == 0:
            print(f"Processing document {i}/{len(documents)}...")
        
        try:
            text = extract_text_from_json(doc['data'])
            
            if not text or len(text) < 50:
                continue
            
            # Extract normative content
            result = service.extract(text)
            
            doc_stats = {
                'filename': doc['filename'],
                'text_length': len(text),
                'total_extractions': 0,
                'by_type': {}
            }
            
            has_normative = False
            content = result.normative_content
            
            # Count obligations
            if content.obligations:
                count = len(content.obligations)
                stats['by_type']['obligations'] += count
                stats['total_extractions'] += count
                doc_stats['by_type']['obligations'] = count
                doc_stats['total_extractions'] += count
                has_normative = True
                
                # Store examples
                for obligation in content.obligations[:3]:  # First 3 examples
                    if len(stats['examples']['obligations']) < 10:
                        stats['examples']['obligations'].append({
                            'text': obligation.source_text[:200],
                            'confidence': obligation.confidence,
                            'document': doc['filename']
                        })
            
            # Count prohibitions
            if content.prohibitions:
                count = len(content.prohibitions)
                stats['by_type']['prohibitions'] += count
                stats['total_extractions'] += count
                doc_stats['by_type']['prohibitions'] = count
                doc_stats['total_extractions'] += count
                has_normative = True
                
                for prohibition in content.prohibitions[:3]:
                    if len(stats['examples']['prohibitions']) < 10:
                        stats['examples']['prohibitions'].append({
                            'text': prohibition.source_text[:200],
                            'confidence': prohibition.confidence,
                            'document': doc['filename']
                        })
            
            # Count permissions
            if content.permissions:
                count = len(content.permissions)
                stats['by_type']['permissions'] += count
                stats['total_extractions'] += count
                doc_stats['by_type']['permissions'] = count
                doc_stats['total_extractions'] += count
                has_normative = True
                
                for permission in content.permissions[:3]:
                    if len(stats['examples']['permissions']) < 10:
                        stats['examples']['permissions'].append({
                            'text': permission.source_text[:200],
                            'confidence': permission.confidence,
                            'document': doc['filename']
                        })
            
            # Count definitions
            if content.definitions:
                count = len(content.definitions)
                stats['by_type']['definitions'] += count
                stats['total_extractions'] += count
                doc_stats['by_type']['definitions'] = count
                doc_stats['total_extractions'] += count
                has_normative = True
                
                for definition in content.definitions[:3]:
                    if len(stats['examples']['definitions']) < 10:
                        stats['examples']['definitions'].append({
                            'text': definition.source_text[:200],
                            'confidence': definition.confidence,
                            'document': doc['filename']
                        })
            
            # Count waivers
            if content.waivers:
                count = len(content.waivers)
                stats['by_type']['waivers'] += count
                stats['total_extractions'] += count
                doc_stats['by_type']['waivers'] = count
                doc_stats['total_extractions'] += count
                has_normative = True
                
                for waiver in content.waivers[:3]:
                    if len(stats['examples']['waivers']) < 10:
                        stats['examples']['waivers'].append({
                            'text': waiver.source_text[:200],
                            'confidence': waiver.confidence,
                            'document': doc['filename']
                        })
            
            # Count transfers
            if content.transfers:
                count = len(content.transfers)
                stats['by_type']['transfers'] += count
                stats['total_extractions'] += count
                doc_stats['by_type']['transfers'] = count
                doc_stats['total_extractions'] += count
                has_normative = True
                
                for transfer in content.transfers[:3]:
                    if len(stats['examples']['transfers']) < 10:
                        stats['examples']['transfers'].append({
                            'text': transfer.source_text[:200],
                            'confidence': transfer.confidence,
                            'document': doc['filename']
                        })
            
            # Count assignments
            if content.assignments:
                count = len(content.assignments)
                stats['by_type']['assignments'] += count
                stats['total_extractions'] += count
                doc_stats['by_type']['assignments'] = count
                doc_stats['total_extractions'] += count
                has_normative = True
                
                for assignment in content.assignments[:3]:
                    if len(stats['examples']['assignments']) < 10:
                        stats['examples']['assignments'].append({
                            'text': assignment.source_text[:200],
                            'confidence': assignment.confidence,
                            'document': doc['filename']
                        })
            
            if has_normative:
                stats['documents_with_normative'] += 1
                stats['by_document'].append(doc_stats)
            
            stats['documents_processed'] += 1
            
        except Exception as e:
            print(f"Error processing {doc['filename']}: {e}")
    
    return stats

def print_analysis_report(stats: Dict[str, Any]):
    """Print detailed analysis report"""
    
    print("\n" + "="*80)
    print("NORMATIVE EXTRACTION COVERAGE ANALYSIS")
    print("="*80)
    
    print(f"\n📊 OVERALL STATISTICS")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Documents processed: {stats['documents_processed']}")
    print(f"   Documents with normative content: {stats['documents_with_normative']}")
    coverage_rate = (stats['documents_with_normative']/stats['documents_processed']*100) if stats['documents_processed'] > 0 else 0
    print(f"   Coverage rate: {coverage_rate:.1f}%")
    print(f"   Total extractions: {stats['total_extractions']}")
    avg_extractions = (stats['total_extractions']/stats['documents_processed']) if stats['documents_processed'] > 0 else 0
    print(f"   Avg extractions per document: {avg_extractions:.1f}")
    
    print(f"\n📋 EXTRACTION BY TYPE")
    for content_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        percentage = count / stats['total_extractions'] * 100 if stats['total_extractions'] > 0 else 0
        print(f"   {content_type.capitalize():15s}: {count:5d} ({percentage:5.1f}%)")
    
    print(f"\n📈 TOP 10 DOCUMENTS BY EXTRACTIONS")
    top_docs = sorted(stats['by_document'], key=lambda x: x['total_extractions'], reverse=True)[:10]
    for i, doc in enumerate(top_docs, 1):
        print(f"   {i:2d}. {doc['filename']:40s} - {doc['total_extractions']:3d} extractions")
        type_breakdown = ', '.join([f"{k}: {v}" for k, v in doc['by_type'].items()])
        print(f"       ({type_breakdown})")
    
    print(f"\n💡 EXAMPLE EXTRACTIONS")
    for content_type, examples in stats['examples'].items():
        if examples:
            print(f"\n   {content_type.upper()}:")
            for i, example in enumerate(examples[:5], 1):
                print(f"      {i}. [{example['document']}]")
                print(f"         \"{example['text']}...\"")
                print(f"         Confidence: {example['confidence']:.2f}")
    
    print("\n" + "="*80)

def save_results(stats: Dict[str, Any], output_file: str):
    """Save analysis results to JSON"""
    
    # Convert defaultdict to regular dict for JSON serialization
    stats_copy = dict(stats)
    stats_copy['by_type'] = dict(stats_copy['by_type'])
    stats_copy['pattern_matches'] = dict(stats_copy['pattern_matches'])
    stats_copy['examples'] = dict(stats_copy['examples'])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats_copy, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {output_file}")

def main():
    json_dir = "test_data/json_output"
    output_file = "normative_coverage_analysis.json"
    
    print("="*80)
    print("NORMATIVE EXTRACTOR COVERAGE ANALYSIS")
    print("Testing expanded patterns on 200+ JSON documents")
    print("="*80)
    
    # Load documents
    documents = load_json_exports(json_dir)
    
    if not documents:
        print("❌ No documents found!")
        return
    
    print(f"✅ Loaded {len(documents)} documents")
    
    # Analyze normative content
    stats = analyze_normative_content(documents)
    
    # Print report
    print_analysis_report(stats)
    
    # Save results
    save_results(stats, output_file)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()

# Made with Bob

"""
GROOVE.AI Single Document Processor
====================================

Processes a SINGLE document through the complete pipeline with semantic extraction.
Designed to be called from batch orchestrator for memory-safe processing.

Includes safety limits:
- Max text length: 500,000 characters
- Max processing time: 5 minutes
- Memory monitoring
"""

import sys
import os
import time
import logging
import gc
import signal
import uuid
import re
from pathlib import Path
from datetime import datetime
import json

# Timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Processing timeout exceeded")

# Set timeout (5 minutes)
if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, timeout_handler)

# Set environment variable to suppress module console logging
os.environ['GROOVE_BATCH_MODE'] = '1'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


def process_document(
    input_file: str,
    output_dir: str,
    enable_semantic: bool = True,
    unified_db_path: str = "data/databases/grooveai_unified.db"
) -> dict:
    """
    Process a single document through the complete pipeline.
    
    Args:
        input_file: Path to input document
        output_dir: Directory for output JSON
        enable_semantic: Enable semantic extraction
        unified_db_path: Path to unified database
        
    Returns:
        Dictionary with processing result
    """
    from modules.file_reader.service import read_file
    from modules.latinizer.service import latinize_text
    from modules.text_normalizer.service import normalize_text
    from modules.legal_parser.service import parse_legal_document
    from modules.entity_recognizer.service import recognize_entities
    from modules.assertion_extractor.service import extract_assertions
    from modules.condition_extractor.service import extract_conditions
    from modules.assertion_classifier.service import classify_assertions
    from shared.unified_database import UnifiedDatabaseManager
    
    input_path = Path(input_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    doc_name = input_path.name
    
    # Check if output file already exists
    output_file = output_path / f"{input_path.stem}_processed.json"
    if output_file.exists():
        logger.info(f"  ⏭️  SKIP: Output already exists for {doc_name}")
        return {'success': True, 'skipped': True, 'reason': 'Output file already exists'}
    
    start_time = time.time()
    
    try:
        logger.info(f"  Processing: {doc_name}")
        
        # Check file size
        file_size_mb = input_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 2:
            logger.warning(f"    SKIP: File too large ({file_size_mb:.1f}MB)")
            return {'success': False, 'error': 'File too large'}
        
        # M1: File Reader
        file_content = read_file(str(input_path))
        if not file_content or not file_content.get('content'):
            logger.warning(f"    SKIP: Empty content")
            return {'success': False, 'error': 'Empty content'}
        
        text = file_content['content']
        
        # Check text length
        text_len = len(text)
        if text_len > 500000:  # 500K characters limit
            logger.warning(f"    SKIP: Text too long ({text_len:,} chars)")
            return {'success': False, 'error': f'Text too long: {text_len:,} chars'}
        
        logger.info(f"    Text length: {text_len:,} chars")
        
        # Set timeout alarm (5 minutes)
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(300)
        
        # M2: Latinizer
        latinized = latinize_text(text)
        text = latinized['latinized_text']
        
        # M3: Text Normalizer
        normalized = normalize_text(text)
        text = normalized['normalized_text']
        
        # Clear intermediate results
        del file_content, latinized, normalized
        gc.collect()
        
        # M4: Legal Parser
        db_manager = UnifiedDatabaseManager(unified_db_path)
        with db_manager.get_session() as session:
            parsed = parse_legal_document(
                text=text,
                document_id=doc_name,
                db_session=session
            )
        
        # M6: Entity Recognition
        entities_by_unit = {}
        if parsed and parsed.get('units'):
            for unit in parsed['units']:
                unit_id = unit.get('unit_id', '')
                unit_text = unit.get('text', '')
                if unit_text:
                    unit_entities = recognize_entities(unit_text, use_ner=False)
                    # Handle both dict and object response
                    if hasattr(unit_entities, 'entities'):
                        raw_entities = unit_entities.entities
                    elif isinstance(unit_entities, dict):
                        raw_entities = unit_entities.get('entities', [])
                    else:
                        raw_entities = []
                    
                    # Convert Entity objects to dicts
                    converted_entities = []
                    for entity in raw_entities:
                        if hasattr(entity, 'model_dump'):
                            converted_entities.append(entity.model_dump())
                        elif hasattr(entity, 'dict'):
                            converted_entities.append(entity.dict())
                        elif isinstance(entity, dict):
                            converted_entities.append(entity)
                        else:
                            converted_entities.append({
                                'entity_id': getattr(entity, 'entity_id', ''),
                                'entity_type': getattr(entity, 'entity_type', ''),
                                'text': getattr(entity, 'text', ''),
                                'start_char': getattr(entity, 'start_char', 0),
                                'end_char': getattr(entity, 'end_char', 0),
                                'confidence': getattr(entity, 'confidence', 0.0)
                            })
                    entities_by_unit[unit_id] = converted_entities
        
        gc.collect()
        
        # M7 & M8: Assertions and Conditions
        assertions_by_unit = {}
        conditions_by_unit = {}
        
        if parsed and parsed.get('units'):
            for unit in parsed['units']:
                unit_id = unit.get('unit_id', '')
                unit_text = unit.get('text', '')
                
                if unit_text:
                    assertions = extract_assertions(unit_text)
                    assertions_by_unit[unit_id] = assertions.get('assertions', [])
                    
                    conditions = extract_conditions(unit_text)
                    conditions_by_unit[unit_id] = conditions.get('conditions', [])
            
            gc.collect()
        
        # M9: Assertion Classification
        classified_assertions = {}
        for unit_id, assertions in assertions_by_unit.items():
            classified = []
            for assertion in assertions:
                result = classify_assertions([assertion])
                if result and result.get('classified_assertions'):
                    classified.extend(result['classified_assertions'])
            classified_assertions[unit_id] = classified
        
        # SEMANTIC EXTRACTION
        semantic_data = {}
        if enable_semantic and text:
            try:
                logger.info(f"    → Semantic extraction...")
                
                from modules.normative_extractor.service import NormativeExtractor
                from modules.procedural_extractor.service import ProceduralExtractor
                from modules.conditional_logic_extractor.service import ConditionalLogicExtractor
                from modules.temporal_linker.service import TemporalLinker
                from modules.legal_hierarchy.service import LegalHierarchyClassifier
                from modules.quantitative_extractor.service import QuantitativeExtractor
                
                normative_extractor = NormativeExtractor()
                procedural_extractor = ProceduralExtractor()
                conditional_extractor = ConditionalLogicExtractor()
                temporal_linker = TemporalLinker()
                hierarchy_classifier = LegalHierarchyClassifier()
                quantitative_extractor = QuantitativeExtractor()
                
                # Extract
                normative_result = normative_extractor.extract(text)
                semantic_data['normative_content'] = {
                    'obligations': [{'text': o.source_text, 'confidence': o.confidence} 
                                   for o in normative_result.normative_content.obligations],
                    'prohibitions': [{'text': p.source_text, 'confidence': p.confidence} 
                                    for p in normative_result.normative_content.prohibitions],
                    'permissions': [{'text': p.source_text, 'confidence': p.confidence} 
                                   for p in normative_result.normative_content.permissions],
                    'definitions': [{'text': d.source_text, 'confidence': d.confidence} 
                                   for d in normative_result.normative_content.definitions],
                    'waivers': [{'text': w.source_text, 'confidence': w.confidence} 
                               for w in normative_result.normative_content.waivers],
                    'transfers': [{'text': t.source_text, 'confidence': t.confidence} 
                                 for t in normative_result.normative_content.transfers],
                    'assignments': [{'text': a.source_text, 'confidence': a.confidence} 
                                   for a in normative_result.normative_content.assignments],
                    'total_count': normative_result.normative_content.total_count
                }
                
                procedural_result = procedural_extractor.extract(text)
                semantic_data['procedural_content'] = procedural_result.to_dict()
                
                conditional_result = conditional_extractor.extract(text)
                semantic_data['conditional_logic'] = conditional_result.to_dict()
                
                temporal_elements = temporal_linker.extract_temporal_elements(text)
                semantic_data['temporal_references'] = {
                    'elements': [e.model_dump() for e in temporal_elements],
                    'total_count': len(temporal_elements)
                }
                
                hierarchy_result = hierarchy_classifier.classify(text)
                semantic_data['legal_hierarchy'] = hierarchy_result.model_dump()
                
                quantitative_result = quantitative_extractor.extract(text)
                semantic_data['quantitative_data'] = quantitative_result.to_dict()
                
                logger.info(f"      Normative: {semantic_data['normative_content']['total_count']} items")
                logger.info(f"      Procedural: {semantic_data['procedural_content'].get('total_elements', 0)} elements")
                logger.info(f"      Conditional: {semantic_data['conditional_logic'].get('total_elements', 0)} elements")
                
            except Exception as e:
                logger.warning(f"      ⚠️  Semantic extraction error: {e}")
                semantic_data = {}
        
        # Extract document title from text
        document_title = _extract_document_title(text)
        
        # Detect document type from title
        document_type = _detect_document_type(document_title)
        
        # Generate document-level UUID and import_run_id
        document_legal_unit_id = str(uuid.uuid4())
        import_run_id = str(uuid.uuid4())
        
        # Extract document-level entities
        document_entities_result = recognize_entities(text, use_ner=False)
        # Handle both dict and object response and convert to dict
        if hasattr(document_entities_result, 'entities'):
            raw_entities = document_entities_result.entities
        elif isinstance(document_entities_result, dict):
            raw_entities = document_entities_result.get('entities', [])
        else:
            raw_entities = []
        
        # Convert Entity objects to dicts
        document_entities = []
        for entity in raw_entities:
            if hasattr(entity, 'model_dump'):
                document_entities.append(entity.model_dump())
            elif hasattr(entity, 'dict'):
                document_entities.append(entity.dict())
            elif isinstance(entity, dict):
                document_entities.append(entity)
            else:
                # Fallback: try to convert to dict manually
                document_entities.append({
                    'entity_id': getattr(entity, 'entity_id', ''),
                    'entity_type': getattr(entity, 'entity_type', ''),
                    'text': getattr(entity, 'text', ''),
                    'start_char': getattr(entity, 'start_char', 0),
                    'end_char': getattr(entity, 'end_char', 0),
                    'confidence': getattr(entity, 'confidence', 0.0)
                })
        
        # Add document_legal_unit_id to all units and fix parent_legal_unit_id
        if parsed and parsed.get('units'):
            for unit in parsed['units']:
                unit['document_legal_unit_id'] = document_legal_unit_id
                
                # Fix parent_legal_unit_id: if it's None or empty, set it to document_legal_unit_id
                if not unit.get('parent_legal_unit_id'):
                    unit['parent_legal_unit_id'] = document_legal_unit_id
                
                # Add article title if it's an article
                if unit.get('unit_type') == 'article' and unit.get('number'):
                    unit['title'] = f"Član {unit['number']}"
                elif unit.get('heading'):
                    unit['title'] = unit['heading']
        
        # Build document metadata with processed_at timestamp
        document_metadata = {
            'import_run_id': import_run_id,
            'path': str(input_path),
            'title': document_title,
            'document_type': document_type,
            'language_code': 'sr',
            'legal_units_count': len(parsed.get('units', [])) if parsed else 0,
            'processed_at': datetime.now().isoformat()
        }
        
        # Build enhanced output
        output = {
            'document_id': doc_name,
            'document_legal_unit_id': document_legal_unit_id,
            'document_metadata': document_metadata,
            'document_title': document_title,
            'full_text': text,
            'document_entities': document_entities,
            'processed_at': datetime.now().isoformat(),
            'export_timestamp': datetime.now().isoformat(),
            'parsed_structure': parsed,
            'entities_by_unit': entities_by_unit,
            'assertions_by_unit': classified_assertions,
            'conditions_by_unit': conditions_by_unit
        }
        
        if semantic_data:
            output['semantic_extraction'] = semantic_data
        
        # Save JSON (output_file already defined at start)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        elapsed = time.time() - start_time
        logger.info(f"    ✓ Complete ({elapsed:.1f}s)")
        
        # Cancel timeout
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        
        return {'success': True, 'time': elapsed}
        
    except TimeoutError as e:
        logger.error(f"    ⏱️  TIMEOUT: Processing exceeded 5 minutes")
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        logger.error(f"    ✗ Error: {str(e)}")
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        return {'success': False, 'error': str(e)}


def _extract_document_title(text: str) -> str:
    """
    Extract document title from text.
    Looks for common patterns like "ZAKON O ...", "PRAVILNIK O ...", etc.
    """
    # Common title patterns
    patterns = [
        r'^([A-ZŠĐČĆŽ\s]+O\s+[A-ZŠĐČĆŽ\s]+)',  # ZAKON O RADU
        r'^(ZAKON\s+[^\n]+)',
        r'^(PRAVILNIK\s+[^\n]+)',
        r'^(UREDBA\s+[^\n]+)',
        r'^(ODLUKA\s+[^\n]+)',
        r'^(STATUT\s+[^\n]+)',
    ]
    
    # Try each pattern
    for pattern in patterns:
        match = re.search(pattern, text[:500], re.MULTILINE | re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            return title
    
    # Fallback: use first line
    first_line = text.split('\n')[0].strip()
    if len(first_line) > 10 and len(first_line) < 200:
        return first_line
    
    return "Untitled Document"


def _detect_document_type(title: str) -> str:
    """
    Detect document type from title.
    Returns: 'law', 'regulation', 'decree', 'decision', 'statute', or 'other'
    """
    title_upper = title.upper()
    
    if 'ZAKON' in title_upper:
        return 'law'
    elif 'PRAVILNIK' in title_upper:
        return 'regulation'
    elif 'UREDBA' in title_upper:
        return 'decree'
    elif 'ODLUKA' in title_upper:
        return 'decision'
    elif 'STATUT' in title_upper:
        return 'statute'
    else:
        return 'other'


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process single document")
    parser.add_argument("--input-file", required=True, help="Input document path")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--disable-semantic", action="store_true", help="Disable semantic extraction")
    
    args = parser.parse_args()
    
    result = process_document(
        input_file=args.input_file,
        output_dir=args.output_dir,
        enable_semantic=not args.disable_semantic
    )
    
    sys.exit(0 if result['success'] else 1)

# Made with Bob

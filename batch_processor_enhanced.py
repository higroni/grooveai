"""
GROOVE.AI Enhanced Sequential Batch Document Processor
=======================================================

Enhanced batch processor with semantic extraction modules:
- Normative Extractor (obligations, prohibitions, permissions, definitions, waivers, transfers, assignments)
- Procedural Extractor (steps, sequences, actors)
- Conditional Logic Extractor (IF-THEN-UNLESS patterns)
- Temporal Linker (time references)
- Legal Hierarchy Classifier (document types)
- Quantitative Extractor (numbers, thresholds, standards)

This processor integrates all semantic modules into the pipeline and exports
enriched JSON suitable for Qdrant vector store import.
"""

import sys
import os
import time
import logging
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Set environment variable to suppress module console logging
os.environ['GROOVE_BATCH_MODE'] = '1'

# Configure logging with UTF-8 encoding for Windows compatibility
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout,
    encoding='utf-8',
    errors='replace'
)

logger = logging.getLogger(__name__)


class EnhancedBatchProcessor:
    """
    Enhanced sequential batch document processor with semantic extraction.
    
    Processes documents one at a time with:
    - All original modules (M1-M9)
    - New semantic extraction modules
    - Aggressive memory cleanup
    - Automatic process restart
    """
    
    def __init__(
        self,
        restart_interval: int = 20,
        unified_db_path: str = "data/databases/grooveai_unified.db",
        enable_semantic_modules: bool = True
    ):
        """
        Initialize enhanced batch processor.
        
        Args:
            restart_interval: Restart process after this many documents
            unified_db_path: Path to unified database
            enable_semantic_modules: Enable semantic extraction modules
        """
        self.restart_interval = restart_interval
        self.unified_db_path = unified_db_path
        self.enable_semantic_modules = enable_semantic_modules
        
        logger.info(f"Enhanced Batch Processor initialized:")
        logger.info(f"  Restart interval: {self.restart_interval} documents")
        logger.info(f"  Database: {self.unified_db_path}")
        logger.info(f"  Semantic modules: {'ENABLED' if enable_semantic_modules else 'DISABLED'}")
    
    def process_batch(
        self,
        input_dir: str,
        output_dir: str,
        start_index: int = 0,
        max_documents: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process documents sequentially with semantic extraction.
        
        Args:
            input_dir: Directory containing input documents
            output_dir: Directory for output files
            start_index: Start processing from this document index
            max_documents: Maximum number of documents to process
            
        Returns:
            Dictionary with processing statistics
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get all document files
        doc_files = sorted([
            f for f in input_path.glob("*")
            if f.suffix.lower() in ['.docx', '.pdf', '.txt']
        ])
        
        if not doc_files:
            logger.error(f"No documents found in {input_dir}")
            return {'success': False, 'error': 'No documents found'}
        
        # Apply start index and max documents
        if start_index > 0:
            doc_files = doc_files[start_index:]
        if max_documents:
            doc_files = doc_files[:max_documents]
        
        total_docs = len(doc_files)
        logger.info(f"\n{'='*80}")
        logger.info(f"ENHANCED BATCH PROCESSING WITH SEMANTIC EXTRACTION")
        logger.info(f"{'='*80}")
        logger.info(f"Total documents: {total_docs}")
        logger.info(f"Restart interval: {self.restart_interval}")
        logger.info(f"Semantic modules: {'ENABLED' if self.enable_semantic_modules else 'DISABLED'}")
        logger.info(f"{'='*80}\n")
        
        # Process in chunks with restart
        processed = 0
        failed = 0
        chunk_start = 0
        
        while chunk_start < total_docs:
            chunk_end = min(chunk_start + self.restart_interval, total_docs)
            chunk_files = doc_files[chunk_start:chunk_end]
            
            logger.info(f"\n{'='*80}")
            logger.info(f"CHUNK {chunk_start//self.restart_interval + 1}: Documents {chunk_start+1}-{chunk_end}")
            logger.info(f"{'='*80}\n")
            
            # Process this chunk
            chunk_results = self._process_chunk(chunk_files, output_path, chunk_start)
            
            processed += chunk_results['processed']
            failed += chunk_results['failed']
            
            chunk_start = chunk_end
            
            # Force garbage collection between chunks
            gc.collect()
            
            if chunk_start < total_docs:
                logger.info(f"\n⚠️  RESTARTING PROCESS to free memory...")
                logger.info(f"   Processed so far: {processed}/{total_docs}")
                logger.info(f"   Failed: {failed}")
                time.sleep(2)  # Brief pause before restart
        
        # Final summary
        logger.info(f"\n{'='*80}")
        logger.info(f"ENHANCED BATCH PROCESSING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total processed: {processed}/{total_docs}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {(processed/(processed+failed)*100):.1f}%")
        logger.info(f"{'='*80}\n")
        
        return {
            'success': True,
            'total': total_docs,
            'processed': processed,
            'failed': failed
        }
    
    def _process_chunk(
        self,
        doc_files: List[Path],
        output_path: Path,
        start_index: int
    ) -> Dict[str, int]:
        """
        Process a chunk of documents with semantic extraction.
        
        Args:
            doc_files: List of document files to process
            output_path: Output directory
            start_index: Starting index for numbering
            
        Returns:
            Dictionary with processed and failed counts
        """
        # Lazy imports to minimize memory footprint
        from modules.file_reader.service import read_file
        from modules.latinizer.service import latinize_text
        from modules.text_normalizer.service import normalize_text
        from modules.legal_parser.service import parse_legal_document
        from modules.entity_recognizer.service import recognize_entities
        from modules.assertion_extractor.service import extract_assertions
        from modules.condition_extractor.service import extract_conditions
        from modules.assertion_classifier.service import classify_assertions
        from shared.unified_database import UnifiedDatabaseManager
        
        # Import semantic modules if enabled
        if self.enable_semantic_modules:
            from modules.normative_extractor.service import NormativeExtractor
            from modules.procedural_extractor.service import ProceduralExtractor
            from modules.conditional_logic_extractor.service import ConditionalLogicExtractor
            from modules.temporal_linker.service import TemporalLinker
            from modules.legal_hierarchy.service import LegalHierarchyClassifier
            from modules.quantitative_extractor.service import QuantitativeExtractor
            
            # Initialize semantic extractors
            normative_extractor = NormativeExtractor()
            procedural_extractor = ProceduralExtractor()
            conditional_extractor = ConditionalLogicExtractor()
            temporal_linker = TemporalLinker()
            hierarchy_classifier = LegalHierarchyClassifier()
            quantitative_extractor = QuantitativeExtractor()
        
        processed = 0
        failed = 0
        
        for idx, doc_file in enumerate(doc_files, start=start_index+1):
            doc_name = doc_file.name
            start_time = time.time()
            
            try:
                logger.info(f"[{idx}] Processing: {doc_name}")
                
                # Check file size
                file_size_mb = doc_file.stat().st_size / (1024 * 1024)
                if file_size_mb > 2:
                    logger.warning(f"    SKIP: File too large ({file_size_mb:.1f}MB)")
                    failed += 1
                    continue
                
                # M1: File Reader
                file_content = read_file(str(doc_file))
                if not file_content or not file_content.get('content'):
                    logger.warning(f"    SKIP: Empty content")
                    failed += 1
                    continue
                
                text = file_content['content']
                
                # M2: Latinizer
                latinized = latinize_text(text)
                text = latinized['latinized_text']
                
                # M3: Text Normalizer
                normalized = normalize_text(text)
                text = normalized['normalized_text']
                
                # Clear intermediate results
                del file_content, latinized, normalized
                gc.collect()
                
                # M4: Legal Parser (with database)
                db_manager = UnifiedDatabaseManager(self.unified_db_path)
                
                with db_manager.get_session() as session:
                    parsed = parse_legal_document(
                        text=text,
                        document_id=doc_name,
                        db_session=session
                    )
                
                # M6: Entity Recognition (regex only, no NER)
                entities_doc = recognize_entities(text, use_ner=False)
                
                # Entity recognition for each unit
                entities_by_unit = {}
                if parsed and parsed.get('units'):
                    for unit in parsed['units']:
                        unit_id = unit.get('unit_id', '')
                        unit_text = unit.get('text', '')
                        if unit_text:
                            unit_entities = recognize_entities(unit_text, use_ner=False)
                            # Handle both dict and object response
                            if hasattr(unit_entities, 'entities'):
                                entities_by_unit[unit_id] = unit_entities.entities
                            elif isinstance(unit_entities, dict):
                                entities_by_unit[unit_id] = unit_entities.get('entities', [])
                            else:
                                entities_by_unit[unit_id] = []
                
                # Clear entity data
                del entities_doc
                gc.collect()
                
                # M7 & M8: Assertions and Conditions (batch processing)
                assertions_by_unit = {}
                conditions_by_unit = {}
                
                if parsed and parsed.get('units'):
                    # Process in batches of 10 units
                    units = parsed['units']
                    for i in range(0, len(units), 10):
                        batch = units[i:i+10]
                        
                        for unit in batch:
                            unit_id = unit.get('unit_id', '')
                            unit_text = unit.get('text', '')
                            
                            if unit_text:
                                # Extract assertions
                                assertions = extract_assertions(unit_text)
                                assertions_by_unit[unit_id] = assertions.get('assertions', [])
                                
                                # Extract conditions
                                conditions = extract_conditions(unit_text)
                                conditions_by_unit[unit_id] = conditions.get('conditions', [])
                        
                        # Clear batch
                        del batch
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
                
                # SEMANTIC EXTRACTION MODULES (NEW)
                semantic_data = {}
                
                if self.enable_semantic_modules:
                    logger.info(f"    → Extracting semantic features...")
                    
                    # Extract normative content (obligations, prohibitions, permissions, etc.)
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
                    
                    # Extract procedural content (steps, sequences, actors)
                    procedural_result = procedural_extractor.extract(text)
                    semantic_data['procedural_content'] = procedural_result.to_dict()
                    
                    # Extract conditional logic (IF-THEN-UNLESS patterns)
                    conditional_result = conditional_extractor.extract(text)
                    semantic_data['conditional_logic'] = conditional_result.to_dict()
                    
                    # Extract temporal references
                    temporal_elements = temporal_linker.extract_temporal_elements(text)
                    semantic_data['temporal_references'] = {
                        'elements': [e.model_dump() for e in temporal_elements],
                        'total_count': len(temporal_elements)
                    }
                    
                    # Classify legal hierarchy
                    hierarchy_result = hierarchy_classifier.classify(text)
                    semantic_data['legal_hierarchy'] = hierarchy_result.model_dump()
                    
                    # Extract quantitative data
                    quantitative_result = quantitative_extractor.extract(text)
                    semantic_data['quantitative_data'] = quantitative_result.to_dict()
                    
                    logger.info(f"    ✓ Semantic extraction complete")
                    logger.info(f"      - Normative: {semantic_data['normative_content'].get('total_elements', 0)} items")
                    logger.info(f"      - Procedural: {semantic_data['procedural_content'].get('total_elements', 0)} items")
                    logger.info(f"      - Conditional: {semantic_data['conditional_logic'].get('total_elements', 0)} items")
                    logger.info(f"      - Temporal: {semantic_data['temporal_references'].get('total_count', 0)} items")
                    logger.info(f"      - Quantitative: {semantic_data['quantitative_data'].get('total_elements', 0)} items")
                
                # Extract document title
                document_title = self._extract_document_title(text)
                document_type = self._detect_document_type(document_title)
                
                # Generate UUIDs
                import uuid
                document_legal_unit_id = str(uuid.uuid4())
                import_run_id = str(uuid.uuid4())
                
                # Extract document-level entities
                from modules.entity_recognizer.service import recognize_entities
                document_entities_result = recognize_entities(text, use_ner=False)
                if hasattr(document_entities_result, 'entities'):
                    document_entities = document_entities_result.entities
                elif isinstance(document_entities_result, dict):
                    document_entities = document_entities_result.get('entities', [])
                else:
                    document_entities = []
                
                # Add document_legal_unit_id to all units
                if parsed and parsed.get('units'):
                    for unit in parsed['units']:
                        unit['document_legal_unit_id'] = document_legal_unit_id
                        
                        # Add article title if it's an article
                        if unit.get('unit_type') == 'article' and unit.get('number'):
                            unit['title'] = f"Član {unit['number']}"
                        elif unit.get('heading'):
                            unit['title'] = unit['heading']
                
                # Build document metadata
                document_metadata = {
                    'import_run_id': import_run_id,
                    'path': str(doc_file),
                    'title': document_title,
                    'document_type': document_type,
                    'language_code': 'sr',
                    'legal_units_count': len(parsed.get('units', [])) if parsed else 0
                }
                
                # Build final output with semantic data
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
                    'conditions_by_unit': conditions_by_unit,
                    'semantic_extraction': semantic_data if self.enable_semantic_modules else None
                }
                
                # Save to JSON
                output_file = output_path / f"{doc_file.stem}_enhanced.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, ensure_ascii=False, indent=2)
                
                elapsed = time.time() - start_time
                logger.info(f"    ✓ Complete ({elapsed:.1f}s)")
                
                processed += 1
                
                # Aggressive cleanup
                del text, parsed, entities_by_unit, assertions_by_unit
                del conditions_by_unit, classified_assertions, semantic_data, output
                gc.collect()
                
                # GPU cache clear (if available)
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except:
                    pass
                
            except Exception as e:
                logger.error(f"    ✗ Error: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                failed += 1
                gc.collect()
        
    
    def _extract_document_title(self, text: str) -> str:
        """
        Extract document title from text.
        Looks for common patterns like "ZAKON O ...", "PRAVILNIK O ...", etc.
        """
        import re
        
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
    
    def _detect_document_type(self, title: str) -> str:
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
        return {'processed': processed, 'failed': failed}


def main():
    """Main entry point for enhanced batch processing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Batch Document Processor with Semantic Extraction")
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Input directory containing documents"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for processed files"
    )
    parser.add_argument(
        "--restart-interval",
        type=int,
        default=20,
        help="Restart process after N documents (default: 20)"
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start processing from document N (default: 0)"
    )
    parser.add_argument(
        "--max-documents",
        type=int,
        default=None,
        help="Maximum number of documents to process (default: all)"
    )
    parser.add_argument(
        "--disable-semantic",
        action="store_true",
        help="Disable semantic extraction modules"
    )
    
    args = parser.parse_args()
    
    processor = EnhancedBatchProcessor(
        restart_interval=args.restart_interval,
        enable_semantic_modules=not args.disable_semantic
    )
    
    result = processor.process_batch(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        start_index=args.start_index,
        max_documents=args.max_documents
    )
    
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()

# Made with Bob
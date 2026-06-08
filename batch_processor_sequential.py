"""
GROOVE.AI Sequential Batch Document Processor
==============================================

Sequential batch processor that eliminates memory leaks by:
1. Processing documents one at a time (no multiprocessing)
2. Automatic process restart every N documents
3. Aggressive memory cleanup after each document

This approach trades some speed for reliability and memory safety.
"""

import sys
import os
import time
import logging
import gc
import subprocess
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


class SequentialBatchProcessor:
    """
    Sequential batch document processor with automatic process restart.
    
    Processes documents one at a time with aggressive memory cleanup
    and automatic process restart every N documents to prevent memory leaks.
    """
    
    def __init__(
        self,
        restart_interval: int = 20,
        unified_db_path: str = "data/databases/grooveai_unified.db"
    ):
        """
        Initialize sequential batch processor.
        
        Args:
            restart_interval: Restart process after this many documents
            unified_db_path: Path to unified database
        """
        self.restart_interval = restart_interval
        self.unified_db_path = unified_db_path
        
        logger.info(f"Sequential Batch Processor initialized:")
        logger.info(f"  Restart interval: {self.restart_interval} documents")
        logger.info(f"  Database: {self.unified_db_path}")
    
    def process_batch(
        self,
        input_dir: str,
        output_dir: str,
        start_index: int = 0,
        max_documents: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process documents sequentially with automatic restart.
        
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
        logger.info(f"SEQUENTIAL BATCH PROCESSING")
        logger.info(f"{'='*80}")
        logger.info(f"Total documents: {total_docs}")
        logger.info(f"Restart interval: {self.restart_interval}")
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
        logger.info(f"BATCH PROCESSING COMPLETE")
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
        Process a chunk of documents sequentially.
        
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
                            entities_by_unit[unit_id] = unit_entities['entities']
                
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
                
                # Build final output
                output = {
                    'document_id': doc_name,
                    'processed_at': datetime.now().isoformat(),
                    'parsed_structure': parsed,
                    'entities_by_unit': entities_by_unit,
                    'assertions_by_unit': classified_assertions,
                    'conditions_by_unit': conditions_by_unit
                }
                
                # Save to JSON
                output_file = output_path / f"{doc_file.stem}_processed.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, ensure_ascii=False, indent=2)
                
                elapsed = time.time() - start_time
                logger.info(f"    ✓ Complete ({elapsed:.1f}s)")
                
                processed += 1
                
                # Aggressive cleanup
                del text, parsed, entities_by_unit, assertions_by_unit
                del conditions_by_unit, classified_assertions, output
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
                failed += 1
                gc.collect()
        
        return {'processed': processed, 'failed': failed}


def main():
    """Main entry point for sequential batch processing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sequential Batch Document Processor")
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
    
    args = parser.parse_args()
    
    processor = SequentialBatchProcessor(
        restart_interval=args.restart_interval
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

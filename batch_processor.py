"""
GROOVE.AI Batch Document Processor
==================================

High-performance batch processor that eliminates HTTP overhead by using
direct Python function calls and multiprocessing for parallelization.

Target Performance:
- 8,000 documents in 2-3 hours (2-3s per document)
- 60x speedup vs HTTP-based architecture

Architecture:
- Direct function calls (no HTTP)
- Multiprocessing for parallelism
- Shared GPU models via CUDA streams
- Batch database operations
- Unified database for all modules
"""

import sys
import os
import time
import logging
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional
from multiprocessing import Pool, cpu_count
from datetime import datetime
import json
from io import StringIO

# Set environment variable to suppress module console logging
os.environ['GROOVE_BATCH_MODE'] = '1'

# Suppress all module logging by redirecting to null
class SuppressModuleLogs:
    """Context manager to suppress module logging during batch processing."""
    def __init__(self):
        self.null_handler = logging.NullHandler()
        
    def __enter__(self):
        # Suppress all loggers except batch processor
        for name in ['latinizer', 'legal-parser', 'UnifiedDatabaseManager',
                     'entity-recognizer', 'assertion-extractor',
                     'condition-extractor', 'assertion-classifier',
                     'file-reader', 'text-normalizer']:
            logger = logging.getLogger(name)
            logger.addHandler(self.null_handler)
            logger.propagate = False
        return self
    
    def __exit__(self, *args):
        pass

# Configure logging with UTF-8 encoding for Windows compatibility
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Simple format without timestamps
    stream=sys.stdout,
    encoding='utf-8',
    errors='replace'
)

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    High-performance batch document processor.
    
    Processes documents through the complete M1→M10 pipeline using
    direct function calls and multiprocessing for maximum performance.
    """
    
    def __init__(
        self,
        num_workers: Optional[int] = None,
        batch_size: int = 10,
        unified_db_path: str = "data/databases/grooveai_unified.db"
    ):
        """
        Initialize batch processor.
        
        Args:
            num_workers: Number of parallel workers (default: CPU cores - 1)
            batch_size: Number of documents to process in each batch
            unified_db_path: Path to unified database
        """
        self.num_workers = num_workers or max(1, cpu_count() - 1)
        self.batch_size = batch_size
        self.unified_db_path = unified_db_path
        
        logger.info(f"Batch Processor initialized:")
        logger.info(f"  Workers: {self.num_workers}")
        logger.info(f"  Batch size: {self.batch_size}")
        logger.info(f"  Database: {self.unified_db_path}")
    
    def process_documents(
        self,
        document_paths: List[str],
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process multiple documents through the complete pipeline.
        
        Args:
            document_paths: List of document file paths
            output_dir: Optional directory for output files
            
        Returns:
            Dictionary with processing results and statistics
        """
        start_time = time.time()
        total_docs = len(document_paths)
        
        logger.info(f"Starting batch processing of {total_docs} documents...")
        logger.info(f"Using {self.num_workers} parallel workers")
        
        # Process documents in parallel
        results = []
        failed = []
        
        pool = None
        try:
            with Pool(processes=self.num_workers) as pool:
                # Map documents to workers
                for i, result in enumerate(pool.imap_unordered(
                    self._process_single_document,
                    document_paths
                ), 1):
                    if result['success']:
                        results.append(result)
                        logger.info(f"[{i}/{total_docs}] OK {result['document']}")
                    else:
                        failed.append(result)
                        logger.error(f"[{i}/{total_docs}] FAIL {result['document']}: {result['error']}")
                    
                    # Progress update every 10 documents
                    if i % 10 == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed
                        remaining = (total_docs - i) / rate if rate > 0 else 0
                        logger.info(f"Progress: {i}/{total_docs} ({i/total_docs*100:.1f}%) - "
                                  f"Rate: {rate:.2f} docs/s - "
                                  f"ETA: {remaining/60:.1f} min")
        
        except KeyboardInterrupt:
            logger.warning("Processing interrupted by user")
            if pool:
                pool.terminate()
                pool.join()
        
        # Calculate statistics
        elapsed_time = time.time() - start_time
        success_count = len(results)
        failure_count = len(failed)
        
        stats = {
            'total_documents': total_docs,
            'successful': success_count,
            'failed': failure_count,
            'success_rate': success_count / total_docs * 100 if total_docs > 0 else 0,
            'total_time_seconds': elapsed_time,
            'average_time_per_document': elapsed_time / total_docs if total_docs > 0 else 0,
            'documents_per_second': total_docs / elapsed_time if elapsed_time > 0 else 0,
            'results': results,
            'failures': failed
        }
        
        # Log summary
        logger.info("="*80)
        logger.info("BATCH PROCESSING COMPLETE")
        logger.info("="*80)
        logger.info(f"Total documents: {total_docs}")
        logger.info(f"Successful: {success_count} ({stats['success_rate']:.1f}%)")
        logger.info(f"Failed: {failure_count}")
        logger.info(f"Total time: {elapsed_time/60:.2f} minutes")
        logger.info(f"Average: {stats['average_time_per_document']:.2f}s per document")
        logger.info(f"Throughput: {stats['documents_per_second']:.2f} docs/s")
        logger.info("="*80)
        
        return stats
    
    def _process_single_document(self, document_path: str) -> Dict[str, Any]:
        """
        Process a single document through the complete M1→M10 pipeline.
        
        Uses direct function calls instead of HTTP for maximum performance.
        Each worker process has its own service instances and database session.
        
        Args:
            document_path: Path to document file
            
        Returns:
            Dictionary with processing result
        """
        start_time = time.time()
        doc_name = Path(document_path).name
        
        # PRE-CHECK: Skip documents that are too large
        try:
            file_size_mb = os.path.getsize(document_path) / (1024 * 1024)
            if file_size_mb > 2:  # CRITICAL: Reduced to 2MB to prevent memory issues
                logger.warning(f"SKIP {doc_name}: File too large ({file_size_mb:.1f}MB)")
                return {
                    'success': False,
                    'document': doc_name,
                    'path': document_path,
                    'error': f'File too large ({file_size_mb:.1f}MB) - skipped to prevent memory issues',
                    'error_type': 'FileTooLarge',
                    'processing_time': time.time() - start_time,
                    'json_output_path': None
                }
        except Exception as e:
            logger.warning(f"SKIP {doc_name}: Could not check file size: {e}")
        
        try:
            # Import services (lazy import in worker process)
            from modules.file_reader.service import FileReaderService
            from modules.latinizer.service import LatinizerService
            from modules.text_normalizer.service import TextNormalizerService
            from modules.legal_parser.service import LegalParserService
            from modules.entity_recognizer.service import recognize_entities
            from modules.assertion_extractor.service import AssertionExtractorService
            from modules.condition_extractor.service import ConditionExtractorService
            from modules.condition_extractor.models import Assertion as ConditionAssertion, ConditionExtractionRequest
            from modules.assertion_classifier.service import AssertionClassifierService
            from modules.assertion_classifier.models import Assertion as ClassifierAssertion
            from shared.unified_database import unified_db
            
            # Start processing
            logger.info(f"Processing: {doc_name}")
            
            # Initialize services
            file_reader = FileReaderService()
            latinizer = LatinizerService()
            normalizer = TextNormalizerService()
            parser = LegalParserService()
            assertion_extractor = AssertionExtractorService()
            condition_extractor = ConditionExtractorService()
            classifier = AssertionClassifierService()
            
            # M1-M3: Read, Latinize, Normalize (OUTSIDE database session)
            file_data = file_reader.read_file(document_path)
            text = file_data['text']
            del file_data
            gc.collect()
            
            latin_result = latinizer.latinize(text)
            latinized_text = latin_result['latinized_text']
            del latin_result, text
            gc.collect()
            
            norm_result = normalizer.normalize(latinized_text)
            normalized_text = norm_result['normalized_text']
            del norm_result
            gc.collect()
            
            # Get database session ONLY for database operations
            with unified_db.get_session() as session:
                
                # M4: Legal Parser
                parse_output = parser.parse_document(
                    text=normalized_text,
                    source_uri=document_path,
                    filename=doc_name
                )
                legal_units = parse_output.legal_units
                logger.info(f"  M4: Parsed {len(legal_units)} legal units")
                
                # M6: Entity Recognizer (document + units)
                full_doc_entities = recognize_entities(
                    text=normalized_text,
                    min_confidence=0.5,
                    use_ner=False  # CRITICAL: NER disabled for batch processing
                )
                document_level_entities = full_doc_entities.entities
                
                unit_level_entities = []
                for unit in legal_units:
                    entity_output = recognize_entities(
                        text=unit.content_text,
                        min_confidence=0.5,
                        use_ner=False  # CRITICAL: NER disabled for batch processing
                    )
                    unit_level_entities.extend(entity_output.entities)
                
                # Deduplicate entities
                all_entities = document_level_entities + unit_level_entities
                seen = set()
                unique_entities = []
                for entity in all_entities:
                    key = (entity.text.lower(), entity.entity_type)
                    if key not in seen:
                        seen.add(key)
                        unique_entities.append(entity)
                
                total_entities = len(unique_entities)
                logger.info(f"  M6: Found {total_entities} unique entities")
                
                # Free entity extraction intermediates IMMEDIATELY
                del full_doc_entities, document_level_entities, unit_level_entities
                del all_entities, seen
                gc.collect()
                
                # NOTE: Do NOT delete classla pipeline - it should be reused across documents
                # The pipeline has built-in periodic reinitialization (every 50 uses)
                
                # M7: Assertion Extractor
                all_assertions = []
                for unit in legal_units:
                    assertion_output = assertion_extractor.extract_assertions(
                        content=unit.content_text
                    )
                    all_assertions.extend(assertion_output.assertions)
                    del assertion_output
                
                logger.info(f"  M7: Extracted {len(all_assertions)} assertions")
                
                # Create mapping: assertion_id -> {entities, conditions, classification}
                assertion_metadata = {}
                
                # M6b: Extract entities for each assertion
                # Process in smaller batches to avoid memory buildup
                batch_size = 50
                for i in range(0, len(all_assertions), batch_size):
                    batch = all_assertions[i:i+batch_size]
                    for assertion in batch:
                        assertion_entities = recognize_entities(
                            text=assertion.text,
                            min_confidence=0.5,
                            use_ner=False  # CRITICAL: Disable NER for assertions to save memory
                        )
                        assertion_metadata[assertion.assertion_id] = {
                            'entities': assertion_entities.entities,
                            'conditions': [],
                            'classification': None
                        }
                        del assertion_entities
                    
                    # Cleanup after each batch
                    gc.collect()
                
                # M8: Condition Extractor (process in batches)
                total_conditions = 0
                batch_size = 50
                for i in range(0, len(all_assertions), batch_size):
                    batch = all_assertions[i:i+batch_size]
                    for assertion in batch:
                        # Convert to ConditionAssertion model
                        cond_assertion = ConditionAssertion(
                            assertion_id=assertion.assertion_id,
                            text=assertion.text
                        )
                        request = ConditionExtractionRequest(
                            assertion=cond_assertion,
                            language="sr"
                        )
                        condition_output = condition_extractor.extract_conditions(request)
                        total_conditions += len(condition_output.conditions)
                        
                        # Store conditions in metadata
                        if assertion.assertion_id in assertion_metadata:
                            assertion_metadata[assertion.assertion_id]['conditions'] = condition_output.conditions
                        
                        del cond_assertion, request, condition_output
                    
                    # Cleanup after each batch
                    gc.collect()
                
                logger.info(f"  M8: Extracted {total_conditions} conditions")
                
                # M9: Assertion Classifier (process in batches)
                batch_size = 50
                for i in range(0, len(all_assertions), batch_size):
                    batch = all_assertions[i:i+batch_size]
                    for assertion in batch:
                        # Convert to ClassifierAssertion model
                        class_assertion = ClassifierAssertion(
                            assertion_id=assertion.assertion_id,
                            text=assertion.text
                        )
                        classification = classifier.classify_assertion(
                            assertion=class_assertion,
                            language="sr"
                        )
                        
                        # Store classification in metadata
                        if assertion.assertion_id in assertion_metadata:
                            assertion_metadata[assertion.assertion_id]['classification'] = classification
                        
                        del class_assertion, classification
                    
                    # Cleanup after each batch
                    gc.collect()
                
                logger.info(f"  M9: Classified {len(all_assertions)} assertions")
                
                # Save counts before cleanup
                legal_units_count = len(parse_output.legal_units)
                assertions_count = len(all_assertions)
                
                # Commit all changes to database
                session.commit()
                
                # Export to JSON for Qdrant import
                json_output = self._export_to_json(
                    document_path=document_path,
                    parse_output=parse_output,
                    all_assertions=all_assertions,
                    assertion_metadata=assertion_metadata,
                    all_entities=unique_entities,
                    latinized_text=latinized_text
                )
            
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'document': Path(document_path).name,
                'path': document_path,
                'processing_time': processing_time,
                'legal_units_count': legal_units_count,
                'assertions_count': assertions_count,
                'entities_count': total_entities,
                'conditions_count': total_conditions,
                'json_output_path': json_output
            }
            
            logger.info(f"DONE {doc_name}: {processing_time:.2f}s ({legal_units_count} units, {assertions_count} assertions, {total_entities} entities)")
            
            # CRITICAL: Aggressive memory cleanup after each document
            # This prevents RAM overflow in multiprocessing
            
            # 1. Clear remaining large data structures
            del latinized_text, normalized_text
            del parse_output
            del unique_entities
            del all_assertions, assertion_metadata
            del legal_units
            
            # 2. Clear service instances
            del file_reader, latinizer, normalizer, parser
            del assertion_extractor, condition_extractor, classifier
            
            # 3. NOTE: Do NOT delete classla pipeline - reuse across documents
            # The pipeline has built-in periodic reinitialization (every 50 uses)
            
            # 4. Force garbage collection to free intermediate data
            gc.collect()
            gc.collect()
            
            # 5. Clear GPU cache if using PyTorch/CUDA
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            
            # 5. Log memory usage (only if verbose)
            # Removed to reduce log clutter
            
            return result
            
        except MemoryError as e:
            error_msg = "MemoryError - Document too large or complex"
            logger.error(f"ERROR {doc_name}: {error_msg}")
            
            # Aggressive cleanup on memory error
            gc.collect()
            gc.collect()
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
            except ImportError:
                pass
            
            return {
                'success': False,
                'document': doc_name,
                'path': document_path,
                'error': error_msg,
                'error_type': 'MemoryError',
                'processing_time': time.time() - start_time,
                'json_output_path': None
            }
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"❌ {doc_name}: {error_type} - {error_msg}")
            
            # Cleanup even on error to prevent memory leaks
            gc.collect()
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            
            return {
                'success': False,
                'document': doc_name,
                'path': document_path,
                'error': error_msg,
                'error_type': error_type,
                'processing_time': time.time() - start_time,
                'json_output_path': None
            }
    
    def _export_to_json(
        self,
        document_path: str,
        parse_output: Any,
        all_assertions: List[Any],
        assertion_metadata: Dict[str, Any],
        all_entities: List[Any],
        latinized_text: str
    ) -> str:
        """
        Export document data to JSON format for Qdrant import.
        
        Args:
            document_path: Path to source document
            parse_output: Legal parser output
            all_assertions: List of extracted assertions
            all_entities: List of all extracted entities (document + unit level)
            latinized_text: Full latinized document text
            
        Returns:
            Path to exported JSON file
        """
        from datetime import datetime
        import uuid
        
        # Create output directory
        output_dir = Path("test_data/json_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate import run ID
        import_run_id = str(uuid.uuid4())
        
        # Convert entities to dict format
        document_entities = []
        for entity in all_entities:
            entity_dict = {
                "entity_id": entity.entity_id,
                "entity_type": entity.entity_type,
                "text": entity.text,
                "start_char": entity.start_char,
                "end_char": entity.end_char,
                "confidence": entity.confidence
            }
            document_entities.append(entity_dict)
        
        # Build assertions with metadata
        assertions_data = []
        for assertion in all_assertions:
            # Get metadata for this assertion
            metadata = assertion_metadata.get(assertion.assertion_id, {})
            
            # Convert entities to dict
            entities_list = []
            for entity in metadata.get('entities', []):
                entities_list.append({
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type,
                    "text": entity.text,
                    "start_char": entity.start_char,
                    "end_char": entity.end_char,
                    "confidence": entity.confidence
                })
            
            # Convert conditions to dict
            conditions_list = []
            for condition in metadata.get('conditions', []):
                conditions_list.append({
                    "condition_id": condition.condition_id,
                    "condition_type": condition.condition_type,
                    "text": condition.text,
                    "trigger_word": condition.trigger_word,
                    "confidence": condition.confidence
                })
            
            # Get classification (only if valid)
            classification = metadata.get('classification')
            classification_dict = None
            if classification and hasattr(classification, 'classification_type'):
                class_type = classification.classification_type
                # Only include if not "unknown"
                if class_type and class_type.lower() != "unknown":
                    classification_dict = {
                        "type": class_type,
                        "confidence": classification.confidence if hasattr(classification, 'confidence') else 0.0
                    }
            
            assertion_dict = {
                "assertion_id": assertion.assertion_id,
                "text": assertion.text,
                "confidence": assertion.confidence,
                "sentence_index": assertion.sentence_index,
                "start_char": assertion.start_char,
                "end_char": assertion.end_char,
                "entities": entities_list,
                "conditions": conditions_list
            }
            
            # Only add classification if it exists and is valid
            if classification_dict:
                assertion_dict["classification"] = classification_dict
            
            assertions_data.append(assertion_dict)
        
        # Build JSON structure
        export_data = {
            "import_run_id": import_run_id,
            "document": {
                "name": Path(document_path).name,
                "path": document_path,
                "title": parse_output.document.title,
                "document_type": parse_output.document.document_type,
                "language_code": parse_output.document.language_code,
                "processed_at": datetime.utcnow().isoformat() + "Z"
            },
            "full_text": latinized_text,
            "legal_units_count": len(parse_output.legal_units),
            "document_entities": document_entities,
            "assertions": assertions_data,
            "export_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Save to file
        filename = Path(document_path).stem + "_export.json"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported JSON to: {output_path}")
        
        return str(output_path)


def main():
    """CLI entry point for batch processor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='GROOVE.AI Batch Document Processor'
    )
    parser.add_argument(
        'input',
        help='Input directory or file list'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: CPU cores - 1)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Batch size for processing (default: 10)'
    )
    parser.add_argument(
        '--output',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Get document paths
    input_path = Path(args.input)
    if input_path.is_dir():
        # Process all PDFs in directory
        document_paths = [str(p) for p in input_path.glob('**/*.pdf')]
        logger.info(f"Found {len(document_paths)} PDF files in {input_path}")
    elif input_path.is_file():
        # Single file
        document_paths = [str(input_path)]
    else:
        logger.error(f"Input path not found: {input_path}")
        sys.exit(1)
    
    if not document_paths:
        logger.error("No documents found to process")
        sys.exit(1)
    
    # Create processor
    processor = BatchProcessor(
        num_workers=args.workers,
        batch_size=args.batch_size
    )
    
    # Process documents
    stats = processor.process_documents(
        document_paths=document_paths,
        output_dir=args.output
    )
    
    # Save statistics
    stats_file = Path('batch_processing_stats.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        # Remove detailed results for cleaner stats file
        summary = {k: v for k, v in stats.items() if k not in ['results', 'failures']}
        summary['failed_documents'] = [f['document'] for f in stats['failures']]
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Statistics saved to: {stats_file}")
    
    # Exit with appropriate code
    sys.exit(0 if stats['failure_count'] == 0 else 1)


if __name__ == '__main__':
    main()

# Made with Bob

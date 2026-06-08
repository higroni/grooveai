"""
Test script for Qdrant Loader Module

Tests loading legal documents from JSON exports into Qdrant vector database.
"""

import sys
import logging
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.qdrant_loader import QdrantLoaderService, LoaderConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_single_document():
    """Test loading a single document"""
    logger.info("=" * 80)
    logger.info("TEST 1: Loading Single Document")
    logger.info("=" * 80)
    
    # Configure loader
    config = LoaderConfig(
        qdrant_url="http://localhost:6333",
        recreate_collections=True,  # Fresh start
        batch_size=50
    )
    
    # Initialize service
    logger.info("Initializing Qdrant Loader Service...")
    loader = QdrantLoaderService(config)
    
    # Setup collections
    logger.info("Setting up collections...")
    loader.setup_collections()
    
    # Load single document
    json_path = Path("test_data/json_output/radni_odnosi_0001_000001_export.json")
    
    if not json_path.exists():
        logger.error(f"Test file not found: {json_path}")
        return False
    
    logger.info(f"Loading document: {json_path}")
    loader.load_document_from_json(json_path)
    
    # Check results
    logger.info("\nLoader Statistics:")
    logger.info(f"  Documents processed: {loader.stats.documents_processed}")
    logger.info(f"  Legal units loaded: {loader.stats.legal_units_loaded}")
    logger.info(f"  Normative content loaded: {loader.stats.normative_content_loaded}")
    logger.info(f"  Metadata loaded: {loader.stats.metadata_loaded}")
    logger.info(f"  Errors: {len(loader.stats.errors)}")
    
    if loader.stats.errors:
        logger.error("Errors encountered:")
        for error in loader.stats.errors:
            logger.error(f"  - {error}")
    
    # Check collection info
    logger.info("\nCollection Information:")
    info = loader.get_all_collections_info()
    for collection_name, collection_info in info.items():
        logger.info(f"\n{collection_name}:")
        logger.info(f"  Points: {collection_info['points_count']}")
        logger.info(f"  Vectors: {collection_info['vectors_count']}")
        logger.info(f"  Indexed: {collection_info['indexed_vectors_count']}")
        logger.info(f"  Status: {collection_info['status']}")
    
    return loader.stats.documents_processed > 0


def test_batch_load_small():
    """Test loading a small batch of documents"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Loading Small Batch (5 documents)")
    logger.info("=" * 80)
    
    # Configure loader
    config = LoaderConfig(
        qdrant_url="http://localhost:6333",
        recreate_collections=True,  # Fresh start
        batch_size=100
    )
    
    # Initialize service
    logger.info("Initializing Qdrant Loader Service...")
    loader = QdrantLoaderService(config)
    
    # Setup collections
    logger.info("Setting up collections...")
    loader.setup_collections()
    
    # Create temp directory with subset of files
    json_dir = Path("test_data/json_output")
    
    if not json_dir.exists():
        logger.error(f"Test directory not found: {json_dir}")
        return False
    
    # Get first 5 files
    json_files = sorted(list(json_dir.glob("*.json")))[:5]
    
    if not json_files:
        logger.error("No JSON files found")
        return False
    
    logger.info(f"Found {len(json_files)} files to load")
    
    # Load each file
    for json_file in json_files:
        logger.info(f"Loading: {json_file.name}")
        loader.load_document_from_json(json_file)
    
    # Check results
    logger.info("\nLoader Statistics:")
    logger.info(f"  Documents processed: {loader.stats.documents_processed}")
    logger.info(f"  Legal units loaded: {loader.stats.legal_units_loaded}")
    logger.info(f"  Normative content loaded: {loader.stats.normative_content_loaded}")
    logger.info(f"  Metadata loaded: {loader.stats.metadata_loaded}")
    logger.info(f"  Errors: {len(loader.stats.errors)}")
    
    if loader.stats.errors:
        logger.error("Errors encountered:")
        for error in loader.stats.errors:
            logger.error(f"  - {error}")
    
    # Check collection info
    logger.info("\nCollection Information:")
    info = loader.get_all_collections_info()
    for collection_name, collection_info in info.items():
        logger.info(f"\n{collection_name}:")
        logger.info(f"  Points: {collection_info['points_count']}")
        logger.info(f"  Vectors: {collection_info['vectors_count']}")
        logger.info(f"  Indexed: {collection_info['indexed_vectors_count']}")
        logger.info(f"  Status: {collection_info['status']}")
    
    return loader.stats.documents_processed == 5


def test_batch_load_all():
    """Test loading all documents using batch method"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Loading All Documents (Batch Method)")
    logger.info("=" * 80)
    
    # Configure loader
    config = LoaderConfig(
        qdrant_url="http://localhost:6333",
        recreate_collections=True,  # Fresh start
        batch_size=100
    )
    
    # Initialize service
    logger.info("Initializing Qdrant Loader Service...")
    loader = QdrantLoaderService(config)
    
    # Setup collections
    logger.info("Setting up collections...")
    loader.setup_collections()
    
    # Load all documents
    json_dir = Path("test_data/json_output")
    
    if not json_dir.exists():
        logger.error(f"Test directory not found: {json_dir}")
        return False
    
    logger.info(f"Loading all documents from: {json_dir}")
    stats = loader.load_batch(json_dir)
    
    # Check results
    logger.info("\nLoader Statistics:")
    logger.info(f"  Documents processed: {stats.documents_processed}")
    logger.info(f"  Legal units loaded: {stats.legal_units_loaded}")
    logger.info(f"  Normative content loaded: {stats.normative_content_loaded}")
    logger.info(f"  Metadata loaded: {stats.metadata_loaded}")
    logger.info(f"  Duration: {stats.duration_seconds:.2f}s")
    logger.info(f"  Errors: {len(stats.errors)}")
    
    if stats.errors:
        logger.error("Errors encountered:")
        for error in stats.errors:
            logger.error(f"  - {error}")
    
    # Check collection info
    logger.info("\nCollection Information:")
    info = loader.get_all_collections_info()
    for collection_name, collection_info in info.items():
        logger.info(f"\n{collection_name}:")
        logger.info(f"  Points: {collection_info['points_count']}")
        logger.info(f"  Vectors: {collection_info['vectors_count']}")
        logger.info(f"  Indexed: {collection_info['indexed_vectors_count']}")
        logger.info(f"  Status: {collection_info['status']}")
    
    # Calculate averages
    if stats.documents_processed > 0:
        logger.info("\nAverages per Document:")
        logger.info(f"  Legal units: {stats.legal_units_loaded / stats.documents_processed:.1f}")
        logger.info(f"  Normative content: {stats.normative_content_loaded / stats.documents_processed:.1f}")
        logger.info(f"  Processing time: {stats.duration_seconds / stats.documents_processed:.2f}s")
    
    return stats.documents_processed > 0


def main():
    """Run all tests"""
    logger.info("Starting Qdrant Loader Tests")
    logger.info("=" * 80)
    
    # Check if Qdrant is running
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:6333")
        client.get_collections()
        logger.info("✓ Qdrant server is running")
    except Exception as e:
        logger.error(f"✗ Cannot connect to Qdrant server: {e}")
        logger.error("Please start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
        return
    
    # Run tests
    tests = [
        ("Single Document", test_single_document),
        ("Small Batch (5 docs)", test_batch_load_small),
        ("All Documents", test_batch_load_all)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\nRunning: {test_name}")
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            logger.error(f"Test failed with exception: {e}", exc_info=True)
            results[test_name] = "ERROR"
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    for test_name, result in results.items():
        status_symbol = "✓" if result == "PASS" else "✗"
        logger.info(f"{status_symbol} {test_name}: {result}")
    
    # Overall result
    all_passed = all(r == "PASS" for r in results.values())
    logger.info("\n" + "=" * 80)
    if all_passed:
        logger.info("✓ ALL TESTS PASSED")
    else:
        logger.info("✗ SOME TESTS FAILED")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

# Made with Bob

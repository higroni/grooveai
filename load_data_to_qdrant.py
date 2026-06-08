"""
Load Legal Documents into Qdrant

This script loads all processed legal documents from JSON exports into Qdrant
vector database for semantic search and conflict detection.
"""

import sys
import logging
from pathlib import Path
import argparse

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.qdrant_loader import QdrantLoaderService, LoaderConfig

# Setup logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Load legal documents into Qdrant vector database'
    )
    parser.add_argument(
        '--json-dir',
        type=str,
        default='test_data/json_output',
        help='Directory containing JSON export files (default: test_data/json_output)'
    )
    parser.add_argument(
        '--qdrant-url',
        type=str,
        default='http://localhost:6333',
        help='Qdrant server URL (default: http://localhost:6333)'
    )
    parser.add_argument(
        '--recreate',
        action='store_true',
        help='Recreate collections (deletes existing data)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for uploads (default: 100)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of documents to load (for testing)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("GROOVE.AI - Load Data to Qdrant")
    logger.info("=" * 80)
    
    # Check if JSON directory exists
    json_dir = Path(args.json_dir)
    if not json_dir.exists():
        logger.error(f"JSON directory not found: {json_dir}")
        return 1
    
    # Count JSON files
    json_files = list(json_dir.glob("*.json"))
    if not json_files:
        logger.error(f"No JSON files found in: {json_dir}")
        return 1
    
    logger.info(f"Found {len(json_files)} JSON files")
    
    if args.limit:
        json_files = json_files[:args.limit]
        logger.info(f"Limited to {len(json_files)} files")
    
    # Configure loader
    config = LoaderConfig(
        qdrant_url=args.qdrant_url,
        recreate_collections=args.recreate,
        batch_size=args.batch_size
    )
    
    logger.info(f"\nConfiguration:")
    logger.info(f"  Qdrant URL: {config.qdrant_url}")
    logger.info(f"  Recreate collections: {config.recreate_collections}")
    logger.info(f"  Batch size: {config.batch_size}")
    logger.info(f"  Embedding model: {config.embedding_model}")
    logger.info(f"  Vector size: {config.vector_size}")
    
    # Check Qdrant connection
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=args.qdrant_url)
        client.get_collections()
        logger.info(f"\nConnected to Qdrant at {args.qdrant_url}")
    except Exception as e:
        logger.error(f"\nCannot connect to Qdrant: {e}")
        logger.error("Please start Qdrant with: docker-compose -f docker-compose.qdrant.yml up -d")
        return 1
    
    # Initialize service
    logger.info("\nInitializing Qdrant Loader Service...")
    try:
        loader = QdrantLoaderService(config)
    except Exception as e:
        logger.error(f"Failed to initialize loader: {e}")
        return 1
    
    # Setup collections
    logger.info("\nSetting up collections...")
    try:
        loader.setup_collections()
    except Exception as e:
        logger.error(f"Failed to setup collections: {e}")
        return 1
    
    # Load documents
    logger.info("\n" + "=" * 80)
    logger.info("Loading Documents")
    logger.info("=" * 80)
    
    try:
        stats = loader.load_batch(json_dir)
    except Exception as e:
        logger.error(f"Failed to load documents: {e}", exc_info=True)
        return 1
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("LOADING COMPLETE")
    logger.info("=" * 80)
    
    logger.info(f"\nStatistics:")
    logger.info(f"  Documents processed: {stats.documents_processed}")
    logger.info(f"  Legal units loaded: {stats.legal_units_loaded}")
    logger.info(f"  Normative content loaded: {stats.normative_content_loaded}")
    logger.info(f"  Metadata loaded: {stats.metadata_loaded}")
    logger.info(f"  Duration: {stats.duration_seconds:.2f}s")
    logger.info(f"  Errors: {len(stats.errors)}")
    
    if stats.errors:
        logger.warning("\nErrors encountered:")
        for error in stats.errors[:10]:  # Show first 10 errors
            logger.warning(f"  - {error}")
        if len(stats.errors) > 10:
            logger.warning(f"  ... and {len(stats.errors) - 10} more errors")
    
    # Calculate averages
    if stats.documents_processed > 0:
        logger.info(f"\nAverages per Document:")
        logger.info(f"  Legal units: {stats.legal_units_loaded / stats.documents_processed:.1f}")
        logger.info(f"  Normative content: {stats.normative_content_loaded / stats.documents_processed:.1f}")
        logger.info(f"  Processing time: {stats.duration_seconds / stats.documents_processed:.2f}s")
    
    # Get collection info
    logger.info("\n" + "=" * 80)
    logger.info("Collection Information")
    logger.info("=" * 80)
    
    info = loader.get_all_collections_info()
    for collection_name, collection_info in info.items():
        logger.info(f"\n{collection_name}:")
        logger.info(f"  Points: {collection_info['points_count']:,}")
        logger.info(f"  Vectors: {collection_info['vectors_count']:,}")
        logger.info(f"  Indexed: {collection_info['indexed_vectors_count']:,}")
        logger.info(f"  Status: {collection_info['status']}")
    
    logger.info("\n" + "=" * 80)
    logger.info("SUCCESS - Data loaded into Qdrant")
    logger.info("=" * 80)
    logger.info(f"\nQdrant Dashboard: {args.qdrant_url}/dashboard")
    logger.info("Next step: Run conflict detection tests")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob

"""
Test script for Proposal Processor Module

Tests processing legal proposals through the full pipeline.
"""

import sys
import logging
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.proposal_processor import ProposalProcessorService, ProposalInput

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_process_from_text():
    """Test processing from direct text input"""
    logger.info("=" * 80)
    logger.info("TEST 1: Process from Text")
    logger.info("=" * 80)
    
    # Sample proposal text
    proposal_text = """
    PREDLOG ZAKONA O IZMENI ZAKONA O RADU
    
    Član 1.
    U Zakonu o radu ("Službeni glasnik RS", br. 24/2005, 61/2005, 54/2009, 32/2013, 
    75/2014, 13/2017 - odluka US, 113/2017 i 95/2018 - autentično tumačenje), 
    u članu 24. stav 1. menja se i glasi:
    
    "Poslodavac je dužan da zaposlenom isplati zaradu za obavljeni rad i vreme provedeno 
    na radu, u skladu sa zakonom, opštim aktom i ugovorom o radu."
    
    Član 2.
    U članu 25. dodaje se stav 3. koji glasi:
    
    "Minimalna zarada ne može biti niža od 60% prosečne zarade u Republici Srbiji."
    
    Član 3.
    Ovaj zakon stupa na snagu osmog dana od dana objavljivanja u "Službenom glasniku 
    Republike Srbije".
    """
    
    # Create input
    proposal_input = ProposalInput(
        source_type="text",
        source=proposal_text,
        title="Predlog zakona o izmeni Zakona o radu",
        author="Ministarstvo za rad, zapošljavanje, boračka i socijalna pitanja",
        submission_date="2024-01-15",
        document_type="predlog_zakona"
    )
    
    # Initialize processor
    processor = ProposalProcessorService()
    
    # Process
    logger.info("Processing proposal...")
    result = processor.process_proposal(proposal_input)
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("RESULTS")
    logger.info("=" * 80)
    
    logger.info(f"\nSuccess: {result.success}")
    
    if result.success:
        logger.info(f"\nMetadata:")
        logger.info(f"  Proposal ID: {result.metadata.proposal_id}")
        logger.info(f"  Title: {result.metadata.title}")
        logger.info(f"  Author: {result.metadata.author}")
        logger.info(f"  Submission Date: {result.metadata.submission_date}")
        logger.info(f"  Processing Time: {result.metadata.processing_time_seconds:.2f}s")
        
        logger.info(f"\nStatistics:")
        logger.info(f"  Total Characters: {result.metadata.total_chars:,}")
        logger.info(f"  Total Words: {result.metadata.total_words:,}")
        logger.info(f"  Total Units: {result.metadata.total_units}")
        logger.info(f"  Total Normative: {result.metadata.total_normative}")
        
        logger.info(f"\nLegal Units:")
        for i, unit in enumerate(result.legal_units[:5], 1):
            logger.info(f"\n  Unit {i}:")
            logger.info(f"    ID: {unit['legal_unit_id']}")
            logger.info(f"    Type: {unit['unit_type']}")
            logger.info(f"    Title: {unit.get('title', 'N/A')}")
            logger.info(f"    Content: {unit['content'][:100]}...")
            logger.info(f"    Normative: {len(unit.get('normative_assertions', []))}")
        
        if len(result.legal_units) > 5:
            logger.info(f"\n  ... and {len(result.legal_units) - 5} more units")
    
    if result.errors:
        logger.error(f"\nErrors:")
        for error in result.errors:
            logger.error(f"  - {error}")
    
    if result.warnings:
        logger.warning(f"\nWarnings:")
        for warning in result.warnings:
            logger.warning(f"  - {warning}")
    
    return result.success


def test_process_from_file():
    """Test processing from file"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Process from File")
    logger.info("=" * 80)
    
    # Use existing test file
    file_path = Path("DOCUMENTS/DEV/radni_odnosi_0001_000001.pdf")
    
    if not file_path.exists():
        logger.warning(f"Test file not found: {file_path}")
        logger.warning("Skipping file test")
        return True
    
    # Create input
    proposal_input = ProposalInput(
        source_type="file",
        source=str(file_path),
        title="Zakon o radu (test)",
        document_type="predlog_zakona"
    )
    
    # Initialize processor
    processor = ProposalProcessorService()
    
    # Process
    logger.info(f"Processing file: {file_path}")
    result = processor.process_proposal(proposal_input)
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("RESULTS")
    logger.info("=" * 80)
    
    logger.info(f"\nSuccess: {result.success}")
    
    if result.success:
        logger.info(f"\nMetadata:")
        logger.info(f"  Proposal ID: {result.metadata.proposal_id}")
        logger.info(f"  Title: {result.metadata.title}")
        logger.info(f"  Processing Time: {result.metadata.processing_time_seconds:.2f}s")
        
        logger.info(f"\nStatistics:")
        logger.info(f"  Total Characters: {result.metadata.total_chars:,}")
        logger.info(f"  Total Words: {result.metadata.total_words:,}")
        logger.info(f"  Total Units: {result.metadata.total_units}")
        logger.info(f"  Total Normative: {result.metadata.total_normative}")
    
    if result.errors:
        logger.error(f"\nErrors:")
        for error in result.errors:
            logger.error(f"  - {error}")
    
    return result.success


def test_export_format():
    """Test export to JSON format"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Export to JSON Format")
    logger.info("=" * 80)
    
    # Sample proposal text
    proposal_text = """
    PREDLOG ZAKONA O DIGITALNOJ IMOVINI
    
    Član 1.
    Ovim zakonom uređuje se pravni režim digitalne imovine.
    
    Član 2.
    Digitalna imovina je imovina koja postoji u digitalnom obliku.
    """
    
    # Create input
    proposal_input = ProposalInput(
        source_type="text",
        source=proposal_text,
        title="Predlog zakona o digitalnoj imovini"
    )
    
    # Initialize processor
    processor = ProposalProcessorService()
    
    # Process
    logger.info("Processing proposal...")
    result = processor.process_proposal(proposal_input)
    
    if not result.success:
        logger.error("Processing failed")
        return False
    
    # Export to JSON format
    logger.info("Exporting to JSON format...")
    json_data = result.to_json_export_format()
    
    # Display structure
    logger.info("\nJSON Structure:")
    logger.info(f"  document_metadata: {len(json_data['document_metadata'])} fields")
    logger.info(f"  legal_units: {len(json_data['legal_units'])} units")
    logger.info(f"  is_proposal: {json_data['document_metadata'].get('is_proposal')}")
    
    # Save to file
    import json
    output_path = Path("test_output/proposal_export.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\nExported to: {output_path}")
    logger.info(f"File size: {output_path.stat().st_size:,} bytes")
    
    return True


def main():
    """Run all tests"""
    logger.info("Starting Proposal Processor Tests")
    logger.info("=" * 80)
    
    # Check if services are running
    import requests
    services = [
        ("File Reader", "http://localhost:8001/health"),
        ("Text Normalizer", "http://localhost:8002/health"),
        ("Legal Parser", "http://localhost:8003/health"),
        ("Normative Extractor", "http://localhost:8006/health"),
        ("Condition Extractor", "http://localhost:8008/health"),
        ("Assertion Extractor", "http://localhost:8010/health")
    ]
    
    logger.info("\nChecking services...")
    all_running = True
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                logger.info(f"  ✓ {service_name}")
            else:
                logger.warning(f"  ✗ {service_name} (status: {response.status_code})")
                all_running = False
        except Exception as e:
            logger.warning(f"  ✗ {service_name} (not running)")
            all_running = False
    
    if not all_running:
        logger.warning("\nNot all services are running!")
        logger.warning("Start services with: start_all_modules.py")
        logger.warning("Continuing with available services...")
    
    # Run tests
    tests = [
        ("Process from Text", test_process_from_text),
        ("Process from File", test_process_from_file),
        ("Export to JSON", test_export_format)
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

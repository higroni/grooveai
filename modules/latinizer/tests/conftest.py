"""
Pytest configuration and fixtures for Latinizer tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_database():
    """Provide a test database for the session."""
    # Tests will use the regular database
    # In production, you might want to use a separate test database
    yield


@pytest.fixture
def sample_cyrillic_text():
    """Provide sample Cyrillic text for testing."""
    return "Закон о раду регулише права и обавезе запослених."


@pytest.fixture
def sample_latin_text():
    """Provide sample Latin text for testing."""
    return "Zakon o radu"


@pytest.fixture
def sample_mixed_text():
    """Provide sample mixed Cyrillic/Latin text for testing."""
    return "Члан 1: General provisions"

# Made with Bob

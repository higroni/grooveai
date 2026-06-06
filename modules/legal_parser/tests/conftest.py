"""Pytest fixtures for Legal Parser tests."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.legal_parser.service import LegalParserService
from modules.legal_parser.database import LegalParserDatabaseManager


@pytest.fixture
def service():
    """Create Legal Parser service instance."""
    return LegalParserService()


@pytest.fixture
def test_db():
    """Create test database instance."""
    db = LegalParserDatabaseManager(db_path=":memory:")
    yield db
    # Cleanup handled by in-memory database


@pytest.fixture
def db(test_db):
    """Alias for test_db fixture."""
    return test_db


@pytest.fixture
def sample_text():
    """Sample Serbian legal text for testing."""
    return """Član 1.
Predmet zakona

(1) Ovim zakonom uredjuje se zasnivanje radnog odnosa, prava, obaveze i odgovornosti iz radnog odnosa.
(2) Ovaj zakon primenjuje se na:
1) zaposlene kod poslodavca;
2) poslodavce;
3) lica koja samostalno obavljaju delatnost.

Član 2.
Pojmovi

(1) Pojedini pojmovi upotrebljeni u ovom zakonu imaju sledece znacenje:
1) zaposleni je fizicko lice koje je zasnovalo radni odnos kod poslodavca;
2) poslodavac je pravno lice, preduzetnik ili fizicko lice kod koga je zaposleni zasnovao radni odnos."""


@pytest.fixture
def sample_article_text():
    """Simple article text for testing."""
    return """Član 1.
Predmet zakona

(1) Ovim zakonom uredjuje se predmet."""


@pytest.fixture
def sample_paragraph_text():
    """Text with paragraphs for testing."""
    return """Član 1.

(1) Prvi stav.
(2) Drugi stav."""


@pytest.fixture
def sample_point_text():
    """Text with points for testing."""
    return """Član 1.

(1) Ovaj zakon primenjuje se na:
1) zaposlene;
2) poslodavce."""

# Made with Bob

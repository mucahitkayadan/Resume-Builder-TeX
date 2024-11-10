import pytest
from core.database.factory import get_unit_of_work
from core.database.models.tex_header import TexHeader
from loaders.tex_loader import TexLoader
from datetime import datetime

@pytest.fixture
def uow():
    return get_unit_of_work()

@pytest.fixture
def tex_loader(uow):
    return TexLoader(uow)

def test_get_all_headers(uow):
    with uow:
        headers = uow.tex_headers.get_all()
        assert isinstance(headers, list)
        for header in headers:
            assert isinstance(header, TexHeader)
            assert header.name
            assert header.content

def test_add_and_delete_header(uow):
    with uow:
        # Create test header
        test_header = TexHeader(
            id=None,  # Explicitly set id as None for new headers
            name="test_template",
            content="\\section{Test Content}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add header
        added_header = uow.tex_headers.add(test_header)
        assert added_header.id is not None
        
        # Verify it exists
        assert uow.tex_headers.exists(added_header.id)
        
        # Delete header
        assert uow.tex_headers.delete(added_header.id)
        
        # Verify it's gone
        assert not uow.tex_headers.exists(added_header.id)
        
        uow.commit()

def test_update_header(uow):
    with uow:
        # Create test header
        test_header = TexHeader(
            id=None,  # Explicitly set id as None for new headers
            name="test_update",
            content="\\section{Original Content}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add and update
        added_header = uow.tex_headers.add(test_header)
        added_header.content = "\\section{Updated Content}"
        assert uow.tex_headers.update(added_header)
        
        # Verify update
        updated = uow.tex_headers.get_by_id(added_header.id)
        assert updated.content == "\\section{Updated Content}"
        
        # Cleanup
        uow.tex_headers.delete(added_header.id)
        uow.commit()

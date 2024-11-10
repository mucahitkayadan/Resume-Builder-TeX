import pytest
from datetime import datetime
from core.database.factory import get_unit_of_work
from core.database.models.preamble import Preamble
from core.database.models.resume import Resume

@pytest.fixture
def uow():
    return get_unit_of_work()

def test_preamble_operations(uow):
    with uow:
        # Create test preamble
        test_preamble = Preamble(
            id=None,
            name="resume_preamble",
            content="\\documentclass{article}",
            template_type="resume",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add preamble
        added_preamble = uow.preambles.add(test_preamble)
        assert added_preamble.id is not None
        
        # Get by name
        retrieved_preamble = uow.preambles.get_by_name("resume_preamble")
        assert retrieved_preamble is not None
        assert retrieved_preamble.content == "\\documentclass{article}"
        
        # Update preamble
        retrieved_preamble.content = "\\documentclass{moderncv}"
        assert uow.preambles.update(retrieved_preamble)
        
        # Verify update
        updated = uow.preambles.get_by_id(retrieved_preamble.id)
        assert updated.content == "\\documentclass{moderncv}"
        
        # Cleanup
        assert uow.preambles.delete(retrieved_preamble.id)
        uow.commit()

def test_resume_operations(uow):
    with uow:
        # Create test resume
        test_resume = Resume(
            id=None,
            user_id="test_user_123",
            company_name="Test Corp",
            job_title="Software Engineer",
            job_description="Python development",
            personal_information={"name": "John Doe", "email": "john@example.com"},
            career_summary="Experienced developer",
            skills=[{"Programming": ["Python", "JavaScript"]}],
            work_experience=[],
            education=[],
            projects=[],
            awards=[],
            publications=[],
            model_type="gpt-4",
            model_name="gpt-4",
            temperature=0.7,
            pdf_content=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add resume
        added_resume = uow.resumes.add(test_resume)
        assert added_resume.id is not None
        
        # Get by ID
        retrieved_resume = uow.resumes.get_by_id(added_resume.id)
        assert retrieved_resume is not None
        assert retrieved_resume.company_name == "Test Corp"
        
        # Get by user ID
        user_resumes = uow.resumes.get_by_user_id("test_user_123")
        assert len(user_resumes) > 0
        assert user_resumes[0].user_id == "test_user_123"
        
        # Get latest resume
        latest_resume = uow.resumes.get_latest_resume()
        assert latest_resume is not None
        assert latest_resume.id == added_resume.id
        
        # Update resume
        retrieved_resume.job_title = "Senior Software Engineer"
        assert uow.resumes.update(retrieved_resume)
        
        # Verify update
        updated = uow.resumes.get_by_id(retrieved_resume.id)
        assert updated.job_title == "Senior Software Engineer"
        
        # Cleanup
        assert uow.resumes.delete(retrieved_resume.id)
        uow.commit() 
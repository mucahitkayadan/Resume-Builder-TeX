import pytest
from datetime import datetime

from src.core.database.models.user import User
from src.core.database.models.portfolio import Portfolio
from src.core.database.models.resume import Resume

@pytest.fixture
def mongo_connection():
    """Create a mock MongoDB connection"""
    import mongomock
    from src.core.database.connections.mongo_connection import MongoConnection
    
    connection = MongoConnection()
    connection._client = mongomock.MongoClient()
    connection._db = connection.client["test_db"]
    connection._is_mock = True
    return connection

@pytest.fixture
def mongo_uow(mongo_connection):
    """Create MongoDB Unit of Work"""
    from src.core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork
    return MongoUnitOfWork(mongo_connection)

def test_portfolio_repository_crud(mongo_uow):
    """Test CRUD operations for portfolio repository"""
    with mongo_uow:
        # Create
        portfolio = Portfolio(
            id=None,
            user_id="user123",
            personal_information={"name": "Test User"},
            career_summary="Test summary",
            skills=[{"Programming": ["Python", "JavaScript"]}],
            work_experience=[],
            education=[],
            projects=[],
            awards=[],
            publications=[],
            certifications=[],
            languages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        created_portfolio = mongo_uow.portfolio.add(portfolio)
        assert created_portfolio.id is not None
        
        # Read
        retrieved_portfolio = mongo_uow.portfolio.get_by_id(created_portfolio.id)
        assert retrieved_portfolio is not None
        assert retrieved_portfolio.personal_information["name"] == "Test User"
        
        # Update
        retrieved_portfolio.career_summary = "Updated summary"
        success = mongo_uow.portfolio.update(retrieved_portfolio)
        assert success
        updated_portfolio = mongo_uow.portfolio.get_by_id(created_portfolio.id)
        assert updated_portfolio.career_summary == "Updated summary"
        
        # Delete
        success = mongo_uow.portfolio.delete(created_portfolio.id)
        assert success
        assert mongo_uow.portfolio.get_by_id(created_portfolio.id) is None

def test_user_repository_crud(mongo_uow):
    """Test CRUD operations for user repository"""
    with mongo_uow:
        # Create
        user = User(
            id=None,
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
            preferences={"theme": "dark"},
            last_login=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        created_user = mongo_uow.users.add(user)
        assert created_user.id is not None
        
        # Read
        retrieved_user = mongo_uow.users.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        
        # Update
        retrieved_user.preferences["theme"] = "light"
        success = mongo_uow.users.update(retrieved_user)
        assert success
        updated_user = mongo_uow.users.get_by_id(created_user.id)
        assert updated_user.preferences["theme"] == "light"
        
        # Delete
        success = mongo_uow.users.delete(created_user.id)
        assert success
        assert mongo_uow.users.get_by_id(created_user.id) is None

def test_resume_repository_crud(mongo_uow):
    """Test CRUD operations for resume repository"""
    with mongo_uow:
        # Create
        resume = Resume(
            id=None,
            user_id="user123",
            company_name="Test Company",
            job_title="Software Engineer",
            job_description="Test description",
            personal_information={"name": "Test User"},
            career_summary="Test summary",
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
        created_resume = mongo_uow.resumes.add(resume)
        assert created_resume.id is not None
        
        # Read
        retrieved_resume = mongo_uow.resumes.get_by_id(created_resume.id)
        assert retrieved_resume is not None
        assert retrieved_resume.company_name == "Test Company"
        
        # Update
        retrieved_resume.job_title = "Senior Software Engineer"
        success = mongo_uow.resumes.update(retrieved_resume)
        assert success
        updated_resume = mongo_uow.resumes.get_by_id(created_resume.id)
        assert updated_resume.job_title == "Senior Software Engineer"
        
        # Delete
        success = mongo_uow.resumes.delete(created_resume.id)
        assert success
        assert mongo_uow.resumes.get_by_id(created_resume.id) is None 
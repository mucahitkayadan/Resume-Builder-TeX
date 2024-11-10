import pytest
from datetime import datetime
from core.database.models.user import User
from core.exceptions.database_exceptions import DatabaseError


def test_mongo_uow_transaction_commit(mongo_uow):
    """Test successful transaction commit in MongoDB"""
    with mongo_uow:
        user = User(
            id=None,
            email="test@example.com",
            hashed_password="password",
            full_name="Test User",
            preferences={},
            last_login=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mongo_uow.users.add(user)

    # Verify commit was successful
    with mongo_uow:
        retrieved_user = mongo_uow.users.get_by_email("test@example.com")
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"


def test_mongo_uow_transaction_rollback(mongo_uow):
    """Test transaction rollback on error in MongoDB"""
    try:
        with mongo_uow:
            user = User(
                id=None,
                email="test@example.com",
                hashed_password="password",
                full_name="Test User",
                preferences={},
                last_login=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mongo_uow.users.add(user)
            raise ValueError("Test error")
    except ValueError:
        pass

    # Verify rollback was successful
    with mongo_uow:
        retrieved_user = mongo_uow.users.get_by_email("test@example.com")
        assert retrieved_user is None

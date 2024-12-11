import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch
from src.api.main import app
from src.api.schemas.application import ApplicationStatus, JobApplicationCreate

client = TestClient(app)

@pytest.fixture
def mock_auth_middleware():
    with patch("src.api.middleware.auth.auth0_middleware") as mock:
        mock.return_value = {"sub": "test_user_id"}
        yield mock

@pytest.fixture
def mock_application_service():
    with patch("src.api.services.application_service.ApplicationService") as mock:
        yield mock

def test_create_application(mock_auth_middleware, mock_application_service):
    # Arrange
    test_application = {
        "company_name": "Test Company",
        "job_title": "Software Engineer",
        "job_description": "Test description",
        "job_url": "https://example.com/job",
        "status": ApplicationStatus.DRAFT,
        "application_date": datetime.utcnow().isoformat()
    }
    
    mock_service = Mock()
    mock_service.create_application.return_value = {
        **test_application,
        "id": "test_id",
        "user_id": "test_user_id",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    mock_application_service.return_value = mock_service

    # Act
    response = client.post("/api/v1/applications/", json=test_application)

    # Assert
    assert response.status_code == 200
    assert response.json()["company_name"] == test_application["company_name"]
    assert response.json()["job_title"] == test_application["job_title"]
    mock_service.create_application.assert_called_once()

def test_list_applications(mock_auth_middleware, mock_application_service):
    # Arrange
    mock_applications = [
        {
            "id": "1",
            "company_name": "Company 1",
            "job_title": "Position 1",
            "status": ApplicationStatus.APPLIED,
            "user_id": "test_user_id",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "2",
            "company_name": "Company 2",
            "job_title": "Position 2",
            "status": ApplicationStatus.INTERVIEWING,
            "user_id": "test_user_id",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    mock_service = Mock()
    mock_service.list_applications.return_value = mock_applications
    mock_application_service.return_value = mock_service

    # Act
    response = client.get("/api/v1/applications/")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_service.list_applications.assert_called_once()

def test_get_application_not_found(mock_auth_middleware, mock_application_service):
    # Arrange
    mock_service = Mock()
    mock_service.get_application.return_value = None
    mock_application_service.return_value = mock_service

    # Act
    response = client.get("/api/v1/applications/nonexistent_id")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"

def test_update_application(mock_auth_middleware, mock_application_service):
    # Arrange
    test_update = {
        "status": ApplicationStatus.INTERVIEWING,
        "notes": "Updated notes"
    }
    
    mock_service = Mock()
    mock_service.update_application.return_value = {
        "id": "test_id",
        "user_id": "test_user_id",
        **test_update,
        "updated_at": datetime.utcnow()
    }
    mock_application_service.return_value = mock_service

    # Act
    response = client.patch("/api/v1/applications/test_id", json=test_update)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == test_update["status"]
    assert response.json()["notes"] == test_update["notes"]
    mock_service.update_application.assert_called_once() 
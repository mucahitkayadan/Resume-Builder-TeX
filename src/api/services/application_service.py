from typing import Optional, List
from datetime import datetime
from src.core.database.factory import get_unit_of_work
from src.api.schemas.application import ApplicationStatus

class ApplicationService:
    def __init__(self):
        self.uow = get_unit_of_work()

    async def create_application(self, user_id: str, application_data: dict):
        with self.uow:
            application_data.update({
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            created = self.uow.applications.create(application_data)
            self.uow.commit()
            return created

    async def get_application(self, user_id: str, application_id: str):
        with self.uow:
            application = self.uow.applications.get_by_id(application_id)
            if application and application.user_id == user_id:
                return application
            return None

    async def list_applications(
        self,
        user_id: str,
        status: Optional[ApplicationStatus] = None
    ) -> List:
        with self.uow:
            if status:
                return self.uow.applications.get_by_status(user_id, status)
            return self.uow.applications.get_all_by_user(user_id)

    async def update_application(self, user_id: str, application_id: str, update_data: dict):
        with self.uow:
            application = self.uow.applications.get_by_id(application_id)
            if not application or application.user_id != user_id:
                raise Exception("Application not found")

            update_data["updated_at"] = datetime.utcnow()
            updated = self.uow.applications.update(application_id, update_data)
            self.uow.commit()
            return updated

    async def delete_application(self, user_id: str, application_id: str):
        with self.uow:
            application = self.uow.applications.get_by_id(application_id)
            if not application or application.user_id != user_id:
                raise Exception("Application not found")

            self.uow.applications.delete(application_id)
            self.uow.commit() 
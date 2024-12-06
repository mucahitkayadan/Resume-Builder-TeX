from typing import Dict, Any
from datetime import datetime
from src.core.database.factory import get_unit_of_work

class PreferencesService:
    def __init__(self):
        self.uow = get_unit_of_work()

    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        with self.uow:
            preferences = self.uow.users.get_preferences(user_id)
            if not preferences:
                return {}
            return preferences

    async def update_preferences(self, user_id: str, preferences_update: Dict[str, Any]) -> Dict[str, Any]:
        with self.uow:
            user = self.uow.users.get_by_user_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Get current preferences
            current_preferences = user.preferences.model_dump()

            # Update only provided fields
            for key, value in preferences_update.items():
                if value is not None:
                    current_preferences[key] = value

            # Update user preferences
            success = self.uow.users.update_preferences(user_id, current_preferences)
            if not success:
                raise ValueError("Failed to update preferences")

            return current_preferences
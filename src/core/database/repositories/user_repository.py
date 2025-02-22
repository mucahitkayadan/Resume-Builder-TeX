"""User repository module."""

from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId

from ..connections.mongo_connection import MongoConnection
from ..interfaces.repository_interface import BaseRepository
from ..models.user import User, UserPreferences


class MongoUserRepository(BaseRepository[User]):
    """Repository for handling user-related database operations."""

    def __init__(self, connection: MongoConnection):
        """Initialize UserRepository with database connection."""
        self.connection = connection
        self.collection = connection.db.users
        self.model = User

    def _prepare_for_validation(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare document for Pydantic validation."""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = self.collection.find_one({"email": email})
        if result:
            result = self._prepare_for_validation(result)
        return self.model.model_validate(result) if result else None

    def get_by_user_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id."""
        result = self.collection.find_one({"user_id": user_id})
        if result:
            result = self._prepare_for_validation(result)
        return self.model.model_validate(result) if result else None

    def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        try:
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"preferences": preferences, "updated_at": datetime.now()}},
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error updating preferences: {str(e)}")

    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        result = self.collection.find_one({"user_id": user_id}, {"preferences": 1})
        return result.get("preferences") if result else None

    def get_by_id(self, id: Any) -> Optional[User]:
        """Get user by ID."""
        result = self.collection.find_one({"_id": ObjectId(id)})
        if result:
            result = self._prepare_for_validation(result)
        return self.model.model_validate(result) if result else None

    def get_all(self) -> list[User]:
        """Get all users."""
        results = self.collection.find()
        return [
            self.model.model_validate(self._prepare_for_validation(doc))
            for doc in results
        ]

    def add(self, entity: User) -> User:
        """Add a new user."""
        result = self.collection.insert_one(entity.model_dump(exclude={"id"}))
        entity.id = str(result.inserted_id)
        return entity

    def update(self, entity: User) -> bool:
        """Update an existing user."""
        result = self.collection.update_one(
            {"_id": ObjectId(entity.id)}, {"$set": entity.model_dump(exclude={"id"})}
        )
        return result.modified_count > 0

    def delete(self, id: Any) -> bool:
        """Delete a user."""
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    def exists(self, id: Any) -> bool:
        """Check if a user exists."""
        return self.collection.count_documents({"_id": ObjectId(id)}) > 0

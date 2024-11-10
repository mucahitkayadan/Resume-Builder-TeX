from typing import Optional, List
from bson import ObjectId
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.user import User
from datetime import datetime

class MongoUserRepository(BaseRepository[User]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['users']

    def get_by_id(self, id: str) -> Optional[User]:
        try:
            result = self.collection.find_one({'_id': ObjectId(id)})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving user: {str(e)}")

    def get_by_email(self, email: str) -> Optional[User]:
        try:
            result = self.collection.find_one({'email': email})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving user by email: {str(e)}")

    def get_all(self) -> List[User]:
        try:
            results = self.collection.find()
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving all users: {str(e)}")

    def add(self, user: User) -> User:
        try:
            user_dict = user.dict(exclude={'id'})
            user_dict['created_at'] = datetime.utcnow()
            user_dict['updated_at'] = datetime.utcnow()
            result = self.collection.insert_one(user_dict)
            user.id = str(result.inserted_id)
            return user
        except Exception as e:
            raise DatabaseError(f"Error adding user: {str(e)}")

    def update(self, user: User) -> bool:
        try:
            user_dict = user.dict(exclude={'id'})
            user_dict['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(user.id)},
                {'$set': user_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating user: {str(e)}")

    def update_last_login(self, user_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'last_login': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating user last login: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({'_id': ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting user: {str(e)}")

    def exists(self, id: str) -> bool:
        try:
            return self.collection.count_documents({'_id': ObjectId(id)}) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking user existence: {str(e)}")

    def _map_to_entity(self, doc: dict) -> User:
        if doc:
            doc['id'] = str(doc.pop('_id'))
            return User(**doc)
        return None
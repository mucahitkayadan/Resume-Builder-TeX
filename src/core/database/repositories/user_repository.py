from typing import Optional, List, Dict, Any
from bson import ObjectId
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.user import User
from datetime import datetime, timezone

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
            user_dict = user.model_dump(exclude={'id'})
            user_dict['created_at'] = datetime.now(timezone.utc)
            user_dict['updated_at'] = datetime.now(timezone.utc)
            result = self.collection.insert_one(user_dict)
            user.id = str(result.inserted_id)
            return user
        except Exception as e:
            raise DatabaseError(f"Error adding user: {str(e)}")

    def update(self, user: User) -> bool:
        try:
            user_dict = user.model_dump(exclude={'id'})
            user_dict['updated_at'] = datetime.now(timezone.utc)
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
                        'last_login': datetime.now(timezone.utc),
                        'updated_at': datetime.now(timezone.utc)
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

    def get_by_user_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id field"""
        try:
            result = self.collection.find_one({'user_id': user_id})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving user by user_id: {str(e)}")

    def _map_to_entity(self, doc: dict) -> Optional[User]:
        if not doc:
            return None
        
        try:
            # Handle ID conversion
            doc['id'] = str(doc.pop('_id'))
            
            # Handle binary data
            if 'signature_image' in doc and doc['signature_image']:
                doc['signature_image'] = doc['signature_image']
                
            # Set default values
            doc.setdefault('signature_filename', None)
            doc.setdefault('signature_content_type', None)
            doc.setdefault('created_at', datetime.now(timezone.utc))
            doc.setdefault('updated_at', datetime.now(timezone.utc))
            doc.setdefault('last_login', None)
            
            return User(**doc)
        except Exception as e:
            print(f"Error mapping user entity: {str(e)}")
            return None

    def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'preferences': preferences,
                        'updated_at': datetime.now(timezone.utc)
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating user preferences: {str(e)}")

    def update_life_story(self, user_id: str, life_story: str) -> bool:
        """Update the user life story"""
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'life_story': life_story,
                        'updated_at': datetime.now(timezone.utc)
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating user life story: {str(e)}")

    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        try:
            user = self.get_by_id(user_id)
            return user.preferences.model_dump() if user else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving user preferences: {str(e)}")

    def get_life_story(self, user_id: str) -> Optional[str]:
        """Get the user life story"""
        try:
            user = self.get_by_id(user_id)
            return user.life_story if user else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving user life story: {str(e)}")

    def update_skill_preferences(self, user_id: str, max_categories: int = None, 
                               min_skills: int = None, max_skills: int = None) -> bool:
        """Update user's skill preferences"""
        try:
            update_dict = {}
            if max_categories is not None:
                update_dict['preferences.skills_details.max_categories'] = max_categories
            if min_skills is not None:
                update_dict['preferences.skills_details.min_skills_per_category'] = min_skills
            if max_skills is not None:
                update_dict['preferences.skills_details.max_skills_per_category'] = max_skills
            
            if not update_dict:
                return True
            
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': update_dict,
                    '$currentDate': {'updated_at': True}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating skill preferences: {str(e)}")

    def update_llm_preferences(self, user_id: str, preferences: dict):
        """Update LLM preferences for a user"""
        self.collection.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'llm_preferences': preferences,
                    'updated_at': datetime.utcnow()
                }
            }
        )

    def update_section_preferences(self, user_id: str, preferences: dict):
        """Update section preferences for a user"""
        self.collection.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'section_preferences': preferences,
                    'updated_at': datetime.utcnow()
                }
            }
        )

    def get_preferences(self, user_id: str):
        """Get all preferences for a user"""
        user = self.collection.find_one({'user_id': user_id})
        if user:
            return {
                'llm_preferences': user.get('llm_preferences', {}),
                'section_preferences': user.get('section_preferences', {}),
                'feature_preferences': user.get('feature_preferences', {})
            }
        return None
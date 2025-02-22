from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone
from ..interfaces.repository_interface import BaseRepository
from ..models.profile import Profile, Signature
from ...exceptions.database_exceptions import DatabaseError

class MongoProfileRepository(BaseRepository[Profile]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['profiles']

    def get_by_id(self, id: str) -> Optional[Profile]:
        try:
            result = self.collection.find_one({'_id': ObjectId(id)})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving profile: {str(e)}")

    def get_by_user_id(self, user_id: str) -> Optional[Profile]:
        try:
            result = self.collection.find_one({'user_id': user_id})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving profile by user ID: {str(e)}")

    def get_all(self) -> List[Profile]:
        try:
            results = self.collection.find()
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving all profiles: {str(e)}")

    def add(self, profile: Profile) -> Profile:
        try:
            doc = profile.dict(exclude={'id'})
            doc['created_at'] = datetime.now(timezone.utc)
            doc['updated_at'] = doc['created_at']
            result = self.collection.insert_one(doc)
            return self.get_by_id(str(result.inserted_id))
        except Exception as e:
            raise DatabaseError(f"Error adding profile: {str(e)}")

    def update(self, profile: Profile) -> Optional[Profile]:
        try:
            doc = profile.dict(exclude={'id'})
            doc['updated_at'] = datetime.now(timezone.utc)
            result = self.collection.update_one(
                {'_id': ObjectId(profile.id)},
                {'$set': doc}
            )
            if result.modified_count == 0:
                return None
            return self.get_by_id(profile.id)
        except Exception as e:
            raise DatabaseError(f"Error updating profile: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({'_id': ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting profile: {str(e)}")

    def exists(self, id: str) -> bool:
        try:
            return self.collection.count_documents({'_id': ObjectId(id)}) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking profile existence: {str(e)}")

    def update_signature(self, user_id: str, signature_data: bytes, 
                        filename: str, content_type: str) -> Optional[Profile]:
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'signature.image': signature_data,
                        'signature.filename': filename,
                        'signature.content_type': content_type,
                        'updated_at': datetime.now(timezone.utc)
                    }
                }
            )
            if result.modified_count == 0:
                return None
            return self.get_by_user_id(user_id)
        except Exception as e:
            raise DatabaseError(f"Error updating signature: {str(e)}")

    def update_personal_information(self, user_id: str, 
                                  personal_info: dict) -> Optional[Profile]:
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'personal_information': personal_info,
                        'updated_at': datetime.now(timezone.utc)
                    }
                }
            )
            if result.modified_count == 0:
                return None
            return self.get_by_user_id(user_id)
        except Exception as e:
            raise DatabaseError(f"Error updating personal information: {str(e)}")

    def update_life_story(self, user_id: str, life_story: str) -> Optional[Profile]:
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
            if result.modified_count == 0:
                return None
            return self.get_by_user_id(user_id)
        except Exception as e:
            raise DatabaseError(f"Error updating life story: {str(e)}")

    def _map_to_entity(self, doc: dict) -> Optional[Profile]:
        if not doc:
            return None
        try:
            doc['id'] = str(doc.pop('_id'))
            
            # Handle signature if it exists
            if 'signature' in doc and isinstance(doc['signature'], dict):
                signature_data = doc['signature']
                doc['signature'] = Signature(
                    content_type=signature_data.get('content_type', ''),
                    filename=signature_data.get('filename', ''),
                    image=signature_data.get('image', None)
                )
            
            return Profile(**doc)
        except Exception as e:
            raise DatabaseError(f"Error mapping profile entity: {str(e)}")

from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.resume import Resume

class MongoResumeRepository(BaseRepository[Resume]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['resumes']

    def get_by_id(self, id: str) -> Optional[Resume]:
        try:
            # Validate ObjectId format
            if not ObjectId.is_valid(id):
                return None
                
            result = self.collection.find_one({'_id': ObjectId(id)})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving resume: {str(e)}")

    def get_all_by_user(self, user_id: str) -> List[Resume]:
        """Get all resumes for a specific user"""
        try:
            results = self.collection.find({'user_id': user_id})
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving user resumes: {str(e)}")

    def get_latest_resume(self, user_id: str) -> Optional[Resume]:
        """Get the most recent resume for a user"""
        try:
            result = self.collection.find_one(
                {'user_id': user_id},
                sort=[('created_at', -1)]
            )
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving latest resume: {str(e)}")

    def exists(self, id: str) -> bool:
        """Check if resume exists"""
        try:
            if not ObjectId.is_valid(id):
                return False
            return self.collection.count_documents({'_id': ObjectId(id)}) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking resume existence: {str(e)}")

    def get_all(self) -> List[Resume]:
        """Get all resumes"""
        try:
            results = self.collection.find()
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving all resumes: {str(e)}")

    def add(self, resume: Resume) -> Resume:
        try:
            resume_dict = resume.model_dump(exclude={'id'})
            resume_dict['created_at'] = datetime.now(timezone.utc)
            resume_dict['updated_at'] = datetime.now(timezone.utc)
            result = self.collection.insert_one(resume_dict)
            resume.id = str(result.inserted_id)
            return resume
        except Exception as e:
            raise DatabaseError(f"Error adding resume: {str(e)}")

    def update(self, resume: Resume) -> bool:
        try:
            if not ObjectId.is_valid(resume.id):
                return False
                
            update_data = resume.model_dump(exclude={'id'})
            update_data['updated_at'] = datetime.now(timezone.utc)
            result = self.collection.update_one(
                {'_id': ObjectId(resume.id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating resume: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            if not ObjectId.is_valid(id):
                return False
                
            result = self.collection.delete_one({'_id': ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting resume: {str(e)}")

    def _map_to_entity(self, doc: dict) -> Optional[Resume]:
        if not doc:
            return None
        try:
            # Convert ObjectId to string for id field
            doc['id'] = str(doc.pop('_id'))
            
            # Convert datetime objects to UTC
            for field in ['created_at', 'updated_at']:
                if field in doc and doc[field]:
                    # If it's a string, parse it to datetime
                    if isinstance(doc[field], str):
                        try:
                            doc[field] = datetime.fromisoformat(doc[field].replace('Z', '+00:00'))
                        except ValueError:
                            # If parsing fails, use current time
                            doc[field] = datetime.now(timezone.utc)
                    # If it's already a datetime but has no timezone
                    elif isinstance(doc[field], datetime) and not doc[field].tzinfo:
                        doc[field] = doc[field].replace(tzinfo=timezone.utc)

            return Resume(**doc)
        except Exception as e:
            raise DatabaseError(f"Error mapping resume entity: {str(e)}")
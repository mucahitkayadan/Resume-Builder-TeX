from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.resume import Resume
import logging

logger = logging.getLogger(__name__)

class MongoResumeRepository(BaseRepository[Resume]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['resumes']

    def get_by_id(self, resume_id: str) -> Optional[Resume]:
        try:
            # Validate ObjectId format
            if not ObjectId.is_valid(resume_id):
                return None
                
            result = self.collection.find_one({'_id': ObjectId(resume_id)})
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
            if not isinstance(user_id, str):
                logger.error(f"Invalid user_id type: {type(user_id)}")
                raise ValueError(f"user_id must be a string, got {type(user_id)}")
            
            logger.debug(f"Attempting to get latest resume for user_id: {user_id}")
            
            # First, check if any resumes exist for this user
            count = self.collection.count_documents({'user_id': user_id})
            logger.debug(f"Found {count} resumes for user_id: {user_id}")
            
            # Log the query we're about to execute
            query = {'user_id': user_id}
            sort_order = [('created_at', -1)]
            logger.debug(f"Executing MongoDB query: {query} with sort: {sort_order}")
            
            result = self.collection.find_one(query, sort=sort_order)
            logger.debug(f"Raw MongoDB result: {result}")
            
            if result:
                mapped_result = self._map_to_entity(result)
                logger.debug(f"Mapped result user_id: {mapped_result.user_id}, id: {mapped_result.id}")
                return mapped_result
            
            logger.debug(f"No resume found for user: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving latest resume: {str(e)}")
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
            logger.debug(f"Adding resume with user_id: {resume_dict.get('user_id')}")
            resume_dict['created_at'] = datetime.now(timezone.utc)
            resume_dict['updated_at'] = datetime.now(timezone.utc)
            result = self.collection.insert_one(resume_dict)
            resume.id = str(result.inserted_id)
            logger.debug(f"Successfully added resume with _id: {resume.id}")
            return resume
        except Exception as e:
            logger.error(f"Error adding resume: {str(e)}")
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
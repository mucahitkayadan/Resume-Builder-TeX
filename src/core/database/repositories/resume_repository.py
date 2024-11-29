from typing import Optional, List
from bson import ObjectId
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.resume import Resume
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MongoResumeRepository(BaseRepository[Resume]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['resumes']

    def get_by_id(self, id: str) -> Optional[Resume]:
        try:
            result = self.collection.find_one({'_id': ObjectId(id)})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving resume: {str(e)}")

    def get_all(self) -> List[Resume]:
        try:
            results = self.collection.find()
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving all resumes: {str(e)}")

    def add(self, resume: Resume) -> Resume:
        try:
            # Create base dictionary with all fields
            resume_dict = resume.dict(exclude={'id'})
            
            # Handle timestamps
            resume_dict['created_at'] = datetime.utcnow()
            resume_dict['updated_at'] = datetime.utcnow()
            
            # Handle binary data separately to avoid encoding issues
            if resume.resume_pdf:
                try:
                    resume_dict['resume_pdf'] = resume.resume_pdf
                except Exception as e:
                    logger.info(f"Error handling resume PDF: {e}")
                    resume_dict['resume_pdf'] = None
                    
            if resume.cover_letter_pdf:
                try:
                    resume_dict['cover_letter_pdf'] = resume.cover_letter_pdf
                except Exception as e:
                    logger.info(f"Error handling cover letter PDF: {e}")
                    resume_dict['cover_letter_pdf'] = None
            
            # Ensure model information is explicitly set
            resume_dict['model_type'] = resume.model_type
            resume_dict['model_name'] = resume.model_name
            resume_dict['temperature'] = float(resume.temperature) if resume.temperature is not None else 0.1
            
            # Insert into database
            result = self.collection.insert_one(resume_dict)
            resume.id = str(result.inserted_id)
            return resume
        except Exception as e:
            logger.info(f"Full error details: {str(e)}")
            raise DatabaseError(f"Error adding resume: {str(e)}")

    def update(self, resume: Resume) -> bool:
        try:
            resume_dict = resume.dict(exclude={'id'})
            resume_dict['updated_at'] = datetime.utcnow()
            
            # Handle binary data separately
            if resume.resume_pdf:
                resume_dict['resume_pdf'] = resume.resume_pdf
            if resume.cover_letter_pdf:
                resume_dict['cover_letter_pdf'] = resume.cover_letter_pdf
                
            result = self.collection.update_one(
                {'_id': ObjectId(resume.id)},
                {'$set': resume_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating resume: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({'_id': ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting resume: {str(e)}")

    def exists(self, id: str) -> bool:
        try:
            return self.collection.count_documents({'_id': ObjectId(id)}) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking resume existence: {str(e)}")

    def get_by_user_id(self, user_id: str) -> List[Resume]:
        """Get all resumes for a specific user"""
        try:
            results = self.collection.find({'user_id': user_id})
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving resumes by user ID: {str(e)}")

    def _map_to_entity(self, doc: dict) -> Resume:
        if not doc:
            return None
        
        try:
            # Handle ID conversion
            doc['id'] = str(doc.pop('_id'))
            
            # Set default user_id if missing
            doc.setdefault('user_id', 'default_user')
            
            # Set default values for required fields
            doc.setdefault('company_name', '')
            doc.setdefault('job_title', '')
            doc.setdefault('job_description', '')
            
            # Set default values for optional fields
            doc.setdefault('personal_information', '')
            doc.setdefault('career_summary', '')
            doc.setdefault('skills', '')
            doc.setdefault('work_experience', '')
            doc.setdefault('education', '')
            doc.setdefault('projects', '')
            doc.setdefault('awards', '')
            doc.setdefault('publications', '')
            
            # Ensure model information is present
            doc.setdefault('model_type', None)
            doc.setdefault('model_name', None)
            doc.setdefault('temperature', 0.1)
            
            # Set default timestamps
            doc.setdefault('created_at', datetime.utcnow())
            doc.setdefault('updated_at', datetime.utcnow())
            
            # Handle binary data
            if 'resume_pdf' in doc and doc['resume_pdf']:
                doc['resume_pdf'] = doc['resume_pdf']
            if 'cover_letter_pdf' in doc and doc['cover_letter_pdf']:
                doc['cover_letter_pdf'] = doc['cover_letter_pdf']
                
            return Resume(**doc)
        except Exception as e:
            logger.info(f"Error mapping entity: {str(e)}")
            return None

    def get_latest_resume(self) -> Optional[Resume]:
        """Get the most recently created resume"""
        try:
            result = self.collection.find_one(
                sort=[('created_at', -1)]
            )
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving latest resume: {str(e)}")
from typing import Optional, List
from bson import ObjectId
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.portfolio import Portfolio, CareerSummary
from datetime import datetime

class MongoPortfolioRepository(BaseRepository[Portfolio]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['portfolio']

    def get_by_id(self, id: str) -> Optional[Portfolio]:
        try:
            result = self.collection.find_one({'_id': ObjectId(id)})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving portfolio: {str(e)}")

    def get_all(self) -> List[Portfolio]:
        try:
            results = self.collection.find()
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving all portfolios: {str(e)}")

    def add(self, portfolio: Portfolio) -> Portfolio:
        try:
            result = self.collection.insert_one(portfolio.dict(exclude={'id'}))
            portfolio.id = str(result.inserted_id)
            return portfolio
        except Exception as e:
            raise DatabaseError(f"Error adding portfolio: {str(e)}")

    def update(self, portfolio: Portfolio) -> bool:
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(portfolio.id)},
                {'$set': portfolio.dict(exclude={'id'})}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating portfolio: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({'_id': ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting portfolio: {str(e)}")

    def exists(self, id: str) -> bool:
        try:
            return self.collection.count_documents({'_id': ObjectId(id)}) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking portfolio existence: {str(e)}")

    def _map_to_entity(self, doc: dict) -> Portfolio:
        if not doc:
            return None
        
        try:
            # Convert _id to string id
            doc['id'] = str(doc.pop('_id'))
            
            # Handle career_summary mapping
            if 'career_summary' in doc and isinstance(doc['career_summary'], dict):
                doc['career_summary'] = CareerSummary(
                    job_titles=doc['career_summary'].get('job_titles', []),
                    years_of_experience=doc['career_summary'].get('years_of_experience', ''),
                    default_summary=doc['career_summary'].get('default_summary', '')
                )
                
            if 'skills' in doc and isinstance(doc['skills'], dict):
                # Convert skill dict to a list of dicts format
                doc['skills'] = [
                    {category: skills_list} 
                    for category, skills_list in doc['skills'].items()
                ]
                
            # Add missing required fields with default values
            doc.setdefault('certifications', [])
            doc.setdefault('languages', [])
            doc.setdefault('created_at', datetime.utcnow())
            doc.setdefault('updated_at', datetime.utcnow())
            
            return Portfolio(**doc)
        except Exception as e:
            print(f"Error mapping portfolio entity: {str(e)}")
            raise DatabaseError(f"Error mapping portfolio entity: {str(e)}")

    def get_by_user_id(self, user_id: str) -> Optional[Portfolio]:
        """Additional method specific to portfolio repository"""
        try:
            result = self.collection.find_one({'user_id': user_id})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving portfolio by user ID: {str(e)}") 
    
    def update_career_summary(self, portfolio_id: str, career_summary: CareerSummary) -> bool:
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(portfolio_id)},
                {'$set': {
                    'career_summary': career_summary.dict(),
                    'updated_at': datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating career summary: {str(e)}")
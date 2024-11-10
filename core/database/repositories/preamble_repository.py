from typing import Optional, List
from bson import ObjectId
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.preamble import Preamble
from datetime import datetime

class MongoPreambleRepository(BaseRepository[Preamble]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['preambles']

    def get_by_id(self, id: str) -> Optional[Preamble]:
        try:
            result = self.collection.find_one({'_id': ObjectId(id)})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving preamble: {str(e)}")

    def get_all(self) -> List[Preamble]:
        try:
            results = self.collection.find()
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving all preambles: {str(e)}")

    def add(self, preamble: Preamble) -> Preamble:
        try:
            preamble_dict = preamble.dict(exclude={'id'})
            result = self.collection.insert_one(preamble_dict)
            preamble.id = str(result.inserted_id)
            return preamble
        except Exception as e:
            raise DatabaseError(f"Error adding preamble: {str(e)}")

    def update(self, preamble: Preamble) -> bool:
        try:
            preamble_dict = preamble.dict(exclude={'id'})
            result = self.collection.update_one(
                {'_id': ObjectId(preamble.id)},
                {'$set': preamble_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating preamble: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({'_id': ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting preamble: {str(e)}")

    def exists(self, id: str) -> bool:
        try:
            return self.collection.count_documents({'_id': ObjectId(id)}) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking preamble existence: {str(e)}")

    def _map_to_entity(self, doc: dict) -> Preamble:
        if doc:
            doc['id'] = str(doc.pop('_id'))
            return Preamble(**doc)
        return None

    def get_by_name(self, name: str) -> Optional[Preamble]:
        """Get a preamble by its name"""
        try:
            result = self.collection.find_one({'name': name})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving preamble by name: {str(e)}")

    def get_by_type(self, type: str) -> Optional[Preamble]:
        """Get a preamble by its type"""
        try:
            result = self.collection.find_one({'type': type})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving preamble by type: {str(e)}")
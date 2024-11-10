from typing import Optional, List
from bson import ObjectId
from ...exceptions.database_exceptions import DatabaseError
from ..interfaces.repository_interface import BaseRepository
from ..models.tex_header import TexHeader
from datetime import datetime

class MongoTexHeaderRepository(BaseRepository[TexHeader]):
    def __init__(self, connection):
        self.connection = connection
        self.collection = self.connection.db['tex_headers']

    def get_by_id(self, id: str) -> Optional[TexHeader]:
        try:
            result = self.collection.find_one({'_id': ObjectId(id)})
            return self._map_to_entity(result) if result else None
        except Exception as e:
            raise DatabaseError(f"Error retrieving tex header: {str(e)}")

    def get_all(self) -> List[TexHeader]:
        try:
            results = self.collection.find()
            return [self._map_to_entity(doc) for doc in results]
        except Exception as e:
            raise DatabaseError(f"Error retrieving all tex headers: {str(e)}")

    def add(self, tex_header: TexHeader) -> TexHeader:
        try:
            header_dict = tex_header.dict(exclude={'id'})
            header_dict['created_at'] = datetime.utcnow()
            header_dict['updated_at'] = datetime.utcnow()
            result = self.collection.insert_one(header_dict)
            tex_header.id = str(result.inserted_id)
            return tex_header
        except Exception as e:
            raise DatabaseError(f"Error adding tex header: {str(e)}")

    def update(self, tex_header: TexHeader) -> bool:
        try:
            header_dict = tex_header.dict(exclude={'id'})
            header_dict['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(tex_header.id)},
                {'$set': header_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error updating tex header: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({'_id': ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting tex header: {str(e)}")

    def exists(self, id: str) -> bool:
        try:
            return self.collection.count_documents({'_id': ObjectId(id)}) > 0
        except Exception as e:
            raise DatabaseError(f"Error checking tex header existence: {str(e)}")

    def _map_to_entity(self, doc: dict) -> TexHeader:
        if doc:
            doc['id'] = str(doc.pop('_id'))
            if 'created_at' not in doc:
                doc['created_at'] = datetime.utcnow()
            if 'updated_at' not in doc:
                doc['updated_at'] = datetime.utcnow()
            return TexHeader(**doc)
        return None
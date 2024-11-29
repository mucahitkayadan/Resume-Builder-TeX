from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Retrieve an entity by its ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities"""
        pass
    
    @abstractmethod
    def add(self, entity: T) -> T:
        """Add a new entity"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete an entity by its ID"""
        pass
    
    @abstractmethod
    def exists(self, id: Any) -> bool:
        """Check if an entity exists"""
        pass 
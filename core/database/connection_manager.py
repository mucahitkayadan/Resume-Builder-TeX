import sqlite3
from typing import Optional
from contextlib import contextmanager

class ConnectionManager:
    """Manages database connections"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
        return self._connection
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        try:
            yield self.connection
        except Exception as e:
            self.connection.rollback()
            raise e
        
    def close(self):
        """Close the database connection"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None 
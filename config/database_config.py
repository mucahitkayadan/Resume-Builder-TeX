"""Database configuration module."""

from typing import Dict, Any
from dataclasses import dataclass
from config.config import MONGODB_URI, MONGODB_DATABASE

@dataclass
class MongoDBConfig:
    """MongoDB configuration settings."""
    
    uri: str
    database: str
    collections: Dict[str, str]
    options: Dict[str, Any]

class DatabaseConfig:
    """Database configuration handler."""
    
    # MongoDB configuration
    MONGODB = MongoDBConfig(
        uri=MONGODB_URI,
        database=MONGODB_DATABASE,
        collections={
            'users': "users",
            'profiles': "profiles",
            'resumes': "resumes",
            'cover_letters': "cover_letters",
            'portfolios': "portfolios"
        },
        options={
            'max_pool_size': 50,
            'connect_timeout': 30000,
            'server_selection_timeout': 5000
        }
    )
    
    @classmethod
    def get_mongodb_config(cls) -> MongoDBConfig:
        """
        Get MongoDB configuration.
        
        Returns:
            MongoDBConfig: MongoDB configuration settings
        """
        return cls.MONGODB
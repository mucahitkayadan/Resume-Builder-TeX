from pathlib import Path
from typing import Dict, Any

class DatabaseConfig:
    # Base paths
    DB_DIR = Path(__file__).parent.parent / "db"
    
    # SQLite configuration
    SQLITE = {
        'resume_db': str(DB_DIR / "resumes.db"),
        'preamble_db': str(DB_DIR / "preambles.db"),
        'user_db': str(DB_DIR / "users.db")
    }
    
    # MongoDB configuration
    MONGODB = {
        'uri': "mongodb://localhost:27017/",
        'database': "user_information",
        'collections': {
            'portfolio': "portfolio",
            'users': "users",
            'analytics': "analytics"
        },
        'options': {
            'max_pool_size': 50,
            'connect_timeout': 30000,
            'server_selection_timeout': 5000
        }
    }
    
    @classmethod
    def get_sqlite_config(cls, db_name: str) -> str:
        return cls.SQLITE.get(db_name)
    
    @classmethod
    def get_mongodb_config(cls) -> Dict[str, Any]:
        return cls.MONGODB
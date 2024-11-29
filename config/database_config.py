from config.config import MONGODB_URI, MONGODB_DATABASE

class DatabaseConfig:
    # MongoDB configuration
    MONGODB = {
        'uri': MONGODB_URI,
        'database': MONGODB_DATABASE,
        'collections': {
            'portfolio': "portfolio",
            'users': "users",
            'analytics': "analytics",
            'resumes': "resumes"
        },
        'options': {
            'max_pool_size': 50,
            'connect_timeout': 30000,
            'server_selection_timeout': 5000
        }
    }
    
    @classmethod
    def get_mongodb_config(cls):
        return cls.MONGODB
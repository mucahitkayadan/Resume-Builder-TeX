from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from config.config import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION
import logging

class MongoLoader:
    """
    A class to load user information from MongoDB.
    """
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DATABASE]
        self.collection = self.db[MONGODB_COLLECTION]
        self.data = self._load_data()

    def _load_data(self) -> Optional[Dict[str, Any]]:
        """Load user data from MongoDB."""
        try:
            return self.collection.find_one()
        except Exception as e:
            logging.error(f"Error loading data from MongoDB: {e}")
            return None

    def get_personal_information(self) -> Dict[str, Any]:
        """Get personal information from MongoDB."""
        return self.data.get('personal_information', {})

    def get_career_summary(self) -> Dict[str, Any]:
        """Get career summary from MongoDB."""
        return self.data.get('career_summary', {})

    def get_skills(self) -> Dict[str, List[str]]:
        """Get skills from MongoDB."""
        return self.data.get('skills', {})

    def get_work_experience(self) -> List[Dict[str, Any]]:
        """Get work experience from MongoDB."""
        return self.data.get('work_experience', [])

    def get_education(self) -> List[Dict[str, Any]]:
        """Get education from MongoDB."""
        return self.data.get('education', [])

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get projects from MongoDB."""
        return self.data.get('projects', [])

    def get_awards(self) -> List[Dict[str, Any]]:
        """Get awards from MongoDB."""
        return self.data.get('awards', [])

    def get_publications(self) -> List[Dict[str, Any]]:
        """Get publications from MongoDB."""
        return self.data.get('publications', []) 
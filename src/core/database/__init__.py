"""
Database management package including repositories, models, and unit of work implementations.
"""

from .models import User, Portfolio, Resume, Profile
from .repositories import (
    MongoPortfolioRepository,
    MongoUserRepository,
    MongoResumeRepository,
    MongoProfileRepository
)
from .unit_of_work import *
from .connections import *
from .interfaces import *

__all__ = [
    # Models
    'User',
    'Portfolio',
    'Resume',
    'Profile',
    
    # Repositories
    'MongoPortfolioRepository',
    'MongoUserRepository',
    'MongoResumeRepository',
    'MongoProfileRepository',
    
    # Unit of Work
    'MongoUnitOfWork',
    
    # Connections
    'MongoConnection',
    
    # Interfaces
    'DatabaseInterface',
    'BaseRepository'
]

"""
Core interfaces for database operations.
"""

from .database_interface import DatabaseInterface
from .repository_interface import BaseRepository

__all__ = [
    'DatabaseInterface',
    'BaseRepository'
]

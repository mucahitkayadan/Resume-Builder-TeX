"""
Custom exceptions for the core package.
"""

from .database_exceptions import (
    ConnectionError,
    DatabaseError,
    EntityNotFoundError,
    TransactionError,
)

__all__ = [
    "DatabaseError",
    "ConnectionError",
    "TransactionError",
    "EntityNotFoundError",
]

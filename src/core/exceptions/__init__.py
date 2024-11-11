"""
Custom exceptions for the core package.
"""

from .database_exceptions import (
    DatabaseError,
    ConnectionError,
    TransactionError,
    EntityNotFoundError
)

__all__ = [
    'DatabaseError',
    'ConnectionError',
    'TransactionError',
    'EntityNotFoundError'
] 
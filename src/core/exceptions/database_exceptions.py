class DatabaseError(Exception):
    """Base class for database exceptions"""

    def __init__(self, message="A database error occurred"):
        self.message = message
        super().__init__(self.message)


class ConnectionError(DatabaseError):
    """Raised when database connection fails"""

    def __init__(self, message="Failed to connect to database"):
        self.message = message
        super().__init__(self.message)


class TransactionError(DatabaseError):
    """Raised when transaction operations fail"""

    def __init__(self, message="Database transaction failed"):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DatabaseError):
    """Raised when requested entity is not found"""

    def __init__(self, entity_type=None, entity_id=None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        message = (
            f"{entity_type} with id {entity_id} not found"
            if entity_type and entity_id
            else "Entity not found"
        )
        super().__init__(message)



class InvalidIdentifierError(ValueError):
    """Raised when an identifier has an invalid format."""
    pass

class InvalidRecordError(ValueError):
    """Raised when a CSV record cannot be accepted due to invalid data."""
    pass
"""Define custom exception types."""

class GeanyError(Exception):
    
    def __init__(self, message):
        super().__init__(message)

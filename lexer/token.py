from .token_types import TokenType

class Token:
    """
    Represents a token in the GGScript language
    """
    def __init__(self, type, value, line, column):
        self.type = type      # TokenType enum
        self.value = value    # Actual value (string, int, float, etc.)
        self.line = line      # Line number in source
        self.column = column  # Column number in source
    
    def __repr__(self):
        """String representation for debugging"""
        return f"Token({self.type.name}, '{self.value}', Line: {self.line}, Col: {self.column})"
    
    def __str__(self):
        """User-friendly string representation"""
        return f"{self.type.name}: {self.value}"
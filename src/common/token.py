"""
Token class and related functionality for representing lexical tokens.
"""
from dataclasses import dataclass
from typing import Optional, Literal, Union


TokenType = Literal["ID", "KEYWORD", "NUM", "SYMBOL", "WHITESPACE", "COMMENT", "EOF"]


@dataclass(frozen=True)
class Token:
    """
    Immutable representation of a token in the source code.
    
    Attributes:
        type: The token type (KEYWORD, ID, NUM, SYMBOL, etc.)
        lexeme: The actual text of the token
        line: The line number where the token appears
    """
    type: TokenType
    lexeme: str
    line: int
    
    def __str__(self) -> str:
        """String representation of the token."""
        return f"({self.type}, {self.lexeme})"
    
    def __repr__(self) -> str:
        """Detailed representation including line number."""
        return f"Token({self.type}, '{self.lexeme}', line={self.line})"


class TokenError(Exception):
    """
    Exception raised for token-related errors.
    """
    pass 
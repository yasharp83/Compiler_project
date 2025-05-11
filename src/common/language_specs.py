"""
Language specifications for the compiler, defining tokens, keywords, and character sets.
"""
from typing import List, Set, FrozenSet


# Language constants
KEYWORDS: FrozenSet[str] = frozenset([
    "if", "else", "void", "int", "while", "break", "return"
])

SYMBOLS: FrozenSet[str] = frozenset([
    ';', ':', ',', '[', ']', '(', ')', '{', '}', 
    '+', '-', '*', '/', '\\', '=', '>', '<'
])

# Character classes
WHITESPACE: FrozenSet[str] = frozenset([
    ' ', '\n', '\t', '\r', '\v', '\f'  # Using actual characters instead of chr()
])

DIGITS: FrozenSet[str] = frozenset([str(i) for i in range(10)])  # '0'-'9'

LETTERS: FrozenSet[str] = frozenset(
    [chr(i) for i in range(65, 91)] +  # A-Z
    [chr(i) for i in range(97, 123)]   # a-z
)

# Generate the full alphabet (all possible characters)
SIGMA: FrozenSet[str] = frozenset([chr(i) for i in range(256)])

# Generate illegal characters (everything not explicitly allowed)
ILLEGAL: FrozenSet[str] = SIGMA - SYMBOLS - WHITESPACE - DIGITS - LETTERS


def is_keyword(token: str) -> bool:
    """
    Check if a token is a keyword.
    
    Args:
        token: String to check
        
    Returns:
        True if the token is a keyword, False otherwise
    """
    return token in KEYWORDS


def is_symbol(char: str) -> bool:
    """
    Check if a character is a symbol.
    
    Args:
        char: Character to check
        
    Returns:
        True if the character is a symbol, False otherwise
    """
    return char in SYMBOLS


def is_whitespace(char: str) -> bool:
    """
    Check if a character is whitespace.
    
    Args:
        char: Character to check
        
    Returns:
        True if the character is whitespace, False otherwise
    """
    return char in WHITESPACE


def is_digit(char: str) -> bool:
    """
    Check if a character is a digit.
    
    Args:
        char: Character to check
        
    Returns:
        True if the character is a digit, False otherwise
    """
    return char in DIGITS


def is_letter(char: str) -> bool:
    """
    Check if a character is a letter.
    
    Args:
        char: Character to check
        
    Returns:
        True if the character is a letter, False otherwise
    """
    return char in LETTERS


def is_legal_char(char: str) -> bool:
    """
    Check if a character is legal in the language.
    
    Args:
        char: Character to check
        
    Returns:
        True if the character is legal, False otherwise
    """
    return char not in ILLEGAL 
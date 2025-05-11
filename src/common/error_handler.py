"""
Error handling for the compiler.
"""
import logging
from enum import Enum, auto
from typing import Dict, List, Tuple, Union, Optional
from collections import defaultdict


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Enum for error types."""
    # Lexical errors
    INVALID_NUMBER = auto()
    INVALID_INPUT = auto()
    UNMATCHED_COMMENT = auto()
    UNCLOSED_COMMENT = auto()
    
    # Syntax errors
    UNEXPECTED_TOKEN = auto()
    MISSING_TOKEN = auto()
    
    # Semantic errors
    TYPE_MISMATCH = auto()
    UNDEFINED_VARIABLE = auto()
    UNDEFINED_FUNCTION = auto()
    DUPLICATE_DEFINITION = auto()
    
    def __str__(self) -> str:
        """String representation of the error type."""
        return self.name


class CompilerError(Exception):
    """Base exception for compiler errors."""
    pass


class ErrorHandler:
    """
    Base class for handling and reporting errors.
    """
    def __init__(self, error_file_path: str):
        """
        Initialize the error handler.
        
        Args:
            error_file_path: Path to the error output file
        """
        self.error_file_path = error_file_path
        self.errors: Dict[int, List[Tuple[ErrorType, str, Optional[str]]]] = defaultdict(list)
        self.error_messages: Dict[ErrorType, str] = self._get_default_error_messages()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the error file exists."""
        try:
            with open(self.error_file_path, 'a'):
                pass
        except IOError as e:
            logger.error(f"Error creating error file {self.error_file_path}: {e}")
            raise CompilerError(f"Could not create error file: {e}")
    
    def _get_default_error_messages(self) -> Dict[ErrorType, str]:
        """
        Get default error messages for each error type.
        
        Returns:
            Dictionary mapping error types to messages
        """
        return {
            ErrorType.INVALID_NUMBER: "Invalid number",
            ErrorType.INVALID_INPUT: "Invalid input",
            ErrorType.UNMATCHED_COMMENT: "Unmatched comment",
            ErrorType.UNCLOSED_COMMENT: "Unclosed comment",
            ErrorType.UNEXPECTED_TOKEN: "Unexpected token",
            ErrorType.MISSING_TOKEN: "Missing token",
            ErrorType.TYPE_MISMATCH: "Type mismatch",
            ErrorType.UNDEFINED_VARIABLE: "Undefined variable",
            ErrorType.UNDEFINED_FUNCTION: "Undefined function",
            ErrorType.DUPLICATE_DEFINITION: "Duplicate definition",
        }
    
    def add_error(self, line: int, error_type: ErrorType, text: str, 
                 additional_info: Optional[str] = None) -> None:
        """
        Add an error at a specific line.
        
        Args:
            line: The line number where the error occurred
            error_type: The type of error
            text: The text that caused the error
            additional_info: Additional information about the error (optional)
        """
        self.errors[line].append((error_type, text, additional_info))
        logger.debug(f"Error at line {line}: {error_type} - {text}")
    
    def has_errors(self) -> bool:
        """
        Check if there are any errors.
        
        Returns:
            True if there are errors, False otherwise
        """
        return bool(self.errors)
    
    def get_errors(self, line: Optional[int] = None) -> Union[Dict[int, List], List]:
        """
        Get all errors or errors for a specific line.
        
        Args:
            line: Optional line number to filter errors
            
        Returns:
            Dictionary of errors by line, or list of errors for the specified line
        """
        if line is not None:
            return self.errors.get(line, [])
        return dict(self.errors)
    
    def write_to_file(self) -> None:
        """Write errors to the output file."""
        try:
            with open(self.error_file_path, 'w') as f:
                if not self.has_errors():
                    f.write("There is no error.\n")
                    return
                
                for line in sorted(self.errors.keys()):
                    f.write(f"{line}.\t")
                    for error_type, text, additional_info in self.errors[line]:
                        error_message = self.error_messages.get(error_type, "Unknown error")
                        
                        # Format text for unclosed comments
                        if error_type == ErrorType.UNCLOSED_COMMENT and len(text) > 7:
                            text = text[:7] + "..."
                        
                        error_text = f"({text}, {error_message})"
                        if additional_info:
                            error_text += f" - {additional_info}"
                        
                        f.write(f" {error_text}")
                    f.write("\n")
        except IOError as e:
            logger.error(f"Error writing to error file {self.error_file_path}: {e}")
            raise CompilerError(f"Could not write to error file: {e}")
    
    def clear(self) -> None:
        """Clear all errors."""
        self.errors.clear() 
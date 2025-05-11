"""
Lexical error handling for the lexer phase.
"""
from typing import Optional

from src.common.error_handler import ErrorHandler, ErrorType, CompilerError


class LexicalErrorHandler(ErrorHandler):
    """
    Specialized error handler for lexical errors.
    """
    
    def __init__(self, error_file_path: str = "lexical_errors.txt"):
        """
        Initialize the lexical error handler.
        
        Args:
            error_file_path: Path to the lexical error output file
        """
        super().__init__(error_file_path)
    
    def add_invalid_number(self, line: int, text: str) -> None:
        """
        Add an invalid number error.
        
        Args:
            line: The line number where the error occurred
            text: The text that caused the error
        """
        self.add_error(line, ErrorType.INVALID_NUMBER, text)
    
    def add_invalid_input(self, line: int, text: str) -> None:
        """
        Add an invalid input error.
        
        Args:
            line: The line number where the error occurred
            text: The text that caused the error
        """
        self.add_error(line, ErrorType.INVALID_INPUT, text)
    
    def add_unmatched_comment(self, line: int, text: str) -> None:
        """
        Add an unmatched comment error.
        
        Args:
            line: The line number where the error occurred
            text: The text that caused the error
        """
        self.add_error(line, ErrorType.UNMATCHED_COMMENT, text)
    
    def add_unclosed_comment(self, line: int, text: str) -> None:
        """
        Add an unclosed comment error.
        
        Args:
            line: The line number where the error occurred
            text: The text that caused the error
        """
        self.add_error(line, ErrorType.UNCLOSED_COMMENT, text)
    
    def write_to_file(self) -> None:
        """Write lexical errors to the output file."""
        try:
            with open(self.error_file_path, 'w') as f:
                if not self.has_errors():
                    f.write("There is no lexical error.\n")
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
            raise CompilerError(f"Could not write to lexical error file: {e}") 
"""
Syntax error handling for the parser phase.
"""
from typing import Optional

from src.common.error_handler import ErrorHandler, ErrorType, CompilerError


class SyntaxErrorHandler(ErrorHandler):
    """
    Specialized error handler for syntax errors.
    """
    
    def __init__(self, error_file_path: str = "syntax_errors.txt"):
        """
        Initialize the syntax error handler.
        
        Args:
            error_file_path: Path to the syntax error output file
        """
        super().__init__(error_file_path)
    
    def add_unexpected_token(self, line: int, found: str, expected: Optional[str] = None) -> None:
        """
        Add an unexpected token error.
        
        Args:
            line: The line number where the error occurred
            found: The token that was found
            expected: The token that was expected (optional)
        """
        additional_info = f"Expected {expected}" if expected else None
        self.add_error(line, ErrorType.UNEXPECTED_TOKEN, found, additional_info)
    
    def add_missing_token(self, line: int, expected: str) -> None:
        """
        Add a missing token error.
        
        Args:
            line: The line number where the error occurred
            expected: The token that was expected
        """
        self.add_error(line, ErrorType.MISSING_TOKEN, expected)
    
    def write_to_file(self) -> None:
        """Write syntax errors to the output file."""
        try:
            with open(self.error_file_path, 'w') as f:
                if not self.has_errors():
                    f.write("There is no syntax error.\n")
                    return
                
                for line in sorted(self.errors.keys()):
                    f.write(f"{line}.\t")
                    for error_type, text, additional_info in self.errors[line]:
                        error_message = self.error_messages.get(error_type, "Unknown error")
                        
                        error_text = f"{error_message}"
                        if error_type == ErrorType.UNEXPECTED_TOKEN:
                            error_text = f"Unexpected {text}"
                            if additional_info:
                                error_text += f", {additional_info}"
                        elif error_type == ErrorType.MISSING_TOKEN:
                            error_text = f"Missing {text}"
                        
                        f.write(f" {error_text}")
                    f.write("\n")
        except IOError as e:
            raise CompilerError(f"Could not write to syntax error file: {e}") 
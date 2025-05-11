"""
Buffer module for efficient file reading with character-by-character access.
"""
from typing import Tuple, Optional, Union


class BufferedFileReader:
    """
    A buffered file reader that provides character-by-character access to a file.
    Maintains line count and position information for error reporting.
    """
    def __init__(self, file_path: str, buffer_size: int = 1024):
        """
        Initialize the buffered file reader.
        
        Args:
            file_path: Path to the input file
            buffer_size: Size of the buffer in characters
        """
        self.file_path = file_path
        self.buffer_size = buffer_size
        self.buffer = ''
        self.pos = 0
        self.line = 1
        self.eof = False
        
        try:
            self.file = open(file_path, 'r', encoding='utf-8')
            self._fill_buffer()
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {file_path}")
        except Exception as e:
            raise IOError(f"Error opening file {file_path}: {str(e)}")

    def _fill_buffer(self) -> None:
        """Fill the buffer with more characters from the file."""
        chunk = self.file.read(self.buffer_size)
        if chunk:
            self.buffer = chunk
            self.pos = 0
        else:
            self.eof = True
            self.buffer = ''
            self.pos = 0

    def has_next(self) -> bool:
        """Check if there are more characters to read."""
        if self.pos < len(self.buffer):
            return True
        if not self.eof:
            self._fill_buffer()
            return self.pos < len(self.buffer)
        return False

    def get_next_char(self) -> Union[Tuple[str, int], bool]:
        """
        Get the next character from the buffer.
        
        Returns:
            Tuple of (character, line_number) or False if at end of file
        """
        if not self.has_next():
            return False
        
        char = self.buffer[self.pos]
        current_line = self.line
        self.pos += 1

        if char == '\n':
            self.line += 1

        return char, current_line
    
    def check_next_char(self) -> Union[Tuple[str, int], bool]:
        """
        Check the next character without consuming it.
        
        Returns:
            Tuple of (character, line_number) or False if at end of file
        """
        if not self.has_next():
            return False
        
        char = self.buffer[self.pos]
        current_line = self.line
        return char, current_line

    def close(self) -> None:
        """Close the file handle."""
        self.file.close()
        
    def __enter__(self):
        """Support for context manager protocol."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure file is closed when exiting context."""
        self.close() 
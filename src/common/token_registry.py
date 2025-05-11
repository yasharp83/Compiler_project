"""
Token registry for managing and persisting collections of tokens.
"""
import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

from src.common.token import Token, TokenError


logger = logging.getLogger(__name__)


class TokenRegistry:
    """
    Registry for tokens identified during lexical analysis.
    Responsible for storing tokens by line and writing them to a file.
    """
    
    def __init__(self, file_path: str = "tokens.txt"):
        """
        Initialize a token registry.
        
        Args:
            file_path: Path to the output file
        """
        self.file_path = file_path
        self.tokens: Dict[int, List[Token]] = defaultdict(list)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the output file exists."""
        try:
            with open(self.file_path, 'a'):
                pass
        except IOError as e:
            logger.error(f"Error creating token file {self.file_path}: {e}")
            raise TokenError(f"Could not create token file: {e}")
    
    def add(self, token: Token) -> None:
        """
        Add a token to the registry.
        
        Args:
            token: The token to add
        """
        self.tokens[token.line].append(token)
    
    def get_tokens_by_line(self, line: int) -> List[Token]:
        """
        Get all tokens for a specific line.
        
        Args:
            line: The line number
            
        Returns:
            List of tokens on that line
        """
        return self.tokens.get(line, [])
    
    def get_all_tokens(self) -> List[Token]:
        """
        Get all tokens in order of line number and position.
        
        Returns:
            Flattened list of all tokens
        """
        result = []
        for line in sorted(self.tokens.keys()):
            result.extend(self.tokens[line])
        return result
    
    def write_to_file(self) -> None:
        """Write all tokens to the output file."""
        try:
            with open(self.file_path, 'w') as f:
                for line in sorted(self.tokens.keys()):
                    f.write(f"{line}.\t")
                    for token in self.tokens[line]:
                        f.write(f" {token}")
                    f.write("\n")
        except IOError as e:
            logger.error(f"Error writing to token file {self.file_path}: {e}")
            raise TokenError(f"Could not write to token file: {e}")
    
    def read_from_file(self, file_path: Optional[str] = None) -> None:
        """
        Read tokens from a file formatted as:
        line_num.    (token_type, token_lexeme) (token_type, token_lexeme) ...
        
        Args:
            file_path: Path to the input file, defaults to self.file_path
        """
        if file_path is None:
            file_path = self.file_path
        
        self.tokens.clear()
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    parts = line.strip().split('\t')
                    if len(parts) < 2:
                        logger.warning(f"Skipping malformed line: {line.strip()}")
                        continue
                    
                    try:
                        line_num = int(parts[0].rstrip('.'))
                        tokens_str = parts[1].strip()
                        
                        # Use regex to parse tokens properly
                        token_pattern = r'\(\s*([^,]+)\s*,\s*([^)]*)\s*\)'
                        for match in re.finditer(token_pattern, tokens_str):
                            token_type = match.group(1).strip()
                            token_lexeme = match.group(2).strip()
                            
                            # Remove quotes if they were added
                            if token_lexeme.startswith('"') and token_lexeme.endswith('"'):
                                token_lexeme = token_lexeme[1:-1]
                                
                            token = Token(type=token_type, lexeme=token_lexeme, line=line_num)
                            self.tokens[line_num].append(token)
                    except Exception as e:
                        logger.error(f"Error parsing line: {line.strip()}, error: {e}")
        except IOError as e:
            logger.error(f"Error reading token file {file_path}: {e}")
            raise TokenError(f"Could not read token file: {e}")
            
    def clear(self) -> None:
        """Clear all tokens from the registry."""
        self.tokens.clear() 
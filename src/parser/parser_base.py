"""
Base parser class for syntactic analysis.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any, Union

from src.common.token import Token
from src.common.token_registry import TokenRegistry
from src.common.symbol_table import SymbolTable, Symbol
from src.parser.syntax_errors import SyntaxErrorHandler
from src.parser.parse_tree import ParseTreeNode, ParseTree


logger = logging.getLogger(__name__)


class ParserBase(ABC):
    """
    Abstract base class for parsers.
    Provides common functionality for different parser implementations.
    """
    
    def __init__(
        self,
        tokens: List[Token],
        symbol_table: SymbolTable,
        syntax_errors_file_path: str = "syntax_errors.txt",
        parse_tree_file_path: str = "parse_tree.txt"
    ):
        """
        Initialize the parser.
        
        Args:
            tokens: List of tokens to parse
            symbol_table: Symbol table from lexical analysis
            syntax_errors_file_path: Path to the syntax errors output file
            parse_tree_file_path: Path to the parse tree output file
        """
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.syntax_errors_file_path = syntax_errors_file_path
        self.parse_tree_file_path = parse_tree_file_path
        
        # Initialize current token position
        self.current_token_index = 0
        
        # Initialize error handler
        self.error_handler = SyntaxErrorHandler(syntax_errors_file_path)
        
        # Initialize parse tree
        self.parse_tree = ParseTree(parse_tree_file_path)
    
    def get_current_token(self) -> Optional[Token]:
        """
        Get the current token.
        
        Returns:
            The current token or None if at the end of the token list
        """
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None
    
    def get_next_token(self) -> Optional[Token]:
        """
        Get the next token and advance the position.
        
        Returns:
            The next token or None if at the end of the token list
        """
        token = self.get_current_token()
        if token:
            self.current_token_index += 1
        return token
    
    def peek_token(self, offset: int = 0) -> Optional[Token]:
        """
        Peek at a token without advancing the position.
        
        Args:
            offset: Number of tokens ahead to peek (0 = current)
            
        Returns:
            The token at the specified offset or None if out of bounds
        """
        index = self.current_token_index + offset
        if 0 <= index < len(self.tokens):
            return self.tokens[index]
        return None
    
    def match(self, expected_type: str, expected_lexeme: Optional[str] = None) -> Optional[Token]:
        """
        Check if the current token matches the expected type and lexeme,
        and advance if it does.
        
        Args:
            expected_type: Expected token type
            expected_lexeme: Expected token lexeme (optional)
            
        Returns:
            The matched token if successful, None otherwise
        """
        token = self.get_current_token()
        
        if token and token.type == expected_type:
            if expected_lexeme is None or token.lexeme == expected_lexeme:
                return self.get_next_token()
        
        return None
    
    def expect(
        self, 
        expected_type: str, 
        expected_lexeme: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[Token]:
        """
        Expect a token of a certain type and optionally lexeme.
        If the current token doesn't match, add an error.
        
        Args:
            expected_type: Expected token type
            expected_lexeme: Expected token lexeme (optional)
            error_message: Custom error message (optional)
            
        Returns:
            The matched token if successful, None otherwise
        """
        token = self.match(expected_type, expected_lexeme)
        
        if token:
            return token
        
        # Get the actual token for better error reporting
        actual_token = self.get_current_token()
        
        # Create error message if not provided
        if not error_message:
            if actual_token:
                message = f"Expected {expected_type}"
                if expected_lexeme:
                    message += f" '{expected_lexeme}'"
                message += f", got {actual_token.type} '{actual_token.lexeme}'"
            else:
                message = f"Expected {expected_type}"
                if expected_lexeme:
                    message += f" '{expected_lexeme}'"
                message += ", but reached end of input"
        else:
            message = error_message
        
        # Add the error
        if actual_token:
            self.error_handler.add_unexpected_token(
                actual_token.line,
                actual_token.lexeme,
                f"{expected_type} '{expected_lexeme}'" if expected_lexeme else expected_type
            )
        else:
            # At end of input, use the last token's line
            line = self.tokens[-1].line if self.tokens else 1
            self.error_handler.add_missing_token(line, expected_type)
        
        return None
    
    def add_node_to_parse_tree(self, node_name: str, level: int) -> ParseTreeNode:
        """
        Add a node to the parse tree.
        
        Args:
            node_name: Name of the node
            level: Indentation level
            
        Returns:
            The created parse tree node
        """
        node = ParseTreeNode(name=node_name, level=level)
        self.parse_tree.add_node(node)
        return node
    
    def write_output_files(self) -> None:
        """Write parse tree and syntax errors to output files."""
        # Write syntax errors
        self.error_handler.write_to_file()
        
        # Write parse tree
        self.parse_tree.write_to_file()
    
    @abstractmethod
    def parse(self) -> ParseTree:
        """
        Parse the tokens and build a parse tree.
        Must be implemented by derived classes.
        
        Returns:
            The completed parse tree
        """
        pass 
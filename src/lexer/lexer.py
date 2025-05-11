"""
Main lexer module for lexical analysis.
"""
import logging
from typing import Optional, List

from src.common.token import Token
from src.common.token_registry import TokenRegistry
from src.common.symbol_table import SymbolTable
from src.lexer.lexical_errors import LexicalErrorHandler
from src.lexer.dfa import DFA
from src.lexer.dfa_builder import build_dfa
from src.lexer.token_scanner import TokenScanner
from src.utils.buffer import BufferedFileReader


logger = logging.getLogger(__name__)


class Lexer:
    """
    Lexical analyzer for breaking source code into tokens.
    Follows the Single Responsibility Principle by delegating
    specialized tasks to dedicated components.
    """
    
    def __init__(
        self,
        input_file_path: str = "input.txt",
        tokens_file_path: str = "tokens.txt",
        lexical_errors_file_path: str = "lexical_errors.txt",
        symbol_table_file_path: str = "symbol_table.txt"
    ):
        """
        Initialize the lexer.
        
        Args:
            input_file_path: Path to the input source code file
            tokens_file_path: Path to the output tokens file
            lexical_errors_file_path: Path to the output lexical errors file
            symbol_table_file_path: Path to the output symbol table file
        """
        self.input_file_path = input_file_path
        self.tokens_file_path = tokens_file_path
        self.lexical_errors_file_path = lexical_errors_file_path
        self.symbol_table_file_path = symbol_table_file_path
        
        # Initialize components
        self.buffer = None
        self.dfa = None
        self.token_registry = None
        self.symbol_table = None
        self.error_handler = None
        self.scanner = None
        
        # Initialize token list
        self.tokens: List[Token] = []
    
    def initialize(self) -> None:
        """Initialize all components of the lexer."""
        try:
            # Create components
            self.buffer = BufferedFileReader(self.input_file_path)
            self.dfa = build_dfa()
            self.token_registry = TokenRegistry(self.tokens_file_path)
            self.symbol_table = SymbolTable(self.symbol_table_file_path)
            self.error_handler = LexicalErrorHandler(self.lexical_errors_file_path)
            
            # Create scanner
            self.scanner = TokenScanner(
                buffer=self.buffer,
                dfa=self.dfa,
                token_registry=self.token_registry,
                symbol_table=self.symbol_table,
                error_handler=self.error_handler
            )
        except Exception as e:
            logger.error(f"Error initializing lexer: {e}")
            raise
    
    def tokenize(self) -> List[Token]:
        """
        Tokenize the input file.
        
        Returns:
            List of tokens
        """
        if not self.scanner:
            self.initialize()
        
        self.tokens = []
        
        try:
            # Continuously get tokens until None is returned
            while True:
                token = self.scanner.get_next_token()
                if token is None:
                    break
                if token.type != "WHITE":  # Skip whitespace tokens
                    self.tokens.append(token)
        except Exception as e:
            logger.error(f"Error during tokenization: {e}")
            raise
        
        return self.tokens
    
    def write_output_files(self) -> None:
        """Write the results to output files."""
        try:
            # Write tokens
            self.token_registry.write_to_file()
            
            # Write symbol table
            self.symbol_table.write_to_file()
            
            # Write lexical errors
            self.error_handler.write_to_file()
        except Exception as e:
            logger.error(f"Error writing output files: {e}")
            raise
    
    def analyze(self) -> List[Token]:
        """
        Perform lexical analysis on the input file.
        
        Returns:
            List of tokens
        """
        try:
            # Initialize components
            self.initialize()
            
            # Tokenize the input
            tokens = self.tokenize()
            
            # Write output files
            self.write_output_files()
            
            # Close buffer
            if self.buffer:
                self.buffer.close()
            
            return tokens
        except Exception as e:
            logger.error(f"Error during lexical analysis: {e}")
            raise


def analyze(
    input_file_path: str = "input.txt",
    tokens_file_path: str = "tokens.txt",
    lexical_errors_file_path: str = "lexical_errors.txt",
    symbol_table_file_path: str = "symbol_table.txt"
) -> List[Token]:
    """
    Perform lexical analysis on an input file.
    
    Args:
        input_file_path: Path to the input source code file
        tokens_file_path: Path to the output tokens file
        lexical_errors_file_path: Path to the output lexical errors file
        symbol_table_file_path: Path to the output symbol table file
        
    Returns:
        List of tokens
    """
    lexer = Lexer(
        input_file_path=input_file_path,
        tokens_file_path=tokens_file_path,
        lexical_errors_file_path=lexical_errors_file_path,
        symbol_table_file_path=symbol_table_file_path
    )
    
    return lexer.analyze() 
"""
Parser module for syntactic analysis.
"""
import logging
from typing import List, Optional

from src.common.token import Token
from src.common.symbol_table import SymbolTable
from src.parser.recursive_descent_parser import RecursiveDescentParser
from src.parser.parse_tree import ParseTree


logger = logging.getLogger(__name__)


def parse(
    tokens: List[Token],
    symbol_table: SymbolTable,
    syntax_errors_file_path: str = "syntax_errors.txt", 
    parse_tree_file_path: str = "parse_tree.txt"
) -> ParseTree:
    """
    Parse a list of tokens and build a parse tree.
    
    Args:
        tokens: List of tokens from lexical analysis
        symbol_table: Symbol table from lexical analysis
        syntax_errors_file_path: Path to the syntax errors output file
        parse_tree_file_path: Path to the parse tree output file
        
    Returns:
        The completed parse tree
    """
    # Create a recursive descent parser
    parser = RecursiveDescentParser(
        tokens=tokens,
        symbol_table=symbol_table,
        syntax_errors_file_path=syntax_errors_file_path,
        parse_tree_file_path=parse_tree_file_path
    )
    
    # Parse the tokens
    return parser.parse()


class Parser:
    """
    Main parser class that orchestrates syntactic analysis.
    This class provides a facade for the parser module.
    """
    
    def __init__(
        self,
        tokens_file_path: str = "tokens.txt",
        symbol_table_file_path: str = "symbol_table.txt",
        syntax_errors_file_path: str = "syntax_errors.txt",
        parse_tree_file_path: str = "parse_tree.txt"
    ):
        """
        Initialize the parser.
        
        Args:
            tokens_file_path: Path to the tokens file from lexical analysis
            symbol_table_file_path: Path to the symbol table file from lexical analysis
            syntax_errors_file_path: Path to the syntax errors output file
            parse_tree_file_path: Path to the parse tree output file
        """
        self.tokens_file_path = tokens_file_path
        self.symbol_table_file_path = symbol_table_file_path
        self.syntax_errors_file_path = syntax_errors_file_path
        self.parse_tree_file_path = parse_tree_file_path
        
        # Initialize components
        self.tokens = []
        self.symbol_table = None
        self.parse_tree = None
    
    def load_tokens(self) -> List[Token]:
        """
        Load tokens from the tokens file.
        
        Returns:
            List of tokens
        """
        from src.common.token_registry import TokenRegistry
        
        # Create a token registry and load tokens
        token_registry = TokenRegistry(self.tokens_file_path)
        token_registry.read_from_file()
        
        # Get all tokens
        self.tokens = token_registry.get_all_tokens()
        
        return self.tokens
    
    def load_symbol_table(self) -> SymbolTable:
        """
        Load the symbol table from the symbol table file.
        
        Returns:
            Symbol table
        """
        # Create a symbol table and load symbols
        self.symbol_table = SymbolTable(self.symbol_table_file_path)
        self.symbol_table.read_from_file()
        
        return self.symbol_table
    
    def analyze(self, tokens: Optional[List[Token]] = None, symbol_table: Optional[SymbolTable] = None) -> ParseTree:
        """
        Perform syntactic analysis.
        
        Args:
            tokens: List of tokens (optional, will be loaded from file if not provided)
            symbol_table: Symbol table (optional, will be loaded from file if not provided)
            
        Returns:
            The completed parse tree
        """
        # Load tokens if not provided
        if not tokens:
            tokens = self.load_tokens()
        
        # Load symbol table if not provided
        if not symbol_table:
            symbol_table = self.load_symbol_table()
        
        # Parse the tokens
        self.parse_tree = parse(
            tokens=tokens,
            symbol_table=symbol_table,
            syntax_errors_file_path=self.syntax_errors_file_path,
            parse_tree_file_path=self.parse_tree_file_path
        )
        
        return self.parse_tree 
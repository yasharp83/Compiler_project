"""
Token scanner for lexical analysis.
"""
from typing import Optional, Tuple, Union, List

from src.common.token import Token
from src.common.token_registry import TokenRegistry
from src.common.symbol_table import SymbolTable
from src.common.language_specs import is_keyword
from src.lexer.lexical_errors import LexicalErrorHandler
from src.lexer.dfa import DFA, TokenClass
from src.utils.buffer import BufferedFileReader


class TokenScanner:
    """
    Scanner for recognizing tokens in source code.
    """
    
    def __init__(
        self,
        buffer: BufferedFileReader,
        dfa: DFA,
        token_registry: TokenRegistry,
        symbol_table: SymbolTable,
        error_handler: LexicalErrorHandler
    ):
        """
        Initialize the token scanner.
        
        Args:
            buffer: Input buffer
            dfa: DFA for token recognition
            token_registry: Registry for storing tokens
            symbol_table: Symbol table for storing identifiers
            error_handler: Error handler for lexical errors
        """
        self.buffer = buffer
        self.dfa = dfa
        self.token_registry = token_registry
        self.symbol_table = symbol_table
        self.error_handler = error_handler
    
    def get_next_token(self) -> Optional[Token]:
        """
        Get the next token from the input buffer.
        
        Returns:
            The next token, or None if at the end of input
        """
        # Reset the DFA
        self.dfa.reset()
        
        # Check if we have characters to read
        if not self.buffer.has_next():
            return None
        
        # Start building the token
        token_text = ""
        start_line = self.buffer.check_next_char()[1]
        
        while True:
            # Check if we've reached the end of the buffer
            if not self.buffer.has_next():
                # Check if we have an error
                current_state = self.dfa.get_current_state()
                if current_state.error_type:
                    self._handle_error(current_state.error_type, token_text, start_line)
                    return None
                
                # Check if we have a valid token
                if is_keyword(token_text):
                    return self._create_and_register_token("KEYWORD", token_text, start_line)
                
                # Determine token type from current state
                token_type = self._get_token_type_from_state(current_state.token_class)
                return self._create_and_register_token(token_type, token_text, start_line)
            
            # Peek at the next character
            char, line = self.buffer.check_next_char()
            
            # Check what state we would transition to
            next_state = self.dfa.get_next_state(char)
            
            # Handle error states
            if next_state.is_trap and next_state.error_type:
                # Consume the character and add it to the token
                self.dfa.transition(char)
                self.buffer.get_next_char()
                token_text += char
                
                # Register the error
                self._handle_error(next_state.error_type, token_text, start_line)
                
                # Continue scanning for the next token
                return self.get_next_token()
            
            # Handle accepting states when next state is a trap
            current_state = self.dfa.get_current_state()
            if next_state.is_trap and current_state.is_accept:
                # If we're in a comment, skip it and continue
                if current_state.token_class == TokenClass.COMMENT:
                    # Consume the comment token and continue scanning
                    return self.get_next_token()
                
                # For other token types, return the current token
                if is_keyword(token_text):
                    return self._create_and_register_token("KEYWORD", token_text, start_line)
                
                # Determine token type from current state
                token_type = self._get_token_type_from_state(current_state.token_class)
                return self._create_and_register_token(token_type, token_text, start_line)
            
            # Transition to the next state
            self.dfa.transition(char)
            self.buffer.get_next_char()
            token_text += char
    
    def _get_token_type_from_state(self, token_class: TokenClass) -> str:
        """
        Convert a TokenClass to a string token type.
        
        Args:
            token_class: The token class
            
        Returns:
            String representation of the token type
        """
        if token_class == TokenClass.ID:
            return "ID"
        elif token_class == TokenClass.NUMBER:
            return "NUM"
        elif token_class == TokenClass.SYMBOL:
            return "SYMBOL"
        elif token_class == TokenClass.WHITESPACE:
            return "WHITE"
        elif token_class == TokenClass.COMMENT:
            return "COMMENT"
        else:
            return "UNKNOWN"
    
    def _create_and_register_token(self, token_type: str, lexeme: str, line: int) -> Token:
        """
        Create a token and register it.
        
        Args:
            token_type: The token type
            lexeme: The token lexeme
            line: The line number
            
        Returns:
            The created token
        """
        token = Token(type=token_type, lexeme=lexeme, line=line)
        
        # Register the token if it's not whitespace
        if token_type != "WHITE":
            self.token_registry.add(token)
        
        # Add to symbol table if ID or KEYWORD
        if token_type in ("ID", "KEYWORD"):
            self.symbol_table.add(name=lexeme)
        
        return token
    
    def _handle_error(self, error_type: str, text: str, line: int) -> None:
        """
        Handle a lexical error.
        
        Args:
            error_type: The type of error
            text: The text that caused the error
            line: The line number
        """
        if error_type == "ERROR_INVALID_NUMBER":
            self.error_handler.add_invalid_number(line, text)
        elif error_type == "ERROR_INVALID_INPUT":
            self.error_handler.add_invalid_input(line, text)
        elif error_type == "ERROR_UNMATCHED_COMMENT":
            self.error_handler.add_unmatched_comment(line, text)
        elif error_type == "ERROR_UNCLOSED_COMMENT":
            self.error_handler.add_unclosed_comment(line, text) 
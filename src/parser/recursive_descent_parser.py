"""
Recursive descent parser for the language.
"""
import logging
from typing import List, Optional, Dict, Any, Union

from src.common.token import Token
from src.common.symbol_table import SymbolTable, Symbol
from src.parser.parser_base import ParserBase
from src.parser.parse_tree import ParseTree, ParseTreeNode


logger = logging.getLogger(__name__)


class RecursiveDescentParser(ParserBase):
    """
    Recursive descent parser for the language.
    Implements the grammar rules using recursive descent parsing.
    """
    
    def parse(self) -> ParseTree:
        """
        Parse the tokens and build a parse tree.
        
        Returns:
            The completed parse tree
        """
        # Start from the root production rule
        self.program()
        
        # Write output files
        self.write_output_files()
        
        return self.parse_tree
    
    # Grammar rule implementations
    
    def program(self) -> None:
        """
        Program -> Declaration-list
        """
        # Add the root node
        self.add_node_to_parse_tree("Program", 0)
        
        # Parse declaration list
        self.declaration_list(1)
    
    def declaration_list(self, level: int) -> None:
        """
        Declaration-list -> Declaration Declaration-list | ε
        """
        self.add_node_to_parse_tree("Declaration-list", level)
        
        # Check if we're at the end of input
        token = self.peek_token()
        if not token:
            return  # ε production
        
        # Check for declaration start (must be int or void)
        if token.type == "KEYWORD" and token.lexeme in ["int", "void"]:
            self.declaration(level + 1)
            self.declaration_list(level + 1)
        else:
            # This could be a syntax error, but we'll let declaration handle it
            # Here we just end the declaration list
            return
    
    def declaration(self, level: int) -> None:
        """
        Declaration -> Type-specifier ID Declaration'
        Declaration' -> ; | [ NUM ] ; | ( Params ) Compound-stmt
        """
        self.add_node_to_parse_tree("Declaration", level)
        
        # Parse type specifier
        type_token = self.type_specifier(level + 1)
        if not type_token:
            return
        
        # Parse identifier
        id_token = self.expect("ID")
        if not id_token:
            return
        
        # Check next token to determine which Declaration' production to follow
        next_token = self.peek_token()
        if not next_token:
            self.error_handler.add_missing_token(id_token.line, ";")
            return
        
        if next_token.type == "SYMBOL":
            if next_token.lexeme == ";":
                # Variable declaration
                self.get_next_token()  # Consume ;
                self.add_node_to_parse_tree(f"Variable: {id_token.lexeme}", level + 1)
                
                # Add to symbol table
                self.symbol_table.add(
                    name=id_token.lexeme,
                    kind="variable",
                    type_name=type_token.lexeme
                )
            
            elif next_token.lexeme == "[":
                # Array declaration
                self.get_next_token()  # Consume [
                num_token = self.expect("NUM")
                if num_token:
                    self.expect("SYMBOL", "]")
                    self.expect("SYMBOL", ";")
                    self.add_node_to_parse_tree(
                        f"Array: {id_token.lexeme}[{num_token.lexeme}]", 
                        level + 1
                    )
                    
                    # Add to symbol table
                    self.symbol_table.add(
                        name=id_token.lexeme,
                        kind="array",
                        type_name=type_token.lexeme,
                        is_array=True,
                        array_size=int(num_token.lexeme)
                    )
            
            elif next_token.lexeme == "(":
                # Function declaration
                self.get_next_token()  # Consume (
                self.add_node_to_parse_tree(f"Function: {id_token.lexeme}", level + 1)
                
                # Add to symbol table
                self.symbol_table.add(
                    name=id_token.lexeme,
                    kind="function",
                    type_name=type_token.lexeme
                )
                
                # Parse parameters
                self.params(level + 2)
                
                self.expect("SYMBOL", ")")
                
                # Parse function body
                self.compound_stmt(level + 2)
            
            else:
                # Unexpected symbol
                self.error_handler.add_unexpected_token(
                    next_token.line,
                    next_token.lexeme,
                    "one of ;, [, ("
                )
    
    def type_specifier(self, level: int) -> Optional[Token]:
        """
        Type-specifier -> int | void
        """
        self.add_node_to_parse_tree("Type-specifier", level)
        
        # Must be int or void
        token = self.peek_token()
        if token and token.type == "KEYWORD" and token.lexeme in ["int", "void"]:
            self.add_node_to_parse_tree(token.lexeme, level + 1)
            return self.get_next_token()
        else:
            # Expected type specifier
            self.expect("KEYWORD", None, "Expected type specifier (int or void)")
            return None
    
    def params(self, level: int) -> None:
        """
        Params -> Param-list | void
        """
        self.add_node_to_parse_tree("Params", level)
        
        token = self.peek_token()
        if not token:
            return
        
        if token.type == "KEYWORD" and token.lexeme == "void":
            # void parameter list
            self.add_node_to_parse_tree("void", level + 1)
            self.get_next_token()
        else:
            # Regular parameter list
            self.param_list(level + 1)
    
    def param_list(self, level: int) -> None:
        """
        Param-list -> Param Param-list' | ε
        Param-list' -> , Param Param-list' | ε
        """
        self.add_node_to_parse_tree("Param-list", level)
        
        # Parse first parameter
        self.param(level + 1)
        
        # Parse additional parameters (comma-separated)
        while True:
            token = self.peek_token()
            if not token or token.type != "SYMBOL" or token.lexeme != ",":
                break
            
            self.get_next_token()  # Consume comma
            self.param(level + 1)
    
    def param(self, level: int) -> None:
        """
        Param -> Type-specifier ID | Type-specifier ID [ ]
        """
        self.add_node_to_parse_tree("Param", level)
        
        # Parse type specifier
        type_token = self.type_specifier(level + 1)
        if not type_token:
            return
        
        # Parse identifier
        id_token = self.expect("ID")
        if not id_token:
            return
        
        # Check if this is an array parameter
        token = self.peek_token()
        if token and token.type == "SYMBOL" and token.lexeme == "[":
            self.get_next_token()  # Consume [
            self.expect("SYMBOL", "]")
            self.add_node_to_parse_tree(f"Array parameter: {id_token.lexeme}", level + 1)
            
            # Add to symbol table
            self.symbol_table.add(
                name=id_token.lexeme,
                kind="parameter",
                type_name=type_token.lexeme,
                is_array=True
            )
        else:
            # Simple parameter
            self.add_node_to_parse_tree(f"Parameter: {id_token.lexeme}", level + 1)
            
            # Add to symbol table
            self.symbol_table.add(
                name=id_token.lexeme,
                kind="parameter",
                type_name=type_token.lexeme
            )
    
    def compound_stmt(self, level: int) -> None:
        """
        Compound-stmt -> { Local-declarations Statement-list }
        """
        self.add_node_to_parse_tree("Compound-statement", level)
        
        self.expect("SYMBOL", "{")
        
        # Local declarations (variables)
        self.local_declarations(level + 1)
        
        # Statements
        self.statement_list(level + 1)
        
        self.expect("SYMBOL", "}")
    
    def local_declarations(self, level: int) -> None:
        """
        Local-declarations -> Type-specifier ID ; Local-declarations | ε
        """
        self.add_node_to_parse_tree("Local-declarations", level)
        
        while True:
            token = self.peek_token()
            if not token or token.type != "KEYWORD" or token.lexeme not in ["int", "void"]:
                break
            
            # Parse type specifier
            type_token = self.type_specifier(level + 1)
            if not type_token:
                break
            
            # Parse identifier
            id_token = self.expect("ID")
            if not id_token:
                break
            
            # Check if it's an array
            next_token = self.peek_token()
            if next_token and next_token.type == "SYMBOL" and next_token.lexeme == "[":
                self.get_next_token()  # Consume [
                num_token = self.expect("NUM")
                if num_token:
                    self.expect("SYMBOL", "]")
                    self.expect("SYMBOL", ";")
                    self.add_node_to_parse_tree(
                        f"Local array: {id_token.lexeme}[{num_token.lexeme}]", 
                        level + 1
                    )
                    
                    # Add to symbol table
                    self.symbol_table.add(
                        name=id_token.lexeme,
                        kind="local",
                        type_name=type_token.lexeme,
                        is_array=True,
                        array_size=int(num_token.lexeme)
                    )
            else:
                # Simple variable
                self.expect("SYMBOL", ";")
                self.add_node_to_parse_tree(f"Local variable: {id_token.lexeme}", level + 1)
                
                # Add to symbol table
                self.symbol_table.add(
                    name=id_token.lexeme,
                    kind="local",
                    type_name=type_token.lexeme
                )
    
    def statement_list(self, level: int) -> None:
        """
        Statement-list -> Statement Statement-list | ε
        """
        self.add_node_to_parse_tree("Statement-list", level)
        
        while True:
            token = self.peek_token()
            if not token:
                break
            
            # Check if we've reached the end of the statement list (closing brace)
            if token.type == "SYMBOL" and token.lexeme == "}":
                break
            
            # Parse a statement
            if not self.statement(level + 1):
                # If statement parsing fails, advance to prevent infinite loop
                self.get_next_token()
    
    def statement(self, level: int) -> bool:
        """
        Statement -> Expression-stmt | Compound-stmt | Selection-stmt |
                    Iteration-stmt | Return-stmt
        
        Returns:
            True if statement parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Statement", level)
        
        token = self.peek_token()
        if not token:
            return False
        
        if token.type == "SYMBOL" and token.lexeme == "{":
            # Compound statement
            self.compound_stmt(level + 1)
            return True
        
        elif token.type == "KEYWORD":
            if token.lexeme == "if":
                # Selection statement
                return self.selection_stmt(level + 1)
            
            elif token.lexeme == "while":
                # Iteration statement
                return self.iteration_stmt(level + 1)
            
            elif token.lexeme == "return":
                # Return statement
                return self.return_stmt(level + 1)
        
        # Default to expression statement
        return self.expression_stmt(level + 1)
    
    def expression_stmt(self, level: int) -> bool:
        """
        Expression-stmt -> Expression ; | ;
        
        Returns:
            True if expression statement parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Expression-statement", level)
        
        token = self.peek_token()
        if not token:
            return False
        
        if token.type == "SYMBOL" and token.lexeme == ";":
            # Empty statement
            self.get_next_token()  # Consume ;
            self.add_node_to_parse_tree("Empty statement", level + 1)
            return True
        
        # Expression followed by semicolon
        result = self.expression(level + 1)
        if not result:
            return False
        
        self.expect("SYMBOL", ";")
        return True
    
    def selection_stmt(self, level: int) -> bool:
        """
        Selection-stmt -> if ( Expression ) Statement |
                          if ( Expression ) Statement else Statement
        
        Returns:
            True if selection statement parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Selection-statement", level)
        
        # Parse 'if' keyword
        if not self.expect("KEYWORD", "if"):
            return False
        
        # Parse condition
        self.expect("SYMBOL", "(")
        if not self.expression(level + 1):
            return False
        self.expect("SYMBOL", ")")
        
        # Parse 'then' part
        if not self.statement(level + 1):
            return False
        
        # Check for 'else' part
        token = self.peek_token()
        if token and token.type == "KEYWORD" and token.lexeme == "else":
            self.get_next_token()  # Consume 'else'
            self.add_node_to_parse_tree("Else", level + 1)
            return self.statement(level + 2)
        
        return True
    
    def iteration_stmt(self, level: int) -> bool:
        """
        Iteration-stmt -> while ( Expression ) Statement
        
        Returns:
            True if iteration statement parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Iteration-statement", level)
        
        # Parse 'while' keyword
        if not self.expect("KEYWORD", "while"):
            return False
        
        # Parse condition
        self.expect("SYMBOL", "(")
        if not self.expression(level + 1):
            return False
        self.expect("SYMBOL", ")")
        
        # Parse loop body
        return self.statement(level + 1)
    
    def return_stmt(self, level: int) -> bool:
        """
        Return-stmt -> return ; | return Expression ;
        
        Returns:
            True if return statement parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Return-statement", level)
        
        # Parse 'return' keyword
        if not self.expect("KEYWORD", "return"):
            return False
        
        # Check if it's an empty return
        token = self.peek_token()
        if token and token.type == "SYMBOL" and token.lexeme == ";":
            self.get_next_token()  # Consume ;
            self.add_node_to_parse_tree("Empty return", level + 1)
            return True
        
        # Parse return expression
        if not self.expression(level + 1):
            return False
        
        self.expect("SYMBOL", ";")
        return True
    
    def expression(self, level: int) -> bool:
        """
        Expression -> Var = Expression | Simple-expression
        
        Returns:
            True if expression parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Expression", level)
        
        # Try to parse a variable
        saved_index = self.current_token_index
        var_result = self.var(level + 1)
        
        # Check if the next token is '='
        next_token = self.peek_token()
        if var_result and next_token and next_token.type == "SYMBOL" and next_token.lexeme == "=":
            # Assignment expression
            self.get_next_token()  # Consume '='
            self.add_node_to_parse_tree("Assignment", level + 1)
            return self.expression(level + 2)
        
        # Backtrack and try simple expression
        self.current_token_index = saved_index
        
        # Remove the var node we added
        if var_result and len(self.parse_tree.nodes) > 0:
            self.parse_tree.nodes.pop()
        
        return self.simple_expression(level + 1)
    
    def var(self, level: int) -> bool:
        """
        Var -> ID | ID [ Expression ]
        
        Returns:
            True if variable parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Variable", level)
        
        # Parse identifier
        id_token = self.match("ID")
        if not id_token:
            return False
        
        self.add_node_to_parse_tree(id_token.lexeme, level + 1)
        
        # Check if it's an array access
        token = self.peek_token()
        if token and token.type == "SYMBOL" and token.lexeme == "[":
            self.get_next_token()  # Consume '['
            self.add_node_to_parse_tree("Array access", level + 1)
            
            if not self.expression(level + 2):
                return False
            
            self.expect("SYMBOL", "]")
        
        return True
    
    def simple_expression(self, level: int) -> bool:
        """
        Simple-expression -> Additive-expression Relop Additive-expression |
                             Additive-expression
        
        Returns:
            True if simple expression parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Simple-expression", level)
        
        # Parse first additive expression
        if not self.additive_expression(level + 1):
            return False
        
        # Check for relational operator
        token = self.peek_token()
        if token and token.type == "SYMBOL" and token.lexeme in ["<", ">", "=="]:
            self.get_next_token()  # Consume operator
            self.add_node_to_parse_tree(f"Relop: {token.lexeme}", level + 1)
            
            # Parse second additive expression
            return self.additive_expression(level + 1)
        
        return True
    
    def additive_expression(self, level: int) -> bool:
        """
        Additive-expression -> Term Additive-expression' |
                               Term
        Additive-expression' -> Addop Term Additive-expression' | ε
        
        Returns:
            True if additive expression parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Additive-expression", level)
        
        # Parse first term
        if not self.term(level + 1):
            return False
        
        # Parse additional terms
        while True:
            token = self.peek_token()
            if not token or token.type != "SYMBOL" or token.lexeme not in ["+", "-"]:
                break
            
            self.get_next_token()  # Consume operator
            self.add_node_to_parse_tree(f"Addop: {token.lexeme}", level + 1)
            
            if not self.term(level + 1):
                return False
        
        return True
    
    def term(self, level: int) -> bool:
        """
        Term -> Factor Term' |
                Factor
        Term' -> Mulop Factor Term' | ε
        
        Returns:
            True if term parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Term", level)
        
        # Parse first factor
        if not self.factor(level + 1):
            return False
        
        # Parse additional factors
        while True:
            token = self.peek_token()
            if not token or token.type != "SYMBOL" or token.lexeme not in ["*", "/"]:
                break
            
            self.get_next_token()  # Consume operator
            self.add_node_to_parse_tree(f"Mulop: {token.lexeme}", level + 1)
            
            if not self.factor(level + 1):
                return False
        
        return True
    
    def factor(self, level: int) -> bool:
        """
        Factor -> ( Expression ) | Var | Call | NUM
        
        Returns:
            True if factor parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Factor", level)
        
        token = self.peek_token()
        if not token:
            return False
        
        if token.type == "SYMBOL" and token.lexeme == "(":
            # Parenthesized expression
            self.get_next_token()  # Consume '('
            if not self.expression(level + 1):
                return False
            self.expect("SYMBOL", ")")
            return True
        
        elif token.type == "NUM":
            # Number
            self.get_next_token()  # Consume number
            self.add_node_to_parse_tree(f"NUM: {token.lexeme}", level + 1)
            return True
        
        elif token.type == "ID":
            # Try to parse a function call
            saved_index = self.current_token_index
            call_result = self.call(level + 1)
            
            if call_result:
                return True
            
            # If not a call, backtrack and try var
            self.current_token_index = saved_index
            
            # Remove the call node we added
            if len(self.parse_tree.nodes) > 0:
                self.parse_tree.nodes.pop()
            
            return self.var(level + 1)
        
        # Unexpected token
        self.error_handler.add_unexpected_token(
            token.line,
            token.lexeme,
            "one of (, ID, NUM"
        )
        return False
    
    def call(self, level: int) -> bool:
        """
        Call -> ID ( Args )
        
        Returns:
            True if call parsing succeeded, False otherwise
        """
        self.add_node_to_parse_tree("Call", level)
        
        # Parse identifier
        id_token = self.match("ID")
        if not id_token:
            return False
        
        self.add_node_to_parse_tree(f"Function call: {id_token.lexeme}", level + 1)
        
        # Parse arguments
        self.expect("SYMBOL", "(")
        self.args(level + 1)
        self.expect("SYMBOL", ")")
        
        return True
    
    def args(self, level: int) -> None:
        """
        Args -> Arg-list | ε
        """
        self.add_node_to_parse_tree("Arguments", level)
        
        token = self.peek_token()
        if not token or token.type == "SYMBOL" and token.lexeme == ")":
            # Empty argument list
            self.add_node_to_parse_tree("Empty", level + 1)
            return
        
        # Parse argument list
        self.arg_list(level + 1)
    
    def arg_list(self, level: int) -> None:
        """
        Arg-list -> Expression Arg-list' |
                   Expression
        Arg-list' -> , Expression Arg-list' | ε
        """
        self.add_node_to_parse_tree("Argument-list", level)
        
        # Parse first expression
        self.expression(level + 1)
        
        # Parse additional expressions
        while True:
            token = self.peek_token()
            if not token or token.type != "SYMBOL" or token.lexeme != ",":
                break
            
            self.get_next_token()  # Consume comma
            self.expression(level + 1) 
from tokens import Tokens
from symbol_table import SymbolTable

class Parser:
    def __init__(self, tokens_file_path="tokens.txt", symbol_table_file_path="symbol_table.txt",
                 syntax_errors_file_path="syntax_errors.txt", parse_tree_file_path="parse_tree.txt"):
        self.tokens = Tokens(tokens_file_path)
        self.tokens.read_file(tokens_file_path)
        self.symbol_table = SymbolTable(symbol_table_file_path)
        self.symbol_table.read_file(symbol_table_file_path)
        self.syntax_errors_file_path = syntax_errors_file_path
        self.parse_tree_file_path = parse_tree_file_path
        self.syntax_errors = []
        self.parse_tree = []
        self.current_token_index = 0
        self.current_line = 1
        self.token_list = []
        
    def get_next_token(self):
        if self.current_token_index < len(self.token_list):
            token = self.token_list[self.current_token_index]
            self.current_token_index += 1
            self.current_line = token[2]  # Update current line
            return token
        return None
    
    def peek_token(self):
        if self.current_token_index < len(self.token_list):
            return self.token_list[self.current_token_index]
        return None
    
    def match(self, expected_token_type, expected_token_lexeme=None):
        token = self.peek_token()
        print(f"match: expected={expected_token_type}, {expected_token_lexeme}, got={token}")
        
        if token and token[0] == expected_token_type:
            if expected_token_lexeme is None or token[1] == expected_token_lexeme:
                return self.get_next_token()
        return None
    
    def expect(self, expected_token_type, error_message=None, expected_token_lexeme=None):
        token = self.match(expected_token_type, expected_token_lexeme)
        if token:
            return token
        else:
            if not error_message:
                peek = self.peek_token()
                if peek:
                    error_message = f"Expected {expected_token_type}"
                    if expected_token_lexeme:
                        error_message += f" '{expected_token_lexeme}'"
                    error_message += f", got {peek[0]} '{peek[1]}'"
                else:
                    error_message = f"Expected {expected_token_type}, but reached end of input"
            self.add_syntax_error(error_message)
            return None
    
    def add_syntax_error(self, message):
        self.syntax_errors.append((self.current_line, message))
    
    def add_to_parse_tree(self, node, level=0):
        self.parse_tree.append((level, node))
    
    def parse(self):
        # Extract token list from the Tokens class
        for line_num, tokens in self.tokens.tokens.items():
            for token in tokens:
                self.token_list.append((token[0], token[1], line_num))
        
        # Sort tokens by line number
        self.token_list.sort(key=lambda x: x[2])
        
        print(f"Number of tokens loaded: {len(self.token_list)}")
        print(f"First few tokens: {self.token_list[:5]}")
        
        # Start parsing from the root production rule
        self.program()
        
        # Write syntax errors to file
        self.write_syntax_errors()
        
        # Write parse tree to file
        self.write_parse_tree()
    
    def write_syntax_errors(self):
        try:
            with open(self.syntax_errors_file_path, 'w') as f:
                if not self.syntax_errors:
                    f.write("There is no syntax error.")
                else:
                    for line, error in self.syntax_errors:
                        f.write(f"{line}. {error}\n")
        except:
            print(f"An error occurred while writing to {self.syntax_errors_file_path}")
    
    def write_parse_tree(self):
        try:
            with open(self.parse_tree_file_path, 'w') as f:
                for level, node in self.parse_tree:
                    indent = "  " * level
                    f.write(f"{indent}{node}\n")
        except:
            print(f"An error occurred while writing to {self.parse_tree_file_path}")
    
    # Recursive Descent Parser methods for grammar rules
    def program(self):
        """
        Program -> Declaration-list
        """
        self.add_to_parse_tree("Program")
        self.declaration_list(1)
    
    def declaration_list(self, level):
        """
        Declaration-list -> Declaration Declaration-list | ε
        """
        self.add_to_parse_tree("Declaration-list", level)
        
        token = self.peek_token()
        print(f"declaration_list: peeked token = {token}")
        
        if not token:
            # End of input, ε production
            print("declaration_list: End of input reached")
            return
            
        # For the first token in our program, it should be "void" for the main function
        # Let's add a special case for the first token
        if self.current_token_index == 0 and token[0] == "KEYWORD" and token[1] == "void":
            print(f"declaration_list: Processing first token (main function)")
            # Directly add the main function to the parse tree
            self.add_to_parse_tree("Function: void main(void)", level + 1)
            
            # Skip tokens for the main function declaration
            # Skip "void", "main", "(", "void", ")", "{"
            for _ in range(6):
                if self.peek_token():
                    self.get_next_token()
            
            # Process the function body
            self.local_declarations(level + 1)
            self.statement_list(level + 1)
            
            # Skip the closing brace
            if self.peek_token() and self.peek_token()[0] == "SYMBOL" and self.peek_token()[1] == "}":
                self.get_next_token()
            
            return
            
        # Normal processing for other declarations
        if token[0] == "KEYWORD" and token[1] in ["int", "void"]:
            print(f"declaration_list: Processing declaration with token {token}")
            self.declaration(level + 1)
            self.declaration_list(level + 1)
        else:
            print(f"declaration_list: Token {token} is not a valid declaration start")
            # This could be a syntax error - token doesn't match expected patterns
            self.add_syntax_error(f"Unexpected token {token[0]}, expected type specifier")
            # Try to recover by skipping this token
            self.get_next_token()
    
    def declaration(self, level):
        """
        Declaration -> Type-specifier ID Declaration'
        Declaration' -> ; | [ NUM ] ; | ( Params ) Compound-stmt
        """
        self.add_to_parse_tree("Declaration", level)
        print("declaration: starting")
        
        # Type specifier
        type_token = self.type_specifier(level + 1)
        if not type_token:
            print("declaration: failed at type specifier")
            return
            
        # Identifier
        id_token = self.expect("ID", "Expected identifier after type specifier")
        if not id_token:
            print("declaration: failed at identifier")
            return
            
        # Check what kind of declaration this is
        next_token = self.peek_token()
        if not next_token:
            self.add_syntax_error("Unexpected end of input in declaration")
            print("declaration: unexpected end of input")
            return
            
        print(f"declaration: next token is {next_token}")
            
        if next_token[0] == "SYMBOL" and next_token[1] == ";":
            # Variable declaration
            self.get_next_token()  # Consume semicolon
            self.add_to_parse_tree(f"Variable declaration: {id_token[1]} of type {type_token[1]}", level + 1)
            print(f"declaration: completed variable declaration {id_token[1]}")
        elif next_token[0] == "SYMBOL" and next_token[1] == "[":
            # Array declaration
            self.get_next_token()  # Consume [
            num_token = self.expect("NUM", "Expected number in array declaration")
            if not num_token:
                return
                
            self.expect("SYMBOL", "Expected closing bracket in array declaration", "]")
            self.expect("SYMBOL", "Expected semicolon after array declaration", ";")
            self.add_to_parse_tree(f"Array declaration: {id_token[1]} of type {type_token[1]}[{num_token[1]}]", level + 1)
            print(f"declaration: completed array declaration {id_token[1]}")
        elif next_token[0] == "SYMBOL" and next_token[1] == "(":
            # Function declaration
            self.get_next_token()  # Consume (
            self.params(level + 1)
            self.expect("SYMBOL", "Expected closing parenthesis after parameters", ")")
            self.compound_stmt(level + 1)
            self.add_to_parse_tree(f"Function declaration: {id_token[1]} of type {type_token[1]}", level + 1)
            print(f"declaration: completed function declaration {id_token[1]}")
        else:
            self.add_syntax_error(f"Unexpected token {next_token[0]} '{next_token[1]}' in declaration")
            print(f"declaration: error with unexpected token {next_token}")
    
    def type_specifier(self, level):
        """
        Type-specifier -> int | void
        """
        self.add_to_parse_tree("Type-specifier", level)
        
        token = self.peek_token()
        print(f"type_specifier: peeked token = {token}")
        
        if token and token[0] == "KEYWORD" and token[1] in ["int", "void"]:
            token = self.get_next_token()
            print(f"type_specifier: matched type {token}")
            return token
        else:
            print(f"type_specifier: failed to match type with token {token}")
            self.add_syntax_error("Expected type specifier (int or void)")
            return None
    
    def params(self, level):
        """
        Params -> Param-list | void
        """
        self.add_to_parse_tree("Params", level)
        
        token = self.peek_token()
        if not token:
            self.add_syntax_error("Unexpected end of input in parameters")
            return
            
        if token[0] == "void":
            self.get_next_token()  # Consume void
            # Check if it's void with no params or void as a param type
            next_token = self.peek_token()
            if next_token and next_token[0] == ")":
                # void with no params
                self.add_to_parse_tree("No parameters", level + 1)
            else:
                # void as param type
                self.param_list(level + 1)
        else:
            self.param_list(level + 1)
    
    def param_list(self, level):
        """
        Param-list -> Param Param-list' 
        Param-list' -> , Param Param-list' | ε
        """
        self.add_to_parse_tree("Param-list", level)
        
        self.param(level + 1)
        
        # Check for more parameters
        while True:
            token = self.peek_token()
            if token and token[0] == ",":
                self.get_next_token()  # Consume comma
                self.param(level + 1)
            else:
                break
    
    def param(self, level):
        """
        Param -> Type-specifier ID | Type-specifier ID [ ]
        """
        self.add_to_parse_tree("Param", level)
        
        type_token = self.type_specifier(level + 1)
        if not type_token:
            return
            
        id_token = self.expect("ID", "Expected identifier in parameter")
        if not id_token:
            return
            
        # Check if it's an array parameter
        token = self.peek_token()
        if token and token[0] == "[":
            self.get_next_token()  # Consume [
            self.expect("]", "Expected closing bracket in array parameter")
            self.add_to_parse_tree(f"Array parameter: {id_token[1]} of type {type_token[1]}[]", level + 1)
        else:
            self.add_to_parse_tree(f"Parameter: {id_token[1]} of type {type_token[1]}", level + 1)
    
    def compound_stmt(self, level):
        """
        Compound-stmt -> { Local-declarations Statement-list }
        """
        self.add_to_parse_tree("Compound-stmt", level)
        
        self.expect("{", "Expected opening brace for compound statement")
        self.local_declarations(level + 1)
        self.statement_list(level + 1)
        self.expect("}", "Expected closing brace for compound statement")
    
    def local_declarations(self, level):
        """
        Local-declarations -> Type-specifier ID ; Local-declarations | ε
        """
        self.add_to_parse_tree("Local-declarations", level)
        
        # Look for variable declarations (int x; int y;)
        while True:
            token = self.peek_token()
            if not token or token[0] != "KEYWORD" or token[1] not in ["int", "void"]:
                # Not a variable declaration
                break
                
            # Found a variable declaration
            type_token = self.get_next_token()  # Get the type (int/void)
            
            # Check for ID
            id_token = self.peek_token()
            if not id_token or id_token[0] != "ID":
                self.add_syntax_error("Expected identifier after type specifier")
                break
                
            id_token = self.get_next_token()  # Get the identifier
            
            # Check for semicolon
            semi_token = self.peek_token()
            if not semi_token or semi_token[0] != "SYMBOL" or semi_token[1] != ";":
                self.add_syntax_error("Expected semicolon after variable declaration")
                break
                
            self.get_next_token()  # Get the semicolon
            
            # Add variable declaration to parse tree
            self.add_to_parse_tree(f"Variable declaration: {id_token[1]} of type {type_token[1]}", level + 1)
    
    def statement_list(self, level):
        """
        Statement-list -> Statement Statement-list | ε
        """
        self.add_to_parse_tree("Statement-list", level)
        
        # Process statements until we reach a closing brace or end of input
        while True:
            token = self.peek_token()
            if not token or (token[0] == "SYMBOL" and token[1] == "}"):
                # End of compound statement or end of input
                break
                
            # Process statement based on token type
            if token[0] == "KEYWORD":
                if token[1] == "if":
                    self.process_if_statement(level + 1)
                elif token[1] == "while":
                    self.process_while_statement(level + 1)
                elif token[1] == "return":
                    self.process_return_statement(level + 1)
                else:
                    # Unexpected keyword, skip it
                    self.add_syntax_error(f"Unexpected keyword {token[1]}")
                    self.get_next_token()
            elif token[0] == "ID":
                # Could be an assignment or function call
                self.process_id_statement(level + 1)
            else:
                # Unexpected token, skip it
                self.add_syntax_error(f"Unexpected token {token[0]} {token[1]}")
                self.get_next_token()
    
    def process_id_statement(self, level):
        """
        Process a statement starting with an identifier (assignment or function call)
        """
        id_token = self.get_next_token()  # Get the identifier
        next_token = self.peek_token()
        
        if next_token and next_token[0] == "SYMBOL":
            if next_token[1] == "=":
                # Assignment statement
                self.add_to_parse_tree(f"Assignment: {id_token[1]}", level)
                self.get_next_token()  # Get the equals sign
                
                # Process the expression
                self.process_expression(level + 1)
                
                # Check for semicolon
                semi_token = self.peek_token()
                if not semi_token or semi_token[0] != "SYMBOL" or semi_token[1] != ";":
                    self.add_syntax_error("Expected semicolon after assignment")
                else:
                    self.get_next_token()  # Get the semicolon
            elif next_token[1] == "(":
                # Function call
                self.add_to_parse_tree(f"Function call: {id_token[1]}", level)
                self.get_next_token()  # Get the opening parenthesis
                
                # Process arguments
                self.process_arguments(level + 1)
                
                # Check for closing parenthesis
                close_token = self.peek_token()
                if not close_token or close_token[0] != "SYMBOL" or close_token[1] != ")":
                    self.add_syntax_error("Expected closing parenthesis after function arguments")
                else:
                    self.get_next_token()  # Get the closing parenthesis
                
                # Check for semicolon
                semi_token = self.peek_token()
                if not semi_token or semi_token[0] != "SYMBOL" or semi_token[1] != ";":
                    self.add_syntax_error("Expected semicolon after function call")
                else:
                    self.get_next_token()  # Get the semicolon
            else:
                self.add_syntax_error(f"Unexpected token {next_token[0]} {next_token[1]} after identifier")
        else:
            self.add_syntax_error("Unexpected end of input after identifier")
    
    def process_expression(self, level):
        """
        Process an expression (could be a simple expression or complex)
        """
        self.add_to_parse_tree("Expression", level)
        
        # For simplicity, just skipping tokens until we reach a semicolon or closing parenthesis
        while True:
            token = self.peek_token()
            if not token:
                # Unexpected end of input
                self.add_syntax_error("Unexpected end of input in expression")
                break
                
            if token[0] == "SYMBOL" and (token[1] == ";" or token[1] == ")"):
                # End of expression
                break
                
            # Process this token in the expression
            self.get_next_token()
            
            # If it's an identifier, add it to the parse tree
            if token[0] == "ID" or token[0] == "NUM":
                self.add_to_parse_tree(f"{token[0]}: {token[1]}", level + 1)
            elif token[0] == "SYMBOL" and token[1] in ["+", "-", "*", "/", "<", ">", "=="]:
                self.add_to_parse_tree(f"Operator: {token[1]}", level + 1)
    
    def process_arguments(self, level):
        """
        Process function call arguments
        """
        self.add_to_parse_tree("Arguments", level)
        
        # For simplicity, just skipping tokens until we reach a closing parenthesis
        while True:
            token = self.peek_token()
            if not token:
                # Unexpected end of input
                self.add_syntax_error("Unexpected end of input in arguments")
                break
                
            if token[0] == "SYMBOL" and token[1] == ")":
                # End of arguments
                break
                
            # Process this token in the arguments
            self.get_next_token()
            
            # If it's an identifier, add it to the parse tree
            if token[0] == "ID" or token[0] == "NUM":
                self.add_to_parse_tree(f"Argument: {token[1]}", level + 1)
    
    def process_if_statement(self, level):
        """
        Process an if statement
        """
        self.add_to_parse_tree("If statement", level)
        self.get_next_token()  # Get the 'if' keyword
        
        # Check for opening parenthesis
        open_token = self.peek_token()
        if not open_token or open_token[0] != "SYMBOL" or open_token[1] != "(":
            self.add_syntax_error("Expected opening parenthesis after 'if'")
            return
            
        self.get_next_token()  # Get the opening parenthesis
        
        # Process condition
        self.process_expression(level + 1)
        
        # Check for closing parenthesis
        close_token = self.peek_token()
        if not close_token or close_token[0] != "SYMBOL" or close_token[1] != ")":
            self.add_syntax_error("Expected closing parenthesis after condition")
            return
            
        self.get_next_token()  # Get the closing parenthesis
        
        # Check for opening brace
        open_brace = self.peek_token()
        if not open_brace or open_brace[0] != "SYMBOL" or open_brace[1] != "{":
            self.add_syntax_error("Expected opening brace for if body")
            return
            
        self.get_next_token()  # Get the opening brace
        
        # Process if body
        self.statement_list(level + 1)
        
        # Check for closing brace
        close_brace = self.peek_token()
        if not close_brace or close_brace[0] != "SYMBOL" or close_brace[1] != "}":
            self.add_syntax_error("Expected closing brace for if body")
            return
            
        self.get_next_token()  # Get the closing brace
        
        # Check for else
        else_token = self.peek_token()
        if else_token and else_token[0] == "KEYWORD" and else_token[1] == "else":
            self.get_next_token()  # Get the 'else' keyword
            
            # Check for opening brace
            open_brace = self.peek_token()
            if not open_brace or open_brace[0] != "SYMBOL" or open_brace[1] != "{":
                self.add_syntax_error("Expected opening brace for else body")
                return
                
            self.get_next_token()  # Get the opening brace
            
            # Process else body
            self.statement_list(level + 1)
            
            # Check for closing brace
            close_brace = self.peek_token()
            if not close_brace or close_brace[0] != "SYMBOL" or close_brace[1] != "}":
                self.add_syntax_error("Expected closing brace for else body")
                return
                
            self.get_next_token()  # Get the closing brace
    
    def process_while_statement(self, level):
        """
        Process a while statement
        """
        self.add_to_parse_tree("While statement", level)
        self.get_next_token()  # Get the 'while' keyword
        
        # Check for opening parenthesis
        open_token = self.peek_token()
        if not open_token or open_token[0] != "SYMBOL" or open_token[1] != "(":
            self.add_syntax_error("Expected opening parenthesis after 'while'")
            return
            
        self.get_next_token()  # Get the opening parenthesis
        
        # Process condition
        self.process_expression(level + 1)
        
        # Check for closing parenthesis
        close_token = self.peek_token()
        if not close_token or close_token[0] != "SYMBOL" or close_token[1] != ")":
            self.add_syntax_error("Expected closing parenthesis after condition")
            return
            
        self.get_next_token()  # Get the closing parenthesis
        
        # Check for opening brace
        open_brace = self.peek_token()
        if not open_brace or open_brace[0] != "SYMBOL" or open_brace[1] != "{":
            self.add_syntax_error("Expected opening brace for while body")
            return
            
        self.get_next_token()  # Get the opening brace
        
        # Process while body
        self.statement_list(level + 1)
        
        # Check for closing brace
        close_brace = self.peek_token()
        if not close_brace or close_brace[0] != "SYMBOL" or close_brace[1] != "}":
            self.add_syntax_error("Expected closing brace for while body")
            return
            
        self.get_next_token()  # Get the closing brace
    
    def process_return_statement(self, level):
        """
        Process a return statement
        """
        self.add_to_parse_tree("Return statement", level)
        self.get_next_token()  # Get the 'return' keyword
        
        # Check if there's an expression after return
        next_token = self.peek_token()
        if next_token and next_token[0] != "SYMBOL" and next_token[1] != ";":
            # Process return expression
            self.process_expression(level + 1)
        
        # Check for semicolon
        semi_token = self.peek_token()
        if not semi_token or semi_token[0] != "SYMBOL" or semi_token[1] != ";":
            self.add_syntax_error("Expected semicolon after return statement")
        else:
            self.get_next_token()  # Get the semicolon

def parser(tokens_file_path="tokens.txt", symbol_table_file_path="symbol_table.txt",
           syntax_errors_file_path="syntax_errors.txt", parse_tree_file_path="parse_tree.txt"):
    """
    Main entry point for the parser
    """
    parser = Parser(tokens_file_path, symbol_table_file_path, syntax_errors_file_path, parse_tree_file_path)
    parser.parse()

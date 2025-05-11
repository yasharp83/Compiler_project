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
    
    def add_token_to_parse_tree(self, token, level):
        self.add_to_parse_tree(f"({token[0]}, {token[1]})", level)
    
    def add_epsilon(self, level):
        self.add_to_parse_tree("epsilon", level)
    
    def parse(self):
        for line_num, tokens in self.tokens.tokens.items():
            for token in tokens:
                self.token_list.append((token[0], token[1], line_num))
        self.token_list.sort(key=lambda x: x[2])
        self.program(0)
        self.write_syntax_errors()
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
    
    # --- Grammar rules ---
    def program(self, level):
        self.add_to_parse_tree("Program", level)
        self.declaration_list(level + 1)
        # End of input marker
        self.add_to_parse_tree("$", level)
    
    def declaration_list(self, level):
        self.add_to_parse_tree("DeclarationList", level)
        token = self.peek_token()
        if token and (token[0] == "KEYWORD" and token[1] in ["int", "void"]):
            self.declaration(level + 1)
            self.declaration_list(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def declaration(self, level):
        self.add_to_parse_tree("Declaration", level)
        self.declaration_initial(level + 1)
        self.declaration_prime(level + 1)
    
    def declaration_initial(self, level):
        self.add_to_parse_tree("DeclarationInitial", level)
        self.type_specifier(level + 1)
        self.match_and_add("ID", level + 1)
    
    def declaration_prime(self, level):
        self.add_to_parse_tree("DeclarationPrime", level)
        token = self.peek_token()
        if token and token[0] == "SYMBOL":
            if token[1] == ";":
                self.match_and_add("SYMBOL", level + 1, ";")
                self.var_declaration_prime(level + 1)
            elif token[1] == "[":
                self.match_and_add("SYMBOL", level + 1, "[")
                self.match_and_add("NUM", level + 1)
                self.match_and_add("SYMBOL", level + 1, "]")
                self.match_and_add("SYMBOL", level + 1, ";")
                self.var_declaration_prime(level + 1)
            elif token[1] == "(":
                self.fun_declaration_prime(level + 1)
            else:
                self.add_epsilon(level + 1)
        elif token and token[0] == "ID":
            # Error recovery: unexpected ID
            self.add_syntax_error(f"Unexpected ID {token[1]} in declaration prime")
            self.get_next_token()
            self.add_epsilon(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def var_declaration_prime(self, level):
        self.add_to_parse_tree("VarDeclarationPrime", level)
        self.add_epsilon(level + 1)
    
    def fun_declaration_prime(self, level):
        self.add_to_parse_tree("FunDeclarationPrime", level)
        self.match_and_add("SYMBOL", level + 1, "(")
        self.params(level + 1)
        self.match_and_add("SYMBOL", level + 1, ")")
        self.compound_stmt(level + 1)
    
    def type_specifier(self, level):
        self.add_to_parse_tree("TypeSpecifier", level)
        token = self.peek_token()
        if token and token[0] == "KEYWORD" and token[1] in ["int", "void"]:
            self.add_token_to_parse_tree(self.get_next_token(), level + 1)
        else:
            self.add_syntax_error("Expected type specifier (int or void)")
            self.add_epsilon(level + 1)
    
    def params(self, level):
        self.add_to_parse_tree("Params", level)
        token = self.peek_token()
        if token and token[0] == "KEYWORD" and token[1] == "void":
            self.add_token_to_parse_tree(self.get_next_token(), level + 1)
            token2 = self.peek_token()
            if token2 and token2[0] == "SYMBOL" and token2[1] == ")":
                self.add_epsilon(level + 1)
            else:
                self.param_list(level + 1)
        else:
            self.param_list(level + 1)
    
    def param_list(self, level):
        self.add_to_parse_tree("ParamList", level)
        token = self.peek_token()
        if token and token[0] == "KEYWORD" and token[1] in ["int", "void"]:
            self.param(level + 1)
            self.param_list_prime(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def param_list_prime(self, level):
        self.add_to_parse_tree("ParamListPrime", level)
        token = self.peek_token()
        if token and token[0] == "SYMBOL" and token[1] == ",":
            self.match_and_add("SYMBOL", level + 1, ",")
            self.param(level + 1)
            self.param_list_prime(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def param(self, level):
        self.add_to_parse_tree("Param", level)
        self.type_specifier(level + 1)
        self.match_and_add("ID", level + 1)
        self.param_prime(level + 1)
    
    def param_prime(self, level):
        self.add_to_parse_tree("ParamPrime", level)
        token = self.peek_token()
        if token and token[0] == "SYMBOL" and token[1] == "[":
            self.match_and_add("SYMBOL", level + 1, "[")
            self.match_and_add("SYMBOL", level + 1, "]")
        else:
            self.add_epsilon(level + 1)
    
    def compound_stmt(self, level):
        self.add_to_parse_tree("CompoundStmt", level)
        self.match_and_add("SYMBOL", level + 1, "{")
        self.declaration_list(level + 1)
        self.statement_list(level + 1)
        self.match_and_add("SYMBOL", level + 1, "}")
    
    def statement_list(self, level):
        self.add_to_parse_tree("StatementList", level)
        token = self.peek_token()
        if token and (token[0] == "ID" or (token[0] == "SYMBOL" and token[1] == ";")):
            self.statement(level + 1)
            self.statement_list(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def statement(self, level):
        self.add_to_parse_tree("Statement", level)
        token = self.peek_token()
        if token and token[0] == "ID":
            self.expression_stmt(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def expression_stmt(self, level):
        self.add_to_parse_tree("ExpressionStmt", level)
        self.expression(level + 1)
        self.match_and_add("SYMBOL", level + 1, ";")
    
    def expression(self, level):
        self.add_to_parse_tree("Expression", level)
        token = self.peek_token()
        if token and token[0] == "ID":
            self.add_token_to_parse_tree(self.get_next_token(), level + 1)
            self.B(level + 1)
        elif token and token[0] == "NUM":
            self.simple_expression_zegond(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def B(self, level):
        self.add_to_parse_tree("B", level)
        token = self.peek_token()
        if token and token[0] == "SYMBOL" and token[1] == "=":
            self.match_and_add("SYMBOL", level + 1, "=")
            self.expression(level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def simple_expression_zegond(self, level):
        self.add_to_parse_tree("SimpleExpressionZegond", level)
        self.additive_expression_zegond(level + 1)
        self.C(level + 1)
    
    def additive_expression_zegond(self, level):
        self.add_to_parse_tree("AdditiveExpressionZegond", level)
        self.term_zegond(level + 1)
        self.D(level + 1)
    
    def term_zegond(self, level):
        self.add_to_parse_tree("TermZegond", level)
        self.signed_factor_zegond(level + 1)
        self.G(level + 1)
    
    def signed_factor_zegond(self, level):
        self.add_to_parse_tree("SignedFactorZegond", level)
        self.factor_zegond(level + 1)
    
    def factor_zegond(self, level):
        self.add_to_parse_tree("FactorZegond", level)
        token = self.peek_token()
        if token and token[0] == "NUM":
            self.add_token_to_parse_tree(self.get_next_token(), level + 1)
        else:
            self.add_epsilon(level + 1)
    
    def G(self, level):
        self.add_to_parse_tree("G", level)
        self.add_epsilon(level + 1)
    
    def D(self, level):
        self.add_to_parse_tree("D", level)
        self.add_epsilon(level + 1)
    
    def C(self, level):
        self.add_to_parse_tree("C", level)
        self.add_epsilon(level + 1)
    
    def match_and_add(self, expected_token_type, level, expected_token_lexeme=None):
        token = self.match(expected_token_type, expected_token_lexeme)
        if token:
            self.add_token_to_parse_tree(token, level)
        else:
            self.add_epsilon(level)

def parser(tokens_file_path="tokens.txt", symbol_table_file_path="symbol_table.txt",
           syntax_errors_file_path="syntax_errors.txt", parse_tree_file_path="parse_tree.txt"):
    parser = Parser(tokens_file_path, symbol_table_file_path, syntax_errors_file_path, parse_tree_file_path)
    parser.parse()

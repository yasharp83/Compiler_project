# Yashar Paymai (401100325)
# Pouria Erfanzadeh (401011180)
# Group: G3

from parser.parser import Parser
from parser.syntax_errors import SyntaxErrors
from scanner.buffer import BufferedFileReader
from scanner.init_dfa import init_dfa
from scanner.lexical_errors import LexicalErrors
from scanner.symbol_table import SymbolTable
from scanner.tokens import Tokens

# from scanner.scanner import scanner
# import os

# file_path = "input.txt"
# print(f"Current working directory: {os.getcwd()}")
# print(f"Input file exists: {os.path.exists(file_path)}")
# print(f"Input file path: {os.path.abspath(file_path)}")


# scanner(code_file_path=file_path)

# try:
#     # Phase 1: Scanner
#     print("Starting scanner phase...")
#     scanner(code_file_path=file_path)
#     print("Scanner phase completed.")
    
#     # Phase 2: Parser
#     # print("Starting parser phase...")
#     # parser(tokens_file_path="tokens.txt", 
#     #        symbol_table_file_path="symbol_table.txt",
#     #        syntax_errors_file_path="syntax_errors.txt", 
#     #        parse_tree_file_path="parse_tree.txt")
#     # print("Parser phase completed.")
# except Exception as e:
#     print(f"Error occurred: {e}")
#     import traceback
#     traceback.print_exc()

code_file_path="input.txt"
lexical_error_file_path="lexical_errors.txt"
tokens_file_path="tokens.txt"
symbol_table_file_path="symbol_table.txt"

lexical_errors = LexicalErrors(file_path=lexical_error_file_path)
buffer = BufferedFileReader(file_path=code_file_path)
tokens = Tokens(tokens_file_path)
symbol_table = SymbolTable(file_path=symbol_table_file_path)
dfa = init_dfa()

P = Parser(buffer=buffer , dfa=dfa , lexical_errors=lexical_errors , 
          tokens=tokens , symbol_table=symbol_table , syntax_errors=SyntaxErrors())
P.start()
lexical_errors.update_file()
tokens.update_file()
symbol_table.update_file()
# for key in P.grammar : 
#     print(key , P.grammar[key])


# for key in P.graph.nodes : 
#     print(key , P.graph.nodes[key].component , P.graph.nodes[key].edges)
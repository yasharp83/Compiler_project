from init_dfa import init_dfa
from symbol_table import SymbolTable
from tokens import Tokens
from lexical_errors import LexicalErrors
from buffer import BufferedFileReader
from get_next_token import get_next_token

def scanner(code_file_path , lexical_error_file_path="lexical_errors.txt" , tokens_file_path="tokens.txt" , symbol_table_file_path="symbol_table.txt"):
    lexical_errors = LexicalErrors(file_path=lexical_error_file_path)
    buffer = BufferedFileReader(file_path=code_file_path)
    tokens = Tokens(tokens_file_path)
    symbol_table = SymbolTable(file_path=symbol_table_file_path)
    dfa = init_dfa()

    while True : 
        new_token = get_next_token(buffer=buffer , dfa=dfa , lexical_errors=lexical_errors , 
                                   tokens=tokens , symbol_table=symbol_table)
        if not new_token : 
            break
    lexical_errors.update_file()
    tokens.update_file()
    symbol_table.update_file()
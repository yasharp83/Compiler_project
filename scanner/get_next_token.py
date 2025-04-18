from buffer import BufferedFileReader
from DFA import DFA
from tokens import Tokens
from lexical_errors import LexicalErrors
from symbol_table import SymbolTable
from alphabet_config import is_keyword


def get_next_token(buffer:BufferedFileReader , dfa:DFA , lexical_errors:LexicalErrors , tokens:Tokens , symbol_table:SymbolTable , add_tokens=True , add_symbols=True):
    dfa.reset()
    if not buffer.has_next() : 
        return False
    token = ""
    start_line = buffer.check_next_char()[1]
    while True : 
        if not buffer.has_next() :
            if dfa.get_current_node().status[0:5]=="ERROR" : 
                lexical_errors.add(start_line,[dfa.get_current_node().status , token])
                return False
            if is_keyword(token) :
                handle_token(["KEYWORD" , token] , start_line , tokens , symbol_table , add_tokens , add_symbols)
                return  ["KEYWORD" , token]
            handle_token([dfa.get_current_node().status,token] , start_line , tokens , symbol_table , add_tokens , add_symbols)
            return [dfa.get_current_node().status,token] 

        new_char , new_line = buffer.check_next_char()
        new_state = dfa.get_new_state(new_char)
        if new_state.status[0:5]=="ERROR" and new_state.trap : 
            dfa.change_state(new_char)
            buffer.get_next_char()
            token+=new_char
            lexical_errors.add(start_line,[new_state.status , token])
            return get_next_token(buffer,dfa,lexical_errors,tokens,symbol_table)
        
        if new_state.trap and dfa.get_current_node().accept and dfa.get_current_node().status[0:7]!="COMMENT":
            if is_keyword(token) : 
                handle_token(["KEYWORD" , token] , start_line , tokens , symbol_table , add_tokens , add_symbols)
                return  ["KEYWORD" , token]
            else : 
                handle_token([dfa.get_current_node().status,token] , start_line , tokens , symbol_table , add_tokens , add_symbols)
                return [dfa.get_current_node().status,token]
        
        if new_state.trap and dfa.get_current_node().accept and dfa.get_current_node().status[0:7]=="COMMENT":
            return get_next_token(buffer,dfa,lexical_errors,tokens,symbol_table)
        
        dfa.change_state(new_char)
        buffer.get_next_char()
        token+=new_char


def handle_token(token, no_line ,tokens:Tokens , symbol_table:SymbolTable ,add_tokens=True , add_symbols=True):
    stat = token[0]
    txt = token[1]
    if add_symbols:
        if stat=="KEYWORD" or stat=="ID":
            symbol_table.add(txt)
    if add_tokens:
        if stat!="WHITE":
            tokens.add(no_line , token)
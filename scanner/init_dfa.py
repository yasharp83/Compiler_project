import DFA
from alphabet_config import *

def get_except(L1,L2):
    return [i for i in L1 if i not in L2]



def init_dfa():
    dfa = DFA.DFA()

    #NUM
    number_state_1 = dfa.add_state(True,False,"NUM")
    error_invalid_number = dfa.add_state(False,True,"ERROR_INVALID_NUMBER")
    error_invalid_input = dfa.add_state(False,True,"ERROR_INVALID_INPUT")
    
    dfa.add_edge(dfa.start_node,number_state_1,Digits)
    dfa.add_edge(number_state_1,number_state_1,Digits)
    dfa.add_edge(number_state_1,dfa.basic_trap,White_spaces+Symbols)
    dfa.add_edge(number_state_1,error_invalid_number,English_aphabet)
    dfa.add_edge(number_state_1,error_invalid_input,Illegal)

    #symbol general
    for symbol in get_except(Symbols,['*' , '/' , '=']):
        symbol_state_i = dfa.add_state(True,False,"SYMBOL")
        dfa.add_edge(dfa.start_node,symbol_state_i,[symbol])
        dfa.add_edge(symbol_state_i,dfa.basic_trap,sigma)
    
    #handling = == * / seperatly
    #handling *
    symbol_state_star = dfa.add_state(True,False,"SYMBOL")
    dfa.add_edge(dfa.start_node,symbol_state_star,['*'])
    dfa.add_edge(symbol_state_star,dfa.basic_trap,White_spaces+English_aphabet+Digits+get_except(Symbols , ['/']))
    dfa.add_edge(symbol_state_star,error_invalid_input,Illegal)
    error_unmachted_comment = dfa.add_state(False,True,"ERROR_UNMATCHED_COMMENT")
    dfa.add_edge(symbol_state_star,error_unmachted_comment,['/'])

    #handling = ==
    symbol_state_eq = dfa.add_state(True,False,"SYMBOL")
    symbol_state_eqeq = dfa.add_state(True,False,"SYMBOL")
    dfa.add_edge(dfa.start_node,symbol_state_eq,["="])
    dfa.add_edge(symbol_state_eq,symbol_state_eqeq,["="])
    dfa.add_edge(symbol_state_eq,dfa.basic_trap,get_except(sigma , ["="]+Illegal))
    dfa.add_edge(symbol_state_eq,error_invalid_input,Illegal)
    dfa.add_edge(symbol_state_eqeq,dfa.basic_trap,sigma)

    #handling /
    symbol_state_div = dfa.add_state(True,False,"SYMBOL")
    dfa.add_edge(dfa.start_node,symbol_state_div,["/"])
    dfa.add_edge(symbol_state_div,dfa.basic_trap,White_spaces+English_aphabet+Digits+get_except(Symbols , ['*']))
    dfa.add_edge(symbol_state_div,error_invalid_input,Illegal)


    #hanlding comment state /*
    comment_state_1 = dfa.add_state(False,False,"ERROR_UNCLOSED_COMMENT")
    comment_state_2 = dfa.add_state(False,False,"ERROR_UNCLOSED_COMMENT")
    comment_state_3 = dfa.add_state(True,False,"COMMENT_CLOSED")
    dfa.add_edge(symbol_state_div,comment_state_1,['*'])
    dfa.add_edge(comment_state_1,comment_state_1,get_except(sigma,['*']))
    dfa.add_edge(comment_state_1,comment_state_2,['*'])
    dfa.add_edge(comment_state_2,comment_state_1,get_except(sigma,['/']))
    dfa.add_edge(comment_state_2,comment_state_3,['/'])
    dfa.add_edge(comment_state_3,dfa.basic_trap,sigma)

    #handling whitespaces
    for white_space in White_spaces:
        white_space_state_i = dfa.add_state(True,False,"WHITE")
        dfa.add_edge(dfa.start_node,white_space_state_i,white_space)
        dfa.add_edge(white_space_state_i,dfa.basic_trap,sigma)

    #handling ID,Keywords
    id_state_1 = dfa.add_state(True,False,"ID")
    dfa.add_edge(dfa.start_node,id_state_1,English_aphabet)
    dfa.add_edge(id_state_1,id_state_1,English_aphabet+Digits)
    dfa.add_edge(id_state_1,dfa.basic_trap,White_spaces+Symbols)
    dfa.add_edge(id_state_1,error_invalid_input,Illegal)

    #Illegals
    for illegal in Illegal:
        dfa.add_edge(dfa.start_node,error_invalid_input,illegal)


    return dfa
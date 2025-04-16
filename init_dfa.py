
class DFA:
    class Node:
        def __init__(self , accept:bool , trap:bool , status:str):
            self.accept = accept
            self.trap = trap
            self.status = status
    def __init__(self):
        self.alphabet = [chr(i) for i in range(128)]

        self.states = {0:DFA.Node(False , False,"START") , 1:DFA.node(False , True , "TRAP_BASIC")}

        self.transition = {}

        for v in self.states.keys:
            self.transition[v] = {}
            for edge in self.alphabet : 
                self.transition[v][edge] = self.basic_trap

        self.current_state = 0
        self.start_node = 0
        self.basic_trap = 1
        self.num_nodes = 2

    def reset(self): 
        self.current_state = self.start_node
        return 

    def add_state(self,accept:bool , trap:bool , status:str):
        self.states[self.num_nodes] = DFA.Node(accept, trap , status)
        for edge in self.alphabet : 
            self.transition[self.num_nodes][edge] = self.basic_trap
        self.num_nodes+=1
        return self.num_nodes - 1
    
    def add_edge(self,v , u , edges):
        for edge in edges : 
            self.transition[v][edge] = u
        return
    
    def get_new_state(self,edge):
        return self.transition[self.current_state][edge]
    
    def change_state(self,edge):
        self.current_state = self.transition[self.current_state][edge]
        return

    def get_current_node(self):
        return self.states[self.current_state]
    



    

#import DFA

Keywords = ["if" , "else" , "void" , "int" , "while" , "break" , "return"]
Symbols = [';' , ':' , ',' , '[' , ']' , '(' , ')' , '{' , '}' , '+' , '-' , '*' , '/' , '\\' , '=' , '=' , '>' , '<']
#TODO: handling == 
White_spaces = [chr(32),chr(10),chr(9),chr(13),chr(11),chr(12)]
Digits = [i for i in range(10)]
English_aphabet = [chr(i) for i in (range(65,91) + range(97,123))]
Illegal = []
for i in range(128):
    if (chr(i) not in Symbols) and (chr(i) not in White_spaces) and (chr(i) not in Digits) and (chr(i) not in English_aphabet) :
        Illegal.append(chr(i))
sigma = [chr(i) for i in range(128)]

def get_except(L1,L2):
    return [i for i in L1 if i not in L2]



def init_dfa():
    dfa = DFA()

    #NUM
    number_state_1 = dfa.add_state(True,False,"NUM")
    error_invalid_number = dfa.add_state(False,True,"ERROR_INVALID_NUMBER")
    error_invalid_input = dfa.add_state(False,True,"ERROR_INVALID_INPUT")
    
    dfa.add_edge(dfa.start_node,dfa.number_state_1,Digits)
    dfa.add_edge(number_state_1,dfa.basic_trap,White_spaces+Symbols)
    dfa.add_edge(number_state_1,error_invalid_number,English_aphabet)
    dfa.add_edge(number_state_1,error_invalid_input,Illegal)

    #symbol general
    for symbol in get_except(Symbols,['*' , '/' , '=']):
        symbol_state_i = dfa.add_state(True,False,"SYMBOL"+symbol)
        dfa.add_edge(dfa.start_node,symbol_state_i,[symbol])
        dfa.add_edge(symbol_state_i,dfa.basic_trap,sigma)
    
    #handling = == * / seperatly
    #handling *
    symbol_state_star = dfa.add_state(True,False,"SYMBOL*")
    dfa.add_edge(dfa.start_node,symbol_state_star,['*'])
    dfa.add_edge(symbol_state_star,dfa.basic_trap,White_spaces+English_aphabet+Digits+get_except(Symbols , ['/']))
    dfa.add_edge(symbol_state_star,error_invalid_input,Illegal)
    error_unmachted_comment = dfa.add_state(False,True,"ERROR_UNMATCHED_COMMENT")
    dfa.add_edge(symbol_state_star,error_unmachted_comment,['/'])

    #handling = ==
    symbol_state_eq = dfa.add_state(True,False,"SYMBOL=")
    symbol_state_eqeq = dfa.add_state(True,False,"SYMBOL==")
    dfa.add_edge(dfa.start_node,symbol_state_eq,["="])
    dfa.add_edge(symbol_state_eq,symbol_state_eqeq,["="])
    dfa.add_edge(symbol_state_eq,dfa.basic_trap,sigma)
    dfa.add_edge(symbol_state_eqeq,dfa.basic_trap,sigma)

    #TODO


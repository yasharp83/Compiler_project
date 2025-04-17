
class DFA:
    class Node:
        def __init__(self , accept:bool , trap:bool , status:str):
            self.accept = accept
            self.trap = trap
            self.status = status
    def __init__(self):
        self.alphabet = [chr(i) for i in range(128)]

        self.states = {0:DFA.Node(False , False,"START") , 1:DFA.Node(False , True , "TRAP_BASIC")}

        self.transition = {}

        self.current_state = 0
        self.start_node = 0
        self.basic_trap = 1
        self.num_nodes = 2

        for v in self.states.keys():
            self.transition[v] = {}
            for edge in self.alphabet : 
                self.transition[v][edge] = self.basic_trap



    def reset(self): 
        self.current_state = self.start_node
        return 

    def add_state(self,accept:bool , trap:bool , status:str):
        self.states[self.num_nodes] = DFA.Node(accept, trap , status)
        self.transition[self.num_nodes] = {}
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
        return self.states[self.current_state]

    def get_current_node(self):
        return self.states[self.current_state]
    



    
from parser.syntax_errors import SyntaxErrors
from scanner.buffer import BufferedFileReader
from scanner.DFA import DFA
from scanner.tokens import Tokens
from scanner.lexical_errors import LexicalErrors
from scanner.symbol_table import SymbolTable
from scanner.get_next_token import get_next_token
from scanner.init_dfa import init_dfa
from code_gen.codeGen import CodeGen
from scanner.symbol_table import Token
class TdNode:
    def __init__(self ,component: str , id : int , is_accept : bool = False):
        self.id = id
        self.component = component
        self.is_accept = is_accept
        self.edges = []
    def add_edge(self , edge: str , dest : int , actions:dict[str , list[str]]={"start":[] , "finish":[]}):
        self.edges.append((edge , dest , actions))

    def __str__(self):
        return f'{self.id} ,{self.component} , {self.is_accept} , {self.edges}'

class TdGraph:
    def __init__(self):
        self.non_terminal_first : dict[str , int] = {}
        self.cur_id : int = 0
        self.nodes : dict[int , TdNode] = {}

    def add_node(self , component : str , is_accept : bool = False) -> int:
        self.cur_id+=1
        node = TdNode(component=component , id = self.cur_id ,  is_accept=is_accept)
        if component not in self.non_terminal_first : 
            self.non_terminal_first[component] = self.cur_id
        self.nodes[self.cur_id] = node
        return self.cur_id

    def add_edge(self , start: int , edge : str, dest : int , actions:dict[str , list[str]]={"start":[] , "finish":[]}):
        self.nodes[start].add_edge(edge , dest , actions=actions)

    def get_edge_actions(self , start: int , edge : str  , dest : int):
        for e in self.nodes[start].edges : 
            if e[0]==edge and e[1]==dest : 
                return e[2]
        return None
    
    def get_first_non_terminal(self , component : str) -> int: 
        try : 
            return self.non_terminal_first[component]
        except:
            return  -1
    
    def __str__(self):
        return "\n".join([f"{i} : {self.nodes[i]}" for i in self.nodes.keys()]) + "\n" + str(self.non_terminal_first)


class PtNode:
    def __init__(self,label : str):
        self.label = label
        self.children : list[PtNode] = []
    
    def add_children(self,child : "PtNode"):
        self.children.append(child)
    
    def to_lines(self,prefix : str = '' , is_last : bool = True) -> list[str]:
        joint = joint = '└── ' if is_last else '├── '
        if self.label == "Program" : 
            joint = ''
        line  = prefix + joint + self.label
        lines = [line]
        child_prefix = prefix + ('    ' if is_last else '│   ')
        if self.label == "Program" : 
            child_prefix = prefix
        for i, child in enumerate(self.children):
            last = i ==(len(self.children) - 1)
            lines.extend(child.to_lines(child_prefix, last))
        return lines
    
class Parser : 
    def __init__(self , buffer:BufferedFileReader 
                      , dfa:DFA 
                      , lexical_errors:LexicalErrors 
                      , tokens:Tokens 
                      , symbol_table:SymbolTable 
                      , syntax_errors : SyntaxErrors 
                      , codeGen : CodeGen
                      , grammar_path : str = "parser/grammar_config/grammar.txt"
                      , follow_path : str = "parser/grammar_config/follow.txt"
                      , first_path : str = "parser/grammar_config/first.txt" 
                      , debug:bool = False
                 ):

        self.nonTerminals : list[str] = []
        self.terminals : list[str] = []
        self.grammar = self.load_grammar(grammar_path) 
        self.follows = self.load_follow_first(follow_path)
        self.firsts = self.load_follow_first(first_path)

        self.graph : TdGraph = TdGraph()
        self.makeTdGraph()

        self.cur_symbol : str = None
        self.cur_token = None
        
        self.parse_tree_root : PtNode = None

        self.syntax_errors = syntax_errors

        self.buffer = buffer
        self.dfa = dfa 
        self.lexical_errors = lexical_errors
        self.tokens = tokens
        self.symbol_table = symbol_table

        self.codeGen = codeGen

        self.eof_error_occured = False
        self.debug = debug

    def start(self):
        self.advance()
        root = PtNode("Program")
        self.parse_nonterminal("Program" , root)
        
        self.parse_tree_root = root
        self.write_tree()
        self.syntax_errors.update_file()


    def parse_nonterminal(self , cur_nt : str , pt_par : PtNode):
        node_id = self.graph.get_first_non_terminal(cur_nt)
        cur_node= self.graph.nodes[node_id]
        self.debug_print("#entered node : " + cur_nt)
        if len(cur_node.edges) > 1 : 
            look = self.cur_symbol
            progressed = False

            for edge , dest , edge_actions in cur_node.edges : 
                self.debug_print(f"## {cur_nt} : checking edge {edge} with look {look}")
                if self.edge_match(edge , cur_nt , look) :
                    ### codeGen
                    self.do_actions(cur_node_id=cur_node.id , edge=edge , dest_id=dest , start=True)
                    ###
                    self.debug_print(f"# {edge} matched with {look}")
                    if edge.lower()=="epsilon" : 
                        pt_par.add_children(PtNode("epsilon"))
                        cur_node = self.graph.nodes[dest]
                        progressed = True
                        break
                    
                    if edge in self.terminals:
                        self.do_actions(cur_node_id=cur_node.id , edge=edge , dest_id=dest , start=False)
                        pt_par.add_children(PtNode(self.leaf_repr()))
                        self.advance()
                        cur_node = self.graph.nodes[dest]
                        progressed = True
                        break

                    child = PtNode(edge)
                    pt_par.add_children(child)
                    self.parse_nonterminal(edge , child)
                    ### codeGen
                    self.do_actions(cur_node_id=cur_node.id , edge=edge , dest_id=dest , start=False)
                    ###
                    cur_node = self.graph.nodes[dest]
                    progressed = True
                    break
            
            if not progressed : 
                self.debug_print(f"## {cur_nt} : no edge matched with look {look}")
                if look == "$" : 
                    if not self.eof_error_occured:
                        self.eof_error_occured=True
                        self.syntax_errors.add(self.buffer.line , "syntax error, Unexpected EOF")
                    return True
                elif look not in self.follows[cur_nt]: 
                    self.debug_print(f"## {cur_nt} : no edge matched with look {look} and not in follows")
                    self.syntax_errors.add(self.buffer.line , f"syntax error, illegal {look}")
                    self.advance()

                else : 
                    self.debug_print(f"## {cur_nt} : no edge matched with look {look} and in follows")
                    self.syntax_errors.add(self.buffer.line , f"syntax error, missing {cur_nt}")
                    return False


        while True : 
            if cur_node.is_accept : 
                return True
            
            look = self.cur_symbol

            edge , dest , edge_actions = cur_node.edges[0]
            self.debug_print(f"## {cur_nt} : checking edge {edge} with look {look}")
            if self.edge_match(edge , cur_nt , look) : 
                ### codeGen
                self.do_actions(cur_node_id=cur_node.id , edge=edge , dest_id=dest , start=True)
                ###
                self.debug_print(f"# {edge} matched with {look}")
                if edge in self.terminals:
                    self.do_actions(cur_node_id=cur_node.id , edge=edge , dest_id=dest , start=False)
                    pt_par.add_children(PtNode(self.leaf_repr()))
                    self.advance()
                    cur_node = self.graph.nodes[dest]
                    continue

                child = PtNode(edge)
                pt_par.add_children(child)
                self.parse_nonterminal(edge , child)
                ### codeGen
                self.do_actions(cur_node_id=cur_node.id , edge=edge , dest_id=dest , start=False)
                ###
                cur_node = self.graph.nodes[dest]
                continue
            if look == "$" : 
                if not self.eof_error_occured:
                    self.eof_error_occured=True
                    self.syntax_errors.add(self.buffer.line , "syntax error, Unexpected EOF")
                return True
            elif self.is_terminal(edge) and look not in self.follows[cur_nt]: 
                self.debug_print(f"## {cur_nt} : no edge matched with look {look} and not in follows")
                self.syntax_errors.add(self.buffer.line , f"syntax error, illegal {look}")
                self.advance()
            elif not self.is_terminal(edge) and look not in self.follows[edge]:
                self.debug_print(f"## {cur_nt} : no edge matched with look {look} and not in follows")
                self.syntax_errors.add(self.buffer.line , f"syntax error, illegal {look}")
                self.advance()
            else :
                self.debug_print(f"## {cur_nt} : no edge matched with look {look} and in follows")
                self.syntax_errors.add(self.buffer.line , f"syntax error, missing {edge}")
                cur_node = self.graph.nodes[dest]
    
    def edge_match(self, edge : str , component : str , look : str) -> bool:
        if edge.lower() == "epsilon" : 
            return look in self.follows[component] 
        if self.is_terminal(edge):
            return edge.lower()==look.lower()
        if look in self.firsts[edge] or ("EPSILON" in self.firsts[edge] and (look in self.follows[edge])):
            return True
        return False

    
    def advance(self):
        tok = self._get_next_token()
        if tok[0].lower()=="white" : 
            self.advance()
            return
        self.cur_token = tok
        self.cur_symbol = self.token_to_symbol(tok)

    def extract_action_params(self , action : str) -> list[str]:
        if "(" not in action : 
            return []
        return action[action.find('(')+1:action.rfind(')')].split(',')
    def extract_action_action(self , action : str):
        if "(" not in action : 
            return action[1:]
        return action[1:action.find('(')]

    def do_actions(self , cur_node_id , edge , dest_id , start):
        dict_key = "start" if start else "finish"
        for action in self.graph.get_edge_actions(start=cur_node_id , edge=edge , dest=dest_id)[dict_key]:
            if self.extract_action_action(action) in self.codeGen.sub_routines.keys():

                self.debug_print(f"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Start:{self.buffer.line}")
                self.debug_print(f"{action} , {self.cur_token[0]} , {self.cur_token[1]} called")
                self.debug_print(f"semantic_stack :  {self.codeGen.semantic_stack}")
                self.debug_print("scopes : ")
                for sc in self.codeGen.symbol_table.scopes : 
                    self.debug_print([(scr.address , scr.token.lexeme , scr.token_type , scr.args_type) for scr in sc.records])
                self.debug_print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@End")
                self.codeGen.sub_routines[self.extract_action_action(action)](token=Token(self.cur_token[0] , self.cur_token[1]) , param=self.extract_action_params(action)+[self.buffer.line])
            else : 
                print(f"{action} doesnt support yet :(")
        

    def token_to_symbol(self,tok) -> str:
        if tok[0].lower()=="keyword" or tok[0].lower()=="symbol" : 
            return tok[1]
        return tok[0]
    
    def leaf_repr(self) -> str : 
        if self.cur_symbol=="$" : 
            return "$"
        return f"({self.cur_token[0]}, {self.cur_token[1]}) "

    def load_grammar(self , path : str) -> dict[str , list[list[str]]]:
        d = {}
        with open(path , "r" , encoding="utf8") as f : 
            for line in f :
                line = line.strip()
                if not line : 
                    continue
                lhs , rhs = [x.strip() for x in line.split("->" , 1)]
                self.nonTerminals.append(lhs)
                self.terminals.append(lhs)
                for alt in rhs.split("|"):
                    try :
                        d[lhs].append(alt.strip().split())
                    except:
                        d[lhs] = []
                        d[lhs].append(alt.strip().split())
                    self.terminals.extend(alt.strip().split())
        self.terminals = list(set(self.terminals))
        self.nonTerminals = list(set(self.nonTerminals))
        for i in self.nonTerminals : 
            if i in self.terminals : 
                self.terminals.remove(i)
        self.terminals = [i for i in self.terminals if i[0]!="#" ]
        self.nonTerminals = [i for i in self.nonTerminals if i[0]!="#" ]
        return d
    
    def load_follow_first(self , path : str) -> dict[str , list[str]]:
        d = {}
        with open(path , "r" , encoding="utf8") as f : 
            for line in f : 
                line = line.strip().split()
                d[line[0]] = line[1:]
        return d
    
    def tdGraph_accept_index(self , path):
        for i in range(len(path)-1 , -1 , -1):
            if path[i][0]!="#" : 
                return i
        
    def makeTdGraph(self):
        for v in self.grammar.keys():
            cur_id = self.graph.add_node(v)
            for path in self.grammar[v] : 
                actions = []
                cur_id = self.graph.get_first_non_terminal(v)
                last_edge_details = (None , None , None)
                for i in range(len(path)):
                    u = path[i]
                    if u[0]=="#" : 
                        actions.append(u)
                        continue
                    new_id = self.graph.add_node(v , is_accept=(i==self.tdGraph_accept_index(path=path)))
                    self.graph.add_edge(cur_id , u , new_id , actions={"start":actions.copy() , "finish":[]})
                    actions.clear()
                    last_edge_details = (cur_id , u , new_id)
                    cur_id = new_id
                if len(actions) > 0 : 
                    act_dict = self.graph.get_edge_actions(start=last_edge_details[0] , edge=last_edge_details[1] , dest=last_edge_details[2])
                    act_dict["finish"] = actions


    def is_terminal(self , token : str) -> bool:
        return token in self.terminals
    
    def _get_next_token(self):
        nt = get_next_token(buffer=self.buffer , dfa=self.dfa , lexical_errors=self.lexical_errors , 
                              tokens=self.tokens , symbol_table=self.symbol_table)
        return nt
    
    def write_tree(self , path="parse_tree.txt"):
        if not self.parse_tree_root:
            return
        with open(path , "w" , encoding="utf-8") as f : 
            f.write("\n".join(self.parse_tree_root.to_lines()))

    def debug_print(self , msg : str):
        if not self.debug:
            return
        print(msg)
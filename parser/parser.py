from parser.syntax_errors import SyntaxErrors
from scanner.buffer import BufferedFileReader
from scanner.DFA import DFA
from scanner.tokens import Tokens
from scanner.lexical_errors import LexicalErrors
from scanner.symbol_table import SymbolTable
from scanner.get_next_token import get_next_token
from scanner.init_dfa import init_dfa
class TdNode:
    def __init__(self ,component: str , id : int , is_accept : bool = False):
        self.id = id
        self.component = component
        self.is_accept = is_accept
        self.edges = []
    def add_edge(self , edge: str , dest : int):
        self.edges.append((edge , dest))

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

    def add_edge(self , start: int , edge : str, dest : int):
        self.nodes[start].add_edge(edge , dest)
    
    def get_first_non_terminal(self , component : str) -> int: 
        try : 
            return self.non_terminal_first[component]
        except:
            return  -1

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
                      , grammar_path : str = "parser/grammar_config/grammar.txt"
                      , follow_path : str = "parser/grammar_config/follow.txt"
                      , first_path : str = "parser/grammar_config/first.txt" 
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

        #get_next_token stuff
        self.buffer = buffer
        self.dfa = dfa 
        self.lexical_errors = lexical_errors
        self.tokens = tokens
        self.symbol_table = symbol_table

        self.eof_error_occured = False

    def start(self):
        self.advance()
        root = PtNode("Program")
        self.parse_nonterminal("Program" , root)
        
        
        root.children.append(PtNode("$"))

        self.parse_tree_root = root
        self.write_tree()
        self.syntax_errors.update_file()


    def parse_nonterminal(self , cur_nt : str , pt_par : PtNode):
        node_id = self.graph.get_first_non_terminal(cur_nt)
        cur_node= self.graph.nodes[node_id]
        if len(cur_node.edges) > 1 : 
            look = self.cur_symbol
            progressed = False

            for edge , dest in cur_node.edges : 
                if self.edge_match(edge , cur_nt , look) : 
                    if edge.lower()=="epsilon" : 
                        pt_par.add_children(PtNode("epsilon"))
                        cur_node = self.graph.nodes[dest]
                        progressed = True
                        break
                    
                    if edge in self.terminals:
                        pt_par.add_children(PtNode(self.leaf_repr()))
                        self.advance()
                        cur_node = self.graph.nodes[dest]
                        progressed = True
                        break

                    child = PtNode(edge)
                    pt_par.add_children(child)
                    self.parse_nonterminal(edge , child)
                    cur_node = self.graph.nodes[dest]
                    progressed = True
                    break
            
            if not progressed : 

                if look == "$" : 
                    if not self.eof_error_occured:
                        self.eof_error_occured=True
                        self.syntax_errors.add(self.buffer.line , "syntax error, Unexpected EOF")
                    return True
                elif look not in self.follows[cur_nt]: 
                    self.syntax_errors.add(self.buffer.line , f"syntax error, illegal {look}")
                    self.advance()

                else : 
                    self.syntax_errors.add(self.buffer.line , f"syntax error, missing {cur_nt}")
                    return False


        while True : 
            if cur_node.is_accept : 
                return True
            
            look = self.cur_symbol

            edge , dest = cur_node.edges[0]
            #print(cur_nt , " " , edge , " " , look)
            if self.edge_match(edge , cur_nt , look) : 
                #print("koobs")
                if edge in self.terminals:
                    pt_par.add_children(PtNode(self.leaf_repr()))
                    self.advance()
                    cur_node = self.graph.nodes[dest]
                    continue

                child = PtNode(edge)
                pt_par.add_children(child)
                self.parse_nonterminal(edge , child)
                cur_node = self.graph.nodes[dest]
                continue
            if look == "$" : 
                if not self.eof_error_occured:
                    self.eof_error_occured=True
                    self.syntax_errors.add(self.buffer.line , "syntax error, Unexpected EOF")
                return True
            elif self.is_terminal(edge) and look not in self.follows[cur_nt]: 
                self.syntax_errors.add(self.buffer.line , f"syntax error, illegal {look}")
                self.advance()
            elif not self.is_terminal(edge) and look not in self.follows[edge]:
                self.syntax_errors.add(self.buffer.line , f"syntax error, illegal {look}")
                self.advance()
            else :
                self.syntax_errors.add(self.buffer.line , f"syntax error, missing {edge}")
                cur_node = self.graph.nodes[dest]
    
    def edge_match(self, edge : str , component : str , look : str) -> bool:
        if edge.lower() == "epsilon" : 
            return look in self.follows[component] #or look =="$"
        if self.is_terminal(edge):
            return edge.lower()==look.lower()
        if look in self.firsts[edge] or ("EPSILON" in self.firsts[edge] and (look in self.follows[edge])):#or look == "$"
            return True
        return False

    
    def advance(self):
        tok = self._get_next_token()
        if tok[0].lower()=="white" : 
            self.advance()
            return
        self.cur_token = tok
        self.cur_symbol = self.token_to_symbol(tok)

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
        return d
    
    def load_follow_first(self , path : str) -> dict[str , list[str]]:
        d = {}
        with open(path , "r" , encoding="utf8") as f : 
            for line in f : 
                line = line.strip().split()
                d[line[0]] = line[1:]
        return d
        
    def makeTdGraph(self):
        for v in self.grammar.keys():
            cur_id = self.graph.add_node(v)
            for path in self.grammar[v] : 
                cur_id = self.graph.get_first_non_terminal(v)
                for i in range(len(path)):
                    u = path[i]
                    new_id = self.graph.add_node(v , is_accept=(i==len(path)-1))
                    self.graph.add_edge(cur_id , u , new_id)
                    cur_id = new_id

    def is_terminal(self , token : str) -> bool:
        return token in self.terminals
    
    def _get_next_token(self):
        return get_next_token(buffer=self.buffer , dfa=self.dfa , lexical_errors=self.lexical_errors , 
                              tokens=self.tokens , symbol_table=self.symbol_table)
    
    def write_tree(self , path="parse_tree.txt"):
        if not self.parse_tree_root:
            return
        with open(path , "w" , encoding="utf-8") as f : 
            f.write("\n".join(self.parse_tree_root.to_lines()))


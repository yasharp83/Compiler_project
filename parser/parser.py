class TdNode:
    def __init__(self ,component , id , is_accept = False):
        self.id = id
        self.component = component
        self.is_accept = is_accept
        self.edges = []
    def add_edge(self , edge , dest):
        self.edges.append((edge , dest))

class TdGraph:
    def __init__(self):
        self.non_terminal_first = {}
        self.cur_id = 0
        self.nodes = {}

    def add_node(self , component , is_accept = False):
        self.cur_id+=1
        node = TdNode(component=component , id = self.cur_id ,  is_accept=is_accept)
        if component not in self.non_terminal_first : 
            self.non_terminal_first[component] = self.cur_id
        self.nodes[self.cur_id] = node
        return self.cur_id

    def add_edge(self , start , edge , dest):
        self.nodes[start].add_edge(edge , dest)
    
    def get_first_non_terminal(self , component) : 
        try : 
            return self.non_terminal_first[component]
        except:
            return  -1

class Parser : 
    def __init__(self , grammar_path = "parser/grammar_config/grammar.txt"
                      , follow_path = "parser/grammar_config/follow.txt"
                      , first_path  = "parser/grammar_config/first.txt"
                 ):

        self.nonTerminals = []
        self.terminals = []
        self.grammar = self.load_grammar(grammar_path) 
        self.follows = self.load_follow_first(follow_path)
        self.firsts = self.load_follow_first(first_path)

        self.graph = TdGraph()
        self.makeTdGraph()

    def load_grammar(self , path):
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
    
    def load_follow_first(self , path):
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
                for u in path : 
                    new_id = self.graph.add_node(v , is_accept=(u==path[-1]))
                    self.graph.add_edge(cur_id , u , new_id)
                    cur_id = new_id

P = Parser()
for v in P.graph.nodes.keys():
    print(v , " : " , P.graph.nodes[v].component  ," " , P.graph.nodes[v].is_accept ,  " " , P.graph.nodes[v].edges )
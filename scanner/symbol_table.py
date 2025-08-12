from scanner.alphabet_config import Keywords

class Token:
    def __init__(self , type , lexeme):
        self.type = type
        self.lexeme = lexeme

class Record:
    def __init__(self , token: Token =None , address=None , token_type=None , scope : 'Scope' = None , num_args=None):
        self.token = token
        self.address = address
        self.token_type = token_type
        self.scope = scope
        self.num_args = num_args

class Scope:
    def __init__(self , parent=None):
        self.records : list[Record] = []
        self.parent : Scope = parent

    def add(self , token : Token) -> bool:
        if self.get_record(token_lexeme=token.lexeme) is None:
            record = Record(token=token , scope=self)
            self.records.append(record)
            return True
        return False
    
    def get_record(self , token_lexeme) -> Record:
        for record in self.records : 
            if record.token.lexeme == token_lexeme:
                return record
        if self.parent is not None : 
            return self.parent.get_record(token_lexeme=token_lexeme)
        return None


class SymbolTable:
    def __init__(self, file_path="symbol_table.txt"):
        self.file_path = file_path
        self.scopes = [Scope()]
        self.keywords = Keywords

    def get_current_scope(self): 
        return self.scopes[-1]

    def add_scope(self):
        self.scopes.append(Scope(self.get_current_scope()))
        return
    
    def remove_scope(self):
        return self.scopes.pop()
    
    def add(self , token) -> bool:
        if type(token) is list : 
            token = Token(token[0] , token[1])
        if token.lexeme in self.keywords : 
            return False
        return self.get_current_scope().add(token=token)
    
    def find_record_by_id(self , lexeme) -> Record:
        return self.get_current_scope().get_record(token_lexeme=lexeme)
    
    def update_file(self):
        #TODO
        return

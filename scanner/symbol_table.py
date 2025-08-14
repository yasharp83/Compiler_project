from scanner.alphabet_config import Keywords

class Token:
    def __init__(self , type , lexeme):
        self.type = type
        self.lexeme = lexeme

class Record:
    def __init__(self , token: Token =None , address=None , token_type=None , scope : 'Scope' = None , is_function=None ,  num_args=None , args_type:list[str]=None):
        self.token = token
        self.address = address
        self.token_type = token_type
        self.scope = scope
        self.is_function = is_function
        self.num_args = num_args
        self.args_type = args_type

class Scope:
    def __init__(self , parent=None , layer=0):
        self.records : list[Record] = []
        self.parent : Scope = parent
        self.layer = layer

    def add(self , token : Token) -> bool:
        if self.get_record_local(token_lexeme=token.lexeme) is None:
            record = Record(token=token , scope=self)
            self.records.append(record)
            return True
        return False
    
    def get_record_local(self , token_lexeme) -> Record:
        for record in self.records : 
            if record.token.lexeme == token_lexeme:
                return record
        if self.parent is not None and self.parent.layer!=0 : 
            return self.parent.get_record(token_lexeme=token_lexeme)
        return None
        
    def get_record(self , token_lexeme) -> Record:
        for record in self.records : 
            if record.token.lexeme == token_lexeme:
                return record
        if self.parent is not None : 
            return self.parent.get_record(token_lexeme=token_lexeme)
        return None
    def get_record_by_address(self , address) -> Record: 
        for record in self.records : 
            if record.address == address : 
                return record
        if self.parent is not None : 
            return self.parent.get_record_by_address(address=address)
        return None


class SymbolTable:
    def __init__(self, file_path="symbol_table.txt"):
        self.file_path = file_path
        self.scopes : list[Scope] = [Scope()]
        self.keywords = Keywords

    def get_current_scope(self): 
        return self.scopes[-1]

    def add_scope(self):
        self.scopes.append(Scope(self.get_current_scope() , layer=len(self.scopes)))
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
    
    def get_record_by_address(self , address) -> Record: 
        return self.get_current_scope().get_record_by_address(address=address)
    
    def get_last_function_record(self) -> Record : 
        for r in reversed(self.scopes[0].records): 
            if r.is_function :
                return r
        return None
    
    def update_file(self):
        #TODO
        return

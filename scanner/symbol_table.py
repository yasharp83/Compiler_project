from alphabet_config import Keywords
class SymbolTable:
    def __init__(self,file_path="symbol_table.txt"):
        self.file_path = file_path
        self.symbols = []
        for keyword in Keywords : 
            self.symbols.append(keyword)
        try:
            with open(file_path, 'a'):
                pass 
        except:
            print(f"an error occurred while creating the file{self.file_path}")
    
    def add(self,symbol):
        if symbol in self.symbols:
            return False
        self.symbols.append(symbol)
        return True
    
    def update_file(self):
        try:
            with open(self.file_path, 'w') as f:
                ind = 1
                for symbol in self.symbols:
                    f.write(f"{ind}.\t{symbol}\n")
                    ind+=1
        except:
            print(f"an error occurred while updating the file{self.file_path}")

    #TODO : next phase
    def read_file(self,file_path):
        pass
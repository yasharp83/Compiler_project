from .alphabet_config import Keywords
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

    def read_file(self, file_path=None):
        """
        Read symbols from a file formatted as:
        1.    symbol1
        2.    symbol2
        etc.
        """
        if file_path is None:
            file_path = self.file_path
            
        try:
            # Keep keywords but reset other symbols
            self.symbols = [symbol for symbol in self.symbols if symbol in Keywords]
            
            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    parts = line.strip().split('\t')
                    if len(parts) < 2:
                        continue
                    
                    # Extract symbol (ignore index)
                    symbol = parts[1].strip()
                    if symbol and symbol not in self.symbols:
                        self.symbols.append(symbol)
                        
            return True
        except Exception as e:
            print(f"An error occurred while reading the file {file_path}: {e}")
            return False
class Tokens:
    def __init__(self,file_path="tokens.txt"):
        self.file_path = file_path
        self.tokens ={}
        try:
            with open(file_path, 'a'):
                pass 
        except:
            print(f"an error occurred while creating the file{self.file_path}")
    
    def add(self,no_line , token):
        #TODO
        try : 
            self.tokens[no_line].append(token)
        except:
            self.tokens[no_line] = []
            self.tokens[no_line].append(token)
    
    def update_file(self):
        try:
            with open(self.file_path, 'w') as f:
                for line in self.tokens.keys():
                    f.write(f"{line}\t")
                    for token in self.tokens[line]:
                        f.write(f" {token}")
                    f.write("\n")
                
        except:
            print(f"an error occurred while updating the file{self.file_path}")

    #TODO : next phase
    def read_file(self,file_path):
        pass